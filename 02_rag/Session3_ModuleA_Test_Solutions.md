# Session 3: Advanced Index Algorithms - Test Solutions

## 📝 Multiple Choice Test

### Question 1: Custom HNSW for RAG

**What is the primary advantage of custom HNSW implementations for RAG systems?**

A) Better memory efficiency  
B) RAG-specific optimizations like semantic clustering and keyword integration ✅  
C) Faster training times  
D) Lower computational requirements  

**Explanation:** Custom HNSW implementations for RAG can incorporate domain-specific optimizations such as semantic clustering to group related content, keyword indexing for hybrid search capabilities, and temporal indexing for recency-aware retrieval. These optimizations are specifically designed for RAG workloads.

---

### Question 2: Dynamic Index Optimization

**How does dynamic index optimization improve RAG performance?**

A) It reduces storage requirements  
B) It adapts index parameters based on actual query patterns for better performance ✅  
C) It eliminates the need for embeddings  
D) It automatically generates new content  

**Explanation:** Dynamic index optimization analyzes real query patterns to adjust parameters like `ef_search`, `M`, and `ef_construction`. This data-driven approach ensures that the index configuration matches actual usage patterns, improving both speed and accuracy for the specific workload.

---

### Question 3: Semantic Clustering Benefits

**What is the main benefit of semantic clustering in RAG index structures?**

A) It reduces vector dimensions  
B) It groups similar content for more efficient search within relevant topics ✅  
C) It eliminates duplicate content  
D) It compresses the index size  

**Explanation:** Semantic clustering organizes vectors by topic similarity, allowing search algorithms to focus on relevant content clusters rather than searching the entire index. This reduces search time while maintaining high recall for topically related queries.

---

### Question 4: Hybrid Indexing Benefits

**Why is hybrid indexing valuable for RAG systems?**

A) It simplifies implementation complexity  
B) Enables multi-dimensional optimization for semantic, exact match, and recency needs ✅  
C) It reduces computational overhead  
D) It eliminates the need for preprocessing  

**Explanation:** Hybrid indexing combines vector similarity (semantic), keyword matching (exact terms), and temporal indexing (recency) to provide comprehensive retrieval capabilities. This multi-signal approach addresses different types of user information needs more effectively than any single indexing method.

---

### Question 5: RAG-Optimized vs General Vector Search

**How does RAG-optimized search differ from general vector search?**

A) It uses different embedding models  
B) It combines semantic similarity with domain-specific factors like keywords and recency ✅  
C) It processes queries faster  
D) It requires less training data  

**Explanation:** RAG-optimized search recognizes that information retrieval for generation tasks requires more than semantic similarity. It incorporates keyword relevance for specific terms, temporal factors for fresh information, and contextual factors specific to the knowledge domain being searched.

---

[← Back to Session 3](Session3_ModuleA_Index_Algorithms.md)