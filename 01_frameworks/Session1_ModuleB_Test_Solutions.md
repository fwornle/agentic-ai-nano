# Session 1 - Module B: Test Solutions

**Multiple Choice Test - Module B Solutions**

---

**Question 1:** What information does the `MemoryEntry` dataclass track to enable intelligent memory management?

**Answer: B) Content, timestamp, importance_score, and size_bytes**

**Explanation:** The `MemoryEntry` dataclass tracks four essential pieces of information: the actual content, when it was created (timestamp), how important it is (importance_score), and its memory footprint (size_bytes). This comprehensive tracking enables intelligent decisions about what to keep and what to remove.

---

**Question 2:** How does the memory cleanup algorithm prioritize which entries to keep?

**Answer: C) Sorts by importance and age, keeps top 70%**

**Explanation:** The `_cleanup_memory` method sorts entries by both importance_score and timestamp, then keeps the top 70% of entries. This balanced approach preserves both critical information and recent context while managing memory usage.

---

**Question 3:** Why are certain tools marked as non-cacheable in the optimization system?

**Answer: B) They have side effects or time-dependent results**

**Explanation:** Tools like "web_search", "current_time", "random_generator", and "file_write" are non-cacheable because they either have side effects (modify external state) or produce time-dependent results that would be stale if cached. Caching these would provide incorrect or outdated information.

---

**Question 4:** What technique does the context compression use to fit within size limits?

**Answer: C) Weights importance (70%) higher than recency (30%) when sorting**

**Explanation:** The `get_compressed_context` method uses a weighted sorting algorithm where importance_score has 70% weight and recency_score has 30% weight. This ensures critical information is prioritized while still valuing recent context, then packs entries until the size limit is reached.

---

**Question 5:** What does the performance monitoring system track to optimize agent responses?

**Answer: C) Response times, percentiles, cache hit rates, and target achievement**

**Explanation:** The performance monitoring system tracks comprehensive metrics including average/min/max response times, percentiles (p50, p90, p95), cache entries count, target achievement rates, and the number of responses under the target time. This comprehensive data enables informed optimization decisions.

---

### Return to Module
[← Back to Module B](Session1_ModuleB_Performance_Optimization.md)