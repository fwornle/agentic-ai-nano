# Session 3: Vector Databases & Search Optimization

This module implements production-ready vector database architectures with hybrid search capabilities and advanced optimization techniques for RAG systems.

## 🏗️ Architecture Overview

The module provides a comprehensive vector search infrastructure with:

- **Multiple Vector Database Support**: ChromaDB, Pinecone, Qdrant implementations
- **Hybrid Search**: Combines semantic similarity with BM25 lexical search  
- **Advanced Indexing**: HNSW and IVF optimization strategies
- **Multi-Stage Retrieval**: Query enhancement, parallel search, and reranking
- **Production Optimization**: Caching, batching, and performance monitoring

## 📁 File Structure

```
session3/
├── __init__.py                      # Module exports
├── config.py                       # Configuration management
├── requirements.txt                # Dependencies
├── README.md                       # This file
│
├── vector_database_interface.py    # Abstract interface for vector DBs
├── chroma_vector_store.py          # ChromaDB implementation
├── pinecone_vector_store.py        # Pinecone implementation  
├── qdrant_vector_store.py          # Qdrant implementation
│
├── hybrid_search_engine.py         # Semantic + BM25 fusion
├── advanced_reranker.py            # Cross-encoder reranking
├── optimized_vector_index.py       # FAISS indexing strategies
├── optimized_search_engine.py      # Caching and optimization
│
├── multi_stage_retriever.py        # Multi-stage retrieval pipeline
├── contextual_filter.py            # Advanced filtering and ranking
├── production_vector_search.py     # Complete production system
└── demo_vector_search.py           # Interactive demonstration
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Basic Usage

```python
from session3 import ProductionVectorSearch, config

# Setup configuration
production_config = config.get_production_config()
production_config['documents'] = your_document_list

# Initialize search system
search_system = ProductionVectorSearch(production_config)

# Perform hybrid search
results = await search_system.production_search(
    "your query here", 
    search_type="hybrid", 
    top_k=10
)
```

### 3. Run Demo

```bash
python demo_vector_search.py
```

## 🔧 Configuration

### Environment Variables

```bash
# Pinecone (optional)
export PINECONE_API_KEY="your-api-key"
export PINECONE_ENVIRONMENT="your-environment"

# Qdrant (if using remote instance)
export QDRANT_HOST="your-qdrant-host"
export QDRANT_PORT="6333"
```

### Database-Specific Configuration

#### ChromaDB (Local/Development)
```python
chroma_config = {
    'persist_directory': './chroma_db',
    'collection_name': 'documents',
    'hnsw_construction_ef': 200,
    'hnsw_m': 16,
    'hnsw_search_ef': 100
}
```

#### Pinecone (Managed/Production)
```python
pinecone_config = {
    'api_key': 'your-api-key',
    'environment': 'your-environment', 
    'index_name': 'rag-documents',
    'dimension': 1536,
    'pods': 2,
    'replicas': 1
}
```

#### Qdrant (Self-Hosted/Hybrid)
```python
qdrant_config = {
    'host': 'localhost',
    'port': 6333,
    'collection_name': 'documents',
    'dimension': 1536
}
```

## 🔍 Search Methods

### 1. Hybrid Search
Combines semantic vector similarity with BM25 keyword matching:

```python
results = await search_system.production_search(
    query="vector database optimization",
    search_type="hybrid",
    top_k=10
)
```

**Key Features:**
- BM25 lexical scoring with tunable k1/b parameters
- Reciprocal Rank Fusion (RRF) for score combination
- Cross-encoder reranking for accuracy improvement

### 2. Multi-Stage Retrieval
Advanced pipeline with query enhancement and progressive filtering:

```python
results = await search_system.production_search(
    query="complex multi-part question",
    search_type="multi_stage", 
    top_k=10
)
```

**Pipeline Stages:**
1. Query variant generation (original, expanded, HyDE, sub-queries)
2. Parallel retrieval across variants
3. Result deduplication and merging
4. Progressive filtering and reranking

### 3. Optimized Search
High-performance search with caching and preprocessing:

```python
from session3 import OptimizedSearchEngine

optimized_engine = OptimizedSearchEngine(vector_store, cache_size=1000)
results = optimized_engine.optimized_search(
    query="your query",
    top_k=10,
    use_cache=True
)
```

## ⚡ Performance Optimization

### Index Configuration

#### HNSW Parameters (for accuracy-focused scenarios)
```python
hnsw_config = {
    'M': 32,                    # Higher connectivity = better recall
    'ef_construction': 200,     # Build-time accuracy 
    'ef_search': 128           # Query-time accuracy
}
```

#### IVF Parameters (for scale-focused scenarios)  
```python
ivf_config = {
    'centroids': n_vectors * 0.08,    # ~8% of dataset size
    'nprobe': centroids // 16,        # Search 6.25% of clusters
    'use_pq': True,                   # Enable compression
    'pq_segments': 16                 # Compression ratio
}
```

### Caching Strategy

The system implements multi-level caching:

1. **Query Embedding Cache**: Reuse embeddings for identical queries
2. **Result Cache**: Store complete search results 
3. **Index Cache**: Persist built indices across sessions

### Batch Operations

Optimize for bulk operations:

```python
# Batch document addition
chroma_store.add_documents_batch(
    documents=documents,
    embeddings=embeddings,
    metadata=metadata,
    ids=ids,
    batch_size=1000
)

# Batch vector upserts
pinecone_store.upsert_vectors_batch(
    vectors=vector_data,
    batch_size=100
)
```

## 📊 Architecture Recommendations

The system includes intelligent architecture selection:

```python
from session3 import RAGArchitectureOptimizer

requirements = {
    'daily_queries': 10000,
    'document_count': 1000000, 
    'max_latency_ms': 100,
    'monthly_budget_usd': 500,
    'min_recall': 0.90
}

recommendation = RAGArchitectureOptimizer.recommend_architecture(requirements)
```

**Decision Matrix:**

| Scenario | Database | Index | Rationale |
|----------|----------|-------|-----------|
| High Performance (<100ms) | Pinecone | HNSW | Managed infrastructure, consistent latency |
| Large Scale (>1M docs) | Qdrant | IVF+PQ | Compression, cost efficiency |  
| Development/Moderate | ChromaDB | HNSW | Local setup, balanced performance |

## 🧪 Evaluation Metrics

Monitor search quality and performance:

```python
# Performance metrics
metrics = search_system.performance_metrics
print(f"Average search time: {metrics['hybrid']['total_time'] / metrics['hybrid']['total_queries']:.3f}s")

# Quality evaluation (implement based on your golden dataset)
def evaluate_search_quality(search_system, test_queries):
    precision_scores = []
    recall_scores = []
    
    for query, expected_docs in test_queries:
        results = search_system.production_search(query, top_k=10)
        # Calculate precision@k, recall@k, NDCG
        # ...
        
    return {
        'precision_at_10': np.mean(precision_scores),
        'recall_at_10': np.mean(recall_scores)
    }
```

## 🔧 Troubleshooting

### Common Issues

**ChromaDB Collection Errors:**
- Ensure persistent directory exists and is writable
- Check HNSW parameter compatibility with your data

**Pinecone Rate Limits:**
- Implement exponential backoff in batch operations
- Monitor pod utilization and scale as needed

**Qdrant Memory Issues:**
- Enable `on_disk=True` for large collections
- Tune `memmap_threshold` based on available RAM

**Poor Search Quality:**
- Adjust hybrid search weights (semantic vs lexical)
- Fine-tune BM25 parameters (k1, b) for your domain
- Implement domain-specific preprocessing

### Performance Tuning

**Slow Query Performance:**
- Reduce `ef_search` for HNSW indices
- Increase batch sizes for bulk operations
- Enable result caching for repeated queries

**High Memory Usage:**
- Use IVF+PQ compression for large datasets
- Enable disk storage in Qdrant configuration
- Implement query result pagination

## 📚 Key References

- **HNSW Algorithm**: [Efficient and robust approximate nearest neighbor search](https://arxiv.org/abs/1603.09320)
- **BM25 Scoring**: [The Probabilistic Relevance Framework: BM25 and Beyond](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- **Hybrid Search**: [Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906)
- **Vector Database Comparison**: [Vector Database Benchmarks](https://benchmark.vectorview.ai/)

## 🎯 Next Steps

This vector search infrastructure enables:

- **Session 4**: Query Enhancement & Context Augmentation
- **Session 5**: RAG Evaluation & Quality Assessment  
- **Session 6**: Graph-Enhanced Retrieval
- **Session 9**: Production Deployment & Scaling

The optimized search foundation you've built here will support increasingly sophisticated RAG capabilities throughout the remaining sessions.