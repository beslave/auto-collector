import aiohttp_jinja2
import asyncio
import jinja2

from aiohttp import web

from auto import settings
from auto.server.middlewares import middlewares
from auto.server.urls import url_patterns


loop = asyncio.get_event_loop()
app = web.Application(middlewares=middlewares)

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(settings.TEMPLATE_DIR))

for url in url_patterns:
    app.router.add_route(url.method, url.pattern, url.view)

app_handler = app.make_handler()


async def serve_task():
    return await loop.create_server(
        app_handler,
        settings.SITE_ADDR,
        settings.SITE_PORT
    )


tasks = [serve_task]
