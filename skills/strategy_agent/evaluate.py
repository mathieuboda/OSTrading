from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Signal(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    SKIP = "skip"


@dataclass
class StrategySignal:
    symbol: str
    signal: Signal
    rationale: str
    position_size_pct: float = 0.0
    indicators: dict | None = None


def evaluate_entry(
    symbol: str,
    indicators: dict,
    rsi_threshold: float = 30.0,
    volume_multiplier: float = 1.5,
) -> StrategySignal:
    rsi = indicators.get("rsi_14")
    volume = indicators.get("volume")
    avg_volume = indicators.get("avg_volume_20d")

    if rsi is None:
        return StrategySignal(
            symbol=symbol,
            signal=Signal.SKIP,
            rationale=f"RSI not available for {symbol}",
        )

    if volume is not None and avg_volume is not None and avg_volume > 0:
        volume_ratio = volume / avg_volume
    else:
        volume_ratio = 0.0

    if rsi < rsi_threshold and volume_ratio >= volume_multiplier:
        return StrategySignal(
            symbol=symbol,
            signal=Signal.BUY,
            rationale=f"RSI={rsi:.1f} < {rsi_threshold}, Vol ratio={volume_ratio:.2f}x >= {volume_multiplier}x",
            position_size_pct=0.03,
            indicators=indicators,
        )

    if rsi < rsi_threshold:
        return StrategySignal(
            symbol=symbol,
            signal=Signal.HOLD,
            rationale=f"RSI={rsi:.1f} < {rsi_threshold} but volume ratio={volume_ratio:.2f}x < {volume_multiplier}x",
            indicators=indicators,
        )

    return StrategySignal(
        symbol=symbol,
        signal=Signal.HOLD,
        rationale=f"RSI={rsi:.1f} >= {rsi_threshold}, no entry signal",
        indicators=indicators,
    )


def evaluate_exit(
    symbol: str,
    indicators: dict,
    unrealized_loss_pct: float = 0.0,
    rsi_exit_threshold: float = 65.0,
    stop_loss_pct: float = -0.05,
) -> StrategySignal:
    rsi = indicators.get("rsi_14")

    if unrealized_loss_pct <= stop_loss_pct:
        return StrategySignal(
            symbol=symbol,
            signal=Signal.SELL,
            rationale=f"Stop loss hit: unrealized loss={unrealized_loss_pct:.2%} <= {stop_loss_pct:.2%}",
            indicators=indicators,
        )

    if rsi is not None and rsi > rsi_exit_threshold:
        return StrategySignal(
            symbol=symbol,
            signal=Signal.SELL,
            rationale=f"RSI={rsi:.1f} > {rsi_exit_threshold}, take profit signal",
            indicators=indicators,
        )

    return StrategySignal(
        symbol=symbol,
        signal=Signal.HOLD,
        rationale=f"Holding: RSI={rsi}, loss={unrealized_loss_pct:.2%}",
        indicators=indicators,
    )
