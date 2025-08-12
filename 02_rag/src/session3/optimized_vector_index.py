"""Advanced indexing strategies with FAISS implementation."""

import faiss
import numpy as np
import time
from typing import List, Tuple


class OptimizedVectorIndex:
    """Advanced vector indexing with intelligent algorithm selection.
    
    This implementation automatically selects the optimal indexing strategy
    based on dataset characteristics and performance requirements.
    """
    
    def __init__(self, dimension: int, index_type: str = "auto"):
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.id_map = {}  # Map internal IDs to external IDs
        self.performance_metrics = {}  # Track build and search performance
        
    def build_index(self, vectors: np.ndarray, 
                   external_ids: List[str],
                   performance_target: str = "balanced") -> None:
        """Build optimized index with intelligent algorithm selection.
        
        Args:
            vectors: Vector data to index
            external_ids: External identifiers for vectors
            performance_target: "speed", "memory", "accuracy", or "balanced"
        """
        
        n_vectors = vectors.shape[0]
        memory_gb = vectors.nbytes / (1024**3)
        
        # Intelligent index selection if auto mode
        if self.index_type == "auto":
            self.index_type = self._select_optimal_index(
                n_vectors, memory_gb, performance_target
            )
        
        print(f"Building {self.index_type} index for {n_vectors:,} vectors "
              f"({memory_gb:.1f}GB)")
        
        build_start = time.time()
        
        if self.index_type == "HNSW":
            self.index = self._build_hnsw_index(vectors, performance_target)
        elif self.index_type == "IVF":
            self.index = self._build_ivf_index(vectors, n_vectors, performance_target)
        elif self.index_type == "IVF_PQ":
            self.index = self._build_ivf_pq_index(vectors, n_vectors, performance_target)
        else:
            # Fallback to flat index for small datasets
            self.index = self._build_flat_index(vectors)
        
        build_time = time.time() - build_start
        self.performance_metrics['build_time'] = build_time
        self.performance_metrics['vectors_per_second'] = n_vectors / build_time
        
        # Store ID mapping
        for i, external_id in enumerate(external_ids):
            self.id_map[i] = external_id
            
        print(f"Index built in {build_time:.1f}s "
              f"({n_vectors/build_time:.0f} vectors/sec)")
    
    def _select_optimal_index(self, n_vectors: int, memory_gb: float, 
                             target: str) -> str:
        """Intelligent index selection based on dataset characteristics."""
        
        if n_vectors < 10000:
            return "Flat"  # Exact search for small datasets
        
        if target == "speed" and memory_gb < 8.0:
            return "HNSW"  # Best latency for moderate memory usage
        
        if target == "memory" or memory_gb > 16.0:
            return "IVF_PQ"  # Compression for large datasets
            
        if target == "accuracy":
            return "HNSW"  # Superior recall characteristics
            
        # Balanced approach
        if n_vectors > 1000000:
            return "IVF_PQ"  # Scale efficiency
        else:
            return "HNSW"    # Performance consistency
    
    def _build_ivf_index(self, vectors: np.ndarray, n_vectors: int, 
                        performance_target: str) -> faiss.Index:
        """Build IVF index with target-specific optimizations."""
        
        # Adaptive centroid selection based on dataset size and target
        if performance_target == "speed":
            centroid_ratio = 0.05  # Fewer clusters, faster search
        elif performance_target == "accuracy":
            centroid_ratio = 0.15  # More clusters, better partitioning
        else:
            centroid_ratio = 0.08  # Balanced approach
            
        n_centroids = max(32, min(65536, int(n_vectors * centroid_ratio)))
        
        print(f"IVF Configuration: {n_centroids:,} centroids "
              f"(ratio: {centroid_ratio:.3f})")
        
        # Create quantizer (centroid index)
        quantizer = faiss.IndexFlatIP(self.dimension)
        
        # Choose IVF variant based on size
        if n_vectors > 100000:
            # Use Product Quantization for large datasets
            m = self._select_pq_segments(self.dimension)
            index = faiss.IndexIVFPQ(quantizer, self.dimension, 
                                   n_centroids, m, 8)  # 8 bits per sub-vector
            print(f"Using IVF+PQ with {m} segments for compression")
        else:
            # Use flat storage for better accuracy on smaller datasets
            index = faiss.IndexIVFFlat(quantizer, self.dimension, n_centroids)
            print("Using IVFFlat for optimal accuracy")
        
        # Training phase - critical for clustering quality
        print("Training IVF centroids...")
        if n_vectors > 1000000:
            # Use sample for very large datasets to speed training
            sample_size = min(1000000, n_vectors)
            sample_indices = np.random.choice(n_vectors, sample_size, replace=False)
            training_data = vectors[sample_indices]
            print(f"Using {sample_size:,} vectors for training")
        else:
            training_data = vectors
            
        index.train(training_data)
        
        # Add all vectors
        print("Adding vectors to index...")
        index.add(vectors)
        
        # Set query parameters based on target
        if performance_target == "speed":
            index.nprobe = max(1, n_centroids // 32)  # Search fewer clusters
        elif performance_target == "accuracy":
            index.nprobe = min(n_centroids, n_centroids // 4)  # Search more clusters
        else:
            index.nprobe = max(8, n_centroids // 16)  # Balanced search
            
        print(f"IVF index ready: nprobe={index.nprobe} "
              f"({100*index.nprobe/n_centroids:.1f}% cluster coverage)")
        
        return index
    
    def _build_ivf_pq_index(self, vectors: np.ndarray, n_vectors: int, 
                           performance_target: str) -> faiss.Index:
        """Build IVF+PQ index with compression."""
        # Similar to _build_ivf_index but with PQ compression
        return self._build_ivf_index(vectors, n_vectors, performance_target)
    
    def _select_pq_segments(self, dimension: int) -> int:
        """Select optimal number of PQ segments for compression."""
        # PQ segments must evenly divide the dimension
        # Common choices: 8, 16, 32, 64 segments
        for m in [8, 16, 32, 64, 96, 128]:
            if dimension % m == 0 and m <= dimension // 2:
                return m
        return 8  # Safe fallback
    
    def _build_hnsw_index(self, vectors: np.ndarray, 
                         performance_target: str) -> faiss.Index:
        """Build HNSW index with target-specific parameter optimization."""
        
        # Parameter selection based on performance target
        if performance_target == "speed":
            M = 16           # Lower connectivity for speed
            ef_construct = 128   # Faster construction
            ef_search = 64       # Faster queries
        elif performance_target == "accuracy":
            M = 64           # High connectivity for best recall
            ef_construct = 512   # Thorough graph construction
            ef_search = 256      # High-accuracy searches
        else:
            M = 32           # Balanced connectivity
            ef_construct = 200   # Good graph quality
            ef_search = 128      # Balanced search
            
        print(f"HNSW Configuration: M={M}, ef_construct={ef_construct}, "
              f"ef_search={ef_search}")
        
        # Create HNSW index
        index = faiss.IndexHNSWFlat(self.dimension, M)
        index.hnsw.efConstruction = ef_construct
        
        # Build the graph
        print("Building HNSW graph structure...")
        index.add(vectors)
        
        # Set search parameter
        index.hnsw.efSearch = ef_search
        
        # Calculate memory usage for monitoring
        memory_per_vector = self.dimension * 4 + M * 4  # Float32 + connections
        total_memory_mb = (len(vectors) * memory_per_vector) / (1024**2)
        
        print(f"HNSW index ready: {len(vectors):,} vectors, "
              f"~{total_memory_mb:.1f}MB memory usage")
        
        return index
    
    def _build_flat_index(self, vectors: np.ndarray) -> faiss.Index:
        """Build flat index for exact search."""
        index = faiss.IndexFlatIP(self.dimension)
        index.add(vectors)
        return index