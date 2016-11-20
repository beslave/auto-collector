import aiohttp
import asyncio
import json
import re

from datetime import datetime

import settings

from auto.connection import ConnectionManager


def get_absolute_url(url, base_url):
    if url and url.startswith('/') and not url.startswith('//'):
        url = base_url.rstrip('/') + url

    return url


def parse_int(value):
    value = str(value)
    value = value.strip().replace(' ', '')
    value = re.subn(r'[^\d]+', '', value)[0]
    if value.isdigit():
        return int(value)


def parse_interval_depended(value):
    value = str(value)

    if '/' not in value:
        return parse_int(value), None, None

    value, interval = value.split('/')
    value = parse_int(value)

    if '-' in interval:
        start, end = interval.split('-')
        start = parse_int(start)
        end = parse_int(end)
    else:
        start = end = parse_int(interval)

    return value, start, end


def parse_float_to_int(value, multiplier):
    if not value:
        return value

    value = str(value)
    value = value.replace(',', '.')
    value = re.subn(r'[^.\d]+', '', value)[0]
    value = float(value)
    return int(value * multiplier)


def parse_roman(value):
    value = str(value).strip()
    digits = {
        'I': 1,
        'II': 2,
        'III': 3,
        'IV': 4,
        'V': 5,
        'VI': 6,
        'VII': 7,
        'VIII': 8,
        'IX': 9,
        'X': 10,
    }
    return digits.get(value)


def get_first_for_keys(data, keys=[]):
    for key in keys:
        if key in data:
            return data[key]


def has_keys(data, *keys):
    for key in keys:
        if key not in data:
            return False
    return True


async def shorten_url(url):
    if settings.SHORTENER_API_KEY and url and len(url) > 32:
        params = {'longUrl': url}
        data = json.dumps(params).encode('utf-8')
        headers = {'content-type': 'application/json'}

        await asyncio.sleep(1.0 / settings.SHORTENER_MAX_REQUESTS_PER_SECOND)

        api_url = '{}?key={}'.format(settings.SHORTENER_API_URL, settings.SHORTENER_API_KEY)
        with aiohttp.ClientSession() as client:
            post = client.post(api_url, data=data, headers=headers)
            async with post as response:
                response_json = await response.json()
                if response.status == 200:
                    url = response_json['id']
                else:
                    print(response_json)

    return url


async def make_db_query(query, processor=None):
    async with ConnectionManager() as connection:
        results = await connection.execute(query)

        if processor:
            return await processor(results)

        return results


async def db_insert(query):
    async with ConnectionManager() as connection:
        query = query.returning(query.table.c.id)
        pk = await connection.scalar(query)
        return pk
