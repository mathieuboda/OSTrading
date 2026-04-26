# Technologies Utilisées

## Runtime
- **Python 3.12+** : Langage principal pour les skills de trading (via `uv` pour la gestion des dépendances)
- **Node.js 20+** : Runtime pour OpenClaw Gateway

## Framework Orchestration
- **OpenClaw** (`npm install -g openclaw`, version 2026.4.x) : Assistant IA personnel multi-canal, fournit gateway, cron, MCP, canaux (Telegram, Slack...), système de skills modulaires

## APIs & Intégrations
- **alpaca-py** : SDK Python officiel Alpaca (données de marché + ordres)
- **alpaca-mcp-server** : Bridge MCP standardisé pour connecter le LLM à l'API Alpaca (ordres, portfolio, positions)
- **Alpaca Data API v2** : Données de marché US stocks/ETFs (gratuit avec compte Alpaca)

## Analyse Technique & Data
- **pandas** : Manipulation de données tabulaires (OHLCV, indicateurs)
- **numpy** : Calculs numériques
- **ta** (technical-analysis) : Bibliothèque d'indicateurs techniques (RSI, SMA, EMA, MACD, Bollinger, ATR, OBV)

## Backtest
- **vectorbt** : Backtesting vectoriel rapide avec métriques (Sharpe, drawdown, win rate)

## Logging & Monitoring
- **loguru** : Logging structuré avec rotation automatique
- **JSON logs** : Format standardisé pour parsing et audit

## Notifications
- **Telegram Bot API** : Alertes temps réel (intégration native via OpenClaw channels)

## Dev & Test
- **pytest** : Framework de test
- **ruff** : Linter et formateur Python
- **python-dotenv** : Gestion des variables d'environnement en développement

## Infrastructure
- **VPS Ubuntu 24.04 LTS** : Hébergement production (DigitalOcean / Linode / AWS Lightsail, ~$6-12/mo)
- **systemd** : Gestion du service OpenClaw Gateway
- **Git** : Versioning du code métier
