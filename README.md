# Market Risk VaR Model Validation and Basel Backtesting 
This is a Champion/challenger VaR backtesting project with an in-process DuckDB backed data pipeline.

**Champing**: Historical simulation (HS), vs
**Challengers**: GARCH, EWMA

## Data
- Source: yfinance ^GSPC
- Range: 2015-01-01 - 2026-01-01, which covers multiple stress periods including the 2020 COVID crash
  
## Database
- File: data/var_backtest.duckdb
- Schema: defined in sql/schema.sql

### Conventions
VaR is stored with raw sign, which is usually negative. Then, `breach = true` when `log_return < var`.

## Reproduce
```
mkdir -p data
python -m src.db
python -m src.ingest
python -m src.clean
python -m src.forecast
python -m src.backtest
python -m src.mapping
```

## Requirements
```
pip install -e .
```