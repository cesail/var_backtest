import duckdb
from contextlib import contextmanager
from pathlib import Path

DB_PATH = r"data/var_backtest.duckdb"
SCHEMA_PATH = "sql/schema.sql"


@contextmanager
def get_connection(read_only: bool = False):
    con = duckdb.connect(DB_PATH, read_only=read_only)
    print(f"[DEBUG] 连接到: {Path(DB_PATH).resolve()}")
    try:
        yield con
    finally:
        con.close()

# may delete this function
def init_schema():
    """
    Initialize schema
    This function should only be called at the beginning of ingest.py
    """
    with get_connection() as con:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            con.execute(f.read())