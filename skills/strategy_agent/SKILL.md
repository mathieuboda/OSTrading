# Strategy Agent Skill

Evaluates market data against defined rules and generates trading signals.

## Triggers
- After Data Agent completes a fetch cycle
- Manual: `/strategy-evaluate [symbol]`

## Strategy: RSI Mean Reversion
- **Entry**: RSI(14) < 30 AND Volume > 1.5x 20-day average
- **Exit**: RSI(14) > 65 OR Unrealized loss > 5%

## Inputs
- Enriched DataFrame from Data Agent (with RSI, SMA, Volume indicators)

## Outputs
- Signal: BUY, SELL, HOLD, SKIP
- Suggested position size (passed to Risk Agent for validation)
- Rationale string (for logging)

## Configuration
- `config/strategy.yaml`
