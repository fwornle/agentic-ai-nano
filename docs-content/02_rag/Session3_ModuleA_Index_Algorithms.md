# Session 3 - Module A: Advanced Index Algorithms

## 🎯 Module Overview
**Time Investment**: 45 minutes
**Prerequisites**: Session 3 Core Content
**Learning Outcome**: Master advanced vector indexing algorithms and optimization

---

## 🧭 Navigation & Quick Start

### Related Modules
- **[📄 Session 3 Core: Vector Databases & Search Optimization →](Session3_Vector_Databases_Search_Optimization.md)** - Foundation vector search concepts
- **[🔍 Session 4 Modules →](Session4_ModuleA_Query_Understanding.md)** - Query processing techniques

### 🗂️ Code Files
- **Vector Index Engine**: [`src/session3/optimized_vector_index.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/02_rag/src/session3/optimized_vector_index.py) - Advanced indexing algorithms
- **Search Optimization**: [`src/session3/optimized_search_engine.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/02_rag/src/session3/optimized_search_engine.py) - Search performance optimization
- **Hybrid Search**: [`src/session3/hybrid_search_engine.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/02_rag/src/session3/hybrid_search_engine.py) - Combined vector/keyword search
- **Demo Application**: [`src/session3/demo_vector_search.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/02_rag/src/session3/demo_vector_search.py) - Index algorithms showcase

### 🚀 Quick Start
```bash
# Test advanced indexing algorithms
cd src/session3
python demo_vector_search.py

# Benchmark vector index performance
python -c "from optimized_vector_index import OptimizedVectorIndex; OptimizedVectorIndex().benchmark()"

# Test hybrid search capabilities
python -c "from hybrid_search_engine import HybridSearchEngine; print('Advanced indexing ready!')"
```

---

## 📚 Advanced Indexing Algorithms

### **Algorithm 1: Custom HNSW Implementation**

First, let's establish the foundational imports and core HNSW class structure. HNSW (Hierarchical Navigable Small World) is a state-of-the-art algorithm for approximate nearest neighbor search:

```python
import numpy as np
from typing import List, Dict, Set, Tuple
import heapq
import random
```

These imports provide the mathematical operations, data structures, and random number generation needed for implementing the HNSW algorithm efficiently.

Now we'll define the core HNSW class with its initialization parameters:

```python
class CustomHNSW:
    """Custom HNSW implementation with optimizations for RAG workloads."""
    
    def __init__(self, dimension: int, M: int = 16, ef_construction: int = 200, ml: float = 1/np.log(2)):
        self.dimension = dimension
        self.M = M  # Maximum connections per node
        self.ef_construction = ef_construction
        self.ml = ml  # Level generation factor
        
        self.data = {}  # Vector storage
        self.levels = {}  # Node levels
        self.connections = {}  # Graph connections
        self.entry_point = None
```

The HNSW parameters are critical for performance: `M` controls connectivity (higher M = better recall but more memory), `ef_construction` affects build quality (higher = better index but slower construction), and `ml` determines the probability distribution for node levels.

Let's implement the vector addition method, which is the core of HNSW construction:

```python
    def add_vector(self, vector_id: str, vector: np.ndarray):
        """Add vector to HNSW index with optimized insertion."""
        
        # Determine level for new node
        level = self._get_random_level()
        
        # Store vector and initialize connections
        self.data[vector_id] = vector
        self.levels[vector_id] = level
        self.connections[vector_id] = [set() for _ in range(level + 1)]
        
        # Find entry point and insert
        if self.entry_point is None:
            self.entry_point = vector_id
            return
```

This initial setup assigns each new vector to multiple levels of the hierarchical graph. The random level assignment creates the skip-list-like structure that enables logarithmic search complexity.

Now we implement the search and connection logic that maintains the graph structure:

```python
        # Search for closest nodes at each level
        current_closest = self.entry_point
        
        # Search from top level down to level + 1
        for lev in range(self.levels[self.entry_point], level, -1):
            current_closest = self._search_level(vector, current_closest, 1, lev)[0][1]
```

This top-down search efficiently navigates through higher levels of the hierarchy to find good starting points for detailed search.

Next, we search and connect at the target levels, building the graph connections:

```python
        # Search and connect at levels <= level
        for lev in range(min(level, self.levels[self.entry_point]), -1, -1):
            candidates = self._search_level(vector, current_closest, self.ef_construction, lev)
            
            # Select connections using heuristic
            M_level = self.M if lev > 0 else self.M * 2
            connections = self._select_connections_heuristic(vector, candidates, M_level)
```

The connection selection heuristic maintains graph quality by choosing diverse, high-quality neighbors.

Finally, we establish bidirectional connections and maintain the entry point:

```python
            # Add bidirectional connections
            for _, neighbor_id in connections:
                self.connections[vector_id][lev].add(neighbor_id)
                self.connections[neighbor_id][lev].add(vector_id)
                
                # Prune connections if necessary
                if len(self.connections[neighbor_id][lev]) > M_level:
                    self._prune_connections(neighbor_id, lev, M_level)
            
            current_closest = connections[0][1] if connections else current_closest
        
        # Update entry point if necessary
        if level > self.levels[self.entry_point]:
            self.entry_point = vector_id
```

### **Algorithm 2: Dynamic Index Optimization**

The hierarchical search and connection process is what makes HNSW so efficient. By starting at high levels with fewer connections and working down to dense lower levels, we achieve both speed and accuracy.

### **Algorithm 2: Dynamic Index Optimization**

Real-world RAG systems need to adapt their indices based on actual query patterns. This dynamic optimization approach analyzes recent queries to tune index parameters for better performance:

```python
class DynamicIndexOptimizer:
    """Dynamic optimization of vector indices based on query patterns."""
    
    def __init__(self, index):
        self.index = index
        self.query_stats = {}
        self.optimization_history = []
```

The optimizer maintains statistics about query patterns and tracks optimization history to make informed decisions about parameter adjustments.

Let's implement the main optimization method that analyzes patterns and applies improvements:

```python
    def optimize_based_on_queries(self, recent_queries: List[np.ndarray]) -> Dict[str, Any]:
        """Optimize index parameters based on recent query patterns."""
        
        # Analyze query characteristics
        query_analysis = self._analyze_query_patterns(recent_queries)
        
        # Determine optimal parameters
        optimal_params = self._calculate_optimal_parameters(query_analysis)
        
        # Apply optimizations
        optimization_results = self._apply_optimizations(optimal_params)
        
        return {
            "query_analysis": query_analysis,
            "optimal_parameters": optimal_params,
            "optimization_results": optimization_results
        }
```

This optimization pipeline demonstrates the data-driven approach to index tuning, where real usage patterns inform performance improvements.

Now let's examine the query pattern analysis that drives optimization decisions:

```python
    def _analyze_query_patterns(self, queries: List[np.ndarray]) -> Dict[str, float]:
        """Analyze query patterns to inform optimization."""
        
        if not queries:
            return {}
            
        # Calculate query statistics
        query_vectors = np.array(queries)
        
        analysis = {
            "avg_query_norm": np.mean(np.linalg.norm(query_vectors, axis=1)),
            "query_diversity": self._calculate_diversity(query_vectors),
            "dominant_dimensions": self._find_dominant_dimensions(query_vectors),
            "query_frequency": len(queries)
        }
        
        return analysis
```

This analysis captures key characteristics of query patterns: vector magnitudes, diversity of queries, dimensional preferences, and query volume. These metrics directly influence optimal index configuration.

Finally, let's see how analysis results translate into parameter adjustments:

```python
    def _calculate_optimal_parameters(self, analysis: Dict[str, float]) -> Dict[str, Any]:
        """Calculate optimal index parameters based on analysis."""
        
        # Default parameters
        params = {
            "ef_search": 100,
            "M": 16,
            "ef_construction": 200
        }
        
        # Adjust based on query patterns
        if analysis.get("query_diversity", 0) > 0.8:
            params["ef_search"] = 150  # Higher diversity needs more exploration
            
        if analysis.get("query_frequency", 0) > 1000:
            params["M"] = 24  # High frequency benefits from more connections
            
        return params
```

### **Algorithm 3: Specialized RAG Index**

Parameter optimization based on query patterns ensures that the index adapts to actual usage. High query diversity requires more extensive search, while high query frequency benefits from denser connectivity for faster retrieval.

### **Algorithm 3: Specialized RAG Index**

RAG systems have unique requirements that generic vector indices don't address. This specialized index combines semantic similarity with keyword matching and temporal relevance:

```python
class RAGOptimizedIndex:
    """Vector index optimized specifically for RAG workloads."""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.semantic_clusters = {}
        self.keyword_index = {}
        self.temporal_index = {}
```

This multi-index architecture recognizes that RAG retrieval benefits from multiple ranking signals: semantic similarity for conceptual matching, keywords for exact term matching, and temporal indexing for recency preferences.

Let's implement the document chunk addition method that populates all three indices:

```python
    def add_document_chunk(self, chunk_id: str, vector: np.ndarray, 
                          metadata: Dict[str, Any]):
        """Add document chunk with RAG-specific optimizations."""
        
        # Store in semantic clusters
        cluster_id = self._assign_semantic_cluster(vector, metadata)
        if cluster_id not in self.semantic_clusters:
            self.semantic_clusters[cluster_id] = []
        self.semantic_clusters[cluster_id].append({
            "id": chunk_id,
            "vector": vector,
            "metadata": metadata
        })
        
        # Index keywords for hybrid search
        keywords = metadata.get("keywords", [])
        for keyword in keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = set()
            self.keyword_index[keyword].add(chunk_id)
```

Semantic clustering groups similar content together, enabling faster search within relevant topics. Keyword indexing provides exact match capabilities that complement semantic similarity.

Now we'll add temporal indexing and implement the optimized search method:

```python
        # Temporal indexing for recency
        timestamp = metadata.get("timestamp", 0)
        if timestamp not in self.temporal_index:
            self.temporal_index[timestamp] = set()
        self.temporal_index[timestamp].add(chunk_id)
    
    def rag_optimized_search(self, query_vector: np.ndarray, 
                           query_keywords: List[str],
                           recency_weight: float = 0.1) -> List[Tuple[float, str]]:
        """Search optimized for RAG retrieval patterns."""
        
        # Semantic search within relevant clusters
        semantic_results = self._cluster_aware_search(query_vector)
```

Temporal indexing enables time-based filtering and recency weighting for fresh information needs.

The optimized search combines multiple ranking signals:

```python
        # Keyword boosting
        keyword_boosted = self._apply_keyword_boosting(semantic_results, query_keywords)
        
        # Recency boosting
        final_results = self._apply_recency_boosting(keyword_boosted, recency_weight)
        
        return final_results
```

The RAG-optimized search combines three complementary ranking signals. Semantic search finds conceptually related content, keyword boosting enhances results with exact term matches, and recency boosting prioritizes newer information when appropriate. This multi-signal approach provides more relevant and comprehensive retrieval than semantic similarity alone.

---

## 📝 Multiple Choice Test - Module A

Test your understanding of advanced index algorithms:

**Question 1:** What is the key advantage of custom HNSW implementation for RAG?

A) Reduced memory usage  
B) RAG-specific optimizations like semantic clustering and keyword integration  
C) Faster build times  
D) Simpler configuration  

**Question 2:** Why is dynamic index optimization important?

A) It reduces storage costs  
B) It adapts index parameters based on actual query patterns for better performance  
C) It simplifies maintenance  
D) It reduces memory usage  

**Question 3:** How does semantic clustering improve RAG performance?

A) It reduces index size  
B) It groups similar content for more efficient search within relevant topics  
C) It speeds up indexing  
D) It reduces computational requirements  

**Question 4:** What is the benefit of hybrid indexing (vector + keyword + temporal)?

A) Reduces complexity  
B) Enables multi-dimensional optimization for semantic, exact match, and recency needs  
C) Reduces memory usage  
D) Simplifies implementation  

**Question 5:** Why is RAG-optimized search different from general vector search?

A) It's always faster  
B) It combines semantic similarity with domain-specific factors like keywords and recency  
C) It uses less memory  
D) It's simpler to implement  

[**🗂️ View Test Solutions →**](Session3_ModuleA_Test_Solutions.md)

---

[← Back to Session 3](Session3_Vector_Databases_Search_Optimization.md)