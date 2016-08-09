async def is_ajax_middleware_factory(app, handler):
    async def middleware_handler(request):
        request.is_ajax = request.headers.get('X-REQUESTED-WITH') == 'XMLHttpRequest'
        return await handler(request)
    return middleware_handler


middlewares = [
    is_ajax_middleware_factory,
]
