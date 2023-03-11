import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

import app.db
from app.core.models import Base, User, TelegramAuthEntry

# In-memory DB not working for some reason.
# _DB_URL = "sqlite+pysqlite:///:memory:"
DB_PATH = "/test.db"
DB_URL = "sqlite:///" + DB_PATH

readonly = False

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},
    echo=False,
    future=True,
)

Base.metadata.create_all(bind=engine)

session_local = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


@event.listens_for(session_local, "after_flush")
def after_flush(_session, _flush_context):
    if readonly:
        raise AssertionError("Flush occurred in DB readonly mode")


def get_session():
    session = session_local()
    try:
        yield session
    finally:
        session.close()


def override_db(client: TestClient):
    """
    Override connection to the real DB with the fake one.
    """

    client.app.dependency_overrides[app.db.get_session] = get_session


def finalize_overriden_db():
    os.remove(DB_PATH)


def db_set_readonly_mode(readonly_: bool):
    """
    Sets readonly mode.
    If any changes were made when enabled then AssertionError will be raised by event listener.
    Useful for tests that shouldn't modify DB.
    """

    global readonly
    readonly = readonly_


@contextmanager
def ignore_db_readonly():
    """
    Ignores db readonly mode.
    Use in with statement.
    """
    global readonly
    tmp, readonly = readonly, False
    try:
        yield
    finally:
        readonly = tmp


def truncate_tables():
    session = next(get_session())
    session.query(User).delete()
    session.query(TelegramAuthEntry).delete()
    session.commit()
