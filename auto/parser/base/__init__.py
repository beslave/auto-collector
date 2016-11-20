import aiohttp
import asyncio
import logging

from importlib import import_module
from inspect import isclass
from urllib.parse import urlencode

from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


logger = logging.getLogger('auto.parser')


class BaseParser(object):
    ORIGIN = None
    MAX_GET_ATTEMPTS = 5
    BASE_URL = None
    ADVERTISEMENTS_LIST_URL = ''
    ADVERTISEMENTS_LIST_URL_PARAMS = {}
    ADVERTISEMENTS_LIST_URL_PAGE_PARAM = 'page'
    ADVERTISEMENTS_LIST_API_GETTER = 'json'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__instance__

    async def get_attempts(self, url, getter='json'):
        retries = 1
        while True:
            try:
                async with self.client.get(url) as response:
                    if response.status >= 400:
                        print(response.status, response)
                    return await getattr(response, getter)()

            except Exception as e:
                if retries > self.MAX_GET_ATTEMPTS:
                    raise

                await asyncio.sleep(retries * 1)
                retries += 1

    async def init_updaters(self):
        if getattr(self, 'is_initialized', False):
            return

        self.updaters = {}
        origin_updaters = import_module('auto.parser.origin_updaters')

        for Updater in vars(origin_updaters).values():
            if not isclass(Updater) or not issubclass(Updater, OriginUpdater) or Updater is OriginUpdater:
                continue

            updater = await Updater.new(self.ORIGIN)
            self.updaters[updater.name] = updater

        self.is_initialized = True

    async def parse(self):
        await self.init_updaters()
        with aiohttp.ClientSession() as client:
            self.client = client
            await self.parse_advertisements_index()

    async def parse_advertisements_index(self):
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
                    advertisement_data = await self.get_advertisement_data(list_item_data)
                except Exception as e:
                    logger.exception(e)
                    continue

                await self.update_advertisement_data(advertisement_data)

    async def get_advertisement_list_data(self):
        raise NotImplemented

    async def get_advertisement_data(self, list_item_data):
        raise NotImplemented

    async def update_advertisement_data(self, advertisement_data):
        stored_data_per_updater = {}
        updaters = list(self.updaters.values())

        while updaters:
            updater = updaters[0]

            if updater.name in stored_data_per_updater:
                updaters.pop(0)
                continue

            has_unfulfilled_dependencies = False
            for field_dependency in updater.field_dependencies.values():
                dependency_updater_name, dependency_field = field_dependency.split('.')

                if dependency_updater_name not in stored_data_per_updater:
                    dependency_updater = self.updaters[dependency_updater_name]
                    updaters.insert(0, dependency_updater)
                    has_unfulfilled_dependencies = True

            if has_unfulfilled_dependencies:
                continue

            data = {}
            for model_field, api_key in updater.api_fields.items():
                value = advertisement_data.get(api_key)
                data[model_field] = value

            for model_field, field_dependency in updater.field_dependencies.items():
                dependency_updater_name, dependency_field = field_dependency.split('.')
                value = stored_data_per_updater[dependency_updater_name].get(dependency_field)
                data[model_field] = value

            is_valid = True
            required_fields = set(updater.comparable_fields + updater.required_fields)
            for required_field in required_fields:
                value = data.get(required_field)
                if value is None or value == '':
                    is_valid = False
                    break

            if is_valid:
                data = await updater.update(data)
            else:
                data = {}

            stored_data_per_updater[updater.name] = data
