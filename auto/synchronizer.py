import asyncio
import logging

from aiopg.sa import create_engine

from auto import settings
from auto.models import (
    Advertisement,
    Brand,
    Model,
    OriginAdvertisement,
    OriginBrand,
    OriginModel,
)
from auto.updaters import SynchronizerUpdater
from auto.utils import make_db_query

logger = logging.getLogger('auto.synchronizer')

advertisement_table = Advertisement.__table__
brand_table = Brand.__table__
model_table = Model.__table__
origin_advertisement_table = OriginAdvertisement.__table__
origin_brand_table = OriginBrand.__table__
origin_model_table = OriginModel.__table__


class BrandsUpdater(SynchronizerUpdater):
    table = brand_table
    sync_fields = ['name']


class ModelsUpdater(SynchronizerUpdater):
    table = model_table
    sync_fields = ['name', 'brand_id']

    async def preprocess_data(self, data):
        data = await super().preprocess_data(data)
        query = origin_brand_table.select().where(origin_brand_table.c.id == data['brand_id'])
        data['brand_id'] = await make_db_query(query, lambda rows: [x for x in rows][0].real_instance)
        return data


class AdvertisementsUpdater(SynchronizerUpdater):
    table = advertisement_table
    condition_fields = ['id', 'name', 'created_at', 'updated_at']
    sync_fields = ['name', 'model_id', 'is_new', 'year', 'price', 'origin_url', 'preview']
    shorten_url_fields = ['origin_url', 'preview']
    comparable_fields = ['id']

    async def preprocess_data(self, data):
        data = await super().preprocess_data(data)
        query = origin_model_table.select().where(origin_model_table.c.id == data['model_id'])
        data['model_id'] = await make_db_query(query, lambda rows: [x for x in rows][0].real_instance)
        return data


class Synchronizer:
    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '__instance__', None):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)

        return cls.__instance__

    async def init_updaters(self):
        if getattr(self, 'is_updaters_initialized', False):
            return

        self.is_updaters_initialized = True
        self.brands_updater = await BrandsUpdater.new()
        self.models_updater = await ModelsUpdater.new()
        self.advertisements_updater = await AdvertisementsUpdater.new()

    async def run(self):
        await self.init_updaters()

        while True:
            async with create_engine(**settings.DATABASE) as engine:
                async with engine.acquire() as connection:
                    logger.debug('Synchronize brands')
                    await self.sync(connection, origin_brand_table, self.brands_updater)

                    logger.debug('Synchronize models')
                    await self.sync(connection, origin_model_table, self.models_updater)

                    logger.debug('Synchronize advertisements')
                    await self.sync(connection, origin_advertisement_table, self.advertisements_updater)

            await asyncio.sleep(settings.SYNC_TIMEOUT)

    async def sync(self, connection, origin_table, updater):
        rows = await connection.execute(origin_table.select())

        for row in rows:
            data = dict(row)
            prev_real_instance = data['real_instance']
            data['id'] = data['real_instance']
            del data['real_instance']
            pk = await updater.update(data)

            if prev_real_instance != pk:
                await connection.execute(
                    origin_table.update()
                    .values(real_instance=pk)
                    .where(origin_table.c.id == row.id)
                )
