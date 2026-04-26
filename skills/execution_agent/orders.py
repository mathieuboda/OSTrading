from __future__ import annotations

import os

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
from loguru import logger


def _get_trading_client() -> TradingClient:
    api_key = os.environ["ALPACA_API_KEY"]
    secret = os.environ["ALPACA_API_SECRET"]
    paper = os.environ.get("ALPACA_PAPER_TRADING", "true").lower() == "true"
    return TradingClient(api_key, secret, paper=paper)


def get_account_info() -> dict:
    client = _get_trading_client()
    account = client.get_account()
    return {
        "cash": float(account.cash),
        "equity": float(account.equity),
        "buying_power": float(account.buying_power),
        "long_market_value": float(account.long_market_value),
        "short_market_value": float(account.short_market_value),
        "pattern_day_trader": account.pattern_day_trader,
        "trading_blocked": account.trading_blocked,
        "transfers_blocked": account.transfers_blocked,
    }


def get_positions() -> list[dict]:
    client = _get_trading_client()
    positions = client.get_all_positions()
    return [
        {
            "symbol": p.symbol,
            "qty": float(p.qty),
            "side": p.side,
            "market_value": float(p.market_value),
            "cost_basis": float(p.cost_basis),
            "unrealized_pl": float(p.unrealized_pl),
            "unrealized_plpc": float(p.unrealized_plpc),
            "current_price": float(p.current_price),
            "avg_entry_price": float(p.avg_entry_price),
        }
        for p in positions
    ]


def place_limit_order(
    symbol: str,
    side: str,
    qty: float,
    limit_price: float,
    time_in_force: str = "day",
) -> dict:
    client = _get_trading_client()

    order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
    tif = TimeInForce.DAY if time_in_force == "day" else TimeInForce.GTC

    request = LimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=order_side,
        time_in_force=tif,
        limit_price=round(limit_price, 2),
    )

    try:
        order = client.submit_order(request)
        logger.info(f"Order submitted: {side} {qty} {symbol} @ {limit_price} (id={order.id})")
        return {
            "order_id": str(order.id),
            "symbol": order.symbol,
            "side": order.side.value,
            "qty": float(order.qty),
            "limit_price": float(order.limit_price) if order.limit_price else None,
            "status": order.status.value,
            "created_at": str(order.created_at),
        }
    except Exception as e:
        logger.error(f"Order failed: {side} {qty} {symbol} @ {limit_price}: {e}")
        return {"error": str(e), "symbol": symbol, "side": side, "qty": qty}


def place_market_order(
    symbol: str,
    side: str,
    qty: float,
    time_in_force: str = "day",
) -> dict:
    client = _get_trading_client()

    order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
    tif = TimeInForce.DAY if time_in_force == "day" else TimeInForce.GTC

    request = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=order_side,
        time_in_force=tif,
    )

    try:
        order = client.submit_order(request)
        logger.info(f"Market order submitted: {side} {qty} {symbol} (id={order.id})")
        return {
            "order_id": str(order.id),
            "symbol": order.symbol,
            "side": order.side.value,
            "qty": float(order.qty),
            "status": order.status.value,
            "created_at": str(order.created_at),
        }
    except Exception as e:
        logger.error(f"Market order failed: {side} {qty} {symbol}: {e}")
        return {"error": str(e), "symbol": symbol, "side": side, "qty": qty}


def cancel_all_orders() -> dict:
    client = _get_trading_client()
    try:
        cancellations = client.cancel_orders()
        logger.info("Cancelled all open orders")
        return {"cancelled": True, "count": len(cancellations) if cancellations else 0}
    except Exception as e:
        logger.error(f"Cancel orders failed: {e}")
        return {"error": str(e)}


def close_position(symbol: str) -> dict:
    client = _get_trading_client()
    try:
        close = client.close_position(symbol)
        logger.info(f"Closed position: {symbol}")
        return {
            "order_id": str(close.id),
            "symbol": close.symbol,
            "status": close.status.value,
        }
    except Exception as e:
        logger.error(f"Close position failed for {symbol}: {e}")
        return {"error": str(e), "symbol": symbol}
