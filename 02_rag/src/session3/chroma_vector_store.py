"""ChromaDB implementation with production optimizations."""

import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Optional, Tuple


class ChromaVectorStore:
    """Advanced ChromaDB wrapper with optimization features.
    
    This implementation prioritizes:
    - HNSW index optimization for 100k-1M document collections
    - Persistent storage for production reliability
    - Batch operations for efficient data loading
    - Memory-conscious configuration for stable performance
    """
    
    def __init__(self, persist_directory: str, collection_name: str):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Performance tracking for optimization feedback
        self.query_times = []
        self.build_times = []
        
        # Initialize client with optimized settings
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                allow_reset=True,        # Enables index rebuilding during development
                anonymized_telemetry=False  # Reduces network calls in production
            )
        )
        
        # Create or get collection with optimized settings
        self.collection = self._initialize_collection()
        
    def _initialize_collection(self):
        """Initialize collection with carefully tuned HNSW parameters.
        
        Parameter Selection Rationale:
        - cosine similarity: Optimal for text embeddings (handles normalization)
        - construction_ef=200: Higher accuracy during index building (2-3x query ef)
        - M=16: Sweet spot for memory vs. connectivity (typical range: 12-48)
        - search_ef=100: Balances speed vs. accuracy for RAG recall requirements
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(
                name=self.collection_name
            )
            print(f"Loaded existing collection: {self.collection_name}")
            
        except ValueError:
            # Create new collection with optimized HNSW settings
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",           # Cosine similarity for text embeddings
                    "hnsw:construction_ef": 200,     # Build-time accuracy (higher = better quality)
                    "hnsw:M": 16,                     # Node connectivity (higher = more memory, better recall)
                    "hnsw:search_ef": 100             # Query-time speed/accuracy trade-off
                }
            )
            print(f"Created new collection: {self.collection_name}")
        
        return collection
    
    def add_documents_batch(self, documents: List[str], 
                           embeddings: List[List[float]], 
                           metadata: List[Dict], 
                           ids: List[str], 
                           batch_size: int = 1000):
        """Add documents in optimized batches."""
        
        total_docs = len(documents)
        print(f"Adding {total_docs} documents in batches of {batch_size}")
        
        for i in range(0, total_docs, batch_size):
            batch_end = min(i + batch_size, total_docs)
            
            batch_documents = documents[i:batch_end]
            batch_embeddings = embeddings[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_ids = ids[i:batch_end]
            
            self.collection.add(
                documents=batch_documents,
                embeddings=batch_embeddings,
                metadatas=batch_metadata,
                ids=batch_ids
            )
            
            print(f"Added batch {i//batch_size + 1}/{(total_docs-1)//batch_size + 1}")
    
    def similarity_search_with_scores(self, query: str, k: int = 10, 
                                     filters: Dict = None):
        """Search for similar documents with scores."""
        # Note: In a real implementation, you would need to embed the query first
        # This is a simplified interface
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=filters
        )
        return results