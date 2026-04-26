import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from api.models import Base

DATABASE_URL = os.environ.get("DATABASE_URL", "")

engine = None
async_session = None


def _init_engine():
    global engine, async_session
    if not DATABASE_URL:
        return
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    _init_engine()
    if engine is None:
        print("WARNING: No DATABASE_URL set — database features disabled.")
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    if async_session is None:
        raise Exception("Database not configured — set DATABASE_URL environment variable.")
    async with async_session() as session:
        yield session
