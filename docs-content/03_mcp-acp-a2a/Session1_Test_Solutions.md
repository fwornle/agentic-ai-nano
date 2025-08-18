# Session 1: Building Your First MCP Server - Test Solutions

## 📝 Multiple Choice Test

### Question 1: MCP Problem Solving
**What is the primary purpose of the Model Context Protocol (MCP)?**

A) To standardize how LLMs interact with external data sources and tools ✅  
B) To enable direct communication between AI agents  
C) To provide a framework for building AI agents  
D) To manage agent discovery across organizations  
**Correct Answer: A) To standardize how LLMs interact with external data sources and tools**

**Explanation:** MCP solves the M×N integration problem by providing a standardized bridge between AI applications and external data sources, reducing the complexity from M×N integrations to M+N.

---

### Question 2: MCP Server Components
**Which component of MCP is responsible for exposing capabilities to clients?**

A) MCP Server ✅  
B) MCP Tools  
C) MCP Resources  
D) MCP Client  
**Correct Answer: A) MCP Server**

**Explanation:** The MCP Server exposes capabilities (tools, resources, and prompts) to clients, which then make these capabilities available to LLMs.

---

### Question 3: MCP Capabilities
**What are the three main types of capabilities that MCP servers can expose?**

A) APIs, Databases, and Files  
B) Agents, Models, and Protocols  
C) Servers, Clients, and Bridges  
D) Tools, Resources, and Prompts ✅  
**Correct Answer: D) Tools, Resources, and Prompts**

**Explanation:** MCP servers expose three core capability types: Tools (functions that can be called), Resources (data endpoints that can be queried), and Prompts (pre-configured templates).

---

### Question 4: Tool Registration
**What is the correct decorator to define an MCP tool?**

A) `@mcp.tool()` ✅  
B) `@mcp.method()`  
C) `@mcp.function()`  
D) `@mcp.action()`  
**Correct Answer: A) `@mcp.tool()`**

**Explanation:** The `@mcp.tool()` decorator registers a function as an MCP tool that can be called by AI agents, with type hints providing parameter information.

---

### Question 5: Transport Mechanism
**Which transport mechanism is used in this session's MCP server?**

A) stdio ✅  
B) WebSocket  
C) HTTP  
D) gRPC  
**Correct Answer: A) stdio**

**Explanation:** The session uses stdio (standard input/output) transport, which allows communication through standard input and output streams using JSON-RPC protocol.

---

### Question 6: Communication Protocol
**What format do MCP servers use for communication?**

A) JSON-RPC ✅  
B) GraphQL  
C) Protocol Buffers  
D) REST  
**Correct Answer: A) JSON-RPC**

**Explanation:** MCP uses JSON-RPC 2.0 protocol for all client-server communication, providing a standardized way to call methods and exchange data.

---

### Question 7: Resource Naming
**When defining a resource, what URI scheme is used in the weather server example?**

A) resource://  
B) weather:// ✅  
C) mcp://  
D) http://  
**Correct Answer: B) weather://**

**Explanation:** The weather server uses custom URI schemes like `weather://cities/available` to organize and identify different resource endpoints.

---

### Question 8: Error Handling
**What should a tool return when encountering an error?**

A) Return a dict with an "error" key ✅  
B) Return False  
C) Raise an exception  
D) Return None  
**Correct Answer: A) Return a dict with an "error" key**

**Explanation:** MCP tools should return dictionaries with an "error" key for graceful error handling, allowing clients to understand and respond to specific error conditions.

---

### Question 9: Type Hints Importance
**Why are type hints crucial in MCP tool definitions?**

A) They enable code completion  
B) They prevent runtime errors  
C) They improve performance  
D) They tell AI agents how to use the tool ✅  
**Correct Answer: D) They tell AI agents how to use the tool**

**Explanation:** Type hints provide essential metadata to AI agents, allowing them to understand parameter types, requirements, and return values for proper tool usage.

---

### Question 10: Data Validation
**What is a best practice for handling invalid city names in the weather tool?**

A) Raise an exception  
B) Return default weather for London  
C) Return error with available cities list ✅  
D) Ignore invalid inputs  
**Correct Answer: C) Return error with available cities list**

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