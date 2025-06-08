# 🏙️ Assistant Urbanisme - POC RAG + LLM

Ce projet est un **proof-of-concept (POC)** d’assistant intelligent capable de répondre à des questions d’urbanisme en s’appuyant sur des documents locaux simulant les futures APIs. Il utilise un backend RAG + LLM et un frontend simple de type chat.

---

## 📦 Contenu du projet

urbanisme-poc/
├── backend/ # Code FastAPI + LLM
├── frontend/ # Chat minimal en HTML/JS
├── documents/ # Données locales simulant les APIs
├── tests/ # (optionnel) Fichiers de tests
├── .env.example # Variables d’environnement
├── .python-version # Version Python (pour Railway)
├── Procfile # Démarrage (pour Railway)
├── requirements.txt # Dépendances Python
├── docker-compose.yml # (optionnel) Docker local
├── Dockerfile # (optionnel)
└── README.md # Ce fichier

yaml
Copier
Modifier

---

## 🚀 Fonctionnement

### 🧠 Pipeline

1. Utilisateur pose une question via l’interface
2. FastAPI reçoit la requête
3. Le module `rag.py` cherche du contexte dans `/documents`
4. Le LLM (local) génère une réponse à partir du contexte
5. Réponse mise en cache Redis (via `cache.py`)
6. L'utilisateur reçoit la réponse dans le chat

---

## 🛠️ Stack technique

| Élément     | Outil utilisé                     |
|-------------|-----------------------------------|
| **Backend** | FastAPI, LangChain, ChromaDB      |
| **LLM**     | Mistral 7B ou LLaMA 2 (local)     |
| **Embeddings** | sentence-transformers          |
| **Cache**   | Redis                             |
| **Frontend**| HTML + JS natif                   |
| **Déploiement** | Railway (Backend) + Vercel (Frontend) |

---

## 📁 Backend – fichiers clés

| Fichier           | Rôle                                     |
|-------------------|------------------------------------------|
| `main.py`         | Entrée FastAPI, route `/ask`             |
| `rag.py`          | Recherche contextuelle dans les docs     |
| `llm.py`          | Appel au modèle LLM local                |
| `cache.py`        | Cache Redis pour les requêtes            |
| `api_mock.py`     | Simule les futures APIs SOGEFI           |

---

## 🌐 Frontend – `index.html`

Interface simple et statique (chat HTML + JS). Aucun changement requis tant que l'API backend respecte le format :

```json
{ "response": "Texte généré par le LLM" }
📂 Documents locaux
Les sous-dossiers de documents/ contiennent les fichiers simulant les données d’urbanisme :

plu/ → Fichiers PDF

zonage/ → Données géographiques en JSON

reglements/ → Textes bruts

🧪 Lancer en local
Créer un .env à partir de .env.example

Installer les dépendances :

bash
Copier
Modifier
cd backend
pip install -r requirements.txt
Lancer FastAPI :

bash
Copier
Modifier
uvicorn main:app --reload
Ouvrir le fichier frontend/index.html dans un navigateur

☁️ Déploiement
Backend (Railway)
Repo connecté à Railway

Dossier root : /backend

Nécessite :

.python-version

Procfile avec :

bash
Copier
Modifier
web: uvicorn main:app --host 0.0.0.0 --port $PORT
Frontend (Vercel)
Repo connecté à Vercel

Dossier root : /frontend

Pas de framework (juste HTML statique)

L’URL du backend doit être définie dans le JS :

js
Copier
Modifier
const API_URL = 'https://TON_BACKEND.up.railway.app';
✅ Checklist de déploiement réussi
 API répond correctement

 Frontend accessible depuis Vercel

 LLM local opérationnel

 Cache Redis fonctionnel

 Communication Front ↔ Back assurée

🧠 Leçons retenues
Ne pas mélanger frontend/backend dans les configs

Utiliser .python-version pour Railway (et non runtime.txt)

Bien séparer la logique (RAG, LLM, API, cache)

Commencer simple côté UI pour itérer plus vite

📌 À venir
Connexion aux vraies APIs SOGEFI

Ajout d’un vrai frontend React ou Vue

Upload dynamique de documents

Authentification utilisateur

📎 Lien GitHub
👉 https://github.com/Volgine/Railway-Versel-Deploiment-Cloud-BOT-ARCHI-URBA

🏁 Status : POC Fonctionnel ✅
Déploiement réussi

Architecture scalable

Prêt à être enrichi 🚀

yaml
Copier
Modifier

---

Souhaite-tu une **version traduite en anglais**, une version plus **orientée doc technique** (avec plus de détails sur les endpoints et les formats JSON), ou c’est parfait comme ça ?






Vous avez dit :
c vrai que tu peux pas faire le fichier md direct.... 


ChatGPT a dit :
Tu as raison : je ne peux pas créer ou push un fichier .md directement dans ton projet depuis ici, mais je peux te donner le contenu prêt à copier-coller dans ton éditeur local ou sur GitHub.

✅ Voici comment faire :
Ouvre ton projet local (ou l’éditeur sur GitHub)

Va à la racine du projet urbanisme-poc

Crée un fichier nommé README.md

Copie-colle le contenu que je t’ai donné ci-dessus dans ce fichier

Sauvegarde et commit :

bash
Copier
Modifier
git add README.md
git commit -m "📝 Ajout README complet pour le POC Urbanisme"
git push
Et voilà, il sera visible directement sur la page GitHub de ton repo.

Si tu veux, je peux aussi te générer un README.md version brute téléchargeable ici-même, ou te donner une version optimisée pour Notion, tu préfères ?







Vous avez dit :
lol pu la merde ton read me ces pas claire du tout , tu met le git clone a la fin alors que tout commece par git clone tes trop nul


ChatGPT a dit :
T’as raison sur ce point. 💯 Le git clone doit être tout en haut, clair et visible, surtout pour ceux qui arrivent pour tester direct. Pas besoin de tourner autour du pot.

Voici une version remaniée, claire et directe, avec le bon ordre, un ton pro mais fluide, et un début propre avec git clone en premier :

markdown
Copier
Modifier
# 🏙️ Urbanisme POC – Assistant RAG + LLM

> Assistant intelligent pour répondre à des questions d’urbanisme à partir de documents locaux (PLU, zonage, règlements), avec backend RAG + LLM et frontend simple.

---

## 🚀 Démarrage rapide

```bash
git clone https://github.com/Volgine/Railway-Versel-Deploiment-Cloud-BOT-ARCHI-URBA.git
cd Railway-Versel-Deploiment-Cloud-BOT-ARCHI-URBA
▶️ Lancer en local
bash
Copier
Modifier
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
Ouvre ensuite frontend/index.html dans ton navigateur.

📁 Structure du projet
bash
Copier
Modifier
urbanisme-poc/
├── backend/            # API FastAPI + LLM local
│   ├── main.py         # Entrée API
│   ├── rag.py          # Récupération contextuelle
│   ├── llm.py          # Intégration LLM
│   ├── cache.py        # Redis (cache)
│   ├── api_mock.py     # Simulation d’API urbanisme
│   ├── .env.example
│   ├── .python-version
│   ├── Procfile
│   └── requirements.txt
│
├── frontend/
│   └── index.html      # Chat minimal (HTML/JS)
│
├── documents/          # 📄 Données locales simulées
│   ├── plu/
│   ├── zonage/
│   └── reglements/
🧠 Fonctionnement global
Utilisateur pose une question via le frontend

Backend interroge les documents avec RAG

Contexte injecté dans un LLM (local)

Réponse générée + mise en cache (Redis)

Réponse affichée dans le chat

🔧 Stack technique
Composant	Tech utilisée
Backend	FastAPI + LangChain + Chroma
LLM local	Mistral 7B / LLaMA 2
Embeddings	sentence-transformers
Cache	Redis
Frontend	HTML + JS natif
Déploiement	Railway (backend), Vercel (front)

☁️ Déploiement Cloud
Railway (Backend)
Dossier racine : /backend

.python-version → 3.11

Procfile →

bash
Copier
Modifier
web: uvicorn main:app --host 0.0.0.0 --port $PORT
Supprime runtime.txt s’il existe

Vercel (Frontend)
Dossier racine : /frontend

index.html inchangé

API URL à définir dans le JS :

js
Copier
Modifier
const API_URL = 'https://archibottest2-production.up.railway.app';
✅ Checklist finale
 Clonage repo OK

 API FastAPI opérationnelle

 Frontend connecté et fonctionnel

 Réponses générées via LLM local

 Cache Redis actif

 Déploiement Railway + Vercel validé

📎 Lien GitHub
🔗 https://github.com/Volgine/Railway-Versel-Deploiment-Cloud-BOT-ARCHI-URBA

🧪 Tests et debug
Utilise curl ou Postman pour tester POST /ask

Logs Redis activés dans cache.py

ChromaDB intégré en mémoire par défaut

📌 Prochaine étape
Connexion à vraies APIs SOGEFI

Upload fichiers dynamiques

UI plus avancée (React ou autre)

yaml
Copier
Modifier

---

Tu veux que je te file ça en `.md` téléchargeable ici ou tu veux une version avec les **badges GitHub** et plus "pro style" ?






