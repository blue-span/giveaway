from itertools import groupby
import re
from operator import itemgetter
from uuid import UUID

from giveaway import database
from giveaway import model


_youtube = re.compile("^(?:https:\/\/www.youtube.com\/channel\/|)(UC[a-zA-Z0-9~._-]{22})\/?$")


def registrations(giveaway_id):
    cursor = database.connection.cursor()

    registration_prizes = cursor.execute(model.get_registrations_by_prize, dict(
        giveaway_id=giveaway_id
    ))

    def as_object(registration_prize):
        registration_id, youtube_url, discord_username, giveaway_prize_id, prize_title, verified = registration_prize
        youtube_channel_id, = _youtube.match(youtube_url).groups()

        return {
            "registration_id": str(UUID(bytes=registration_id)),
            "youtube_channel_id": youtube_channel_id,
            "discord_username": discord_username,
            "giveaway_prize_id": str(UUID(bytes=giveaway_prize_id)),
            "prize_title": prize_title,
            "verified": verified
        }

    prize_groups = groupby(
        sorted(
            map(as_object, registration_prizes),
            key=itemgetter("giveaway_prize_id")
        ),
        key=itemgetter("giveaway_prize_id")
    )

    return {k: list(v) for k, v in prize_groups}
