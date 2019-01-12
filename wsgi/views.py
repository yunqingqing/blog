# -*- encoding: utf-8 -*-
# this is view module
from urllib import parse

def index(environ : dict, start_response : callable) -> list:
    """index view."""
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response('200 OK', headers)
    return [b'Index Page.']


def hello(environ : dict, start_response : callable) -> list:
    parameters = parse.parse_qs(environ.get('QUERY_STRING', ''))
    if 'subject' in parameters:
        subject = parameters['subject'][0]
    else:
        subject = 'World'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response('200 OK', headers)
    resp = 'Hello {}.'.format(subject)
    return [resp.encode()]


def not_found(environ : dict, start_response : callable) -> list:
    """404 Page"""
    headers = [('Content-Type', 'text/plain')]
    start_response('404 NOT FOUND', headers)
    return [b'Not Found']