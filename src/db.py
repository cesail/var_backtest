import duckdb
from contextlib import contextmanager
from pathlib import Path

DB_PATH = r"data/var_backtest.duckdb"
SCHEMA_PATH = r"sql/schema.sql"


@contextmanager
def get_connection(read_only: bool = False):
    con = duckdb.connect(DB_PATH, read_only=read_only)
    print(f"[DEBUG] Connect to: {Path(DB_PATH).resolve()}")
    try:
        yield con
    finally:
        con.close()


def init_schema():
    """
    Initialize schema. Only invoked via `python db.py`.
    """
    with get_connection() as con:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            con.execute(f.read())


def load_forecasts_to_db(con, forecasts_df):
    """
    Load a pandas DataFrame for VaR forecasts to the var_forecasts table in db.
    Erase any existing records from the var_forecasts table before writing to it.

    Args:
        con: a DuckDB connection
        forecasts_df: a pandas dataframe with columns date, model, var, window_size, confidence_level, created_at
    """
    con.execute("DELETE FROM var_forecasts")
    con.execute("INSERT INTO var_forecasts " \
                "(date, model, var, window_size, confidence_level, created_at) " \
                "SELECT date, model, var, window_size, confidence_level, created_at " \
                "FROM forecasts_df " \
                "WHERE var IS NOT NULL")


if __name__ == "__main__":
    init_schema()
    print("[DEBUG] Schema initialized")
