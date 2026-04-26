from __future__ import annotations

import pandas as pd
import pytest

from skills.data_agent.indicators import (
    compute_avg_volume,
    compute_rsi,
    compute_sma,
    enrich_dataframe,
    get_latest_indicators,
)


def _make_ohlcv_df(rows: int = 100) -> pd.DataFrame:
    import numpy as np

    np.random.seed(42)
    dates = pd.date_range("2026-01-01", periods=rows, freq="5min")
    close = 100 + np.cumsum(np.random.randn(rows) * 0.5)
    volume = 1_000_000 + np.random.randint(0, 500_000, rows)

    return pd.DataFrame(
        {
            "timestamp": dates,
            "open": close - 0.1,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": volume,
        }
    )


def test_compute_rsi():
    df = _make_ohlcv_df()
    rsi = compute_rsi(df["close"], period=14)
    assert len(rsi) == len(df)
    assert rsi.iloc[-1] >= 0
    assert rsi.iloc[-1] <= 100


def test_compute_sma():
    df = _make_ohlcv_df()
    sma = compute_sma(df["close"], period=20)
    assert len(sma) == len(df)
    assert sma.iloc[-1] > 0


def test_compute_avg_volume():
    df = _make_ohlcv_df()
    avg_vol = compute_avg_volume(df["volume"], period=20)
    assert len(avg_vol) == len(df)


def test_enrich_dataframe():
    df = _make_ohlcv_df()
    enriched = enrich_dataframe(df)
    assert "rsi_14" in enriched.columns
    assert "sma_20" in enriched.columns
    assert "sma_50" in enriched.columns
    assert "avg_volume_20d" in enriched.columns


def test_enrich_dataframe_missing_close():
    df = pd.DataFrame({"open": [1, 2], "volume": [100, 200]})
    with pytest.raises(ValueError, match="close"):
        enrich_dataframe(df)


def test_get_latest_indicators():
    df = _make_ohlcv_df()
    enriched = enrich_dataframe(df)
    indicators = get_latest_indicators(enriched)
    assert "close" in indicators
    assert "rsi_14" in indicators
    assert indicators["close"] > 0


def test_get_latest_indicators_empty():
    df = pd.DataFrame()
    indicators = get_latest_indicators(df)
    assert indicators == {}
