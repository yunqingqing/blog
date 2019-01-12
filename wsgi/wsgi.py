# -*- encoding: utf-8 -*-
from my_app import app
from middleware import TestMiddleware

application = TestMiddleware(app)
