from scipy.stats import chi2
import numpy as np

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
    p_hat01 = n01 / (n00+n01); p_hat11 = n11 / (n10+n11)
    p_hat   = (n01+n11) / (n00+n01+n10+n11)
    nume  = (1-p_hat)**(n00+n10)  * p_hat**(n01+n11)
    deno  = (1-p_hat01)**n00 * p_hat01**n01 * (1-p_hat11)**n10 * p_hat11**n11
    chris_stat = -2 * (np.log(nume) - np.log(deno))
    return chris_stat, chi2.sf(chris_stat, 1)

def christoffersen_cc(kupiec_stat, chris_stat):
    cc_stat = kupiec_stat + chris_stat
    return cc_stat, chi2.sf(cc_stat, 2)


"""
TO DO
1. def run_backtest(con): Execute backtest.sql.
2. def compute_stats(counts): For each model, run the three tests and assemble the backtest_stats frame.
3. if __name__ == "__main__":
    with get_connection() as con:
        counts = run_backtest(con)
        stats = compute_stats(counts)
        load_backtest_stats_to_db(con, stats)
        print(stats)
4. address potential log(0) issue in the christoffersen_ind function
5. write the following function to db.pydef load_backtest_stats_to_db(con, stats_df):
  
    Load a pandas DataFrame of backtest test statistics to the backtest_stats table in db.
    Erase any existing records from the backtest_stats table before writing to it.

    Args:
        con: a DuckDB connection
        stats_df: a pandas dataframe with columns model, confidence_level, n_obs,
            exceptions, exception_rate, lr_uc, p_uc, lr_ind, p_ind, lr_cc, p_cc, created_at
"""