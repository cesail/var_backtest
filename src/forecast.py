import pandas as pd
from src.db import get_connection
from src.db import load_forecasts_to_db
from src.models.hs import hs_var
from src.models.ewma import ewma_var
from src.models.garch import garch_var


CONF = 0.99
HS_WINDOW = 250
GARCH_WINDOW = 250
EWMA_LAM = 0.94


def read_returns(con):
    """
    Read date and log returns from the daily_returns table in db
    """
    df = con.execute(
        "SELECT date, log_return FROM daily_returns ORDER BY date"
    ).df()
    return df["date"], df["log_return"]


def align(dates, var):
    """
    Abandon some oldest dates that do not have VaR forecasts due to window length

    Args:
        dates (pd.Series): trading dates 
        var (pd.Series): a series of daily VaR predictions

    Returns:
        tuple[pd.Series, pd.Series]
    """
    offset = len(dates) - len(var)
    dates_with_forecast = dates.iloc[offset:].reset_index(drop=True)
    return dates_with_forecast, var.reset_index(drop=True)


def build(con):
    """
    Read dates and log_returns from the daily_returns table. Run each model in the runs list to get series of daily VaR predictions. Integrate actual log_returns and VaR predictions into a data frame.

    Args:
        con (duckdb.DuckDBPyConnection): the connection produced by get_connection.

    Returns:
        pd.DataFrame: a data frame with columns date, model (e.g., garch), var (the daily var predicted by the model using past returns), window_size (0 for ewma), confidence_level (e.g., 0.99), and a time stamp.
    """
    dates, r = read_returns(con)
    runs = [
        ("hs",    hs_var(r, CONF, HS_WINDOW),       HS_WINDOW),
        ("ewma",  ewma_var(r, CONF, EWMA_LAM),      0),
        ("garch", garch_var(r, CONF, GARCH_WINDOW), GARCH_WINDOW),
    ]

    frames = []
    for model, var, window in runs:
        d, v = align(dates, var)
        frames.append(pd.DataFrame({
            "date": d,
            "model": model,
            "var": v,
            "window_size": window,
            "confidence_level": CONF,
        }))

    result_frame = pd.concat(frames, ignore_index=True) # indexed by integers
    result_frame["created_at"] = pd.Timestamp.now()

    return result_frame


if __name__ == "__main__":
    with get_connection() as con:
        var_forecasts = build(con)
        load_forecasts_to_db(con, var_forecasts)