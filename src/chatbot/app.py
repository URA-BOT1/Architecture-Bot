import streamlit as st
from llama_cpp import Llama

from src.embeddings.embedder import Embedder
from src.vectorstore.chroma_manager import ChromaManager
from src.generation.prompts import PROMPT_DEVIS
from src.config.config import MODEL_PATH, CONTEXT_LENGTH
from src.ingestion import load_file

embedder = Embedder()
vectorstore = ChromaManager()
llm = Llama(model_path=MODEL_PATH, n_ctx=CONTEXT_LENGTH)

st.title("Chatbot Architecture")
question = st.text_input("Votre demande :")

if st.button("Envoyer") and question:
    q_vec = embedder.encode([question])[0]
    results = vectorstore.search(q_vec, k=5)

    # Only build context if search returned documents
    docs = results.get("documents") if results else None
    if docs and len(docs) > 0 and docs[0]:
        context = "\n".join(docs[0])
        prompt = PROMPT_DEVIS.format(context=context, question=question)
        answer = llm(prompt, max_tokens=256, temperature=0.2)
        st.write("**Réponse du bot :**", answer["choices"][0]["text"])
    else:
        st.write("Aucun résultat trouvé")
