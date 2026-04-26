# ROADMAP.md

> **Current Phase**: Phase 1
> **Milestone**: v1.0 (Paper Trading Prototype)

## Must-Haves (from SPEC)
- [ ] Environnement Python 3.12+ avec dépendances installées
- [ ] OpenClaw Gateway opérationnel
- [ ] Connexion fonctionnelle à l'API Alpaca Paper Trading
- [ ] Data Agent fonctionnel (fetch + indicateurs)
- [ ] Strategy Agent fonctionnel (RSI Mean Reversion)
- [ ] Risk Agent fonctionnel (limites conservatrices)
- [ ] Execution Agent fonctionnel (paper orders)
- [ ] Notifications Telegram (trades, alertes)
- [ ] Paper Trading validé sur 2 semaines minimum

## Phases

### Phase 1: Foundation & Environment Setup
**Status**: 🟡 In Progress
**Objective**: Créer l'arborescence, configurer Python + OpenClaw, obtenir les clés API Alpaca.

- [ ] 1.1 Créer l'arborescence projet (config/, skills/, scripts/, tests/, logs/)
- [ ] 1.2 Setup Python 3.12+ avec uv + pyproject.toml + dépendances
- [ ] 1.3 Setup OpenClaw Gateway (npm install openclaw, openclaw onboard)
- [ ] 1.4 Configurer les variables d'environnement (.env.example → .env)
- [ ] 1.5 Obtenir les clés API Alpaca Paper Trading (trade-only, withdraw disabled)

### Phase 2: Data & Strategy Layer
**Status**: ⬜ Not Started
**Objective**: Implémenter le Data Agent et le Strategy Agent avec la stratégie RSI Mean Reversion.

- [ ] 2.1 Implémenter Data Agent (fetch bars via alpaca-py, compute RSI/SMA/Volume)
- [ ] 2.2 Implémenter Strategy Agent (RSI Mean Reversion: RSI < 30 → BUY, RSI > 65 → SELL)
- [ ] 2.3 Tests unitaires Data Agent + Strategy Agent
- [ ] 2.4 Backtest RSI strategy sur 6-12 mois avec vectorbt

### Phase 3: Risk & Execution Layer
**Status**: ⬜ Not Started
**Objective**: Implémenter le Risk Agent (bouncer) et l'Execution Agent (ordres paper).

- [ ] 3.1 Implémenter Risk Agent (max position 3%, daily loss 2%, drawdown halt, market hours, pre-earnings 48h)
- [ ] 3.2 Implémenter Execution Agent (place/cancel orders via alpaca-py)
- [ ] 3.3 Tests unitaires Risk Agent + Execution Agent
- [ ] 3.4 Intégration complète Data → Strategy → Risk → Execution

### Phase 4: Orchestration & Monitoring
**Status**: ⬜ Not Started
**Objective**: Configurer les cron jobs, Telegram, logging, et lancer le paper trading.

- [ ] 4.1 Configurer cron jobs OpenClaw (premarket 08:45, live 09:31, check 12:00, close 15:45, report 17:00)
- [ ] 4.2 Configurer notifications Telegram (trades exécutés, alertes drawdown, daily report)
- [ ] 4.3 Logging JSON structuré + healthcheck endpoint
- [ ] 4.4 Paper Trading — 2 semaines minimum, audit manuel quotidien des logs

### Phase 5: VPS Deployment & Validation
**Status**: ⬜ Not Started
**Objective**: Déployer en production sur VPS et valider le système en conditions réelles.

- [ ] 5.1 Provisionner VPS Ubuntu 24.04 (DigitalOcean/Linode $6-12/mo)
- [ ] 5.2 Déployer: git clone + uv sync + npm install
- [ ] 5.3 Configurer systemd pour le service OpenClaw Gateway
- [ ] 5.4 Vérifier cron jobs + healthchecks en production
- [ ] 5.5 Paper Trading validation finale (30 sessions) avant décision go-live
