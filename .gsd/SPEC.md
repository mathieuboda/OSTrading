# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
Créer un agent de trading IA autonome ("OpenClaw Alpaca Trader") hébergé sur VPS, spécialisé dans l'investissement sur les actions traditionnelles (US Stocks) et les devises (Forex). L'agent exploitera les capacités d'analyse web (actualités, X/Twitter, métriques sociales) et d'outils quantitatifs pour automatiser la prise de décision via l'API sécurisée d'Alpaca.

## Goals
1. Mettre en place un environnement VPS sécurisé capable de faire tourner l'agent IA OpenClaw 24/7.
2. Intégrer l'agent avec l'API d'Alpaca (commencer par l'environnement Paper Trading pour valider les modèles sans risque financier).
3. Développer et intégrer des compétences ("skills") d'analyse de sentiment (web scraping, flux X/Twitter, actualités financières) pour influencer les décisions de l'agent.

## Non-Goals (Out of Scope)
- Trading de cryptomonnaies ou de marchés de prédiction décentralisés (Polymarket).
- Hébergement de l'agent sur un ordinateur personnel avec des clés API ayant des permissions de retrait.
- Utilisation de scripts tiers non audités (pour éviter les attaques "supply-chain" comme ClawHavoc).

## Users
Un investisseur particulier cherchant à automatiser ses investissements en bourse classique en tirant parti de "l'alpha agentique" des LLMs pour interpréter les signaux du marché en temps réel.

## Constraints
- **Sécurité (Critique)** : L'agent doit impérativement utiliser des clés API Alpaca en "Trade-Only" (impossibilité mathématique de retirer des fonds).
- **Techniques** : Nécessite une configuration VPS robuste, potentiellement avec Model Context Protocol (MCP).
- **Réglementation** : Respect des limites fixées par Alpaca pour les comptes "Pattern Day Trader" (PDT) si le compte est inférieur à 25 000 $.

## Success Criteria
- [ ] Le VPS est opérationnel avec OpenClaw installé de manière sécurisée.
- [ ] Le bot parvient à se connecter à Alpaca via un MCP (ou une intégration validée) en Paper Trading.
- [ ] Le bot est capable de prendre une décision d'Achat/Vente basée sur un signal d'actualité externe (ex: tweet ou news) et de l'exécuter sur le compte de simulation Alpaca.
