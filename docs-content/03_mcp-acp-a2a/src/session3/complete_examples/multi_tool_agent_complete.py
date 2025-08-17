# Complete Multi-Tool Agent Implementation
# This is the full implementation referenced in Session 3

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