# Session 3: LangChain MCP Integration - Solution Guide

## 🧪 Multiple Choice Quiz - Answer Key

### Quick Check Questions

1. **What is the primary advantage of using LangChain MCP adapters?**
   - A) Better performance
   - B) Automatic tool discovery and integration ✅ **CORRECT**
   - C) Reduced memory usage  
   - D) Simplified configuration

   **Explanation:** LangChain MCP adapters automatically discover available tools from MCP servers and convert them to LangChain-compatible tools, eliminating the need for manual integration code.

2. **In the ReAct pattern, what does the agent do after each Action?**
   - A) Plan the next action
   - B) Wait for user input
   - C) Observe the result ✅ **CORRECT**
   - D) Generate a final answer

   **Explanation:** The ReAct pattern follows a Thought→Action→Observation cycle. After each action, the agent observes the result before planning the next step.

3. **What is the purpose of the health monitoring in MCPServerManager?**
   - A) Improve performance
   - B) Automatically restart failed servers ✅ **CORRECT**
   - C) Monitor memory usage
   - D) Log user interactions

   **Explanation:** The health monitoring system continuously checks MCP server availability and automatically attempts to restart failed servers to ensure high availability.

4. **What advantage does LangGraph provide over simple ReAct agents?**
   - A) Faster execution
   - B) Complex stateful workflows ✅ **CORRECT**
   - C) Better error handling
   - D) Simpler configuration

   **Explanation:** LangGraph enables the creation of complex, stateful workflows with multiple nodes, branching logic, and sophisticated control flow that goes beyond simple ReAct loops.

5. **How does our multi-tool agent decide which tools to use?**
   - A) Random selection
   - B) Pre-configured rules
   - C) LLM reasoning about tool descriptions ✅ **CORRECT**
   - D) User specification

   **Explanation:** The agent uses the LLM's reasoning capabilities to analyze the user query and tool descriptions to intelligently select the most appropriate tools.

---

## 💡 Practical Exercise Solution

**Challenge:** Create a travel planning agent that gets weather, searches files, stores preferences, and creates a report.

### Complete Solution:

```python
# agents/travel_planning_agent.py
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferWindowMemory

from utils.mcp_manager import MCPServerManager
from config import Config

class TravelPlanningAgent:
    """Specialized agent for comprehensive travel planning."""
    
    def __init__(self, mcp_manager: MCPServerManager):
        self.mcp_manager = mcp_manager
        self.llm = None
        self.agent_executor = None
        self.memory = None
    
    async def initialize(self) -> bool:
        """Initialize the travel planning agent."""
        try:
            # Initialize LLM
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.3,  # Lower temperature for more consistent planning
                api_key=Config.OPENAI_API_KEY
            )
            
            # Initialize memory
            self.memory = ConversationBufferWindowMemory(
                k=20,  # Remember more for travel context
                memory_key="chat_history",
                return_messages=True
            )
            
            # Create specialized travel tools
            travel_tools = await self._create_travel_tools()
            
            if not travel_tools:
                return False
            
            # Create travel-focused ReAct agent
            travel_prompt = PromptTemplate.from_template("""
You are a professional travel planning AI assistant with access to weather information, 
file system for travel documents, and database for storing preferences.

TRAVEL PLANNING APPROACH:
1. Understand the travel request (destinations, dates, preferences)
2. Check weather conditions for all potential destinations
3. Search for relevant travel documents, guides, or previous trip information
4. Store or retrieve user travel preferences
5. Create a comprehensive, actionable travel plan

Available tools:
{tools}

CONVERSATION HISTORY:
{chat_history}

TRAVEL PLANNING FORMAT:
Question: {input}
Thought: Let me analyze this travel request and determine what information I need
Action: [choose appropriate tool from {tool_names}]
Action Input: [provide specific parameters]
Observation: [analyze the results]
... (continue gathering information as needed)
Thought: Now I have sufficient information to create a comprehensive travel plan
Final Answer: [provide detailed travel recommendations with weather, logistics, and stored preferences]

Question: {input}
{agent_scratchpad}
""")
            
            agent = create_react_agent(
                llm=self.llm,
                tools=travel_tools,
                prompt=travel_prompt
            )
            
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=travel_tools,
                memory=self.memory,
                verbose=True,
                max_iterations=15,  # More iterations for complex planning
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize travel agent: {e}")
            return False
    
    async def _create_travel_tools(self) -> List[Tool]:
        """Create specialized tools for travel planning."""
        tools = []
        
        # Weather tools
        weather_adapter = await self.mcp_manager.get_adapter("weather")
        if weather_adapter:
            # Multi-destination weather comparison tool
            async def compare_destination_weather(destinations_input: str):
                """Compare weather across multiple travel destinations."""
                try:
                    # Parse destinations (expecting comma-separated cities)
                    destinations = [city.strip() for city in destinations_input.split(',')]
                    weather_comparison = {}
                    
                    for city in destinations:
                        try:
                            current = await weather_adapter.call_tool("get_current_weather", {"city": city})
                            forecast = await weather_adapter.call_tool("get_weather_forecast", {"city": city, "days": 7})
                            
                            weather_comparison[city] = {
                                "current": current,
                                "forecast": forecast,
                                "travel_recommendation": self._generate_weather_recommendation(current, forecast)
                            }
                        except Exception as e:
                            weather_comparison[city] = {"error": str(e)}
                    
                    return json.dumps(weather_comparison, indent=2)
                    
                except Exception as e:
                    return f"Weather comparison failed: {str(e)}"
            
            tools.append(Tool(
                name="compare_destination_weather",
                description="Compare weather conditions across multiple travel destinations. Input: comma-separated city names.",
                func=lambda x: asyncio.create_task(compare_destination_weather(x))
            ))
        
        # File system tools for travel documents
        fs_adapter = await self.mcp_manager.get_adapter("filesystem")
        if fs_adapter:
            async def search_travel_documents(search_term: str):
                """Search for travel-related documents and guides."""
                try:
                    # Search for travel-related files
                    travel_keywords = ["travel", "trip", "vacation", "guide", "itinerary", "hotel", "flight"]
                    results = {}
                    
                    for keyword in travel_keywords:
                        try:
                            search_result = await fs_adapter.call_tool("search_files", {
                                "pattern": f"*{keyword}*",
                                "search_type": "name"
                            })
                            if search_result and search_result.get("results"):
                                results[keyword] = search_result["results"]
                        except:
                            continue
                    
                    # Also search by the specific term
                    if search_term:
                        try:
                            specific_search = await fs_adapter.call_tool("search_files", {
                                "pattern": f"*{search_term}*",
                                "search_type": "content"
                            })
                            if specific_search:
                                results["specific_search"] = specific_search
                        except:
                            pass
                    
                    return json.dumps(results, indent=2) if results else "No travel documents found"
                    
                except Exception as e:
                    return f"Document search failed: {str(e)}"
            
            tools.append(Tool(
                name="search_travel_documents",
                description="Search for travel guides, itineraries, and travel-related documents. Input: search term or destination name.",
                func=lambda x: asyncio.create_task(search_travel_documents(x))
            ))
            
            async def create_travel_itinerary(itinerary_data: str):
                """Create and save a travel itinerary file."""
                try:
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"travel_itinerary_{timestamp}.md"
                    
                    # Create formatted itinerary
                    formatted_itinerary = f"""# Travel Itinerary
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{itinerary_data}

---
*Generated by AI Travel Planning Agent*
"""
                    
                    result = await fs_adapter.call_tool("write_file", {
                        "path": f"travel_plans/{filename}",
                        "content": formatted_itinerary,
                        "create_dirs": True
                    })
                    
                    return f"Travel itinerary saved as {filename}: {result}"
                    
                except Exception as e:
                    return f"Failed to save itinerary: {str(e)}"
            
            tools.append(Tool(
                name="create_travel_itinerary",
                description="Create and save a detailed travel itinerary file. Input: itinerary content in markdown format.",
                func=lambda x: asyncio.create_task(create_travel_itinerary(x))
            ))
        
        # Database tools for preferences (simulated)
        db_adapter = await self.mcp_manager.get_adapter("database")
        if db_adapter:
            async def store_travel_preferences(preferences_json: str):
                """Store user travel preferences in database."""
                try:
                    # In a real implementation, this would store in a database
                    # For demo, we'll simulate storage
                    preferences = json.loads(preferences_json)
                    
                    # Add metadata
                    preferences["stored_at"] = datetime.now().isoformat()
                    preferences["agent_version"] = "travel_v1.0"
                    
                    # Simulate database storage
                    result = {
                        "success": True,
                        "stored_preferences": preferences,
                        "message": "Travel preferences stored successfully"
                    }
                    
                    return json.dumps(result, indent=2)
                    
                except Exception as e:
                    return f"Failed to store preferences: {str(e)}"
            
            tools.append(Tool(
                name="store_travel_preferences",
                description="Store user travel preferences (budget, accommodation type, activities, etc.). Input: JSON object with preference data.",
                func=lambda x: asyncio.create_task(store_travel_preferences(x))
            ))
            
            async def retrieve_travel_preferences(user_id: str):
                """Retrieve stored travel preferences for a user."""
                try:
                    # Simulate preference retrieval
                    # In production, this would query a real database
                    default_preferences = {
                        "user_id": user_id,
                        "budget_range": "medium",
                        "accommodation_type": "hotel",
                        "preferred_activities": ["sightseeing", "cultural", "food"],
                        "travel_pace": "moderate",
                        "climate_preference": "mild",
                        "last_updated": datetime.now().isoformat()
                    }
                    
                    return json.dumps(default_preferences, indent=2)
                    
                except Exception as e:
                    return f"Failed to retrieve preferences: {str(e)}"
            
            tools.append(Tool(
                name="retrieve_travel_preferences",
                description="Retrieve stored travel preferences for a user. Input: user ID or identifier.",
                func=lambda x: asyncio.create_task(retrieve_travel_preferences(x))
            ))
        
        return tools
    
    def _generate_weather_recommendation(self, current: Dict, forecast: List) -> str:
        """Generate travel recommendation based on weather data."""
        if not current or "error" in current:
            return "Weather data unavailable for recommendation"
        
        temp = current.get("temp", 0)
        condition = current.get("condition", "").lower()
        
        recommendations = []
        
        # Temperature-based recommendations
        if temp > 25:
            recommendations.append("Great weather for outdoor activities")
        elif temp > 15:
            recommendations.append("Pleasant weather for sightseeing")
        else:
            recommendations.append("Pack warm clothes, consider indoor activities")
        
        # Condition-based recommendations
        if "rain" in condition:
            recommendations.append("Bring umbrella and waterproof gear")
        elif "sunny" in condition:
            recommendations.append("Don't forget sunscreen and sunglasses")
        elif "cloudy" in condition:
            recommendations.append("Good weather for walking tours")
        
        return "; ".join(recommendations)
    
    async def plan_trip(self, travel_request: str) -> Dict[str, Any]:
        """Plan a complete trip based on the travel request."""
        if not self.agent_executor:
            return {"error": "Agent not initialized"}
        
        try:
            # Enhanced travel planning prompt
            detailed_request = f"""
Create a comprehensive travel plan for: {travel_request}

Please include:
1. Weather analysis for all mentioned destinations
2. Search for relevant travel documents or guides
3. Store any mentioned preferences (budget, activities, etc.)
4. Provide specific recommendations for:
   - Best time to visit based on weather
   - Suggested activities based on conditions
   - Packing recommendations
   - Any relevant travel documents found

Create a detailed, actionable travel plan.
"""
            
            result = await self.agent_executor.ainvoke({"input": detailed_request})
            
            return {
                "success": True,
                "travel_plan": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "request": travel_request
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "request": travel_request
            }

# Example usage and testing
async def demo_travel_agent():
    """Demonstrate the travel planning agent."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    console = Console()
    
    # Initialize MCP manager
    manager = MCPServerManager(Config.MCP_SERVERS)
    
    async with manager.managed_servers():
        # Create travel agent
        agent = TravelPlanningAgent(manager)
        
        if not await agent.initialize():
            console.print("❌ Failed to initialize travel agent", style="red")
            return
        
        console.print(Panel.fit(
            "✈️ Travel Planning Agent Ready!\n"
            "I can help you plan trips with weather analysis, document search, and preference storage.",
            title="Travel Agent Initialized",
            border_style="blue"
        ))
        
        # Example travel requests
        travel_requests = [
            "Plan a 5-day trip to London and Paris in spring, I enjoy museums and good food, moderate budget",
            "Compare weather between Tokyo and Sydney for a winter vacation",
            "I want to visit New York for business, need weather info and any travel guides"
        ]
        
        for request in travel_requests:
            console.print(f"\n✈️ Travel Request: {request}")
            console.print("🗺️ Planning your trip...", style="yellow")
            
            result = await agent.plan_trip(request)
            
            if result["success"]:
                plan_panel = Panel(
                    Markdown(result["travel_plan"]),
                    title="🗺️ Your Travel Plan",
                    border_style="green"
                )
                console.print(plan_panel)
                
                # Show reasoning steps
                if result.get("intermediate_steps"):
                    console.print("\n🔍 Planning process:", style="dim")
                    for i, step in enumerate(result["intermediate_steps"][:3], 1):
                        console.print(f"  {i}. {step[0].tool}: {step[1][:100]}...", style="dim")
            else:
                console.print(f"❌ Planning failed: {result['error']}", style="red")
            
            console.print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(demo_travel_agent())
```

### Key Features Implemented:

1. **Multi-Destination Weather Comparison**: Analyzes weather across multiple cities with travel recommendations
2. **Document Search Integration**: Finds travel guides, itineraries, and relevant documents
3. **Preference Management**: Stores and retrieves user travel preferences
4. **Intelligent Planning**: Uses LLM reasoning to create comprehensive travel plans
5. **Travel-Specific Tools**: Custom tools designed specifically for travel planning workflows

### Advanced Extensions:

```python
# Additional tool for budget analysis
async def analyze_travel_budget(destination_data: str):
    """Analyze and estimate travel budget based on destinations and preferences."""
    try:
        # Parse destination and preference data
        data = json.loads(destination_data) if destination_data.startswith('{') else {"destination": destination_data}
        
        # Simulate budget analysis
        base_costs = {
            "London": {"accommodation": 120, "food": 50, "activities": 40},
            "Paris": {"accommodation": 100, "food": 45, "activities": 35},
            "Tokyo": {"accommodation": 80, "food": 40, "activities": 30},
            "New York": {"accommodation": 150, "food": 60, "activities": 50},
            "Sydney": {"accommodation": 110, "food": 55, "activities": 45}
        }
        
        destination = data.get("destination", "London")
        days = data.get("days", 3)
        
        if destination in base_costs:
            costs = base_costs[destination]
            total_daily = sum(costs.values())
            total_trip = total_daily * days
            
            budget_analysis = {
                "destination": destination,
                "duration_days": days,
                "daily_breakdown": costs,
                "daily_total": total_daily,
                "trip_total": total_trip,
                "budget_tier": "moderate" if total_trip < 1000 else "premium",
                "currency": "USD"
            }
        else:
            budget_analysis = {
                "error": f"Budget data not available for {destination}",
                "available_destinations": list(base_costs.keys())
            }
        
        return json.dumps(budget_analysis, indent=2)
        
    except Exception as e:
        return f"Budget analysis failed: {str(e)}"
```

### Testing Scenarios:

1. **Basic Trip Planning**: "Plan a weekend trip to Paris"
2. **Multi-City Comparison**: "Compare London vs Berlin for a spring vacation"
3. **Business Travel**: "Need weather and logistics for a business trip to Tokyo"
4. **Budget-Conscious Planning**: "Plan a budget trip to Sydney with outdoor activities"
5. **Seasonal Planning**: "Best time to visit New York for photography"

This solution demonstrates how to build specialized agents that combine multiple MCP servers into domain-specific workflows, providing comprehensive and actionable results.