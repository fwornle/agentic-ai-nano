# ⚙️ Session 3 Advanced: Enterprise Agent Patterns

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths
> Time Investment: 2-3 hours
> Outcome: Master production deployment and advanced error handling patterns

## Advanced Learning Outcomes

After completing this module, you will master:

- Implementing production-ready error handling and recovery mechanisms  
- Building scalable multi-tool coordination patterns for enterprise environments  
- Designing health monitoring and observability systems for MCP integrations  
- Creating advanced agent architectures for high-throughput applications  

## Advanced Multi-Tool Coordination

### The Art of Intelligent Tool Selection

Production agents must make sophisticated decisions about which tools to use based on user queries. This isn't random selection - it's intelligent analysis that considers context, capabilities, and optimal execution paths.

### The Agent's Decision-Making Process

Here's how sophisticated agents analyze and plan their tool usage:

#### 1. Query Analysis: Understanding Intent

- **Parse user intent**: What is the user trying to accomplish?  
- **Extract key entities**: Cities, dates, specific requests  
- **Identify complexity level**: Simple lookup or multi-step process?  

#### 2. Tool Capability Mapping

- **Identify relevant tools**: Which tools can help with this specific task?  
- **Assess tool dependencies**: Do any tools require input from others?  
- **Plan execution sequence**: What order makes logical sense?  

#### 3. Execution Strategy

- **Handle failures gracefully**: What if a tool doesn't work as expected?  
- **Optimize for efficiency**: Can any operations run in parallel?  
- **Maintain context**: How do we preserve information between tool calls?  

### Real-World Decision Tree Example

```
User: "What's the weather in London and do I have any files about UK shipping?"

Agent reasoning process:
├── Weather query detected → Use weather tool
├── File search detected → Use filesystem tool
└── Coordination needed → Use both tools, then synthesize results
```

### Advanced MCP Server Management

```python
async def start_all_servers(self) -> Dict[str, bool]:
    """The startup orchestration - Bringing your digital workforce online."""
    results = {}

    for name, config in self.server_configs.items():
        result = await self._start_single_server(name, config)
        results[name] = result

    return results
```

This orchestration method brings all MCP servers online systematically. Notice how it continues starting other servers even if one fails - this resilient startup pattern ensures your agent gets access to whatever tools are available rather than failing completely if one MCP server is down.

```python
async def _start_single_server(self, name: str, config: MCPServerConfig) -> bool:
    """Individual server startup with comprehensive validation."""
    try:
        logger.info(f"Starting MCP server: {name}")
        adapter = MCPAdapter(
            command=config.command,
            args=config.args,
            timeout=config.timeout
        )

        # The critical handshake - Test connection and discover tools
        await adapter.start()
        tools = await adapter.list_tools()

        # Success - Store adapter and update status
        self.adapters[name] = adapter
        self.health_status[name] = True

        logger.info(f"Server '{name}' started with {len(tools)} tools")
        return True

    except Exception as e:
        logger.error(f"Failed to start server '{name}': {e}")
        self.health_status[name] = False
        return False
```

The individual server startup process creates an MCP adapter with the configured launch parameters. The timeout configuration is crucial for production deployments - it prevents the agent from hanging indefinitely if an MCP server doesn't respond during startup.

### Production-Ready Health Monitoring

```python
async def get_adapter(self, server_name: str) -> Optional[MCPAdapter]:
    """Smart adapter access with automatic health checking."""
    if server_name not in self.adapters:
        logger.warning(f"Server '{server_name}' not found")
        return None

    if not self.health_status.get(server_name, False):
        logger.warning(f"Server '{server_name}' is unhealthy")
        # The resilience factor - Attempt automatic restart
        await self._restart_server(server_name)

    return self.adapters.get(server_name)

async def _restart_server(self, name: str):
    """Automatic recovery - Attempt to restart a failed server."""
    config = self.server_configs.get(name)
    if config:
        await self._start_single_server(name, config)
```

This server management system includes features that make the difference in production LangChain-MCP environments:

- **Health monitoring**: Continuous checks with automatic restart - reliability through automation for 24/7 operations  
- **Error recovery**: Graceful handling of server failures - resilience by design for enterprise reliability  
- **Resource management**: Proper cleanup prevents memory leaks - operational sustainability in long-running deployments  
- **Observability**: Comprehensive logging for debugging - transparency for troubleshooting complex integration issues  
- **Startup validation**: Comprehensive server testing before marking as ready - prevents runtime tool failures  
- **Resilient orchestration**: Continue starting other servers when individual servers fail - maximize available capabilities  

### Building Production-Ready Multi-Tool Agents

```python
class MultiToolMCPAgent:
    """Advanced ReAct agent using multiple MCP servers - Your coordination engine."""

    def __init__(self, mcp_manager: MCPServerManager):
        self.mcp_manager = mcp_manager
        self.llm = None
        self.agent_executor = None
        self.memory = None
        self.available_tools = {}

    async def initialize(self) -> bool:
        """The comprehensive initialization - Building your multi-tool intelligence."""
        try:
            # Intelligence foundation - Initialize LLM
            self.llm = ChatOpenAI(
                model=Config.LLM.model,
                temperature=Config.LLM.temperature,
                api_key=Config.OPENAI_API_KEY
            )

            # Memory system - Initialize conversation memory
            self.memory = ConversationBufferWindowMemory(
                k=10,  # Remember last 10 exchanges
                memory_key="chat_history",
                return_messages=True
            )

            # Tool ecosystem - Collect tools from all available servers
            langchain_tools = await self._collect_all_tools()

            if not langchain_tools:
                logger.error("No tools available from MCP servers")
                return False

            # Agent creation - Create enhanced agent executor
            self.agent_executor = self._create_enhanced_agent(langchain_tools)

            tool_count = len(langchain_tools)
            server_count = len(self.available_tools)
            logger.info(f"Multi-tool agent: {tool_count} tools from {server_count} servers")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize multi-tool agent: {e}")
            return False
```

This class design embodies the separation of concerns principle. The agent doesn't manage MCP servers directly - it delegates that responsibility to the `MCPServerManager`. This makes the agent focused on coordination and reasoning, while the manager handles server lifecycle and health.

### Advanced Tool Collection and Integration

```python
async def _collect_all_tools(self) -> List[Tool]:
    """The tool aggregator - Collect tools from all available MCP servers."""
    all_tools = []

    # Discover all available servers
    for server_name in self.mcp_manager.server_configs.keys():
        try:
            adapter = await self.mcp_manager.get_adapter(server_name)
            if not adapter:
                logger.warning(f"Skipping unavailable server: {server_name}")
                continue

            # Get tools from this server
            mcp_tools = await adapter.list_tools()
            server_tools = self._create_langchain_tools(mcp_tools, adapter, server_name)

            # Track tools per server for management
            self.available_tools[server_name] = {
                "tool_count": len(server_tools),
                "tool_names": [tool.name for tool in server_tools],
                "adapter": adapter
            }

            all_tools.extend(server_tools)
            logger.info(f"Collected {len(server_tools)} tools from {server_name}")

        except Exception as e:
            logger.error(f"Failed to collect tools from {server_name}: {e}")
            continue

    return all_tools
```

This tool collection method demonstrates resilient integration patterns. It attempts to connect to all configured MCP servers but continues operating with whatever servers are available. The detailed tracking of tools per server enables intelligent debugging and health monitoring.

### Enhanced Tool Wrapping with Error Handling

```python
def _create_langchain_tools(self, mcp_tools, adapter, server_name):
    """The enhanced translation layer - Converting MCP tools with comprehensive error handling."""
    langchain_tools = []

    for mcp_tool in mcp_tools:
        # Enhanced wrapper with server context
        async def tool_wrapper(tool_input: str, tool_name=mcp_tool.name, srv_name=server_name):
            """Enhanced wrapper with retry logic and error context."""
            max_retries = 3

            for attempt in range(max_retries):
                try:
                    # Health check before tool call
                    if not self.mcp_manager.health_status.get(srv_name, False):
                        await self.mcp_manager._restart_server(srv_name)

                    result = await adapter.call_tool(tool_name, {"input": tool_input})
                    return f"[{srv_name}] {str(result)}"

                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Tool call failed (attempt {attempt + 1}), retrying: {e}")
                        await asyncio.sleep(1)  # Brief delay before retry
                        continue
                    else:
                        error_msg = f"Tool {tool_name} from {srv_name} failed after {max_retries} attempts: {str(e)}"
                        logger.error(error_msg)
                        return error_msg

        # Enhanced LangChain tool with server context
        langchain_tool = Tool(
            name=f"{server_name}_{mcp_tool.name}",
            description=f"[{server_name}] {mcp_tool.description or f'Tool from {server_name}'}",
            func=lambda x, tn=mcp_tool.name, sn=server_name: asyncio.create_task(tool_wrapper(x, tn, sn))
        )
        langchain_tools.append(langchain_tool)

    return langchain_tools
```

This enhanced tool wrapper provides several production-ready features:

- **Server context**: Tools are prefixed with server names for clarity  
- **Retry logic**: Failed tool calls are automatically retried up to 3 times  
- **Health checking**: Server health is verified before tool calls  
- **Comprehensive logging**: All failures are logged with context  
- **Graceful degradation**: Tools return error messages instead of crashing  

### Enhanced Agent Creation with Sophisticated Prompting

```python
def _create_enhanced_agent(self, langchain_tools):
    """The intelligence amplifier - Create enhanced ReAct agent with sophisticated prompting."""
    react_prompt = PromptTemplate.from_template("""
You are an intelligent AI assistant with access to multiple specialized tools across different servers.
You can use weather information, file system operations, database queries, and other tools as available.

STRATEGIC APPROACH:
1. Analyze the user's request carefully to understand their true intent
2. Identify which tools might be helpful from your available toolkit
3. Use tools in logical sequence, building on previous results
4. If a tool from one server fails, try equivalent tools from other servers
5. Provide comprehensive, helpful responses that synthesize information from multiple sources

AVAILABLE TOOL SERVERS:
{tool_servers}

TOOL COORDINATION GUIDELINES:
- Tools are prefixed with server names (e.g., weather_get_current_weather)
- If a tool fails, the error message will indicate the server and issue
- You can use tools from multiple servers to cross-validate information
- Always explain your reasoning when switching between different tool servers

Available tools: {tools}

Use this format:
Question: {input}
Thought: Let me analyze what information I need and which tools can help
Action: [tool_name_with_server_prefix]
Action Input: [input_for_tool]
Observation: [result_from_tool]
... (repeat Thought/Action/Observation as needed)
Thought: I have gathered sufficient information from multiple sources
Final Answer: [comprehensive_response_synthesizing_all_information]

Conversation history: {chat_history}
Question: {input}
{agent_scratchpad}
""")

    # Generate server summary for prompt
    tool_servers = []
    for server_name, info in self.available_tools.items():
        tool_servers.append(f"- {server_name}: {info['tool_count']} tools ({', '.join(info['tool_names'])})")

    # Create enhanced agent
    agent = create_react_agent(
        llm=self.llm,
        tools=langchain_tools,
        prompt=react_prompt.partial(tool_servers="\n".join(tool_servers))
    )

    return AgentExecutor(
        agent=agent,
        tools=langchain_tools,
        memory=self.memory,
        verbose=Config.AGENT_CONFIG["verbose"],
        max_iterations=Config.AGENT_CONFIG["max_iterations"],
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        max_execution_time=Config.AGENT_CONFIG.get("timeout", 300)
    )
```

This enhanced prompting system provides several critical advantages:

- **Server awareness**: The agent understands which servers provide which tools  
- **Failure recovery**: Clear instructions for handling tool failures and trying alternatives  
- **Cross-validation**: Encouragement to use multiple tools for verification  
- **Context synthesis**: Guidelines for combining information from multiple sources  
- **Timeout protection**: Maximum execution time prevents hanging agents  

### Advanced Agent Runtime Features

```python
async def run(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Enhanced agent execution with comprehensive monitoring and error handling."""
    if not self.agent_executor:
        return {
            "success": False,
            "error": "Agent not initialized. Call initialize() first.",
            "query": query
        }

    start_time = asyncio.get_event_loop().time()

    try:
        # Prepare enhanced input with context
        enhanced_input = {"input": query}
        if context:
            enhanced_input.update(context)

        # Execute with timeout and monitoring
        result = await asyncio.wait_for(
            self.agent_executor.ainvoke(enhanced_input),
            timeout=Config.AGENT_CONFIG.get("timeout", 300)
        )

        execution_time = asyncio.get_event_loop().time() - start_time

        return {
            "success": True,
            "query": query,
            "output": result["output"],
            "execution_time": execution_time,
            "steps": len(result.get("intermediate_steps", [])),
            "tools_used": self._extract_tools_used(result.get("intermediate_steps", []))
        }

    except asyncio.TimeoutError:
        execution_time = asyncio.get_event_loop().time() - start_time
        return {
            "success": False,
            "query": query,
            "error": f"Agent execution timed out after {execution_time:.2f} seconds",
            "execution_time": execution_time
        }

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        logger.error(f"Agent execution failed: {e}")
        return {
            "success": False,
            "query": query,
            "error": f"Agent execution error: {str(e)}",
            "execution_time": execution_time
        }

def _extract_tools_used(self, intermediate_steps) -> List[str]:
    """Extract list of tools used during execution for monitoring."""
    tools_used = []
    for step in intermediate_steps:
        if hasattr(step, 'tool') and step.tool:
            tools_used.append(step.tool)
    return list(set(tools_used))  # Remove duplicates
```

This enhanced execution method provides comprehensive monitoring and error handling essential for production environments:

- **Timeout protection**: Prevents agents from hanging indefinitely  
- **Performance monitoring**: Tracks execution time and step count  
- **Tool usage tracking**: Records which tools were used for analytics  
- **Context injection**: Allows additional context to be passed to agents  
- **Structured responses**: Consistent response format for integration  

### Key Advances Over Basic Agents

This enterprise-ready multi-tool agent represents a significant evolution from basic patterns:

- **Multi-server resilience**: Continues operating when individual servers fail - operational continuity  
- **Enhanced error handling**: Comprehensive retry logic and error context - production reliability  
- **Performance monitoring**: Detailed execution metrics and tool usage tracking - operational observability  
- **Context awareness**: Conversation memory and context injection - intelligent interaction patterns  
- **Server-aware prompting**: Agent understands its tool ecosystem - intelligent tool selection  
- **Health integration**: Automatic server health checking and recovery - self-healing architecture  

These patterns form the foundation for enterprise-grade LangChain-MCP integrations that can handle real-world complexity and operational demands.
---

**Next:** [Session 4 - Production MCP Deployment →](Session4_Production_MCP_Deployment.md)

---
