# Complete Research Workflow Implementation
# This is the full implementation referenced in Session 3

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