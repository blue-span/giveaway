import h11
import mimetypes
from pathlib import Path

from giveaway.handlers import registration


def static_handler(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    path = Path(request.target[len(b'/giveaway/'):].decode('utf-8'))

    yield h11.Response(
        status_code=200,
        headers=[
            (b'content-type', b'text/css'),
            (b'content-length', str(path.stat().st_size).encode('utf-8')),
        ]
    )

    with path.open('rb') as f:
        yield h11.Data(
            data=f.read(),
        )


routes = {
    (b'GET', b'/giveaway/register'): registration.request_handler,
    (b'GET', b'/giveaway/css/bluespan-normalize.css'): static_handler,
}


def request_handler(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

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
