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
    table = OriginModel.__table__
    brand_table = OriginBrand.__table__

    PER_PAGE = 20

    async def get_json(self, connection):
        page = int(self.request.GET.get('page', 1))
        offset = (page - 1) * self.PER_PAGE

        join = sa.join(self.table, self.brand_table)
        join = join.join(OriginAdvertisement.__table__)
        price_avg = sa.func.avg(OriginAdvertisement.__table__.c.price)
        price_min = sa.func.min(OriginAdvertisement.__table__.c.price)
        price_max = sa.func.max(OriginAdvertisement.__table__.c.price)
        previews = sa.func.array_agg(
            OriginAdvertisement.__table__.c.preview,
            order_by=OriginAdvertisement.__table__.c.price,
        )
        query = (
            sa.select([
                self.table.c.id,
                self.table.c.name,
                self.brand_table.c.name,
                price_avg.label('price_average'),
                price_min.label('price_min'),
                price_max.label('price_max'),
                previews.label('previews'),
            ], use_labels=True)
            .select_from(join)
            .where(OriginAdvertisement.__table__.c.price > 0)
            .group_by(self.brand_table.c.id, self.table.c.id)
            .order_by(price_avg)
            .having(price_avg > 0)
            .offset(offset).limit(self.PER_PAGE)
        )

        models_rows = list(await connection.execute(query))

        def get_preview(previews):
            previews = sorted(filter(None, previews))
            if previews:
                return previews[0]

        return [{
            'id': row[0],
            'name': row[1],
            'brand': row[2],
            'price_avg': int(row[3]),
            'price_min': int(row[4]),
            'price_max': int(row[5]),
            'preview': get_preview(row[6]),
        } for row in models_rows]


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
