
import datetime as dt

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, orm, Table, UniqueConstraint
from sqlalchemy.orm import relationship, joinedload, subqueryload



Base = declarative_base()

file_tag_link = Table(
    "file_tag_link",
    Base.metadata,
    Column("file_id", Integer, ForeignKey("file.id"), nullable=False),
    Column("tag_id", Integer, ForeignKey("tag.id"), nullable=False))

class Bundle(Base):
    """A general group of files."""

    __tablename__ = "bundle"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.now)
    versions = relationship(
        "Version",
        order_by="-Version.created_at",
        cascade="delete, save-update",
    )
    
    def __repr__(self):
        return f"<Bundle(id={self.id}, name='{self.name}', created_at='{self.created_at}')>"

class Tag(Base):
    """Represents tags for bundles"""

    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String)
    created_at = Column(DateTime, default=dt.datetime.now)
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"

    
class Version(Base):
    """Keeps track of versions"""

    __tablename__ = "version"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=dt.datetime.now)
    expires_at = Column(DateTime)
    included_at = Column(DateTime)
    removed_at = Column(DateTime)
    archived_at = Column(DateTime)
    archive_path = Column(String, unique=True)
    archive_checksum = Column(String, unique=True)
    bundle_id = Column(ForeignKey("bundle.id", ondelete="CASCADE"), nullable=False)
    files = relationship("File", cascade="delete, save-update")
    tag = Column(String(64))
    included = Column(Boolean, default=False)
    bundle = relationship("Bundle", primaryjoin=bundle_id == Bundle.id)
    
    def __repr__(self):
        return f"<Version(id={self.id}, tag='{self.tag}', bundle_id={self.bundle_id}, bundle='{self.bundle.name}', created_at='{self.created_at}')>"



class File(Base):
    """Represent a file."""

    __tablename__ = "file"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)
    checksum = Column(String)
    to_archive = Column(Boolean, default=False)
    version_id = Column(ForeignKey("version.id", ondelete="CASCADE"), nullable=False)
    tags = relationship("Tag", secondary="file_tag_link")
    version = relationship("Version", primaryjoin=version_id == Version.id)
    
    def __repr__(self):
        return f"<File(id={self.id}, path='{self.path}', version='{self.version}', tags={self.tags})>"
    

    
    