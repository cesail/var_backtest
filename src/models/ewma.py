from scipy.stats import norm
import pandas as pd
import numpy as np


def ewma_var(returns, lam=0.94, confidence=0.99):
    """
    Input: returns is a pandas Series with labeled index being integers 0, 1, 2,...  0 corresponds to the oldest value

    returns.ewm(alpha=1-lam) is an exponentially weighted window object that uses all past data points

    var_series is a series of Day t variance predicted from previous variances

    Output: a pandas series using the  worst 1% (1st percentile) log return that is assumed to follow a normal distribution with the predicted variance, used as the out-of-sample VaR forecast for Day t

    Note: the output should contain mostly negative values. Values are not negated for VaR convention
    """
    var_series = returns.ewm(alpha=1-lam).var()
    sigma = np.sqrt(var_series)
    z = norm.ppf(1 - confidence)
    return z * sigma