"""Configuration settings for Session 3 vector databases and search optimization."""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ChromaConfig:
    """ChromaDB configuration."""
    persist_directory: str = "./chroma_db"
    collection_name: str = "documents"
    hnsw_space: str = "cosine"
    hnsw_construction_ef: int = 200
    hnsw_m: int = 16
    hnsw_search_ef: int = 100


@dataclass
class PineconeConfig:
    """Pinecone configuration."""
    api_key: str = os.getenv('PINECONE_API_KEY', '')
    environment: str = os.getenv('PINECONE_ENVIRONMENT', '')
    index_name: str = "rag-documents"
    dimension: int = 1536
    metric: str = "cosine"
    pods: int = 2
    replicas: int = 1
    pod_type: str = "p1.x1"


@dataclass
class QdrantConfig:
    """Qdrant configuration."""
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "documents"
    dimension: int = 1536
    distance_metric: str = "cosine"


@dataclass
class SearchConfig:
    """Search optimization configuration."""
    cache_size: int = 1000
    batch_size: int = 1000
    enable_hybrid_search: bool = True
    enable_reranking: bool = True
    semantic_weight: float = 0.7
    lexical_weight: float = 0.3
    bm25_k1: float = 1.2
    bm25_b: float = 0.75
    

class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.chroma = ChromaConfig()
        self.pinecone = PineconeConfig()
        self.qdrant = QdrantConfig()
        self.search = SearchConfig()
        
    def get_production_config(self) -> Dict[str, Any]:
        """Get production-ready configuration."""
        return {
            'use_chroma': True,
            'use_pinecone': bool(self.pinecone.api_key),
            'use_qdrant': True,
            'chroma_persist_dir': self.chroma.persist_directory,
            'chroma_collection': self.chroma.collection_name,
            'pinecone_api_key': self.pinecone.api_key,
            'pinecone_environment': self.pinecone.environment,
            'pinecone_index': self.pinecone.index_name,
            'qdrant_host': self.qdrant.host,
            'qdrant_port': self.qdrant.port,
            'qdrant_collection': self.qdrant.collection_name,
            'dimension': self.pinecone.dimension,
            'documents': [],  # To be populated with actual documents
            'search_config': self.search
        }


# Global configuration instance
config = Config()