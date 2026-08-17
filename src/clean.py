def clean_and_load():
"""
Use SQL to clean raw data with window functions
Load to daily_returns table
"""


    with get_connection() as con:
        con.execute(
        """
        INSERT OR REPLACE INTO daily_returns
        SELECT
            date,
            ticker,
            adj_close,
            LN(adj_close / LAG(adj_close) OVER (PARTITION BY ticker ORDER BY date)) AS log_return,
            adj_close / LAG(adj_close) OVER (PARTITION BY ticker ORDER BY date) - 1 AS pct_return
        FROM raw_prices
        WHERE adj_close IS NOT NULL
        QUALIFY log_return IS NOT NULL
        """
        )
