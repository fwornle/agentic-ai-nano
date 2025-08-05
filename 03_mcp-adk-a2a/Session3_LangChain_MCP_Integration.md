# Session 3: LangChain MCP Integration - Building Intelligent Multi-Tool Agents

## 🎯 Learning Outcomes

By the end of this session, you will be able to:
- **Integrate** multiple MCP servers with LangChain to create powerful multi-tool agents
- **Build** ReAct agents that can reason about and use various tools dynamically
- **Implement** robust error handling and fallback strategies for production agents
- **Design** complex workflows using LangGraph for multi-step agent tasks
- **Create** conversational agents that maintain context across multiple tool interactions

## 📚 Chapter Overview

In this session, we'll bridge the gap between our MCP servers and LangChain's powerful agent framework. This integration allows us to build AI agents that can intelligently select and use multiple tools to accomplish complex tasks.

![LangChain MCP Architecture](images/langchain-mcp-architecture.png)

The diagram shows how LangChain agents can seamlessly integrate with multiple MCP servers, providing a unified interface for complex reasoning and tool execution workflows.

### Key Concepts We'll Cover:

- **LangChain MCP Adapters**: Automatic tool discovery and integration
- **ReAct Pattern**: Reasoning and Acting in iterative loops
- **Multi-Server Management**: Coordinating multiple MCP servers
- **Error Handling**: Graceful degradation when tools fail
- **LangGraph Workflows**: Complex multi-step agent processes

---

## Part 1: Environment Setup and Architecture (15 minutes)

### Understanding the Integration Challenge

When we built our MCP servers in previous sessions, they worked well independently. But real-world AI applications need to:
- Use multiple tools together (weather + file system + database)
- Make intelligent decisions about which tools to use
- Handle failures gracefully
- Maintain conversation context across tool calls

LangChain's MCP adapter solves these challenges by providing a unified interface.

### Step 1.1: Install Dependencies

Let's set up our development environment with all necessary packages:

```bash
# Create project directory
mkdir langchain-mcp-integration
cd langchain-mcp-integration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install langchain-mcp-adapters langgraph langchain-openai \
            langchain-anthropic python-dotenv colorama rich
```

**New dependencies explained:**
- `langchain-mcp-adapters`: Official LangChain integration for MCP servers
- `langgraph`: Advanced workflow and graph-based agent execution
- `langchain-openai/anthropic`: LLM providers for our agents
- `rich`: Enhanced console output for better debugging

### Step 1.2: Project Structure

We'll organize our code into logical modules for maintainability:

```
langchain-mcp-integration/
├── mcp_servers/           # Our MCP server implementations
│   ├── weather_server.py
│   ├── filesystem_server.py
│   └── database_server.py
├── agents/                # Agent implementations
│   ├── __init__.py
│   ├── basic_agent.py     # Simple single-tool agent
│   ├── multi_tool_agent.py # Multi-server ReAct agent
│   └── workflow_agent.py  # LangGraph workflow agent
├── workflows/             # LangGraph workflow definitions
│   ├── __init__.py
│   ├── research_workflow.py
│   └── data_analysis_workflow.py
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── mcp_manager.py     # MCP server management
│   └── logging_config.py  # Structured logging
├── config.py              # Configuration management
├── main.py               # Main application entry point
└── .env                  # Environment variables
```

### Step 1.3: Configuration Management

First, let's create a robust configuration system that can manage multiple MCP servers:

```python
# config.py
import os
from typing import Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""
    name: str
    command: str
    args: List[str]
    transport: str = "stdio"
    description: str = ""
    timeout: int = 30
    retry_attempts: int = 3

@dataclass 
class LLMConfig:
    """Configuration for language models."""
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60

class Config:
    """Main configuration class for LangChain MCP integration."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # LLM Configuration
    LLM = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "openai"),
        model=os.getenv("LLM_MODEL", "gpt-4"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    )
    
    # MCP Server Configurations
    MCP_SERVERS = [
        MCPServerConfig(
            name="weather",
            command="python",
            args=["mcp_servers/weather_server.py"],
            description="Weather information and forecasts"
        ),
        MCPServerConfig(
            name="filesystem", 
            command="python",
            args=["mcp_servers/filesystem_server.py"],
            description="Secure file system operations"
        ),
        MCPServerConfig(
            name="database",
            command="python", 
            args=["mcp_servers/database_server.py"],
            description="Database query and manipulation"
        )
    ]
    
    # Agent Configuration
    AGENT_CONFIG = {
        "max_iterations": int(os.getenv("MAX_ITERATIONS", "10")),
        "verbose": os.getenv("VERBOSE", "true").lower() == "true",
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.7")),
        "timeout": int(os.getenv("AGENT_TIMEOUT", "300"))  # 5 minutes
    }
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**Configuration insights:**
- Dataclasses provide type safety and easy validation
- Environment variables allow easy deployment configuration
- Timeouts and retry logic prevent hanging processes
- Structured logging helps with debugging complex agent workflows

---

## Part 2: MCP Server Management (20 minutes)

### Step 2.1: MCP Manager Utility

Before building agents, we need a robust system to manage multiple MCP servers. Let's create a manager that handles lifecycle, health checks, and error recovery:

```python
# utils/mcp_manager.py
import asyncio
import logging
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
from langchain_mcp_adapters import MCPAdapter
from config import Config, MCPServerConfig

logger = logging.getLogger(__name__)

class MCPServerManager:
    """Manages multiple MCP servers with health checking and recovery."""
    
    def __init__(self, server_configs: List[MCPServerConfig]):
        self.server_configs = {config.name: config for config in server_configs}
        self.adapters: Dict[str, MCPAdapter] = {}
        self.health_status: Dict[str, bool] = {}
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def start_all_servers(self) -> Dict[str, bool]:
        """Start all configured MCP servers."""
        results = {}
        
        for name, config in self.server_configs.items():
            try:
                logger.info(f"Starting MCP server: {name}")
                adapter = MCPAdapter(
                    command=config.command,
                    args=config.args,
                    timeout=config.timeout
                )
                
                # Test the connection
                await adapter.start()
                tools = await adapter.list_tools()
                
                self.adapters[name] = adapter
                self.health_status[name] = True
                results[name] = True
                
                logger.info(f"MCP server '{name}' started successfully with {len(tools)} tools")
                
            except Exception as e:
                logger.error(f"Failed to start MCP server '{name}': {e}")
                self.health_status[name] = False
                results[name] = False
        
        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._health_monitor())
        
        return results
    
    async def get_adapter(self, server_name: str) -> Optional[MCPAdapter]:
        """Get an adapter for a specific server, with health check."""
        if server_name not in self.adapters:
            logger.warning(f"Server '{server_name}' not found")
            return None
        
        if not self.health_status.get(server_name, False):
            logger.warning(f"Server '{server_name}' is unhealthy")
            # Try to restart the server
            await self._restart_server(server_name)
        
        return self.adapters.get(server_name)
    
    async def get_all_tools(self) -> Dict[str, List[str]]:
        """Get all available tools from all healthy servers."""
        all_tools = {}
        
        for name, adapter in self.adapters.items():
            if self.health_status.get(name, False):
                try:
                    tools = await adapter.list_tools()
                    all_tools[name] = [tool.name for tool in tools]
                except Exception as e:
                    logger.warning(f"Failed to list tools for server '{name}': {e}")
                    self.health_status[name] = False
        
        return all_tools
    
    async def _health_monitor(self):
        """Background task to monitor server health."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for name, adapter in self.adapters.items():
                    try:
                        # Simple health check - list tools
                        await asyncio.wait_for(adapter.list_tools(), timeout=5.0)
                        self.health_status[name] = True
                    except Exception as e:
                        logger.warning(f"Health check failed for server '{name}': {e}")
                        self.health_status[name] = False
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def _restart_server(self, server_name: str) -> bool:
        """Attempt to restart a failed server."""
        if server_name not in self.server_configs:
            return False
        
        try:
            logger.info(f"Attempting to restart server: {server_name}")
            
            # Clean up old adapter
            if server_name in self.adapters:
                try:
                    await self.adapters[server_name].stop()
                except:
                    pass
                del self.adapters[server_name]
            
            # Start new adapter
            config = self.server_configs[server_name]
            adapter = MCPAdapter(
                command=config.command,
                args=config.args,
                timeout=config.timeout
            )
            
            await adapter.start()
            self.adapters[server_name] = adapter
            self.health_status[server_name] = True
            
            logger.info(f"Successfully restarted server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart server '{server_name}': {e}")
            self.health_status[server_name] = False
            return False
    
    async def stop_all_servers(self):
        """Stop all MCP servers and cleanup resources."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        for name, adapter in self.adapters.items():
            try:
                logger.info(f"Stopping MCP server: {name}")
                await adapter.stop()
            except Exception as e:
                logger.warning(f"Error stopping server '{name}': {e}")
        
        self.adapters.clear()
        self.health_status.clear()
    
    @asynccontextmanager
    async def managed_servers(self):
        """Context manager for automatic server lifecycle management."""
        try:
            results = await self.start_all_servers()
            healthy_count = sum(results.values())
            total_count = len(results)
            
            logger.info(f"Started {healthy_count}/{total_count} MCP servers")
            
            if healthy_count == 0:
                raise RuntimeError("No MCP servers started successfully")
            
            yield self
            
        finally:
            await self.stop_all_servers()
```

**Key features of our MCP manager:**
- **Health Monitoring**: Continuous health checks with automatic restart
- **Error Recovery**: Graceful handling of server failures
- **Context Management**: Automatic cleanup of resources
- **Logging**: Comprehensive logging for debugging
- **Async Support**: Non-blocking operations for better performance

### Step 2.2: Creating Simplified MCP Servers

Let's create lightweight versions of our MCP servers for this integration:

```python
# mcp_servers/weather_server.py
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, List

mcp = FastMCP("Weather Server")

# Simulated weather data
WEATHER_DATA = {
    "London": {"temp": 15, "condition": "Cloudy", "humidity": 75},
    "New York": {"temp": 22, "condition": "Sunny", "humidity": 60},
    "Tokyo": {"temp": 18, "condition": "Rainy", "humidity": 85},
    "Sydney": {"temp": 25, "condition": "Clear", "humidity": 55},
}

@mcp.tool()
def get_current_weather(city: str, units: str = "celsius") -> Dict:
    """Get current weather for a city."""
    if city not in WEATHER_DATA:
        return {"error": f"Weather data not available for {city}"}
    
    data = WEATHER_DATA[city].copy()
    if units == "fahrenheit":
        data["temp"] = (data["temp"] * 9/5) + 32
        data["units"] = "°F"
    else:
        data["units"] = "°C"
    
    data["city"] = city
    data["timestamp"] = datetime.now().isoformat()
    return data

@mcp.tool()
def get_weather_forecast(city: str, days: int = 3) -> List[Dict]:
    """Get weather forecast for multiple days."""
    if days < 1 or days > 7:
        return [{"error": "Days must be between 1 and 7"}]
    
    if city not in WEATHER_DATA:
        return [{"error": f"Forecast not available for {city}"}]
    
    base_temp = WEATHER_DATA[city]["temp"]
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]
    
    forecast = []
    for i in range(days):
        forecast.append({
            "day": i + 1,
            "city": city,
            "high": base_temp + (i * 2),
            "low": base_temp - 5 + i,
            "condition": conditions[i % len(conditions)],
            "precipitation_chance": (i * 10) % 80
        })
    
    return forecast

if __name__ == "__main__":
    mcp.run()
```

---

## Part 3: Building ReAct Agents (25 minutes)

### Step 3.1: Basic Single-Tool Agent

Let's start with a simple agent that uses one MCP server to understand the integration pattern:

```python
# agents/basic_agent.py
import asyncio
import logging
from typing import Optional
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool

from utils.mcp_manager import MCPServerManager
from config import Config

logger = logging.getLogger(__name__)

class BasicMCPAgent:
    """A basic ReAct agent that uses a single MCP server."""
    
    def __init__(self, server_name: str, mcp_manager: MCPServerManager):
        self.server_name = server_name
        self.mcp_manager = mcp_manager
        self.llm = None
        self.agent_executor = None
    
    async def initialize(self) -> bool:
        """Initialize the agent with LLM and tools."""
        try:
            # Initialize LLM
            self.llm = ChatOpenAI(
                model=Config.LLM.model,
                temperature=Config.LLM.temperature,
                api_key=Config.OPENAI_API_KEY
            )
            
            # Get MCP adapter and tools
            adapter = await self.mcp_manager.get_adapter(self.server_name)
            if not adapter:
                logger.error(f"Failed to get adapter for server: {self.server_name}")
                return False
            
            # Convert MCP tools to LangChain tools
            mcp_tools = await adapter.list_tools()
            langchain_tools = []
            
            for mcp_tool in mcp_tools:
                # Create a LangChain tool wrapper
                async def tool_wrapper(tool_input: str, tool_name=mcp_tool.name):
                    """Wrapper to call MCP tool from LangChain."""
                    try:
                        result = await adapter.call_tool(tool_name, {"input": tool_input})
                        return str(result)
                    except Exception as e:
                        return f"Error calling tool {tool_name}: {str(e)}"
                
                langchain_tool = Tool(
                    name=mcp_tool.name,
                    description=mcp_tool.description or f"Tool from {self.server_name} server",
                    func=lambda x, tn=mcp_tool.name: asyncio.create_task(tool_wrapper(x, tn))
                )
                langchain_tools.append(langchain_tool)
            
            # Create ReAct agent
            react_prompt = PromptTemplate.from_template("""
You are a helpful AI assistant with access to external tools.

Available tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}
""")
            
            agent = create_react_agent(
                llm=self.llm,
                tools=langchain_tools,
                prompt=react_prompt
            )
            
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=langchain_tools,
                verbose=Config.AGENT_CONFIG["verbose"],
                max_iterations=Config.AGENT_CONFIG["max_iterations"],
                handle_parsing_errors=True
            )
            
            logger.info(f"Initialized basic agent with {len(langchain_tools)} tools from {self.server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize basic agent: {e}")
            return False
    
    async def run(self, query: str) -> str:
        """Run the agent with a query."""
        if not self.agent_executor:
            return "Agent not initialized. Call initialize() first."
        
        try:
            logger.info(f"Running agent with query: {query}")
            result = await self.agent_executor.ainvoke({"input": query})
            return result["output"]
        
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return f"I encountered an error while processing your request: {str(e)}"

# Example usage function
async def run_basic_weather_agent():
    """Example of running a basic weather agent."""
    # Initialize MCP manager
    manager = MCPServerManager(Config.MCP_SERVERS)
    
    async with manager.managed_servers():
        # Create and initialize agent
        agent = BasicMCPAgent("weather", manager)
        
        if await agent.initialize():
            # Test queries
            queries = [
                "What's the weather like in London?",
                "Can you give me a 5-day forecast for Tokyo?",
                "Compare the weather between New York and Sydney"
            ]
            
            for query in queries:
                print(f"\n🤔 Query: {query}")
                result = await agent.run(query)
                print(f"🤖 Agent: {result}")
        else:
            print("Failed to initialize agent")

if __name__ == "__main__":
    asyncio.run(run_basic_weather_agent())
```

**Key concepts in our basic agent:**
- **Tool Wrapping**: Converting MCP tools to LangChain-compatible tools
- **ReAct Pattern**: The agent reasons (Thought) then acts (Action) iteratively
- **Error Handling**: Graceful degradation when tools fail
- **Async Support**: Non-blocking execution for better performance

### Step 3.2: Multi-Tool Agent with Advanced Reasoning

Now let's build a more sophisticated agent that can use multiple MCP servers intelligently:

```python
# agents/multi_tool_agent.py
import asyncio
import logging
from typing import Dict, List, Any, Optional
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferWindowMemory

from utils.mcp_manager import MCPServerManager
from config import Config

logger = logging.getLogger(__name__)

class MultiToolMCPAgent:
    """Advanced ReAct agent that intelligently uses multiple MCP servers."""
    
    def __init__(self, mcp_manager: MCPServerManager):
        self.mcp_manager = mcp_manager
        self.llm = None
        self.agent_executor = None
        self.memory = None
        self.available_tools = {}
    
    async def initialize(self) -> bool:
        """Initialize the agent with LLM, tools, and memory."""
        try:
            # Initialize LLM with function calling
            self.llm = ChatOpenAI(
                model=Config.LLM.model,
                temperature=Config.LLM.temperature,
                api_key=Config.OPENAI_API_KEY
            )
            
            # Initialize conversation memory
            self.memory = ConversationBufferWindowMemory(
                k=10,  # Remember last 10 exchanges
                memory_key="chat_history",
                return_messages=True
            )
            
            # Collect tools from all available servers
            langchain_tools = await self._collect_all_tools()
            
            if not langchain_tools:
                logger.error("No tools available from MCP servers")
                return False
            
            # Create enhanced ReAct agent with better prompting
            react_prompt = PromptTemplate.from_template("""
You are an intelligent AI assistant with access to multiple specialized tools.
You can use weather information, file system operations, and database queries to help users.

INSTRUCTIONS:
1. Analyze the user's request carefully
2. Identify which tools might be helpful
3. Use tools in logical sequence
4. Provide comprehensive, helpful responses
5. If a tool fails, try alternative approaches

Available tools:
{tools}

CONVERSATION HISTORY:
{chat_history}

Use this format for your reasoning:

Question: {input}
Thought: Let me analyze what the user needs and which tools I should use
Action: [choose from {tool_names}]
Action Input: [provide the appropriate input]
Observation: [result from the tool]
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: Now I have enough information to provide a comprehensive answer
Final Answer: [provide detailed, helpful response]

Question: {input}
{agent_scratchpad}
""")
            
            agent = create_react_agent(
                llm=self.llm,
                tools=langchain_tools,
                prompt=react_prompt
            )
            
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=langchain_tools,
                memory=self.memory,
                verbose=Config.AGENT_CONFIG["verbose"],
                max_iterations=Config.AGENT_CONFIG["max_iterations"],
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
            
            tool_count = len(langchain_tools)
            server_count = len(self.available_tools)
            logger.info(f"Initialized multi-tool agent with {tool_count} tools from {server_count} servers")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize multi-tool agent: {e}")
            return False
    
    async def _collect_all_tools(self) -> List[Tool]:
        """Collect and wrap tools from all available MCP servers."""
        langchain_tools = []
        
        # Get all available tools from all servers
        all_tools = await self.mcp_manager.get_all_tools()
        
        for server_name, tool_names in all_tools.items():
            adapter = await self.mcp_manager.get_adapter(server_name)
            if not adapter:
                continue
            
            # Get detailed tool information
            mcp_tools = await adapter.list_tools()
            self.available_tools[server_name] = mcp_tools
            
            for mcp_tool in mcp_tools:
                # Create async wrapper for each tool
                async def create_tool_wrapper(server_name, tool_name):
                    async def tool_wrapper(tool_input: str):
                        try:
                            adapter = await self.mcp_manager.get_adapter(server_name)
                            if not adapter:
                                return f"Server {server_name} is not available"
                            
                            # Parse input if it's JSON-like
                            try:
                                import json
                                if tool_input.strip().startswith('{'):
                                    tool_args = json.loads(tool_input)
                                else:
                                    tool_args = {"input": tool_input}
                            except:
                                tool_args = {"input": tool_input}
                            
                            result = await adapter.call_tool(tool_name, tool_args)
                            return str(result)
                            
                        except Exception as e:
                            logger.warning(f"Tool {tool_name} failed: {e}")
                            return f"Error using {tool_name}: {str(e)}"
                    
                    return tool_wrapper
                
                # Create the wrapper
                wrapper = await create_tool_wrapper(server_name, mcp_tool.name)
                
                # Enhanced tool description with server context
                enhanced_description = f"""
{mcp_tool.description or f'Tool from {server_name} server'}

Server: {server_name}
Tool: {mcp_tool.name}
Use this tool when you need to: {self._get_tool_use_case(server_name, mcp_tool.name)}
""".strip()
                
                langchain_tool = Tool(
                    name=f"{server_name}_{mcp_tool.name}",
                    description=enhanced_description,
                    func=lambda x, w=wrapper: asyncio.create_task(w(x))
                )
                langchain_tools.append(langchain_tool)
        
        return langchain_tools
    
    def _get_tool_use_case(self, server_name: str, tool_name: str) -> str:
        """Provide contextual use case descriptions for tools."""
        use_cases = {
            "weather": {
                "get_current_weather": "get current weather conditions for a specific city",
                "get_weather_forecast": "get multi-day weather predictions for planning"
            },
            "filesystem": {
                "read_file": "read the contents of text files",
                "write_file": "create or update files with content", 
                "list_directory": "see what files and folders exist in a directory",
                "search_files": "find files by name or search content within files"
            },
            "database": {
                "query_database": "retrieve information from the database",
                "insert_record": "add new data to the database",
                "update_record": "modify existing database records"
            }
        }
        
        return use_cases.get(server_name, {}).get(tool_name, f"perform {tool_name} operations")
    
    async def run_conversation(self, query: str) -> Dict[str, Any]:
        """Run the agent and return detailed results."""
        if not self.agent_executor:
            return {
                "output": "Agent not initialized. Call initialize() first.",
                "error": "Agent not initialized"
            }
        
        try:
            logger.info(f"Processing query: {query}")
            
            result = await self.agent_executor.ainvoke({"input": query})
            
            return {
                "output": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True
            }
        
        except Exception as e:
            logger.error(f"Agent conversation failed: {e}")
            return {
                "output": f"I encountered an error while processing your request: {str(e)}",
                "error": str(e),
                "success": False
            }
    
    async def get_conversation_history(self) -> str:
        """Get the current conversation history."""
        if self.memory:
            return self.memory.buffer
        return "No conversation history available"
    
    def clear_memory(self):
        """Clear the conversation memory."""
        if self.memory:
            self.memory.clear()
            logger.info("Conversation memory cleared")

# Example usage with interactive conversation
async def run_interactive_agent():
    """Interactive example of the multi-tool agent."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    console = Console()
    
    # Initialize MCP manager
    manager = MCPServerManager(Config.MCP_SERVERS)
    
    async with manager.managed_servers():
        # Create and initialize agent
        agent = MultiToolMCPAgent(manager)
        
        if not await agent.initialize():
            console.print("❌ Failed to initialize agent", style="red")
            return
        
        console.print(Panel.fit(
            "🤖 Multi-Tool Agent Ready!\n"
            "I can help you with weather, files, and database operations.\n"
            "Type 'quit' to exit, 'clear' to clear memory, or 'history' to see conversation history.",
            title="Agent Initialized"
        ))
        
        while True:
            try:
                # Get user input
                query = console.input("\n💬 You: ")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                elif query.lower() == 'clear':
                    agent.clear_memory()
                    console.print("🧹 Memory cleared!", style="green")
                    continue
                elif query.lower() == 'history':
                    history = await agent.get_conversation_history()
                    console.print(Panel(history, title="Conversation History"))
                    continue
                
                # Process query
                console.print("🤔 Thinking...", style="yellow")
                result = await agent.run_conversation(query)
                
                if result["success"]:
                    # Display response
                    response_panel = Panel(
                        Markdown(result["output"]),
                        title="🤖 Agent Response",
                        border_style="green"
                    )
                    console.print(response_panel)
                    
                    # Show intermediate steps if verbose
                    if Config.AGENT_CONFIG["verbose"] and result.get("intermediate_steps"):
                        console.print("\n🔍 Reasoning steps:", style="dim")
                        for i, step in enumerate(result["intermediate_steps"], 1):
                            console.print(f"  {i}. {step}", style="dim")
                else:
                    console.print(f"❌ Error: {result['output']}", style="red")
                    
            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!", style="blue")
                break
            except Exception as e:
                console.print(f"❌ Unexpected error: {e}", style="red")

if __name__ == "__main__":
    asyncio.run(run_interactive_agent())
```

---

## Part 4: Advanced Workflows with LangGraph (20 minutes)

### Step 4.1: Creating a Research Workflow

LangGraph allows us to create complex, stateful workflows. Let's build a research workflow that combines multiple tools systematically:

```python
# workflows/research_workflow.py
import asyncio
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from dataclasses import dataclass

from utils.mcp_manager import MCPServerManager
from config import Config

@dataclass
class ResearchState:
    """State for the research workflow."""
    query: str
    messages: List[Any] 
    research_plan: str = ""
    weather_data: Dict = None
    file_data: Dict = None
    database_data: Dict = None
    final_report: str = ""
    step_count: int = 0

class ResearchWorkflow:
    """Advanced research workflow using LangGraph and multiple MCP servers."""
    
    def __init__(self, mcp_manager: MCPServerManager):
        self.mcp_manager = mcp_manager
        self.workflow = None
    
    async def build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Define the workflow graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("planner", self._planning_node)
        workflow.add_node("weather_researcher", self._weather_research_node)
        workflow.add_node("file_researcher", self._file_research_node)
        workflow.add_node("database_researcher", self._database_research_node)
        workflow.add_node("synthesizer", self._synthesis_node)
        
        # Add edges (workflow flow)
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "weather_researcher")
        workflow.add_edge("weather_researcher", "file_researcher")
        workflow.add_edge("file_researcher", "database_researcher")
        workflow.add_edge("database_researcher", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
        self.workflow = workflow.compile()
        return self.workflow
    
    async def _planning_node(self, state: ResearchState) -> ResearchState:
        """Plan the research approach based on the query."""
        # Simple planning logic - in production, use LLM for planning
        query_lower = state.query.lower()
        
        plan_elements = []
        
        if any(word in query_lower for word in ["weather", "climate", "temperature", "forecast"]):
            plan_elements.append("- Gather weather information from weather server")
        
        if any(word in query_lower for word in ["file", "document", "read", "data"]):
            plan_elements.append("- Search for relevant files and documents")
        
        if any(word in query_lower for word in ["database", "record", "history", "log"]):
            plan_elements.append("- Query database for historical information")
        
        state.research_plan = "Research Plan:\n" + "\n".join(plan_elements) if plan_elements else "General research approach"
        state.step_count += 1
        
        return state
    
    async def _weather_research_node(self, state: ResearchState) -> ResearchState:
        """Research weather-related information."""
        if "weather" not in state.query.lower():
            state.weather_data = {"skipped": True, "reason": "No weather terms in query"}
            return state
        
        try:
            adapter = await self.mcp_manager.get_adapter("weather")
            if adapter:
                # Extract potential city names (simple approach)
                cities = self._extract_cities_from_query(state.query)
                
                weather_results = {}
                for city in cities:
                    try:
                        result = await adapter.call_tool("get_current_weather", {"city": city})
                        weather_results[city] = result
                    except:
                        pass
                
                state.weather_data = weather_results if weather_results else {"error": "No weather data found"}
            else:
                state.weather_data = {"error": "Weather server not available"}
        
        except Exception as e:
            state.weather_data = {"error": str(e)}
        
        state.step_count += 1
        return state
    
    async def _file_research_node(self, state: ResearchState) -> ResearchState:
        """Research file-based information."""
        try:
            adapter = await self.mcp_manager.get_adapter("filesystem")
            if adapter:
                # Search for relevant files
                search_terms = self._extract_search_terms(state.query)
                
                file_results = {}
                for term in search_terms:
                    try:
                        # Search by filename
                        result = await adapter.call_tool("search_files", {
                            "pattern": f"*{term}*",
                            "search_type": "name"
                        })
                        if result:
                            file_results[f"files_matching_{term}"] = result
                    except:
                        pass
                
                state.file_data = file_results if file_results else {"info": "No relevant files found"}
            else:
                state.file_data = {"error": "File system server not available"}
        
        except Exception as e:
            state.file_data = {"error": str(e)}
        
        state.step_count += 1
        return state
    
    async def _database_research_node(self, state: ResearchState) -> ResearchState:
        """Research database information."""
        try:
            adapter = await self.mcp_manager.get_adapter("database")
            if adapter:
                # Simulate database queries based on the research query
                state.database_data = {
                    "info": "Database research completed",
                    "note": "Database server integration would go here"
                }
            else:
                state.database_data = {"error": "Database server not available"}
        
        except Exception as e:
            state.database_data = {"error": str(e)}
        
        state.step_count += 1
        return state
    
    async def _synthesis_node(self, state: ResearchState) -> ResearchState:
        """Synthesize all research into a final report."""
        report_sections = []
        
        # Add query and plan
        report_sections.append(f"# Research Report\n\n**Query:** {state.query}\n")
        report_sections.append(f"**Research Plan:**\n{state.research_plan}\n")
        
        # Add weather findings
        if state.weather_data and not state.weather_data.get("skipped"):
            report_sections.append("## Weather Information")
            if "error" in state.weather_data:
                report_sections.append(f"Weather research failed: {state.weather_data['error']}")
            else:
                for city, data in state.weather_data.items():
                    if isinstance(data, dict) and "temp" in data:
                        report_sections.append(f"- **{city}**: {data['temp']}{data.get('units', '°C')}, {data.get('condition', 'N/A')}")
        
        # Add file findings
        if state.file_data:
            report_sections.append("\n## File System Research")
            if "error" in state.file_data:
                report_sections.append(f"File research failed: {state.file_data['error']}")
            else:
                report_sections.append("File system data collected successfully")
        
        # Add database findings
        if state.database_data:
            report_sections.append("\n## Database Research")
            if "error" in state.database_data:
                report_sections.append(f"Database research failed: {state.database_data['error']}")
            else:
                report_sections.append("Database research completed")
        
        # Add summary
        report_sections.append(f"\n## Summary")
        report_sections.append(f"Research completed in {state.step_count} steps using multiple MCP servers.")
        
        state.final_report = "\n".join(report_sections)
        state.step_count += 1
        
        return state
    
    def _extract_cities_from_query(self, query: str) -> List[str]:
        """Extract potential city names from query (simple implementation)."""
        # In production, use NER or more sophisticated methods
        common_cities = ["London", "New York", "Tokyo", "Sydney", "Paris", "Berlin", "Moscow"]
        found_cities = []
        
        query_words = query.lower().split()
        for city in common_cities:
            if city.lower() in query.lower():
                found_cities.append(city)
        
        return found_cities or ["London"]  # Default to London
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query."""
        # Simple keyword extraction
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = query.lower().split()
        return [word for word in words if len(word) > 3 and word not in stop_words][:3]
    
    async def run_research(self, query: str) -> Dict[str, Any]:
        """Run the complete research workflow."""
        if not self.workflow:
            await self.build_workflow()
        
        # Initialize state
        initial_state = ResearchState(
            query=query,
            messages=[HumanMessage(content=query)]
        )
        
        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": True,
                "query": query,
                "report": final_state.final_report,
                "steps": final_state.step_count,
                "research_plan": final_state.research_plan
            }
        
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "report": f"Research workflow failed: {str(e)}"
            }

# Example usage
async def run_research_example():
    """Example of running the research workflow."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    console = Console()
    
    # Initialize MCP manager
    manager = MCPServerManager(Config.MCP_SERVERS)
    
    async with manager.managed_servers():
        # Create research workflow
        researcher = ResearchWorkflow(manager)
        
        # Example queries
        queries = [
            "What's the weather like in London and how does it compare to Tokyo?",
            "Find any documentation files about weather patterns",
            "Research climate data and file system information"
        ]
        
        for query in queries:
            console.print(f"\n📊 Research Query: {query}")
            console.print("🔬 Conducting research...", style="yellow")
            
            result = await researcher.run_research(query)
            
            if result["success"]:
                report_panel = Panel(
                    Markdown(result["report"]),
                    title=f"Research Report ({result['steps']} steps)",
                    border_style="green"
                )
                console.print(report_panel)
            else:
                console.print(f"❌ Research failed: {result['error']}", style="red")

if __name__ == "__main__":
    asyncio.run(run_research_example())
```

---

## 📝 Chapter Summary

Congratulations! You've mastered LangChain MCP integration and built sophisticated multi-tool AI agents. Let's review what you've accomplished:

### Key Concepts Mastered:

1. **MCP Server Management**: Built a robust manager for multiple MCP servers with health monitoring and automatic recovery
2. **Tool Integration**: Seamlessly converted MCP tools to LangChain-compatible tools with proper error handling
3. **ReAct Agents**: Created intelligent agents that reason about tool usage and execute multi-step workflows
4. **Conversation Memory**: Implemented persistent memory for context-aware conversations
5. **LangGraph Workflows**: Built complex, stateful workflows for advanced research and analysis tasks

### Your Enhanced Agent Can Now:

- ✅ **Use Multiple Tools Simultaneously**: Weather, file system, and database operations in one conversation
- ✅ **Reason Intelligently**: Understand which tools to use based on user queries
- ✅ **Handle Failures Gracefully**: Automatic recovery when tools fail or servers are unavailable
- ✅ **Maintain Context**: Remember previous interactions and build on them
- ✅ **Execute Complex Workflows**: Multi-step research processes with LangGraph
- ✅ **Provide Rich Responses**: Comprehensive answers combining multiple data sources

### Production Considerations:

- **Scalability**: The architecture supports adding new MCP servers easily
- **Reliability**: Health monitoring and automatic restart capabilities
- **Security**: Proper error handling prevents sensitive information leakage
- **Observability**: Comprehensive logging for debugging and monitoring
- **Performance**: Async operations for non-blocking execution

---

## 🧪 Testing Your Understanding

### Quick Check Questions

1. **What is the primary advantage of using LangChain MCP adapters?**
   - A) Better performance
   - B) Automatic tool discovery and integration
   - C) Reduced memory usage  
   - D) Simplified configuration

2. **In the ReAct pattern, what does the agent do after each Action?**
   - A) Plan the next action
   - B) Wait for user input
   - C) Observe the result
   - D) Generate a final answer

3. **What is the purpose of the health monitoring in MCPServerManager?**
   - A) Improve performance
   - B) Automatically restart failed servers
   - C) Monitor memory usage
   - D) Log user interactions

4. **What advantage does LangGraph provide over simple ReAct agents?**
   - A) Faster execution
   - B) Complex stateful workflows
   - C) Better error handling
   - D) Simpler configuration

5. **How does our multi-tool agent decide which tools to use?**
   - A) Random selection
   - B) Pre-configured rules
   - C) LLM reasoning about tool descriptions
   - D) User specification

### Practical Exercise

Create a travel planning agent that:
1. Gets weather information for multiple destinations
2. Searches for travel documents in the file system
3. Stores trip preferences in the database
4. Creates a comprehensive travel report

**💡 Hint:** Check the [`Session3_LangChain_MCP_Integration-solution.md`](Session3_LangChain_MCP_Integration-solution.md) file for answers and detailed explanations.

---

## Next Session Preview

In Session 4, we'll focus on **Production MCP Deployment** including:
- Docker containerization of MCP servers
- Cloud deployment strategies (AWS Lambda, Google Cloud Run)
- Load balancing and scaling
- Monitoring and observability
- CI/CD pipelines for MCP servers

### Homework

1. **Extend the multi-tool agent** to handle more complex queries requiring all three servers
2. **Build a custom workflow** using LangGraph for a specific use case
3. **Add error recovery** that tries alternative tools when the primary tool fails
4. **Implement rate limiting** to prevent overwhelming MCP servers

---

## Additional Resources

- [LangChain MCP Adapters Documentation](https://python.langchain.com/docs/integrations/providers/mcp)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)
- [ReAct Paper](https://arxiv.org/abs/2210.03629) - Original research on reasoning and acting
- [MCP Specification](https://modelcontextprotocol.io/specification) - Official protocol documentation

You've now built the foundation for production-ready AI agents that can intelligently use multiple tools. The next step is deploying these systems at scale! 🚀