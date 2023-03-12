from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_session

from app.config import get_config

AsyncSessionLocal: async_sessionmaker[AsyncSession]


def connect_to_db():
    global AsyncSessionLocal
    engine = create_async_engine(
        get_config().sqlalchemy.db_url,
        echo=True
    )

    AsyncSessionLocal = async_sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine
    )


async def get_session() -> any:
    async with AsyncSessionLocal() as session:
        yield session
