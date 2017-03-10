import json
import sqlalchemy as sa

from aiohttp import web
from aiohttp_jinja2 import render_template as jinja2_render_template
from functools import partial

import settings

from auto import models
from auto.connection import ConnectionManager


def json_serialize(obj):
    return str(obj)


smart_json_dumps = partial(json.dumps, default=json_serialize)
global_template_context = {
    'settings': settings,
    'static': lambda path: '{}{}'.format(settings.STATIC_URL, path),
}


def render_template(template_name, request, context):
    context = dict(context)
    context.update(global_template_context)
    return jinja2_render_template(template_name, request, context)


class BaseApiView(web.View):
    async def get(self):
        data = await self.get_json()
        return web.json_response(data, dumps=smart_json_dumps)


class IndexView(web.View):
    template_name = 'index.html'

    async def get(self):
        response = render_template(self.template_name, self.request, {})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


class AutoDataView(BaseApiView):
    table = models.Advertisement.__table__
    body_table = models.Body.__table__

    async def get_json(self):
        fields = [
            'id',
            'is_new',
            'year',
            'price',
            'model_id',
            'state_id',
        ]
        select_from = self.table.join(
            self.body_table,
            self.table.c.complectation_id == self.body_table.c.complectation_id,
            isouter=True,
        ).join(
            models.Engine.__table__,
            models.Engine.__table__.c.complectation_id == self.table.c.complectation_id,
            isouter=True,
        )

        select_fields = [
            getattr(self.table.c, f) for f in fields
        ] + [
            self.body_table.c.body_type_id,
            models.Engine.__table__.c.energy_source_id,

        ]

        rows = await self.request.connection.execute(
            sa.select(select_fields)
            .select_from(select_from)
            .where(self.table.c.price > 0)
            .order_by(self.table.c.price)
        )

        rows_data = []
        async for row in rows:
            rows_data.append(row.as_tuple())

        return {
            'fields': fields + [
                'body_type_id',
                'energy_source_id',
            ],
            'rows': rows_data,
        }


class ModelView(BaseApiView):
    brand_table = models.Brand.__table__
    table = models.Model.__table__
    adv_table = models.Advertisement.__table__

    async def get_json(self):
        model_id = int(self.request.match_info['pk'])
        model_result = await self.request.connection.execute(
            self.table.select()
            .where(self.table.c.id == model_id)
            .limit(1)
        )
        model = await model_result.fetchone()

        brand_result = await self.request.connection.execute(
            self.brand_table.select()
            .where(self.brand_table.c.id == model.brand_id)
            .limit(1)
        )
        brand = await brand_result.fetchone()

        advertisement_fields = [
            'id',
            'is_new',
            'name',
            'price',
            'year',
            'preview',
            'state_id',
        ]
        select_fields = [
            getattr(self.adv_table.c, field) for field in advertisement_fields
        ] + [
            models.Body.__table__.c.doors,
            models.Body.__table__.c.seats,
            models.BodyType.__table__.c.id,
            models.BodyType.__table__.c.name,
            models.Dimensions.__table__.c.length,
            models.Dimensions.__table__.c.width,
            models.Dimensions.__table__.c.height,
            models.Dimensions.__table__.c.clearance,
            models.Dimensions.__table__.c.curb_weight,
            models.Dimensions.__table__.c.max_allowed_weight,
            models.Dimensions.__table__.c.trunk_volume,
            models.Dimensions.__table__.c.fuel_tank_volume,
            models.Dimensions.__table__.c.wheel_base,
            models.Dimensions.__table__.c.bearing_capacity,
            models.EnginePosition.__table__.c.name,
            models.EnergySource.__table__.c.id,
            models.EnergySource.__table__.c.name,
            models.Engine.__table__.c.volume,
            models.Engine.__table__.c.cylinders,
            models.EngineCylindersPosition.__table__.c.name,
            models.EnginePower.__table__.c.horses,
            models.EnginePower.__table__.c.rotations_start,
            models.EnginePower.__table__.c.rotations_end,
            models.EnginePower.__table__.c.max_torque,
            models.EnginePower.__table__.c.max_torque_rotations_start,
            models.EnginePower.__table__.c.max_torque_rotations_end,
            models.EngineFuelRate.__table__.c.mixed,
            models.EngineFuelRate.__table__.c.urban,
            models.EngineFuelRate.__table__.c.extra_urban,
            models.Engine.__table__.c.valves_count,
            models.Engine.__table__.c.co2_emission,
            models.Engine.__table__.c.euro_toxicity_norms,
            models.GearboxType.__table__.c.name,
            models.Transmission.__table__.c.gears_count,
            models.DriveType.__table__.c.name,
            models.SteerAmplifier.__table__.c.name,
            models.Steering.__table__.c.spread_diameter,
            models.DynamicCharacteristics.__table__.c.max_velocity,
            models.DynamicCharacteristics.__table__.c.acceleration_time_to_100,
        ]

        select_from = self.adv_table.join(
            models.Complectation.__table__,
            self.adv_table.c.complectation_id == models.Complectation.__table__.c.id,
            isouter=True,
        ).join(
            models.Body.__table__,
            models.Complectation.__table__.c.id == models.Body.__table__.c.complectation_id,
            isouter=True,
        ).join(
            models.BodyType.__table__,
            models.Body.__table__.c.body_type_id == models.BodyType.__table__.c.id,
            isouter=True,
        ).join(
            models.Dimensions.__table__,
            models.Dimensions.__table__.c.complectation_id == models.Complectation.__table__.c.id,
            isouter=True,
        ).join(
            models.Engine.__table__,
            models.Engine.__table__.c.complectation_id == models.Complectation.__table__.c.id,
            isouter=True,
        ).join(
            models.EnginePosition.__table__,
            models.EnginePosition.__table__.c.id == models.Engine.__table__.c.position_id,
            isouter=True,
        ).join(
            models.EnergySource.__table__,
            models.EnergySource.__table__.c.id == models.Engine.__table__.c.energy_source_id,
            isouter=True,
        ).join(
            models.EngineCylindersPosition.__table__,
            models.EngineCylindersPosition.__table__.c.id == models.Engine.__table__.c.cylinders_position_id,
            isouter=True,
        ).join(
            models.EnginePower.__table__,
            models.EnginePower.__table__.c.id == models.Engine.__table__.c.id,
            isouter=True,
        ).join(
            models.EngineFuelRate.__table__,
            models.EngineFuelRate.__table__.c.id == models.Engine.__table__.c.id,
            isouter=True,
        ).join(
            models.Transmission.__table__,
            models.Transmission.__table__.c.complectation_id == models.Complectation.__table__.c.id,
            isouter=True,
        ).join(
            models.GearboxType.__table__,
            models.GearboxType.__table__.c.id == models.Transmission.__table__.c.gearbox_type_id,
            isouter=True,
        ).join(
            models.DriveType.__table__,
            models.DriveType.__table__.c.id == models.Transmission.__table__.c.drive_type_id,
            isouter=True,
        ).join(
            models.Steering.__table__,
            models.Steering.__table__.c.complectation_id == models.Complectation.__table__.c.id,
            isouter=True,
        ).join(
            models.SteerAmplifier.__table__,
            models.SteerAmplifier.__table__.c.id == models.Steering.__table__.c.amplifier_id,
            isouter=True,
        ).join(
            models.DynamicCharacteristics.__table__,
            models.DynamicCharacteristics.__table__.c.complectation_id == models.Complectation.__table__.c.id,
            isouter=True,
        )

        rows = await self.request.connection.execute(
            sa.select(select_fields, use_labels=True)
            .select_from(select_from)
            .where(self.adv_table.c.model_id == model_id)
            .where(self.adv_table.c.price > 0)
            .order_by(self.adv_table.c.price)
        )

        advertisements = []
        fields = advertisement_fields + [
            'doors',
            'seats',
            'body_type_id',
            'body_type',
            'length',
            'width',
            'height',
            'clearance',
            'curb_weight',
            'max_allowed_weight',
            'trunk_volume',
            'fuel_tank_volume',
            'wheel_base',
            'bearing_capacity',
            'engine_position',
            'energy_source_id',
            'energy_source',
            'engine_volume',
            'engine_cylinders',
            'engine_cylinders_position',
            'engine_horses',
            'engine_rotations_start',
            'engine_rotations_end',
            'engine_max_torque',
            'engine_max_torque_rotations_start',
            'engine_max_torque_rotations_end',
            'engine_fuel_rate_mixed',
            'engine_fuel_rate_urban',
            'engine_fuel_rate_extra_urban',
            'engine_valves_count',
            'engine_co2_emission',
            'engine_euro_toxicity_norms',
            'gearbox_type',
            'gears_count',
            'drive_type',
            'steer_amplifier',
            'spread_diameter',
            'max_velocity',
            'acceleration_time_to_100',
        ]

        async for row in rows:
            data = dict(zip(fields, row.as_tuple()))
            advertisements.append(data)

        data = dict(model)
        data['full_title'] = '{brand} {model}'.format(
            brand=brand.name,
            model=model.name,
        )
        data['advertisements'] = advertisements

        return data


class ApiListView(BaseApiView):
    table = None
    order_by = 'id'

    async def get_json(self):
        rows = await self.request.connection.execute(
            self.table.select()
            .order_by(getattr(self.table.c, self.order_by))
        )

        data = []
        async for row in rows:
            data.append(dict(row))

        return data


class BrandListView(ApiListView):
    table = models.Brand.__table__
    order_by = 'name'


class ModelListView(ApiListView):
    table = models.Model.__table__
    order_by = 'name'


class BodyTypeListView(ApiListView):
    table = models.BodyType.__table__
    order_by = 'name'


class EnergySourceListView(ApiListView):
    table = models.EnergySource.__table__
    order_by = 'name'


class StateListView(ApiListView):
    table = models.State.__table__
    order_by = 'name'


class BaseAdvertisementRedirectView(web.View):
    table = models.Advertisement.__table__
    cache = {}

    async def get(self):
        pk = int(self.request.match_info['pk'])
        rows = await self.request.connection.execute(
            self.table.select().where(self.table.c.id == pk)
            .limit(1)
        )
        instance = await rows.fetchone()
        self.cache[pk] = getattr(instance, self.redirect_field)

        return web.HTTPFound(self.cache[pk])


class RedirectToOriginView(BaseAdvertisementRedirectView):
    redirect_field = 'origin_url'


class AdvertisementPreviewView(BaseAdvertisementRedirectView):
    redirect_field = 'preview'
