import os
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import hashlib

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainFilter

import pypdf2
import pdfplumber

logger = logging.getLogger(__name__)

class RAGSystem:
    """
    Système RAG (Retrieval Augmented Generation) pour l'urbanisme
    """
    
    def __init__(self, 
                 documents_path: str = "documents",
                 persist_directory: str = "chroma_db",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialise le système RAG
        
        Args:
            documents_path: Chemin vers les documents
            persist_directory: Dossier pour persister ChromaDB
            embedding_model: Modèle pour les embeddings
        """
        self.documents_path = Path(documents_path)
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        
        # Splitter pour découper les documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Embeddings
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        
        # Cache des documents indexés
        self.indexed_files = set()
        self._load_indexed_files()
    
    def initialize(self):
        """Initialise les embeddings et la base vectorielle"""
        try:
            logger.info("🚀 Initialisation du système RAG...")
            
            # Créer les embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Créer ou charger la base vectorielle
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            # Créer le retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            logger.info("✅ Système RAG initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation RAG: {e}")
            raise
    
    def _load_indexed_files(self):
        """Charge la liste des fichiers déjà indexés"""
        index_file = Path(self.persist_directory) / "indexed_files.txt"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                self.indexed_files = set(line.strip() for line in f)
    
    def _save_indexed_files(self):
        """Sauvegarde la liste des fichiers indexés"""
        index_file = Path(self.persist_directory) / "indexed_files.txt"
        index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(index_file, "w", encoding="utf-8") as f:
            for file in self.indexed_files:
                f.write(f"{file}\n")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calcule le hash d'un fichier"""
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def load_document(self, file_path: Path) -> List[Document]:
        """
        Charge un document et le découpe en chunks
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Liste de documents LangChain
        """
        documents = []
        
        try:
            if file_path.suffix == ".pdf":
                # Utiliser pdfplumber pour meilleure extraction
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                
                if not text.strip():
                    # Fallback sur PyPDF2
                    with open(file_path, "rb") as f:
                        reader = pypdf2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
            
            elif file_path.suffix in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            
            else:
                logger.warning(f"Type de fichier non supporté: {file_path}")
                return documents
            
            # Créer le document avec métadonnées
            metadata = {
                "source": str(file_path),
                "type": file_path.parent.name,  # plu, zonage, reglements
                "filename": file_path.name
            }
            
            # Si c'est un règlement, extraire la zone
            if "reglement" in file_path.name.lower():
                zone = file_path.stem.replace("reglement_", "").upper()
                metadata["zone"] = zone
            
            # Découper en chunks
            chunks = self.text_splitter.split_text(text)
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={**metadata, "chunk_index": i}
                )
                documents.append(doc)
            
            logger.info(f"📄 Chargé {file_path.name}: {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Erreur chargement {file_path}: {e}")
        
        return documents
    
    def index_documents(self, force_reindex: bool = False):
        """
        Indexe tous les documents du dossier
        
        Args:
            force_reindex: Force la réindexation même si déjà indexé
        """
        if not self.vectorstore:
            raise ValueError("RAG non initialisé. Appelez initialize() d'abord.")
        
        all_documents = []
        
        # Parcourir tous les sous-dossiers
        for subdir in ["plu", "zonage", "reglements"]:
            dir_path = self.documents_path / subdir
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.glob("*"):
                if file_path.is_file():
                    file_hash = f"{file_path}:{self._get_file_hash(file_path)}"
                    
                    # Vérifier si déjà indexé
                    if not force_reindex and file_hash in self.indexed_files:
                        logger.info(f"⏭️ Déjà indexé: {file_path.name}")
                        continue
                    
                    # Charger et indexer
                    docs = self.load_document(file_path)
                    if docs:
                        all_documents.extend(docs)
                        self.indexed_files.add(file_hash)
        
        # Ajouter à la base vectorielle
        if all_documents:
            logger.info(f"🔄 Indexation de {len(all_documents)} chunks...")
            self.vectorstore.add_documents(all_documents)
            self.vectorstore.persist()
            self._save_indexed_files()
            logger.info("✅ Indexation terminée")
        else:
            logger.info("ℹ️ Aucun nouveau document à indexer")
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Recherche dans la base vectorielle
        
        Args:
            query: Question de recherche
            k: Nombre de résultats
            
        Returns:
            Documents pertinents
        """
        if not self.retriever:
            raise ValueError("RAG non initialisé. Appelez initialize() d'abord.")
        
        try:
            # Recherche simple
            docs = self.retriever.get_relevant_documents(query)
            
            # Log pour debug
            logger.info(f"🔍 Recherche: '{query[:50]}...' → {len(docs)} résultats")
            
            return docs[:k]
            
        except Exception as e:
            logger.error(f"Erreur recherche: {e}")
            return []
    
    def get_context_for_question(self, question: str, commune: Optional[str] = None) -> Tuple[str, List[Document]]:
        """
        Récupère le contexte pertinent pour une question
        
        Args:
            question: Question de l'utilisateur
            commune: Filtrer par commune (optionnel)
            
        Returns:
            Tuple (contexte formaté, documents sources)
        """
        # Rechercher les documents pertinents
        docs = self.search(question)
        
        # Filtrer par commune si spécifié
        if commune and docs:
            filtered_docs = []
            for doc in docs:
                if commune.lower() in doc.page_content.lower() or \
                   commune.lower() in doc.metadata.get("source", "").lower():
                    filtered_docs.append(doc)
            
            # Si pas de résultats pour la commune, garder tous les docs
            if filtered_docs:
                docs = filtered_docs
        
        # Formater le contexte
        context_parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Document")
            zone = doc.metadata.get("zone", "")
            
            header = f"[Source {i+1}: {source}"
            if zone:
                header += f" - Zone {zone}"
            header += "]"
            
            context_parts.append(f"{header}\n{doc.page_content}")
        
        context = "\n\n".join(context_parts)
        
        return context, docs
    
    def create_qa_chain(self, llm):
        """
        Crée une chaîne question-réponse avec le LLM
        
        Args:
            llm: Instance du LLM
            
        Returns:
            Chaîne QA configurée
        """
        if not self.vectorstore:
            raise ValueError("RAG non initialisé. Appelez initialize() d'abord.")
        
        # Créer la chaîne QA
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            verbose=True
        )
        
        return qa_chain

# Instance globale
rag_system = None

def init_rag(documents_path: str = "documents", 
             persist_directory: str = "chroma_db") -> RAGSystem:
    """
    Initialise le système RAG global
    
    Returns:
        Instance du système RAG
    """
    global rag_system
    rag_system = RAGSystem(documents_path, persist_directory)
    rag_system.initialize()
    return rag_system