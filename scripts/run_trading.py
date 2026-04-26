from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from skills.data_agent.fetch import fetch_bars  # noqa: E402
from skills.data_agent.indicators import enrich_all, get_latest_indicators  # noqa: E402
from skills.execution_agent.orders import (  # noqa: E402
    close_position,
    get_account_info,
    get_positions,
    place_limit_order,
)
from skills.reporting.report import (  # noqa: E402
    notify_order_rejected,
    notify_trade,
    send_daily_report,
)
from skills.risk_agent.checks import is_trade_approved, run_all_risk_checks  # noqa: E402
from skills.strategy_agent.evaluate import Signal, evaluate_entry, evaluate_exit  # noqa: E402


def run_premarket():
    logger.info("=== PREMARKET CHECK ===")
    account = get_account_info()
    logger.info(f"Account equity: ${account.get('equity', 0):,.2f}")
    logger.info(f"Cash: ${account.get('cash', 0):,.2f}")
    logger.info(f"Trading blocked: {account.get('trading_blocked', False)}")
    return account


def run_live_trading(watchlist: list[str]):
    logger.info("=== LIVE TRADING CYCLE ===")

    account = get_account_info()
    equity = account.get("equity", 0)
    daily_pnl = 0.0

    positions = get_positions()
    position_symbols = {p["symbol"] for p in positions}

    bars = fetch_bars(watchlist, bar_size="5Min", lookback_days=5)
    enriched = enrich_all(bars)

    signals_generated = 0
    trades: list[dict] = []

    for symbol, df in enriched.items():
        indicators = get_latest_indicators(df)
        if not indicators:
            continue

        if symbol in position_symbols:
            pos = next(p for p in positions if p["symbol"] == symbol)
            unrealized_loss_pct = pos.get("unrealized_plpc", 0)
            signal = evaluate_exit(symbol, indicators, unrealized_loss_pct=unrealized_loss_pct)
        else:
            signal = evaluate_entry(symbol, indicators)

        signals_generated += 1

        if signal.signal in (Signal.HOLD, Signal.SKIP):
            logger.info(f"[{symbol}] {signal.signal.value}: {signal.rationale}")
            continue

        if signal.signal == Signal.BUY:
            price = indicators.get("close", 0)
            if price <= 0:
                continue

            qty = max(1, int((equity * signal.position_size_pct) / price))

            risk_results = run_all_risk_checks(
                symbol=symbol,
                side="buy",
                qty=qty,
                price=price,
                equity=equity,
                daily_pnl=daily_pnl,
                positions=positions,
                peak_equity=equity,
            )

            if not is_trade_approved(risk_results):
                for r in risk_results:
                    if r.verdict != "pass":
                        notify_order_rejected(symbol, "buy", r.reason)
                continue

            order = place_limit_order(symbol, "buy", qty, price * 1.001)

            if "error" not in order:
                trades.append(order)
                notify_trade(symbol, "buy", qty, price, order.get("order_id", ""))
            else:
                notify_order_rejected(symbol, "buy", order["error"])

        elif signal.signal == Signal.SELL:
            order = close_position(symbol)

            if "error" not in order:
                trades.append(order)
                notify_trade(symbol, "sell", 0, 0, order.get("order_id", ""))

    return {
        "signals_generated": signals_generated,
        "trades_executed": len(trades),
        "trades": trades,
    }


def run_close_all():
    logger.info("=== CLOSING ALL POSITIONS ===")
    positions = get_positions()
    for p in positions:
        symbol = p["symbol"]
        logger.info(f"Closing position: {symbol}")
        result = close_position(symbol)
        if "error" in result:
            logger.error(f"Failed to close {symbol}: {result['error']}")


def run_report(account: dict, trading_summary: dict):
    logger.info("=== DAILY REPORT ===")
    positions = get_positions()
    send_daily_report(
        account=account,
        positions=positions,
        trades=trading_summary.get("trades", []),
        signals_generated=trading_summary.get("signals_generated", 0),
        signals_executed=trading_summary.get("trades_executed", 0),
    )


def load_watchlist() -> list[str]:
    path = Path("config/watchlist.json")
    with open(path) as f:
        data = json.load(f)
    return [item["symbol"] for item in data]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "live"

    logger.add(
        f"logs/trading_{datetime.now().strftime('%Y-%m-%d')}.log",
        rotation="1 day",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    logger.info(f"Starting trading run in mode: {mode}")

    if mode == "premarket":
        run_premarket()
    elif mode == "live":
        watchlist = load_watchlist()
        run_live_trading(watchlist)
    elif mode == "close":
        run_close_all()
    elif mode == "report":
        account = get_account_info()
        run_report(account, {})
    elif mode == "full":
        watchlist = load_watchlist()
        account = run_premarket()
        summary = run_live_trading(watchlist)
        run_report(account, summary)
    else:
        logger.error(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
