import json
import sqlalchemy as sa

from aiohttp import web
from aiohttp_jinja2 import render_template as jinja2_render_template
from functools import partial

import settings

from auto.connection import ConnectionManager
from auto.models import (
    Advertisement,
    BodyType,
    Brand,
    Model,
)


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
    table = Advertisement.__table__

    PER_PAGE = 50

    async def get_json(self):
        fields = [
            'id',
            'is_new',
            'year',
            'price',
            'model_id',
        ]
        rows = await self.request.connection.execute(
            sa.select([getattr(self.table.c, f) for f in fields])
            .where(self.table.c.price > 0)
            .order_by(self.table.c.price)
        )

        rows_data = []
        async for row in rows:
            rows_data.append(row.as_tuple())

        return {
            'fields': fields,
            'rows': rows_data,
        }


class ModelView(BaseApiView):
    brand_table = Brand.__table__
    table = Model.__table__
    adv_table = Advertisement.__table__

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

        query = (
            self.adv_table
            .select()
            .where(self.adv_table.c.model_id == model_id)
            .where(self.adv_table.c.price > 0)
            .order_by(self.adv_table.c.price)
        )
        rows = await self.request.connection.execute(query)

        advertisements = []
        async for row in rows:
            advertisements.append({
                'id': row.id,
                'is_new': row.is_new,
                'name': row.name,
                'price': row.price,
                'year': row.year,
                'preview': row.preview
            })

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
    table = Brand.__table__
    order_by = 'name'


class ModelListView(ApiListView):
    table = Model.__table__
    order_by = 'name'


class BodyTypeListView(ApiListView):
    table = BodyType.__table__
    order_by = 'name'


class BaseAdvertisementRedirectView(web.View):
    table = Advertisement.__table__
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
