from aiohttp import web

from auto import views


class Url:
    def __init__(self, pattern, view, method=None):
        self.pattern = pattern
        self.view = self.get_view(view)
        self.method = method

        if method is None and isinstance(view, web.View):
            self.method = '*'
        elif method is None:
            self.method = 'GET'


    def get_view(self, view):
        if isinstance(view, str):
            view = getattr(views, view)
        return view


url_patterns = [
    Url(r'/', 'IndexView'),
    Url(r'/{model_id:\d+}/', 'ModelView'),

    Url(r'/api/brands', 'BrandListView'),
    Url(r'/api/brands/{brand_id:\d+}/models', 'ModelListView'),
]
