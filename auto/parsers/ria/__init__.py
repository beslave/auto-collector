from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlencode

from auto.parsers.base import BaseParser
from auto.utils import get_absolute_url, parse_int


class Parser(BaseParser):
    NAME = 'ria'
    BASE_URL = 'https://auto.ria.com'
    BASE_LIST_PAGE = 'https://auto.ria.com/newauto_blocks/search?' + urlencode({
        'catalog_name': 'category',
        'category_id': 1,
        'is_land': 1,
        'lang_id': 2,
        'limit': 100,
        'order': 15,
        't': 'newdesign/search/search',
        'target': 'newauto_category',
    })
    BRANDS_URL = 'https://api.auto.ria.com/categories/1/marks'
    MODELS_URL = 'https://api.auto.ria.com/categories/1/marks/{brand}/models'

    async def parse_brands(self, client):
        async with client.get(self.BRANDS_URL) as response:
            brands = await response.json()

        for data in brands:
            await self.brand_updater.update({
                'origin': self.NAME,
                'id': data['value'],
                'name': data['name'],
                'updated_at': datetime.now(),
            })

    async def parse_models(self, client):
        for brand_id in self.brand_updater:
            MODELS_URL = self.MODELS_URL.format(brand=brand_id)
            async with client.get(MODELS_URL) as response:
                models = await response.json()

            for data in models:
                await self.model_updater.update({
                    'origin': self.NAME,
                    'id': data['value'],
                    'brand_id': brand_id,
                    'name': data['name'],
                    'updated_at': datetime.now(),
                })

    async def parse_advertisements(self, client):
        page_url = self.BASE_LIST_PAGE
        retries = 0
        while page_url and retries < self.MAX_RETRIES:
            try:
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
                'id': parse_int(name_element.attrs.get('auto_id')),
                'is_new': True,
                'origin': self.NAME,
                'origin_url': origin_url,
                'name': name_element.text.strip(),
                'model_id': name_element.attrs.get('model_id'),
                'year': parse_int(year_element.text),
                'price': parse_int(price_element.text),
                'updated_at': datetime.now(),
                'preview': preview,
                # 'autosalon_id': name_element.attrs.get('autosalon_id'),
                # 'marka_id': name_element.attrs.get('marka_id'),
                # 'complectation_id': name_element.attrs.get('complete_id'),
            }
