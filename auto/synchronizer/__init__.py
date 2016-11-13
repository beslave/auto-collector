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


async def get_first_row(rows):
    async for row in rows:
        return row


class BrandUpdater(SynchronizerUpdater):
    table = Brand.__table__
    origin_table = OriginBrand.__table__
    sync_fields = ['name']


class ModelUpdater(SynchronizerUpdater):
    table = Model.__table__
    origin_table = OriginModel.__table__
    comparable_fields = ['name', 'brand_id']
    sync_fields = ['name', 'brand_id']

    async def preprocess_data(self, data):
        query = OriginBrand.__table__.select().where(
            OriginBrand.__table__.c.id == data['brand_id']
        )
        brand = await make_db_query(query, get_first_row)
        data['brand_id'] = brand.real_instance
        return await super().preprocess_data(data)


class AdvertisementUpdater(SynchronizerUpdater):
    table = Advertisement.__table__
    origin_table = OriginAdvertisement.__table__
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
        query = OriginModel.__table__.select().where(OriginModel.__table__.c.id == data['model_id'])
        model = await make_db_query(query, get_first_row)
        data['model_id'] = model.real_instance
        return await super().preprocess_data(data)


class ComplectationUpdater(SynchronizerUpdater):
    table = Complectation.__table__
    origin_table = OriginComplectation.__table__
    sync_fields = [
        'name',
        'model_id',
    ]
    comparable_fields = ['name', 'model_id']

    async def preprocess_data(self, data):
        query = OriginModel.__table__.select().where(OriginModel.__table__.c.id == data['model_id'])
        model = await make_db_query(query, get_first_row)
        data['model_id'] = model.real_instance
        return await super().preprocess_data(data)


class Synchronizer:
    updaters_list = [
        BrandUpdater,
        ModelUpdater,
        AdvertisementUpdater,
        ComplectationUpdater,
    ]

    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '__instance__', None):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)

        return cls.__instance__

    async def init_updaters(self):
        if getattr(self, 'is_updaters_initialized', False):
            return

        self.updaters = []
        for updater_class in self.updaters_list:
            updater = await updater_class.new()
            self.updaters.append(updater)

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

        for updater in self.updaters:
            await updater.sync()


synchronizer = Synchronizer()
tasks = [synchronizer.run]
