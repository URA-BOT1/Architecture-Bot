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
Si vous modifiez le `Dockerfile`, relancez la commande avec `--build` pour
reconstruire l'image du backend.

Le backend sera disponible sur `http://localhost:8000` et le frontend sur `http://localhost:3000`.

## Déploiement sur Railway

1. Créez un compte sur [Railway](https://railway.app) et connectez votre compte GitHub.
2. Depuis le tableau de bord Railway, cliquez sur **New Project** puis **Deploy from GitHub repo** et sélectionnez ce dépôt.
3. Dans les options d'import, indiquez `backend` comme **Root Directory** pour que Railway utilise le `Dockerfile`.
4. Railway détecte alors le `Dockerfile` et construit l'image automatiquement.
5. Ajoutez si besoin les variables d'environnement (ex. `REDIS_HOST`, `REDIS_PORT`).
   La variable `PORT` vaut `8000` par défaut mais Railway la remplacera automatiquement.
6. Lancez le déploiement : Railway exécutera `uvicorn app.main:app --host 0.0.0.0 --port $PORT` comme défini dans le `Dockerfile`.

Une URL publique est alors fournie pour accéder à l'API.

## Déploiement du frontend sur Vercel

Le dossier `frontend/` est un site statique. Sur [Vercel](https://vercel.com) :

1. Importez ce dépôt GitHub comme nouveau projet.
2. Lors de l'import, définissez `frontend` comme **Root Directory**.
3. Gardez ensuite les autres paramètres par défaut : Vercel détectera `vercel.json` et servira directement `index.html` et `app.js`.

## Tests

Pour exécuter le script de charge localement :

```bash
pip install -r requirements.txt
pytest -q
```

Cela lancera `tests/test_load.py` pour simuler des requêtes sur l'API.
