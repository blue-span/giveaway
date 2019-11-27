import datetime
import sys
from uuid import UUID

import apsw
import pytz

from giveaway import model
from giveaway import database


PT = pytz.timezone("America/Los_Angeles")
timestamp = lambda *a, **kw: int(PT.localize(datetime.datetime(*a, **kw)).timestamp())


# giveaway

giveaways = [
    {
        "id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes,
        "title": "Nov 24",
        "start_ts": timestamp(2019, 11, 13, hour=0, minute=0),
        "end_ts": timestamp(2019, 11, 24, hour=11, minute=59, second=59)
    },
    {
        "id": UUID("15718946-d2d9-47b5-bbf4-7878266349d3").bytes,
        "title": "Dec 8",
        #"start_ts": timestamp(2019, 11, 29, hour=0, minute=0),
        "start_ts": timestamp(2019, 11, 26, hour=17, minute=0),
        "end_ts": timestamp(2019, 12, 7, hour=6, minute=0)
    }
]

# prize

prizes = [
    {
        "id": UUID("76bfea4a-aad1-4938-b638-23d51eaa0a67").bytes,
        "title": "AMD Gaming Computer",
        "image_src": "/static/images/amd-ryzen-radeon.png",
        "theme": "amd-red"
    },
    {
        "id": UUID("6c6f1ffc-89ec-402b-b454-ecc826111ec6").bytes,
        "title": "Warcraft 3: Reforged",
        "image_src": "/static/images/warcraft-reforged.png",
        "theme": "warcraft-yellow"
    },
    {
        "id": UUID("2725611e-1c22-4841-a211-45538600f432").bytes,
        "title": "SteelSeries Peripherals",
        "image_src": "/static/images/steelseries.png",
        "theme": "steelseries-black"
    },
    {
        "id": UUID("e9eb6dab-fd47-44e1-a240-de19b6d2bede").bytes,
        "title": "Breville the Tea Maker",
        "image_src": "/static/images/breville.png",
        "theme": "breville-purple"
    },
    {
        "id": UUID("6f85f14a-0da6-48e2-abf5-a1947094ac49").bytes,
        "title": "Fake Prize",
        "image_src": "fake.png",
        "theme": "fake-theme"
    }
]

# giveaway_prize

giveaway_prizes = [
    {
        "id": UUID("f7b0b621-1e16-4881-ad24-1986c3bf4a59").bytes,
        "giveaway_id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes, # Nov 24
        "prize_id": UUID("76bfea4a-aad1-4938-b638-23d51eaa0a67").bytes, # AMD Gaming Computer
        "quantity": 1,
        "featured": 1
    },
    {
        "id": UUID("32ad6a64-2894-4e43-8cea-6d9dcec50077").bytes,
        "giveaway_id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes, # Nov 24
        "prize_id": UUID("6c6f1ffc-89ec-402b-b454-ecc826111ec6").bytes, # Warcraft 3: Reforged
        "quantity": 1,
        "featured": 0
    },
    {
        "id": UUID("479f00cd-43c6-4f9b-913f-d2dbe705486d").bytes,
        "giveaway_id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes, # Nov 24
        "prize_id": UUID("2725611e-1c22-4841-a211-45538600f432").bytes, # SteelSeries Peripherals
        "quantity": 1,
        "featured": 0
    },
    {
        "id": UUID("82e10303-5c8b-498c-a569-d46b88a3749b").bytes,
        "giveaway_id": UUID("15718946-d2d9-47b5-bbf4-7878266349d3").bytes, # Dec 8
        "prize_id": UUID("76bfea4a-aad1-4938-b638-23d51eaa0a67").bytes, # AMD Gaming Computer
        "quantity": 1,
        "featured": 1
    },
    {
        "id": UUID("7ac987ab-bb4c-4119-aea3-e7d2620da5f3").bytes,
        "giveaway_id": UUID("15718946-d2d9-47b5-bbf4-7878266349d3").bytes, # Dec 8
        "prize_id": UUID("e9eb6dab-fd47-44e1-a240-de19b6d2bede").bytes, # Breville the Tea Maker
        "quantity": 1,
        "featured": 0
    }
]


def main():
    cursor = database.connection.cursor()

    # schema
    cursor.execute(model._create_all_tables)

    cursor.executemany(model.create_prize, prizes)
    cursor.executemany(model.create_giveaway_prize, giveaway_prizes)
    cursor.executemany(model.create_giveaway, giveaways)

    print(f"changes={database.connection.totalchanges()}", file=sys.stderr)
