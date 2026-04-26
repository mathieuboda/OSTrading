from __future__ import annotations

from skills.risk_agent.checks import (
    RiskVerdict,
    check_daily_loss_limit,
    check_drawdown_halt,
    check_max_position_size,
    check_portfolio_concentration,
    is_trade_approved,
    run_all_risk_checks,
)


def test_max_position_size_pass():
    result = check_max_position_size("AAPL", qty=1, price=150, equity=100000, max_pct=0.03)
    assert result.verdict == RiskVerdict.PASS


def test_max_position_size_fail():
    result = check_max_position_size("AAPL", qty=100, price=150, equity=100000, max_pct=0.03)
    assert result.verdict == RiskVerdict.FAIL
    assert result.adjusted_qty is not None


def test_daily_loss_limit_pass():
    result = check_daily_loss_limit(daily_pnl=-100, equity=100000, max_daily_loss_pct=0.02)
    assert result.verdict == RiskVerdict.PASS


def test_daily_loss_limit_fail():
    result = check_daily_loss_limit(daily_pnl=-2500, equity=100000, max_daily_loss_pct=0.02)
    assert result.verdict == RiskVerdict.FAIL


def test_drawdown_halt_pass():
    result = check_drawdown_halt(equity=98000, peak_equity=100000, halt_threshold_pct=0.05)
    assert result.verdict == RiskVerdict.PASS


def test_drawdown_halt_fail():
    result = check_drawdown_halt(equity=94000, peak_equity=100000, halt_threshold_pct=0.05)
    assert result.verdict == RiskVerdict.FAIL


def test_portfolio_concentration_pass():
    positions = [{"sector": "Technology", "market_value": 5000}]
    result = check_portfolio_concentration(
        "Technology", order_value=2000, positions=positions, equity=100000, max_concentration_pct=0.15,
    )
    assert result.verdict == RiskVerdict.PASS


def test_portfolio_concentration_fail():
    positions = [{"sector": "Technology", "market_value": 12000}]
    result = check_portfolio_concentration(
        "Technology", order_value=5000, positions=positions, equity=100000, max_concentration_pct=0.15,
    )
    assert result.verdict == RiskVerdict.FAIL


def test_is_trade_approved_all_pass():
    results = [
        check_max_position_size("AAPL", 1, 150, 100000),
        check_daily_loss_limit(-100, 100000),
    ]
    assert is_trade_approved(results) is True


def test_is_trade_approved_one_fail():
    results = [
        check_max_position_size("AAPL", 100, 150, 100000),
        check_daily_loss_limit(-100, 100000),
    ]
    assert is_trade_approved(results) is False


def test_run_all_risk_checks():
    config = {
        "risk": {
            "position_sizing": {"max_position_pct": 0.03, "max_portfolio_concentration_pct": 0.15},
            "daily_limits": {"max_daily_loss_pct": 0.02},
            "drawdown": {"halt_on_drawdown": True, "halt_threshold_pct": 0.05},
            "market_rules": {"market_hours_only": False},
        }
    }
    results = run_all_risk_checks(
        symbol="AAPL",
        side="buy",
        qty=1,
        price=150,
        equity=100000,
        daily_pnl=-100,
        positions=[],
        peak_equity=100000,
        config=config,
    )
    assert len(results) >= 2
    assert is_trade_approved(results) is True
