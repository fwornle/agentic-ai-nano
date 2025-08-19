# Session 6: ACP Fundamentals - Test Solutions

## 📝 Multiple Choice Test

### Question 1: ACP Purpose
**What is the primary purpose of the Agent Communication Protocol (ACP)?**  

A) To provide internet-dependent agent communication  
B) To replace REST APIs entirely  
C) To facilitate local-first agent coordination with minimal overhead ✅  
D) To enable cloud-based agent coordination  
**Correct Answer: C) To facilitate local-first agent coordination with minimal overhead**

**Explanation:** ACP is specifically designed for local-first agent coordination that works within the same runtime, edge device, or local network without requiring internet connectivity.

---

### Question 2: ACP Advantage
**What is the main advantage of ACP over traditional cloud-dependent agent protocols?**  

A) Higher performance  
B) Easier implementation  
C) Better security  
D) Offline capability and low latency ✅  
**Correct Answer: D) Offline capability and low latency**

**Explanation:** ACP's offline capability and low latency make it ideal for edge computing and local environments where internet connectivity may be unreliable or unavailable.

---

### Question 3: Agent Capabilities
**What information must an ACP agent capability declaration include?**  

A) Only the agent ID  
B) Only the capability name  
C) Just the input parameters  
D) Name, description, input schema, and output schema ✅  
**Correct Answer: D) Name, description, input schema, and output schema**

**Explanation:** Complete capability declarations include name, human-readable description, input schema for parameters, and output schema for return values to enable proper agent discovery and interaction.

---

### Question 4: Agent Discovery
**How do ACP agents discover each other's capabilities?**  

A) Via embedded metadata and local REST endpoints ✅  
B) Through a centralized cloud registry  
C) Through manual configuration files  
D) Using UDP broadcasts only  
**Correct Answer: A) Via embedded metadata and local REST endpoints**

**Explanation:** ACP agents use embedded metadata exposed through standard REST endpoints, enabling automatic discovery without external dependencies.

---

### Question 5: Communication Protocol
**What communication protocol does ACP use for agent interactions?**  

A) WebSocket  
B) gRPC  
C) Custom binary protocol  
D) Standard HTTP/REST ✅  
**Correct Answer: D) Standard HTTP/REST**

**Explanation:** ACP uses standard HTTP/REST endpoints, making it framework-agnostic and easy to implement with existing web technologies.

---

### Question 6: Coordinator Pattern
**What role does the coordinator agent play in ACP architectures?**  

A) Provides security authentication  
B) Orchestrates multi-agent workflows and manages task distribution ✅  
C) Stores all data permanently  
D) Acts as a backup for other agents  
**Correct Answer: B) Orchestrates multi-agent workflows and manages task distribution**

**Explanation:** The coordinator agent orchestrates multi-agent workflows by discovering available agents, distributing tasks, and managing the overall workflow execution.

---

### Question 7: Agent Specialization
**Why are specialized agents (like data agents and text agents) beneficial in ACP systems?**  

A) They cost less to deploy  
B) They require less memory  
C) They provide focused expertise and better task delegation ✅  
D) They are faster than general-purpose agents  
**Correct Answer: C) They provide focused expertise and better task delegation**

**Explanation:** Specialized agents provide focused expertise in specific domains, enabling better task delegation and more efficient problem-solving through division of labor.

---

### Question 8: Service Registration
**How do agents register their services in an ACP system?**  

A) Through manual configuration  
B) Using external service registries only  
C) Through database entries  
D) By exposing standardized metadata endpoints ✅  
**Correct Answer: D) By exposing standardized metadata endpoints**

**Explanation:** Agents register services by exposing standardized metadata endpoints that describe their capabilities, allowing for automatic service discovery.

---

### Question 9: Local Registry
**What is the purpose of the local registry in ACP systems?**  

A) To store all agent data  
B) To provide internet connectivity  
C) To facilitate agent discovery and capability lookup ✅  
D) To handle authentication  
**Correct Answer: C) To facilitate agent discovery and capability lookup**

**Explanation:** The local registry serves as a central point for agent discovery and capability lookup, maintaining a directory of available agents and their services.

---

### Question 10: Framework Agnostic Design
**Why is ACP designed to be framework-agnostic?**  

A) To improve performance  
B) To simplify testing  
C) To enable integration with any agent implementation ✅  
D) To reduce development costs  
**Correct Answer: C) To enable integration with any agent implementation**

**Explanation:** Framework-agnostic design allows ACP to work with any agent implementation, providing flexibility and enabling integration across different agent frameworks and technologies.

---

## Scoring Guide

- **10 correct**: Expert level - Ready for advanced ACP implementations  
- **8-9 correct**: Proficient - Strong understanding of local agent coordination  
- **6-7 correct**: Competent - Good grasp of ACP fundamentals  
- **4-5 correct**: Developing - Review agent discovery and coordination patterns  
- **Below 4**: Beginner - Revisit ACP principles and local-first concepts  

## Key Concepts Summary

1. **Local-First Design**: ACP enables offline-capable agent coordination  
2. **REST-Native**: Standard HTTP endpoints for framework-agnostic integration  
3. **Capability Declaration**: Complete schemas for automatic service discovery  
4. **Coordinator Pattern**: Centralized orchestration for complex workflows  
5. **Agent Specialization**: Focused expertise through division of labor  

---

[Return to Session 6](Session6_ACP_Fundamentals.md)