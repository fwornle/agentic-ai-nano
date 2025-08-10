# src/session2/langchain_tool_use.py
"""
Tool Use Agent implementation with LangChain framework.
"""

from langchain.agents import Tool, AgentType, initialize_agent, AgentExecutor
from langchain.agents.tools import InvalidTool
from langchain.memory import ConversationBufferMemory
from langchain.tools import DuckDuckGoSearchResults, BaseTool
from langchain_tools import CalculatorTool, weather_tool, email_tool, NewsAPITool
from typing import List, Dict
from datetime import datetime


class LangChainToolAgent:
    """Advanced tool use agent with LangChain"""
    
    def __init__(self, llm, tools: List[Tool] = None):
        self.llm = llm
        self.tools = tools or self._default_tools()
        
        # Create memory for conversation context
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize agent with tools
        self.agent = initialize_agent(
            tools=self.tools,
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
            max_execution_time=30,
            max_iterations=10
        )
    
    def _default_tools(self) -> List[Tool]:
        """Create default tool set"""
        tools = [
            CalculatorTool(),
            weather_tool,
            email_tool
        ]
        
        # Add search tool if available
        try:
            search_tool = DuckDuckGoSearchResults(num_results=5)
            tools.append(search_tool)
        except Exception:
            print("Search tool not available")
        
        return tools
    
    async def process_message(self, message: str) -> str:
        """Process message using available tools"""
        try:
            response = await self.agent.arun(message)
            return response
        except Exception as e:
            return f"Error processing message: {str(e)}"
    
    def add_tool(self, tool: Tool):
        """Add a new tool to the agent"""
        self.tools.append(tool)
        # Reinitialize agent with new tools
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
        )
    
    def get_tool_info(self) -> Dict:
        """Get information about available tools"""
        return {
            "total_tools": len(self.tools),
            "tool_names": [tool.name for tool in self.tools],
            "tool_descriptions": {
                tool.name: tool.description for tool in self.tools
            }
        }


# Custom domain-specific tool
class DatabaseQueryTool(BaseTool):
    """Tool for querying a database"""
    name = "database_query"
    description = "Query database for information about customers, orders, or products"
    
    def _run(self, query: str, table: str) -> str:
        """Execute database query (simulated)"""
        # Simulate database query
        if table.lower() == "customers":
            return f"Found 15 customers matching query: {query}"
        elif table.lower() == "orders":
            return f"Found 8 orders matching query: {query}"
        elif table.lower() == "products":
            return f"Found 23 products matching query: {query}"
        else:
            return f"Table '{table}' not found"

    def _arun(self, query: str, table: str):
        """Async version (if needed)"""
        raise NotImplementedError("Database tool doesn't support async")


# Example usage with custom tools
async def demo_advanced_tool_use():
    from llm_setup import LLMFactory
    
    llm = LLMFactory.create_llm("openai")
    
    # Create agent with custom tools
    custom_tools = [
        CalculatorTool(),
        DatabaseQueryTool(),
        weather_tool
    ]
    
    agent = LangChainToolAgent(llm, custom_tools)
    
    # Test complex tool usage
    response = await agent.process_message(
        "Check the weather in San Francisco, then calculate what our Q4 revenue would be if we had 15% more customers than our current customer count."
    )
    
    print("Agent Response:", response)
    print("Tool Info:", agent.get_tool_info())