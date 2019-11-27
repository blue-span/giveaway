SELECT
  registration.id
FROM
  registration
WHERE
  registration.giveaway_id = :giveaway_id
  AND (
    registration.youtube_channel_id = :youtube_channel_id
    OR registration.discord_username = :discord_username
  );
