from __future__ import annotations

from skills.strategy_agent.evaluate import Signal, evaluate_entry, evaluate_exit


def test_evaluate_entry_buy_signal():
    indicators = {"rsi_14": 25.0, "volume": 2000000, "avg_volume_20d": 1000000}
    result = evaluate_entry("AAPL", indicators)
    assert result.signal == Signal.BUY
    assert "RSI" in result.rationale


def test_evaluate_entry_hold_no_volume():
    indicators = {"rsi_14": 25.0, "volume": 1000000, "avg_volume_20d": 1000000}
    result = evaluate_entry("AAPL", indicators)
    assert result.signal == Signal.HOLD


def test_evaluate_entry_hold_rsi_not_oversold():
    indicators = {"rsi_14": 45.0, "volume": 2000000, "avg_volume_20d": 1000000}
    result = evaluate_entry("AAPL", indicators)
    assert result.signal == Signal.HOLD


def test_evaluate_entry_skip_no_rsi():
    indicators = {"volume": 2000000, "avg_volume_20d": 1000000}
    result = evaluate_entry("AAPL", indicators)
    assert result.signal == Signal.SKIP


def test_evaluate_entry_no_volume_data():
    indicators = {"rsi_14": 25.0}
    result = evaluate_entry("AAPL", indicators)
    assert result.signal == Signal.HOLD


def test_evaluate_exit_take_profit():
    indicators = {"rsi_14": 70.0}
    result = evaluate_exit("AAPL", indicators, unrealized_loss_pct=0.01)
    assert result.signal == Signal.SELL
    assert "take profit" in result.rationale.lower() or "RSI" in result.rationale


def test_evaluate_exit_stop_loss():
    indicators = {"rsi_14": 40.0}
    result = evaluate_exit("AAPL", indicators, unrealized_loss_pct=-0.06)
    assert result.signal == Signal.SELL
    assert "stop loss" in result.rationale.lower()


def test_evaluate_exit_hold():
    indicators = {"rsi_14": 50.0}
    result = evaluate_exit("AAPL", indicators, unrealized_loss_pct=-0.01)
    assert result.signal == Signal.HOLD


def test_evaluate_exit_no_rsi():
    indicators = {}
    result = evaluate_exit("AAPL", indicators, unrealized_loss_pct=-0.01)
    assert result.signal == Signal.HOLD
