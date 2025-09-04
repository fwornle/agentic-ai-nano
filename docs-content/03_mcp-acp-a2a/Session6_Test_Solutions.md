# Session 6: ACP Fundamentals - Test Solutions

## 📝 Multiple Choice Test - Session 6

**Question 1:** What is the primary purpose of the Agent Communication Protocol (ACP)?  

A) To provide internet-dependent agent communication  
B) To replace REST APIs entirely  
C) To facilitate local-first agent coordination with minimal overhead ✅  
D) To enable cloud-based agent coordination  

**Explanation:** ACP is specifically designed for local-first agent coordination that works within the same runtime, edge device, or local network without requiring internet connectivity.

**Question 2:** What is the main advantage of ACP over traditional cloud-dependent agent protocols?  

A) Higher performance  
B) Easier implementation  
C) Better security  
D) Offline capability and low latency ✅  

**Explanation:** ACP's offline capability and low latency make it ideal for edge computing and local environments where internet connectivity may be unreliable or unavailable.

**Question 3:** What information must an ACP agent capability declaration include?  

A) Only the agent ID  
B) Only the capability name  
C) Just the input parameters  
D) Name, description, input schema, and output schema ✅  

**Explanation:** Complete capability declarations include name, human-readable description, input schema for parameters, and output schema for return values to enable proper agent discovery and interaction.

**Question 4:** How do ACP agents discover each other's capabilities?  

A) Via embedded metadata and local REST endpoints ✅  
B) Through a centralized cloud registry  
C) Through manual configuration files  
D) Using UDP broadcasts only  

**Explanation:** ACP agents use embedded metadata exposed through standard REST endpoints, enabling automatic discovery without external dependencies.

**Question 5:** What communication protocol does ACP use for agent interactions?  

A) WebSocket  
B) gRPC  
C) Custom binary protocol  
D) Standard HTTP/REST ✅  

**Explanation:** ACP uses standard HTTP/REST endpoints, making it framework-agnostic and easy to implement with existing web technologies.

**Question 6:** What role does the coordinator agent play in ACP architectures?  

A) Provides security authentication  
B) Orchestrates multi-agent workflows and manages task distribution ✅  
C) Stores all data permanently  
D) Acts as a backup for other agents  

**Explanation:** The coordinator agent orchestrates multi-agent workflows by discovering available agents, distributing tasks, and managing the overall workflow execution.

**Question 7:** Why are specialized agents (like data agents and text agents) beneficial in ACP systems?  

A) They cost less to deploy  
B) They require less memory  
C) They provide focused expertise and better task delegation ✅  
D) They are faster than general-purpose agents  

**Explanation:** Specialized agents provide focused expertise in specific domains, enabling better task delegation and more efficient problem-solving through division of labor.

**Question 8:** How do agents register their services in an ACP system?  

A) Through manual configuration  
B) Using external service registries only  
C) Through database entries  
D) By exposing standardized metadata endpoints ✅  

**Explanation:** Agents register services by exposing standardized metadata endpoints that describe their capabilities, allowing for automatic service discovery.

**Question 9:** What is the purpose of the local registry in ACP systems?  

A) To store all agent data  
B) To provide internet connectivity  
C) To facilitate agent discovery and capability lookup ✅  
D) To handle authentication  

**Explanation:** The local registry serves as a central point for agent discovery and capability lookup, maintaining a directory of available agents and their services.

**Question 10:** Why is ACP designed to be framework-agnostic?  

A) To improve performance  
B) To simplify testing  
C) To enable integration with any agent implementation ✅  
D) To reduce development costs  

**Explanation:** Framework-agnostic design allows ACP to work with any agent implementation, providing flexibility and enabling integration across different agent frameworks and technologies.

---

## 🧭 Navigation

**Back to Test:** [Session 6 Test Questions →](Session6_ACP_Fundamentals.md#multiple-choice-test)

---
