from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_config


SessionLocal: sessionmaker | None = None

def connect_to_db():
    global SessionLocal
    engine = create_engine(
        get_config().sqlalchemy.db_url,
        echo=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
