from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name: str = "dangvantuan/sentence-camembert-large"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return self.model.encode(texts, show_progress_bar=False)
