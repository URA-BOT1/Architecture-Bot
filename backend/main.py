import sys
import os

# Configuration du path AVANT tous les autres imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
import time
from typing import Optional, List, Dict
import asyncio

# Import des modules custom
from cache import init_cache, CacheManager
from api_mock import init_mock_api, MockUrbanismAPI
from llm import init_llm, LocalLLM
from rag import init_rag, RAGSystem

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'app
app = FastAPI(title="Assistant Urbanisme API", version="1.0.0")

# CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instances globales
cache: Optional[CacheManager] = None
mock_api: Optional[MockUrbanismAPI] = None
llm_manager: Optional[LocalLLM] = None
rag_system: Optional[RAGSystem] = None

# État de l'initialisation
initialization_status = {
    "cache": False,
    "mock_api": False,
    "llm": False,
    "rag": False,
    "documents_indexed": False
}

# Modèles Pydantic
class QueryRequest(BaseModel):
    question: str
    commune: Optional[str] = None
    parcelle: Optional[str] = None
    use_cache: bool = True

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict] = []
    cached: bool = False
    processing_time: float
    model_used: Optional[str] = None

class StatsResponse(BaseModel):
    total_queries: int
    cache_hits: int
    api_calls: int
    rag_searches: int
    llm_calls: int
    cache_enabled: bool

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, bool]
    cache_status: Optional[Dict] = None

# Fonctions d'initialisation
async def initialize_services():
    """Initialise tous les services au démarrage"""
    global cache, mock_api, llm_manager, rag_system
    
    logger.info("🚀 Initialisation des services...")
    
    # Cache Redis
    try:
        cache = init_cache(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD')
        )
        initialization_status["cache"] = True
    except Exception as e:
        logger.error(f"Erreur init cache: {e}")
    
    # Mock API
    try:
        mock_api = init_mock_api()
        initialization_status["mock_api"] = True
    except Exception as e:
        logger.error(f"Erreur init mock API: {e}")
    
    # LLM
    try:
        llm_manager = init_llm()
        # Note: Le chargement du modèle est différé pour ne pas bloquer le démarrage
        initialization_status["llm"] = True
    except Exception as e:
        logger.error(f"Erreur init LLM: {e}")
    
    # RAG System
    try:
        rag_system = init_rag()
        initialization_status["rag"] = True
    except Exception as e:
        logger.error(f"Erreur init RAG: {e}")
    
    logger.info("✅ Services initialisés")

async def load_llm_model():
    """Charge le modèle LLM en arrière-plan"""
    if llm_manager and not llm_manager.model:
        logger.info("📥 Chargement du modèle LLM en arrière-plan...")
        try:
            llm_manager.load_model()
            logger.info("✅ Modèle LLM chargé")
        except Exception as e:
            logger.error(f"❌ Erreur chargement LLM: {e}")

async def index_documents():
    """Indexe les documents en arrière-plan"""
    if rag_system:
        logger.info("📚 Indexation des documents...")
        try:
            rag_system.index_documents()
            initialization_status["documents_indexed"] = True
            logger.info("✅ Documents indexés")
        except Exception as e:
            logger.error(f"❌ Erreur indexation: {e}")

# Events de démarrage
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'app"""
    await initialize_services()
    
    # Lancer les tâches lourdes en arrière-plan
    asyncio.create_task(load_llm_model())
    asyncio.create_task(index_documents())

# Routes
@app.get("/")
async def read_root():
    return {
        "message": "Assistant Urbanisme API - Avec RAG & LLM ! 🏗️🤖",
        "version": "1.0.0",
        "docs": "/docs",
        "services": initialization_status
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérifie l'état de tous les services"""
    cache_status = None
    if cache and cache.enabled:
        cache_status = cache.health_check()
    
    return HealthResponse(
        status="healthy" if all(initialization_status.values()) else "degraded",
        services=initialization_status,
        cache_status=cache_status
    )

@app.post("/api/query", response_model=QueryResponse)
async def query_urbanisme(request: QueryRequest):
    """
    Endpoint principal pour les questions d'urbanisme
    Utilise RAG + LLM pour générer des réponses
    """
    start_time = time.time()
    
    # Incrémenter le compteur total
    if cache:
        cache.increment_stat("total_queries")
    
    # Vérifier le cache si activé
    cache_key = None
    if request.use_cache and cache and cache.enabled:
        cache_key = cache.generate_key(f"{request.commune}:{request.question}")
        cached_result = cache.get(cache_key)
        if cached_result:
            if cache:
                cache.increment_stat("cache_hits")
            cached_result['cached'] = True
            cached_result['processing_time'] = time.time() - start_time
            return QueryResponse(**cached_result)
    
    # Vérifier que les services sont prêts
    if not all([initialization_status["rag"], initialization_status["llm"]]):
        # Mode dégradé : utiliser les réponses mockées
        logger.warning("⚠️ Services non prêts, utilisation du mode dégradé")
        
        # Utiliser l'ancienne logique de réponse mockée
        answer = await generate_fallback_response(request.question, request.commune)
        response_data = {
            "answer": answer,
            "sources": [],
            "cached": False,
            "processing_time": time.time() - start_time,
            "model_used": "fallback"
        }
        
        return QueryResponse(**response_data)
    
    # Vérifier que le modèle LLM est chargé
    if not llm_manager.model:
        raise HTTPException(
            status_code=503,
            detail="Le modèle LLM est en cours de chargement. Veuillez réessayer dans quelques instants."
        )
    
    try:
        # Incrémenter les stats
        if cache:
            cache.increment_stat("rag_searches")
            cache.increment_stat("llm_calls")
        
        # 1. Récupérer le contexte avec le RAG
        context, sources = rag_system.get_context_for_question(
            request.question, 
            request.commune
        )
        
        # 2. Si on a une parcelle, enrichir avec les données de zonage
        if request.parcelle and request.commune and mock_api:
            zonage_data = await mock_api.get_zonage_parcelle(
                request.commune, 
                request.parcelle
            )
            if zonage_data:
                zone = zonage_data.get("zone")
                if zone:
                    # Récupérer le règlement de la zone
                    reglement = await mock_api.get_reglement_zone(
                        request.commune, 
                        zone
                    )
                    if reglement:
                        context = f"Zone {zone}:\n{reglement}\n\n{context}"
        
        # 3. Analyser le type de question
        template_type = llm_manager.analyze_question_type(request.question)
        
        # 4. Générer la réponse avec le LLM
        answer = llm_manager.generate_response(
            question=request.question,
            context=context,
            template_type=template_type
        )
        
        # 5. Formater la réponse avec les sources
        response_data = llm_manager.format_response_with_sources(answer, sources)
        response_data["cached"] = False
        response_data["processing_time"] = time.time() - start_time
        
        # 6. Mettre en cache si activé
        if cache_key and cache and cache.enabled:
            cache.set(cache_key, response_data)
        
        return QueryResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Récupère les statistiques d'utilisation"""
    if cache and cache.enabled:
        stats = cache.get_stats()
    else:
        stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "api_calls": 0,
            "rag_searches": 0,
            "llm_calls": 0
        }
    
    stats["cache_enabled"] = cache.enabled if cache else False
    return StatsResponse(**stats)

@app.delete("/api/cache")
async def clear_cache():
    """Vide le cache (admin only)"""
    if cache and cache.enabled:
        deleted = cache.delete()
        return {"message": f"Cache vidé: {deleted} entrées supprimées"}
    else:
        return {"message": "Cache non activé"}

@app.post("/api/index/refresh")
async def refresh_index(background_tasks: BackgroundTasks):
    """Force la réindexation des documents"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system non initialisé")
    
    background_tasks.add_task(rag_system.index_documents, force_reindex=True)
    return {"message": "Réindexation lancée en arrière-plan"}

# Fonction de fallback
async def generate_fallback_response(question: str, commune: Optional[str] = None) -> str:
    """
    Génère une réponse de base quand le LLM n'est pas disponible
    Reprend la logique du POC initial
    """
    q_lower = question.lower()
    
    if "hauteur" in q_lower:
        return "La hauteur maximale autorisée varie selon le zonage. En général : Zone UA (centre-ville) : 15-18m, Zone UB (urbain mixte) : 12m, Zone UC (pavillonnaire) : 9m. Consultez le PLU de votre commune pour les règles précises."
    elif "zone" in q_lower:
        return "Le zonage dépend du PLU de chaque commune. Les principales zones sont : UA (centre urbain), UB (urbain mixte), UC (pavillonnaire), AU (à urbaniser), A (agricole), N (naturelle)."
    elif "emprise" in q_lower:
        return "L'emprise au sol maximale varie selon les zones : 60-80% en zone urbaine dense, 40-60% en zone mixte, 30-40% en zone pavillonnaire."
    else:
        return "Je peux vous aider avec les questions sur le zonage, les hauteurs maximales, l'emprise au sol, les distances aux limites, et les règles de stationnement. Précisez votre question pour une réponse plus détaillée."

# Pour tester localement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
