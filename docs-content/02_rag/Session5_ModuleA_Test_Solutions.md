# Session 5: Advanced Evaluation Metrics - Test Solutions

## 📝 Multiple Choice Test - Session 5

**Question 1:** What is the primary advantage of BERTScore over BLEU for RAG evaluation?  

A) Better semantic similarity assessment using contextual embeddings ✅  
B) Lower memory requirements  
C) Simpler implementation  
D) Faster computation speed  

**Explanation:** BERTScore's main advantage is its use of contextual embeddings from BERT to evaluate semantic similarity rather than exact word matches. While BLEU relies on n-gram overlap and can miss semantically equivalent phrases that use different words, BERTScore captures meaning through dense vector representations. This makes it particularly valuable for RAG evaluation where responses may be semantically correct without exact lexical matches to reference texts.

**Question 2:** Why are domain-specific evaluation metrics important for RAG systems?  

A) They provide more accurate assessment of domain-relevant quality factors ✅  
B) They eliminate the need for human evaluation  
C) They simplify the evaluation process  
D) They reduce computational costs  

**Explanation:** Domain-specific evaluation metrics address the unique quality requirements of specialized fields. For example, medical RAG systems need safety checks for contraindications, legal systems require citation accuracy, and financial systems need regulatory compliance validation. Generic metrics miss these critical domain-specific quality dimensions that determine real-world system effectiveness and safety.

**Question 3:** What do attribution scores measure in RAG systems?  

A) The accuracy of individual retrieved documents  
B) The relevance ranking of search results  
C) The contribution of each retrieved document to the final response ✅  
D) The computational cost of document processing  

**Explanation:** Attribution scores quantify how much each retrieved document influenced the final RAG response using leave-one-out analysis. By measuring the quality difference when individual documents are removed, these scores provide transparency into which sources were most important for response generation. This explainability is crucial for building trust and understanding RAG decision-making processes.

**Question 4:** What is the key benefit of neural evaluation metrics over traditional metrics?  

A) Simpler configuration  
B) Ability to capture nuanced semantic relationships that traditional metrics miss ✅  
C) Lower computational requirements  
D) Faster processing speed  

**Explanation:** Neural evaluation metrics leverage deep learning models to understand semantic relationships, context, and meaning beyond surface-level text matching. Traditional metrics like ROUGE and BLEU focus on lexical overlap, while neural metrics can recognize paraphrases, synonyms, and conceptual equivalence. This makes them particularly effective for evaluating RAG systems where responses may be semantically accurate without exact word matches.

**Question 5:** In medical RAG systems, what should be the highest priority safety metric?  

A) Contraindication detection and safety assessment ✅  
B) Response generation speed  
C) Database query optimization  
D) User interface quality  

**Explanation:** In medical RAG systems, contraindication detection is the most critical safety metric because it prevents potentially dangerous drug interactions or treatment recommendations. Medical errors can have life-threatening consequences, making safety assessment the highest priority over performance metrics like speed or interface quality. This includes checking for drug allergies, interaction warnings, and treatment compatibility with patient conditions.

---

## 🧭 Navigation

**Back to Test:** [Session 5 Test Questions →](Session5_RAG_Evaluation_Quality_Assessment.md#multiple-choice-test-session-5)

---
