import h11
from itertools import starmap
import re
import os
from uuid import UUID, uuid4
from urllib import parse

import apsw
import h11
import trio

from giveaway import database
from giveaway import model
from giveaway.registration import view
from giveaway.registration import schema
from giveaway.http import client
from giveaway import oauth


_youtube_token = os.environ["BLUESPAN_YOUTUBE_TOKEN"]


def list_youtube_channels(youtube_channel_id):
    def list_channel_builder(authorization_header):
        request = h11.Request(
            method="GET",
            target="/youtube/v3/channels?" + parse.urlencode({
                "part": "snippet",
                "id": youtube_channel_id,
            }),
            headers=[
                ("host", "www.googleapis.com"),
                ("content-length", "0"),
                authorization_header
            ])
        return request,

    async def do_request():
        async with oauth.authorizer(_youtube_token) as authorize, \
                   client.factory("www.googleapis.com", 443) as make_request:
            data = await client.json_auth_request_factory(list_channel_builder, authorize, make_request)
            return data
    return trio.run(do_request)


def insert_registration(fields):
    cursor = database.connection.cursor()

    giveaway_id, = fields["giveaway:id"]
    giveaway_id = UUID(giveaway_id).bytes
    youtube_channel_id, = fields["youtube:channel-id"]
    youtube_channel_id, = schema._youtube.match(youtube_channel_id).groups()
    discord_username, = fields["discord:username"]
    giveaway_prize_ids = set(
        UUID(giveaway_prize_id).bytes
        for giveaway_prize_id in fields["giveaway-prize:id"]
    )

    registrations = cursor.execute(model.find_duplicate_registration, dict(
        giveaway_id=giveaway_id,
        youtube_channel_id=youtube_channel_id,
        discord_username=discord_username,
    ))
    if list(registrations):
        return {
            "status": "rejected",
            "message":"""

            The youtube channel ID or discord username you entered is already
            registered for this giveaway. If believe you made a mistake during
            your registration and would like to correct it, please message
            bluespan.gg#8616 on Blue Span's discord server.

            """.strip(),
            "giveaway_id": giveaway_id,
        }

    youtube_channels = list_youtube_channels(youtube_channel_id)
    youtube_channel = next(iter(youtube_channels["items"]), None)
    if youtube_channel is None:
        return {
            "status": "rejected",
            "giveaway_id": giveaway_id,
            "message":"""

            The youtube channel ID you entered does not exist.

            """
        }

    with database.connection:
        cursor.execute(model.insert_youtube_channel, dict(
            id=youtube_channel["id"],
            title=youtube_channel["snippet"]["title"]
        ))

        registration_id = uuid4().bytes
        cursor.execute(model.create_registration, dict(
            id=registration_id,
            giveaway_id=giveaway_id,
            youtube_channel_id=youtube_channel["id"],
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


def registrations_closed():
    yield h11.Response(
        status_code=403,
        headers=[
            ("content-type", "text/plain"),
        ]
    )
    yield h11.Data(
        data=b"\n".join([
            b"registrations are currently closed"
            b"\n"
        ])
    )


def form(fields=dict()):
    cursor = database.connection.cursor()
    try:
        giveaway_view = next(cursor.execute(model.get_current_giveaway))
    except StopIteration:
        yield from registrations_closed()
        return
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
        giveaway_id=status["giveaway_id"]
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
