from wsgiref.simple_server import make_server

from my_app import app
from middleware import TestMiddleware


httpd = make_server('localhost', 8000, TestMiddleware(app))
httpd.serve_forever()