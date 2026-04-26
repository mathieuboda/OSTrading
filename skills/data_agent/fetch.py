from __future__ import annotations

import os
from datetime import datetime, timedelta

import pandas as pd
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from loguru import logger


def _get_data_client() -> StockHistoricalDataClient:
    api_key = os.environ["ALPACA_API_KEY"]
    secret = os.environ["ALPACA_API_SECRET"]
    return StockHistoricalDataClient(api_key, secret)


def fetch_bars(
    symbols: list[str],
    bar_size: str = "5Min",
    lookback_days: int = 30,
) -> dict[str, pd.DataFrame]:
    client = _get_data_client()

    tf_map = {
        "1Min": TimeFrame(1, TimeFrameUnit.Minute),
        "5Min": TimeFrame(5, TimeFrameUnit.Minute),
        "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
        "1Day": TimeFrame(1, TimeFrameUnit.Day),
    }
    timeframe = tf_map.get(bar_size, TimeFrame(5, TimeFrameUnit.Minute))

    end = datetime.now()
    start = end - timedelta(days=lookback_days)

    result: dict[str, pd.DataFrame] = {}
    for symbol in symbols:
        try:
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                end=end,
            )
            bars = client.get_stock_bars(request)
            if symbol in bars:
                df = bars[symbol].df
                if not df.empty:
                    result[symbol] = df
                    logger.info(f"Fetched {len(df)} bars for {symbol}")
                else:
                    logger.warning(f"No bars returned for {symbol}")
            else:
                logger.warning(f"No data for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching bars for {symbol}: {e}")

    return result


def fetch_latest_bar(symbol: str) -> pd.Series | None:
    bars = fetch_bars([symbol], bar_size="5Min", lookback_days=1)
    if symbol in bars and not bars[symbol].empty:
        return bars[symbol].iloc[-1]
    return None
