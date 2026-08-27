CREATE TABLE IF NOT EXISTS raw (
    date        DATE,
    ticker      VARCHAR,
    open        DOUBLE,
    high        DOUBLE,
    low         DOUBLE,
    close       DOUBLE,
    adj_close   DOUBLE,
    volume      BIGINT,
    PRIMARY KEY (date, ticker)
);

CREATE TABLE IF NOT EXISTS daily_returns (
    date        DATE,
    ticker      VARCHAR,
    adj_close   DOUBLE,
    log_return  DOUBLE,
    pct_return  DOUBLE,
    PRIMARY KEY (date, ticker)
);

CREATE TABLE IF NOT EXISTS var_forecasts (
    date              DATE      NOT NULL,
    model             VARCHAR   NOT NULL,      -- 'hs' / 'garch' / 'ewma'
    var               DOUBLE    NOT NULL,      -- raw sign, usually negative
    log_return        DOUBLE    NOT NULL,      -- actual return on this date
    breach            INTEGER   NOT NULL,      -- 1 if log_return < var
    window_size       INTEGER   NOT NULL,      -- 0 for ewma
    confidence_level  DOUBLE    NOT NULL,      -- example: 0.99
    created_at        TIMESTAMP NOT NULL,
    PRIMARY KEY (date, model, window_size, confidence_level)
);

CREATE TABLE IF NOT EXISTS backtest_stats (
    model            VARCHAR,
    confidence_level DOUBLE,
    n_obs            INTEGER,  -- T-window_size for hs and garch; T-1 for ewma
    exceptions       INTEGER,
    exception_rate   DOUBLE,
    kupiec_stat  DOUBLE, p_kupiec  DOUBLE,   -- Kupiec POF
    chris_stat DOUBLE, p_chris DOUBLE,   -- Christoffersen independence
    cc_stat  DOUBLE, p_cc  DOUBLE,   -- Conditional cover
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS basel_zones (
    zone       VARCHAR,   -- green / yellow / red
    min_exc    INTEGER,   -- inclusive, per-250-day equivalent
    max_exc    INTEGER    -- inclusive
);
DELETE FROM basel_zones;
INSERT INTO basel_zones VALUES
    ('green', 0, 4),
    ('yellow', 5, 9),
    ('red', 10, 999);