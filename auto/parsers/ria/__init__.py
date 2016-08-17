import asyncio
import logging

from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor
from urllib.parse import urlencode

from auto import settings
from auto.parsers.base import BaseParser
from auto.utils import get_absolute_url, get_first_for_keys, parse_int


logger = logging.getLogger('auto.parsers.ria')
executor = ProcessPoolExecutor()
loop = asyncio.get_event_loop()


class BaseRiaParser(BaseParser):
    BASE_URL = 'https://auto.ria.com'
    BRANDS_URL = 'https://api.auto.ria.com/categories/1/marks'
    MODELS_URL = 'https://api.auto.ria.com/categories/1/marks/{brand}/models'

    async def parse_brands(self, client):
        brands = await self.get_attempts(client, self.BRANDS_URL)

        for data in brands:
            await self.brand_updater.update({
                'origin': self.ORIGIN,
                'id': data['value'],
                'name': data['name'],
            })

    async def parse_models(self, client):
        for brand_id in self.brand_updater:
            models_url = self.MODELS_URL.format(brand=brand_id)

            try:
                models = await self.get_attempts(client, models_url)
            except Exception as e:
                continue

            for data in models:
                await self.model_updater.update({
                    'origin': self.ORIGIN,
                    'id': data['value'],
                    'brand_id': brand_id,
                    'name': data['name'],
                })


def parse_advertisements_list_html(list_html):
    data = []
    soup = BeautifulSoup(list_html, 'html.parser')

    for adv_element in soup.select('.ticket-item-newauto'):
        name_element = adv_element.select('.name a')[0]
        year_element = adv_element.select('.year')[0]
        price_element = adv_element.select('.block-price strong')[0]
        photo_element = adv_element.select('.block-photo img')[0]

        origin_url = name_element.attrs['href']
        origin_url = get_absolute_url(origin_url, RiaNewParser.BASE_URL)
        preview = photo_element.attrs.get('src', '').strip()
        preview = get_absolute_url(preview, RiaNewParser.BASE_URL)
        data.append({
            'id': parse_int(name_element.attrs.get('auto_id')),
            'is_new': True,
            'origin': RiaNewParser.ORIGIN,
            'origin_url': origin_url,
            'name': name_element.text.strip(),
            'model_id': name_element.attrs.get('model_id'),
            'year': parse_int(year_element.text),
            'price': parse_int(price_element.text),
            'preview': preview,
            # 'autosalon_id': name_element.attrs.get('autosalon_id'),
            # 'marka_id': name_element.attrs.get('marka_id'),
            # 'complectation_id': name_element.attrs.get('complete_id'),
        })

    next_link = soup.select('.pagination .show-more.fl-r')
    next_page = next_link and next_link[0].attrs['page']

    return data, next_page


class RiaNewParser(BaseRiaParser):
    ORIGIN = 'ria-new'
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

    async def parse_advertisements(self, client):
        page_url = self.BASE_LIST_PAGE
        while page_url:
            try:
                list_html = await self.get_attempts(client, page_url, getter='read')
            except Exception as e:
                break

            advertisements, next_page = await loop.run_in_executor(
                executor,
                parse_advertisements_list_html,
                list_html,
            )

            for adv_data in advertisements:
                await self.adv_updater.update(adv_data)

            page_url = next_page and self.BASE_LIST_PAGE + '&page=' + next_page


class RiaUsedParser(BaseRiaParser):
    ORIGIN = 'ria-used'
    BASE_LIST_PAGE = 'https://s-ua.auto.ria.com/blocks_search_ajax/search/?' + urlencode({
        'countpage': 100,
    })
    ADV_URL = 'https://c-ua1.riastatic.com/demo/bu/searchPage/v2/view/auto/{}/{}/{}?lang_id=2'

    async def parse_advertisements(self, client):
        page = 1
        retries = 0
        while True:
            page_url = self.BASE_LIST_PAGE + '&page={}'.format(page)
            page += 1

            try:
                result = await self.get_attempts(client, page_url)
                ids = result['result']['search_result']['ids']
            except Exception as e:
                continue

            for adv_id in ids:
                first4 = round(int(adv_id[:5]), -1) // 10
                first6 = round(int(adv_id[:7]), -1) // 10
                adv_id = int(adv_id)
                adv_url = self.ADV_URL.format(first4, first6, adv_id)

                try:
                    await self.parse_advertisement(client, adv_url)
                except Exception as e:
                    logger.exception(e)

    async def parse_advertisement(self, client, adv_url):
        try:
            data = await self.get_attempts(client, adv_url)
        except Exception:
            return

        preview = get_first_for_keys(data.get('photoData', {}), keys=[
            'seoLinkF',
            'seoLinkM',
            'seoLinkS',
            'seoLinkSX',
        ])
        autoData = data['autoData']

        await self.adv_updater.update({
            'id': autoData['autoId'],
            'is_new': False,
            'origin_url': get_absolute_url(data['linkToView'], self.BASE_URL),
            'name': data['title'].strip(),
            'model_id': data['modelId'],
            'year': autoData.get('year'),
            'price': data['UAH'],
            'preview': preview,
        })
