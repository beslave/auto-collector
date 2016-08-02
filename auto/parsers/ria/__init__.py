import asyncio
import aiohttp
import json

from bs4 import BeautifulSoup
from psycopg2 import IntegrityError

from auto.models import (
    OriginAdvertisement,
    OriginBrand,
    OriginComplectation,
    OriginModel,
)


class Parser(object):
    NAME = 'ria'
    BASE_LIST_PAGE = 'https://auto.ria.com/newauto_blocks/search?t=newdesign/search/search&limit=100'
    BRANDS_URL = 'https://api.auto.ria.com/categories/1/marks'
    BRAND_MODELS_URL = 'https://api.auto.ria.com/categories/1/marks/{brand}/models'

    def __init__(self):
        self.current_page_url = self.BASE_LIST_PAGE
        self.number = 0
        self.adv_iterator = None

    async def prepare(self, connection):
        self.connection = connection
        with aiohttp.ClientSession() as session:
            async with session.get(self.BRANDS_URL) as response:
                brands_json = await response.read()

                for brand in json.loads(brands_json.decode('utf-8')):
                    await self.prepare_brand(session, brand)

    async def prepare_brand(self, session, data):
        try:
            await self.connection.execute(
                OriginBrand.__table__.insert().values(
                    origin=self.NAME,
                    id=data['value'],
                    name=data['name'],
                )
            )
        except IntegrityError as e:
            await self.connection.execute(
                OriginBrand.__table__.update().values(
                    origin=self.NAME,
                    name=data['name'],
                ).where(OriginBrand.__table__.c.id == data['value'])
            )

        print('Brand "{}" is synced'.format(data['name']))
        brand_models_url = self.BRAND_MODELS_URL.format(brand=data['value'])
        async with session.get(brand_models_url) as response:
            models_json = await response.read()
            for model in json.loads(models_json.decode('utf-8')):
                await self.prepare_model(data['value'], model)

    async def prepare_model(self, brand_id, data):
        try:
            await self.connection.execute(
                OriginModel.__table__.insert().values(
                    origin=self.NAME,
                    id=data['value'],
                    brand_id=brand_id,
                    name=data['name'],
                )
            )
        except IntegrityError as e:
            await self.connection.execute(
                OriginModel.__table__.update().values(
                    origin=self.NAME,
                    name=data['name'],
                    brand_id=brand_id,
                ).where(OriginModel.__table__.c.id == data['value'])
            )

        print('Model "{}" is synced'.format(data['name']))

    def iter_pages(self):
        pass

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
            }
            yield data

    async def parse_advertisement(self, adv):
        self.number += 1
        return self.number

    async def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.current_page_url:
            raise StopAsyncIteration

        if not self.adv_iterator:
            with aiohttp.ClientSession() as session:
                with aiohttp.Timeout(10):
                    async with session.get(self.current_page_url) as response:
                        list_html = await response.read()
                        soup = BeautifulSoup(list_html, 'html.parser')
                        self.adv_iterator = self.iter_advertisements(soup)
                        next_link = soup.select('.pagination .show-more.fl-r')
                        if next_link:
                            next_page = next_link[0].attrs['page']
                            self.current_page_url = self.BASE_LIST_PAGE + '&page=' + next_page
                        else:
                            self.current_page_url = None

        try:
            data = self.adv_iterator.__next__()
            adv_data = {
                'is_new': False,
                'origin': self.NAME,
                'name': data['name'],
                'model_id': data['model_id'],
                'year': data['year'],
            }
            try:
                await self.connection.execute(
                    OriginAdvertisement.__table__.insert().values(
                        id=data['advertisement_id'],
                        **adv_data,
                    )
                )
            except IntegrityError as e:
                await self.connection.execute(
                    OriginAdvertisement.__table__.update().values(
                        **adv_data
                    ).where(OriginAdvertisement.__table__.c.id == data['advertisement_id'])
                )

            print('Advertismenet "{}"" is synced'.format(data['name']))
            return data
        except StopIteration:
            self.adv_iterator = None
            return await self.__anext__()
