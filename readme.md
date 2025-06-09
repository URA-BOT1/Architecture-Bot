# 🏙️ Urbanisme POC – Assistant RAG + LLM

> Assistant intelligent pour répondre à des questions d’urbanisme à partir de documents locaux (PLU, zonage, règlements), avec backend RAG + LLM et frontend simple.

---

## 🚀 Démarrage rapide

```bash
git clone https://github.com/Volgine/urbanisme-bot.git
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
🔗 https://github.com/Volgine/urbanisme-bot

🧪 Tests et debug
Utilise curl ou Postman pour tester POST /ask

Logs Redis activés dans cache.py

ChromaDB intégré en mémoire par défaut

📌 Prochaine étape
Connexion à vraies APIs SOGEFI

Upload fichiers dynamiques

UI plus avancée (React ou autre)
