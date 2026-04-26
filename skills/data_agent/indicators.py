from __future__ import annotations

import pandas as pd
import ta


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    return ta.momentum.rsi(series, window=period)


def compute_sma(series: pd.Series, period: int) -> pd.Series:
    return ta.trend.sma_indicator(series, window=period)


def compute_avg_volume(volume: pd.Series, period: int = 20) -> pd.Series:
    return volume.rolling(window=period).mean()


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "close" not in df.columns:
        raise ValueError("DataFrame must contain 'close' column")

    df["rsi_14"] = compute_rsi(df["close"], period=14)
    df["sma_20"] = compute_sma(df["close"], period=20)
    df["sma_50"] = compute_sma(df["close"], period=50)

    if "volume" in df.columns:
        df["avg_volume_20d"] = compute_avg_volume(df["volume"], period=20)

    return df


def enrich_all(bars: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    enriched: dict[str, pd.DataFrame] = {}
    for symbol, df in bars.items():
        try:
            enriched[symbol] = enrich_dataframe(df)
        except Exception as e:
            from loguru import logger
            logger.error(f"Failed to enrich {symbol}: {e}")
    return enriched


def get_latest_indicators(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    last = df.iloc[-1]
    keys = ["close", "volume", "rsi_14", "sma_20", "sma_50", "avg_volume_20d"]
    return {k: float(last[k]) for k in keys if k in last.index and pd.notna(last[k])}
