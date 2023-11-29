from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from housekeeper.exc import HousekeeperError
from housekeeper.store.models import Model

SESSION: Session | None = None
ENGINE: Engine | None = None


def initialize_database(db_uri: str) -> None:
    """Initialize the global SQLAlchemy engine and session for housekeeper db."""
    global SESSION, ENGINE
    ENGINE = create_engine(db_uri, pool_pre_ping=True, future=True)
    session_factory = sessionmaker(ENGINE)
    SESSION = scoped_session(session_factory)


def get_session() -> Session:
    """
    Get a SQLAlchemy session with a connection to housekeeper db.
    The session is retrieved from the scoped session registry and is thread local.
    """
    if not SESSION:
        raise HousekeeperError("Database not initialised")
    return SESSION


def get_engine() -> Engine:
    """Get the SQLAlchemy engine with a connection to housekeeper db."""
    if not ENGINE:
        raise HousekeeperError("Database not initialised")
    return ENGINE


def create_all_tables() -> None:
    """Create all tables in housekeeper db."""
    session: Session = get_session()
    Model.metadata.create_all(bind=session.get_bind())


def drop_all_tables() -> None:
    """Drop all tables in housekeeper db."""
    session: Session = get_session()
    Model.metadata.drop_all(bind=session.get_bind())


def get_tables() -> list[str]:
    """Get a list of all tables in housekeeper db."""
    engine: Engine = get_engine()
    inspector: Inspector = inspect(engine)
    return inspector.get_table_names()
