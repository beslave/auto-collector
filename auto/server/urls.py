from aiohttp import web

from auto.server import views


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
    Url(r'/compare/', 'IndexView'),  # compare view
    Url(r'/{pk:\d+}/', 'IndexView'),  # model view

    Url(r'/advertisement/{pk:\d+}/go/', 'RedirectToOriginView'),
    Url(r'/advertisement/{pk:\d+}/preview/', 'AdvertisementPreviewView'),

    Url(r'/api/', 'AutoDataView'),
    Url(r'/api/brands/', 'BrandListView'),
    Url(r'/api/models/', 'ModelListView'),
    Url(r'/api/body-types/', 'BodyTypeListView'),
    Url(r'/api/models/{pk:\d+}/', 'ModelView'),
]
