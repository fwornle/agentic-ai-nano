# Session 6: First ADK Agent - Code-Along Tutorial

## 🎯 Learning Objectives
- Understand Agent Development Kit (ADK) architecture
- Create your first ADK agent with Gemini integration
- Connect ADK agents to MCP servers
- Implement agent memory and conversation state
- Deploy agents to Google Cloud Platform

## 📚 Pre-Session Reading
- [ADK Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit)
- [Currency Agent Codelab](https://codelabs.developers.google.com/codelabs/currency-agent#0)
- [Gemini API Guide](https://ai.google.dev/gemini-api/docs)

---

## Part 1: ADK Environment Setup (15 minutes)

### Step 1.1: Create ADK Project Structure
```bash
# Create project directory
mkdir adk-agent-tutorial
cd adk-agent-tutorial

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install google-cloud-aiplatform google-cloud-vertexai \
            fastapi uvicorn pydantic google-auth \
            requests python-dotenv aiohttp
```

### Step 1.2: Project Structure
```
adk-agent-tutorial/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── weather_agent.py
│   └── data_agent.py
├── mcp_servers/
│   ├── weather_server.py
│   └── data_server.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── utils/
│   ├── __init__.py
│   ├── memory.py
│   └── conversation.py
├── main.py
├── requirements.txt
└── .env
```

### Step 1.3: Configuration Setup
```python
# config/settings.py
import os
from typing import Dict, Any, List
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class ADKSettings(BaseSettings):
    """Configuration for ADK agents."""
    
    # Google Cloud Configuration
    PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
    LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Gemini Configuration
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048
    
    # MCP Server Configuration
    MCP_SERVERS: Dict[str, Dict[str, Any]] = {
        "weather": {
            "url": "http://localhost:8080",
            "description": "Weather information and forecasts"
        },
        "data": {
            "url": "http://localhost:8081", 
            "description": "Data processing and analysis"
        }
    }
    
    # Agent Configuration
    AGENT_MEMORY_SIZE: int = 1000  # Number of conversation turns to remember
    MAX_CONVERSATION_LENGTH: int = 20  # Max turns per conversation
    
    # Security
    API_KEY: str = os.getenv("API_KEY", "dev-key-123")
    
    class Config:
        env_file = ".env"

settings = ADKSettings()
```

---

## Part 2: Base ADK Agent Implementation (25 minutes)

### Step 2.1: Base Agent Class
```python
# agents/base_agent.py
import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, AsyncIterator
from abc import ABC, abstractmethod

import google.auth
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Part
import aiohttp
import logging

from config.settings import settings
from utils.memory import ConversationMemory
from utils.conversation import ConversationManager

logger = logging.getLogger(__name__)

class BaseADKAgent(ABC):
    """Base class for ADK agents with MCP integration."""
    
    def __init__(self, 
                 agent_name: str,
                 system_instruction: str,
                 capabilities: List[str] = None):
        
        self.agent_id = str(uuid.uuid4())
        self.agent_name = agent_name
        self.system_instruction = system_instruction
        self.capabilities = capabilities or []
        
        # Initialize Vertex AI
        self._initialize_vertex_ai()
        
        # Create Gemini model
        self.model = GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=system_instruction
        )
        
        # Memory and conversation management
        self.memory = ConversationMemory(max_size=settings.AGENT_MEMORY_SIZE)
        self.conversation_manager = ConversationManager()
        
        # MCP connections
        self.mcp_connections: Dict[str, aiohttp.ClientSession] = {}
        self.available_tools: Dict[str, Dict] = {}
        
        # Agent state
        self.active_sessions: Dict[str, ChatSession] = {}
        self.is_initialized = False
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with credentials."""
        try:
            # Set up authentication
            credentials, project = google.auth.default()
            
            # Initialize Vertex AI
            vertexai.init(
                project=settings.PROJECT_ID,
                location=settings.LOCATION,
                credentials=credentials
            )
            
            logger.info(f"Vertex AI initialized for project: {settings.PROJECT_ID}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise
    
    async def initialize(self):
        """Initialize the agent with MCP connections."""
        if self.is_initialized:
            return
        
        logger.info(f"Initializing agent: {self.agent_name}")
        
        # Connect to MCP servers
        await self._connect_mcp_servers()
        
        # Load available tools
        await self._load_mcp_tools()
        
        self.is_initialized = True
        logger.info(f"Agent {self.agent_name} initialized successfully")
    
    async def _connect_mcp_servers(self):
        """Connect to configured MCP servers."""
        for server_name, server_config in settings.MCP_SERVERS.items():
            try:
                session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30)
                )
                
                # Test connection
                async with session.get(f"{server_config['url']}/health") as response:
                    if response.status == 200:
                        self.mcp_connections[server_name] = session
                        logger.info(f"Connected to MCP server: {server_name}")
                    else:
                        logger.warning(f"MCP server {server_name} health check failed")
                        await session.close()
                        
            except Exception as e:
                logger.error(f"Failed to connect to MCP server {server_name}: {e}")
    
    async def _load_mcp_tools(self):
        """Load available tools from MCP servers."""
        for server_name, session in self.mcp_connections.items():
            try:
                server_config = settings.MCP_SERVERS[server_name]
                
                # Get tools list
                async with session.post(
                    f"{server_config['url']}/mcp",
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "params": {},
                        "id": 1
                    }
                ) as response:
                    data = await response.json()
                    
                    if "result" in data:
                        for tool in data["result"]:
                            tool_name = f"{server_name}_{tool['name']}"
                            self.available_tools[tool_name] = {
                                "server": server_name,
                                "original_name": tool["name"],
                                "description": tool.get("description", ""),
                                "parameters": tool.get("inputSchema", {})
                            }
                        
                        logger.info(f"Loaded {len(data['result'])} tools from {server_name}")
                        
            except Exception as e:
                logger.error(f"Failed to load tools from {server_name}: {e}")
    
    async def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool {tool_name} not available")
        
        tool_info = self.available_tools[tool_name]
        server_name = tool_info["server"]
        original_name = tool_info["original_name"]
        
        if server_name not in self.mcp_connections:
            raise ValueError(f"MCP server {server_name} not connected")
        
        session = self.mcp_connections[server_name]
        server_config = settings.MCP_SERVERS[server_name]
        
        try:
            async with session.post(
                f"{server_config['url']}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": original_name,
                        "arguments": parameters
                    },
                    "id": 1
                }
            ) as response:
                data = await response.json()
                
                if "error" in data:
                    raise Exception(f"MCP tool error: {data['error']}")
                
                return data.get("result", {})
                
        except Exception as e:
            logger.error(f"Failed to call MCP tool {tool_name}: {e}")
            raise
    
    async def start_conversation(self, user_id: str) -> str:
        """Start a new conversation session."""
        session_id = str(uuid.uuid4())
        
        # Create chat session
        chat_session = self.model.start_chat()
        self.active_sessions[session_id] = chat_session
        
        # Initialize conversation memory
        await self.memory.start_conversation(session_id, user_id)
        
        logger.info(f"Started conversation {session_id} for user {user_id}")
        return session_id
    
    async def send_message(self, session_id: str, message: str, 
                          user_id: str = None) -> str:
        """Send message to agent and get response."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        chat_session = self.active_sessions[session_id]
        
        # Store user message in memory
        await self.memory.add_message(session_id, "user", message)
        
        try:
            # Check if message requires tool use
            tool_calls = await self._analyze_message_for_tools(message)
            
            # Prepare context with tool information
            context = await self._prepare_context(session_id, tool_calls)
            
            # Generate response
            response = await self._generate_response(
                chat_session, message, context, tool_calls
            )
            
            # Store assistant response
            await self.memory.add_message(session_id, "assistant", response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_response = "I apologize, but I encountered an error processing your request. Please try again."
            await self.memory.add_message(session_id, "assistant", error_response)
            return error_response
    
    async def _analyze_message_for_tools(self, message: str) -> List[Dict[str, Any]]:
        """Analyze message to determine if tools are needed."""
        # Simple keyword-based analysis (in production, use more sophisticated NLP)
        tool_calls = []
        
        message_lower = message.lower()
        
        # Weather tools
        if any(word in message_lower for word in ["weather", "temperature", "rain", "forecast"]):
            if "weather_get_weather" in self.available_tools:
                tool_calls.append({
                    "tool": "weather_get_weather",
                    "reason": "Weather information requested",
                    "confidence": 0.8
                })
        
        # Data processing tools
        if any(word in message_lower for word in ["analyze", "process", "data", "calculate"]):
            if "data_process_data" in self.available_tools:
                tool_calls.append({
                    "tool": "data_process_data", 
                    "reason": "Data processing requested",
                    "confidence": 0.7
                })
        
        return tool_calls
    
    async def _prepare_context(self, session_id: str, 
                              tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare context for response generation."""
        # Get conversation history
        history = await self.memory.get_conversation_history(session_id)
        
        # Get available tools summary
        tools_summary = {
            name: info["description"] 
            for name, info in self.available_tools.items()
        }
        
        return {
            "conversation_history": history[-5:],  # Last 5 messages
            "available_tools": tools_summary,
            "suggested_tools": tool_calls,
            "agent_capabilities": self.capabilities
        }
    
    async def _generate_response(self, chat_session: ChatSession, 
                                message: str, context: Dict[str, Any],
                                tool_calls: List[Dict[str, Any]]) -> str:
        """Generate response using Gemini with tool integration."""
        
        # Execute tool calls if needed
        tool_results = []
        for tool_call in tool_calls:
            if tool_call["confidence"] > 0.6:  # Only use high-confidence tools
                try:
                    # Extract parameters from message (simplified)
                    parameters = await self._extract_tool_parameters(
                        message, tool_call["tool"]
                    )
                    
                    # Call the tool
                    result = await self.call_mcp_tool(tool_call["tool"], parameters)
                    tool_results.append({
                        "tool": tool_call["tool"],
                        "result": result
                    })
                    
                except Exception as e:
                    logger.error(f"Tool call failed: {e}")
                    tool_results.append({
                        "tool": tool_call["tool"],
                        "error": str(e)
                    })
        
        # Prepare enhanced prompt
        enhanced_message = await self._create_enhanced_prompt(
            message, context, tool_results
        )
        
        # Get response from Gemini
        response = chat_session.send_message(enhanced_message)
        
        return response.text
    
    async def _extract_tool_parameters(self, message: str, tool_name: str) -> Dict[str, Any]:
        """Extract parameters for tool from message."""
        # Simplified parameter extraction
        # In production, use more sophisticated NLP or structured prompting
        
        if "weather" in tool_name:
            # Look for city names
            import re
            cities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', message)
            city = cities[0] if cities else "London"
            return {"city": city}
        
        elif "data" in tool_name:
            return {"data": {"message": message}, "operation": "analyze"}
        
        return {}
    
    async def _create_enhanced_prompt(self, message: str, 
                                     context: Dict[str, Any],
                                     tool_results: List[Dict[str, Any]]) -> str:
        """Create enhanced prompt with context and tool results."""
        
        prompt_parts = [f"User message: {message}"]
        
        # Add tool results if available
        if tool_results:
            prompt_parts.append("\nTool Results:")
            for result in tool_results:
                if "error" in result:
                    prompt_parts.append(f"- {result['tool']}: Error - {result['error']}")
                else:
                    prompt_parts.append(f"- {result['tool']}: {json.dumps(result['result'], indent=2)}")
        
        # Add conversation context
        if context.get("conversation_history"):
            prompt_parts.append("\nRecent conversation:")
            for msg in context["conversation_history"][-3:]:
                prompt_parts.append(f"- {msg['role']}: {msg['content'][:100]}...")
        
        prompt_parts.append("\nPlease provide a helpful, natural response based on the above information.")
        
        return "\n".join(prompt_parts)
    
    async def end_conversation(self, session_id: str):
        """End a conversation session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        await self.memory.end_conversation(session_id)
        logger.info(f"Ended conversation {session_id}")
    
    async def cleanup(self):
        """Clean up resources."""
        # Close MCP connections
        for session in self.mcp_connections.values():
            await session.close()
        
        self.mcp_connections.clear()
        logger.info(f"Agent {self.agent_name} cleaned up")
    
    @abstractmethod
    async def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information for A2A protocol."""
        pass
```

### Step 2.2: Memory Management
```python
# utils/memory.py
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Represents a conversation message."""
    id: str
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    metadata: Dict[str, Any] = None

class ConversationMemory:
    """Manages conversation memory for agents."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.session_metadata: Dict[str, Dict[str, Any]] = {}
        
    async def start_conversation(self, session_id: str, user_id: str):
        """Start a new conversation."""
        self.conversations[session_id] = []
        self.session_metadata[session_id] = {
            "user_id": user_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "message_count": 0
        }
        
        logger.info(f"Started conversation memory for session {session_id}")
    
    async def add_message(self, session_id: str, role: str, content: str, 
                         metadata: Dict[str, Any] = None) -> str:
        """Add a message to conversation memory."""
        if session_id not in self.conversations:
            raise ValueError(f"Session {session_id} not found")
        
        message_id = f"{session_id}_{len(self.conversations[session_id])}"
        
        message = ConversationMessage(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {}
        )
        
        self.conversations[session_id].append(message)
        self.session_metadata[session_id]["message_count"] += 1
        
        # Trim conversation if too long
        if len(self.conversations[session_id]) > self.max_size:
            self.conversations[session_id] = self.conversations[session_id][-self.max_size:]
        
        return message_id
    
    async def get_conversation_history(self, session_id: str, 
                                     limit: int = None) -> List[Dict[str, Any]]:
        """Get conversation history."""
        if session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id]
        if limit:
            messages = messages[-limit:]
        
        return [asdict(msg) for msg in messages]
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation session summary."""
        if session_id not in self.conversations:
            return {}
        
        messages = self.conversations[session_id]
        metadata = self.session_metadata[session_id]
        
        return {
            "session_id": session_id,
            "user_id": metadata.get("user_id"),
            "started_at": metadata.get("started_at"),
            "message_count": len(messages),
            "last_message_at": messages[-1].timestamp if messages else None,
            "summary": await self._generate_summary(messages[-10:])  # Last 10 messages
        }
    
    async def _generate_summary(self, messages: List[ConversationMessage]) -> str:
        """Generate a summary of conversation messages."""
        if not messages:
            return "No messages"
        
        # Simple summary generation
        user_messages = [msg.content for msg in messages if msg.role == "user"]
        topics = []
        
        # Extract key topics (simplified)
        for content in user_messages:
            if "weather" in content.lower():
                topics.append("weather")
            if "data" in content.lower() or "analyze" in content.lower():
                topics.append("data analysis")
        
        if topics:
            return f"Discussion about: {', '.join(set(topics))}"
        else:
            return f"General conversation ({len(messages)} messages)"
    
    async def end_conversation(self, session_id: str):
        """End conversation and clean up."""
        if session_id in self.conversations:
            # In production, you might want to persist this data
            logger.info(f"Ending conversation {session_id} with {len(self.conversations[session_id])} messages")
            del self.conversations[session_id]
        
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]
```

---

## Part 3: Specialized Weather Agent (20 minutes)

### Step 3.1: Weather Agent Implementation
```python
# agents/weather_agent.py
import json
from typing import Dict, List, Any
from agents.base_agent import BaseADKAgent

class WeatherAgent(BaseADKAgent):
    """Specialized agent for weather information and analysis."""
    
    def __init__(self):
        system_instruction = """You are a professional weather assistant agent.
        
Your capabilities include:
- Providing current weather information for any city
- Weather forecasts and predictions
- Weather-related advice and recommendations
- Travel weather planning
- Weather alert notifications

You have access to real-time weather data through MCP tools. Always use the weather tools when users ask about weather conditions, forecasts, or weather-related questions.

Provide responses that are:
- Accurate and based on real data
- Helpful and actionable
- Easy to understand
- Conversational and friendly

When using weather tools, interpret the data and provide meaningful insights rather than just raw data."""

        capabilities = [
            "current_weather_lookup",
            "weather_forecasting", 
            "weather_alerts",
            "travel_weather_advice",
            "weather_data_analysis"
        ]
        
        super().__init__(
            agent_name="WeatherAgent",
            system_instruction=system_instruction,
            capabilities=capabilities
        )
    
    async def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information for A2A protocol."""
        return {
            "agent_id": self.agent_id,
            "name": self.agent_name,
            "description": "Professional weather assistant providing current conditions, forecasts, and weather-related advice",
            "capabilities": self.capabilities,
            "version": "1.0.0",
            "supported_languages": ["en"],
            "category": "weather",
            "specializations": [
                "current_weather",
                "forecasts",
                "weather_alerts",
                "travel_planning"
            ],
            "mcp_servers": list(settings.MCP_SERVERS.keys()),
            "status": "active" if self.is_initialized else "inactive"
        }
    
    async def _analyze_message_for_tools(self, message: str) -> List[Dict[str, Any]]:
        """Enhanced weather-specific tool analysis."""
        tool_calls = []
        message_lower = message.lower()
        
        # Weather information requests
        weather_keywords = [
            "weather", "temperature", "temp", "hot", "cold", "rain", "snow",
            "sunny", "cloudy", "forecast", "climate", "humidity", "wind"
        ]
        
        if any(keyword in message_lower for keyword in weather_keywords):
            # Determine if it's current weather or forecast
            if any(word in message_lower for word in ["forecast", "tomorrow", "week", "days"]):
                tool_calls.append({
                    "tool": "weather_get_weather",
                    "reason": "Weather forecast requested",
                    "confidence": 0.9,
                    "parameters_hint": {"include_forecast": True}
                })
            else:
                tool_calls.append({
                    "tool": "weather_get_weather", 
                    "reason": "Current weather requested",
                    "confidence": 0.95,
                    "parameters_hint": {"include_forecast": False}
                })
        
        # Weather comparison requests
        if any(word in message_lower for word in ["compare", "better", "warmer", "colder"]):
            tool_calls.append({
                "tool": "weather_compare_weather",
                "reason": "Weather comparison requested", 
                "confidence": 0.8
            })
        
        # Weather alerts
        if any(word in message_lower for word in ["alert", "warning", "storm", "severe"]):
            tool_calls.append({
                "tool": "weather_set_weather_alert",
                "reason": "Weather alert requested",
                "confidence": 0.7
            })
        
        return tool_calls
    
    async def _extract_tool_parameters(self, message: str, tool_name: str) -> Dict[str, Any]:
        """Enhanced parameter extraction for weather tools."""
        import re
        
        if "weather_get_weather" in tool_name:
            # Extract city names
            city_patterns = [
                r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "in London"
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+weather',  # "London weather"
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+forecast',  # "London forecast"
            ]
            
            city = None
            for pattern in city_patterns:
                matches = re.findall(pattern, message)
                if matches:
                    city = matches[0]
                    break
            
            # Default to London if no city found
            city = city or "London"
            
            # Check if forecast is needed
            include_forecast = any(word in message.lower() 
                                 for word in ["forecast", "tomorrow", "week", "days"])
            
            return {
                "city": city,
                "include_forecast": include_forecast
            }
        
        elif "weather_compare_weather" in tool_name:
            # Extract multiple cities
            cities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', message)
            # Filter out common words that might be capitalized
            common_words = {"The", "This", "What", "How", "Where", "When", "Weather", "Compare"}
            cities = [city for city in cities if city not in common_words]
            
            return {"cities": cities[:5]}  # Limit to 5 cities
        
        elif "weather_set_weather_alert" in tool_name:
            # Extract alert parameters
            city = re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', message)
            city = city.group(0) if city else "London"
            
            # Determine alert type
            condition = "temperature" 
            threshold = 30.0  # Default threshold
            
            if "rain" in message.lower():
                condition = "precipitation"
                threshold = 0.1
            elif "wind" in message.lower():
                condition = "wind_speed"
                threshold = 50.0
            
            return {
                "city": city,
                "condition": condition,
                "threshold": threshold
            }
        
        return {}
    
    async def handle_weather_query(self, city: str, include_forecast: bool = False) -> str:
        """Handle direct weather queries programmatically."""
        try:
            result = await self.call_mcp_tool("weather_get_weather", {
                "city": city,
                "include_forecast": include_forecast
            })
            
            # Format the response nicely
            current = result.get("current", {})
            response = f"Current weather in {current.get('city', city)}:\n"
            response += f"Temperature: {current.get('temperature')}°{current.get('units', 'C')}\n"
            response += f"Condition: {current.get('condition')}\n"
            response += f"Humidity: {current.get('humidity')}%\n"
            
            if include_forecast and "forecast" in result:
                response += "\n3-Day Forecast:\n"
                for day in result["forecast"]:
                    response += f"• {day['day']}: {day['high']}°/{day['low']}° - {day['condition']}\n"
            
            return response
            
        except Exception as e:
            return f"Sorry, I couldn't get weather information for {city}. Error: {str(e)}"

# Create weather agent instance
weather_agent = WeatherAgent()
```

---

## 🧪 Testing Your Understanding

### Quick Check Questions

1. **What is the primary role of the ADK in agent development?**
   - A) Database management
   - B) Agent orchestration and lifecycle management
   - C) User interface design
   - D) Network communication

2. **How do ADK agents connect to MCP servers?**
   - A) Direct database connections
   - B) HTTP/JSON-RPC protocol
   - C) gRPC streaming
   - D) WebSocket connections

3. **What is the purpose of conversation memory in agents?**
   - A) Store user passwords
   - B) Maintain context across interactions
   - C) Cache tool responses
   - D) Log system errors

4. **How does Vertex AI enhance ADK agents?**
   - A) Provides data storage
   - B) Enables LLM-powered responses
   - C) Manages user authentication
   - D) Handles file uploads

5. **What information should an agent provide for A2A discovery?**
   - A) Database schema
   - B) Agent capabilities and metadata
   - C) User credentials
   - D) System logs

### Practical Exercise

Create a data analysis agent that:
1. Connects to a data processing MCP server
2. Can analyze CSV data and generate insights
3. Maintains conversation context about data analyses
4. Provides structured responses with charts/summaries

```python
class DataAnalysisAgent(BaseADKAgent):
    """Agent for data analysis and insights."""
    
    def __init__(self):
        # TODO: Implement data analysis agent
        pass
    
    async def analyze_dataset(self, data_description: str) -> Dict[str, Any]:
        """Analyze a dataset and provide insights."""
        # TODO: Implement data analysis logic
        pass
```

---

## 📝 Session Summary

You've learned to:
- ✅ Set up ADK development environment
- ✅ Create base agent class with MCP integration
- ✅ Implement conversation memory and state management
- ✅ Build specialized weather agent with tool integration
- ✅ Connect agents to Vertex AI and Gemini models
- ✅ Handle tool parameter extraction and response generation

### Next Session Preview
In Session 7, we'll build multi-tool agent systems:
- Coordinate multiple MCP servers
- Implement complex agent workflows
- Add agent-to-agent communication
- Create agent orchestration patterns

### Homework
1. Create a travel planning agent that combines weather and location data
2. Add persistent memory storage using Cloud Firestore
3. Implement agent performance monitoring and metrics
4. Build a conversation flow debugger

### Answer Key
1. B) Agent orchestration and lifecycle management
2. B) HTTP/JSON-RPC protocol  
3. B) Maintain context across interactions
4. B) Enables LLM-powered responses
5. B) Agent capabilities and metadata

---

## Additional Resources
- [Vertex AI Agent Builder](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder)
- [Gemini API Documentation](https://ai.google.dev/gemini-api)
- [Google Cloud ADK Examples](https://github.com/GoogleCloudPlatform/adk-examples)