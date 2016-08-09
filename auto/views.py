import json

from aiohttp import web
from aiohttp_jinja2 import render_template
from aiopg.sa import create_engine

from auto import settings
from auto.models import OriginModel


async def hello(request):
    name = request.match_info.get('name') or'Anonymous'
    text = 'Hello, ' + name.capitalize()
    return web.Response(body=text.encode('utf-8'))


class IndexView(web.View):
    table = OriginModel.__table__
    PER_PAGE = 20

    async def get(self):
        page = int(self.request.GET.get('page', 1))
        offset = page * self.PER_PAGE

        async with create_engine(**settings.DATABASE) as engine:
            async with engine.acquire() as connection:
                models_result = list(await connection.execute(
                    self.table.select().offset(offset).limit(self.PER_PAGE)
                ))

        models = [{
            'id': model.id,
            'name': model.name,
        } for model in models_result]

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
