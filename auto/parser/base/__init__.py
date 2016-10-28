import aiohttp
import asyncio
import logging

from auto.models import (
    OriginAdvertisement,
    OriginBrand,
    OriginModel,
)
from auto.updaters import (
    OriginUpdater,
    UpdateByCreatedAtMixin,
    UpdateNotSimilarMixin,
)


logger = logging.getLogger('auto.parser')


class OriginBrandUpdater(UpdateNotSimilarMixin, OriginUpdater):
    table = OriginBrand.__table__
    condition_fields = ['name']


class OriginModelUpdater(UpdateNotSimilarMixin, OriginUpdater):
    table = OriginModel.__table__
    condition_fields = ['name']


class OriginAdvertisementUpdater(UpdateByCreatedAtMixin, OriginUpdater):
    table = OriginAdvertisement.__table__


class BaseParser(object):
    ORIGIN = None
    MAX_GET_ATTEMPTS = 5

    brand_table = OriginBrand.__table__
    model_table = OriginModel.__table__
    advertisement_table = OriginAdvertisement.__table__

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__instance__

    async def get_attempts(self, client, url, getter='json'):
        retries = 1
        while True:
            try:
                async with client.get(url) as response:
                    assert response.status < 400
                    return await getattr(response, getter)()

            except Exception as e:
                if retries > self.MAX_GET_ATTEMPTS:
                    raise

                await asyncio.sleep(1)
                retries += 1
                logger.wargning(e)

    async def init_updaters(self):
        if getattr(self, 'is_initialized', False):
            return

        self.brand_updater = await OriginBrandUpdater.new(self.ORIGIN)
        self.model_updater = await OriginModelUpdater.new(self.ORIGIN)
        self.adv_updater = await OriginAdvertisementUpdater.new(self.ORIGIN)
        self.is_initialized = True

    async def parse(self):
        await self.init_updaters()

        with aiohttp.ClientSession() as client:
            await self.parse_brands(client)
            await self.parse_models(client)
            await self.parse_advertisements(client)

    async def parse_brands(self, client):
        raise NotImplemented

    async def parse_models(self, client):
        raise NotImplemented

    async def parse_advertisements(self, client):
        raise NotImplemented
