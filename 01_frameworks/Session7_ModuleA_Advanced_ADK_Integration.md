# Session 7 - Module A: Advanced ADK Integration (35 minutes)

**Prerequisites**: [Session 7 Core Section Complete](Session7_First_ADK_Agent.md)  
**Target Audience**: Developers building production ADK agents  
**Cognitive Load**: 4 advanced concepts

---

## 🎯 Module Overview

This module explores sophisticated ADK (Agent Development Kit) integration patterns including advanced Gemini model usage, MCP server orchestration, conversation memory systems, and production deployment strategies. You'll learn to build enterprise-grade ADK agents that can handle complex workflows with persistent state and multi-service coordination.

### Learning Objectives
By the end of this module, you will:
- Implement advanced Gemini model integration with function calling and streaming
- Design sophisticated MCP server orchestration for multi-service coordination
- Build persistent conversation memory systems with context-aware responses
- Create production deployment strategies for Google Cloud Platform

---

## Part 1: Advanced Gemini Integration (20 minutes)

### Sophisticated Model Configuration

🗂️ **File**: `src/session7/advanced_gemini.py` - Advanced Gemini model patterns

Beyond basic chat, enterprise ADK agents require sophisticated Gemini integration with function calling, streaming, and advanced configuration:

```python
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import json
import logging
from enum import Enum

import vertexai
from vertexai.generative_models import (
    GenerativeModel, 
    Tool, 
    FunctionDeclaration,
    Part,
    Content,
    ChatSession
)
from google.cloud import aiplatform

class ModelCapability(Enum):
    """ADK agent model capabilities"""
    TEXT_GENERATION = "text_generation"
    FUNCTION_CALLING = "function_calling"
    CODE_GENERATION = "code_generation"
    MULTIMODAL = "multimodal"
    STREAMING = "streaming"

@dataclass
class ModelConfiguration:
    """Advanced Gemini model configuration"""
    model_name: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_output_tokens: int = 2048
    top_p: float = 0.8
    top_k: int = 40
    
    # Advanced features
    enable_function_calling: bool = True
    enable_streaming: bool = False
    enable_safety_settings: bool = True
    
    # Performance tuning
    request_timeout: int = 60
    retry_count: int = 3
    concurrent_requests: int = 5

class AdvancedGeminiAgent:
    """Production-ready Gemini agent with advanced capabilities"""
    
    def __init__(self, config: ModelConfiguration, project_id: str, location: str):
        self.config = config
        self.project_id = project_id
        self.location = location
        self.logger = logging.getLogger(__name__)
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Model and session management
        self.model: Optional[GenerativeModel] = None
        self.chat_session: Optional[ChatSession] = None
        self.function_registry: Dict[str, Callable] = {}
        self.tool_declarations: List[FunctionDeclaration] = []
        
        # Performance tracking
        self.request_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "function_calls": 0
        }
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Gemini model with advanced configuration"""
        
        try:
            # Configure safety settings
            safety_settings = None
            if self.config.enable_safety_settings:
                from vertexai.generative_models import HarmCategory, HarmBlockThreshold
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            
            # Generation configuration
            generation_config = {
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_output_tokens,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k
            }
            
            # Create tools if function calling is enabled
            tools = None
            if self.config.enable_function_calling and self.tool_declarations:
                tools = [Tool(function_declarations=self.tool_declarations)]
            
            # Initialize model
            self.model = GenerativeModel(
                model_name=self.config.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools
            )
            
            # Initialize chat session
            self.chat_session = self.model.start_chat()
            
            self.logger.info(f"Initialized Gemini model: {self.config.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    def register_function(self, name: str, description: str, 
                         parameters: Dict[str, Any], 
                         function: Callable):
        """Register a function for Gemini function calling"""
        
        # Create function declaration
        function_declaration = FunctionDeclaration(
            name=name,
            description=description,
            parameters=parameters
        )
        
        self.tool_declarations.append(function_declaration)
        self.function_registry[name] = function
        
        # Reinitialize model with new tools
        self._initialize_model()
        
        self.logger.info(f"Registered function: {name}")
    
    async def generate_response(self, prompt: str, 
                              context: Dict[str, Any] = None,
                              use_streaming: bool = None) -> str:
        """Generate response with advanced features"""
        
        if use_streaming is None:
            use_streaming = self.config.enable_streaming
        
        start_time = datetime.now()
        
        try:
            self.request_metrics["total_requests"] += 1
            
            # Prepare context-enhanced prompt
            enhanced_prompt = self._enhance_prompt_with_context(prompt, context or {})
            
            if use_streaming:
                response = await self._generate_streaming_response(enhanced_prompt)
            else:
                response = await self._generate_standard_response(enhanced_prompt)
            
            # Update metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(response_time, success=True)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            self._update_metrics(0, success=False)
            raise
    
    async def _generate_standard_response(self, prompt: str) -> str:
        """Generate standard response with function calling support"""
        
        response = await self.chat_session.send_message_async(prompt)
        
        # Check if function calling is required
        if response.candidates[0].function_calls:
            # Handle function calls
            function_responses = await self._handle_function_calls(
                response.candidates[0].function_calls
            )
            
            # Send function responses back to model
            response = await self.chat_session.send_message_async(function_responses)
        
        return response.text
    
    async def _generate_streaming_response(self, prompt: str) -> str:
        """Generate streaming response for real-time applications"""
        
        response_chunks = []
        
        async for chunk in self.chat_session.send_message_async(prompt, stream=True):
            if chunk.text:
                response_chunks.append(chunk.text)
                # Yield partial response for real-time display
                yield chunk.text
        
        return "".join(response_chunks)
    
    async def _handle_function_calls(self, function_calls: List[Any]) -> List[Part]:
        """Handle function calls from Gemini model"""
        
        function_responses = []
        
        for function_call in function_calls:
            function_name = function_call.name
            function_args = function_call.args
            
            self.request_metrics["function_calls"] += 1
            
            if function_name in self.function_registry:
                try:
                    # Execute registered function
                    function_impl = self.function_registry[function_name]
                    
                    if asyncio.iscoroutinefunction(function_impl):
                        result = await function_impl(**function_args)
                    else:
                        result = function_impl(**function_args)
                    
                    # Create function response
                    function_response = Part.from_function_response(
                        name=function_name,
                        response={"result": result}
                    )
                    function_responses.append(function_response)
                    
                except Exception as e:
                    self.logger.error(f"Function {function_name} execution failed: {e}")
                    error_response = Part.from_function_response(
                        name=function_name,
                        response={"error": str(e)}
                    )
                    function_responses.append(error_response)
            else:
                self.logger.warning(f"Unknown function called: {function_name}")
        
        return function_responses
    
    def _enhance_prompt_with_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with contextual information"""
        
        if not context:
            return prompt
        
        context_parts = []
        
        # Add user context
        if "user_id" in context:
            context_parts.append(f"User ID: {context['user_id']}")
        
        # Add conversation context
        if "conversation_history" in context:
            history = context["conversation_history"]
            if history:
                context_parts.append("Recent conversation:")
                for turn in history[-3:]:  # Last 3 turns
                    role = turn.get("role", "unknown")
                    content = turn.get("content", "")
                    context_parts.append(f"  {role}: {content[:100]}...")
        
        # Add business context
        if "business_context" in context:
            business_ctx = context["business_context"]
            context_parts.append(f"Business context: {business_ctx}")
        
        # Add temporal context
        context_parts.append(f"Current time: {datetime.now().isoformat()}")
        
        if context_parts:
            enhanced_prompt = f"""Context:
{chr(10).join(context_parts)}

User request: {prompt}"""
            return enhanced_prompt
        
        return prompt
    
    def _update_metrics(self, response_time: float, success: bool):
        """Update performance metrics"""
        
        if success:
            self.request_metrics["successful_requests"] += 1
        else:
            self.request_metrics["failed_requests"] += 1
        
        # Update average response time
        total_successful = self.request_metrics["successful_requests"]
        if total_successful > 0:
            current_avg = self.request_metrics["average_response_time"]
            new_avg = ((current_avg * (total_successful - 1)) + response_time) / total_successful
            self.request_metrics["average_response_time"] = new_avg

class MCPGeminiOrchestrator:
    """Orchestrates multiple MCP services with Gemini intelligence"""
    
    def __init__(self, gemini_agent: AdvancedGeminiAgent):
        self.gemini_agent = gemini_agent
        self.mcp_services: Dict[str, Any] = {}
        self.service_capabilities: Dict[str, List[str]] = {}
        self.orchestration_history: List[Dict[str, Any]] = []
        
    def register_mcp_service(self, service_name: str, 
                           service_client: Any, 
                           capabilities: List[str]):
        """Register MCP service with its capabilities"""
        
        self.mcp_services[service_name] = service_client
        self.service_capabilities[service_name] = capabilities
        
        # Register service functions with Gemini
        self._register_service_functions(service_name, capabilities)
    
    def _register_service_functions(self, service_name: str, capabilities: List[str]):
        """Register MCP service functions with Gemini"""
        
        for capability in capabilities:
            function_name = f"{service_name}_{capability}"
            
            # Create function declaration
            parameters = {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"Query for {capability} in {service_name}"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Additional parameters for the service call"
                    }
                },
                "required": ["query"]
            }
            
            # Create wrapper function
            async def service_function(query: str, parameters: Dict[str, Any] = None):
                return await self._call_mcp_service(service_name, capability, query, parameters or {})
            
            self.gemini_agent.register_function(
                name=function_name,
                description=f"Use {service_name} service for {capability}",
                parameters=parameters,
                function=service_function
            )
    
    async def _call_mcp_service(self, service_name: str, 
                               capability: str, 
                               query: str, 
                               parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP service with error handling and logging"""
        
        service_client = self.mcp_services.get(service_name)
        if not service_client:
            return {"error": f"Service {service_name} not available"}
        
        try:
            # Record orchestration attempt
            orchestration_record = {
                "timestamp": datetime.now(),
                "service": service_name,
                "capability": capability,
                "query": query,
                "parameters": parameters
            }
            
            # Call MCP service
            result = await service_client.call_tool(capability, {
                "query": query,
                **parameters
            })
            
            orchestration_record["result"] = result
            orchestration_record["status"] = "success"
            
            self.orchestration_history.append(orchestration_record)
            return result
            
        except Exception as e:
            error_result = {"error": str(e)}
            orchestration_record["result"] = error_result
            orchestration_record["status"] = "error"
            
            self.orchestration_history.append(orchestration_record)
            return error_result
    
    async def intelligent_service_selection(self, user_query: str) -> Dict[str, Any]:
        """Use Gemini to intelligently select and orchestrate MCP services"""
        
        # Analyze query to determine required services
        analysis_prompt = f"""
        Analyze this user query and determine which services would be most helpful:
        Query: "{user_query}"
        
        Available services and their capabilities:
        {self._format_service_capabilities()}
        
        Respond with a JSON object indicating:
        1. Which services to use
        2. What specific capabilities to invoke
        3. The order of operations
        4. Any parameters needed
        """
        
        service_plan = await self.gemini_agent.generate_response(analysis_prompt)
        
        try:
            # Parse service execution plan
            plan = json.loads(service_plan)
            execution_results = []
            
            # Execute services according to plan
            for step in plan.get("steps", []):
                service_name = step.get("service")
                capability = step.get("capability")
                query = step.get("query", user_query)
                parameters = step.get("parameters", {})
                
                result = await self._call_mcp_service(
                    service_name, capability, query, parameters
                )
                execution_results.append({
                    "step": step,
                    "result": result
                })
            
            return {
                "plan": plan,
                "execution_results": execution_results,
                "status": "completed"
            }
            
        except json.JSONDecodeError:
            # Fallback to direct service calls
            return await self._fallback_service_execution(user_query)
    
    def _format_service_capabilities(self) -> str:
        """Format service capabilities for Gemini analysis"""
        
        formatted = []
        for service_name, capabilities in self.service_capabilities.items():
            caps_str = ", ".join(capabilities)
            formatted.append(f"- {service_name}: {caps_str}")
        
        return "\n".join(formatted)
```

---

## Part 2: Production Memory and Context Systems (15 minutes)

### Advanced Conversation Memory

🗂️ **File**: `src/session7/advanced_memory.py` - Production memory systems

```python
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3
import asyncio
import threading
from enum import Enum

class MemoryType(Enum):
    """Types of memory for different use cases"""
    SHORT_TERM = "short_term"      # Current conversation
    LONG_TERM = "long_term"        # Persistent user history
    WORKING = "working"            # Active task context
    EPISODIC = "episodic"         # Specific event memories
    SEMANTIC = "semantic"         # General knowledge

@dataclass
class MemoryEntry:
    """Individual memory entry with metadata"""
    content: str
    memory_type: MemoryType
    timestamp: datetime
    importance: float = 0.5  # 0.0 to 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "context": self.context,
            "tags": self.tags,
            "embedding": self.embedding
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        return cls(
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            importance=data.get("importance", 0.5),
            context=data.get("context", {}),
            tags=data.get("tags", []),
            embedding=data.get("embedding")
        )

class AdvancedConversationMemory:
    """Advanced memory system with multiple memory types and persistence"""
    
    def __init__(self, user_id: str, db_path: str = "agent_memory.db"):
        self.user_id = user_id
        self.db_path = db_path
        self.memories: Dict[MemoryType, List[MemoryEntry]] = {
            memory_type: [] for memory_type in MemoryType
        }
        self.memory_lock = threading.Lock()
        
        # Configuration
        self.max_short_term_memories = 50
        self.max_working_memories = 20
        self.importance_threshold = 0.3
        self.retention_days = 90
        
        # Initialize database
        self._initialize_database()
        self._load_memories()
    
    def _initialize_database(self):
        """Initialize SQLite database for memory persistence"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    importance REAL NOT NULL,
                    context TEXT,
                    tags TEXT,
                    embedding TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_type_time 
                ON memories(user_id, memory_type, timestamp)
            """)
    
    def _load_memories(self):
        """Load memories from database"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT content, memory_type, timestamp, importance, context, tags, embedding
                FROM memories 
                WHERE user_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """, (self.user_id, (datetime.now() - timedelta(days=self.retention_days)).isoformat()))
            
            for row in cursor.fetchall():
                content, memory_type, timestamp, importance, context, tags, embedding = row
                
                memory_entry = MemoryEntry(
                    content=content,
                    memory_type=MemoryType(memory_type),
                    timestamp=datetime.fromisoformat(timestamp),
                    importance=importance,
                    context=json.loads(context or "{}"),
                    tags=json.loads(tags or "[]"),
                    embedding=json.loads(embedding) if embedding else None
                )
                
                self.memories[memory_entry.memory_type].append(memory_entry)
    
    def add_memory(self, content: str, memory_type: MemoryType, 
                   importance: float = 0.5, context: Dict[str, Any] = None,
                   tags: List[str] = None):
        """Add new memory entry with automatic management"""
        
        memory_entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now(),
            importance=importance,
            context=context or {},
            tags=tags or []
        )
        
        with self.memory_lock:
            # Add to in-memory storage
            self.memories[memory_type].append(memory_entry)
            
            # Manage memory limits
            self._manage_memory_limits(memory_type)
            
            # Persist to database
            self._persist_memory(memory_entry)
    
    def _manage_memory_limits(self, memory_type: MemoryType):
        """Manage memory limits and cleanup old entries"""
        
        memories = self.memories[memory_type]
        
        if memory_type == MemoryType.SHORT_TERM:
            if len(memories) > self.max_short_term_memories:
                # Keep most recent and most important
                memories.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
                self.memories[memory_type] = memories[:self.max_short_term_memories]
        
        elif memory_type == MemoryType.WORKING:
            if len(memories) > self.max_working_memories:
                # Keep most recent working memories
                memories.sort(key=lambda m: m.timestamp, reverse=True)
                self.memories[memory_type] = memories[:self.max_working_memories]
        
        # For long-term memories, use importance-based retention
        elif memory_type == MemoryType.LONG_TERM:
            # Remove low-importance old memories
            cutoff_date = datetime.now() - timedelta(days=30)
            self.memories[memory_type] = [
                m for m in memories 
                if m.importance >= self.importance_threshold or m.timestamp > cutoff_date
            ]
    
    def _persist_memory(self, memory_entry: MemoryEntry):
        """Persist memory entry to database"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories (user_id, content, memory_type, timestamp, 
                                    importance, context, tags, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.user_id,
                memory_entry.content,
                memory_entry.memory_type.value,
                memory_entry.timestamp.isoformat(),
                memory_entry.importance,
                json.dumps(memory_entry.context),
                json.dumps(memory_entry.tags),
                json.dumps(memory_entry.embedding) if memory_entry.embedding else None
            ))
    
    def retrieve_relevant_memories(self, query: str, 
                                 memory_types: List[MemoryType] = None,
                                 max_memories: int = 10) -> List[MemoryEntry]:
        """Retrieve memories relevant to a query"""
        
        if memory_types is None:
            memory_types = list(MemoryType)
        
        relevant_memories = []
        
        with self.memory_lock:
            for memory_type in memory_types:
                for memory in self.memories[memory_type]:
                    # Simple relevance scoring (could be enhanced with embeddings)
                    relevance_score = self._calculate_relevance(query, memory)
                    
                    if relevance_score > 0.1:  # Minimum relevance threshold
                        relevant_memories.append((memory, relevance_score))
        
        # Sort by relevance and return top memories
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in relevant_memories[:max_memories]]
    
    def _calculate_relevance(self, query: str, memory: MemoryEntry) -> float:
        """Calculate relevance score between query and memory"""
        
        query_lower = query.lower()
        content_lower = memory.content.lower()
        
        # Simple keyword matching (could be enhanced with semantic similarity)
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        
        if not query_words:
            return 0.0
        
        # Calculate word overlap
        overlap = len(query_words.intersection(content_words))
        relevance = overlap / len(query_words)
        
        # Boost relevance based on importance and recency
        importance_boost = memory.importance * 0.2
        
        # Recency boost (memories from last 24 hours get boost)
        if datetime.now() - memory.timestamp < timedelta(hours=24):
            recency_boost = 0.1
        else:
            recency_boost = 0.0
        
        return min(relevance + importance_boost + recency_boost, 1.0)
    
    def get_conversation_context(self, max_turns: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context for prompt enhancement"""
        
        short_term_memories = self.memories[MemoryType.SHORT_TERM]
        
        # Sort by timestamp and get recent memories
        recent_memories = sorted(
            short_term_memories,
            key=lambda m: m.timestamp,
            reverse=True
        )[:max_turns]
        
        # Convert to conversation format
        context = []
        for memory in reversed(recent_memories):  # Chronological order
            context.append({
                "timestamp": memory.timestamp.isoformat(),
                "content": memory.content,
                "importance": memory.importance,
                "tags": memory.tags
            })
        
        return context
    
    def consolidate_memories(self):
        """Consolidate and organize memories for better retrieval"""
        
        with self.memory_lock:
            # Promote important short-term memories to long-term
            short_term_memories = self.memories[MemoryType.SHORT_TERM]
            
            for memory in short_term_memories[:]:
                if memory.importance >= 0.8:  # High importance threshold
                    # Move to long-term memory
                    memory.memory_type = MemoryType.LONG_TERM
                    self.memories[MemoryType.LONG_TERM].append(memory)
                    self.memories[MemoryType.SHORT_TERM].remove(memory)
                    
                    # Update in database
                    self._update_memory_type(memory)
    
    def _update_memory_type(self, memory: MemoryEntry):
        """Update memory type in database"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE memories 
                SET memory_type = ? 
                WHERE user_id = ? AND content = ? AND timestamp = ?
            """, (
                memory.memory_type.value,
                self.user_id,
                memory.content,
                memory.timestamp.isoformat()
            ))
```

---

## 🎯 Module Summary

You've now mastered advanced ADK integration patterns:

✅ **Advanced Gemini Integration**: Implemented sophisticated model configuration with function calling and streaming  
✅ **MCP Service Orchestration**: Built intelligent multi-service coordination with Gemini-driven selection  
✅ **Production Memory Systems**: Created persistent conversation memory with multiple memory types  
✅ **Enterprise Context Management**: Designed context-aware response generation with relevance scoring

### Next Steps
- **Continue to Module B**: [Enterprise Agent Systems](Session7_ModuleB_Enterprise_Agent_Systems.md) for production deployment patterns
- **Return to Core**: [Session 7 Main](Session7_First_ADK_Agent.md)
- **Advance to Session 8**: [Agno Production Ready Agents](Session8_Agno_Production_Ready_Agents.md)

---

**🗂️ Source Files for Module A:**
- `src/session7/advanced_gemini.py` - Sophisticated Gemini model integration
- `src/session7/advanced_memory.py` - Production memory systems
- `src/session7/mcp_orchestration.py` - Multi-service coordination patterns