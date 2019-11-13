import h11
from urllib import parse

from giveaway.handlers.registration import view


def get_form():
    'application/x-www-form-urlencoded'


def f():
    data = next(event_generator, None)
    if not isinstance(data, h11.Data):
        yield h11.Response(
            status_code=400,
            headers=[],
        )
        return

    print(parse.parse_qsl(data.data.decode('utf-8')))


def request_handler(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    print(request)

    yield h11.Response(
        status_code=200,
        headers=[
            (b"content-type", b"text/html"),
        ],
    )
    yield h11.Data(
        data=view.render(),
    )
