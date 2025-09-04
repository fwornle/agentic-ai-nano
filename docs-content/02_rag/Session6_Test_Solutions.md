# Session 6: Graph-Based RAG (GraphRAG) - Test Solutions

## 📝 Multiple Choice Test - Session 6

**Question 1:** What is the primary advantage of GraphRAG over traditional vector-based RAG?  
A) Faster query processing  
B) Lower computational requirements  
C) Multi-hop reasoning through explicit relationship modeling ✅  
D) Simpler system architecture  

**Explanation:** GraphRAG's key advantage is its ability to perform multi-hop reasoning by following explicit relationships in the knowledge graph. While vector search finds similar content, GraphRAG can answer complex questions like "find companies that supply Apple's automotive partners" by traversing relationship chains that connect entities through multiple hops.

**Question 2:** In knowledge graph construction, what is the purpose of entity standardization?  
A) To reduce memory usage  
B) To merge different mentions of the same entity (e.g., "Apple Inc." and "Apple") ✅  
C) To improve query speed  
D) To compress graph storage  

**Explanation:** Entity standardization (also called entity resolution or deduplication) identifies when different text mentions refer to the same real-world entity. This prevents the graph from having duplicate nodes for "Apple Inc.", "Apple Computer", and "Apple" when they all refer to the same company, ensuring accurate relationship modeling.

**Question 3:** Which graph traversal algorithm is most suitable for finding related entities within a limited number of hops?  
A) Depth-First Search (DFS)  
B) Breadth-First Search (BFS) ✅  
C) Dijkstra's algorithm  
D) A* search  

**Explanation:** BFS is ideal for finding entities within a limited number of hops because it explores all nodes at distance k before exploring nodes at distance k+1. This ensures you find all related entities within your hop limit without going deeper unnecessarily, making it perfect for controlled multi-hop exploration in RAG systems.

**Question 4:** In Code GraphRAG, what information is typically extracted from Abstract Syntax Trees (ASTs)?  
A) Only function definitions  
B) Function calls, imports, class hierarchies, and variable dependencies ✅  
C) Only variable names  
D) Just file names and sizes  

**Explanation:** Code GraphRAG extracts comprehensive structural information from ASTs including function calls (who calls whom), imports (module dependencies), class hierarchies (inheritance relationships), and variable dependencies. This creates a rich knowledge graph that captures code relationships and dependencies for intelligent code search and analysis.

**Question 5:** What is the key benefit of hybrid graph-vector search?  
A) Reduced computational cost  
B) Combining structural relationships with semantic similarity ✅  
C) Simpler implementation  
D) Faster indexing  

**Explanation:** Hybrid graph-vector search combines the structural understanding of graphs (explicit relationships) with the semantic similarity of vector search (content similarity). This allows the system to find both explicitly related entities and semantically similar content, providing more comprehensive and nuanced retrieval.

**Question 6:** When should you choose Neo4j over a simple graph data structure for GraphRAG?  
A) Always, regardless of scale  
B) When you need persistent storage and complex queries at scale ✅  
C) Only for small datasets  
D) Never, simple structures are always better  

**Explanation:** Neo4j becomes valuable when you need persistent storage (graphs that survive application restarts), complex query capabilities (Cypher queries), and scalability for large graphs. For small, in-memory graphs with simple traversal needs, simpler data structures may suffice, but production GraphRAG systems typically benefit from dedicated graph databases.

**Question 7:** What is the primary challenge in multi-hop graph traversal for RAG?  
A) Memory limitations  
B) Balancing comprehensiveness with relevance and avoiding information explosion ✅  
C) Slow database queries  
D) Complex code implementation  

**Explanation:** The key challenge is preventing information explosion while maintaining relevance. As you traverse more hops, the number of connected entities grows exponentially, but not all paths are equally relevant to the query. The system must intelligently prune paths and rank results to provide comprehensive but focused information.

**Question 8:** In production GraphRAG systems, what is the most important consideration for incremental updates?  
A) Minimizing downtime while maintaining graph consistency ✅  
B) Reducing storage costs  
C) Maximizing query speed  
D) Simplifying the codebase  

**Explanation:** In production systems, maintaining graph consistency while minimizing downtime is crucial. Updates must ensure that new entities and relationships are properly integrated without breaking existing connections, and the system should remain available for queries during updates. Inconsistent graphs can lead to incorrect reasoning and poor RAG quality.

---

## 🧭 Navigation

**Back to Test:** [Session 6 Test Questions →](Session6_Hybrid_GraphRAG_Advanced.md#multiple-choice-test-session-6)

---
