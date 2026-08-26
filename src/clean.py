from src.db import get_connection


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
            LN(adj_close / 
                LAG(adj_close) OVER w) AS log_return, 
            adj_close / 
                LAG(adj_close) OVER w - 1 AS pct_return
        FROM raw
        WHERE adj_close > 0 
        WINDOW w AS (PARTITION BY ticker ORDER BY date)
        QUALIFY log_return IS NOT NULL;
        """
        )


if __name__ == "__main__":
    clean_and_load()
    print("[DEBUG] successfully loaded clean data to db")
