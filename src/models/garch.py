from arch import arch_model
import numpy as np

def garch_var_one_step(returns_window, confidence=0.99, dist='t'):
    """
    Input: 
    returns_window: pandas Series or numpy array, a window of returns. Multiplying by 100 rescales to percentage-point units as recommended by arch's documentation

    p=1: number of lagged squared residual terms (ARCH order), q=1: number of lagged conditional-variance terms (GARCH order), so p=1,q=1 is GARCH(1,1)

    arch_model gives an unfit ARCHModel object

    am.fit returns a fitted results object, res (type ARCHModelResult). The fitting process is to find the best (omega, alpha, beta) such that under the resulting t-distribution for return with predicted variance, the log-likelyhood of the actual return data is maximized.

    .forecast(horizon=1): Method on the fitted results object. Produces a forecast object (type ARCHModelForecast) containing the model's variance forecast. horizon=1: forecast 1 step ahead.

    forecast.variance is a pandas DataFrame. forecast.variance.values is a numpy array, where [-1, 0] takes its last row, first column value.

    Output: a single value, usually negative
    """
    
    am = arch_model(returns_window * 100, vol='Garch', p=1, q=1, dist=dist)
    res = am.fit(disp='off')
    # fitting parameters: mu, onega, alpha, beta, nu
    # mu: the constant mean of the return equation, r_t = mu + epsilon_t, where epsilon_t = sigma_t * z_t is the GARCH-modeled residual
    # nu: the degree of freedom that the t-distribution should use

    forecast = res.forecast(horizon=1)
    sigma_next = np.sqrt(forecast.variance.values[-1, 0]) / 100
    q = res.model.distribution.ppf(1 - confidence, [res.params['nu']])
    return q * sigma_next


def garch_var(returns, window=250, confidence=0.99, dist='t'):
    return returns.shift(1).rolling(window).apply(
        garch_var_one_step, kwargs={'confidence': confidence, 'dist': dist}
    )