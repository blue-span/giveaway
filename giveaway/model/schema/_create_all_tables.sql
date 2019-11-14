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
  image_invert INTEGER NOT NULL,
  theme_class TEXT NOT NULL
) WITHOUT ROWID;

--DROP TABLE IF EXISTS giveaway_prize;
CREATE TABLE IF NOT EXISTS giveaway_prize(
  id BLOB PRIMARY KEY,
  giveaway_id BLOB NOT NULL,
  prize_id BLOB NOT NULL,
  quantity INTEGER NOT NULL,
  FOREIGN KEY(giveaway_id) REFERENCES giveaway(id),
  FOREIGN KEY(prize_id) REFERENCES prize(id)
) WITHOUT ROWID;

--DROP TABLE IF EXISTS registration;
CREATE TABLE IF NOT EXISTS registration(
  id BLOB PRIMARY KEY,
  giveaway_id BLOB NOT NULL,
  youtube_url TEXT NOT NULL,
  discord_username TEXT NOT NULL,
  FOREIGN KEY(giveaway_id) REFERENCES giveaway(id)
) WITHOUT ROWID;

--DROP TABLE IF EXISTS ;
CREATE TABLE IF NOT EXISTS registration_prize(
  id BLOB PRIMARY KEY,
  registration_id BLOB NOT NULL,
  giveaway_prize_id BLOB NOT NULL,
  FOREIGN KEY(registration_id) REFERENCES registration(id),
  FOREIGN KEY(giveaway_prize_id) REFERENCES giveaway_prize(id)
) WITHOUT ROWID;
