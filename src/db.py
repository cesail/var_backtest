import duckdb
from contextlib import contextmanager

DB_PATH = "data/var_backtest.duckdb"
SCHEMA_PATH = "sql/schema.sql"


@contextmanager
def get_connection(read_only: bool = False):
    con = duckdb.connect(DB_PATH, read_only=read_only)
    try:
        yield con
    finally:
        con.close()


def init_schema():
    """
    Initialize schema
    This function should only be called at the beginning of ingest.py
    """
    with get_connection() as con:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            con.execute(f.read())