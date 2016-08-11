import aiohttp
import asyncio
import json

from aiopg.sa import create_engine
from functools import wraps
from psycopg2 import IntegrityError

from auto import settings
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
                await parser.parse(connection)


async def sync_data_task():
    while True:
        print('{:=^40}'.format(' SYNC DATA '))
        try:
            await sync_data()
        except Exception as e:
            print(e)

        await asyncio.sleep(settings.SYNC_TIMEOUT)


tasks = [
    sync_data_task,
]
