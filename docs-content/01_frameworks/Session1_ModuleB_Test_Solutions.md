# Session 1 - Module B: Performance Optimization - Test Solutions

## 📝 Multiple Choice Test - Session 1

**Question 1:** What information does the `MemoryEntry` dataclass track to enable intelligent memory management?  
A) Just the memory size and creation time  
B) Only content and timestamp  
C) Content, timestamp, importance_score, and size_bytes ✅  
D) Content and importance score only  

**Explanation:** The `MemoryEntry` dataclass tracks four essential pieces of information: the actual content, when it was created (timestamp), how important it is (importance_score), and its memory footprint (size_bytes). This comprehensive tracking enables intelligent decisions about what to keep and what to remove during memory cleanup operations.

**Question 2:** How does the memory cleanup algorithm prioritize which entries to keep?  
A) First-in-first-out (FIFO)  
B) Random selection  
C) Sorts by importance and age, keeps top 70% ✅  
D) Only keeps the most recent entries  

**Explanation:** The `_cleanup_memory` method sorts entries by both importance_score and timestamp, then keeps the top 70% of entries. This balanced approach preserves both critical information and recent context while managing memory usage effectively.

**Question 3:** Why are certain tools marked as non-cacheable in the optimization system?  
A) They require special permissions  
B) They consume too much memory  
C) They have side effects or time-dependent results ✅  
D) They execute too slowly  

**Explanation:** Tools like "web_search", "current_time", "random_generator", and "file_write" are non-cacheable because they either have side effects (modify external state) or produce time-dependent results that would be stale if cached. Caching these would provide incorrect or outdated information.

**Question 4:** What technique does the context compression use to fit within size limits?  
A) Compresses text using algorithms  
B) Weights importance (70%) higher than recency (30%) when sorting ✅  
C) Removes all older messages completely  
D) Truncates all messages to the same length  

**Explanation:** The `get_compressed_context` method uses a weighted sorting algorithm where importance_score has 70% weight and recency_score has 30% weight. This ensures critical information is prioritized while still valuing recent context, then packs entries until the size limit is reached.

**Question 5:** What does the performance monitoring system track to optimize agent responses?  
A) Only response times  
B) Memory usage exclusively  
C) Response times, percentiles, cache hit rates, and target achievement ✅  
D) Just error rates and failures  

**Explanation:** The performance monitoring system tracks comprehensive metrics including average/min/max response times, percentiles (p50, p90, p95), cache entries count, target achievement rates, and the number of responses under the target time. This comprehensive data enables informed optimization decisions and automatic performance tuning.

---

## 🧭 Navigation

**Back to Test:** [Session 1 Test Questions →](Session1_ModuleA_Advanced_Agent_Patterns.md#multiple-choice-test-session-1)

---
