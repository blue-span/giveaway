import h11
from itertools import starmap
import re

from uuid import UUID, uuid4

import apsw

from giveaway import database
from giveaway import model
from giveaway.registration import view
from giveaway.registration import schema


def insert_registration(fields):
    cursor = database.connection.cursor()

    giveaway_id, = fields["giveaway:id"]
    giveaway_id = UUID(giveaway_id).bytes
    youtube_url, = fields["youtube:url"]
    youtube_url, = schema._youtube.match(youtube_url).groups()
    discord_username, = fields["discord:username"]
    giveaway_prize_ids = set(
        UUID(giveaway_prize_id).bytes
        for giveaway_prize_id in fields["giveaway-prize:id"]
    )

    registrations = cursor.execute(model.find_duplicate_registration, dict(
        giveaway_id=giveaway_id,
        youtube_url=youtube_url,
        discord_username=discord_username,
    ))
    if list(registrations):
        return {
            "status": "rejected",
            "message":"""

            The youtube url or discord username you entered is already
            registered for this giveaway. If believe you made a mistake during
            your registration and would like to correct it, please message
            bluespan.gg#8616 on Blue Span's discord server.

            """.strip(),
            "giveaway_id": giveaway_id,
        }

    with database.connection:
        registration_id = uuid4().bytes
        cursor.execute(model.create_registration, dict(
            id=registration_id,
            giveaway_id=giveaway_id,
            youtube_url=youtube_url,
            discord_username=discord_username,
            verified=False,
        ))

        cursor.executemany(model.add_registration_prize, (dict(
            id=uuid4().bytes,
            registration_id=registration_id,
            giveaway_prize_id=giveaway_prize_id,
        ) for giveaway_prize_id in giveaway_prize_ids))

        return {
            "status": "accepted",
            "message": """

            Your registration is has been accepted, pending a review of your
            conformance with giveaway eligibility requirements. If you are a
            legitimate regular stream viewer, you have absolutely nothing to
            worry about.

            """.strip(),
            "registration_id": UUID(bytes=registration_id),
            "giveaway_id": giveaway_id,
        }


def form(fields=dict()):
    cursor = database.connection.cursor()
    giveaway_view = next(cursor.execute(model.get_current_giveaway))
    giveaway_id, _ = giveaway_view
    prize_view = cursor.execute(model.get_prizes_for_giveaway, dict(
        giveaway_id=giveaway_id
    ))

    yield h11.Response(
        status_code=200,
        headers=[
            (b"content-type", b"text/html"),
        ],
    )
    yield h11.Data(
        data=view.render_form(
            giveaway_view=giveaway_view,
            prize_view=prize_view,
            field_state=fields,
        ),
    )


def status(status):
    cursor = database.connection.cursor()
    giveaway_title, = next(cursor.execute(model.get_giveaway_title, dict(
        giveaway_id=UUID(status["giveaway_id"]).bytes
    )))
    yield h11.Response(
        status_code=200,
        headers=[
            (b"content-type", b"text/html"),
        ],
    )
    yield h11.Data(
        data=view.render_status(
            giveaway_title=giveaway_title,
            **status,
        ),
    )
