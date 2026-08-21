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
    df = con.execute(
        "SELECT date, log_return FROM daily_returns ORDER BY date"
    ).df()
    return df["date"], df["log_return"]