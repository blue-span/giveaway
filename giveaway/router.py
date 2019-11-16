import h11
from pathlib import Path
import sys

from giveaway import registration
from giveaway.handlers import static


routes = {
    (b'GET', b'/giveaway/register'): registration.handler.get,
    (b'POST', b'/giveaway/register'): registration.handler.post,
}

routes.update(dict(static.routes()))


def request_handler(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    def gen():
        yield request
        yield from event_generator

    handler = routes.get((request.method, request.target), None)

    import threading
    print(threading.current_thread(), "router", request.method, request.target, handler, file=sys.stdout)

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
