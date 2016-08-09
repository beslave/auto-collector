import asyncio
import aiohttp

from bs4 import BeautifulSoup
from datetime import datetime
from psycopg2 import IntegrityError

from auto.models import (
    OriginBrand,
    OriginComplectation,
    OriginModel,
)

from .advertisement_parser import AdvertisementParser


class Parser(object):
    NAME = 'ria'
    BASE_LIST_PAGE = 'https://auto.ria.com/newauto_blocks/search?t=newdesign/search/search&limit=100'
    BRANDS_URL = 'https://api.auto.ria.com/categories/1/marks'
    BRAND_MODELS_URL = 'https://api.auto.ria.com/categories/1/marks/{brand}/models'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__instance__

    def __init__(self, *args, **kwargs):
        self.parser = AdvertisementParser(self.NAME)
        loop = asyncio.get_event_loop()
        loop.create_task(self.parser.run())

    async def parse(self, connection):
        brands = await self.prepare(connection)
        await self.parse_advertisements()

    async def parse_advertisements(self):
        page_url = self.BASE_LIST_PAGE
        while page_url:
            with aiohttp.ClientSession() as client:
                async with client.get(page_url) as response:
                    list_html = await response.text()

            page_url = None
            soup = BeautifulSoup(list_html, 'html.parser')

            for adv_data in self.iter_advertisements(soup):
                self.parser.provide_data(adv_data)

            next_link = soup.select('.pagination .show-more.fl-r')
            if next_link:
                next_page = next_link[0].attrs['page']
                page_url = self.BASE_LIST_PAGE + '&page=' + next_page


    async def prepare(self, connection):
        brands = {}
        with aiohttp.ClientSession() as client:
            async with client.get(self.BRANDS_URL) as response:
                brands_json = await response.json()

        for brand in brands_json:
            brand_id, brand_data = await self.prepare_brand(connection, brand)
            brands[brand_id] = brand_data

        return brands

    async def prepare_brand(self, connection, data):
        models = {}
        try:
            await connection.execute(
                OriginBrand.__table__.insert().values(
                    origin=self.NAME,
                    id=data['value'],
                    name=data['name'],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            )
        except IntegrityError as e:
            await connection.execute(
                OriginBrand.__table__.update().values(
                    origin=self.NAME,
                    name=data['name'],
                    updated_at=datetime.now(),
                ).where(OriginBrand.__table__.c.id == data['value'])
            )

        brand_models_url = self.BRAND_MODELS_URL.format(brand=data['value'])
        with aiohttp.ClientSession() as client:
            async with client.get(brand_models_url) as response:
                models_json = await response.json()

        for model in models_json:
            model_id, model_data = await self.prepare_model(connection, data['value'], model)
            models[model_id] = model_data

        print('Brand "{}" is synced'.format(data['name']))
        return data['value'], {
            'models': models,
        }

    async def prepare_model(self, connection, brand_id, data):
        try:
            await connection.execute(
                OriginModel.__table__.insert().values(
                    origin=self.NAME,
                    id=data['value'],
                    brand_id=brand_id,
                    name=data['name'],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            )
        except IntegrityError as e:
            await connection.execute(
                OriginModel.__table__.update().values(
                    origin=self.NAME,
                    name=data['name'],
                    brand_id=brand_id,
                    updated_at=datetime.now(),
                ).where(OriginModel.__table__.c.id == data['value'])
            )

        print('Model "{}" is synced'.format(data['name']))
        return data['value'], {}

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
                'preview': photo_element.attrs.get('src'),
            }
            yield data
