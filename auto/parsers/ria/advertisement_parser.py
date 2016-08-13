import asyncio

from aiopg.sa import create_engine
from datetime import datetime

from auto import settings
from auto.models import OriginAdvertisement
from auto.updaters import UpdaterByCreatedAt
from auto.utils import get_absolute_url, log, shorten_url


class AdvertisementUpdater(UpdaterByCreatedAt):
    table = OriginAdvertisement.__table__

    async def create(self, data):
        data['origin_url'] = await shorten_url(data['origin_url'])
        data['preview'] = await shorten_url(data['preview'])
        return await super().create(data)

    async def update(self, data):
        result = await super().update(data)
        log('Advertisement "{}" is synced', data['name'])
        return result


class AdvertisementParser:
    table = OriginAdvertisement.__table__
    BASE_URL = 'https://auto.ria.com'

    def __init__(self, origin):
        self.origin = origin
        self.queue = asyncio.Queue()

    async def run(self):
        async with create_engine(**settings.DATABASE) as engine:
            async with engine.acquire() as connection:
                updater = await AdvertisementUpdater.new(connection)

                while True:
                    data = await self.queue.get()
                    data = self.parse(data)
                    await updater.update(data)

    def to_int(self, value):
        value = value.replace(' ', '')
        if value.isdigit():
            return int(value)

    def parse(self, data):
        origin_url = get_absolute_url(data['url'], self.BASE_URL)
        preview = get_absolute_url(data['preview'], self.BASE_URL)
        return {
            'id': self.to_int(data['advertisement_id']),
            'is_new': True,
            'origin': self.origin,
            'origin_url': origin_url,
            'name': data['name'],
            'model_id': data['model_id'],
            'year': data['year'],
            'price': self.to_int(data['price']),
            'updated_at': datetime.now(),
            'preview': preview,
        }

    def provide_data(self, data):
        self.queue.put_nowait(data)
