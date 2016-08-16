import aiohttp
import asyncio
import json

from datetime import datetime

from auto import settings


def get_absolute_url(url, base_url):
    if url and url.startswith('/') and not url.startswith('//'):
        url = base_url.rstrip('/') + url

    return url


def parse_int(value):
    value = value.strip().replace(' ', '')
    if value.isdigit():
        return int(value)


def get_first_for_keys(data, keys=[]):
    for key in keys:
        if key in data:
            return data[key]


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
