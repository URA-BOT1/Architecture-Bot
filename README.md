# Assistant Urbanisme

Ce projet propose un exemple simple d'assistant d'urbanisme basé sur un RAG (Retrieval Augmented Generation) et un LLM local.
Il comporte deux parties :

* **backend/** – API FastAPI servant les réponses
* **frontend/** – mini application HTML/JS interrogeant l'API
* **tests/** – petit script de charge

## Lancer en local

```bash
# Nécessite Docker
 docker-compose up --build
```

Le backend sera disponible sur `http://localhost:8000` et le frontend sur `http://localhost:3000`.

## Déploiement sur Railway

1. Créez un compte sur [Railway](https://railway.app) et connectez votre compte GitHub.
2. Depuis le tableau de bord Railway, cliquez sur **New Project** puis **Deploy from GitHub repo** et sélectionnez ce dépôt.
3. Railway détecte le `Dockerfile` dans `backend/` et construit l'image automatiquement.
4. Ajoutez si besoin les variables d'environnement (ex. `REDIS_HOST`, `REDIS_PORT`).
5. Lancez le déploiement : Railway exécutera `uvicorn app.main:app --host 0.0.0.0 --port $PORT` comme défini dans le `Dockerfile`.

Une URL publique est alors fournie pour accéder à l'API.

## Déploiement du frontend sur Vercel

Le dossier `frontend/` est un site statique. Sur [Vercel](https://vercel.com) :

1. Importez ce dépôt GitHub comme nouveau projet.
2. Gardez les paramètres par défaut, Vercel détectera `vercel.json` et servira directement `index.html` et `app.js`.

## Tests

Un script de charge est disponible :

```bash
pytest -q
```

Cela lancera `tests/test_load.py` pour simuler des requêtes sur l'API (les dépendances doivent être installées).
