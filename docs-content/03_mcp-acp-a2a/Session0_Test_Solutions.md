# Session 0: Introduction to MCP, ACP, and A2A - Test Solutions

## 📝 Multiple Choice Test - Answer Key

**Question 1:** What is the primary purpose of the Model Context Protocol (MCP)?  

A) To enable direct communication between AI agents  
B) To manage agent discovery across organizations  
C) To standardize how LLMs interact with external data sources and tools ✅  
D) To provide a framework for building AI agents  

**Explanation:** MCP is designed to be the universal translator that makes enterprise APIs tool-agnostic and LLM-friendly. It standardizes the way Large Language Models access and interact with external data sources, databases, and tools, solving the problem of complex API integration.

---

**Question 2:** Which protocol is designed for local-first agent coordination with minimal overhead?  

A) A2A (Agent-to-Agent)  
B) MCP (Model Context Protocol)  
C) ADK (Agent Development Kit)  
D) ACP (Agent Communication Protocol) ✅  

**Explanation:** ACP is specifically designed for local-first agent coordination, enabling agents to discover and communicate within the same runtime, edge device, or local network—even without internet connectivity.

---

**Question 3:** How do agents discover each other in the A2A protocol?  

A) Through manual configuration files  
B) Using centralized agent registries only  
C) Via `.well-known/agent.json` files and discovery services ✅  
D) Through direct IP address connections  

**Explanation:** A2A uses a standardized discovery mechanism where agents advertise their capabilities through `.well-known/agent.json` files and register with discovery services to enable other agents to find and connect with them.

---

**Question 4:** What is the primary function of MCP Inspector?  

A) To deploy MCP servers to production  
B) To test, debug, and validate MCP servers ✅  
C) To create new MCP protocols  
D) To monitor agent-to-agent communication  

**Explanation:** MCP Inspector is a developer tool (like Postman for MCP) that provides an interactive interface to explore MCP server capabilities, test tools, debug issues, and validate that servers follow the protocol correctly.

---

**Question 5:** When should you use A2A protocol instead of MCP?  

A) When you need to access local databases  
B) When you need agents to communicate across organizational boundaries ✅  
C) When you need to expose tools to LLMs  
D) When you need to manage prompt templates  

**Explanation:** A2A is specifically designed for agent-to-agent communication across organizational and technical boundaries. MCP is for LLM-to-external-system communication, while A2A enables agents to discover and collaborate with each other.

---

**Question 6:** What transport mechanism does MCP typically use for communication?  

A) HTTP REST only  
B) WebSocket only  
C) stdio (standard input/output) and other transports ✅  
D) gRPC only  

**Explanation:** MCP supports multiple transport mechanisms including stdio (standard input/output), HTTP, WebSocket, and others. The stdio transport is commonly used for local MCP server communication.

---

**Question 7:** In ACP, how do agents discover each other in offline environments?  

A) Through cloud-based registries only  
B) Using local runtime discovery and embedded metadata ✅  
C) They cannot discover each other offline  
D) Through manual configuration files  

**Explanation:** ACP enables agents to discover each other using local runtime discovery mechanisms and embedded metadata, allowing them to coordinate even in offline environments without cloud dependencies.

---

**Question 8:** Which of the following is NOT a key problem that A2A solves?  

A) Model training optimization ✅  
B) Cross-organization collaboration  
C) Agent discovery  
D) Communication standards  

**Explanation:** A2A focuses on agent communication and interoperability problems: agent discovery, communication standards, and cross-organization collaboration. Model training optimization is not within A2A's scope—it's about agent communication, not model optimization.

---

**Question 9:** What is the recommended development path for mastering these protocols?  

A) Learn all three simultaneously  
B) Start with ACP, then MCP, then A2A  
C) Start with MCP, then ACP, then A2A ✅  
D) Start with A2A, then ACP, then MCP  

**Explanation:** The curriculum is structured to start with MCP (Sessions 1-5) to understand how agents interact with external systems, then ACP for local agent coordination, and finally A2A (Sessions 7-9) for multi-agent communication—building from foundational concepts to complex multi-agent systems.

---

**Question 10:** Which major companies adopted MCP in 2024-2025?  

A) Only Anthropic and small startups  
B) Microsoft, Google, OpenAI, and major tech leaders ✅  
C) Primarily academic institutions  
D) Only cloud service providers  

**Explanation:** MCP has seen widespread adoption by major technology companies including Microsoft, Google, OpenAI, and other industry leaders, establishing it as the de facto standard for LLM-to-external-system communication in enterprise environments.

---

## Scoring Guide

- **9-10 correct**: Excellent understanding of MCP, ACP, and A2A concepts  
- **7-8 correct**: Good grasp of the fundamentals, review specific areas where questions were missed  
- **5-6 correct**: Basic understanding present, recommend reviewing the session content before proceeding  
- **Below 5**: Recommend thoroughly reviewing Session 0 content before continuing to Session 1  

## Key Concepts Review

If you missed questions in these areas, review the corresponding sections:

### MCP Concepts (Questions 1, 4, 6, 10):  
- Review "What is MCP?" section  
- Focus on MCP architecture components  
- Study the MCP Inspector section  

### ACP Concepts (Questions 2, 7):  
- Review "What is ACP?" section  
- Focus on local-first architecture  
- Study offline coordination capabilities  

### A2A Concepts (Questions 3, 5, 8):  
- Review "What is A2A?" section  
- Focus on agent discovery mechanisms  
- Study cross-organizational communication patterns  

### Integration and Development Path (Question 9):  
- Review "Getting Started: Your Development Path" section  
- Understand the logical progression from MCP to ACP to A2A  

---

[← Return to Session 0](Session0_Introduction_to_MCP_ACP_A2A.md)
---

## 🧭 Navigation

**Next:** [Session 1 - Basic MCP Server →](Session1_Basic_MCP_Server.md)
---
