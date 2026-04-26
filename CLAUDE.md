# CLAUDE.md — OpenClaw Alpaca Trader

## Project Overview

Autonomous AI trading system running on a VPS with Docker. Orchestrated via **OpenClaw Gateway** (Node.js), with 4 Python trading agents (Data, Strategy, Risk, Execution) connecting to **Alpaca Paper Trading API**.

**Current milestone**: v1.0 — Paper Trading Prototype  
**Current phase**: Phase 1 (Foundation) — In Progress  
**VPS**: `root@187.77.161.164` (Docker already installed)

---

## Architecture

```
Docker on VPS
├── openclaw-gateway  (Node.js 20, port 3000)
└── trading-agents    (Python 3.12, uv)
```

Decision flow: `Cron → Data Agent → Strategy Agent → Risk Agent → [PASS] Execution Agent → Alpaca Paper`

4 agents in `skills/`:
- `data_agent/` — fetch OHLCV + compute RSI/SMA via alpaca-py
- `strategy_agent/` — RSI Mean Reversion (RSI < 30 → BUY, RSI > 65 → SELL)
- `risk_agent/` — bouncer: max 3% per position, 2% daily loss, drawdown halt
- `execution_agent/` — place/cancel orders via alpaca-py
- `reporting/` — daily Telegram summary + JSON logs

---

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python deps (managed via `uv`) |
| `config/strategy.yaml` | RSI strategy rules |
| `config/risk.yaml` | Risk limits |
| `config/watchlist.json` | Tickers to trade |
| `scripts/run_trading.py` | Entry point (modes: premarket/live/check/close/report) |
| `scripts/healthcheck.py` | Health check for cron/Docker |
| `.env.example` | Env var template — never commit `.env` |

---

## Environment Variables

Required in `.env` (never committed):
```
ALPACA_API_KEY
ALPACA_API_SECRET
ALPACA_PAPER_TRADING=true
ALPACA_DATA_URL=https://data.alpaca.markets
ALPACA_TRADING_URL=https://paper-api.alpaca.markets
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
OPENCLAW_GATEWAY_URL=http://localhost:3000
MAX_POSITION_PCT=0.03
MAX_DAILY_LOSS_PCT=0.02
HALT_ON_DRAWDOWN=true
```

---

## Commands

```bash
# Install Python deps
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Run trading (local dev)
uv run python scripts/run_trading.py --mode live

# Health check
uv run python scripts/healthcheck.py
```

---

## Docker Deployment (VPS: 187.77.161.164)

The project is containerized for the VPS. Docker is already installed on the server.

```bash
# Build and start
docker compose up -d --build

# View logs
docker compose logs -f trading-agents

# Restart
docker compose restart
```

Files:
- `Dockerfile` — Python 3.12-slim + uv, cron daemon
- `docker-compose.yml` — `trading-agents` service, logs volume, env_file
- `.dockerignore` — excludes `.venv/`, `logs/`, `.env`, tests, docs
- `docker/entrypoint.sh` — exports env vars to `/etc/environment` for cron
- `docker/trading.crontab` — full cron schedule (ET timezone via `TZ=America/New_York`)

**Deploy to VPS:**
```bash
# On VPS (SSH as root@187.77.161.164)
git clone <repo> /opt/trading
cd /opt/trading
cp .env.example .env && nano .env   # fill API keys
docker compose up -d --build

# Verify
docker compose logs -f
docker exec trading-agents python scripts/healthcheck.py
```

---

## Cron Schedule (ET, weekdays only)

| Time | Mode | Action |
|------|------|--------|
| 08:45 | premarket | Pre-market fetch + checks |
| 09:31 | live | Start live trading loop |
| 12:00 | check | Midday health check |
| 15:45 | close | Close all positions |
| 17:00 | report | Daily report → Telegram |

---

## Security Rules

- API keys in env vars only — **never in source code or `.env` committed**
- Alpaca key generated with Trade-Only scope (Withdraw = Disabled)
- Paper Trading mode only until 30+ sessions validated
- Every order validated by Risk Agent before execution
- All logs go to `logs/` (JSON, rotated daily)

---

## Stack

- **Python 3.12+** via `uv`
- **alpaca-py** — Alpaca SDK (data + orders)
- **pandas / numpy / ta** — data manipulation + technical indicators
- **vectorbt** — backtesting
- **loguru** — structured logging
- **OpenClaw** (npm) — Gateway, cron, MCP, Telegram channel
- **Docker** — containerization for VPS deployment
- **Ubuntu 24.04 LTS** on VPS

---

## Conventions

- Python: ruff lint, 120 char line length, Python 3.12 target
- No secrets in code — use `os.getenv()` or `python-dotenv` for local dev
- All agent outputs logged as JSON before passing to next agent
- Risk Agent is a hard gate — no execution without PASS
- Tests in `tests/` — one file per agent
