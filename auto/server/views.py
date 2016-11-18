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

    PER_PAGE = 50

    async def get_json(self):
        fields = [
            'id',
            'is_new',
            'year',
            'price',
            'model_id',
        ]
        select_from = self.table.join(
            self.body_table,
            self.table.c.complectation_id == self.body_table.c.complectation_id,
            isouter=True,
        )
        select_fields = [
            getattr(self.table.c, f) for f in fields
        ] + [
            self.body_table.c.body_type_id,
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
            'fields': fields + ['body_type_id'],
            'rows': rows_data,
        }


class ModelView(BaseApiView):
    body_table = models.Body.__table__
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
        ]
        select_fields = [
            getattr(self.adv_table.c, field) for field in advertisement_fields
        ] + [
            self.body_table.c.body_type_id,
        ]
        select_from = self.adv_table.join(
            self.body_table,
            self.adv_table.c.complectation_id == self.body_table.c.complectation_id,
            isouter=True,
        )
        rows = await self.request.connection.execute(
            sa.select(select_fields)
            .select_from(select_from)
            .where(self.adv_table.c.model_id == model_id)
            .where(self.adv_table.c.price > 0)
            .order_by(self.adv_table.c.price)
        )

        advertisements = []
        fields = advertisement_fields + ['body_type_id']

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
