# -*- encoding: utf-8 -*-
# test middleware

class TestMiddleware(object):
    """The middleware we use."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """Call the application."""
        # 在调用应用程序端之前，先调用middleware做一些处理
        print("middleware do..")
        
        # 调用应用程序并返回
        appiter = self.app(environ, start_response)
        for item in appiter:
            yield item
