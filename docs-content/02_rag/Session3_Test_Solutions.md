# Session 3: Vector Databases & Search Optimization - Test Solutions

## 📝 Multiple Choice Test

### Question 1: Vector Database Metrics

**Which vector database metric is most suitable for RAG applications using cosine similarity?**  
A) Euclidean distance  
B) Manhattan distance  
C) Cosine similarity ✅  
D) Hamming distance  

**Explanation:** Cosine similarity is ideal for RAG applications because it measures the angle between vectors rather than their magnitude, making it particularly effective for text embeddings where document length doesn't affect semantic similarity. It's normalized and works well with high-dimensional sparse vectors typical in NLP.

---

### Question 2: HNSW vs IVF Indexing

**What is the primary advantage of HNSW indexing over IVF indexing?**  
A) Lower memory usage  
B) Better compression ratios  
C) Faster query performance with high recall ✅  
D) Simpler configuration  

**Explanation:** HNSW (Hierarchical Navigable Small World) provides faster query performance with high recall compared to IVF (Inverted File). While IVF can be more memory efficient with compression, HNSW excels in speed by using a graph-based structure that enables efficient approximate nearest neighbor search.

---

### Question 3: Reciprocal Rank Fusion Parameter

**In Reciprocal Rank Fusion (RRF), what does the 'k' parameter control?**  
A) Number of results to return  
B) Weight balance between semantic and lexical scores  
C) The smoothing factor in rank combination ✅  
D) Maximum number of query variants  

**Explanation:** In RRF, the 'k' parameter (typically 60) acts as a smoothing factor in the formula: score = 1/(k + rank). It prevents the top-ranked items from dominating the fusion and provides more balanced combination of rankings from different retrieval methods.

---

### Question 4: Cross-Encoder Benefits

**What is the key benefit of cross-encoder reranking compared to bi-encoder similarity?**  
A) Faster inference speed  
B) Lower computational requirements  
C) Joint processing of query-document pairs for better accuracy ✅  
D) Simpler model architecture  

**Explanation:** Cross-encoders process query-document pairs jointly, allowing for attention mechanisms to directly compare the query and document tokens. This provides more accurate relevance scoring compared to bi-encoders, which encode query and documents separately, though at the cost of slower inference speed.

---

### Question 5: IVF vs HNSW Choice

**When should you choose IVF indexing over HNSW for vector search?**  
A) When you need the fastest possible queries  
B) When you have limited memory and large datasets ✅  
C) When accuracy is more important than speed  
D) When you need real-time updates  

**Explanation:** IVF indexing is preferred when you have memory constraints and large datasets because it supports Product Quantization (PQ) compression, reducing memory usage significantly. While HNSW is faster for queries, IVF with PQ can handle much larger datasets within memory limits.

---

### Question 6: HNSW ef_construction Parameter

**What is the purpose of the 'ef_construction' parameter in HNSW?**  
A) Controls memory usage during search  
B) Determines the number of connections per node  
C) Sets the dynamic candidate list size during index building ✅  
D) Defines the maximum number of layers  

**Explanation:** The 'ef_construction' parameter controls the size of the dynamic candidate list during index construction. A higher value (e.g., 200) improves index quality by considering more candidates when building connections, leading to better search accuracy but longer build times.

---

### Question 7: BM25 in Hybrid Search

**In hybrid search, what does BM25 provide that semantic search lacks?**  
A) Better understanding of context  
B) Exact term matching and frequency analysis ✅  
C) Handling of synonyms and related concepts  
D) Multi-language support  

**Explanation:** BM25 provides exact term matching and considers term frequency and document frequency statistics, which semantic search may miss. While semantic search excels at understanding context and synonyms, BM25 ensures that specific terminology and exact phrases are properly weighted in the results.

---

### Question 8: Query Caching Effectiveness

**Why is query caching particularly effective in RAG systems?**  
A) Vector embeddings are expensive to compute  
B) Users often ask similar or repeated questions  
C) Database queries are the main bottleneck  
D) All of the above ✅  

**Explanation:** All factors contribute to caching effectiveness: (A) Vector embeddings require significant computation time, (B) Users frequently ask similar questions making cache hits likely, and (C) Database vector similarity searches can be computationally expensive. Together, these factors make caching highly beneficial for RAG performance.

---

## Performance Scoring

- **8/8 Correct**: Excellent mastery of vector database optimization
- **7/8 Correct**: Strong understanding with minor technical gaps
- **6/8 Correct**: Good grasp of concepts, review indexing algorithms
- **5/8 Correct**: Adequate knowledge, focus on hybrid search techniques
- **4/8 or below**: Recommend hands-on practice with different vector databases

---

## Key Technical Concepts

### Vector Database Architecture

1. **Similarity Metrics**: Cosine, Euclidean, dot product trade-offs
2. **Index Types**: HNSW for speed, IVF for memory efficiency
3. **Configuration Parameters**: Balancing accuracy, speed, and resources
4. **Production Considerations**: Persistence, scaling, monitoring

### Indexing Strategies

1. **HNSW Parameters**: M (connections), ef_construction, ef_search
2. **IVF Configuration**: Centroids, quantization, search probes
3. **Memory vs Speed**: Trade-offs and optimization strategies
4. **Batch Operations**: Efficient data ingestion techniques

### Hybrid Search Implementation

1. **Score Fusion**: RRF, weighted combination, rank-based merging
2. **BM25 Integration**: Lexical search for exact term matching
3. **Multi-Stage Retrieval**: Progressive filtering and reranking
4. **Query Enhancement**: Expansion, reformulation, variant generation

### Performance Optimization

1. **Caching Strategies**: Query results, embeddings, metadata
2. **Parallel Processing**: Concurrent searches, batch operations
3. **Resource Management**: Memory usage, disk I/O, CPU utilization
4. **Monitoring**: Latency tracking, hit rates, error handling

### Production Deployment

1. **Database Selection**: ChromaDB vs Pinecone vs Qdrant trade-offs
2. **Scaling Strategies**: Horizontal scaling, load balancing
3. **Reliability Features**: Replication, backup, failure recovery
4. **Cost Optimization**: Resource usage, query efficiency

---

[← Back to Session 3](Session3_Vector_Databases_Search_Optimization.md) | [Next: Session 4 →](Session4_Query_Enhancement_Context_Augmentation.md)
