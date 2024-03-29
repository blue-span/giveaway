import json
import os

import h11

from giveaway.winner import presenter
from giveaway import database
from giveaway import model


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

    cursor = database.connection.cursor()
    giveaway_view = next(cursor.execute(model.get_current_giveaway), None)
    if False and giveaway_view is None:
        yield h11.Response(
            status_code=404,
            headers=[],
        )

    else:
        #giveaway_id, _ = giveaway_view
        from uuid import UUID
        obj = presenter.registrations(UUID("15718946-d2d9-47b5-bbf4-7878266349d3").bytes)

        yield h11.Response(
            status_code=200,
            headers=[
                ("content-type", "application/json"),
            ]
        )

        yield h11.Data(
            data=json.dumps(obj).encode("utf-8")
        )
