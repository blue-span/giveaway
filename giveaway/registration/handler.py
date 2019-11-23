import h11

from urllib import parse

from giveaway.lib import starfilter
from giveaway.registration import presenter
from giveaway.registration import schema


def registrations_disabled():
    yield h11.Response(
        status_code=403,
        headers=[
            ("content-type", "text/plain"),
        ]
    )
    yield h11.Data(
        data=b"\n".join([
            b"registrations for the Nov 24 giveaway are currently closed"
            b"\n"
            b"the Dec 8 giveaway registration will open on (or after) Dec 1"
            b"\n"
        ])
    )


def get(event_generator):
    yield from registrations_disabled()
    return

    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    yield from presenter.form()


def post(event_generator):
    yield from registrations_disabled()
    return

    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    data = next(event_generator, None)
    if not isinstance(data, h11.Data):
        yield h11.Response(
            status_code=400,
            headers=[],
        )
        return

    # these forms should be *way* under 32k
    eom = next(event_generator, None)
    if not isinstance(eom, h11.EndOfMessage):
        yield h11.Response(
            status_code=400,
            headers=[],
        )
        return

    qsl = parse.parse_qsl(data.data.decode('utf-8'))
    fields = list(schema.validate(qsl))
    invalid_fields = list(starfilter(lambda _a, _b, explain: explain is not None, fields))

    if invalid_fields:
        yield from presenter.form({k: (v, e) for k, v, e in fields})
    else:
        status = presenter.insert_registration({k: v for k, v, _ in fields})
        yield from presenter.status(status)
