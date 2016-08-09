import json
import sqlalchemy as sa

from aiohttp import web
from aiohttp_jinja2 import render_template
from aiopg.sa import create_engine

from auto import settings
from auto.models import OriginAdvertisement, OriginBrand, OriginModel


async def hello(request):
    name = request.match_info.get('name') or'Anonymous'
    text = 'Hello, ' + name.capitalize()
    return web.Response(body=text.encode('utf-8'))


class IndexView(web.View):
    table = OriginModel.__table__
    brand_table = OriginBrand.__table__

    PER_PAGE = 20

    async def get(self):
        page = int(self.request.GET.get('page', 1))
        offset = (page - 1) * self.PER_PAGE

        async with create_engine(**settings.DATABASE) as engine:
            async with engine.acquire() as connection:
                join = sa.join(self.table, self.brand_table)
                join = join.join(OriginAdvertisement.__table__)
                price_avg = sa.func.avg(OriginAdvertisement.__table__.c.price)
                price_min = sa.func.min(OriginAdvertisement.__table__.c.price)
                price_max = sa.func.max(OriginAdvertisement.__table__.c.price)
                previews = sa.func.array_agg(
                    OriginAdvertisement.__table__.c.preview,
                    order_by=OriginAdvertisement.__table__.c.price,
                )
                query = (sa.select([
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

        models = [{
            'id': row[0],
            'name': row[1],
            'brand': row[2],
            'price_avg': int(row[3]),
            'price_min': int(row[4]),
            'price_max': int(row[5]),
            'preview': get_preview(row[6]),
        } for row in models_rows]

        context = {
            'models_json': json.dumps(models),
            'page': page,
        }

        if self.request.is_ajax:
            return web.Response(
                body=context['models_json'].encode('utf-8'),
                headers={'Content-Type': 'text/json;charset=utf-8'}
            )

        return render_template('index.html', self.request, context)
