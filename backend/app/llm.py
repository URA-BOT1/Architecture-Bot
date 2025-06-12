import os
import logging
from typing import Optional, List, Dict
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    pipeline,
    BitsAndBytesConfig
)
import torch
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.schema import Document

logger = logging.getLogger(__name__)

class LocalLLM:
    """
    Gestionnaire pour LLM local (Claire-7B ou Llama)
    """

    def __init__(self, model_name: str = "OpenLLM-France/Claire-7B-0.1"):
        """
        Initialise le LLM local
        
        Args:
            model_name: Nom du modèle HuggingFace à utiliser
                       Options:
                       - "OpenLLM-France/Claire-7B-0.1" (recommandé)
                       - "meta-llama/Llama-2-7b-chat-hf" (nécessite token HF)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🖥️ Utilisation du device: {self.device}")
        
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.llm = None
        
        # Templates de prompts pour l'urbanisme
        self.prompt_templates = {
            "general": """Tu es un assistant expert en urbanisme et réglementation PLU en France.
            
Contexte trouvé dans les documents:
{context}

Question de l'utilisateur: {question}

Réponds de manière précise et professionnelle en citant les articles pertinents du règlement.
Si l'information n'est pas dans le contexte, dis-le clairement.

Réponse:""",
            
            "zonage": """Tu es un expert en zonage urbain (PLU).

Zone concernée: {zone}
Règlement applicable:
{context}

Question: {question}

Fournis une réponse claire sur les règles de cette zone.

Réponse:""",
            
            "hauteur": """Tu es un expert en règles d'urbanisme.

Contexte réglementaire:
{context}

Question sur les hauteurs: {question}

Indique précisément les hauteurs maximales autorisées et les conditions.

Réponse:"""
        }
    
    def load_model(self):
        """Charge le modèle en mémoire"""
        try:
            logger.info(f"📥 Chargement du modèle {self.model_name}...")
            
            # Configuration pour économiser la mémoire (quantization 4-bit)
            bnb_config = None
            if self.device == "cuda":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            hf_token = os.getenv("HF_TOKEN")

            # Charger le tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                token=hf_token
            )
            
            # Ajouter un pad token si nécessaire
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Charger le modèle
            if bnb_config:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=bnb_config,
                    device_map="auto",
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    token=hf_token
                )
            else:
                # CPU mode
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                    token=hf_token
                )
            
            # Créer le pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                temperature=0.3,
                top_p=0.95,
                repetition_penalty=1.15
            )
            
            # Wrapper LangChain
            self.llm = HuggingFacePipeline(pipeline=self.pipeline)
            
            logger.info("✅ Modèle chargé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            raise
    
    def generate_response(self, 
                         question: str, 
                         context: str = "", 
                         template_type: str = "general") -> str:
        """
        Génère une réponse à partir du contexte et de la question
        
        Args:
            question: Question de l'utilisateur
            context: Contexte trouvé par le RAG
            template_type: Type de template à utiliser
            
        Returns:
            Réponse générée
        """
        if not self.llm:
            raise ValueError("Modèle non chargé. Appelez load_model() d'abord.")
        
        # Sélectionner le template
        template = self.prompt_templates.get(template_type, self.prompt_templates["general"])
        
        # Créer le prompt
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Limiter la taille du contexte pour éviter de dépasser la limite de tokens
        max_context_length = 2000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        # Générer la réponse
        try:
            formatted_prompt = prompt.format(context=context, question=question)
            response = self.llm(formatted_prompt)
            
            # Nettoyer la réponse
            response = response.strip()
            
            # Log pour debug
            logger.info(f"📝 Question: {question[:50]}...")
            logger.info(f"📄 Contexte: {len(context)} caractères")
            logger.info(f"💬 Réponse: {response[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur génération: {e}")
            return "Désolé, je n'ai pas pu générer une réponse. Veuillez réessayer."
    
    def analyze_question_type(self, question: str) -> str:
        """
        Analyse le type de question pour choisir le bon template
        
        Args:
            question: Question de l'utilisateur
            
        Returns:
            Type de template à utiliser
        """
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["hauteur", "haut", "étage", "faîtage"]):
            return "hauteur"
        elif any(word in question_lower for word in ["zone", "zonage", "secteur"]):
            return "zonage"
        else:
            return "general"
    
    def format_response_with_sources(self, response: str, sources: List[Document]) -> Dict:
        """
        Formate la réponse avec les sources
        
        Args:
            response: Réponse générée
            sources: Documents sources utilisés
            
        Returns:
            Dictionnaire avec réponse et sources formatées
        """
        formatted_sources = []
        for doc in sources[:3]:  # Limiter à 3 sources
            formatted_sources.append({
                "type": doc.metadata.get("type", "document"),
                "zone": doc.metadata.get("zone", ""),
                "extrait": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        return {
            "answer": response,
            "sources": formatted_sources,
            "model": self.model_name
        }

# Instance globale
llm_manager = None

def init_llm(model_name: Optional[str] = None) -> LocalLLM:
    """
    Initialise le gestionnaire LLM
    
    Args:
        model_name: Nom du modèle (optionnel)
        
    Returns:
        Instance du gestionnaire LLM
    """
    global llm_manager
    
    # Utiliser variable d'environnement si disponible
    if not model_name:
        model_name = os.getenv("LLM_MODEL", "OpenLLM-France/Claire-7B-0.1")
    
    llm_manager = LocalLLM(model_name)
    return llm_manager
