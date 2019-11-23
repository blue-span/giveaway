import json
import os

import h11

from giveaway.winner import presenter


_token = os.environ["BLUESPAN_TOKEN"]


def get(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    token = dict(request.headers).get(b"authorization")
    if token is None or token.decode("utf-8") != _token:
        yield h11.Response(
            status_code=403,
            headers=[],
        )
        return

    obj = presenter.registrations("949553dd-ab29-4ef5-a325-3f10bee3c7ca")

    yield h11.Response(
        status_code=200,
        headers=[
            ("content-type", "application/json"),
        ]
    )

    yield h11.Data(
        data=json.dumps(obj).encode("utf-8")
    )
