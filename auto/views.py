import json
import sqlalchemy as sa

from aiohttp import web
from aiohttp_jinja2 import render_template
from functools import partial

from auto import settings
from auto.connection import ConnectionManager
from auto.models import Advertisement, Brand, Model


def json_serialize(obj):
    return str(obj)

smart_json_dumps = partial(json.dumps, default=json_serialize)


class BaseApiView(web.View):
    template_name = 'index.html'

    async def get(self):
        if self.template_name and not self.request.is_ajax:
            return render_template(self.template_name, self.request, {})

        data = await self.get_json()

        return web.json_response(data, dumps=smart_json_dumps)


class IndexView(web.View):
    template_name = 'index.html'

    async def get(self):
        return render_template(self.template_name, self.request, {})


class AutoDataView(BaseApiView):
    table = Advertisement.__table__
    template_name = None

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
                'name': row.name,
                'price': row.price,
                'year': row.year,
                'preview': row.preview
            })

        return {
            'brand': dict(brand),
            'model': dict(model),
            'advertisements': advertisements,
        }


class BrandListView(BaseApiView):
    table = Brand.__table__

    async def get_json(self):
        join = sa.join(self.table, Model.__table__).join(Advertisement.__table__)
        adv_count = sa.func.count(Advertisement.__table__.c.id)

        rows = await self.request.connection.execute(
            self.table.select()
            .select_from(join)
            .where(Advertisement.__table__.c.price > 0)
            .group_by(self.table.c.id)
            .having(adv_count > 0)
            .order_by(self.table.c.id)
        )

        data = []
        async for row in rows:
            data.append({
                'id': row.id,
                'name': row.name
            })

        return data


class ModelListView(BaseApiView):
    table = Model.__table__

    async def get_json(self):
        join = sa.join(self.table, Advertisement.__table__)
        adv_count = sa.func.count(Advertisement.__table__.c.id)
        rows = await self.request.connection.execute(
            self.table.select()
            .select_from(join)
            .where(Advertisement.__table__.c.price > 0)
            .group_by(self.table.c.id)
            .having(adv_count > 0)
            .order_by(self.table.c.id)
        )

        data = []
        async for row in rows:
            data.append({
                'id': row.id,
                'name': row.name,
                'brand_id': row.brand_id,
            })

        return data


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
