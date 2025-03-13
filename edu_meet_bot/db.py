from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from edu_meet_bot import settings
from sqlalchemy.ext.asyncio import AsyncSession


engine = create_async_engine(settings.DATABASE_URI, echo=settings.DEBUG)
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)
