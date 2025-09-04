# Session 5: RAG Evaluation & Quality Assessment - Test Solutions

## 📝 Multiple Choice Test - Session 5

**Question 1:** Which metric is most important for evaluating retrieval quality in RAG systems?  
A) Response time  
B) Recall@K (how many relevant documents are in top-K results) ✅  
C) Token count  
D) Database size  

**Explanation:** Recall@K measures how many of the truly relevant documents appear in the top-K retrieved results, which is crucial for RAG quality. If relevant documents aren't retrieved, the generation stage cannot produce accurate answers, regardless of how fast or efficient other aspects are.

**Question 2:** What does the RAGAS faithfulness metric measure?  
A) How fast the system responds  
B) How well retrieved documents match the query  
C) How factually accurate the generated response is relative to retrieved context ✅  
D) How many sources are cited  

**Explanation:** RAGAS faithfulness measures whether the generated response is factually grounded in the retrieved context. It checks for hallucinations by verifying that claims in the response can be supported by the provided context, which is critical for RAG reliability.

**Question 3:** In A/B testing for RAG systems, what is the most reliable success metric?  
A) System latency  
B) Cost per query  
C) User satisfaction and task completion rates ✅  
D) Number of retrieved documents  

**Explanation:** User satisfaction and task completion rates measure the ultimate success of a RAG system - whether it actually helps users accomplish their goals. Technical metrics like latency and cost are important but secondary to user outcomes.

**Question 4:** When should you use automated LLM-as-a-judge evaluation over human evaluation?  
A) When you need perfect accuracy  
B) When you need to evaluate at scale with consistent criteria ✅  
C) When the stakes are very high  
D) Never, human evaluation is always better  

**Explanation:** Automated LLM-as-a-judge evaluation excels at scale and consistency. While human evaluation may be more nuanced, automated evaluation can process thousands of examples consistently, making it ideal for large-scale testing and continuous monitoring.

**Question 5:** What is the primary purpose of regression testing in RAG evaluation?  
A) To test system speed  
B) To ensure new changes don't decrease quality on established benchmarks ✅  
C) To measure user satisfaction  
D) To optimize costs  

**Explanation:** Regression testing ensures that system improvements don't inadvertently harm performance on previously established benchmarks. This is crucial in RAG systems where changes to one component can have unexpected effects on overall quality.

**Question 6:** Which RAG component failure mode is hardest to detect with automated metrics?  
A) Slow retrieval speed  
B) Empty results from vector search  
C) Subtle hallucinations in generated responses ✅  
D) Database connection errors  

**Explanation:** Subtle hallucinations are the most challenging to detect because they often appear plausible and well-written, but contain factual errors or make claims not supported by the context. Automated metrics struggle with nuanced factual accuracy assessment.

**Question 7:** What is the key advantage of multi-dimensional RAG evaluation over single-metric assessment?  
A) Faster evaluation  
B) Lower computational cost  
C) Captures different failure modes that single metrics might miss ✅  
D) Easier to implement  

**Explanation:** Multi-dimensional evaluation captures the complexity of RAG systems where retrieval can be good but generation poor, or vice versa. Single metrics might miss important failure modes that only become apparent when evaluating multiple dimensions simultaneously.

**Question 8:** In production RAG monitoring, what threshold approach is most effective for quality alerts?  
A) Fixed absolute thresholds for all metrics  
B) Adaptive thresholds based on historical performance patterns ✅  
C) No thresholds, manual monitoring only  
D) Random threshold selection  

**Explanation:** Adaptive thresholds based on historical patterns account for natural variations in system performance and can detect significant deviations that indicate real problems. Fixed thresholds often produce false positives or miss gradual degradation.

---

## 🧭 Navigation

**Back to Test:** [Session 5 Test Questions →](Session5_RAG_Evaluation_Quality_Assessment.md#multiple-choice-test)

---
