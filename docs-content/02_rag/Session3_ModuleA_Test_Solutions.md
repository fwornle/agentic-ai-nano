# Session 3: Advanced Index Algorithms - Test Solutions

## 📝 Multiple Choice Test

**Question 1:** What is the key advantage of custom HNSW implementation for RAG?  
A) Reduced memory usage  
B) RAG-specific optimizations like semantic clustering and keyword integration ✅  
C) Faster build times  
D) Simpler configuration  

**Explanation:** Custom HNSW implementations for RAG enable domain-specific optimizations beyond generic vector search. These include semantic clustering for topic-focused search, keyword integration for exact-match capabilities, and temporal indexing for recency weighting. The hierarchical structure of HNSW (multi-level skip-list approach) combined with RAG-specific enhancements creates an efficient retrieval system optimized for generation tasks.

**Question 2:** Why is dynamic index optimization important?  
A) It reduces storage costs  
B) It adapts index parameters based on actual query patterns for better performance ✅  
C) It simplifies maintenance  
D) It reduces memory usage  

**Explanation:** Dynamic index optimization creates a feedback loop where the system learns from actual query patterns to self-improve. It analyzes query diversity, frequency, dimensional preferences, and performance metrics to adjust parameters like `ef_search`, `M`, and `ef_construction`. This adaptive approach ensures optimal performance for the specific workload rather than relying on generic default settings.

**Question 3:** How does semantic clustering improve RAG performance?  
A) It reduces index size  
B) It groups similar content for more efficient search within relevant topics ✅  
C) It speeds up indexing  
D) It reduces computational requirements  

**Explanation:** Semantic clustering creates a hierarchical organization where conceptually related content is grouped together. This enables cluster-aware search that can quickly focus on relevant topic areas rather than scanning the entire vector space. The result is faster retrieval with maintained accuracy, as the search space is intelligently narrowed to topically relevant content.

**Question 4:** What is the benefit of hybrid indexing (vector + keyword + temporal)?  
A) Reduces complexity  
B) Enables multi-dimensional optimization for semantic, exact match, and recency needs ✅  
C) Reduces memory usage  
D) Simplifies implementation  

**Explanation:** Hybrid indexing recognizes that RAG retrieval requires more than semantic similarity. It combines three complementary signals: vector similarity for conceptual matching, keyword indexing for exact term precision, and temporal indexing for freshness weighting. This multi-dimensional approach ensures that whether users ask conceptual questions, seek specific terms, or need recent information, the system can respond appropriately.

**Question 5:** Why is RAG-optimized search different from general vector search?  
A) It's always faster  
B) It combines semantic similarity with domain-specific factors like keywords and recency ✅  
C) It uses less memory  
D) It's simpler to implement  

**Explanation:** RAG-optimized search is designed specifically for retrieval-augmented generation workflows, where the goal isn't just finding similar content but finding the most useful content for answering questions. It combines semantic similarity with keyword boosting for precision, recency weighting for fresh information, and content diversity considerations for comprehensive context. This multi-signal fusion creates retrieval results optimized for generation quality rather than just similarity scoring.
---

## Navigation

**Back to Test:** [Session 3 Test Questions →](Session3_*.md#multiple-choice-test)

---
