import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from api.models import Base

# DB config — only DB_PASS comes from Secret Manager
_user = os.environ.get("DB_USER", "postgres")
_password = os.environ.get("DB_PASS", "")
_db_name = os.environ.get("DB_NAME", "vera")
_instance = os.environ.get("DB_INSTANCE", "vera-494519:us-central1:vera-db")

# Local dev uses DATABASE_URL directly (from docker-compose), prod builds it from parts
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql+asyncpg://{_user}:{_password}@/{_db_name}?host=/cloudsql/{_instance}" if _password else "",
)

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
        print("WARNING: No database configured — database features disabled.")
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    if async_session is None:
        raise Exception("Database not configured — set DATABASE_URL or DB_PASS environment variable.")
    async with async_session() as session:
        yield session
