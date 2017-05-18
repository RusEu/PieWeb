import re

from wsgiref.simple_server import make_server
from urllib.parse import parse_qsl
from http.client import responses


class Response:
    def __init__(self, data={}, status_code=200, headers=[]):
        self.response_data = data
        self.status = f"{status_code} {responses.get(status_code)}"
        self.headers = headers
        if not self.headers:
            self.headers.append(
                ('Content-Type', 'application/json; charset=utf-8')
            )

    def __iter__(self, *args, **kwargs):
        yield f"{self.response_data}".encode('utf-8')


class Request:
    def __init__(self, environ):
        self.request = environ

    @property
    def GET(self):
        return dict(parse_qsl(self.request["QUERY_STRING"]))

    @property
    def POST(self):
        content_length = int(self.request.get('CONTENT_LENGTH', 0))

        if content_length:
            data = self.request['wsgi.input'].read(content_length)
            return dict(parse_qsl(data.decode('utf-8')))
        return {}


class Router:
    def __init__(self):
        self.routes = {}

    def register_route(self, route, fn):
        if route not in self.routes:
            self.routes[route] = fn

    def get_route_from_url(self, url):
        for route in self.routes:
            if re.match(route, url):
                return route
        raise Exception("Route not registered")


class PieWeb:
    def __init__(self, name):
        self.name = name
        self.router = Router()

    def route(self, route):
        def decorator(fn):
            nonlocal self, route
            self.router.register_route(route, fn)

            def wrapper(environ, start_response):

                request = Request(environ)
                response = fn(request)
                start_response(response.status, response.headers)
                return iter(response)
            return wrapper

        return decorator

    def application(self, environ, start_response):
        url_path = environ['PATH_INFO']
        route = self.router.get_route_from_url(url_path)
        fn = self.router.routes[route]
        return self.route(route)(fn)(environ, start_response)

    def run(self):
        with make_server('', 9000, self.application) as server:
            server.serve_forever()

    def __call__(self):
        self.run()
