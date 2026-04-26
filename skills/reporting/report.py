from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import httpx
from loguru import logger

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def _send_telegram(text: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.warning("Telegram credentials not configured, skipping notification")
        return False

    url = TELEGRAM_API.format(token=token)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}

    try:
        resp = httpx.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info("Telegram notification sent")
            return True
        else:
            logger.error(f"Telegram API error: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def notify_trade(symbol: str, side: str, qty: float, price: float, order_id: str) -> bool:
    msg = (
        f"📊 *Trade Executed*\n"
        f"• {side.upper()} {qty} {symbol} @ ${price:.2f}\n"
        f"• Order ID: `{order_id}`\n"
        f"• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    return _send_telegram(msg)


def notify_risk_alert(reason: str) -> bool:
    msg = (
        f"🚨 *Risk Alert*\n"
        f"• {reason}\n"
        f"• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    return _send_telegram(msg)


def notify_order_rejected(symbol: str, side: str, reason: str) -> bool:
    msg = (
        f"❌ *Order Rejected*\n"
        f"• {side.upper()} {symbol}\n"
        f"• Reason: {reason}\n"
        f"• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    return _send_telegram(msg)


def generate_daily_report(
    account: dict,
    positions: list[dict],
    trades: list[dict],
    signals_generated: int,
    signals_executed: int,
) -> str:
    equity = account.get("equity", 0)
    cash = account.get("cash", 0)
    long_value = account.get("long_market_value", 0)

    lines = [
        f"📋 *Daily Trading Report* — {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "*Account:*",
        f"• Equity: ${equity:,.2f}",
        f"• Cash: ${cash:,.2f}",
        f"• Long Value: ${long_value:,.2f}",
        "",
        "*Activity:*",
        f"• Signals generated: {signals_generated}",
        f"• Trades executed: {signals_executed}",
        f"• Open positions: {len(positions)}",
    ]

    if positions:
        lines.append("")
        lines.append("*Open Positions:*")
        for p in positions[:10]:
            pnl_pct = p.get("unrealized_plpc", 0) * 100
            emoji = "🟢" if pnl_pct >= 0 else "🔴"
            lines.append(f"• {emoji} {p['symbol']}: {p['qty']} shares, {pnl_pct:+.2f}%")

    if trades:
        lines.append("")
        lines.append("*Today's Trades:*")
        for t in trades[:10]:
            lines.append(f"• {t.get('side', '').upper()} {t.get('qty', 0)} {t.get('symbol', '')}")

    return "\n".join(lines)


def send_daily_report(
    account: dict,
    positions: list[dict],
    trades: list[dict],
    signals_generated: int,
    signals_executed: int,
) -> bool:
    report = generate_daily_report(account, positions, trades, signals_generated, signals_executed)
    _send_telegram(report)
    _save_json_report(account, positions, trades, signals_generated, signals_executed)
    return True


def _save_json_report(
    account: dict,
    positions: list[dict],
    trades: list[dict],
    signals_generated: int,
    signals_executed: int,
) -> Path:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = logs_dir / f"report_{date_str}.json"

    report = {
        "date": date_str,
        "timestamp": datetime.now().isoformat(),
        "account": account,
        "positions": positions,
        "trades": trades,
        "signals_generated": signals_generated,
        "signals_executed": signals_executed,
    }

    with open(filepath, "w") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"JSON report saved to {filepath}")
    return filepath
