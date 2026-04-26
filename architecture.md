# System Architecture

## Vue Globale

Le système est articulé autour d'un **VPS distant** exécutant **OpenClaw Gateway** comme orchestrateur IA, avec 4 skills Python personnalisés implémentant la logique de trading. OpenClaw fournit l'infrastructure (cron, MCP, canaux de notification, session management). La logique métier (données, stratégie, exécution, risque) est construite au-dessus.

```
┌─────────────────────────────────────────────────────────┐
│                      VPS Linux (Ubuntu 24.04)            │
│  ┌───────────────────────────────────────────────────┐  │
│  │              OpenClaw Gateway                      │  │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │ Cron    │  │ MCP      │  │ Channels         │  │  │
│  │  │ Scheduler│  │ Bridge   │  │ (Telegram/Slack) │  │  │
│  │  └────┬────┘  └────┬─────┘  └────────┬─────────┘  │  │
│  │       │            │                 │             │  │
│  │  ┌────▼────────────▼─────────────────▼─────────┐   │  │
│  │  │         Custom Trading Skills (Python)       │   │  │
│  │  │  ┌────────┬──────────┬──────────┬────────┐  │   │  │
│  │  │  │ Data   │ Strategy │Execution │ Risk   │  │   │  │
│  │  │  │ Agent  │ Agent    │ Agent    │ Agent  │  │   │  │
│  │  │  └───┬────┴────┬─────┴────┬─────┴───┬────┘  │   │  │
│  │  │      │         │          │         │       │   │  │
│  │  └──────┼─────────┼──────────┼─────────┼───────┘   │  │
│  └─────────┼─────────┼──────────┼─────────┼───────────┘  │
│            │         │          │         │               │
│  ┌─────────▼──┐ ┌───▼────┐ ┌───▼──────┐ ┌▼───────────┐  │
│  │ Alpaca     │ │RSI/SMA │ │ Alpaca   │ │Position/   │  │
│  │ Data API   │ │Engine  │ │ Orders   │ │Drawdown    │  │
│  │ v2         │ │        │ │ API      │ │Checker     │  │
│  └────────────┘ └────────┘ └──────────┘ └────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Les 4 Agents (Skills Python)

### 1. Data Agent (`skills/data_agent/`)
Fetch les données de marché via l'API Alpaca Data v2 et calcule les indicateurs techniques.
- **Entrée**: Watchlist de tickers, bar_size (5min/daily)
- **Sortie**: DataFrame avec OHLCV + RSI_14, SMA_20, SMA_50, AVG_VOL_20D
- **Source**: `alpaca-py` SDK (Alpaca Data API v2, gratuit avec compte)

### 2. Strategy Agent (`skills/strategy_agent/`)
Évalue les données contre les règles définies et génère des signaux.
- **Entrée**: DataFrame du Data Agent
- **Sortie**: Signal (BUY / SELL / HOLD / SKIP) + taille de position suggérée
- **Stratégie initiale**: RSI Mean Reversion (RSI < 30 + Volume > 1.5x avg → BUY ; RSI > 65 → SELL)

### 3. Execution Agent (`skills/execution_agent/`)
Place et gère les ordres via Alpaca API, uniquement après validation du Risk Agent.
- **Entrée**: Signal + taille de position (validés par Risk Agent)
- **Sortie**: Ordre exécuté (ou rejeté) + confirmation
- **Canal**: `alpaca-mcp-server` (MCP) ou `alpaca-py` direct

### 4. Risk Agent (`skills/risk_agent/`)
Bouncer — vérifie chaque trade avant exécution. Bloque tout ordre hors limites.
- **Vérifications**: max_position_size, portfolio_concentration, daily_loss_limit, market_hours_only, no_trade_pre_earnings_48h
- **Paramètres**: conservateurs au début (3% max par position, 2% perte quotidienne max, halt_on_drawdown)

## Flux de Décision Complet

```
[Cron trigger]
    → Data Agent (fetch prices + compute indicators)
    → Strategy Agent (evaluate RSI rules → signal)
    → Risk Agent (check limits, exposure, drawdown)
        ├─ [PASS] → Execution Agent (place order via Alpaca) → Alpaca Paper Trading
        └─ [FAIL] → Log rejection reason + notify Telegram
    → Log JSON (every step, every handoff)
    → Daily report at 17:00 ET
```

## Orchestration (Cron Jobs)

| Heure (ET) | Mode | Action |
|-------------|------|--------|
| 08:45 | premarket | Fetch pre-market data, morning checks |
| 09:31 | live | Start live trading loop |
| 12:00 | check | Midday health check |
| 15:45 | close | Close all positions (si configuré) |
| 17:00 | report | Generate daily report + Telegram summary |

Restriction: weekdays only (lundi-vendredi).

## Composants de Sécurité

- Les clés API sont stockées en **variables d'environnement** sur le VPS (jamais dans le code source, jamais dans `.env` commité).
- Clé API Alpaca générée avec **Trade-Only** (Withdraw = Disabled). Impossibilité mathématique de retirer des fonds.
- **Paper Trading** activé pour les 30 premières sessions minimum avant tout live.
- VPS uniquement — jamais de production sur machine locale.
- Chaque ordre est validé par le Risk Agent avant exécution.
- Logging JSON exhaustif pour audit post-trade.

## Monitoring & Alerting

- Logs JSON structurés après chaque session (dans `logs/`)
- Health check à chaque cron run (timestamp + statut)
- Notification Telegram si: échec cron, drawdown > seuil, ordre rejeté inattendu
- Export logs pour audit manuel hebdomadaire
- Daily report: P&L, positions ouvertes, signaux générés vs exécutés, drawdown max

## Flux de Données Critique

```
Market Data → Data Agent → Strategy Agent → Risk Agent → Execution Agent → Alpaca API
                                              ↓ Rejet
                                         Log + Telegram Alert
```
