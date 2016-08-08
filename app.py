from aiohttp import web

from auto.urls import url_patterns


app = web.Application()

for url in url_patterns:
    app.router.add_route(url.method, url.pattern, url.view)

app_handler = app.make_handler()
