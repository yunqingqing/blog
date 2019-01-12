# -*- encoding: utf-8 -*-
# this is my_app module
import re 

from views import index, hello, not_found

urls = [
    (r'^$', index),
    (r'hello/?$', hello),
]

def app(environ : dict, start_response : callable) -> list:
    # environ is dict-like object containing the WSGI environment
    # refer to the PEP for details

    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        # dispatching url
        match = re.search(regex, path)
        if match is not None:
            environ['myapp.url_args'] = match.groups()
            return callback(environ, start_response)

    return not_found(environ, start_response)
