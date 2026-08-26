from scipy.stats import chi2
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.special import xlogy
from src.db import get_connection, load_backtest_stats_to_db

SQL_PATH = Path(__file__).parent.parent / "sql" / "backtest.sql"


def kupiec_pof(n, x, alpha):
    """
     Calculate the Kupiec Proportion of Failures (POF) test statistic and p-value.

    Args:
        n (int): total number of records in the daily_returns table for a given (model, confidence_level) pair.
        x (int): number of VaR exceptions(breaches) for this (model, confidence_level) pair.
        alpha (float): level of significance, equal to 1 - confidence_level.

    Returns:
        tuple[float, float]: A tuple containing:
            - kupiec_stat: Kupiec POF likelihood ratio test statistic.
            - p_value
    """
    p_hat = x / n
    kupiec_stat = -2 * (np.log((1-alpha)**(n-x) * alpha**x) - np.log((1-p_hat)**(n-x) * p_hat**x))
    return kupiec_stat, chi2.sf(kupiec_stat, 1)


def christoffersen_ind(n00, n01, n10, n11):
    """
    Calculate the Christoffersen Independence test statistic and p-value.

    Args:

    Returns:
        tuple[float, float]: A tuple containing:
            - chris_stat: Christoffersen Independence test statistic.
            - p_value
    """
    p_hat01 = n01 / (n00+n01) if (n00+n01) > 0 else 0 
    # avoid potential dividing by 0
    p_hat11 = n11 / (n10+n11) if (n10+n11) > 0 else 0
    p_hat   = (n01+n11) / (n00+n01+n10+n11)
    nume  = (
        xlogy(n00+n10, 1-p_hat) +
        xlogy(n01+n11, p_hat)
    )
    deno  = (
        xlogy(n00, 1-p_hat01) +
        xlogy(n01, p_hat01) +
        xlogy(n10, 1-p_hat11) +
        xlogy(n11, p_hat11)
    )
    chris_stat = -2 * (nume - deno)
    # nume  = (1-p_hat)**(n00+n10)  * p_hat**(n01+n11)
    # deno  = (1-p_hat01)**n00 * p_hat01**n01 * (1-p_hat11)**n10 * p_hat11**n11
    # chris_stat = -2 * (np.log(nume) - np.log(deno)), but this may cause log(0)
    return chris_stat, chi2.sf(chris_stat, 1)


def christoffersen_cc(kupiec_stat, chris_stat):
    cc_stat = kupiec_stat + chris_stat
    return cc_stat, chi2.sf(cc_stat, 2)


def run_backtest(con):
    """
    Execute backtest.sql: build the breaches table, then read per-model counts.

    Args:
        con: a DuckDB connection

    Returns:
        pd.DataFrame: one row per model with columns model, confidence_level, n_obs, exceptions, n00, n01, n10, n11.
    """
    breach_count_frame = con.execute(SQL_PATH.read_text(encoding="utf-8")).df()
    print(f"[DEBUG] successfully executed backtest.sql: Read {len(breach_count_frame)} model rows.")
    return breach_count_frame


def compute_stats(breach_count_frame):
    """
    For each model row, run Kupiec POF, Christoffersen independence, and conditional coverage. Assemble the backtest_stats frame.

    Args:
        breach_count_frame (pd.DataFrame): output of run_backtest.

    Returns:
        pd.DataFrame: columns model, confidence_level, n_obs, exceptions, exception_rate, kupiec_stat, p_kupiec, chris_stat, p_chris, cc_stat, p_cc, created_at.
    """
    rows = []
    for _, row in breach_count_frame.iterrows():
        alpha = 1 - row["confidence_level"]
        n, x = int(row["n_obs"]), int(row["exceptions"])
        kupiec_stat, p_kupiec = kupiec_pof(n, x, alpha)
        chris_stat,  p_chris  = christoffersen_ind(row["n00"], row["n01"], row["n10"], row["n11"])
        cc_stat,     p_cc     = christoffersen_cc(kupiec_stat, chris_stat)
        rows.append({
            "model": row["model"],
            "confidence_level": row["confidence_level"],
            "n_obs": n,
            "exceptions": x,
            "exception_rate": x / n,
            "kupiec_stat": kupiec_stat, "p_kupiec": p_kupiec,
            "chris_stat": chris_stat,   "p_chris": p_chris,
            "cc_stat": cc_stat,         "p_cc": p_cc,
        })
    df = pd.DataFrame(rows)
    df["created_at"] = pd.Timestamp.now()
    print(f"[DEBUG] Computed backtest statistics for {len(df)} models.")
    return df


if __name__ == "__main__":
    with get_connection() as con:
        breach_count_frame = run_backtest(con)
        stats = compute_stats(breach_count_frame)
        load_backtest_stats_to_db(con, stats)
        print(stats)


