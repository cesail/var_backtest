CREATE OR REPLACE TABLE breaches AS
SELECT
    v.model,
    v.confidence_level,
    v.date,
    r.log_return,
    v.var,
    CAST(r.log_return < v.var AS INTEGER) AS breach -- value = 1 if true
FROM var_forecasts v
JOIN daily_returns r USING (date)
ORDER BY v.model, v.date;


WITH intermediate_table AS (
    SELECT
        model, confidence_level, breach,
        LAG(breach) OVER (PARTITION BY model ORDER BY date) AS prev_breach
    FROM breaches
) -- CTE
SELECT
    model, confidence_level,
    COUNT(*)                                    AS n_obs,       -- Kupiec,含首日
    SUM(breach)                                 AS exceptions,  -- Kupiec,含首日
    SUM((prev_breach=0)::INT * (breach=0)::INT) AS n00,  -- Boolean values as integers, 0/1 multiplication; null if prev_breach is null 
    SUM((prev_breach=0)::INT * (breach=1)::INT) AS n01,
    SUM((prev_breach=1)::INT * (breach=0)::INT) AS n10,
    SUM((prev_breach=1)::INT * (breach=1)::INT) AS n11
FROM intermediate_table
GROUP BY model, confidence_level;