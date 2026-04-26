# DECISIONS.md

## 2026-04-26: Architecture Initiale

### D1: OpenClaw comme orchestrateur, pas comme framework de trading
**Decision**: Utiliser OpenClaw comme gateway/orchestrateur (cron, MCP, canaux Telegram) et construire la logique trading en Python custom.
**Rationale**: OpenClaw est un assistant IA personnel multi-canal, pas un framework de trading dédié. L'article MindStudio décrit une architecture conceptuelle à construire par-dessus.
**Alternatives considérées**: Coder from scratch sans OpenClaw, utiliser CrewAI.

### D2: Alpaca Data API v2 comme data provider
**Decision**: Utiliser Alpaca Data API v2 (gratuit avec compte) plutôt que Polygon.io.
**Rationale**: Suffisant pour US stocks/ETFs, pas de coût mensuel supplémentaire, intégration native avec alpaca-py.
**Alternatives considérées**: Polygon.io (qualité pro mais payant).

### D3: RSI Mean Reversion comme stratégie initiale
**Decision**: Commencer avec RSI Mean Reversion (RSI < 30 + volume → BUY, RSI > 65 → SELL).
**Rationale**: Simple, rule-based, clair, testable. Recommandé par l'article MindStudio comme bon candidat pour l'automatisation.
**Alternatives considérées**: SMA Crossover, multi-signaux complexes.

### D4: Telegram Bot API pour les notifications
**Decision**: Utiliser Telegram pour les alertes (trades, drawdown, daily report).
**Rationale**: Intégration native via OpenClaw channels, gratuit, temps réel, facile à configurer.
**Alternatives considérées**: Email SMTP.

### D5: Python 3.12+ avec uv comme gestionnaire de dépendances
**Decision**: Utiliser Python 3.12+ avec `uv` et `pyproject.toml`.
**Rationale**: Standard moderne, rapide, cohérent avec les projets OpenClaw récents (ex: openclaw-lse-trading-agent).
**Alternatives considérées**: pip + requirements.txt, Poetry.

### D6: 4 agents séparés plutôt qu'un monolithe
**Decision**: Architecture Data / Strategy / Execution / Risk en modules séparés.
**Rationale**: Chaque agent est configurable et testable indépendamment. Quand quelque chose casse, on sait quel couche a causé le problème.
**Alternatives considérées**: Script monolithique unique.
