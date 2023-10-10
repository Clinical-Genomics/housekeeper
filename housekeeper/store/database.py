from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, Session, sessionmaker

from housekeeper.exc import HousekeeperError


SESSION: Optional[Session] = None
ENGINE = None


def initialise_database(db_uri: str):
    global SESSION, ENGINE
    ENGINE = create_engine(db_uri, pool_pre_ping=True)
    session_factory = sessionmaker(ENGINE)
    SESSION = scoped_session(session_factory)


def get_session() -> Session:
    if not SESSION:
        raise HousekeeperError("Database not initialised")
    return SESSION()


def get_engine():
    if not ENGINE:
        raise HousekeeperError("Database not initialised")
    return ENGINE
