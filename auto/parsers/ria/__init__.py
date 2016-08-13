import asyncio
import aiohttp

from bs4 import BeautifulSoup
from datetime import datetime

from auto.models import (
    OriginBrand,
    OriginComplectation,
    OriginModel,
)
from auto.utils import log
from auto.updaters import UpdaterByCreatedAt

from .advertisement_parser import AdvertisementParser


class BrandUpdater(UpdaterByCreatedAt):
    table = OriginBrand.__table__

    async def update(self, data):
        result = await super().update(data)
        log('Brand "{}" is synced', data['name'])
        return result


class ModelUpdater(UpdaterByCreatedAt):
    table = OriginModel.__table__

    async def update(self, data):
        result = await super().update(data)
        log('Model "{}" is synced', data['name'])
        return result


class Parser(object):
    NAME = 'ria'
    BASE_LIST_PAGE = 'https://auto.ria.com/newauto_blocks/search?t=newdesign/search/search&limit=100'
    BRANDS_URL = 'https://api.auto.ria.com/categories/1/marks'
    BRAND_MODELS_URL = 'https://api.auto.ria.com/categories/1/marks/{brand}/models'
    MAX_RETRIES = 5

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__instance__

    def __init__(self, *args, **kwargs):
        self.parser = AdvertisementParser(self.NAME)
        loop = asyncio.get_event_loop()
        loop.create_task(self.parser.run())

    async def parse(self, connection):
        await self.prepare(connection)
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
                log(e)
                retries += 1
                continue

            retries = 0
            for adv_data in self.iter_advertisements(soup):
                self.parser.provide_data(adv_data)

            next_link = soup.select('.pagination .show-more.fl-r')
            if next_link:
                next_page = next_link[0].attrs['page']
                page_url = self.BASE_LIST_PAGE + '&page=' + next_page


    async def prepare(self, connection):
        with aiohttp.ClientSession() as client:
            async with client.get(self.BRANDS_URL) as response:
                brands = await response.json()

        brand_updater = await BrandUpdater.new(connection)
        model_updater = await ModelUpdater.new(connection)

        for brand in brands:
            brand_data = self.parse_brand(brand)
            await brand_updater.update(brand_data)

            brand_models_url = self.BRAND_MODELS_URL.format(brand=brand_data['id'])
            with aiohttp.ClientSession() as client:
                async with client.get(brand_models_url) as response:
                    models = await response.json()

            for model in models:
                model['brand_id'] = brand_data['id']
                model_data = self.parse_model(model)
                await model_updater.update(model_data)

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

    def iter_advertisements(self, soup):
        for adv_element in soup.select('.ticket-item-newauto'):
            name_element = adv_element.select('.name a')[0]
            year_element = adv_element.select('.year')[0]
            price_element = adv_element.select('.block-price strong')[0]
            photo_element = adv_element.select('.block-photo img')[0]

            year = year_element.text.strip()
            if year.isdigit():
                year = int(year)
            else:
                year = None

            data = {
                'url': name_element.attrs['href'],
                'name': name_element.text.strip(),
                'year': year,
                'price': price_element.text.strip(),
                'autosalon_id': name_element.attrs.get('autosalon_id'),
                'marka_id': name_element.attrs.get('marka_id'),
                'model_id': name_element.attrs.get('model_id'),
                'complectation_id': name_element.attrs.get('complete_id'),
                'advertisement_id': name_element.attrs.get('auto_id'),
                'preview': photo_element.attrs.get('src', '').strip(),
            }
            yield data
