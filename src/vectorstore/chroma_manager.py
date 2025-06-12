import chromadb
from chromadb.config import Settings

class ChromaManager:
    def __init__(self, persist_dir: str = "chroma_db"):
        self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_dir))
        self.collection = self.client.get_or_create_collection("architecture_docs")

    def add(self, ids, texts, embeddings, metadatas):
        self.collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
        self.client.persist()

    def search(self, query_vec, k=5):
        return self.collection.query(query_embeddings=[query_vec], n_results=k)
