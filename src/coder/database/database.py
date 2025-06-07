from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine
)
import os
from models.models import Base


async def get_engine() -> AsyncEngine:
    return create_async_engine(os.getenv('DATABASE_URL'))


async def get_session():

    async_session = sessionmaker(await get_engine(), class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# async def create_tables():
#     try:
#         engine = await get_engine()
#         async with engine.begin() as eng:
#             await eng.run_sync(Base.metadata.create_all)
#             print("migration successfully")
#     except Exception as e:
#         print("Не удалось создать таблицы. ", str(e))
# maybe later we can use it with alembic