from auto.parser.ria.base_parser import BaseRiaParser
from auto.utils import get_absolute_url, get_first_for_keys


class RiaUsedParser(BaseRiaParser):
    ORIGIN = 'ria-used'
    ADVERTISEMENTS_LIST_URL = 'https://s-ua.auto.ria.com/blocks_search_ajax/search/?lang_id=4'
    ADVERTISEMENTS_LIST_URL_PARAMS = {
        'countpage': 100,
    }
    ADV_URL = 'https://c-ua1.riastatic.com/demo/bu/searchPage/v2/view/auto/{}/{}/{}?lang_id=4'

    async def get_advertisement_list_data(self, api_data):
        return api_data['result']['search_result']['ids']

    async def get_advertisement_data(self, adv_id):
        first4 = round(int(adv_id[:5]), -1) // 10
        first6 = round(int(adv_id[:7]), -1) // 10
        adv_id = int(adv_id)
        api_url = self.ADV_URL.format(first4, first6, adv_id)
        api_data = await self.get_attempts(api_url)

        if not api_data:
            return {}

        auto_data = api_data.get('autoData')

        preview = get_first_for_keys(api_data.get('photoData', {}), keys=[
            'seoLinkF',
            'seoLinkM',
            'seoLinkS',
            'seoLinkSX',
        ])

        data = {
            'id': auto_data['autoId'],
            'is_new': False,
            'name': api_data['title'].strip(),
            'brand': api_data['markName'],
            'model': api_data['modelName'],
            'complectation': auto_data.get('version'),
            'url': get_absolute_url(api_data['linkToView'], self.BASE_URL),
            'price': api_data.get('UAH'),
            'preview': preview,
            'year': auto_data.get('year'),
        }

        return data
