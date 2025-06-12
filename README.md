# Architecture-Bot

Architecture-Bot est un chatbot simple reposant sur l'architecture **RAG** (Retrieval‑Augmented Generation). Le projet utilise :

- **Claire‑7B** chargé localement via `llama-cpp-python` ;
- **ChromaDB** pour la base de vecteurs ;
- **Streamlit** pour l'interface Web.

## Pipeline de réponse

1. **Indexation des documents** : les fichiers sources sont découpés puis convertis en embeddings et stockés dans Chroma.
2. **Recherche sémantique** : pour chaque question, on récupère les passages pertinents à l'aide de Chroma.
3. **Génération de la réponse** : ces passages sont passés en contexte à Claire‑7B pour produire la réponse.
4. **Interface utilisateur** : Streamlit permet de dialoguer avec le modèle via le navigateur.

## Installation et exécution

```bash
git clone https://github.com/URA-BOT1/Architecture-Bot.git
cd Architecture-Bot
pip install -r requirements.txt
./run.sh
```

Placez le fichier du modèle `Claire-7B-0.1.Q4_0.gguf` dans le dossier `models/` avant de lancer l'application.

## Indexation de nouveaux documents

Pour indexer un dossier de documents supplémentaires :

```bash
python src/ingestion/index_documents.py <chemin_du_dossier>
```

L'application Streamlit est ensuite accessible sur [http://localhost:8501](http://localhost:8501).

