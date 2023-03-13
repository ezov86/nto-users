from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import get_config

AsyncSessionLocal: async_sessionmaker[AsyncSession]


def connect_to_db():
    global AsyncSessionLocal
    engine = create_async_engine(
        get_config().sqlalchemy.async_db_url,
        echo=False,
        future=True
    )

    AsyncSessionLocal = async_sessionmaker(
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        bind=engine
    )


async def get_session() -> any:
    async with AsyncSessionLocal() as session:
        yield session
