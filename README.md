# Architecture-Bot

Architecture-Bot est un chatbot basé sur l’architecture RAG (Retrieval-Augmented Generation) permettant de répondre à des questions en s’appuyant sur une base de connaissance spécifique. Le projet utilise un pipeline combinant : (1) **Claire-7B**, un modèle de langage de 7 milliards de paramètres adapté aux dialogues en français:contentReference[oaicite:17]{index=17}, (2) **ChromaDB**, une base de données vectorielle open-source pour stocker et rechercher les embeddings des documents:contentReference[oaicite:18]{index=18}, et (3) **Streamlit**, un framework Python open-source pour créer rapidement des interfaces web interactives:contentReference[oaicite:19]{index=19}.

## Pipeline de réponse (RAG)

1. **Indexation des documents** : les documents de référence sont transformés en vecteurs (embeddings) et stockés dans ChromaDB.
2. **Recherche sémantique** : pour chaque question posée, on calcule son embedding et on interroge ChromaDB afin d’identifier les passages pertinents.
3. **Génération de réponse** : les passages récupérés sont concaténés et passés en contexte à Claire-7B. Le modèle génère alors une réponse textuelle informée.
4. **Interface utilisateur** : l’application Streamlit fournit une interface web où l’utilisateur pose ses questions et reçoit les réponses générées.

Ce pipeline RAG associe la capacité de récupération de données (ChromaDB) aux performances d’un LLM (Claire-7B) pour fournir des réponses contextuelles. Streamlit est utilisé pour rendre le tout accessible via un navigateur sans nécessiter de front-end complexe.

## Installation et exécution

Pour lancer Architecture-Bot localement :

- Cloner le dépôt :  
  ```bash
  git clone https://github.com/URA-BOT1/Architecture-Bot.git
  cd Architecture-Bot
