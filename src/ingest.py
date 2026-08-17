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
        raw.columns = [c.lower().replace(" ", "_") for c in raw.columns]

        # add one new column to this frame called 'ticker' with value the current ticker in the for loop
        raw["ticker"] = t  

        frames.append(raw)

    df = pd.concat(frames, ignore_index=True) 

    return df[["date", "ticker", "open", "high", "low", "close", "adj_close", "volume"]]


def load_raw_to_db():
    df = download_prices()
    with get_connection() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO raw_prices
                (date, ticker, open, high, low, close, adj_close, volume)
            SELECT
                date, ticker, open, high, low, close, adj_close, volume
            FROM df
            """
        )
    print(f"Write {len(df)} rows to raw_prices")
    

if __name__ == "__main__":
    load_raw_to_db()