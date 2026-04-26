from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from zoneinfo import ZoneInfo

import yaml
from loguru import logger


class RiskVerdict(Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass
class RiskCheckResult:
    verdict: RiskVerdict
    check_name: str
    reason: str
    adjusted_qty: float | None = None


def load_risk_config(path: str = "config/risk.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def check_max_position_size(
    symbol: str,
    qty: float,
    price: float,
    equity: float,
    max_pct: float = 0.03,
) -> RiskCheckResult:
    order_value = qty * price
    position_pct = order_value / equity if equity > 0 else 1.0

    if position_pct > max_pct:
        adjusted_qty = int((equity * max_pct) / price)
        return RiskCheckResult(
            verdict=RiskVerdict.FAIL,
            check_name="max_position_size",
            reason=f"Position {position_pct:.2%} > max {max_pct:.2%}. Adjusted qty: {adjusted_qty}",
            adjusted_qty=adjusted_qty,
        )

    return RiskCheckResult(
        verdict=RiskVerdict.PASS,
        check_name="max_position_size",
        reason=f"Position {position_pct:.2%} <= {max_pct:.2%}",
    )


def check_daily_loss_limit(
    daily_pnl: float,
    equity: float,
    max_daily_loss_pct: float = 0.02,
) -> RiskCheckResult:
    if equity <= 0:
        return RiskCheckResult(
            verdict=RiskVerdict.FAIL,
            check_name="daily_loss_limit",
            reason="Invalid equity",
        )

    daily_loss_pct = abs(daily_pnl) / equity if daily_pnl < 0 else 0.0

    if daily_loss_pct >= max_daily_loss_pct:
        return RiskCheckResult(
            verdict=RiskVerdict.FAIL,
            check_name="daily_loss_limit",
            reason=f"Daily loss {daily_loss_pct:.2%} >= limit {max_daily_loss_pct:.2%}",
        )

    return RiskCheckResult(
        verdict=RiskVerdict.PASS,
        check_name="daily_loss_limit",
        reason=f"Daily loss {daily_loss_pct:.2%} < {max_daily_loss_pct:.2%}",
    )


def check_market_hours() -> RiskCheckResult:
    et = ZoneInfo("America/New_York")
    now_et = datetime.now(et)
    current_time = now_et.time()

    market_open = time(9, 30)
    market_close = time(16, 0)

    if now_et.weekday() >= 5:
        return RiskCheckResult(
            verdict=RiskVerdict.FAIL,
            check_name="market_hours_only",
            reason=f"Weekend: {now_et.strftime('%A')}",
        )

    if current_time < market_open or current_time >= market_close:
        return RiskCheckResult(
            verdict=RiskVerdict.FAIL,
            check_name="market_hours_only",
            reason=f"Outside market hours: {current_time.strftime('%H:%M')} ET",
        )

    return RiskCheckResult(
        verdict=RiskVerdict.PASS,
        check_name="market_hours_only",
        reason=f"Within market hours: {current_time.strftime('%H:%M')} ET",
    )


def check_portfolio_concentration(
    symbol_sector: str,
    order_value: float,
    positions: list[dict],
    equity: float,
    max_concentration_pct: float = 0.15,
) -> RiskCheckResult:
    sector_value = sum(
        p.get("market_value", 0)
        for p in positions
        if p.get("sector") == symbol_sector
    )
    total_sector_pct = (sector_value + order_value) / equity if equity > 0 else 1.0

    if total_sector_pct > max_concentration_pct:
        return RiskCheckResult(
            verdict=RiskVerdict.FAIL,
            check_name="portfolio_concentration",
            reason=f"Sector {symbol_sector} concentration {total_sector_pct:.2%} > {max_concentration_pct:.2%}",
        )

    return RiskCheckResult(
        verdict=RiskVerdict.PASS,
        check_name="portfolio_concentration",
        reason=f"Sector {symbol_sector} concentration {total_sector_pct:.2%} <= {max_concentration_pct:.2%}",
    )


def check_drawdown_halt(
    equity: float,
    peak_equity: float,
    halt_threshold_pct: float = 0.05,
) -> RiskCheckResult:
    if peak_equity <= 0:
        return RiskCheckResult(
            verdict=RiskVerdict.PASS,
            check_name="drawdown_halt",
            reason="No peak equity recorded",
        )

    drawdown = (peak_equity - equity) / peak_equity

    if drawdown >= halt_threshold_pct:
        return RiskCheckResult(
            verdict=RiskVerdict.FAIL,
            check_name="drawdown_halt",
            reason=f"Drawdown {drawdown:.2%} >= halt threshold {halt_threshold_pct:.2%}",
        )

    return RiskCheckResult(
        verdict=RiskVerdict.PASS,
        check_name="drawdown_halt",
        reason=f"Drawdown {drawdown:.2%} < {halt_threshold_pct:.2%}",
    )


def run_all_risk_checks(
    symbol: str,
    side: str,
    qty: float,
    price: float,
    equity: float,
    daily_pnl: float,
    positions: list[dict],
    symbol_sector: str = "",
    peak_equity: float = 0.0,
    config: dict | None = None,
) -> list[RiskCheckResult]:
    if config is None:
        config = load_risk_config()

    risk_cfg = config.get("risk", {})
    position_cfg = risk_cfg.get("position_sizing", {})
    daily_cfg = risk_cfg.get("daily_limits", {})
    drawdown_cfg = risk_cfg.get("drawdown", {})
    market_cfg = risk_cfg.get("market_rules", {})

    results: list[RiskCheckResult] = []

    results.append(
        check_max_position_size(
            symbol=symbol,
            qty=qty,
            price=price,
            equity=equity,
            max_pct=position_cfg.get("max_position_pct", 0.03),
        )
    )

    if market_cfg.get("market_hours_only", True):
        results.append(check_market_hours())

    results.append(
        check_daily_loss_limit(
            daily_pnl=daily_pnl,
            equity=equity,
            max_daily_loss_pct=daily_cfg.get("max_daily_loss_pct", 0.02),
        )
    )

    if symbol_sector:
        results.append(
            check_portfolio_concentration(
                symbol_sector=symbol_sector,
                order_value=qty * price,
                positions=positions,
                equity=equity,
                max_concentration_pct=position_cfg.get("max_portfolio_concentration_pct", 0.15),
            )
        )

    if drawdown_cfg.get("halt_on_drawdown", True):
        results.append(
            check_drawdown_halt(
                equity=equity,
                peak_equity=peak_equity,
                halt_threshold_pct=drawdown_cfg.get("halt_threshold_pct", 0.05),
            )
        )

    for r in results:
        status = "PASS" if r.verdict == RiskVerdict.PASS else "FAIL"
        logger.info(f"Risk check [{r.check_name}]: {status} — {r.reason}")

    return results


def is_trade_approved(results: list[RiskCheckResult]) -> bool:
    return all(r.verdict == RiskVerdict.PASS for r in results)
