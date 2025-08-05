# Session 3: LangChain MCP Integration - Code-Along Tutorial

## 🎯 Learning Objectives
- Connect LangChain agents to MCP servers
- Build multi-server MCP client configurations
- Create ReAct agents with MCP tools
- Implement error handling and fallbacks
- Build complex agent workflows with LangGraph

## 📚 Pre-Session Reading
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [ReAct Agent Pattern](https://python.langchain.com/docs/modules/agents/agent_types/react)

---

## Part 1: Environment Setup (10 minutes)

### Step 1.1: Install Dependencies
```bash
# Create project directory
mkdir langchain-mcp-integration
cd langchain-mcp-integration

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install langchain-mcp-adapters langgraph langchain-openai \
            langchain-anthropic python-dotenv colorama
```

### Step 1.2: Project Structure
```
langchain-mcp-integration/
├── mcp_servers/
│   ├── weather_server.py
│   ├── filesystem_server.py
│   └── database_server.py
├── agents/
│   ├── __init__.py
│   ├── basic_agent.py
│   ├── multi_tool_agent.py
│   └── workflow_agent.py
├── config.py
├── utils.py
├── main.py
└── .env
```

### Step 1.3: Configuration Setup
```python
# config.py
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration for LangChain MCP integration."""
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_MODEL = "gpt-4"
    
    # MCP Server Configurations
    MCP_SERVERS: Dict[str, Dict[str, Any]] = {
        "weather": {
            "command": "python",
            "args": ["mcp_servers/weather_server.py"],
            "transport": "stdio",
            "description": "Weather information and forecasts"
        },
        "filesystem": {
            "command": "python",
            "args": ["mcp_servers/filesystem_server.py"],
            "transport": "stdio",
            "description": "File system operations"
        },
        "database": {
            "command": "python",
            "args": ["mcp_servers/database_server.py"],
            "transport": "stdio",
            "description": "Database operations"
        }
    }
    
    # Agent Configuration
    AGENT_TEMPERATURE = 0.7
    MAX_ITERATIONS = 10
    VERBOSE = True
```

---

## Part 2: Creating MCP Servers (20 minutes)

### Step 2.1: Enhanced Weather Server
```python
# mcp_servers/weather_server.py
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
import random
import json

mcp = FastMCP("Enhanced Weather Server")

# Simulated weather database
weather_db = {
    "current": {},
    "forecasts": {},
    "alerts": {}
}

@mcp.tool()
def get_weather(city: str, include_forecast: bool = False) -> dict:
    """
    Get current weather and optional forecast.
    
    Args:
        city: City name
        include_forecast: Include 3-day forecast
    
    Returns:
        Weather data with optional forecast
    """
    # Simulate weather data
    current = {
        "city": city,
        "temperature": random.randint(10, 30),
        "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Snowy"]),
        "humidity": random.randint(40, 80),
        "wind_speed": random.randint(5, 25),
        "timestamp": datetime.now().isoformat()
    }
    
    weather_db["current"][city] = current
    
    result = {"current": current}
    
    if include_forecast:
        forecast = []
        for i in range(1, 4):
            forecast.append({
                "day": (datetime.now() + timedelta(days=i)).strftime("%A"),
                "high": current["temperature"] + random.randint(-5, 5),
                "low": current["temperature"] - random.randint(5, 10),
                "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Snowy"])
            })
        result["forecast"] = forecast
    
    return result

@mcp.tool()
def set_weather_alert(city: str, condition: str, threshold: float) -> dict:
    """Set weather alert for specific conditions."""
    alert_id = f"alert_{len(weather_db['alerts']) + 1}"
    
    weather_db["alerts"][alert_id] = {
        "id": alert_id,
        "city": city,
        "condition": condition,
        "threshold": threshold,
        "created": datetime.now().isoformat(),
        "active": True
    }
    
    return {"alert_id": alert_id, "status": "created"}

@mcp.tool()
def compare_weather(cities: list[str]) -> dict:
    """Compare weather across multiple cities."""
    comparisons = {}
    
    for city in cities:
        weather = get_weather(city)
        comparisons[city] = weather["current"]
    
    # Find best weather
    best_city = max(comparisons.items(), 
                   key=lambda x: x[1]["temperature"])
    
    return {
        "cities": comparisons,
        "best_weather": best_city[0],
        "comparison_time": datetime.now().isoformat()
    }

if __name__ == "__main__":
    mcp.run()
```

### Step 2.2: Simple Database Server
```python
# mcp_servers/database_server.py
from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime
from typing import Dict, List, Any

mcp = FastMCP("Database Server")

# In-memory database
database = {
    "users": {},
    "sessions": {},
    "logs": []
}

@mcp.tool()
def create_record(table: str, record_id: str, data: dict) -> dict:
    """Create a new record in the database."""
    if table not in database:
        return {"error": f"Table '{table}' does not exist"}
    
    if record_id in database[table]:
        return {"error": f"Record '{record_id}' already exists"}
    
    database[table][record_id] = {
        **data,
        "id": record_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    return {"success": True, "record_id": record_id}

@mcp.tool()
def query_records(table: str, filters: dict = None) -> dict:
    """Query records from the database."""
    if table not in database:
        return {"error": f"Table '{table}' does not exist"}
    
    records = database[table]
    
    if filters:
        # Simple filtering
        filtered = {}
        for record_id, record in records.items():
            match = True
            for key, value in filters.items():
                if key not in record or record[key] != value:
                    match = False
                    break
            if match:
                filtered[record_id] = record
        records = filtered
    
    return {
        "table": table,
        "count": len(records),
        "records": records
    }

@mcp.tool()
def update_record(table: str, record_id: str, updates: dict) -> dict:
    """Update an existing record."""
    if table not in database:
        return {"error": f"Table '{table}' does not exist"}
    
    if record_id not in database[table]:
        return {"error": f"Record '{record_id}' not found"}
    
    database[table][record_id].update({
        **updates,
        "updated_at": datetime.now().isoformat()
    })
    
    return {"success": True, "record_id": record_id}

if __name__ == "__main__":
    mcp.run()
```

---

## Part 3: Basic LangChain MCP Integration (25 minutes)

### Step 3.1: MCP Client Wrapper
```python
# utils.py
from typing import Dict, List, Any, Optional
import asyncio
from colorama import Fore, Style, init
from langchain_mcp_adapters.client import MCPClient, StdioServerParameters

init(autoreset=True)

class MCPClientManager:
    """Manages multiple MCP client connections."""
    
    def __init__(self, config: Dict[str, Dict[str, Any]]):
        self.config = config
        self.clients: Dict[str, MCPClient] = {}
        self.connected = False
    
    async def connect_all(self):
        """Connect to all configured MCP servers."""
        print(f"{Fore.CYAN}Connecting to MCP servers...{Style.RESET_ALL}")
        
        for name, server_config in self.config.items():
            try:
                print(f"  → Connecting to {name}...", end="")
                
                # Create client based on transport type
                if server_config["transport"] == "stdio":
                    client = MCPClient(
                        StdioServerParameters(
                            command=server_config["command"],
                            args=server_config["args"]
                        )
                    )
                else:
                    raise ValueError(f"Unsupported transport: {server_config['transport']}")
                
                await client.__aenter__()
                self.clients[name] = client
                
                print(f" {Fore.GREEN}✓{Style.RESET_ALL}")
                
            except Exception as e:
                print(f" {Fore.RED}✗ {str(e)}{Style.RESET_ALL}")
        
        self.connected = True
        print(f"{Fore.GREEN}Connected to {len(self.clients)} servers{Style.RESET_ALL}\n")
    
    async def get_all_tools(self) -> List[Any]:
        """Get all tools from all connected servers."""
        all_tools = []
        
        for name, client in self.clients.items():
            try:
                tools = await client.get_tools()
                # Tag tools with server name
                for tool in tools:
                    tool.name = f"{name}_{tool.name}"
                all_tools.extend(tools)
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Could not get tools from {name}: {e}{Style.RESET_ALL}")
        
        return all_tools
    
    async def disconnect_all(self):
        """Disconnect all clients."""
        for name, client in self.clients.items():
            try:
                await client.__aexit__(None, None, None)
            except:
                pass
        self.connected = False

def print_tool_info(tools: List[Any]):
    """Pretty print tool information."""
    print(f"{Fore.CYAN}Available MCP Tools:{Style.RESET_ALL}")
    for tool in tools:
        print(f"  • {Fore.GREEN}{tool.name}{Style.RESET_ALL}: {tool.description}")
    print()
```

### Step 3.2: Basic ReAct Agent
```python
# agents/basic_agent.py
import asyncio
from typing import List, Dict, Any
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from config import Config
from utils import print_tool_info

class BasicMCPAgent:
    """Basic ReAct agent with MCP tools."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=Config.AGENT_TEMPERATURE
        )
        self.client = None
        self.agent_executor = None
    
    async def initialize(self):
        """Initialize the agent with MCP tools."""
        # Create multi-server client
        self.client = MultiServerMCPClient(Config.MCP_SERVERS)
        
        # Get all tools
        tools = await self.client.get_tools()
        print_tool_info(tools)
        
        # Create agent prompt
        prompt = PromptTemplate.from_template("""
You are a helpful assistant with access to various tools through MCP servers.

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
        
        # Create agent
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=Config.VERBOSE,
            max_iterations=Config.MAX_ITERATIONS,
            handle_parsing_errors=True
        )
    
    async def run(self, query: str) -> str:
        """Run the agent with a query."""
        if not self.agent_executor:
            await self.initialize()
        
        result = await self.agent_executor.ainvoke({"input": query})
        return result["output"]
    
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            # Client cleanup is handled by context manager
            pass

# Example usage
async def test_basic_agent():
    agent = BasicMCPAgent()
    
    try:
        # Test weather query
        result = await agent.run(
            "What's the weather in London and New York? Which city has better weather?"
        )
        print(f"Result: {result}\n")
        
        # Test combined query
        result = await agent.run(
            "Get the weather for Tokyo and save it to a file called tokyo_weather.json"
        )
        print(f"Result: {result}\n")
        
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test_basic_agent())
```

### Step 3.3: Multi-Tool Coordination Agent
```python
# agents/multi_tool_agent.py
from typing import List, Dict, Any, Optional
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import StructuredTool
import json

class MultiToolCoordinationAgent:
    """Agent that coordinates multiple MCP tools for complex tasks."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or "gpt-4"
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.3)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.client = None
        self.agent_executor = None
        self.tools_by_category = {}
    
    async def initialize(self):
        """Initialize with categorized tools."""
        self.client = MultiServerMCPClient(Config.MCP_SERVERS)
        tools = await self.client.get_tools()
        
        # Categorize tools by server
        for tool in tools:
            server_name = tool.name.split('_')[0]
            if server_name not in self.tools_by_category:
                self.tools_by_category[server_name] = []
            self.tools_by_category[server_name].append(tool)
        
        # Add coordination tools
        coordination_tools = self._create_coordination_tools()
        tools.extend(coordination_tools)
        
        # Create structured chat prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent assistant that coordinates multiple specialized tools.

Tool Categories:
- weather: Weather information and forecasts
- filesystem: File operations (read, write, search)
- database: Data storage and retrieval

When handling complex requests:
1. Break down the task into steps
2. Use appropriate tools from different categories
3. Coordinate results between tools
4. Provide comprehensive responses

Always think about which tools to use and in what order."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            max_iterations=15,
            handle_parsing_errors=True
        )
    
    def _create_coordination_tools(self) -> List[StructuredTool]:
        """Create tools for coordinating between MCP servers."""
        
        def plan_multi_tool_task(task_description: str) -> str:
            """Plan how to execute a multi-tool task."""
            # Simple task planning logic
            steps = []
            
            if "weather" in task_description.lower():
                steps.append("1. Use weather tools to get weather information")
            if "save" in task_description.lower() or "file" in task_description.lower():
                steps.append("2. Use filesystem tools to save data")
            if "database" in task_description.lower() or "store" in task_description.lower():
                steps.append("3. Use database tools to store records")
            
            return "Task Plan:\n" + "\n".join(steps)
        
        def combine_results(results: List[Dict[str, Any]]) -> str:
            """Combine results from multiple tools."""
            combined = {
                "combined_results": results,
                "summary": f"Processed {len(results)} results",
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(combined, indent=2)
        
        return [
            StructuredTool.from_function(
                func=plan_multi_tool_task,
                name="plan_task",
                description="Plan how to execute a multi-tool task"
            ),
            StructuredTool.from_function(
                func=combine_results,
                name="combine_results",
                description="Combine results from multiple tool calls"
            )
        ]
    
    async def run(self, query: str) -> str:
        """Run the agent with memory."""
        if not self.agent_executor:
            await self.initialize()
        
        result = await self.agent_executor.ainvoke({"input": query})
        return result["output"]
```

---

## Part 4: Advanced LangGraph Workflows (25 minutes)

### Step 4.1: Workflow Agent with LangGraph
```python
# agents/workflow_agent.py
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import operator

class AgentState(TypedDict):
    """State for the agent workflow."""
    messages: Annotated[List[Any], operator.add]
    current_task: str
    subtasks: List[str]
    results: Dict[str, Any]
    final_output: str

class WorkflowMCPAgent:
    """Advanced workflow agent using LangGraph."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.client = None
        self.tools = None
        self.tool_executor = None
        self.workflow = None
    
    async def initialize(self):
        """Initialize the workflow agent."""
        # Connect to MCP servers
        self.client = MultiServerMCPClient(Config.MCP_SERVERS)
        self.tools = await self.client.get_tools()
        self.tool_executor = ToolExecutor(self.tools)
        
        # Build the workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_task", self._analyze_task)
        workflow.add_node("plan_execution", self._plan_execution)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("synthesize_results", self._synthesize_results)
        
        # Add edges
        workflow.set_entry_point("analyze_task")
        workflow.add_edge("analyze_task", "plan_execution")
        workflow.add_edge("plan_execution", "execute_tools")
        workflow.add_edge("execute_tools", "synthesize_results")
        workflow.add_edge("synthesize_results", END)
        
        return workflow.compile()
    
    async def _analyze_task(self, state: AgentState) -> AgentState:
        """Analyze the task and identify subtasks."""
        task = state["current_task"]
        
        analysis_prompt = f"""Analyze this task and break it down into subtasks:
Task: {task}

Identify:
1. What information needs to be gathered
2. What actions need to be performed
3. What tools might be needed

Return a JSON with subtasks list."""
        
        response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
        
        # Parse subtasks (simplified)
        subtasks = [
            "Gather required data",
            "Process information",
            "Generate output"
        ]
        
        state["subtasks"] = subtasks
        state["messages"].append(response)
        
        return state
    
    async def _plan_execution(self, state: AgentState) -> AgentState:
        """Plan tool execution based on subtasks."""
        subtasks = state["subtasks"]
        
        planning_prompt = f"""Given these subtasks: {subtasks}
And available tools: {[t.name for t in self.tools]}

Create an execution plan specifying which tools to use for each subtask."""
        
        response = await self.llm.ainvoke([HumanMessage(content=planning_prompt)])
        state["messages"].append(response)
        
        return state
    
    async def _execute_tools(self, state: AgentState) -> AgentState:
        """Execute tools based on the plan."""
        # Simplified tool execution
        results = {}
        
        # Example: Execute weather tool
        for tool in self.tools:
            if "weather" in tool.name and "weather" in state["current_task"].lower():
                try:
                    result = await tool.ainvoke({"city": "London"})
                    results["weather_data"] = result
                except Exception as e:
                    results["weather_error"] = str(e)
        
        state["results"] = results
        return state
    
    async def _synthesize_results(self, state: AgentState) -> AgentState:
        """Synthesize results into final output."""
        results = state["results"]
        
        synthesis_prompt = f"""Synthesize these results into a comprehensive response:
Results: {results}
Original task: {state['current_task']}"""
        
        response = await self.llm.ainvoke([HumanMessage(content=synthesis_prompt)])
        state["final_output"] = response.content
        
        return state
    
    async def run(self, task: str) -> str:
        """Run the workflow agent."""
        if not self.workflow:
            await self.initialize()
        
        initial_state = {
            "messages": [],
            "current_task": task,
            "subtasks": [],
            "results": {},
            "final_output": ""
        }
        
        final_state = await self.workflow.ainvoke(initial_state)
        return final_state["final_output"]
```

### Step 4.2: Error Handling and Retry Logic
```python
# agents/robust_agent.py
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

class RobustMCPAgent:
    """MCP Agent with robust error handling."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fallback_responses = {
            "weather": "Weather information temporarily unavailable",
            "filesystem": "File operation could not be completed",
            "database": "Database operation failed"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_tool_with_retry(self, tool, **kwargs):
        """Call a tool with retry logic."""
        try:
            result = await tool.ainvoke(kwargs)
            return {"success": True, "data": result}
        except Exception as e:
            self.logger.error(f"Tool {tool.name} failed: {e}")
            raise
    
    async def call_tool_with_fallback(self, tool, fallback_key: str, **kwargs):
        """Call a tool with fallback handling."""
        try:
            return await self.call_tool_with_retry(tool, **kwargs)
        except Exception as e:
            self.logger.warning(f"All retries failed for {tool.name}, using fallback")
            return {
                "success": False,
                "data": self.fallback_responses.get(fallback_key, "Operation failed"),
                "error": str(e)
            }
```

### Step 4.3: Main Application
```python
# main.py
import asyncio
from agents.basic_agent import BasicMCPAgent
from agents.multi_tool_agent import MultiToolCoordinationAgent
from agents.workflow_agent import WorkflowMCPAgent
from colorama import Fore, Style

async def demo_basic_agent():
    """Demo basic agent capabilities."""
    print(f"\n{Fore.CYAN}=== Basic MCP Agent Demo ==={Style.RESET_ALL}\n")
    
    agent = BasicMCPAgent()
    
    queries = [
        "What's the weather in Paris?",
        "Compare weather in London, Tokyo, and New York",
        "Create a file called weather_report.txt with the current weather in Berlin"
    ]
    
    for query in queries:
        print(f"{Fore.YELLOW}Query:{Style.RESET_ALL} {query}")
        result = await agent.run(query)
        print(f"{Fore.GREEN}Result:{Style.RESET_ALL} {result}\n")
    
    await agent.cleanup()

async def demo_multi_tool_agent():
    """Demo multi-tool coordination."""
    print(f"\n{Fore.CYAN}=== Multi-Tool Coordination Demo ==={Style.RESET_ALL}\n")
    
    agent = MultiToolCoordinationAgent()
    
    # Complex multi-step task
    query = """
    1. Get weather data for London, Paris, and Rome
    2. Save each city's weather to separate JSON files
    3. Create a summary report comparing all three cities
    4. Store the comparison in the database
    """
    
    print(f"{Fore.YELLOW}Complex Query:{Style.RESET_ALL} {query}")
    result = await agent.run(query)
    print(f"{Fore.GREEN}Result:{Style.RESET_ALL} {result}\n")

async def demo_workflow_agent():
    """Demo workflow agent."""
    print(f"\n{Fore.CYAN}=== Workflow Agent Demo ==={Style.RESET_ALL}\n")
    
    agent = WorkflowMCPAgent()
    
    task = "Create a comprehensive weather analysis report for European capitals"
    
    print(f"{Fore.YELLOW}Task:{Style.RESET_ALL} {task}")
    result = await agent.run(task)
    print(f"{Fore.GREEN}Result:{Style.RESET_ALL} {result}\n")

async def main():
    """Run all demos."""
    print(f"{Fore.MAGENTA}{'='*50}")
    print("LangChain MCP Integration Demos")
    print(f"{'='*50}{Style.RESET_ALL}")
    
    await demo_basic_agent()
    await demo_multi_tool_agent()
    await demo_workflow_agent()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧪 Testing Your Understanding

### Quick Check Questions

1. **What is the primary benefit of using MultiServerMCPClient?**
   - A) Better performance
   - B) Connect to multiple MCP servers simultaneously
   - C) Enhanced security
   - D) Reduced memory usage

2. **In LangGraph, what defines the flow between nodes?**
   - A) Conditions
   - B) Edges
   - C) States
   - D) Tools

3. **How are MCP tools integrated into LangChain agents?**
   - A) As LangChain Tool objects
   - B) As raw functions
   - C) As API endpoints
   - D) As prompt templates

4. **What pattern does the ReAct agent follow?**
   - A) Plan-Execute
   - B) Thought-Action-Observation
   - C) Input-Process-Output
   - D) Request-Response

5. **How can you handle MCP server connection failures?**
   - A) Ignore them
   - B) Retry with exponential backoff
   - C) Always use default values
   - D) Terminate the program

### Practical Exercise

Create an agent that:
1. Monitors weather alerts across multiple cities
2. Saves alerts to files when thresholds are exceeded
3. Updates a database with alert history
4. Provides daily summary reports

```python
# Your implementation here
class WeatherAlertAgent:
    """Monitor and manage weather alerts."""
    
    async def monitor_alerts(self, cities: List[str], 
                           thresholds: Dict[str, float]) -> Dict:
        """Monitor weather and trigger alerts."""
        # TODO: Implement monitoring logic
        pass
```

---

## 📝 Session Summary

You've learned to:
- ✅ Connect LangChain agents to multiple MCP servers
- ✅ Build ReAct agents with MCP tools
- ✅ Coordinate multi-tool workflows
- ✅ Implement error handling and retries
- ✅ Create complex workflows with LangGraph
- ✅ Handle tool failures gracefully

### Next Session Preview
In Session 4, we'll deploy MCP servers to production:
- Containerize MCP servers
- Deploy to cloud platforms
- Implement authentication
- Monitor and scale MCP services

### Homework
1. Create an agent that combines data from all three MCP servers
2. Implement a caching layer for MCP tool responses
3. Build a conversation agent with memory and MCP tools
4. Add streaming support for long-running MCP operations

### Answer Key
1. B) Connect to multiple MCP servers simultaneously
2. B) Edges
3. A) As LangChain Tool objects
4. B) Thought-Action-Observation
5. B) Retry with exponential backoff

---

## Additional Resources
- [LangChain Agents Documentation](https://python.langchain.com/docs/modules/agents)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)
- [MCP Client Best Practices](https://modelcontextprotocol.io/docs/concepts/clients)