import datetime
from uuid import UUID

import apsw
import pytz

from giveaway import model

PT = pytz.timezone("America/Los_Angeles")
database = apsw.Connection("giveaway.sqlite3")
cursor = database.cursor()

# schema

cursor.execute(model._create_all_tables)

# giveaway

timestamp = lambda *a, **kw: int(PT.localize(datetime.datetime(*a, **kw)).timestamp())

giveaways = [
    {
        "id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes,
        "title": "Nov 24",
        "start_ts": timestamp(2019, 11, 13, hour=0, minute=0),
        "end_ts": timestamp(2019, 11, 24, hour=11, minute=59, second=59),
    },
    {
        "id": UUID('15718946-d2d9-47b5-bbf4-7878266349d3').bytes,
        "title": "Dec 8",
        "start_ts": timestamp(2019, 11, 29, hour=0, minute=0),
        "end_ts": timestamp(2019, 12, 8, hour=11, minute=59, second=59),
    }
]
cursor.executemany(model.create_giveaway, giveaways)

# prize

prizes = [
    {
        "id": UUID("76bfea4a-aad1-4938-b638-23d51eaa0a67").bytes,
        "title": "Gaming Computer",
        "image_src": "/static/images/amd-ryzen-radeon.png",
        "theme": "amd-red",
    },
    {
        "id": UUID("6c6f1ffc-89ec-402b-b454-ecc826111ec6").bytes,
        "title": "Warcraft 3: Reforged",
        "image_src": "/static/images/warcraft-reforged.png",
        "theme": "warcraft-yellow",
    },
    {
        "id": UUID("2725611e-1c22-4841-a211-45538600f432").bytes,
        "title": "SteelSeries Peripherals",
        "image_src": "/static/images/steelseries.png",
        "theme": "steelseries-black",
    },
    {
        "id": UUID('6f85f14a-0da6-48e2-abf5-a1947094ac49').bytes,
        "title": "Fake Prize",
        "image_src": "fake.png",
        "theme": "no theme",
    },
]
cursor.executemany(model.create_prize, prizes)

# giveaway_prize

giveaway_prizes = [
    {
        "id": UUID('f7b0b621-1e16-4881-ad24-1986c3bf4a59').bytes,
        "giveaway_id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes, # Nov 24
        "prize_id": UUID("76bfea4a-aad1-4938-b638-23d51eaa0a67").bytes, # Gaming Computer
        "quantity": 1,
        "featured": 1,
    },
    {
        "id": UUID('32ad6a64-2894-4e43-8cea-6d9dcec50077').bytes,
        "giveaway_id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes, # Nov 24
        "prize_id": UUID("6c6f1ffc-89ec-402b-b454-ecc826111ec6").bytes, # Warcraft 3: Reforged
        "quantity": 1,
        "featured": 0,
    },
    {
        "id": UUID('479f00cd-43c6-4f9b-913f-d2dbe705486d').bytes,
        "giveaway_id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes, # Nov 24
        "prize_id": UUID("2725611e-1c22-4841-a211-45538600f432").bytes,
        "quantity": 1,
        "featured": 0,
    },
]
cursor.executemany(model.create_giveaway_prize, giveaway_prizes)
