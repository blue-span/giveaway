SELECT
  giveaway_prize.id AS id
FROM
  giveaway_prize
  INNER JOIN current_giveaway_view ON giveaway_prize.giveaway_id = current_giveaway_view.id
WHERE
  giveaway_prize.id = :giveaway_prize_id
