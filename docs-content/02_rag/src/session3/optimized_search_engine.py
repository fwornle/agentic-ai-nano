"""Production search engine with caching and optimization."""

from functools import lru_cache
import hashlib
import pickle
import time
from typing import Optional, List, Dict, Tuple


class OptimizedSearchEngine:
    """Production search engine with caching and optimization."""
    
    def __init__(self, vector_store, cache_size: int = 1000):
        self.vector_store = vector_store
        self.cache_size = cache_size
        self.query_cache = {}
        self.embedding_cache = {}
        
    @lru_cache(maxsize=1000)
    def _get_query_embedding(self, query: str) -> Tuple[float, ...]:
        """Cache query embeddings to avoid recomputation."""
        embedding = self.vector_store.embedding_function.embed_query(query)
        return tuple(embedding)  # Hashable for LRU cache
    
    def optimized_search(self, query: str, top_k: int = 10,
                        filters: Optional[Dict] = None,
                        use_cache: bool = True) -> List[Dict]:
        """Optimized search with caching and preprocessing."""
        
        # Create cache key
        cache_key = self._create_cache_key(query, top_k, filters)
        
        # Check cache
        if use_cache and cache_key in self.query_cache:
            print("Cache hit!")
            return self.query_cache[cache_key]
        
        # Preprocess query
        processed_query = self._preprocess_query(query)
        
        # Get embedding (with caching)
        query_embedding = list(self._get_query_embedding(processed_query))
        
        # Perform search with optimizations
        results = self._search_with_optimizations(
            query_embedding, top_k, filters
        )
        
        # Cache results
        if use_cache and len(self.query_cache) < self.cache_size:
            self.query_cache[cache_key] = results
        
        return results
    
    def _create_cache_key(self, query: str, top_k: int, filters: Optional[Dict]) -> str:
        """Create a hash-based cache key."""
        key_data = f"{query}:{top_k}:{str(filters) if filters else ''}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocess query for better search results."""
        # Basic preprocessing - can be enhanced
        processed = query.strip().lower()
        # Add domain-specific preprocessing here
        return processed
    
    def _search_with_optimizations(self, query_embedding: List[float], 
                                  top_k: int, filters: Optional[Dict]) -> List[Dict]:
        """Perform search with various optimizations."""
        start_time = time.time()
        
        # Perform the actual search
        results = self.vector_store.similarity_search_with_scores(
            query_embedding, k=top_k, filters=filters
        )
        
        search_time = time.time() - start_time
        
        # Add timing information to results
        for result in results:
            result['search_time'] = search_time
        
        return results