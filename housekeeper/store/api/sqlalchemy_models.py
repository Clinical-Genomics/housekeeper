import datetime as dt

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    orm,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, joinedload, subqueryload


Base = declarative_base()

file_tag_link = Table(
    "file_tag_link",
    Base.metadata,
    Column("file_id", Integer, ForeignKey("file.id"), nullable=False),
    Column("tag_id", Integer, ForeignKey("tag.id"), nullable=False),
)


class Bundle(Base):
    """A general group of files."""

    __tablename__ = "bundle"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.now)
    versions = relationship(
        "Version", order_by="-Version.created_at", cascade="delete, save-update",
    )

    def __repr__(self):
        return (
            f"{{'id': {self.id}, "
            f"'name': '{self.name}', "
            f"'created_at': '{self.created_at}', "
            f"'versions': {self.versions}}}"
        ).replace("'", "\"")


class Tag(Base):
    """Represents tags for bundles"""

    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    category = Column(String(64))
    created_at = Column(DateTime, default=dt.datetime.now)

    def __repr__(self):
        return (
            f"{{'id': {self.id}, "
            f"'name': '{self.name}', "
            f"'category': '{self.category}', "
            f"'created_at': '{self.created_at}'}}"
        ).replace("'", "\"")


class Version(Base):
    """Keeps track of versions"""

    __tablename__ = "version"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=dt.datetime.now)
    expires_at = Column(DateTime)
    included_at = Column(DateTime)
    removed_at = Column(DateTime)
    archived_at = Column(DateTime)
    archive_path = Column(String(256), unique=True)
    archive_checksum = Column(String(256), unique=True)
    bundle_id = Column(ForeignKey("bundle.id", ondelete="CASCADE"), nullable=False)
    files = relationship("File", cascade="delete, save-update")
    tag = Column(String(64))
    include = Column(Boolean, default=False)
    bundle = relationship("Bundle", primaryjoin=bundle_id == Bundle.id)

    def __repr__(self):
        return (
            f"{{'id': {self.id}, "
            f"'created_at': '{self.created_at}', "
            f"'expires_at': '{self.expires_at}', "
            f"'included_at': '{self.included_at}', "
            f"'removed_at': '{self.removed_at}', "
            f"'archived_at': '{self.expires_at}', "
            f"'archive_path': '{self.archive_path}', "
            f"'bundle_id': {self.bundle_id}, "
            f"'include': '{self.include}', "
            f"'tag': '{self.tag}', "
            f"'archive_checksum': '{self.archive_checksum}', "
            f"'files': {self.files}}}"
        ).replace("'", "\"")


class File(Base):
    """Represent a file."""

    __tablename__ = "file"

    id = Column(Integer, primary_key=True)
    path = Column(String(256), unique=True, nullable=False)
    checksum = Column(String(256))
    to_archive = Column(Boolean, default=False, nullable=False)
    version_id = Column(ForeignKey("version.id", ondelete="CASCADE"), nullable=False)
    tags = relationship("Tag", secondary="file_tag_link")
    version = relationship("Version", primaryjoin=version_id == Version.id)

    def __repr__(self):
        return (
            f"{{'id': {self.id}, "
            f"'path': '{self.path}', "
            f"'checksum': '{self.checksum}', "
            f"'to_archive': '{self.to_archive}', "
            f"'version_id': {self.version_id}, "
            f"'tags': {self.tags}}}"
        ).replace("'", "\"")

