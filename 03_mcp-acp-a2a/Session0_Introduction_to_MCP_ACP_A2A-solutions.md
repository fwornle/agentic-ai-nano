# Session 0: Introduction to MCP, ACP, and A2A - Quiz Solutions

## Multiple Choice Quiz Answers with Explanations

### Question 1: What is the primary purpose of the Model Context Protocol (MCP)?
**Correct Answer: B) To standardize how LLMs interact with external data sources and tools**

**Explanation:** MCP is designed to be the universal translator that makes enterprise APIs tool-agnostic and LLM-friendly. It standardizes the way Large Language Models access and interact with external data sources, databases, and tools, solving the problem of complex API integration.

### Question 2: Which component of MCP is responsible for exposing capabilities to clients?
**Correct Answer: C) MCP Server**

**Explanation:** The MCP Server is the component that exposes capabilities (tools, resources, and prompts) to MCP clients. The client connects to servers to access these capabilities, but the server is what actually provides and exposes them.

### Question 3: What are the three main types of capabilities that MCP servers can expose?
**Correct Answer: B) Tools, Resources, and Prompts**

**Explanation:** MCP servers expose three types of capabilities:
- **Tools**: Functions that agents can call (e.g., database queries, API calls)
- **Resources**: Data sources that agents can read (e.g., files, databases)
- **Prompts**: Reusable prompt templates for common tasks

### Question 4: Which Google technology provides a flexible orchestration framework for developing AI agents?
**Correct Answer: C) ACP (Agent Communication Protocol)**

**Explanation:** Google's Agent Development Kit (ADK) is the flexible orchestration framework designed for developing sophisticated AI agents with built-in error handling, state management, and tool integration.

### Question 5: What is a key advantage of ADK compared to traditional AI frameworks?
**Correct Answer: B) It has built-in orchestration and error handling**

**Explanation:** ADK provides built-in orchestration engine with automatic retry and fallback mechanisms, integrated state management, and universal tool interfaces, which traditional frameworks require manual implementation for.

### Question 6: How do agents discover each other in the A2A protocol?
**Correct Answer: C) Via `.well-known/agent.json` files and discovery services**

**Explanation:** A2A uses a standardized discovery mechanism where agents advertise their capabilities through `.well-known/agent.json` files and register with discovery services to enable other agents to find and connect with them.

### Question 7: What format does A2A use for agent capability advertisement?
**Correct Answer: C) JSON capability descriptors**

**Explanation:** A2A uses JSON format for capability descriptors in the `.well-known/agent.json` files, which include agent name, version, capabilities, input schemas, and communication protocols.

### Question 8: In the travel planning example, which technology handles access to customer preferences stored in a database?
**Correct Answer: C) MCP client/server**

**Explanation:** In the example, the MCP client connects to a database MCP server to access customer preferences using standardized MCP tools, while A2A is used for external agent communication and ADK provides the overall orchestration.

### Question 9: What is the primary function of MCP Inspector?
**Correct Answer: B) To test, debug, and validate MCP servers**

**Explanation:** MCP Inspector is a developer tool (like Postman for MCP) that provides an interactive interface to explore MCP server capabilities, test tools, debug issues, and validate that servers follow the protocol correctly.

### Question 10: Which command is used to install MCP Inspector via npm?
**Correct Answer: B) `npm install -g @modelcontextprotocol/inspector`**

**Explanation:** The correct npm package name for MCP Inspector is `@modelcontextprotocol/inspector` and it should be installed globally with the `-g` flag to make it available as a command-line tool.

### Question 11: When should you use A2A protocol instead of MCP?
**Correct Answer: B) When you need agents to communicate across organizational boundaries**

**Explanation:** A2A is specifically designed for agent-to-agent communication across organizational and technical boundaries. MCP is for LLM-to-external-system communication, while A2A enables agents to discover and collaborate with each other.

### Question 12: What transport mechanism does MCP typically use for communication?
**Correct Answer: C) stdio (standard input/output) and other transports**

**Explanation:** MCP supports multiple transport mechanisms including stdio (standard input/output), HTTP, WebSocket, and others. The stdio transport is commonly used for local MCP server communication.

### Question 13: In ADK, what happens when an agent encounters an error during task execution?
**Correct Answer: B) The agent has built-in retry and fallback mechanisms**

**Explanation:** One of ADK's key advantages is its robust error recovery system with automatic retry logic and fallback mechanisms, unlike traditional frameworks that require manual error handling implementation.

### Question 14: Which of the following is NOT a key problem that A2A solves?
**Correct Answer: C) Model training optimization**

**Explanation:** A2A focuses on agent communication and interoperability problems: agent discovery, communication standards, and cross-organization collaboration. Model training optimization is not within A2A's scope - it's about agent communication, not model optimization.

### Question 15: What is the recommended development path for mastering this technology stack?
**Correct Answer: C) Start with MCP, then ADK, then A2A**

**Explanation:** The curriculum is structured to start with MCP (Sessions 1-5) to understand how agents interact with external systems, then ADK (Session 6) for agent development, and finally A2A (Sessions 7-9) for multi-agent communication - building from foundational concepts to complex multi-agent systems.

## Quiz Scoring Guide

- **13-15 correct**: Excellent understanding of MCP, ADK, and A2A concepts
- **10-12 correct**: Good grasp of the fundamentals, review specific areas where questions were missed
- **7-9 correct**: Basic understanding present, recommend reviewing the session content before proceeding
- **Below 7 correct**: Recommend thoroughly reviewing Session 0 content before continuing to Session 1

## Key Concepts Review

If you missed questions in these areas, review the corresponding sections:

**MCP Concepts (Questions 1-3, 8, 9, 10, 12):**
- Review "What is MCP?" section
- Focus on MCP architecture components
- Study the MCP Inspector section

**ADK Concepts (Questions 4, 5, 13):**
- Review "What is ADK?" section  
- Focus on ADK advantages over traditional frameworks
- Study agent orchestration patterns

**A2A Concepts (Questions 6, 7, 11, 14):**
- Review "What is A2A?" section
- Focus on agent discovery mechanisms
- Study cross-organizational communication patterns

**Integration and Development Path (Questions 15):**
- Review "Getting Started: Your Development Path" section
- Understand the logical progression from MCP to ADK to A2A