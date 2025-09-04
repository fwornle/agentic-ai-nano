# Session 3: LangGraph Multi-Agent Workflows - Test Solutions

## 📝 Multiple Choice Test - Session 3

**Question 1:** What is the primary advantage of LangGraph over sequential LangChain agents?  

A) Better performance  
B) Lower cost  
C) Graph-based workflows with conditional routing and parallel execution ✅  
D) Simpler implementation  

**Explanation:** LangGraph's graph-based architecture enables sophisticated workflows with conditional routing, parallel execution, and dynamic flow control, far beyond the sequential limitations of traditional agent chains.

**Question 2:** In LangGraph, what component defines the data that flows between nodes?  

A) State (TypedDict) ✅  
B) Edges  
C) Memory  
D) Tools  

**Explanation:** State in LangGraph is defined using TypedDict, providing a structured, type-safe way to define what data flows between nodes and how it's updated throughout the workflow.

**Question 3:** What determines the flow between nodes in a LangGraph workflow?  

A) Random selection  
B) User input  
C) Sequential execution only  
D) Conditional edges and decision functions ✅  

**Explanation:** LangGraph uses conditional edges with decision functions that examine the current state and determine which node to execute next, enabling dynamic and intelligent workflow routing.

**Question 4:** How does LangGraph handle parallel agent execution?  

A) Through parallel nodes with state merging ✅  
B) It doesn't support parallel execution  
C) Through external orchestration  
D) Using threading only  

**Explanation:** LangGraph supports parallel execution through parallel nodes that can run simultaneously, with their outputs automatically merged into the shared state for downstream processing.

**Question 5:** What happens when a LangGraph node updates state?  

A) State is reset to default  
B) The entire state is replaced  
C) Previous state is archived  
D) Only specified fields are updated/merged ✅  

**Explanation:** LangGraph uses state merging where nodes only update the specific fields they return, preserving other state data and enabling incremental workflow progress.

**Question 6:** In the debate pattern, what determines when the debate ends?  

A) Fixed number of rounds  
B) User intervention  
C) Consensus score and maximum iterations ✅  
D) Random timing  

**Explanation:** The debate pattern uses a consensus scoring mechanism combined with maximum iteration limits to determine when agents have reached sufficient agreement or when the debate should terminate.

**Question 7:** What is the purpose of a decision function in conditional edges?  

A) To manage memory  
B) To handle errors  
C) To process user input  
D) To examine state and determine next node ✅  

**Explanation:** Decision functions in conditional edges examine the current workflow state and use that information to intelligently determine which node should be executed next in the graph.

**Question 8:** How does the hierarchical team pattern coordinate work?  

A) Random task assignment  
B) All agents work independently  
C) Workers communicate directly  
D) A supervisor routes tasks to specialized workers ✅  

**Explanation:** The hierarchical team pattern uses a supervisor agent that analyzes tasks, routes them to appropriate specialized worker agents, and coordinates their collaboration.

**Question 9:** What is the circuit breaker pattern used for?  

A) Stopping workflows manually  
B) Optimizing performance  
C) Managing memory usage  
D) Preventing cascade failures from unreliable services ✅  

**Explanation:** The circuit breaker pattern prevents cascade failures by monitoring service reliability and temporarily disabling calls to failing services, allowing workflows to degrade gracefully.

**Question 10:** In parallel execution, when should branches be synchronized?  

A) Only at the end of the workflow  
B) Never - they should be independent  
C) At random intervals  
D) When downstream nodes need data from multiple branches ✅  

**Explanation:** Parallel branches should be synchronized when downstream processing requires data from multiple branches, ensuring all necessary information is available before proceeding.

---

## 🧭 Navigation

**Back to Test:** [Session 3 Test Questions →](Session3_Multi_Agent_Implementation.md#multiple-choice-test-session-3)

---
