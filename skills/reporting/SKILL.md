# Reporting Skill

Generates daily trading reports and sends Telegram notifications.

## Triggers
- Cron: 17:00 ET (daily report)
- On trade execution (immediate notification)
- On risk alert (drawdown halt, daily loss limit)

## Outputs
- Daily summary: P&L, positions, signals, executed trades, drawdown
- Telegram message via OpenClaw channel
- JSON log file in logs/

## Configuration
- Telegram Bot Token + Chat ID (env vars)
