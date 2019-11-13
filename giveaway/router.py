import h11
from pathlib import Path
import sys

from giveaway.handlers import registration
from giveaway.handlers import static

g
routes = {
    (b'GET', b'/giveaway/register'): registration.request_handler,
}

routes.update(dict(static.routes()))


def request_handler(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    import threading
    print(threading.current_thread(), "router", request.method, request.target, file=sys.stdout)

    def gen():
        yield request
        yield from event_generator

    handler = routes.get((request.method, request.target), None)

    if handler is None:
        yield h11.Response(
            status_code=404,
            headers=[],
        )
    else:
        yield from handler(gen())
