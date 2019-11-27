import h11

from urllib import parse

from giveaway.lib import starfilter
from giveaway.registration import presenter
from giveaway.registration import schema


def get(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    yield from presenter.form()


def post(event_generator):
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
