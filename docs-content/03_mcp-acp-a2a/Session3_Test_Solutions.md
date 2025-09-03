# Session 3: LangChain MCP Integration - Test Solutions

## 📝 Multiple Choice Test

**Question 1:** What is the primary advantage of using LangChain MCP adapters?  

A) Better performance  
B) Automatic tool discovery and integration ✅  
C) Reduced memory usage  
D) Simplified configuration  

**Explanation:** LangChain MCP adapters provide automatic tool discovery and integration, enabling seamless connection to multiple MCP servers without manual configuration. This standardized approach simplifies agent development and scales efficiently across enterprise deployments.

**Question 2:** In the ReAct pattern, what does the agent do after each Action?  

A) Plan the next action  
B) Wait for user input  
C) Observe the result ✅  
D) Generate a final answer  

**Explanation:** The ReAct pattern follows a Thought-Action-Observation cycle. After each Action (tool execution), the agent Observes the result before deciding on the next course of action. This iterative process enables intelligent reasoning about tool usage.

**Question 3:** What is the purpose of health monitoring in MCPServerManager?  

A) Improve performance  
B) Automatically restart failed servers ✅  
C) Monitor memory usage  
D) Log user interactions  

**Explanation:** Health monitoring in MCPServerManager detects when servers become unavailable and automatically attempts to restart them. This ensures high availability and resilience in enterprise deployments.

**Question 4:** What advantage does LangGraph provide over simple ReAct agents?  

A) Faster execution  
B) Complex stateful workflows ✅  
C) Better error handling  
D) Simpler configuration  

**Explanation:** LangGraph enables complex stateful workflows with features like parallel processing, conditional branching, and state management. This goes beyond the simple sequential reasoning of basic ReAct agents.

**Question 5:** How does our multi-tool agent decide which tools to use?  

A) Random selection  
B) Pre-configured rules  
C) LLM reasoning about tool descriptions ✅  
D) User specification  

**Explanation:** The multi-tool agent uses LLM reasoning to analyze tool descriptions, understand the user query, and intelligently select the most appropriate tools. This enables dynamic and context-aware tool coordination.

**Question 6:** What enterprise benefit does MCP provide over traditional API integrations?  

A) Faster response times  
B) Standardized protocol for tool integration ✅  
C) Lower development costs  
D) Better user interfaces  

**Explanation:** MCP provides a standardized protocol that eliminates the need for custom integrations with each tool or service. This standardization significantly reduces development time and maintenance overhead in enterprise environments.

**Question 7:** Which companies have adopted MCP in their production systems?  

A) Only startups  
B) Block, OpenAI, and Google DeepMind ✅  
C) Government agencies only  
D) Educational institutions  

**Explanation:** Major technology companies including Block, OpenAI (official adoption in March 2025), and Google DeepMind have adopted MCP in their production systems, demonstrating its enterprise readiness and industry acceptance.

**Question 8:** What authentication standard does MCP use for enterprise security?  

A) Basic authentication  
B) API keys only  
C) OAuth 2.0 ✅  
D) Custom tokens  

**Explanation:** MCP implements OAuth 2.0, a widely-recognized and robust authentication standard that provides secure, scalable authentication suitable for enterprise environments with multi-user scenarios.

**Question 9:** In LangGraph workflows, what tracks data between processing nodes?  

A) Global variables  
B) State objects ✅  
C) Database records  
D) Configuration files  

**Explanation:** LangGraph uses state objects (like dataclasses) that flow through the workflow graph, allowing each node to access and modify shared data as the workflow progresses through different processing stages.

**Question 10:** What happens when an MCP server fails in our architecture?  

A) The entire system crashes  
B) Other servers are affected  
C) Automatic restart is attempted ✅  
D) Manual intervention is required  

**Explanation:** The MCPServerManager implements health monitoring and automatic restart capabilities. When a server fails, the system attempts to restart it automatically, providing resilience and high availability.

## Performance Scoring

- **9-10 Correct**: Excellent mastery - Ready for enterprise agent development  
- **7-8 Correct**: Good understanding - Strong grasp of LangChain MCP integration  
- **5-6 Correct**: Adequate grasp - Review ReAct patterns and workflow orchestration  
- **0-4 Correct**: Review recommended - Revisit session content and practice examples  

## Key Concepts Review

1. **MCP Integration**: Standardized protocol enabling seamless tool coordination  
2. **ReAct Pattern**: Thought-Action-Observation cycles for intelligent reasoning  
3. **Health Monitoring**: Automatic server restart and failure recovery  
4. **Enterprise Adoption**: Major companies using MCP in production systems  
5. **Workflow Orchestration**: LangGraph enables complex stateful processing  
6. **Security Standards**: OAuth 2.0 provides enterprise-grade authentication  
7. **State Management**: Shared objects track data flow between workflow nodes  

## Answer Summary  
1. B  2. C  3. B  4. B  5. C  6. B  7. B  8. C  9. B  10. C  

**Challenge:** Create a travel planning agent that gets weather, searches files, stores preferences, and creates a report.

```python
# agents/travel_planning_agent.py
import asyncio
import json
from typing import Dict, Any, List
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferWindowMemory

from utils.mcp_manager import MCPServerManager

class TravelPlanningAgent:
    """Specialized agent for comprehensive travel planning."""

    def __init__(self, mcp_manager: MCPServerManager):
        self.mcp_manager = mcp_manager
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        self.memory = ConversationBufferWindowMemory(k=20, memory_key="chat_history", return_messages=True)

    async def initialize(self):
        """Initialize the travel planning agent with multi-server tools."""
        travel_tools = await self._create_travel_tools()

        travel_prompt = PromptTemplate.from_template("""
You are a professional travel planning AI assistant with access to weather information,
file system for travel documents, and database for storing preferences.

TRAVEL PLANNING APPROACH:
1. Understand the travel request (destinations, dates, preferences)
2. Check weather conditions for all potential destinations
3. Search for relevant travel documents or previous trip information
4. Store or retrieve user travel preferences
5. Create a comprehensive, actionable travel plan

Available tools: {tools}
Question: {input}
{agent_scratchpad}
""")

        agent = create_react_agent(llm=self.llm, tools=travel_tools, prompt=travel_prompt)

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=travel_tools,
            memory=self.memory,
            max_iterations=15,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

    async def _create_travel_tools(self) -> List[Tool]:
        """Create specialized tools for travel planning."""
        tools = []

        # Weather comparison tool
        weather_adapter = await self.mcp_manager.get_adapter("weather")
        if weather_adapter:
            async def compare_destination_weather(destinations_input: str):
                destinations = [city.strip() for city in destinations_input.split(',')]
                weather_comparison = {}

                for city in destinations:
                    try:
                        current = await weather_adapter.call_tool("get_current_weather", {"city": city})
                        weather_comparison[city] = {
                            "current": current,
                            "recommendation": self._generate_weather_recommendation(current)
                        }
                    except Exception as e:
                        weather_comparison[city] = {"error": str(e)}

                return json.dumps(weather_comparison, indent=2)

            tools.append(Tool(
                name="compare_destination_weather",
                description="Compare weather conditions across multiple travel destinations. Input: comma-separated city names.",
                func=lambda x: asyncio.create_task(compare_destination_weather(x))
            ))

        # File search tool for travel documents
        fs_adapter = await self.mcp_manager.get_adapter("filesystem")
        if fs_adapter:
            async def search_travel_documents(search_term: str):
                try:
                    results = await fs_adapter.call_tool("search_files", {
                        "query": search_term,
                        "file_types": [".md", ".txt", ".pdf"],
                        "max_results": 5
                    })
                    return json.dumps(results, indent=2)
                except Exception as e:
                    return f"Document search failed: {str(e)}"

            tools.append(Tool(
                name="search_travel_documents",
                description="Search for travel-related documents and guides. Input: search terms.",
                func=lambda x: asyncio.create_task(search_travel_documents(x))
            ))

        return tools

    def _generate_weather_recommendation(self, current: Dict) -> str:
        """Generate travel recommendation based on weather data."""
        try:
            temp = current.get("temperature", 0)
            condition = current.get("condition", "unknown")

            if temp > 25:
                return f"Excellent weather for outdoor activities. {temp}°C, {condition}"
            elif temp > 15:
                return f"Pleasant weather, pack light layers. {temp}°C, {condition}"
            else:
                return f"Cool weather, pack warm clothing. {temp}°C, {condition}"
        except Exception:
            return "Weather data insufficient for recommendation"

    async def plan_trip(self, request: str):
        """Execute travel planning based on user request."""
        return await self.agent_executor.arun(request)

# Usage example
async def main():
    mcp_manager = MCPServerManager()
    await mcp_manager.add_server("weather", "python weather_server.py")
    await mcp_manager.add_server("filesystem", "python file_server.py")

    travel_agent = TravelPlanningAgent(mcp_manager)
    await travel_agent.initialize()

    response = await travel_agent.plan_trip(
        "Plan a 5-day trip to Paris or Tokyo in December. Budget: $3000. Check weather and previous travel preferences."
    )
    print("Travel Plan:", response)

    await mcp_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Key Learning Points:

1. **Multi-Server Coordination**: The agent connects to multiple MCP servers and coordinates their capabilities  
2. **Specialized Tool Creation**: Custom tools combine multiple MCP server calls into travel-specific functionality  
3. **Memory Management**: Conversation memory maintains context across the planning session  
4. **Error Handling**: Graceful degradation when servers are unavailable  
5. **Professional Prompting**: Specialized prompts optimized for travel planning workflows

---

## 🧭 Navigation

**Back to Test:** [Session 3 Test Questions →](Session3_*.md#multiple-choice-test)

---
