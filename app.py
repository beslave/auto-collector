import aiohttp_jinja2
import jinja2

from aiohttp import web

from auto import settings
from auto.middlewares import middlewares
from auto.urls import url_patterns


app = web.Application(middlewares=middlewares)

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(settings.TEMPLATE_DIR))

app.router.add_static(settings.STATIC_URL, settings.STATIC_ROOT)

for url in url_patterns:
    app.router.add_route(url.method, url.pattern, url.view)

app_handler = app.make_handler()
