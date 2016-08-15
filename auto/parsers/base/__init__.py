import aiohttp

from auto.models import (
    OriginAdvertisement,
    OriginBrand,
    OriginModel,
)
from auto.updaters import UpdaterByCreatedAt


class BaseParser(object):
    NAME = None
    MAX_RETRIES = 5

    brand_table = OriginBrand.__table__
    model_table = OriginModel.__table__
    advertisement_table = OriginAdvertisement.__table__

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__instance__

    async def parse(self):
        if not getattr(self, 'is_initialized', False):
            self.brand_updater = await UpdaterByCreatedAt.new(self.brand_table)
            self.model_updater = await UpdaterByCreatedAt.new(self.model_table)
            self.adv_updater = await UpdaterByCreatedAt.new(
                self.advertisement_table,
                url_fields=['origin_url', 'preview'],
            )
            self.is_initialized = True

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
