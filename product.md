# Product Definition

## Why this project exists
L'investissement manuel ne permet plus de traiter le volume immense de données sociales et d'actualités en temps réel. Historiquement, l'automatisation par l'IA était réservée aux marchés cryptos (Polymarket). Ce projet existe pour amener "l'alpha agentique" (automatisation intelligente) aux marchés boursiers régulés.

## Problems it solves
- Le manque de temps pour surveiller les marchés 24/7.
- La latence humaine face à des informations financières (tweets, news break).
- Le biais émotionnel lors du trading.

## How it should work
Un agent IA tourne en boucle sur un VPS. Il reçoit des données de marché via l'API Alpaca, scanne le web pour analyser le sentiment sur des actifs cibles, et, lorsqu'une asymétrie d'information ou une opportunité se présente, il exécute des ordres d'achat/vente via le compte "Paper Trading" (puis Live) du courtier.

## User experience goals
L'utilisateur final doit pouvoir monitorer l'activité de son agent via des logs ou des notifications (ex: Telegram/Email), vérifier que les décisions sont logiques et basées sur l'actualité, et dormir sur ses deux oreilles grâce à de strictes limites de risques (clés Trade-Only, pas de crypto).
