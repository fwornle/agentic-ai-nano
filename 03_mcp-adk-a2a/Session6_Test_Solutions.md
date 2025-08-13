# Session 6: ACP Fundamentals - Test Solutions

## 📝 Multiple Choice Test

### Question 1: ACP Purpose
**What is the primary purpose of the Agent Communication Protocol (ACP)?**

A) To enable cloud-based agent coordination  
B) To facilitate local-first agent coordination with minimal overhead ✅  
C) To replace REST APIs entirely  
D) To provide internet-dependent agent communication  

**Explanation:** ACP is specifically designed for local-first agent coordination that works within the same runtime, edge device, or local network without requiring internet connectivity.

---

### Question 2: ACP Advantage
**What is the main advantage of ACP over traditional cloud-dependent agent protocols?**

A) Better security  
B) Higher performance  
C) Offline capability and low latency ✅  
D) Easier implementation  

**Explanation:** ACP's offline capability and low latency make it ideal for edge computing and local environments where internet connectivity may be unreliable or unavailable.

---

### Question 3: Agent Capabilities
**What information must an ACP agent capability declaration include?**

A) Only the capability name  
B) Name, description, input schema, and output schema ✅  
C) Just the input parameters  
D) Only the agent ID  

**Explanation:** Complete capability declarations include name, human-readable description, input schema for parameters, and output schema for return values to enable proper agent discovery and interaction.

---

### Question 4: Agent Discovery
**How do ACP agents discover each other's capabilities?**

A) Through a centralized cloud registry  
B) Via embedded metadata and local REST endpoints ✅  
C) Using UDP broadcasts only  
D) Through manual configuration files  

**Explanation:** ACP agents use embedded metadata exposed through standard REST endpoints, enabling automatic discovery without external dependencies.

---

### Question 5: Communication Protocol
**What communication protocol does ACP use for agent interactions?**

A) WebSocket  
B) gRPC  
C) Standard HTTP/REST ✅  
D) Custom binary protocol  

**Explanation:** ACP uses standard HTTP/REST endpoints, making it framework-agnostic and easy to implement with existing web technologies.

---

### Question 6: Coordinator Pattern
**What role does the coordinator agent play in ACP architectures?**

A) Stores all data permanently  
B) Orchestrates multi-agent workflows and manages task distribution ✅  
C) Provides security authentication  
D) Acts as a backup for other agents  

**Explanation:** The coordinator agent orchestrates multi-agent workflows by discovering available agents, distributing tasks, and managing the overall workflow execution.

---

### Question 7: Agent Specialization
**Why are specialized agents (like data agents and text agents) beneficial in ACP systems?**

A) They require less memory  
B) They provide focused expertise and better task delegation ✅  
C) They are faster than general-purpose agents  
D) They cost less to deploy  

**Explanation:** Specialized agents provide focused expertise in specific domains, enabling better task delegation and more efficient problem-solving through division of labor.

---

### Question 8: Service Registration
**How do agents register their services in an ACP system?**

A) Through manual configuration  
B) By exposing standardized metadata endpoints ✅  
C) Using external service registries only  
D) Through database entries  

**Explanation:** Agents register services by exposing standardized metadata endpoints that describe their capabilities, allowing for automatic service discovery.

---

### Question 9: Local Registry
**What is the purpose of the local registry in ACP systems?**

A) To store all agent data  
B) To facilitate agent discovery and capability lookup ✅  
C) To provide internet connectivity  
D) To handle authentication  

**Explanation:** The local registry serves as a central point for agent discovery and capability lookup, maintaining a directory of available agents and their services.

---

### Question 10: Framework Agnostic Design
**Why is ACP designed to be framework-agnostic?**

A) To reduce development costs  
B) To enable integration with any agent implementation ✅  
C) To improve performance  
D) To simplify testing  

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