# Risk Agent Skill

Validates every trade before execution. Acts as the bouncer that checks every order at the door.

## Triggers
- Before every order placed by Execution Agent
- Manual: `/risk-check [symbol] [side] [qty]`

## Checks (in order)
1. **max_position_size**: Single position <= 3% of portfolio
2. **portfolio_concentration**: No sector > 15% of portfolio
3. **daily_loss_limit**: Daily loss <= 2% of portfolio
4. **market_hours_only**: No trading outside 09:30-16:00 ET
5. **no_trade_pre_earnings_48h**: No new positions 48h before earnings
6. **drawdown_halt**: If drawdown > 5%, halt all trading for 24h

## Inputs
- Proposed trade (symbol, side, qty, price)
- Current portfolio state (positions, equity, daily P&L)

## Outputs
- PASS: Trade approved
- FAIL: Trade rejected with reason

## Configuration
- `config/risk.yaml`
