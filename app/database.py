from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.SQLALCHEMY_ECHO,
    pool_pre_ping=True,
)
async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_db_session():
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
