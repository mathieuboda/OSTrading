from __future__ import annotations

from unittest.mock import patch

from skills.execution_agent.orders import (
    get_account_info,
    get_positions,
    place_limit_order,
)


def test_get_account_info():
    mock_account = type("Account", (), {
        "cash": "50000.00",
        "equity": "100000.00",
        "buying_power": "200000.00",
        "long_market_value": "50000.00",
        "short_market_value": "0.00",
        "pattern_day_trader": False,
        "trading_blocked": False,
        "transfers_blocked": False,
    })()

    with patch("skills.execution_agent.orders._get_trading_client") as mock_client:
        mock_client.return_value.get_account.return_value = mock_account
        result = get_account_info()

    assert result["cash"] == 50000.0
    assert result["equity"] == 100000.0
    assert result["trading_blocked"] is False


def test_get_positions():
    mock_position = type("Position", (), {
        "symbol": "AAPL",
        "qty": "10",
        "side": "long",
        "market_value": "1500.00",
        "cost_basis": "1400.00",
        "unrealized_pl": "100.00",
        "unrealized_plpc": "0.0714",
        "current_price": "150.00",
        "avg_entry_price": "140.00",
    })()

    with patch("skills.execution_agent.orders._get_trading_client") as mock_client:
        mock_client.return_value.get_all_positions.return_value = [mock_position]
        result = get_positions()

    assert len(result) == 1
    assert result[0]["symbol"] == "AAPL"
    assert result[0]["qty"] == 10.0


def test_place_limit_order_error():
    with patch("skills.execution_agent.orders._get_trading_client") as mock_client:
        mock_client.return_value.submit_order.side_effect = Exception("API error")
        result = place_limit_order("AAPL", "buy", 1, 150.0)

    assert "error" in result
    assert "API error" in result["error"]
