import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MockUrbanismAPI:
    """
    Simule les APIs SOGEFI/GPU en lisant des documents locaux
    À remplacer par les vraies APIs plus tard
    """
    
    def __init__(self, documents_path: str = "documents"):
        """
        Initialise le mock API avec le chemin des documents
        
        Args:
            documents_path: Chemin vers le dossier documents
        """
        self.base_path = Path(documents_path)
        self.ensure_directories()
        self.load_mock_data()
    
    def ensure_directories(self):
        """Crée les dossiers nécessaires s'ils n'existent pas"""
        directories = ["plu", "zonage", "reglements"]
        for dir_name in directories:
            dir_path = self.base_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Créer des fichiers d'exemple si vides
            if not any(dir_path.iterdir()):
                self._create_sample_files(dir_path, dir_name)
    
    def _create_sample_files(self, dir_path: Path, dir_type: str):
        """Crée des fichiers d'exemple pour les tests"""
        if dir_type == "zonage":
            # Exemple de données de zonage
            sample_zonage = {
                "montpellier": {
                    "zones": {
                        "UA": {
                            "nom": "Zone urbaine centre-ville",
                            "hauteur_max": 18,
                            "emprise_sol_max": 0.8,
                            "description": "Zone urbaine dense du centre historique"
                        },
                        "UB": {
                            "nom": "Zone urbaine mixte",
                            "hauteur_max": 12,
                            "emprise_sol_max": 0.6,
                            "description": "Zone urbaine à dominante résidentielle"
                        },
                        "UC": {
                            "nom": "Zone pavillonnaire",
                            "hauteur_max": 9,
                            "emprise_sol_max": 0.4,
                            "description": "Zone résidentielle de faible densité"
                        }
                    }
                }
            }
            with open(dir_path / "montpellier.json", "w", encoding="utf-8") as f:
                json.dump(sample_zonage, f, ensure_ascii=False, indent=2)
        
        elif dir_type == "reglements":
            # Exemple de règlement
            sample_reglement = """
RÈGLEMENT ZONE UB - ZONE URBAINE MIXTE

Article UB 1 - OCCUPATIONS ET UTILISATIONS DU SOL INTERDITES
- Les installations classées pour la protection de l'environnement soumises à autorisation
- Les constructions à usage industriel
- Les dépôts de véhicules et de matériaux

Article UB 2 - HAUTEUR MAXIMALE DES CONSTRUCTIONS
La hauteur maximale des constructions est fixée à 12 mètres au faîtage.
En limite séparative, la hauteur est limitée à 3,50 mètres.

Article UB 3 - IMPLANTATION PAR RAPPORT AUX VOIES
Les constructions doivent être implantées avec un recul minimum de 5 mètres par rapport à l'alignement.

Article UB 4 - IMPLANTATION PAR RAPPORT AUX LIMITES SÉPARATIVES
Les constructions peuvent être implantées :
- Soit en limite séparative
- Soit avec un recul minimum de 3 mètres

Article UB 5 - EMPRISE AU SOL
L'emprise au sol maximale est fixée à 60% de la surface du terrain.

Article UB 6 - STATIONNEMENT
- Habitat : 1 place par logement jusqu'à 50m², 2 places au-delà
- Bureaux : 1 place pour 50m² de surface de plancher
- Commerce : 1 place pour 25m² de surface de vente
"""
            with open(dir_path / "reglement_ub.txt", "w", encoding="utf-8") as f:
                f.write(sample_reglement)
        
        elif dir_type == "plu":
            # Exemple de métadonnées PLU
            sample_plu = {
                "commune": "Montpellier",
                "date_approbation": "2023-03-15",
                "zones": ["UA", "UB", "UC", "UD", "AU", "A", "N"],
                "documents": {
                    "reglement": "reglement_complet.pdf",
                    "zonage": "plan_zonage.pdf",
                    "rapport": "rapport_presentation.pdf"
                }
            }
            with open(dir_path / "montpellier_metadata.json", "w", encoding="utf-8") as f:
                json.dump(sample_plu, f, ensure_ascii=False, indent=2)
    
    def load_mock_data(self):
        """Charge les données mockées en mémoire"""
        self.data = {
            "zonage": {},
            "reglements": {},
            "plu": {}
        }
        
        # Charger les données de zonage
        zonage_path = self.base_path / "zonage"
        for file in zonage_path.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    commune = file.stem
                    self.data["zonage"][commune] = json.load(f)
                    logger.info(f"✅ Chargé zonage: {commune}")
            except Exception as e:
                logger.error(f"Erreur chargement {file}: {e}")
    
    async def get_zonage_parcelle(self, commune: str, parcelle: str) -> Optional[Dict]:
        """
        Simule l'API SOGEFI pour récupérer le zonage d'une parcelle
        
        Args:
            commune: Nom de la commune
            parcelle: Référence cadastrale
            
        Returns:
            Données de zonage ou None
        """
        commune_lower = commune.lower()
        if commune_lower in self.data["zonage"]:
            # Pour la simulation, on retourne une zone aléatoire
            # En prod, ce serait basé sur les coordonnées réelles
            zones = self.data["zonage"][commune_lower].get(commune_lower, {}).get("zones", {})
            if zones:
                # Retourner la zone UB par défaut pour les tests
                return {
                    "commune": commune,
                    "parcelle": parcelle,
                    "zone": "UB",
                    "details": zones.get("UB", {})
                }
        return None
    
    async def get_reglement_zone(self, commune: str, zone: str) -> Optional[str]:
        """
        Simule l'API pour récupérer le règlement d'une zone
        
        Args:
            commune: Nom de la commune
            zone: Code de la zone (UA, UB, etc.)
            
        Returns:
            Texte du règlement ou None
        """
        # Lire le fichier de règlement
        reglement_file = self.base_path / "reglements" / f"reglement_{zone.lower()}.txt"
        if reglement_file.exists():
            try:
                with open(reglement_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Erreur lecture règlement: {e}")
        
        # Règlement par défaut si pas trouvé
        return f"Règlement de la zone {zone} non disponible"
    
    async def get_plu_metadata(self, commune: str) -> Optional[Dict]:
        """
        Simule l'API pour récupérer les métadonnées du PLU
        
        Args:
            commune: Nom de la commune
            
        Returns:
            Métadonnées PLU ou None
        """
        metadata_file = self.base_path / "plu" / f"{commune.lower()}_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur lecture métadonnées PLU: {e}")
        
        # Métadonnées par défaut
        return {
            "commune": commune,
            "status": "PLU approuvé",
            "date": "2023-01-01",
            "message": "Données simulées pour les tests"
        }
    
    async def search_documents(self, query: str, commune: Optional[str] = None) -> List[Dict]:
        """
        Simule une recherche dans les documents d'urbanisme
        
        Args:
            query: Requête de recherche
            commune: Filtrer par commune (optionnel)
            
        Returns:
            Liste de documents pertinents
        """
        results = []
        
        # Recherche simple dans les règlements
        reglements_path = self.base_path / "reglements"
        for file in reglements_path.glob("*.txt"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        results.append({
                            "type": "reglement",
                            "file": file.name,
                            "zone": file.stem.replace("reglement_", "").upper(),
                            "extrait": self._extract_context(content, query)
                        })
            except Exception as e:
                logger.error(f"Erreur recherche dans {file}: {e}")
        
        return results[:5]  # Limiter à 5 résultats
    
    def _extract_context(self, text: str, query: str, context_size: int = 200) -> str:
        """Extrait le contexte autour d'une requête dans un texte"""
        lower_text = text.lower()
        lower_query = query.lower()
        
        pos = lower_text.find(lower_query)
        if pos == -1:
            return ""
        
        start = max(0, pos - context_size // 2)
        end = min(len(text), pos + len(query) + context_size // 2)
        
        extract = text[start:end]
        if start > 0:
            extract = "..." + extract
        if end < len(text):
            extract = extract + "..."
            
        return extract

# Instance globale
mock_api = None

def init_mock_api(documents_path: str = "documents") -> MockUrbanismAPI:
    """
    Initialise l'API mockée
    
    Returns:
        Instance de l'API mockée
    """
    global mock_api
    mock_api = MockUrbanismAPI(documents_path)
    return mock_api