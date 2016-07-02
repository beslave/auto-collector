import aiohttp
import asyncio
import asyncio_redis
import json

from functools import wraps

from auto import settings


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
    connection = await asyncio_redis.Connection.create(**settings.REDIS_CONNECTION)
    with aiohttp.ClientSession() as session:
        print(await sync_categories(connection, session))
    connection.close()


async def sync_data_task():
    while True:
        await sync_data()
        await asyncio.sleep(settings.SYNC_TIMEOUT)
