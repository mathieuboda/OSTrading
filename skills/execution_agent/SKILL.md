# Execution Agent Skill

Places and manages orders through the Alpaca API.

## Triggers
- After Risk Agent approves a signal
- Manual: `/execute-order [symbol] [side] [qty]`

## Inputs
- Validated signal from Strategy Agent (approved by Risk Agent)
- Position size from Risk Agent

## Outputs
- Order confirmation (order_id, status, filled_price, filled_qty)
- Or rejection reason

## Order Settings
- Type: limit (with slippage buffer)
- Time-in-force: day
- Slippage buffer: 0.1%

## Dependencies
- alpaca-py (Alpaca Trading API)
