import os
import logging
from typing import Optional, List, Dict

from llama_cpp import Llama
from langchain.prompts import PromptTemplate
from langchain.schema import Document

logger = logging.getLogger(__name__)


class LocalLLM:
    """Simple wrapper around a local GGUF model loaded with llama-cpp."""

    def __init__(self, model_path: str = "models/Claire-7B-0.1.Q4_0.gguf", context_length: int = 2048):
        self.model_path = model_path
        self.context_length = context_length
        self.model: Optional[Llama] = None

        self.prompt_templates = {
            "general": (
                "Tu es un assistant expert en urbanisme.\n"
                "Contexte:\n{context}\n\n"
                "Question: {question}\n\n"
                "Réponse:"
            ),
            "zonage": (
                "Tu es un expert en zonage urbain (PLU).\n"
                "Zone concernée: {zone}\n"
                "Règlement applicable:\n{context}\n\n"
                "Question: {question}\n\n"
                "Réponse:"
            ),
            "hauteur": (
                "Tu es un expert en règles d'urbanisme.\n"
                "Contexte réglementaire:\n{context}\n\n"
                "Question sur les hauteurs: {question}\n\n"
                "Réponse:"
            ),
        }

    def load_model(self) -> None:
        """Load the GGUF model from disk."""
        logger.info(f"Loading model from {self.model_path}")
        self.model = Llama(model_path=self.model_path, n_ctx=self.context_length)

    def generate_response(self, question: str, context: str = "", template_type: str = "general") -> str:
        if not self.model:
            raise ValueError("Model not loaded. Call load_model() first.")
        template = self.prompt_templates.get(template_type, self.prompt_templates["general"])
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        full_prompt = prompt.format(context=context, question=question)
        result = self.model(full_prompt, max_tokens=256, temperature=0.2)
        answer = result["choices"][0]["text"].strip()
        logger.info(f"Q: {question[:50]}... → {answer[:80]}")
        return answer

    @staticmethod
    def analyze_question_type(question: str) -> str:
        q = question.lower()
        if any(w in q for w in ["hauteur", "haut", "étage", "faîtage"]):
            return "hauteur"
        if any(w in q for w in ["zone", "zonage", "secteur"]):
            return "zonage"
        return "general"

    def format_response_with_sources(self, response: str, sources: List[Document]) -> Dict:
        formatted = []
        for doc in sources[:3]:
            formatted.append({
                "type": doc.metadata.get("type", "document"),
                "zone": doc.metadata.get("zone", ""),
                "extrait": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            })
        return {"answer": response, "sources": formatted, "model": self.model_path}


llm_manager: Optional[LocalLLM] = None


def init_llm(model_path: Optional[str] = None, context_length: int = 2048) -> LocalLLM:
    """Initialise and return the global LLM manager."""
    global llm_manager
    if not model_path:
        model_path = os.getenv("MODEL_PATH", "models/Claire-7B-0.1.Q4_0.gguf")
    llm_manager = LocalLLM(model_path, context_length)
    return llm_manager

