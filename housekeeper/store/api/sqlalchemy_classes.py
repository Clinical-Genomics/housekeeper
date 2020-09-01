import datetime as dt
from contextlib import contextmanager
from pathlib import Path
import shutil
import json

from sqlalchemy import orm, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from .sqlalchemy_models import Base, Bundle, Version, File, Tag

Session = sessionmaker()


class BaseHandler:
    Base = Base
    Bundle = Bundle
    Version = Version
    File = File
    Tag = Tag


class BaseActionHandler:
    """Class that handles base logic that doesn't end the session scope
    Session required as second argument for all methods """

    def add_bundle(self, session: Session, name: str) -> Bundle:
        new_bundle = Bundle(name=name)
        session.add(new_bundle)
        return new_bundle

    def add_version(
        self,
        session,
        bundle: str,
        tag: str = None,
        include: bool = False,
        created_at: dt.datetime = dt.datetime.now(),
        files: list = [],
    ) -> Version:
        new_version = Version(
            bundle=(
                self.get_bundle(session=session, name=bundle)
                or self.add_bundle(session=session, name=bundle)
            ),
            tag=tag,
            include=include,
            created_at=created_at,
        )
        new_version.files = [
            self.add_file(
                session=session,
                path=f.get("path"),
                tags=f.get("tags"),
                version=new_version,
            )
            for f in files
        ]
        session.add(new_version)
        return new_version

    def add_file(
        self,
        session,
        version: Version,
        path: str,
        to_archive: bool = False,
        tags: list = [],
    ) -> File:
        new_file = File(
            version=version,
            path=path,
            to_archive=to_archive,
            tags=[
                self.get_tag(session=session, name=name)
                or self.add_tag(session=session, name=name)
                for name in tags
            ],
        )
        session.add(new_file)
        return new_file

    def add_tag(self, session, name: str, category: str = None) -> Tag:
        new_tag = Tag(category=category, name=name)
        session.add(new_tag)
        return new_tag

    def get_bundle(self, session, name: str) -> Bundle:
        query = session.query(Bundle).filter(Bundle.name.like(name))
        return query.first()

    def get_version(self, session, version_id: int) -> Version:
        query = session.query(Version).filter(Version.id == version_id)
        return query.first()

    def get_tag(self, session, name: str) -> Tag:
        query = session.query(Tag).filter(Tag.name.ilike(name))
        return query.first()

    def get_file(self, session, file_id: int) -> File:
        query = session.query(File).filter(File.id == file_id)
        return query.first()

    def include_file(self, session, file_obj: File, include_path: Path) -> None:
        from_path = Path(file_obj.path)
        to_path = Path(include_path, from_path.name)
        try:
            from_path.link_to(to_path)
            file_obj.path = to_path.as_posix()
        except:
            # Raise custom error
            raise

    def include_version(self, session, version_obj: Version) -> None:
        try:
            include_path = Path(
                self.root,
                version_obj.bundle,
                version_obj.id,
                version_obj.created_at.date(),
            )
            Path.mkdir(include_path, parents=True, exist_ok=True)
            for file_obj in version_obj.files:
                self.include_file(
                    session=session, file_obj=file_obj, include_path=include_path,
                )
            version_obj.include = True
        except:
            Path.rmdir(include_path)
            raise


class SessionWrapper:
    def __init__(self, uri: str, root: Path):
        self.engine = create_engine(uri, echo=False, poolclass=NullPool)
        self.root = root
        super().__init__()

    @contextmanager
    def session_scope(self):
        Session.configure(bind=self.engine)
        session = Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


class ActionHandler(SessionWrapper, BaseActionHandler):
    """Class that handles logic to be executed within distinct session scope
    No objects are to be passed as arguments to these methods, since those objects """

    def add_include_version(
        self,
        bundle: str,
        tag: str = None,
        include: bool = False,
        created_at: dt.datetime = dt.datetime.now(),
        files: list = [],
    ) -> None:

        with self.session_scope() as session:
            # New version in session but not committed
            version_obj = self.add_version(
                session=session,
                bundle=bundle,
                tag=tag,
                include=include,
                created_at=created_at,
                files=files,
            )
            if include == True:
                # Do linking logic (Raising exception here will rollback the scope, and version won't be added)
                self.include_version(session=session, version_obj=version_obj)

            # If it made it here, session will commit, close, and connection recycled!

    def include_existing_version(self, version_id: int) -> None:
        with self.session_scope() as session:
            version_obj = self.get_version(session, version_id=version_id)
            self.include_version(session=session, version_obj=version_obj)

    def add_file_to_version(self, version_id: int, path: Path, tags: list = []) -> None:
        with self.session_scope() as session:
            file_obj = self.add_file(
                session=session,
                version=self.get_version(session=session, version_id=version_id),
                path=path,
                tags=tags,
            )
            if file_obj.version.include == True:
                try:
                    include_path = Path(
                        self.root,
                        file_obj.version.bundle,
                        file_obj.version_id,
                        file_obj.version.created_at.date(),
                    )
                    self.include_file(
                        session=session, file_obj=file_obj, include_path=include_path
                    )
                except:
                    raise

    def add_tags_to_file(self, file_id: int, tags: list = []) -> None:
        with self.session_scope() as session:
            file_obj = self.get_file(session=session, file_id=file_id)
            file_obj.tags = file_obj.tags + [
                self.get_tag(session=session, name=name)
                or self.add_tag(session=session, name=name)
                for name in tags
            ]

    def delete_bundle(self, name: str) -> None:
        with self.session_scope() as session:
            bundle = self.get_bundle(session=session, name=name)
            Path(self.root, bundle.name).rmdir()
            session.delete(bundle)

    def delete_version(self, version_id: int) -> None:
        with self.session_scope() as session:
            version_obj = self.get_version(session=session, version_id=version_id)
            Path(
                self.root,
                version_obj.bundle.name,
                version_obj.id,
                version_obj.created_at.date(),
            ).rmdir()
            session.delete(version_obj)

    def delete_file(self, file_id: int) -> None:
        with self.session_scope() as session:
            file_obj = self.get_file(session=session, file_id=file_id)
            if file_obj.version.include == True:
                Path(file_obj.path).unlink()
            session.delete(file_obj)

    def delete_tags_from_file(self, file_id: int, tags: list = []) -> None:
        with self.session_scope() as session:
            file_obj = self.get_file(session=session, file_id=file_id)
            existing_tags = list(
                filter(
                    lambda x: x != None,
                    [self.get_tag(session=session, name=name) for name in tags],
                )
            )
            for tag in existing_tags:
                if tag in file_obj.tags:
                    file_obj.tags.remove(tag)

    def add_tag_to_version(self, version_id, version_tag):
        with self.session_scope() as session:
            version_obj = self.get_version(session=session, version_id=version_id)
            version_obj.tag = version_tag


    def find_version(
        self,
        version_id: int = None,
        bundle: str = "",
        tag: str = "",
        created_at: dt.datetime = None,
    ) -> Version:
        with self.session_scope() as session:
            if version_id:
                query = session.query(Version).filter(Version.id == version_id)
            else:
                query = (
                    session.query(Version)
                    .join(Bundle)
                    .filter(Bundle.name.ilike(f"%{bundle}%"))
                    .filter(Version.tag.ilike(f"%{tag}%"))
                )
                if created_at:
                    query = query.filter(Version.created_at == created_at)
                else:
                    query = query.order_by(Version.created_at)
            return json.loads(str(query.first()))


    def find_multiple_files(
        self,
        bundle: str = "",
        version_tag: str = "",
        created_at: dt.datetime = None,
        tags: list = [],
    ) -> list(File):
        with self.session_scope() as session:
            query = (
                session.query(File)
                .join(File.version, Version.bundle)
                .filter(Bundle.name.ilike(f"%{bundle}%"))
                .filter(Version.tag.ilike(f"%{version_tag}%"))
            )
            if created_at:
                query = query.filter(Version.created_at == created_at)
            else:
                query = query.order_by(Version.created_at)
            if tags:
                query = (
                    query.join(File.tags).filter(Tag.name.in_(tags)).group_by(File.id)
                )
            return json.loads(str(query.all()))

    def find_file(
        self,
        file_id: int = None,
        path: str = "",
        bundle: str = "",
        version_tag: str = "",
        created_at: dt.datetime = None,
        tags: list = [],
    ) -> File:
        with self.session_scope() as session:

            if file_id:
                query = session.query(File).filter(File.id == file_id)
            elif path:
                query = session.query(File).filter(File.path == path)
            else:
                query = (
                    session.query(File)
                    .join(File.version, Version.bundle)
                    .filter(Bundle.name.ilike(f"%{bundle}%"))
                    .filter(Version.tag.ilike(f"%{version_tag}%"))
                )
                if created_at:
                    query = query.filter(Version.created_at == created_at)
                else:
                    query = query.order_by(Version.created_at)
                if tags:
                    query = (
                        query.join(File.tags).filter(Tag.name.in_(tags)).group_by(File.id)
                    )
            return json.loads(str(query.first()))

    def find_bundle(self, name: str):
        with self.session_scope() as session:
            bundle_obj = self.get_bundle(session=session, name=name)
            return json.loads(str(bundle_obj))




class SessionHandler(SessionWrapper):
    def __init__(self, uri: str, root: Path):
        self.session_handler = SessionWrapper(uri=uri, root=root)
        super().__init__(uri, root)


class HousekeeperAPI(SessionHandler, ActionHandler, BaseHandler):
    def init_db(self):
        self.Base.metadata.create_all(self.engine)

    def destroy_db(self):
        self.Base.metadata.drop_all(self.engine)
