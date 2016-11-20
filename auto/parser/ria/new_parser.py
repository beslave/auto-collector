from bs4 import BeautifulSoup
from urllib.parse import urlencode

from auto.parser.ria.base_parser import BaseRiaParser
from auto.utils import (
    has_keys,
    get_absolute_url,
    parse_float_to_int,
    parse_int,
    parse_interval_depended,
    parse_roman,
)


class RiaNewParser(BaseRiaParser):
    ORIGIN = 'ria-new'
    ADVERTISEMENTS_LIST_URL = 'https://auto.ria.com/newauto_blocks/search'
    ADVERTISEMENTS_LIST_URL_PARAMS = {
        'catalog_name': 'category',
        'category_id': 1,
        'is_land': 1,
        'lang_id': 4,
        'limit': 100,
        'order': 15,
        't': 'newdesign/search/search',
        'target': 'newauto_category',
    }
    ADVERTISEMENTS_LIST_API_GETTER = 'read'
    ADVERTISEMENT_API_URL = 'https://auto.ria.com/newauto_blocks/search_ad?lang_id=4&auto_id={}'

    async def get_advertisement_list_data(self, api_data):
        soup = BeautifulSoup(api_data, 'html.parser')
        list_data = []

        for item in soup.select('.ticket-item-newauto'):
            name_element = item.select('.name a')[0]
            photo_element = item.select('.block-photo img')[0]

            advertisement_id = parse_int(name_element.attrs.get('auto_id'))
            preview = photo_element.attrs.get('src', '').strip()

            list_data.append({
                'id': advertisement_id,
                'name': name_element.text.strip(),
                'url': get_absolute_url(name_element.attrs['href'], self.BASE_URL),
                'preview': get_absolute_url(preview, RiaNewParser.BASE_URL)
            })

        return list_data


    async def get_advertisement_data(self, list_item_data):
        advertisement_id = list_item_data['id']
        api_url = self.ADVERTISEMENT_API_URL.format(advertisement_id)
        api_data = await self.get_attempts(api_url)

        if not api_data:
            return {}

        options = api_data.get('options', {})

        parsed_options = {}
        for options_type, type_options in api_data.get('parsed_options', {}).items():
            for cat_options in type_options:
                for option in cat_options:
                    option_id = option['tree_id']
                    option_value = option['val']
                    parsed_options[option_id] = option_value

        data = {
            'id': list_item_data['id'],
            'is_new': True,
            'name': list_item_data['name'],
            'brand': api_data['marka'],
            'model': api_data['model'],
            'complectation': api_data['complete'],
            'url': list_item_data['url'],
            'price': api_data['price_uah'],
            'preview': list_item_data['preview'],
            'year': parse_int(api_data.get('year')),
            'body_type': api_data.get('bodystyle', '').lower(),
            'doors': api_data.get('doors'),
            'seats': api_data.get('seats'),
            'length': api_data.get('length'),
            'width': api_data.get('width'),
            'height': api_data.get('height'),
            'clearance': api_data.get('clearance'),
            'curb_weight': parse_int(options.get(83)),
            'max_allowed_weight': parse_int(options.get(84)),
            'trunk_volume': parse_int(options.get(85)),
            'fuel_tank_volume': parse_int(options.get(86)),
            'wheel_base': parse_int(api_data.get('wheel_base')),
            'bearing_capacity': api_data.get('bearing_capacity'),
            'engine_position': parsed_options.get(44, '').lower(),
            'energy_source': api_data.get('fuel', '').lower(),
            'cylinders_position': parsed_options.get(54, '').lower(),
            'engine_volume': api_data.get('engine'),
            'engine_cylinders': parse_int(api_data.get('cylinders')),
            'engine_valvas_count': parse_int(parsed_options.get(72)),
            'engine_co2_emission': parse_int(parsed_options.get(81)),
            'engine_euro_toxicity_norms': parse_roman(parsed_options.get(358)),
            'engine_fuel_rate_mixed':  api_data.get('fuel_rate'),
            'engine_fuel_rate_urban': options.get(65),
            'engine_fuel_rate_extra_urban': options.get(66),
            'gearbox_type': api_data.get('gear', '').lower(),
            'drive_type': api_data.get('drive', '').lower(),
            'gears_count': parse_int(parsed_options.get(93)),
            'steer_amplifier': parsed_options.get(104, '').lower(),
            'spread_diameter': parse_float_to_int(parsed_options.get(105), 100),
            'max_velocity': api_data.get('spped'),
            'acceleration_time_to_100': parse_float_to_int(api_data.get('acceleration'), 1000),
        }

        if parsed_options.get(62):
            (
                data['engine_power_horses'],
                data['engine_power_rotations_start'],
                data['engine_power_rotations_end'],
            ) = parse_interval_depended(parsed_options[62])

        if parsed_options.get(63):
            (
                data['engine_power_max_torque'],
                data['engine_power_max_torque_rotations_start'],
                data['engine_power_max_torque_rotations_end'],
            ) = parse_interval_depended(parsed_options[63])

        return data
