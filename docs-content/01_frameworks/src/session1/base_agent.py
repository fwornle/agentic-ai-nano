# src/session1/base_agent.py
"""
Foundation classes for building agents from scratch.
Provides base agent architecture with message processing, tool management,
and communication patterns.
"""

import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime


@dataclass
class AgentMessage:
    """Standard message format for agent communication"""
    id: str
    sender: str
    recipient: str
    content: str
    message_type: str
    timestamp: datetime
    metadata: Dict[str, Any]


class Tool(ABC):
    """Abstract base class for agent tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema for agent discovery"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters()
        }
    
    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        """Return parameter schema for this tool"""
        pass


class BaseAgent:
    """Foundation class for all agent implementations"""
    
    def __init__(
        self, 
        name: str, 
        description: str,
        llm_client: Optional[Any] = None,
        tools: Optional[List[Tool]] = None,
        memory: Optional[Dict[str, Any]] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.memory = memory or {}
        self.conversation_history = []
        self.logger = logging.getLogger(f"agent.{self.name}")

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process a message and return response"""
        self.logger.info(f"Processing message: {message[:100]}...")
        
        # Three-step pipeline
        self._store_user_message(message, context)
        response = await self._generate_response(message, context)  
        self._store_agent_response(response)
        
        return response

    def _store_user_message(self, message: str, context: Optional[Dict]):
        """Store user message in conversation history"""
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now(),
            "context": context
        })

    def _store_agent_response(self, response: str):
        """Store agent response in conversation history"""
        self.conversation_history.append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now()
        })

    @abstractmethod
    async def _generate_response(self, message: str, context: Optional[Dict] = None) -> str:
        """Generate response - implemented by specific agent types"""
        pass

    def add_tool(self, tool: Tool):
        """Add a tool to the agent's toolkit"""
        self.tools[tool.name] = tool
        self.logger.info(f"Added tool: {tool.name}")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tool schemas"""
        return [tool.get_schema() for tool in self.tools.values()]

    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with parameters"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not available")
        
        self.logger.info(f"Executing tool: {tool_name} with args: {kwargs}")
        
        try:
            result = await self.tools[tool_name].execute(**kwargs)
            self.logger.info(f"Tool {tool_name} executed successfully")
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"Tool {tool_name} execution failed: {str(e)}")
            return {"success": False, "error": str(e)}