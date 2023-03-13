from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import Config
from app.core.models import User, TelegramAuthData

SessionLocal: sessionmaker[Session]


def init_sync_db(real_config: Config):
    global SessionLocal

    engine = create_engine(
        real_config.tests.sync_db_url,
        echo=False,
        future=True,
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


def get_sync_session_iterator() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_sync_session() -> Session:
    return next(get_sync_session_iterator())


def truncate_tables():
    session = get_sync_session()
    session.query(TelegramAuthData).delete()
    session.query(User).delete()
    session.commit()
