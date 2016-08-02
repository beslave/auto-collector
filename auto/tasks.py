import aiohttp
import asyncio
import json

from aiopg.sa import create_engine
from functools import wraps
from psycopg2 import IntegrityError

from auto import settings
from auto.connection import get_connection
from auto.parsers import get_parsers


api_url = lambda method: 'http://api.auto.ria.com' + method


def api_request(url, expected_status=200):
    def decorator(f):
        @wraps(f)
        async def wrapper(connection, session):
            with aiohttp.Timeout(10):
                async with session.get(api_url('/categories')) as response:
                    assert response.status == expected_status
                    content = await response.read()
                    content = content.decode('utf-8')
                    return await f(connection, json.loads(content))
        return wrapper
    return decorator


@api_request('/categories')
async def sync_categories(connection, response):
    categories = {str(x['value']): x['name'] for x in response}
    await connection.delete(['categories'])
    await connection.hmset('categories', categories)
    return categories


async def sync_data():
    async with create_engine(**settings.DATABASE) as engine:
        async with engine.acquire() as connection:
            for parser in get_parsers():
                await parser.prepare(connection)
                async for adv in parser:
                    pass
            # try:
            #     await connection.execute(AutoBrand.__table__.insert().values(name='BMW'))
            # except IntegrityError as e:
            #     print(e)
            #     pass


async def sync_data_task():
    while True:
        await sync_data()
        await asyncio.sleep(settings.SYNC_TIMEOUT)
