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
    window_size       INTEGER   NOT NULL,      -- 0 for ewma 
    confidence_level  DOUBLE    NOT NULL,      -- example: 0.99
    created_at        TIMESTAMP NOT NULL,
    PRIMARY KEY (date, model, window_size, confidence_level)
);