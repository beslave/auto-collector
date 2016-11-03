from auto.parser.ria.base_parser import BaseRiaParser
from auto.utils import get_absolute_url, get_first_for_keys


class RiaUsedParser(BaseRiaParser):
    ORIGIN = 'ria-used'
    ADVERTISEMENTS_LIST_URL = 'https://s-ua.auto.ria.com/blocks_search_ajax/search/'
    ADVERTISEMENTS_LIST_URL_PARAMS = {
        'countpage': 100,
    }
    ADV_URL = 'https://c-ua1.riastatic.com/demo/bu/searchPage/v2/view/auto/{}/{}/{}?lang_id=2'

    async def get_advertisement_list_data(self, api_data):
        return api_data['result']['search_result']['ids']

    async def get_advertisement_data(self, adv_id):
        first4 = round(int(adv_id[:5]), -1) // 10
        first6 = round(int(adv_id[:7]), -1) // 10
        adv_id = int(adv_id)
        adv_url = self.ADV_URL.format(first4, first6, adv_id)
        return await self.parse_advertisement(adv_url)

    async def parse_advertisement(self, adv_url):
        data = await self.get_attempts(adv_url)

        preview = get_first_for_keys(data.get('photoData', {}), keys=[
            'seoLinkF',
            'seoLinkM',
            'seoLinkS',
            'seoLinkSX',
        ])
        autoData = data['autoData']

        return {
            'id': autoData['autoId'],
            'is_new': False,
            'origin_url': get_absolute_url(data['linkToView'], self.BASE_URL),
            'name': data['title'].strip(),
            'model_id': data['modelId'],
            'year': autoData.get('year'),
            'price': data['UAH'],
            'preview': preview,
        }
