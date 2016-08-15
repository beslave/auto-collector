import json
import sqlalchemy as sa

from aiohttp import web
from aiohttp_jinja2 import render_template
from aiopg.sa import create_engine
from datetime import datetime
from functools import partial

from auto import settings
from auto.models import OriginAdvertisement, OriginBrand, OriginModel


def json_serialize(obj):
    return str(obj)

smart_json_dumps = partial(json.dumps, default=json_serialize)


class BaseApiView(web.View):
    template_name = 'index.html'

    async def get(self):
        if not self.request.is_ajax:
            return render_template(self.template_name, self.request, {})

        async with create_engine(**settings.DATABASE) as engine:
            async with engine.acquire() as connection:
                data = await self.get_json(connection)

        return web.json_response(data, dumps=smart_json_dumps)


class IndexView(BaseApiView):
    table = OriginAdvertisement.__table__

    PER_PAGE = 50

    async def get_json(self, connection):
        fields = ['year', 'price', 'preview', 'origin_url', 'model_id']
        rows = await connection.execute(
            sa.select([getattr(self.table.c, f) for f in fields])
            .where(self.table.c.price > 0)
            .order_by(self.table.c.price)
        )
        return {
            'fields': fields,
            'rows': list(row.as_tuple() for row in rows),
        }


class ModelView(BaseApiView):
    brand_table = OriginBrand.__table__
    table = OriginModel.__table__
    adv_table = OriginAdvertisement.__table__

    async def get_json(self, connection):
        model_id = int(self.request.match_info['model_id'])
        model_result = await connection.execute(
            self.table.select()
            .where(self.table.c.id == model_id)
            .limit(1)
        )
        model = await model_result.fetchone()

        brand_result = await connection.execute(
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
        adv_rows = list(await connection.execute(query))

        advertisements = [dict(row) for row in adv_rows]

        return {
            'brand': dict(brand),
            'model': dict(model),
            'advertisements': advertisements,
        }


class BrandListView(BaseApiView):
    table = OriginBrand.__table__

    async def get_json(self, connection):
        join = sa.join(self.table, OriginModel.__table__).join(OriginAdvertisement.__table__)
        adv_count = sa.func.count(OriginAdvertisement.__table__.c.id)

        brands_result = await connection.execute(
            self.table.select()
            .select_from(join)
            .where(OriginAdvertisement.__table__.c.price > 0)
            .group_by(self.table.c.id)
            .having(adv_count > 0)
            .order_by(self.table.c.name)
        )
        return [{
            'id': row.id,
            'name': row.name
        } for row in brands_result]


class ModelListView(BaseApiView):
    table = OriginModel.__table__

    async def get_json(self, connection):
        join = sa.join(self.table, OriginAdvertisement.__table__)
        adv_count = sa.func.count(OriginAdvertisement.__table__.c.id)
        models_result = await connection.execute(
            self.table.select()
            .select_from(join)
            .where(OriginAdvertisement.__table__.c.price > 0)
            .group_by(self.table.c.id)
            .having(adv_count > 0)
            .order_by(self.table.c.name)
        )
        return [{
            'id': row.id,
            'name': row.name,
            'brand_id': row.brand_id,
        } for row in models_result]
