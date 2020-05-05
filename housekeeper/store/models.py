"""Module for the models"""

import datetime as dt
from pathlib import Path

import alchy
from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint, orm, types

Model = alchy.make_declarative_base(Base=alchy.ModelBase)


file_tag_link = Table(
    "file_tag_link",
    Model.metadata,
    Column("file_id", types.Integer, ForeignKey("file.id"), nullable=False),
    Column("tag_id", types.Integer, ForeignKey("tag.id"), nullable=False),
    UniqueConstraint("file_id", "tag_id", name="_file_tag_uc"),
)


class Bundle(Model):

    """A general group of files."""

    __tablename__ = "bundle"

    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(64), unique=True, nullable=False)
    created_at = Column(types.DateTime, default=dt.datetime.now)
    versions = orm.relationship(
        "Version",
        backref="bundle",
        order_by="-Version.created_at",
        cascade="delete, save-update",
    )


class Version(Model):

    """Keeps track of versions"""

    __tablename__ = "version"

    id = Column(types.Integer, primary_key=True)
    created_at = Column(types.DateTime, nullable=False)
    expires_at = Column(types.DateTime)
    included_at = Column(types.DateTime)
    removed_at = Column(types.DateTime)

    archived_at = Column(types.DateTime)
    archive_path = Column(types.String(256), unique=True)
    archive_checksum = Column(types.String(256), unique=True)

    bundle_id = Column(ForeignKey(Bundle.id, ondelete="CASCADE"), nullable=False)
    files = orm.relationship("File", backref="version", cascade="delete, save-update")

    app_root = None

    @property
    def relative_root_dir(self):
        """Build the relative root dir path for the bundle version."""
        return Path(self.bundle.name) / str(self.created_at.date())

    @property
    def full_path(self):
        """Returns the full path of the bundle"""
        return Path(self.app_root) / self.bundle.name / str(self.created_at.date())


class File(Model):

    """Represent a file."""

    __tablename__ = "file"

    id = Column(types.Integer, primary_key=True)
    path = Column(types.String(256), unique=True, nullable=False)
    checksum = Column(types.String(256))
    to_archive = Column(types.Boolean, nullable=False, default=False)

    version_id = Column(ForeignKey(Version.id, ondelete="CASCADE"), nullable=False)
    tags = orm.relationship("Tag", secondary=file_tag_link, backref="files")

    app_root = None

    @property
    def full_path(self):
        """Return the full path to the file."""
        if Path(self.path).is_absolute():
            return self.path
        return str(self.app_root / self.path)

    @property
    def is_included(self):
        """Check if the file is included in Housekeeper."""
        return str(self.app_root) in self.full_path


class Tag(Model):

    """Represents tags for bundles"""

    __tablename__ = "tag"

    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(64), unique=True, nullable=False)
    category = Column(types.String(64))
    created_at = Column(types.DateTime, default=dt.datetime.now)
