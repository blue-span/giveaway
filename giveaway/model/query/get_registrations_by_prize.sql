SELECT
  registration.id AS registration_id,
  registration.youtube_channel_id AS youtube_channel_id,
  registration.discord_username AS discord_username,
  giveaway_prize.id AS giveaway_prize_id,
  prize.title AS prize_title,
  registration.verified AS verified
FROM
  registration
  INNER JOIN registration_prize ON registration_prize.registration_id = registration.id
  INNER JOIN giveaway_prize ON registration_prize.giveaway_prize_id = giveaway_prize.id
  INNER JOIN prize ON giveaway_prize.prize_id = prize.id
WHERE
  registration.giveaway_id = :giveaway_id;
