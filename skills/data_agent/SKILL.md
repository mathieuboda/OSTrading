# Data Agent Skill

Fetches market data and computes technical indicators for the trading system.

## Triggers
- Cron: every 5 minutes during market hours
- Manual: `/data-fetch [symbol]`

## Inputs
- Watchlist of symbols (from `config/watchlist.json`)
- Bar size (default: 5Min)
- Indicator list: rsi_14, sma_20, sma_50, avg_volume_20d

## Outputs
- JSON with OHLCV + computed indicators per symbol
- DataFrame passed to Strategy Agent

## Dependencies
- alpaca-py (Alpaca Data API v2)
- ta (technical analysis library)
- pandas, numpy

## Environment Variables
- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`
- `ALPACA_DATA_URL`
- `ALPACA_PAPER_TRADING`
