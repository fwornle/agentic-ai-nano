# Session 1: Building Your First MCP Server - Test Solutions

## 📝 Multiple Choice Test

### Question 1: MCP Problem Solving
**What is the primary purpose of the Model Context Protocol (MCP)?**

A) To enable direct communication between AI agents  
B) To standardize how LLMs interact with external data sources and tools ✅  
C) To provide a framework for building AI agents  
D) To manage agent discovery across organizations  

**Explanation:** MCP solves the M×N integration problem by providing a standardized bridge between AI applications and external data sources, reducing the complexity from M×N integrations to M+N.

---

### Question 2: MCP Server Components
**Which component of MCP is responsible for exposing capabilities to clients?**

A) MCP Client  
B) MCP Tools  
C) MCP Server ✅  
D) MCP Resources  

**Explanation:** The MCP Server exposes capabilities (tools, resources, and prompts) to clients, which then make these capabilities available to LLMs.

---

### Question 3: MCP Capabilities
**What are the three main types of capabilities that MCP servers can expose?**

A) Agents, Models, and Protocols  
B) Tools, Resources, and Prompts ✅  
C) Servers, Clients, and Bridges  
D) APIs, Databases, and Files  

**Explanation:** MCP servers expose three core capability types: Tools (functions that can be called), Resources (data endpoints that can be queried), and Prompts (pre-configured templates).

---

### Question 4: Tool Registration
**What is the correct decorator to define an MCP tool?**

A) `@mcp.function()`  
B) `@mcp.tool()` ✅  
C) `@mcp.method()`  
D) `@mcp.action()`  

**Explanation:** The `@mcp.tool()` decorator registers a function as an MCP tool that can be called by AI agents, with type hints providing parameter information.

---

### Question 5: Transport Mechanism
**Which transport mechanism is used in this session's MCP server?**

A) HTTP  
B) WebSocket  
C) stdio ✅  
D) gRPC  

**Explanation:** The session uses stdio (standard input/output) transport, which allows communication through standard input and output streams using JSON-RPC protocol.

---

### Question 6: Communication Protocol
**What format do MCP servers use for communication?**

A) REST  
B) GraphQL  
C) JSON-RPC ✅  
D) Protocol Buffers  

**Explanation:** MCP uses JSON-RPC 2.0 protocol for all client-server communication, providing a standardized way to call methods and exchange data.

---

### Question 7: Resource Naming
**When defining a resource, what URI scheme is used in the weather server example?**

A) http://  
B) mcp://  
C) weather:// ✅  
D) resource://  

**Explanation:** The weather server uses custom URI schemes like `weather://cities/available` to organize and identify different resource endpoints.

---

### Question 8: Error Handling
**What should a tool return when encountering an error?**

A) Raise an exception  
B) Return None  
C) Return a dict with an "error" key ✅  
D) Return False  

**Explanation:** MCP tools should return dictionaries with an "error" key for graceful error handling, allowing clients to understand and respond to specific error conditions.

---

### Question 9: Type Hints Importance
**Why are type hints crucial in MCP tool definitions?**

A) They improve performance  
B) They tell AI agents how to use the tool ✅  
C) They prevent runtime errors  
D) They enable code completion  

**Explanation:** Type hints provide essential metadata to AI agents, allowing them to understand parameter types, requirements, and return values for proper tool usage.

---

### Question 10: Data Validation
**What is a best practice for handling invalid city names in the weather tool?**

A) Ignore invalid inputs  
B) Return default weather for London  
C) Return error with available cities list ✅  
D) Raise an exception  

**Explanation:** Returning an error with helpful context (like available cities) provides informative feedback that guides users toward valid inputs while maintaining system stability.

---

## Scoring Guide

- **10 correct**: Expert level - Ready for advanced MCP server development  
- **8-9 correct**: Proficient - Strong understanding of MCP fundamentals  
- **6-7 correct**: Competent - Good grasp of core concepts  
- **4-5 correct**: Developing - Review MCP architecture and tool creation  
- **Below 4**: Beginner - Revisit session materials and practice examples  

## Key Concepts Summary

1. **MCP Architecture**: Solves M×N integration problem with standardized protocol  
2. **Server Components**: Tools (functions), Resources (data), Prompts (templates)  
3. **Tool Registration**: Use `@mcp.tool()` decorator with type hints and docstrings  
4. **JSON-RPC Protocol**: Standard communication format for MCP  
5. **Error Handling**: Return structured error dictionaries for graceful failures  

---

[Return to Session 1](Session1_Basic_MCP_Server.md)