--DROP TABLE IF EXISTS giveaway;
CREATE TABLE IF NOT EXISTS giveaway(
  id BLOB PRIMARY KEY,
  title TEXT NOT NULL,
  start_ts INTEGER NOT NULL UNIQUE,
  end_ts INTEGER NOT NULL UNIQUE
) WITHOUT ROWID;

--DROP TABLE IF EXISTS prize;
CREATE TABLE IF NOT EXISTS prize(
  id BLOB PRIMARY KEY,
  title TEXT NOT NULL UNIQUE,
  image_src TEXT NOT NULL,
  theme TEXT NOT NULL
) WITHOUT ROWID;

--DROP TABLE IF EXISTS giveaway_prize;
CREATE TABLE IF NOT EXISTS giveaway_prize(
  id BLOB PRIMARY KEY,
  giveaway_id BLOB NOT NULL,
  prize_id BLOB NOT NULL,
  quantity INTEGER NOT NULL,
  featured INTEGER NOT NULL,
  FOREIGN KEY(giveaway_id) REFERENCES giveaway(id),
  FOREIGN KEY(prize_id) REFERENCES prize(id)
) WITHOUT ROWID;

--DROP TABLE IF EXISTS registration;
CREATE TABLE IF NOT EXISTS registration(
  id BLOB PRIMARY KEY,
  giveaway_id BLOB NOT NULL,
  youtube_channel_id TEXT NOT NULL,
  discord_username TEXT NOT NULL,
  verified INTEGER NOT NULL,
  FOREIGN KEY(giveaway_id) REFERENCES giveaway(id)
  FOREIGN KEY(youtube_channel_id) REFERENCES youtube_channel(id)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS youtube_channel(
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL
) WITHOUT ROWID;

--DROP TABLE IF EXISTS ;
CREATE TABLE IF NOT EXISTS registration_prize(
  id BLOB PRIMARY KEY,
  registration_id BLOB NOT NULL,
  giveaway_prize_id BLOB NOT NULL,
  FOREIGN KEY(registration_id) REFERENCES registration(id),
  FOREIGN KEY(giveaway_prize_id) REFERENCES giveaway_prize(id)
) WITHOUT ROWID;

CREATE VIEW IF NOT EXISTS prize_view
AS
SELECT
  prize.title AS title,
  prize.image_src AS image_src,
  prize.theme AS theme,
  giveaway_prize.id AS id,
  giveaway_prize.giveaway_id AS giveaway_id,
  giveaway_prize.quantity AS quantity,
  giveaway_prize.featured AS featured
FROM
  giveaway_prize
  INNER JOIN prize ON giveaway_prize.prize_id = prize.id;


CREATE VIEW IF NOT EXISTS current_giveaway_view
AS
SELECT
  id,
  title
FROM
  giveaway
WHERE
  datetime(giveaway.start_ts, 'unixepoch') <= datetime('now')
  AND datetime(giveaway.end_ts, 'unixepoch') >= datetime('now');
