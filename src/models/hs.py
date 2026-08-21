import pandas as pd
import numpy as np

def hs_var(returns, window=250, confidence=0.99):
    """
    Input: 
        returns is a pandas Series with labeled index being integers 0, 1, 2,... 0 corresponds to the oldest date.

    Returns:
        a pandas series using the worst 1% (1st percentile) return during Day t-1 to Day t-250 used as the out-of-sample VaR forecast for Day t
    """
    return returns.shift(1).rolling(window).apply(
        lambda x: np.percentile(x, (1 - confidence) * 100)
    )