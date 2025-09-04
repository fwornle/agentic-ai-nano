# Session 1: Building Your First MCP Server - Test Solutions

## 📝 Multiple Choice Test - Session 1

**Question 1:** What are the three core capabilities that MCP servers can expose?  

A) APIs, Databases, and Services  
B) Functions, Classes, and Modules  
C) Tools, Resources, and Prompts ✅  
D) Inputs, Outputs, and Errors  

**Explanation:** MCP servers expose three types of capabilities: Tools (executable functions that can be called), Resources (data sources that can be queried), and Prompts (reusable templates for common tasks).

**Question 2:** Which decorator is used to expose a function as an MCP tool?  

A) `@tool()`  
B) `@mcp.tool()` ✅  
C) `@server.tool()`  
D) `@expose_tool()`  

**Explanation:** The `@mcp.tool()` decorator is the FastMCP framework's way to register a function as an MCP tool that can be called by AI agents.

**Question 3:** What is the primary purpose of MCP Inspector?  

A) To deploy MCP servers to production  
B) To test, debug, and validate MCP servers ✅  
C) To monitor server performance  
D) To manage server configurations  

**Explanation:** MCP Inspector is a developer tool (like Postman for MCP) that provides an interactive interface to explore MCP server capabilities, test tools, debug issues, and validate that servers follow the protocol correctly.

**Question 4:** Which transport mechanism is commonly used for local MCP server testing?  

A) HTTP  
B) WebSocket  
C) stdio (standard input/output) ✅  
D) TCP  

**Explanation:** MCP servers communicate over stdio (standard input/output) by default for local development, which allows them to work as subprocess-based tools.

**Question 5:** Why are type hints important in MCP server functions?  

A) They improve code readability only  
B) They enable automatic schema generation for AI clients ✅  
C) They are required by Python  
D) They reduce memory usage  

**Explanation:** Type hints are used by the MCP framework to automatically generate JSON schemas that describe the tool's parameters and return values to AI clients, enabling proper validation and usage.

**Question 6:** What should MCP tools return when encountering invalid input?  

A) Raise an exception  
B) Return None  
C) Return structured error messages with helpful information ✅  
D) Log the error silently  

**Explanation:** MCP tools should return structured error messages with helpful information rather than raising exceptions, which provides better error handling for clients.

**Question 7:** How do MCP resources differ from tools?  

A) Resources are executable functions, tools are data sources  
B) Resources provide read-only data access, tools are executable functions ✅  
C) Resources are faster than tools  
D) Resources require authentication, tools do not  

**Explanation:** Resources are read-only data endpoints that provide information (like file contents or database records), while tools are executable functions that can perform actions or computations.

**Question 8:** What command is used to launch MCP Inspector?  

A) `mcp-inspector`  
B) `npm start inspector`  
C) `npx @modelcontextprotocol/inspector` ✅  
D) `python -m mcp.inspector`  

**Explanation:** MCP Inspector can be launched using the `npx @modelcontextprotocol/inspector` command, which runs the inspector without requiring a global installation.

**Question 9:** Which company reported 60% faster AI integration development using MCP?  

A) Microsoft  
B) Google  
C) Block Inc. ✅  
D) OpenAI  

**Explanation:** Block Inc. reported significant development speed improvements when using MCP for their AI integrations, demonstrating the protocol's real-world benefits in enterprise environments.

**Question 10:** What is the main advantage of MCP over custom API integrations?  

A) Better performance  
B) Standardized protocol with automatic schema validation ✅  
C) Lower cost  
D) Easier to learn  

**Explanation:** MCP provides a standardized protocol that includes automatic schema validation, discovery mechanisms, and consistent error handling, reducing the complexity of custom integrations.

---

## 🧭 Navigation

**Back to Test:** [Session 1 Test Questions →](Session1_Basic_MCP_Server.md#multiple-choice-test-session-1)

---
