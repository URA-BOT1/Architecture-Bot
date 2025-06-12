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
Pour déployer le frontend ailleurs, copiez `frontend/config.js.example` en `frontend/config.js` et indiquez l'URL publique de l'API.

### Développement sans Docker

Pour lancer le backend directement, installez les dépendances Python :

```bash
pip install -r backend/requirements.txt
```

### Notes

* Le port par défaut de Redis est `6379`. Si vous rencontrez un souci de connexion,
  vérifiez la variable `REDIS_PORT` dans votre fichier `.env`. Vous pouvez
  également définir une URL complète via `REDIS_URL` (par ex.
  `redis://user:pass@host:port/0`).
* Le système RAG repose sur la librairie `sentence-transformers`.
  Assurez-vous que cette dépendance est bien installée.
* Certains modèles de LLM (comme Llama 2 ou Mistral) nécessitent un token
  Hugging Face pour être téléchargés. Renseignez la variable `HF_TOKEN` (lue
  automatiquement par l'application) ou connectez-vous via
  `huggingface-cli login`.

Redis doit être démarré (par exemple via `docker-compose` ou un serveur local).
Les variables `REDIS_HOST`/`REDIS_PORT` ou `REDIS_URL` peuvent être ajustées
dans un fichier `.env` copié depuis `backend/.env.example`.

## Déploiement sur Railway

1. Créez un compte sur [Railway](https://railway.app) et connectez votre compte GitHub.
2. Depuis le tableau de bord Railway, cliquez sur **New Project** puis **Deploy from GitHub repo** et sélectionnez ce dépôt.
3. Dans les options d'import, indiquez **obligatoirement** `backend` comme **Root Directory** pour que Railway installe les dépendances du backend et utilise le `Dockerfile`. Sans ce paramètre, le déploiement échouera car Railway ne prendra que `requirements.txt` à la racine.
4. Railway détecte alors le `Dockerfile` et construit l'image automatiquement.
5. Ajoutez si besoin les variables d'environnement (ex. `REDIS_HOST`, `REDIS_PORT` ou `REDIS_URL`).
   La variable `PORT` vaut `8000` par défaut mais Railway la remplacera automatiquement.
6. Lancez le déploiement : Railway exécutera `uvicorn app.main:app --host 0.0.0.0 --port $PORT` comme défini dans le `Dockerfile`.

Une URL publique est alors fournie pour accéder à l'API.

## Déploiement du frontend sur Vercel

Le dossier `frontend/` est un site statique. Sur [Vercel](https://vercel.com) :

1. Importez ce dépôt GitHub comme nouveau projet.
2. Lors de l'import, définissez `frontend` comme **Root Directory**.
3. Copiez `frontend/config.js.example` en `frontend/config.js` et indiquez l'URL publique de votre backend.
4. Gardez ensuite les autres paramètres par défaut : Vercel détectera `vercel.json` et servira directement `index.html`, `config.js` et `app.js`.

## Tests

Pour exécuter le script de charge localement :

```bash
pip install -r requirements.txt
pytest -q
```

Le fichier `requirements.txt` fournit notamment `pytest` et
`pytest-asyncio`, nécessaires pour exécuter les tests asynchrones.

Cela lancera `tests/test_load.py` pour simuler des requêtes sur l'API.

## Git Flow

Un script `gitflow-setup.sh` est fourni pour initialiser rapidement la structure Git Flow.
Après installation de l'outil `git-flow`, lancez :

```bash
chmod +x gitflow-setup.sh
./gitflow-setup.sh
```

Des exemples détaillés d'utilisation se trouvent dans `gitflow-commands-examples.sh`.
Ce petit script liste les commandes Git Flow courantes (init, features, releases,
hotfixes) et montre comment afficher les branches actives.

## Pipeline RAG open-source pour l'architecture

Ce dépôt inclut maintenant une implémentation complète d'un pipeline RAG 100% open-source adapté au français. Les modules situés dans `src/` permettent :

- l'ingestion de documents PDF, DOCX ou Excel via `src/ingestion/` ;
- la génération d'embeddings CamemBERT dans `src/embeddings/` ;
- l'indexation et la recherche locale avec ChromaDB (`src/vectorstore/`) ;
- les prompts de génération dans `src/generation/` ;
- une interface chatbot Streamlit (`src/chatbot/app.py`) exploitant le modèle quantifié 4-bit **Claire-7B** via `llama_cpp`.

Pour installer les dépendances système et Python :

```bash
bash install.sh
```
Ce script installe également les paquets système `tesseract-ocr` et
`poppler-utils` nécessaires à l'OCR utilisé par `pdf2image` et
`pytesseract`.

Avant de démarrer le chatbot, vos documents doivent impérativement être
indexés avec le script dédié. Cette étape crée la base ChromaDB utilisée
par le RAG.

Pour indexer vos documents :

```bash
python src/ingestion/index_documents.py data/
bash run.sh
```

L'interface Streamlit sera alors accessible localement une fois le
script `run.sh` lancé.
