from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, Session, sessionmaker

from housekeeper.exc import HousekeeperError
from housekeeper.store.models import Model


SESSION_FACTORY: Optional[Session] = None
ENGINE = None


def initialise_database(db_uri: str):
    """Initialize the global engine and session factory for SQLAlchemy."""
    global SESSION_FACTORY, ENGINE
    ENGINE = create_engine(db_uri, pool_pre_ping=True)
    session_maker = sessionmaker(ENGINE)
    SESSION_FACTORY = scoped_session(session_maker)


def get_session() -> Session:
    if not SESSION_FACTORY:
        raise HousekeeperError("Database not initialised")
    return SESSION_FACTORY()


def get_engine():
    if not ENGINE:
        raise HousekeeperError("Database not initialised")
    return ENGINE


def create_all_tables() -> None:
    session: Session = get_session()
    Model.metadata.create_all(bind=session.get_bind())


def drop_all_tables() -> None:
    session: Session = get_session()
    Model.metadata.drop_all(bind=session.get_bind())


def get_tables() -> list:
    engine = get_engine()
    return engine.table_names()
