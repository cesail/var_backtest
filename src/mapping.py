from src.db import get_connection


def build_traffic_light():
    with get_connection() as con:
        con.execute(
            """
            CREATE OR REPLACE TABLE traffic_light AS
            WITH scaled AS (
                SELECT model, confidence_level, exceptions, n_obs,
                    CAST(CEIL(exceptions * 250.0 / NULLIF(n_obs, 0)) AS INTEGER) AS exc_250
                FROM backtest_stats
            )
            SELECT s.model, s.confidence_level, s.exceptions, s.n_obs, s.exc_250,
                z.zone, CURRENT_TIMESTAMP AS created_at
            FROM scaled s
            JOIN basel_zones z
                ON s.exc_250 BETWEEN z.min_exc AND z.max_exc
            ORDER BY s.model, s.confidence_level;
            """
        )
        print("[DEBUG] successfully built traffic_light table in db")


if __name__ == "__main__":
    build_traffic_light()