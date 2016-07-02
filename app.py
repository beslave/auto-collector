import asyncio

from aiohttp import web

from auto import tasks as auto_tasks


async def test(i=0):
    while True:
        i += 1
        print('DEBUG timer:', i)
        await asyncio.sleep(1)


async def hello(request):
    name = request.match_info.get('name') or'Anonymous'
    text = 'Hello, ' + name.capitalize()
    return web.Response(body=text.encode('utf-8'))

loop = asyncio.get_event_loop()
app = web.Application(loop=loop)
app.router.add_route('GET', r'/{name:.*}', hello)
app_handler = app.make_handler()
tasks = [
    asyncio.ensure_future(auto_tasks.sync_data_task()),
    asyncio.ensure_future(test()),
    loop.create_server(app_handler, '0.0.0.0', 8080),
]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
