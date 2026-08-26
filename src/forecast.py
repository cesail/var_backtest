import pandas as pd
from src.db import get_connection
from src.db import load_forecasts_to_db
from src.models.hs import hs_var
from src.models.ewma import ewma_var
from src.models.garch import garch_var


CONF = 0.99
# at any time, the var_forecasts table in db will not have 2 different window_size for a model
HS_WINDOW = 250 
GARCH_WINDOW = 250 
EWMA_LAM = 0.94


def read_returns(con):
    """
    Read date and log returns from the daily_returns table in db

    Args:
        con (duckdb.DuckDBPyConnection): the connection produced by get_connection.

    Returns:
        tuple: (pd.Series, pd.Series)
    """
    df = con.execute(
        "SELECT date, log_return FROM daily_returns ORDER BY date"
    ).df()
    print("[DEBUG: forecast.read_returns]Read return data from db.")
    return df["date"], df["log_return"]


def build(con):
    """
    Read dates and log_returns from the daily_returns table. Run each model to get daily VaR predictions. Assemble actual log_returns, VaR predictions, and breach flags (1 if breach, 0 if not) into a data frame.

    Args:
        con (duckdb.DuckDBPyConnection): the connection produced by get_connection.

    Returns:
        pd.DataFrame: columns date, model, var, log_return, breach, window_size, confidence_level, created_at.
    """
    dates, r = read_returns(con)
    runs = [
        ("hs",    hs_var(r, HS_WINDOW, CONF),       HS_WINDOW),
        ("ewma",  ewma_var(r, EWMA_LAM, CONF),      0),
        ("garch", garch_var(r, GARCH_WINDOW, CONF), GARCH_WINDOW),
    ]

    print(f"[DEBUG]Ran {len(runs)} models to predict VaR.")

    frames = []
    for model, var, window in runs:
        frames.append(pd.DataFrame({
            "date": dates,
            "model": model,
            "var": var,
            "log_return": r,
            "breach": (r < var).astype("Int64"),   # 1 if log_return < var; NA where var is NaN
            "window_size": window,
            "confidence_level": CONF,
        }))

    result_frame = pd.concat(frames, ignore_index=True)
    result_frame["created_at"] = pd.Timestamp.now()

    print(f"Created the pandas VaR result frame.")

    return result_frame


if __name__ == "__main__":
    with get_connection() as con:
        var_forecasts = build(con)
        load_forecasts_to_db(con, var_forecasts)

