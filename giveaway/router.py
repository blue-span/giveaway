from collections import deque
from functools import update_wrapper
import h11
from pathlib import Path
from urllib import parse
import sys
import threading
import os

from giveaway import registration
from giveaway import static


def redirect(path, status_code=301):
    def handler(gen):
        request = next(gen)
        host = dict(request.headers).get(b'host', b"bluespan.gg").decode('utf-8')
        yield h11.Response(
            status_code=status_code,
            headers=[
                ('location', parse.urlunparse(parse.ParseResult(
                    scheme="https",
                    netloc=host,
                    path=path,
                    params="",
                    query="",
                    fragment=""
                )))
            ],
        )
    return update_wrapper(handler, redirect)


routes = {
    (b'GET', b'/giveaway/register'): registration.handler.get,
    (b'GET', b'/giveaway/register'): registration.handler.get,
    (b'POST', b'/giveaway/register'): registration.handler.post,

    (b'GET', b'/giveaway/register/'): redirect('/giveaway/register'),
    (b'GET', b'/giveaway'): redirect('/giveaway/'),
    (b'GET', b'/'): redirect('/giveaway/', 302),
}


static_dir = Path(static.__file__).parent
route_generators = [
    static.handler.make_routes(static_dir, "/static"),
    static.handler.make_routes(os.environ["BLUESPAN_GG_PATH"], "/"),
]


deque((routes.update(dict(gen)) for gen in route_generators), maxlen=0)


def handler_name(handler):
    return (
        ".".join((handler.__module__, handler.__qualname__))
        if handler is not None else
        None
    )


def request_handler(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    def gen():
        yield request
        yield from event_generator

    handler = routes.get((request.method, request.target), None)

    print(
        threading.get_ident(),
        "router",
        request.method, request.target,
        handler_name(handler),
        file=sys.stdout
    )

    if handler is None:
        yield h11.Response(
            status_code=404,
            headers=[
                ('content-type', 'text/plain'),
            ],
        )
        yield h11.Data(data=b'404 Not Found\n')
    else:
        yield from handler(gen())



def https_handler(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    host = dict(request.headers).get(b'host', b"bluespan.gg").decode('utf-8')

    yield h11.Response(
        status_code=301,
        headers=[
            ('location', parse.urlunparse(parse.ParseResult(
                scheme="https",
                netloc=host,
                path=request.target.decode('utf-8'),
                params="",
                query="",
                fragment="",
            )))
        ]
    )
