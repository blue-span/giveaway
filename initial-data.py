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

giveaways = [
    {
        "id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes,
        "title": "Nov 24",
        "start_ts": int(datetime.datetime(2019, 11, 15, hour=0 , tzinfo=PT).timestamp()),
        "end_ts": int(datetime.datetime(2019, 11, 24, hour=12, tzinfo=PT).timestamp()),
    }
]
cursor.executemany(model.create_giveaway, giveaways)

# prize

prizes = [
    {
        "id": UUID("76bfea4a-aad1-4938-b638-23d51eaa0a67").bytes,
        "title": "Gaming Computer",
        "image_src": "/static/images/amd-ryzen-radeon.png",
        "image_invert": 1,
        "theme_class": "amd",
    },
    {
        "id": UUID("6c6f1ffc-89ec-402b-b454-ecc826111ec6").bytes,
        "title": "Warcraft 3: Reforged",
        "image_src": "/static/images/warcraft-reforged.png",
        "image_invert": 0,
        "theme_class": "warcraft",
    },
    {
        "id": UUID("2725611e-1c22-4841-a211-45538600f432").bytes,
        "title": "SteelSeries Peripherals",
        "image_src": "/static/images/steelseries.png",
        "image_invert": 1,
        "theme_class": "steelseries",
    }
]
cursor.executemany(model.create_prize, prizes)

# giveaway_prize

giveaway_prizes = [
    {
        "id": UUID('f7b0b621-1e16-4881-ad24-1986c3bf4a59').bytes,
        "giveaway_id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes, # Nov 24
        "prize_id": UUID("76bfea4a-aad1-4938-b638-23d51eaa0a67").bytes, # Gaming Computer
        "quantity": 1,
    },
    {
        "id": UUID('32ad6a64-2894-4e43-8cea-6d9dcec50077').bytes,
        "giveaway_id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes, # Nov 24
        "prize_id": UUID("6c6f1ffc-89ec-402b-b454-ecc826111ec6").bytes, # Warcraft 3: Reforged
        "quantity": 1,
    },
    {
        "id": UUID('479f00cd-43c6-4f9b-913f-d2dbe705486d').bytes,
        "giveaway_id": UUID("949553dd-ab29-4ef5-a325-3f10bee3c7ca").bytes, # Nov 24
        "prize_id": UUID("2725611e-1c22-4841-a211-45538600f432").bytes,
        "quantity": 1,
    },
]
cursor.executemany(model.create_giveaway_prize, giveaway_prizes)
