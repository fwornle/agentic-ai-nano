"""Qdrant high-performance implementation."""

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, OptimizersConfig


class QdrantVectorStore:
    """High-performance Qdrant vector store."""
    
    def __init__(self, host: str = "localhost", port: int = 6333, 
                 collection_name: str = "documents"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        
        # Initialize client
        self.client = QdrantClient(
            host=host, 
            port=port,
            timeout=60  # Extended timeout for large operations
        )
        
        self._setup_collection()
        
    def _setup_collection(self, dimension: int = 1536):
        """Create collection with performance optimizations."""
        
        # Check if collection exists
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            # Create collection with optimized settings
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,
                    on_disk=True  # Store vectors on disk for memory efficiency
                ),
                optimizers_config=OptimizersConfig(
                    deleted_threshold=0.2,
                    vacuum_min_vector_number=1000,
                    default_segment_number=2,
                    max_segment_size=200000,
                    memmap_threshold=200000,
                    indexing_threshold=20000,
                    flush_interval_sec=1,
                    max_optimization_threads=2
                ),
                hnsw_config=models.HnswConfig(
                    m=16,  # Number of bi-directional connections
                    ef_construct=200,  # Size of dynamic candidate list
                    full_scan_threshold=10000,  # Threshold for full scan
                    max_indexing_threads=2,  # Parallel indexing
                    on_disk=True  # Store index on disk
                )
            )
            
            print(f"Created optimized collection: {self.collection_name}")
        else:
            print(f"Using existing collection: {self.collection_name}")