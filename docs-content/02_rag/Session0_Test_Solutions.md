# Session 0: Introduction to RAG Architecture - Test Solutions

**Question 1:** RAG System Architecture  
**What are the three main stages of a RAG system?**
A) Store, Find, Answer  
B) Index, Retrieve, Generate ✅  
C) Parse, Search, Respond  
D) Chunk, Embed, Query  

**Explanation:** The fundamental RAG architecture consists of three main stages: (1) **Index** - offline preprocessing where documents are chunked, embedded, and stored in vector databases; (2) **Retrieve** - real-time similarity search to find relevant context for user queries; (3) **Generate** - LLM synthesis of retrieved context into coherent responses. This three-stage pipeline forms the backbone of all RAG systems.

**Question 2:** Industry Applications  
**Which industry benefits from RAG-powered clinical decision support?**
A) Legal services  
B) Healthcare ✅  
C) Customer support  
D) Financial services  

**Explanation:** Healthcare leverages RAG for clinical decision support by retrieving relevant medical literature, patient data, and treatment guidelines to assist physicians with diagnosis and treatment recommendations. RAG systems help doctors access up-to-date medical knowledge and evidence-based protocols while maintaining source attribution for clinical decisions.

**Question 3:** HyDE Technology  
**What is the primary advantage of HyDE (Hypothetical Document Embeddings)?**
A) Reduces computational cost  
B) Improves query-document semantic alignment ✅  
C) Eliminates need for vector databases  
D) Simplifies system architecture  

**Explanation:** HyDE bridges the semantic gap between user queries and document content by generating hypothetical documents that would answer the query, then searching with those documents instead of the original query. This dramatically improves retrieval because hypothetical answers exist in the same semantic space as actual documents, leading to better query-document alignment.

**Question 4:** RAG Evolution Timeline  
**Which RAG evolution phase introduced self-correcting mechanisms?**
A) 2020 - RAG Foundation  
B) 2021-2022 - Enhanced Fusion  
C) 2023 - Adaptive Systems ✅  
D) 2024-2025 - Graph-Based and Agentic  

**Explanation:** The 2023 Adaptive Systems phase introduced self-correcting mechanisms through Self-RAG and Corrective RAG (CRAG) systems. These systems could evaluate their own outputs, decide when to retrieve additional information, and refine responses through multiple iterations. This marked the transition from static "retrieve-then-generate" to intelligent, self-correcting architectures.

**Question 5:** RAG vs Fine-tuning Decision  
**When should you choose RAG over fine-tuning?**
A) When the domain knowledge is static  
B) When you need frequent knowledge updates ✅  
C) When computational resources are unlimited  
D) When source attribution is not needed  

**Explanation:** RAG is superior when knowledge needs frequent updates because it can incorporate new information without expensive model retraining. Fine-tuning is better for static domain knowledge, but RAG excels when you need to add new documents, update facts, or access real-time information while maintaining source attribution and transparency.

**Question 6:** Structure-Aware Chunking  
**What is structure-aware chunking designed to solve?**
A) Reducing computational costs  
B) Preserving document meaning and context boundaries ✅  
C) Increasing chunk size limits  
D) Eliminating metadata requirements  

**Explanation:** Structure-aware chunking recognizes document structure (headings, paragraphs, tables, code blocks) to create chunks that respect natural semantic boundaries. This prevents important information from being split across chunks and preserves contextual meaning, leading to better retrieval and more coherent responses.

**Question 7:** Semantic Gap Solutions  
**Which technique bridges the semantic gap between user queries and documents?**
A) Reciprocal Rank Fusion  
B) Query expansion with synonyms  
C) HyDE (Hypothetical Document Embeddings) ✅  
D) Metadata filtering  

**Explanation:** While query expansion and fusion techniques help improve retrieval, HyDE specifically addresses the semantic gap by generating hypothetical answer documents that match the user's query intent, then using these for retrieval. This creates better alignment between queries and document embeddings in the vector space.

**Question 8:** Agentic RAG Systems  
**What is the key benefit of Agentic RAG systems?**
A) Simpler system architecture  
B) Multi-agent coordination for complex reasoning ✅  
C) Lower computational requirements  
D) Faster retrieval speed  

**Explanation:** Agentic RAG systems employ multiple specialized agents that can iteratively refine queries, self-correct responses, coordinate complex reasoning workflows, and perform multi-hop retrieval. This enables sophisticated planning, autonomous knowledge acquisition, and complex problem-solving that far exceeds simple retrieve-and-generate approaches.

**Question 9:** System Limitations  
**What is a critical limitation of RAG systems?**
A) They completely eliminate hallucinations  
B) They can introduce new types of errors while solving others ✅  
C) They only work with small knowledge bases  
D) They require constant human supervision  

**Explanation:** While RAG systems reduce hallucinations by grounding responses in retrieved context, they can introduce new error types such as retrieval failures, context contamination, or inconsistent information from multiple sources. Understanding these limitations is crucial for building robust production systems with appropriate error handling.

**Question 10:** Current Evolution Phase  
**What characterizes the "Graph-Based and Agentic" RAG phase?**
A) Simple two-stage pipelines  
B) LLM integration with existing models  
C) Multi-agent systems with knowledge graph integration ✅  
D) Basic similarity matching with cosine distance  

**Explanation:** The 2024-2025 Graph-Based and Agentic phase combines knowledge graphs for structured reasoning with multi-agent systems for autonomous coordination. This enables sophisticated workflows, graph-aware retrieval, and complex reasoning patterns that understand relationships between entities and concepts.

---

## 🧭 Navigation

**Back to Test:** [Session 0 Test Questions →](Session0_RAG_Architecture_Fundamentals.md#multiple-choice-test)

---
