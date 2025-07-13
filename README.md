# Self-Building Crypto Scanner

Ce projet automatise la découverte, l’ingestion, l’analyse et l’évolution autonome de modules d’analyse crypto sur BigQuery.

## Fonctionnalités principales
- Découverte automatique des datasets crypto publics sur BigQuery
- Génération de workers Python pour chaque dataset
- Boucle de test/correction automatique
- Documentation et logs générés automatiquement
- Notification Telegram des succès/échecs

## Structure
- `main.py` : runner principal
- `modules_proposes/` : workers générés automatiquement
- `logs/` : logs d’exécution et d’erreur
- `.env` : variables sensibles (API keys, tokens...)

## Lancement
```bash
pip install -r requirements.txt
python main.py
```

## Exemples de prompts pour l’auto-correction
Voir le fichier `prompts_examples.md`.
