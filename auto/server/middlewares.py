from auto.connection import ConnectionManager


async def is_ajax_middleware_factory(app, handler):
    async def middleware_handler(request):
        request.is_ajax = request.headers.get('X-REQUESTED-WITH') == 'XMLHttpRequest'
        return await handler(request)
    return middleware_handler


async def connection_middleware_factory(app, handler):
    async def connection_handler(request):
        async with ConnectionManager() as connection:
            request.connection = connection
            return await handler(request)
    return connection_handler


middlewares = [
    is_ajax_middleware_factory,
    connection_middleware_factory,
]
