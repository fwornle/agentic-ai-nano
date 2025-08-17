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

## Part 1: Environment Setup and Project Structure (15 minutes)

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

### Step 1.2: Configuration Management

Real-world applications need robust configuration. Let's start with environment setup:

**Why Configuration Matters:**
- Different settings for development vs production
- Secure API key management
- Easy deployment across environments
- Type safety for configuration values

**Step 1.2.1: Environment Variables Setup**

First, create your `.env` file:

```bash
# .env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
VERBOSE=true
MAX_ITERATIONS=10
```

**Step 1.2.2: Type-Safe Configuration Classes**

Now let's examine our configuration structure:

```python
# From: [`src/session3/config.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session3/config.py)

@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""
    name: str           # Unique identifier for the server
    command: str        # Command to start the server
    args: List[str]     # Command line arguments
    transport: str = "stdio"  # Communication method
    description: str = ""     # Human-readable description
    timeout: int = 30         # Connection timeout in seconds
    retry_attempts: int = 3   # Number of retry attempts
```

**Key Benefits:**
- **Type Safety**: Prevents configuration errors
- **Documentation**: Self-documenting configuration
- **Validation**: Built-in validation through dataclasses
- **IDE Support**: Better autocomplete and error checking

**Step 1.2.3: LLM Configuration**

```python
@dataclass 
class LLMConfig:
    """Configuration for language models."""
    provider: str = "openai"      # Which LLM provider to use
    model: str = "gpt-4"          # Specific model name
    temperature: float = 0.7      # Creativity level (0-1)
    max_tokens: int = 2000        # Maximum response length
    timeout: int = 60             # Request timeout
```

**Temperature Explained:**
- **0.0**: Deterministic, focused responses
- **0.7**: Balanced creativity and accuracy
- **1.0**: Maximum creativity, less predictable

---

## Part 2: MCP Server Management System (20 minutes)

### Understanding Multi-Server Coordination

Managing multiple MCP servers introduces complexity:
- **Lifecycle Management**: Starting, stopping, restarting servers
- **Health Monitoring**: Detecting failed servers
- **Graceful Degradation**: Continuing when some servers fail
- **Resource Cleanup**: Preventing memory leaks

### Step 2.1: Server Manager Architecture

Let's build this step by step, starting with the basic structure:

**Step 2.1.1: Initialize the Manager**

```python
class MCPServerManager:
    """Manages multiple MCP servers with health checking and recovery."""
    
    def __init__(self, server_configs: List[MCPServerConfig]):
        # Store configuration for each server
        self.server_configs = {config.name: config for config in server_configs}
        
        # Active adapter instances
        self.adapters: Dict[str, MCPAdapter] = {}
        
        # Health status tracking
        self.health_status: Dict[str, bool] = {}
        
        # Background health monitoring task
        self._health_check_task: Optional[asyncio.Task] = None
```

**Design Decisions Explained:**
- **Dictionary Storage**: Fast lookup by server name
- **Separation of Concerns**: Config vs runtime state
- **Type Hints**: Better code documentation and IDE support

**Step 2.1.2: Starting Servers with Error Handling**

```python
async def start_all_servers(self) -> Dict[str, bool]:
    """Start all configured MCP servers."""
    results = {}
    
    for name, config in self.server_configs.items():
        try:
            logger.info(f"Starting MCP server: {name}")
            
            # Create adapter with configuration
            adapter = MCPAdapter(
                command=config.command,
                args=config.args,
                timeout=config.timeout
            )
            
            # Test the connection
            await adapter.start()
            tools = await adapter.list_tools()
            
            # Store successful adapter
            self.adapters[name] = adapter
            self.health_status[name] = True
            results[name] = True
            
            logger.info(f"Server '{name}' started with {len(tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to start server '{name}': {e}")
            self.health_status[name] = False
            results[name] = False
    
    return results
```

**Error Handling Strategy:**
- **Individual Failure**: One server failing doesn't stop others
- **Detailed Logging**: Clear information for debugging
- **Result Tracking**: Know which servers started successfully

**Step 2.1.3: Health Monitoring System**

Why do we need health monitoring?
- **Network Issues**: Servers can become unreachable
- **Process Crashes**: MCP servers may stop unexpectedly  
- **Resource Exhaustion**: Servers may become unresponsive
- **Automatic Recovery**: Restart failed servers automatically

```python
async def _health_monitor(self):
    """Background task to monitor server health."""
    while True:
        try:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            for name, adapter in self.adapters.items():
                try:
                    # Simple health check - list tools with timeout
                    await asyncio.wait_for(adapter.list_tools(), timeout=5.0)
                    self.health_status[name] = True
                    
                except Exception as e:
                    logger.warning(f"Health check failed for '{name}': {e}")
                    self.health_status[name] = False
                    
        except asyncio.CancelledError:
            break  # Graceful shutdown
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
```

**Health Check Design:**
- **Non-blocking**: Uses asyncio for concurrent checks
- **Timeout Protection**: Won't hang on unresponsive servers
- **Graceful Shutdown**: Handles cancellation properly

### Step 2.2: Simple Weather Server Implementation

Before building complex agents, let's create a simple MCP server to test with:

```python
# From: [`src/session3/mcp_servers/weather_server.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session3/mcp_servers/weather_server.py)

@mcp.tool()
def get_current_weather(city: str, units: str = "celsius") -> Dict:
    """Get current weather for a city."""
    
    # Input validation
    if city not in WEATHER_DATA:
        return {"error": f"Weather data not available for {city}"}
    
    # Process the data
    data = WEATHER_DATA[city].copy()
    
    # Handle unit conversion
    if units == "fahrenheit":
        data["temp"] = (data["temp"] * 9/5) + 32
        data["units"] = "°F"
    else:
        data["units"] = "°C"
    
    # Add metadata
    data["city"] = city
    data["timestamp"] = datetime.now().isoformat()
    
    return data
```

**Tool Design Principles:**
- **Input Validation**: Check parameters before processing
- **Error Handling**: Return error information instead of crashing
- **Metadata**: Include timestamps and context information
- **Flexibility**: Support multiple units/formats

---

## Part 3: Building Your First ReAct Agent (25 minutes)

### Understanding the ReAct Pattern

ReAct (Reasoning + Acting) is a powerful pattern where AI agents:
1. **Think** about what they need to do
2. **Act** using available tools
3. **Observe** the results
4. **Repeat** until the task is complete

This creates transparent, debuggable AI behavior.

### Step 3.1: Basic Agent Architecture

Let's start simple and build complexity gradually:

**Step 3.1.1: Agent Initialization**

```python
class BasicMCPAgent:
    """A basic ReAct agent that uses a single MCP server."""
    
    def __init__(self, server_name: str, mcp_manager: MCPServerManager):
        self.server_name = server_name
        self.mcp_manager = mcp_manager
        
        # These will be initialized later
        self.llm = None
        self.agent_executor = None
```

**Why Separate Initialization?**
- **Async Requirements**: LLM setup may require async operations
- **Error Handling**: Better control over initialization failures
- **Flexibility**: Can reinitialize with different settings

**Step 3.1.2: LLM Setup and Tool Conversion**

```python
async def initialize(self) -> bool:
    """Initialize the agent with LLM and tools."""
    try:
        # Create LLM instance
        self.llm = ChatOpenAI(
            model=Config.LLM.model,
            temperature=Config.LLM.temperature,
            api_key=Config.OPENAI_API_KEY
        )
        
        # Get MCP tools and convert to LangChain format
        adapter = await self.mcp_manager.get_adapter(self.server_name)
        if not adapter:
            return False
        
        langchain_tools = await self._convert_mcp_tools(adapter)
        
        # Create agent with ReAct pattern
        self.agent_executor = self._create_react_agent(langchain_tools)
        
        return True
        
    except Exception as e:
        logger.error(f"Agent initialization failed: {e}")
        return False
```

**Step 3.1.3: Tool Conversion Process**

```python
async def _convert_mcp_tools(self, adapter: MCPAdapter) -> List[Tool]:
    """Convert MCP tools to LangChain tools."""
    mcp_tools = await adapter.list_tools()
    langchain_tools = []
    
    for mcp_tool in mcp_tools:
        # Create async wrapper for each tool
        async def tool_wrapper(tool_input: str, tool_name=mcp_tool.name):
            try:
                # Call the MCP tool
                result = await adapter.call_tool(tool_name, {"input": tool_input})
                return str(result)
            except Exception as e:
                return f"Error calling tool {tool_name}: {str(e)}"
        
        # Create LangChain tool
        langchain_tool = Tool(
            name=mcp_tool.name,
            description=mcp_tool.description or f"Tool from {self.server_name}",
            func=lambda x, tn=mcp_tool.name: asyncio.create_task(tool_wrapper(x, tn))
        )
        langchain_tools.append(langchain_tool)
    
    return langchain_tools
```

**Conversion Challenges:**
- **Async Compatibility**: MCP tools are async, LangChain tools may not be
- **Error Wrapping**: Convert exceptions to returnable strings
- **Parameter Handling**: Map different parameter formats

### Step 3.2: ReAct Prompt Engineering

The ReAct prompt is crucial for agent behavior:

```python
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
```

**Prompt Design Elements:**
- **Clear Structure**: Defined format for reasoning steps
- **Available Context**: Lists available tools
- **Iterative Process**: Allows multiple reasoning cycles
- **Final Answer**: Clear conclusion point

### Step 3.3: Testing Your Agent

Let's create a simple test to see our agent in action:

```python
async def test_basic_agent():
    """Test the basic weather agent."""
    # Setup
    manager = MCPServerManager(Config.MCP_SERVERS)
    
    async with manager.managed_servers():
        agent = BasicMCPAgent("weather", manager)
        
        if await agent.initialize():
            # Test query
            query = "What's the weather like in London?"
            result = await agent.run(query)
            print(f"Query: {query}")
            print(f"Response: {result}")
        else:
            print("Failed to initialize agent")

# Run the test
asyncio.run(test_basic_agent())
```

**Expected Output:**
```
Query: What's the weather like in London?
Response: The current weather in London is 15°C and cloudy, with 75% humidity. 
The information was retrieved at 2024-01-01T10:30:00.
```

---

## Part 4: Multi-Tool Agent Development (20 minutes)

### Scaling to Multiple Tools

A single-tool agent is useful, but real applications need multiple capabilities. Let's build an agent that can use weather, file system, and database tools together.

### Step 4.1: Enhanced Agent Architecture

```python
class MultiToolMCPAgent:
    """Advanced agent that uses multiple MCP servers intelligently."""
    
    def __init__(self, mcp_manager: MCPServerManager):
        self.mcp_manager = mcp_manager
        self.llm = None
        self.agent_executor = None
        self.memory = None  # For conversation context
        self.available_tools = {}  # Track tools by server
```

**Step 4.1.1: Conversation Memory**

```python
from langchain.memory import ConversationBufferWindowMemory

# Initialize memory in the agent
self.memory = ConversationBufferWindowMemory(
    k=10,  # Remember last 10 exchanges
    memory_key="chat_history",
    return_messages=True
)
```

**Why Memory Matters:**
- **Context Awareness**: Agent remembers previous interactions
- **Follow-up Questions**: Can reference earlier parts of conversation
- **Improved UX**: More natural conversation flow

**Step 4.1.2: Collecting Tools from All Servers**

```python
async def _collect_all_tools(self) -> List[Tool]:
    """Collect tools from all available MCP servers."""
    langchain_tools = []
    
    # Get tools from all healthy servers
    all_tools = await self.mcp_manager.get_all_tools()
    
    for server_name, tool_names in all_tools.items():
        adapter = await self.mcp_manager.get_adapter(server_name)
        if not adapter:
            continue
        
        # Get detailed tool information
        mcp_tools = await adapter.list_tools()
        
        for mcp_tool in mcp_tools:
            # Create enhanced tool wrapper
            wrapper = await self._create_tool_wrapper(server_name, mcp_tool)
            langchain_tools.append(wrapper)
    
    return langchain_tools
```

**Step 4.1.3: Enhanced Tool Descriptions**

```python
def _get_enhanced_description(self, server_name: str, tool_name: str) -> str:
    """Create detailed tool descriptions for better agent decision-making."""
    
    base_descriptions = {
        "weather": {
            "get_current_weather": "Get current weather conditions for a specific city"
        },
        "filesystem": {
            "read_file": "Read contents of text files from the file system",
            "write_file": "Create or update files with new content"
        }
    }
    
    description = base_descriptions.get(server_name, {}).get(tool_name, "")
    return f"[{server_name}] {description}"
```

**Why Enhanced Descriptions Matter:**
- **Better Tool Selection**: Agent understands when to use each tool
- **Context Clarity**: Shows which server provides each capability
- **Reduced Errors**: Clearer descriptions lead to better tool usage

### Step 4.2: Advanced Prompt Engineering

Multi-tool agents need more sophisticated prompts:

```python
multi_tool_prompt = PromptTemplate.from_template("""
You are an intelligent AI assistant with access to multiple specialized tools.
You can use weather information, file operations, and database queries to help users.

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
... (repeat as needed)
Thought: Now I have enough information to provide a comprehensive answer
Final Answer: [provide detailed, helpful response]

Question: {input}
{agent_scratchpad}
""")
```

**Advanced Prompt Features:**
- **Multi-step Instructions**: Guides complex reasoning
- **Tool Coordination**: Encourages using tools together
- **Error Recovery**: Instructions for handling failures
- **Conversation Context**: Integrates memory into reasoning

### Step 4.3: Testing Multi-Tool Capabilities

```python
async def test_multi_tool_agent():
    """Test agent with multiple tool coordination."""
    manager = MCPServerManager(Config.MCP_SERVERS)
    
    async with manager.managed_servers():
        agent = MultiToolMCPAgent(manager)
        
        if await agent.initialize():
            # Complex query requiring multiple tools
            queries = [
                "What's the weather in London and New York?",
                "Get weather for Tokyo and save it to a file called tokyo_weather.txt",
                "Compare weather between three cities and summarize the differences"
            ]
            
            for query in queries:
                print(f"\n🤔 Query: {query}")
                result = await agent.run_conversation(query)
                print(f"🤖 Response: {result['output']}")
```

**Expected Multi-Tool Behavior:**
1. **Query Analysis**: Agent identifies need for weather data from multiple cities
2. **Tool Coordination**: Uses weather tool multiple times for different cities
3. **Data Processing**: Combines results intelligently
4. **Response Generation**: Provides comprehensive comparison

---

## Part 5: Introduction to LangGraph Workflows (15 minutes)

### Understanding Workflow Complexity

Sometimes agents need more structured approaches than ReAct provides. LangGraph enables:
- **Predefined Workflows**: Step-by-step processes
- **State Management**: Tracking data through multiple steps
- **Conditional Logic**: Different paths based on results
- **Error Handling**: Retry and fallback strategies

### Step 5.1: Simple Research Workflow

Let's create a workflow that combines multiple research steps:

**Step 5.1.1: Workflow State Definition**

```python
from dataclasses import dataclass

@dataclass
class ResearchState:
    """State for the research workflow."""
    query: str                    # Original user query
    messages: List[Any]           # Conversation messages
    research_plan: str = ""       # Generated research plan
    weather_data: Dict = None     # Weather information
    file_data: Dict = None        # File system results
    database_data: Dict = None    # Database query results
    final_report: str = ""        # Generated report
    step_count: int = 0           # Progress tracking
```

**Step 5.1.2: Planning Node**

```python
async def _planning_node(self, state: ResearchState) -> ResearchState:
    """Plan the research approach based on the query."""
    
    query_lower = state.query.lower()
    plan_elements = []
    
    # Analyze query for different data needs
    if any(word in query_lower for word in ["weather", "climate", "temperature"]):
        plan_elements.append("- Gather weather information")
    
    if any(word in query_lower for word in ["file", "document", "data"]):
        plan_elements.append("- Search relevant files")
    
    if any(word in query_lower for word in ["database", "record", "history"]):
        plan_elements.append("- Query database records")
    
    state.research_plan = "Research Plan:\n" + "\n".join(plan_elements)
    state.step_count += 1
    
    return state
```

**Step 5.1.3: Research Execution Nodes**

```python
async def _weather_research_node(self, state: ResearchState) -> ResearchState:
    """Research weather-related information."""
    
    # Skip if not weather-related
    if "weather" not in state.query.lower():
        state.weather_data = {"skipped": True}
        return state
    
    try:
        adapter = await self.mcp_manager.get_adapter("weather")
        if adapter:
            # Extract city names (simplified)
            cities = self._extract_cities_from_query(state.query)
            
            weather_results = {}
            for city in cities:
                result = await adapter.call_tool("get_current_weather", {"city": city})
                weather_results[city] = result
            
            state.weather_data = weather_results
        else:
            state.weather_data = {"error": "Weather server not available"}
    
    except Exception as e:
        state.weather_data = {"error": str(e)}
    
    state.step_count += 1
    return state
```

**Step 5.1.4: Workflow Assembly**

```python
from langgraph.graph import StateGraph, END

async def build_workflow(self) -> StateGraph:
    """Build the LangGraph workflow."""
    
    workflow = StateGraph(ResearchState)
    
    # Add processing nodes
    workflow.add_node("planner", self._planning_node)
    workflow.add_node("weather_researcher", self._weather_research_node)
    workflow.add_node("file_researcher", self._file_research_node)
    workflow.add_node("synthesizer", self._synthesis_node)
    
    # Define workflow flow
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "weather_researcher")
    workflow.add_edge("weather_researcher", "file_researcher")
    workflow.add_edge("file_researcher", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    return workflow.compile()
```

### Step 5.2: Testing the Workflow

```python
async def test_research_workflow():
    """Test the research workflow with a complex query."""
    
    manager = MCPServerManager(Config.MCP_SERVERS)
    
    async with manager.managed_servers():
        researcher = ResearchWorkflow(manager)
        
        # Test query
        query = "What's the weather like in London and find any related documentation?"
        
        result = await researcher.run_research(query)
        
        if result["success"]:
            print(f"Research Report:\n{result['report']}")
            print(f"Completed in {result['steps']} steps")
        else:
            print(f"Research failed: {result['error']}")
```

**Workflow Benefits:**
- **Structured Processing**: Clear step-by-step execution
- **State Persistence**: Data flows between steps
- **Error Isolation**: Failures in one step don't stop others
- **Progress Tracking**: Visibility into workflow execution

---

## 📝 Chapter Summary

You've successfully built sophisticated LangChain MCP integrations! Here's what you've mastered:

### Key Accomplishments:

#### 🔧 **Infrastructure**
- ✅ **Multi-server management** with health monitoring and automatic recovery
- ✅ **Type-safe configuration** with environment variable support
- ✅ **Robust error handling** with graceful degradation
- ✅ **Resource cleanup** with context managers

#### 🤖 **Agent Development**
- ✅ **Basic ReAct agents** for single-tool interactions
- ✅ **Multi-tool agents** that coordinate multiple MCP servers
- ✅ **Conversation memory** for context-aware interactions
- ✅ **Enhanced prompting** for better tool selection

#### 🔄 **Advanced Workflows**
- ✅ **LangGraph integration** for structured workflows
- ✅ **State management** across workflow steps
- ✅ **Research workflows** combining multiple data sources
- ✅ **Progress tracking** and error recovery

### Production-Ready Features:

- **Scalability**: Supports multiple MCP servers with load balancing
- **Reliability**: Health monitoring with automatic restart capabilities
- **Observability**: Comprehensive logging for debugging and monitoring
- **Maintainability**: Clean separation of concerns and modular design

---

## 🧪 Testing Your Understanding

### Quick Check Questions

1. **What is the primary advantage of the ReAct pattern in AI agents?**
   - A) Faster execution
   - B) Transparent reasoning and debugging
   - C) Lower memory usage
   - D) Better error handling

2. **Why do we use health monitoring in MCPServerManager?**
   - A) To improve performance
   - B) To automatically restart failed servers
   - C) To reduce costs
   - D) To monitor user activity

3. **What does conversation memory provide in multi-tool agents?**
   - A) Better performance
   - B) Context awareness across interactions
   - C) Error recovery
   - D) Tool validation

4. **How does LangGraph differ from simple ReAct agents?**
   - A) It's faster
   - B) It provides structured, stateful workflows
   - C) It uses fewer resources
   - D) It's easier to configure

5. **What is the benefit of enhanced tool descriptions?**
   - A) Smaller memory usage
   - B) Better agent tool selection decisions
   - C) Faster execution
   - D) Improved security

### Practical Exercise

Extend the multi-tool agent to handle a travel planning scenario:

```python
async def plan_travel():
    """
    Create a travel planning agent that:
    1. Gets weather for multiple destinations
    2. Searches for travel documents
    3. Saves trip recommendations to a file
    4. Provides a comprehensive travel report
    """
    # Your implementation here
    pass
```

**💡 Hint:** Check the [`Session3_LangChain_MCP_Integration-solution.md`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session3/Session3_solution.md) file for complete implementations.

---

## Next Session Preview

In Session 4, we'll focus on **Production MCP Deployment** including:
- Docker containerization and cloud deployment
- Monitoring and observability systems
- Auto-scaling and load balancing
- CI/CD pipelines for automated deployment

**Files created in this session:**
- [`src/session3/config.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session3/config.py) - Configuration management
- [`src/session3/utils/mcp_manager.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session3/utils/mcp_manager.py) - Server management
- [`src/session3/mcp_servers/weather_server.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session3/mcp_servers/weather_server.py) - Sample MCP server
- Additional agent and workflow implementations

You now have the foundation for building production-ready AI agents that can intelligently coordinate multiple tools and handle complex, multi-step tasks! 🚀