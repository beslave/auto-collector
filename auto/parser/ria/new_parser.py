from bs4 import BeautifulSoup
from urllib.parse import urlencode

from auto.parser.ria.base_parser import BaseRiaParser
from auto.utils import get_absolute_url, parse_int


class RiaNewParser(BaseRiaParser):
    ORIGIN = 'ria-new'
    ADVERTISEMENTS_LIST_URL = 'https://auto.ria.com/newauto_blocks/search'
    ADVERTISEMENTS_LIST_URL_PARAMS = {
        'catalog_name': 'category',
        'category_id': 1,
        'is_land': 1,
        'lang_id': 2,
        'limit': 100,
        'order': 15,
        't': 'newdesign/search/search',
        'target': 'newauto_category',
    }
    ADVERTISEMENTS_LIST_API_GETTER = 'read'

    async def get_advertisement_list_data(self, api_data):
        soup = BeautifulSoup(api_data, 'html.parser')
        return soup.select('.ticket-item-newauto')

    async def get_advertisement_data(self, list_item_data):
        name_element = list_item_data.select('.name a')[0]
        year_element = list_item_data.select('.year')[0]
        price_element = list_item_data.select('.block-price strong')[0]
        photo_element = list_item_data.select('.block-photo img')[0]

        origin_url = name_element.attrs['href']
        origin_url = get_absolute_url(origin_url, RiaNewParser.BASE_URL)
        preview = photo_element.attrs.get('src', '').strip()
        preview = get_absolute_url(preview, RiaNewParser.BASE_URL)

        return {
            'id': parse_int(name_element.attrs.get('auto_id')),
            'is_new': True,
            'origin_url': origin_url,
            'name': name_element.text.strip(),
            'model_id': name_element.attrs.get('model_id'),
            'year': parse_int(year_element.text),
            'price': parse_int(price_element.text),
            'preview': preview,
            # 'autosalon_id': name_element.attrs.get('autosalon_id'),
            # 'marka_id': name_element.attrs.get('marka_id'),
            # 'complectation_id': name_element.attrs.get('complete_id'),
        }
