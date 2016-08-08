from aiohttp import web
from aiohttp_jinja2 import template


async def hello(request):
    name = request.match_info.get('name') or'Anonymous'
    text = 'Hello, ' + name.capitalize()
    return web.Response(body=text.encode('utf-8'))


class IndexView(web.View):
    @template('index.html')
    async def get(self):
        return {
            'key': 'value',
        }
