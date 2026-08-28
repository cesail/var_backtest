WITH intermediate_table AS (
    SELECT
        model, confidence_level, breach,
        LAG(breach) OVER (PARTITION BY model ORDER BY date) AS prev_breach
    FROM var_forecasts
) -- CTE
SELECT
    model, confidence_level,
    COUNT(*)                                    AS n_obs,       -- Kupiec,including day 0
    SUM(breach)                                 AS exceptions,  -- Kupiec,including day 0
    SUM((prev_breach=0)::INT * (breach=0)::INT) AS n00,  -- Boolean values as integers, 0/1 multiplication; null if prev_breach is null 
    SUM((prev_breach=0)::INT * (breach=1)::INT) AS n01,
    SUM((prev_breach=1)::INT * (breach=0)::INT) AS n10,
    SUM((prev_breach=1)::INT * (breach=1)::INT) AS n11
FROM intermediate_table
GROUP BY model, confidence_level;