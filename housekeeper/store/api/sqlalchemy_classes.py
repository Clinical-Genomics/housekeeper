import datetime as dt
from contextlib import contextmanager

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
    """Class that handles base logic that doesn't end the session scope"""

    def add_bundle(self, session, name: str):
        new_bundle = Bundle(name=name)
        session.add(new_bundle)
        return new_bundle

    def add_version(
        self,
        session,
        bundle: str,
        include: bool = False,
        tag: str = None,
        files: list = [],
        created_at: dt.datetime = dt.datetime.now(),
    ):
        new_version = Version(
            bundle=(
                self.get_bundle(session=session, name=bundle)
                or self.add_bundle(session=session, name=bundle)
            ),
            tag=tag,
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

    def add_file(self, session, version: Version, path: str, tags: list = []):
        new_file = File(
            version=version,
            path=path,
            tags=[
                self.get_tag(session=session, name=name)
                or self.add_tag(session=session, name=name)
                for name in tags
            ],
        )
        session.add(new_file)
        return new_file

    def add_tag(self, session, name: str, category: str = None):
        new_tag = Tag(category=category, name=name)
        session.add(new_tag)
        return new_tag

    def get_bundle(self, session, name):
        query = session.query(Bundle).filter(Bundle.name.like(name))
        return query.first()

    def get_version(
        self, session, bundle: str, tag: str = "", created_at: dt.datetime = None
    ):
        query = (
            session.query(Version)
            .join(Bundle)
            .filter(Bundle.name.ilike(bundle))
            .filter(Version.tag.ilike(f"%{tag}%"))
        )
        if created_at:
            query = query.filter(Version.created_at == created_at)
        else:
            query = query.order_by(Version.created_at)
        return query.first()

    def get_tag(self, session, name):
        query = session.query(Tag).filter(Tag.name.ilike(name))
        return query.first()


class SessionHandler(BaseHandler):
    def __init__(self, uri, root):
        self.engine = create_engine(uri, echo=False, poolclass=NullPool)
        self.root = root

    def init_db(self):
        self.Base.metadata.create_all(self.engine)

    def destroy_db(self):
        self.Base.metadata.drop_all(self.engine)

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


class ComplexActionHandler(SessionHandler, BaseActionHandler):
    """Class that handles logic to be executed within distinct session scope"""

    def link_path(self, **kwargs):
        """Placeholder"""
        return None

    def include_store_version(
        self,
        bundle: str,
        include: bool = False,
        tag: str = None,
        files: list = [],
        created_at: dt.datetime = dt.datetime.now(),
    ):

        with self.session_scope() as session:
            # New version in session but not committed
            new_version = self.add_version(
                session=session,
                bundle=bundle,
                include=include,
                tag=tag,
                files=files,
                created_at=created_at,
            )
            if include == True:
                # Do linking logic (Raising exception here will rollback the scope, and version won't be added)

                for f in new_version.files:
                    f.path = self.link_path(
                        bundle=new_version.bundle,
                        version_id=new_version.id,
                        created_at=new_version.created_at,
                        origin_path=f.path
                    )
                

            # If it made it here, session will commit, close, and connection recycled!

