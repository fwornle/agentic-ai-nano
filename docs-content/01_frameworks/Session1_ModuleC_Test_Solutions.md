# Session 1 - Module C: Test Solutions

**Multiple Choice Test - Module C Solutions**

---

**Question 1:** What four pieces of information does the `ConversationMemory` dataclass track for intelligent memory management?

**Answer: D) All of the above plus embedding and other metadata**

**Explanation:** The `ConversationMemory` dataclass tracks comprehensive metadata including ID, content, timestamp, priority (from the enum), context_tags for categorization, and embedding vectors for semantic search. This rich metadata enables sophisticated memory management decisions.

---

**Question 2:** How does the semantic memory retrieval system determine relevance?

**Answer: B) Cosine similarity between query and memory embeddings**

**Explanation:** The system uses `np.dot(query_embedding, memory.embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(memory.embedding))` to calculate cosine similarity between the query's semantic embedding and stored memory embeddings. This provides semantically meaningful matches rather than simple keyword matching.

---

**Question 3:** What is the purpose of the dual storage approach with working memory and long-term storage?

**Answer: B) Balance performance with long-term retention**

**Explanation:** The dual storage approach keeps recent, frequently accessed memories in fast working memory for quick retrieval, while archiving older memories to persistent storage. This balances the need for fast performance with comprehensive long-term memory retention.

---

**Question 4:** In the state persistence system, what triggers automatic state saving?

**Answer: C) Critical state changes and periodic intervals**

**Explanation:** The state persistence system uses multiple triggers: critical state changes (like important configuration updates) trigger immediate saves, while periodic intervals ensure regular backups. This combination prevents data loss while maintaining performance.

---

**Question 5:** What determines which context layers are activated in dynamic context management?

**Answer: C) Layer scope, message content, context hints, and activation conditions**

**Explanation:** The `_should_activate_layer` method evaluates multiple factors: the layer's scope (conversation, domain, session), whether the message content matches domain keywords, provided context hints, and any custom activation conditions. This multi-factor approach ensures relevant context is activated dynamically.

---

### Return to Module
[← Back to Module C](Session1_ModuleC_Complex_State_Management.md)