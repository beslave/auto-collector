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
        'lang_id': 2,
        'limit': 100,
        'order': 15,
        't': 'newdesign/search/search',
        'target': 'newauto_category',
    }
    ADVERTISEMENTS_LIST_API_GETTER = 'read'
    ADVERTISEMENT_API_URL = 'https://auto.ria.com/newauto_blocks/search_ad?auto_id={}'

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

    async def parse_complectation(self, advertisement_id):
        api_url = self.ADVERTISEMENT_API_URL.format(advertisement_id)
        api_data = await self.get_attempts(api_url)
        options = api_data.get('options', {})
        
        parsed_options = {}
        for options_type, type_options in api_data.get('parsed_options', {}).items():
            for cat_options in type_options:
                for option in cat_options:
                    option_id = option['tree_id']
                    option_value = option['val']
                    parsed_options[option_id] = option_value

        if not has_keys(api_data, 'complete', 'model_id'):
            return

        complectation = await self.complectation_updater.update({
            'name': api_data['complete'],
            'model_id': api_data['model_id'],
        })

        if has_keys(api_data, 'bodystyle'):
            body_type = await self.body_type_updater.update({
                'name': api_data['bodystyle'].lower()
            })

            body = await self.body_updater.update({
                'complectation_id': complectation['id'],
                'body_type_id': body_type['id'],
                'doors': api_data.get('doors'),
                'seats': api_data.get('seats'),
            })

        dimensions = await self.dimensions_updater.update({
            'complectation_id': complectation['id'],
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
        })
        
        engine_position_id = None
        if has_keys(parsed_options, 44):
            engine_position = await self.engine_position_updater.update({
                'name': parsed_options[44].lower(),
            })
            engine_position_id = engine_position['id']

        energy_source_id = None
        if has_keys(api_data, 'fuel'):
            energy_source = await self.energy_source_updater.update({
                'name': api_data['fuel'].lower(),
            })
            energy_source_id = energy_source['id']

        cylinders_position_id = None
        if parsed_options.get(54):
            cylinders_position = await self.engine_cylinders_position_updater.update({
                'name': parsed_options[54].lower(),
            })
            cylinders_position_id = cylinders_position['id']

        engine = await self.engine_updater.update({
            'complectation_id': complectation['id'],
            'position_id': engine_position_id,
            'energy_source_id': energy_source_id,
            'volume': api_data.get('engine'),
            'cylinders': parse_int(api_data.get('cylinders')),
            'cylinders_position_id': cylinders_position_id,
            'valves_count': parse_int(parsed_options.get(72)),
            'co2_emission': parse_int(parsed_options.get(81)),
            'euro_toxicity_norms': parse_roman(parsed_options.get(358)),
        })

        engine_power_data = {'id': engine['id']}

        if parsed_options.get(62):
            (
                engine_power_data['horses'],
                engine_power_data['rotations_start'],
                engine_power_data['rotations_end'],
            ) = parse_interval_depended(parsed_options[62])

        if parsed_options.get(63):
            (
                engine_power_data['max_torque'],
                engine_power_data['max_torque_rotations_start'],
                engine_power_data['max_torque_rotations_end'],
            ) = parse_interval_depended(parsed_options[63])

        engine_power = await self.engine_power_updater.update(engine_power_data)

        if api_data.get('fuel_rate'):
            engine_fuel_rate = await self.engine_fuel_rate_updater.update({
                'id': engine['id'],
                'mixed': api_data['fuel_rate'],
                'urban': options.get(65),
                'extra_urban': options.get(66),
            })

        gearbox_type_id = None
        if api_data.get('gear'):
            gearbox_type = await self.gearbox_type_updater.update({
                'name': api_data['gear'].lower(),
            })
            gearbox_type_id = gearbox_type['id'],

        drive_type_id = None
        if api_data.get('drive'):
            drive_type = await self.drive_type_updater.update({
                'name': api_data['drive'].lower(),
            })
            drive_type_id = drive_type['id']

        transmission = await self.transmission_updater.update({
            'complectation_id': complectation['id'],
            'gearbox_type_id': gearbox_type_id,
            'gears_count': parse_int(parsed_options.get(93)),
            'drive_type_id': drive_type_id,
        })

        steer_amplifier_id = None
        if parsed_options.get(104):
            steer_amplifier = await self.steer_amplifier_updater.update({
                'name': parsed_options[104].lower(),
            })
            steer_amplifier_id = steer_amplifier['id']

        steering = await self.steering_updater.update({
            'complectation_id': complectation['id'],
            'amplifier_id': steer_amplifier_id,
            'spread_diameter': parse_float_to_int(parsed_options.get(105), 100),
        })

        dynamic_characteristics = await self.dynamic_characteristics_updater.update({
            'complectation_id': complectation['id'],
            'max_velocity': api_data.get('speed'),
            'acceleration_time_to_100': parse_float_to_int(api_data.get('acceleration'), 1000),
        })

        return complectation
