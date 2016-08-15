import asyncio
import aiohttp
import logging

from bs4 import BeautifulSoup
from datetime import datetime

from auto import settings
from auto.models import (
    OriginAdvertisement,
    OriginBrand,
    OriginComplectation,
    OriginModel,
)
from auto.utils import get_absolute_url, shorten_url
from auto.updaters import UpdaterByCreatedAt


logger = logging.getLogger('auto.parsers.ria')


class BrandUpdater(UpdaterByCreatedAt):
    table = OriginBrand.__table__


class ModelUpdater(UpdaterByCreatedAt):
    table = OriginModel.__table__


class AdvertisementUpdater(UpdaterByCreatedAt):
    table = OriginAdvertisement.__table__

    async def create(self, data):
        data['origin_url'] = await shorten_url(data['origin_url'])
        data['preview'] = await shorten_url(data['preview'])
        return await super().create(data)


class Parser(object):
    NAME = 'ria'
    BASE_URL = 'https://auto.ria.com'
    BASE_LIST_PAGE = 'https://auto.ria.com/newauto_blocks/search?t=newdesign/search/search&category_id=1&limit=100'
    BRANDS_URL = 'https://api.auto.ria.com/categories/1/marks'
    BRAND_MODELS_URL = 'https://api.auto.ria.com/categories/1/marks/{brand}/models'
    MAX_RETRIES = 5

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__instance__

    async def parse(self):
        if not getattr(self, 'is_initialized', False):
            self.brand_updater = await BrandUpdater.new()
            self.model_updater = await ModelUpdater.new()
            self.adv_updater = await AdvertisementUpdater.new()
            self.is_initialized = True

        await self.prepare()
        await self.parse_advertisements()

    async def parse_advertisements(self):
        page_url = self.BASE_LIST_PAGE
        retries = 0
        while page_url and retries < self.MAX_RETRIES:
            try:
                with aiohttp.ClientSession() as client:
                    async with client.get(page_url) as response:
                        list_html = await response.text()

                page_url = None
                soup = BeautifulSoup(list_html, 'html.parser')
            except Exception as e:
                logger.exception(e)
                retries += 1
                continue

            retries = 0
            for adv_data in self.iter_advertisements(soup):
                await self.adv_updater.update(adv_data)

            next_link = soup.select('.pagination .show-more.fl-r')
            if next_link:
                next_page = next_link[0].attrs['page']
                page_url = self.BASE_LIST_PAGE + '&page=' + next_page


    async def prepare(self):
        with aiohttp.ClientSession() as client:
            async with client.get(self.BRANDS_URL) as response:
                brands = await response.json()

        for brand in brands:
            brand_data = self.parse_brand(brand)
            await self.brand_updater.update(brand_data)

            brand_models_url = self.BRAND_MODELS_URL.format(brand=brand_data['id'])
            with aiohttp.ClientSession() as client:
                async with client.get(brand_models_url) as response:
                    models = await response.json()

            for model in models:
                model['brand_id'] = brand_data['id']
                model_data = self.parse_model(model)
                await self.model_updater.update(model_data)

        return brands

    def parse_brand(self, data):
        return {
            'origin': self.NAME,
            'id': data['value'],
            'name': data['name'],
            'updated_at': datetime.now(),
        }

    def parse_model(self, data):
        return {
            'origin': self.NAME,
            'id': data['value'],
            'brand_id': data['brand_id'],
            'name': data['name'],
            'updated_at': datetime.now(),
        }

    def to_int(self, value):
        value = value.strip().replace(' ', '')
        if value.isdigit():
            return int(value)

    def iter_advertisements(self, soup):
        for adv_element in soup.select('.ticket-item-newauto'):
            name_element = adv_element.select('.name a')[0]
            year_element = adv_element.select('.year')[0]
            price_element = adv_element.select('.block-price strong')[0]
            photo_element = adv_element.select('.block-photo img')[0]

            origin_url = name_element.attrs['href']
            origin_url = get_absolute_url(origin_url, self.BASE_URL)
            preview = photo_element.attrs.get('src', '').strip()
            preview = get_absolute_url(preview, self.BASE_URL)
            yield {
                'id': self.to_int(name_element.attrs.get('auto_id')),
                'is_new': True,
                'origin': self.NAME,
                'origin_url': origin_url,
                'name': name_element.text.strip(),
                'model_id': name_element.attrs.get('model_id'),
                'year': self.to_int(year_element.text),
                'price': self.to_int(price_element.text),
                'updated_at': datetime.now(),
                'preview': preview,
                # 'autosalon_id': name_element.attrs.get('autosalon_id'),
                # 'marka_id': name_element.attrs.get('marka_id'),
                # 'complectation_id': name_element.attrs.get('complete_id'),
            }
