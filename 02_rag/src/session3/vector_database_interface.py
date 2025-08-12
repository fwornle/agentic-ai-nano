"""Vector database abstract interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class VectorDatabaseInterface(ABC):
    """Abstract interface for vector database operations."""
    
    def __init__(self, dimension: int, metric: str = "cosine"):
        self.dimension = dimension
        self.metric = metric  # cosine, euclidean, dot_product
    
    @abstractmethod
    def add_vectors(self, vectors: List[List[float]], 
                   metadata: List[Dict], ids: List[str]):
        """Add vectors with metadata and IDs."""
        raise NotImplementedError
    
    @abstractmethod
    def search(self, query_vector: List[float], 
              top_k: int = 10, filters: Dict = None):
        """Search for similar vectors with optional filtering."""
        raise NotImplementedError
    
    @abstractmethod
    def update_vector(self, vector_id: str, 
                     new_vector: List[float], new_metadata: Dict):
        """Update existing vector and metadata."""
        raise NotImplementedError