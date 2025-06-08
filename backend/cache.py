import redis
import json
import hashlib
import logging
from typing import Optional, Any
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestionnaire de cache Redis pour l'assistant urbanisme"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, 
                 password: Optional[str] = None, db: int = 0):
        """
        Initialise la connexion Redis
        
        Args:
            host: Hôte Redis
            port: Port Redis
            password: Mot de passe Redis (optionnel)
            db: Numéro de base de données Redis
        """
        self.enabled = True
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                password=password,
                db=db,
                decode_responses=True
            )
            # Test de connexion
            self.redis_client.ping()
            logger.info("✅ Redis connecté - Cache activé")
        except Exception as e:
            logger.warning(f"⚠️ Redis non disponible - Mode sans cache: {e}")
            self.enabled = False
            self.redis_client = None
    
    def generate_key(self, query: str, context: Optional[str] = None) -> str:
        """
        Génère une clé unique pour le cache
        
        Args:
            query: Question de l'utilisateur
            context: Contexte additionnel (commune, parcelle, etc.)
        
        Returns:
            Clé de cache unique
        """
        content = f"{query}:{context}" if context else query
        return f"urbanisme:{hashlib.md5(content.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[dict]:
        """
        Récupère une valeur du cache
        
        Args:
            key: Clé de cache
            
        Returns:
            Données du cache ou None
        """
        if not self.enabled:
            return None
            
        try:
            data = self.redis_client.get(key)
            if data:
                logger.info(f"📦 Cache hit: {key[:20]}...")
                return json.loads(data)
        except Exception as e:
            logger.error(f"Erreur lecture cache: {e}")
        
        return None
    
    def set(self, key: str, value: dict, ttl: int = 86400) -> bool:
        """
        Stocke une valeur dans le cache
        
        Args:
            key: Clé de cache
            value: Données à stocker
            ttl: Durée de vie en secondes (défaut: 24h)
            
        Returns:
            True si succès, False sinon
        """
        if not self.enabled:
            return False
            
        try:
            self.redis_client.setex(
                key, 
                timedelta(seconds=ttl), 
                json.dumps(value, ensure_ascii=False)
            )
            logger.info(f"💾 Cache set: {key[:20]}... (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Erreur écriture cache: {e}")
            return False
    
    def delete(self, pattern: str = "*") -> int:
        """
        Supprime des clés du cache selon un pattern
        
        Args:
            pattern: Pattern de recherche (défaut: tout)
            
        Returns:
            Nombre de clés supprimées
        """
        if not self.enabled:
            return 0
            
        try:
            keys = self.redis_client.keys(f"urbanisme:{pattern}")
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"🗑️ Cache vidé: {deleted} entrées")
                return deleted
        except Exception as e:
            logger.error(f"Erreur suppression cache: {e}")
        
        return 0
    
    def increment_stat(self, stat_name: str) -> int:
        """
        Incrémente une statistique
        
        Args:
            stat_name: Nom de la statistique
            
        Returns:
            Nouvelle valeur
        """
        if not self.enabled:
            return 0
            
        try:
            key = f"stats:{stat_name}"
            return self.redis_client.incr(key)
        except Exception as e:
            logger.error(f"Erreur increment stat: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """
        Récupère toutes les statistiques
        
        Returns:
            Dictionnaire des statistiques
        """
        stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "api_calls": 0,
            "rag_searches": 0,
            "llm_calls": 0
        }
        
        if not self.enabled:
            return stats
            
        try:
            for stat in stats.keys():
                value = self.redis_client.get(f"stats:{stat}")
                stats[stat] = int(value) if value else 0
        except Exception as e:
            logger.error(f"Erreur lecture stats: {e}")
            
        return stats
    
    def health_check(self) -> dict:
        """
        Vérifie l'état du cache
        
        Returns:
            État du cache
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Redis non configuré"}
            
        try:
            self.redis_client.ping()
            info = self.redis_client.info()
            return {
                "status": "healthy",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "N/A"),
                "total_keys": self.redis_client.dbsize()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Instance globale (optionnel, peut être créé dans main.py)
cache_manager = None

def init_cache(host: str = "localhost", port: int = 6379, 
               password: Optional[str] = None) -> CacheManager:
    """
    Initialise le gestionnaire de cache global
    
    Returns:
        Instance du gestionnaire de cache
    """
    global cache_manager
    cache_manager = CacheManager(host, port, password)
    return cache_manager