SELECT
  registration.id
FROM
  registration
WHERE
  registration.giveaway_id = :giveaway_id
  AND (
    registration.youtube_url = :youtube_url
    OR registration.discord_username = :discord_username
  );
