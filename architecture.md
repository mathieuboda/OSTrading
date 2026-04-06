# System Architecture

## Architecture Globale
Le système est articulé autour d'un **VPS distant** exécutant l'agent.
1. **Le Cerveau** : Framework OpenClaw agissant comme l'orchestrateur IA.
2. **Les Skills (MCP)** : 
   - `alpaca-mcp-server` pour interagir avec le courtier (ordres, portfolio).
   - Outils de lecture web pour l'analyse de sentiment.
3. **Le Courtier** : API Alpaca, utilisé dans son environnement de "Paper Trading" pour le développement.

## Composants de Sécurité
- Les clés privées/API sont stockées de manière sécurisée en variables d'environnement sur le VPS (pas de code source).
- La clé de l'API Broker est générée SANS la permission de procéder à des retraits financiers (Withdraw = Disabled).

## Flux de donnée critique
Flux -> Analyse LLM -> Décision -> Execution API -> Log.
