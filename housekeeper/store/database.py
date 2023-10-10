from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, Session, sessionmaker


SESSION_FACTORY: Optional[Session] = None
ENGINE = None


def initialise_database(db_uri: str):
    global SESSION_FACTORY, ENGINE
    ENGINE = create_engine(db_uri)
    session_maker = sessionmaker(ENGINE)
    SESSION_FACTORY = scoped_session(session_maker)


def get_session() -> Session:
    if not SESSION_FACTORY:
        raise Exception("Database not initialised")
    return SESSION_FACTORY()


def get_engine():
    if not ENGINE:
        raise Exception("Database not initialised")
    return ENGINE
