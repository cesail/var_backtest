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