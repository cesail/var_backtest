import yfinance as yf
import pandas as pd
from src.db import get_connection

TICKERS = ["^GSPC"]          
START, END = "2015-01-01", "2026-01-01"

def download_prices(tickers=TICKERS, start=START, end=END) -> pd.DataFrame:

    frames = [] # one frame for each ticker

    for t in tickers:
        raw = yf.download(t, start=start, end=end, auto_adjust=False)

        # integer indices, rather than dates
        raw = raw.reset_index() 

        # make column names in lower case, and replace space by _
        # if raw is of type pandas multiindex, only get attributes like 'open'
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        raw.columns = [c.lower().replace(" ", "_") for c in raw.columns]

        # add one new column to this frame called 'ticker' with value the current ticker in the for loop
        raw["ticker"] = t  

        frames.append(raw)

    df = pd.concat(frames, ignore_index=True) 
    print("[DEBUG] successfully downloaded raw data")
    return df[["date", "ticker", "open", "high", "low", "close", "adj_close", "volume"]]


def load_raw_to_db(df=None, tickers=TICKERS, start=START, end=END):
    # df arg is for testing
    if df is None:
        df = download_prices(tickers=tickers, start=start, end=end)
    with get_connection() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO raw
                (date, ticker, open, high, low, close, adj_close, volume)
            SELECT
                date, ticker, open, high, low, close, adj_close, volume
            FROM df
            """
        )
    print(f"Write {len(df)} rows to raw table in db")
    

if __name__ == "__main__":
    load_raw_to_db()