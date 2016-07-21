from aiopg.sa import create_engine

from auto import settings


async def get_connection():
    async with create_engine(**settings.DATABASE) as engine:
        async with engine.acquire() as connection:
            await connection
