import asyncio

from aiopg.sa import create_engine
from datetime import datetime
from psycopg2 import IntegrityError
from random import random
from sqlalchemy.sql import select

from auto import settings
from auto.models import OriginAdvertisement


class AdvertisementParser:
    table = OriginAdvertisement.__table__
    THRESHOLD = 86400

    def __init__(self, origin):
        self.origin = origin
        self.queue = asyncio.Queue()

    async def run(self):
        async with create_engine(**settings.DATABASE) as engine:
            async with engine.acquire() as connection:
                existed_advertisements = await connection.execute(select([
                    self.table.c.id, self.table.c.created_at,
                ]))
                created_at = {
                    row.id: row.created_at
                    for row in existed_advertisements
                }

                while True:
                    data = await self.queue.get()
                    adv_id = int(data['advertisement_id'])
                    create = adv_id not in created_at
                    update_probability = self.get_update_probability(created_at.get(adv_id))

                    if update_probability >= random():
                        await self.parse(connection, data, create)
                        created_at[adv_id] = datetime.now()

    def to_int(self, value):
        value = value.replace(' ', '')
        if value.isdigit():
            return int(value)

    async def parse(self, connection, data, create=True):
        origin_url = data['url']
        if origin_url.startswith('/') and not origin_url.startswith('//'):
            origin_url = 'https://auto.ria.com' + origin_url

        adv_data = {
            'is_new': True,
            'origin': self.origin,
            'origin_url': origin_url,
            'name': data['name'],
            'model_id': data['model_id'],
            'year': data['year'],
            'price': self.to_int(data['price']),
            'updated_at': datetime.now(),
            'preview': data['preview'],
        }
        try:
            if create:
                await connection.execute(self.table.insert().values(
                    id=data['advertisement_id'],
                    created_at=datetime.now(),
                    **adv_data,
                ))
            else:
                await connection.execute(
                    self.table.update().values(**adv_data).where(
                        self.table.c.id == data['advertisement_id']
                    )
                )
        except IntegrityError as e:
            pass

        print('Advertismenet "{}" is synced'.format(data['name']))

    def provide_data(self, data):
        self.queue.put_nowait(data)

    def get_update_probability(self, created_at):
        return 1.0

        if not created_at:
            return 1.0

        delta_seconds = (datetime.now() - created_at).total_seconds()

        if delta_seconds < self.THRESHOLD:
            return delta_seconds / self.THRESHOLD
        else:
            return self.THRESHOLD / delta_seconds
