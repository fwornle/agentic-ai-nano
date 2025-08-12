"""Session 3: Vector Databases & Search Optimization

This module provides production-ready vector database implementations,
hybrid search capabilities, and advanced retrieval techniques for RAG systems.
"""

from .vector_database_interface import VectorDatabaseInterface
from .chroma_vector_store import ChromaVectorStore
from .pinecone_vector_store import PineconeVectorStore
from .qdrant_vector_store import QdrantVectorStore
from .hybrid_search_engine import HybridSearchEngine
from .advanced_reranker import AdvancedReranker
from .optimized_vector_index import OptimizedVectorIndex
from .optimized_search_engine import OptimizedSearchEngine
from .multi_stage_retriever import MultiStageRetriever
from .contextual_filter import ContextualFilter
from .production_vector_search import ProductionVectorSearch, RAGArchitectureOptimizer

__all__ = [
    'VectorDatabaseInterface',
    'ChromaVectorStore',
    'PineconeVectorStore',
    'QdrantVectorStore',
    'HybridSearchEngine',
    'AdvancedReranker',
    'OptimizedVectorIndex',
    'OptimizedSearchEngine',
    'MultiStageRetriever',
    'ContextualFilter',
    'ProductionVectorSearch',
    'RAGArchitectureOptimizer'
]