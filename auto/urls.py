from auto import views


class Url:
    def __init__(self, pattern, view, method='GET'):
        self.pattern = pattern
        self.method = method
        self.view = self.get_view(view)

    def get_view(self, view):
        if isinstance(view, str):
            view = getattr(views, view)
        return view


url_patterns = [
    Url(r'/{name:.*}', 'hello')
]