from aiohttp import web
from aiohttp_jinja2 import template
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

    @template('index.html')
    async def get(self):
        async with create_engine(**settings.DATABASE) as engine:
            async with engine.acquire() as connection:
                models = list(await connection.execute(
                    self.table.select().offset(0).limit(self.PER_PAGE)
                ))
        
        return {
            'models': models,
        }
