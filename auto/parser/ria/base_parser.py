import logging

from urllib.parse import urlencode

from auto.parser.base import BaseParser


logger = logging.getLogger('auto.parser.ria')


class BaseRiaParser(BaseParser):
    ORIGIN = None
    BASE_URL = 'https://auto.ria.com'
    BRANDS_URL = 'https://api.auto.ria.com/categories/1/marks'
    MODELS_URL = 'https://api.auto.ria.com/categories/1/marks/{brand}/models'
    ADVERTISEMENTS_LIST_URL = ''
    ADVERTISEMENTS_LIST_URL_PARAMS = {}
    ADVERTISEMENTS_LIST_URL_PAGE_PARAM = 'page'
    ADVERTISEMENTS_LIST_API_GETTER = 'json'

    async def parse_brands(self):
        brands = await self.get_attempts(self.BRANDS_URL)

        for data in brands:
            await self.brand_updater.update({
                'origin': self.ORIGIN,
                'id': data['value'],
                'name': data['name'],
            })

    async def parse_models(self):
        for brand_id in self.brand_updater:
            models_url = self.MODELS_URL.format(brand=brand_id)

            try:
                models = await self.get_attempts(models_url)
            except Exception as e:
                continue

            for data in models:
                await self.model_updater.update({
                    'origin': self.ORIGIN,
                    'id': data['value'],
                    'brand_id': brand_id,
                    'name': data['name'],
                })

    async def parse_advertisements(self):
        getter = self.ADVERTISEMENTS_LIST_API_GETTER
        page = 1

        while True:
            url_params = dict(self.ADVERTISEMENTS_LIST_URL_PARAMS)
            url_params[self.ADVERTISEMENTS_LIST_URL_PAGE_PARAM] = page
            page_url = self.ADVERTISEMENTS_LIST_URL + '?' + urlencode(url_params)
            logger.debug(page_url)
            page += 1

            try:
                api_data = await self.get_attempts(page_url, getter=getter)
            except Exception as e:
                logger.exception(e)
                break

            advertisements_list_data = await self.get_advertisement_list_data(api_data)

            for list_item_data in advertisements_list_data:
                try:
                    adv_data = await self.get_advertisement_data(list_item_data)
                except Exception as e:
                    logger.exception(e)
                    continue

                complectation = await self.parse_complectation(adv_data['id'])

                adv_data.update({
                    'origin': self.ORIGIN,
                    'complectation_id': complectation and complectation['id'],
                })

                advertisement = await self.adv_updater.update(adv_data)

    async def get_advertisement_list_data(self, api_data):
        raise NotImplemented

    async def get_advertisement_data(self, list_item_data):
        raise NotImplemented

    async def parse_complectation(self, advertisement_id):
        pass
