import asyncio
from .models import *
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from loguru import logger

def get_engine():
    import config
    if config.dburl == "":
        raise ValueError("dburl can not be empty")
    logger.debug(f"dburl={config.dburl}")
    return create_async_engine(config.dburl, echo=False)

engine = get_engine()

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def init_models():
    await create_db()
