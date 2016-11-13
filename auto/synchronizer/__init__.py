import asyncio
import logging
import psycopg2

from auto import settings
from auto.connection import ConnectionManager
from auto.models import (
    Brand, OriginBrand,
    Model, OriginModel,
    Advertisement, OriginAdvertisement,
    Complectation, OriginComplectation,
)
from auto.updaters import SynchronizerUpdater
from auto.utils import make_db_query


logger = logging.getLogger('auto.synchronizer')

advertisement_table = Advertisement.__table__
brand_table = Brand.__table__
model_table = Model.__table__
complectation_table = Complectation.__table__
origin_advertisement_table = OriginAdvertisement.__table__
origin_brand_table = OriginBrand.__table__
origin_model_table = OriginModel.__table__
origin_complectation_table = OriginComplectation.__table__


async def get_first_row(rows):
    async for row in rows:
        return row


class BrandUpdater(SynchronizerUpdater):
    table = brand_table
    sync_fields = ['name']


class ModelUpdater(SynchronizerUpdater):
    table = model_table
    comparable_fields = ['name', 'brand_id']
    sync_fields = ['name', 'brand_id']

    async def preprocess_data(self, data):
        query = origin_brand_table.select().where(
            origin_brand_table.c.id == data['brand_id']
        )
        brand = await make_db_query(query, get_first_row)
        data['brand_id'] = brand.real_instance
        return await super().preprocess_data(data)


class AdvertisementUpdater(SynchronizerUpdater):
    table = advertisement_table
    sync_fields = [
        'name',
        'model_id',
        'is_new',
        'year',
        'price',
        'origin_url',
        'preview',
    ]
    shorten_url_fields = ['origin_url', 'preview']
    comparable_fields = ['id']

    async def preprocess_data(self, data):
        query = origin_model_table.select().where(origin_model_table.c.id == data['model_id'])
        model = await make_db_query(query, get_first_row)
        data['model_id'] = model.real_instance
        return await super().preprocess_data(data)


class ComplectationUpdater(SynchronizerUpdater):
    table = complectation_table
    sync_fields = [
        'name',
        'model_id',
    ]
    comparable_fields = ['name', 'model_id']

    async def preprocess_data(self, data):
        query = origin_model_table.select().where(origin_model_table.c.id == data['model_id'])
        model = await make_db_query(query, get_first_row)
        data['model_id'] = model.real_instance
        return await super().preprocess_data(data)


class Synchronizer:
    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '__instance__', None):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)

        return cls.__instance__

    async def init_updaters(self):
        if getattr(self, 'is_updaters_initialized', False):
            return

        self.brand_updater = await BrandUpdater.new()
        self.model_updater = await ModelUpdater.new()
        self.advertisement_updater = await AdvertisementUpdater.new()
        self.complectation_updater = await ComplectationUpdater.new()
        self.is_updaters_initialized = True


    async def run(self):
        while True:
            try:
                await self.teak()
            except Exception as e:
                logger.exception(e)

            await asyncio.sleep(settings.SYNC_TIMEOUT)

    async def teak(self):
        await self.init_updaters()

        async with ConnectionManager() as connection:
            logger.debug('Synchronize brands')
            await self.sync(connection, origin_brand_table, self.brand_updater)

            logger.debug('Synchronize models')
            await self.sync(connection, origin_model_table, self.model_updater)

            logger.debug('Synchronize advertisements')
            await self.sync(connection, origin_advertisement_table, self.advertisement_updater)

            logger.debug('Synchronize complectations')
            await self.sync(connection, origin_complectation_table, self.complectation_updater)

    async def sync(self, connection, origin_table, updater):
        rows = await connection.execute(origin_table.select())

        async for row in rows:
            data = dict(row)
            prev_real_instance = data['real_instance']
            data['id'] = data['real_instance']
            del data['real_instance']
            object_data = await updater.update(data)
            pk = object_data['id']

            if prev_real_instance != pk:
                await connection.execute(
                    origin_table.update()
                    .values(real_instance=pk)
                    .where(origin_table.c.id == row.id)
                )


synchronizer = Synchronizer()
tasks = [synchronizer.run]
