SELECT
  a.youtube_url,
  b.youtube_url
FROM
  registration a
  INNER JOIN (
    SELECT youtube_url FROM registration
  ) b ON substr(a.youtube_url, 33) = b.youtube_url;
