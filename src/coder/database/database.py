from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine
)
import os

from models.models import Base

async_engine = None
async def get_engine():
    global async_engine
    if async_engine is None: #вот тут указал именно асинхронный, потому что поетри не работал и просил psy
        async_engine = create_async_engine(os.getenv('SQLDATABASE_URL'))
    return async_engine

#лучше все это переделать так как делалось лишь бы работаало)))
async def get_session():
    engine = await get_engine()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()

async def create_tables():
    try:
        engine = await get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Migration successful")
    except Exception as e:
        print("Не удалось создать таблицы. ", str(e))