# Session 0: Introduction to MCP, ACP, and A2A - Test Solutions

## 📝 Multiple Choice Test

### Question 1: MCP Purpose
**What is the primary purpose of the Model Context Protocol (MCP)?**

A) To enable direct communication between AI agents  
B) To standardize how LLMs interact with external data sources and tools ✅  
C) To provide a framework for building AI agents  
D) To manage agent discovery across organizations  

**Explanation:** MCP is designed to be the universal translator that makes enterprise APIs tool-agnostic and LLM-friendly. It standardizes the way Large Language Models access and interact with external data sources, databases, and tools, solving the problem of complex API integration.

---

### Question 2: MCP Components
**Which component of MCP is responsible for exposing capabilities to clients?**

A) MCP Client  
B) MCP Tools  
C) MCP Server ✅  
D) MCP Resources  

**Explanation:** The MCP Server is the component that exposes capabilities (tools, resources, and prompts) to MCP clients. The client connects to servers to access these capabilities, but the server is what actually provides and exposes them.

---

### Question 3: MCP Capabilities
**What are the three main types of capabilities that MCP servers can expose?**

A) Functions, Data, and Templates  
B) Tools, Resources, and Prompts ✅  
C) APIs, Databases, and Services  
D) Commands, Files, and Scripts  

**Explanation:** MCP servers expose three types of capabilities: Tools (functions that agents can call), Resources (data sources that agents can read), and Prompts (reusable prompt templates for common tasks).

---

### Question 4: ACP Framework
**What is the primary purpose of the Agent Communication Protocol (ACP)?**

A) Cloud-based agent deployment  
B) LLM model training  
C) Local-first agent coordination ✅  
D) External API management  

**Explanation:** ACP (Agent Communication Protocol) is designed for local-first agent coordination, enabling agents to discover and communicate within the same runtime, edge device, or local network—even without internet connectivity.

---

### Question 5: ACP Advantages
**What is a key advantage of ACP compared to cloud-dependent agent communication?**

A) It requires internet connectivity  
B) It enables offline agent coordination ✅  
C) It only works with specific frameworks  
D) It requires complex setup  

**Explanation:** ACP enables agents to discover and communicate within local environments without requiring internet connectivity, making it ideal for edge deployments and offline scenarios where traditional cloud-dependent solutions would fail.

---

### Question 6: A2A Communication
**What does A2A stand for in the context of AI systems?**

A) Agent-to-API  
B) Agent-to-Agent ✅  
C) Application-to-Application  
D) API-to-API  

**Explanation:** A2A stands for Agent-to-Agent communication, enabling direct interaction between autonomous AI agents across different systems and organizations.

---

### Question 7: A2A Benefits
**What is the primary benefit of A2A communication?**

A) Faster processing  
B) Direct autonomous agent collaboration ✅  
C) Lower costs  
D) Better security  

**Explanation:** A2A enables autonomous agents to collaborate directly without human intervention, creating more efficient and scalable AI systems that can work together to solve complex problems.

---

### Question 8: Integration Architecture
**In a typical enterprise integration using all three protocols, which handles external data access?**

A) ACP  
B) A2A  
C) MCP ✅  
D) All three equally  

**Explanation:** MCP specifically handles standardized access to external data sources, APIs, and tools, while ACP manages local agent coordination and A2A enables inter-agent communication.

---

### Question 9: MCP Transport
**Which transport methods does MCP support?**

A) HTTP only  
B) WebSocket only  
C) Both HTTP and WebSocket ✅  
D) TCP only  

**Explanation:** MCP supports multiple transport methods including HTTP for request-response patterns and WebSocket for real-time, bidirectional communication.

---

### Question 10: ACP Components
**Which of the following is NOT a core component of ACP?**

A) Agent Registry  
B) REST Endpoints  
C) Local Discovery  
D) Cloud Dependencies ✅  

**Explanation:** ACP core components include Agent Registry (for local discovery), REST Endpoints (for communication), Local Discovery mechanisms, and Framework-agnostic interfaces. Cloud Dependencies are explicitly avoided since ACP is designed for local-first operation.

---

### Question 11: Enterprise Use Case
**Which scenario best demonstrates the power of combining MCP, ACP, and A2A?**

A) A single agent answering questions  
B) Multiple agents coordinating across departments with external data access ✅  
C) Simple API calls  
D) File processing only  

**Explanation:** The combination shines in complex enterprise scenarios where multiple specialized agents need to coordinate (A2A), access various external systems (MCP), while being coordinated locally (ACP).

---

### Question 12: Development Strategy
**What is the recommended approach for learning these three protocols?**

A) Start with the most complex  
B) Learn all simultaneously  
C) Start with MCP, then build up to ACP and A2A ✅  
D) Start with A2A first  

**Explanation:** Starting with MCP provides the foundation for external integrations, then ACP for local agent coordination, and finally A2A for multi-agent communication builds knowledge progressively.

---

### Question 13: MCP Inspector Tool
**What is the primary purpose of the MCP Inspector?**

A) Code debugging  
B) Testing and validating MCP server implementations ✅  
C) Performance monitoring  
D) Security scanning  

**Explanation:** MCP Inspector provides a graphical interface for testing MCP servers, validating tool implementations, and debugging protocol interactions before production deployment.

---

### Question 14: A2A Problem Solving
**Which of the following is NOT a key problem that A2A solves?**

A) Agent discovery  
B) Communication standards  
C) Model training optimization ✅  
D) Cross-organization collaboration  

**Explanation:** A2A focuses on agent discovery, standardized communication protocols, and enabling collaboration across organizations. Model training optimization is handled by other technologies and frameworks.

---

### Question 15: Learning Path
**What is the recommended development path for mastering these protocols?**

A) Start with A2A, then ACP, then MCP  
B) Start with ACP, then MCP, then A2A  
C) Start with MCP, then ACP, then A2A ✅  
D) Learn all three simultaneously  

**Explanation:** The progressive path from MCP (external integrations) to ACP (local agent coordination) to A2A (multi-agent communication) builds foundational knowledge before advancing to complex multi-agent systems.

---

## Scoring Guide

- **13-15 correct**: Expert level - Ready for advanced multi-protocol development
- **10-12 correct**: Proficient - Strong understanding of protocol fundamentals
- **7-9 correct**: Competent - Good grasp of core concepts
- **4-6 correct**: Developing - Review integration and architecture sections
- **Below 4**: Beginner - Revisit session materials and examples

## Key Concepts Summary

1. **MCP**: Standardizes LLM access to external data sources and tools
2. **ACP**: Provides local-first agent coordination and discovery framework
3. **A2A**: Enables direct autonomous agent-to-agent communication
4. **Integration**: All three protocols work together for enterprise AI systems
5. **Development Path**: Progress from MCP foundations through ACP to A2A coordination

---

[Return to Session 0](Session0_Introduction_to_MCP_ACP_A2A.md)