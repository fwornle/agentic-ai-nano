# Session 1 - Module C: Complex State Management (30 minutes)

**Prerequisites**: [Session 1 Core Section Complete](Session1_Bare_Metal_Agents.md)  
**Target Audience**: Developers building stateful agent systems  
**Cognitive Load**: 4 state management concepts

---

## 🎯 Module Overview

This module explores sophisticated state management patterns for bare metal agents, including conversation memory, agent state persistence, and dynamic context management. You'll learn how to build agents that maintain complex state across interactions and sessions.

### Learning Objectives
By the end of this module, you will:
- Implement conversation memory systems that scale with long interactions
- Build agent state persistence for session continuity and recovery
- Design dynamic context management for adaptive agent behavior
- Create state synchronization patterns for multi-agent systems

---

## Part 1: Conversation Memory Systems (12 minutes)

### Advanced Memory Architecture

🗂️ **File**: `src/session1/conversation_memory.py` - Advanced memory management systems

Building on the memory optimization patterns, sophisticated conversation memory requires hierarchical storage, semantic indexing, and intelligent retrieval:

```python
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3
from enum import Enum
import numpy as np
from sentence_transformers import SentenceTransformer

class MemoryPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ConversationMemory:
    id: str
    content: str
    timestamp: datetime
    priority: MemoryPriority
    context_tags: List[str] = field(default_factory=list)
    embedding: Optional[np.ndarray] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    related_memories: List[str] = field(default_factory=list)

class HierarchicalMemoryAgent(BaseAgent):
    """Agent with hierarchical memory management and semantic retrieval"""
    
    def __init__(self, name: str, llm_client, memory_db_path: str = "agent_memory.db"):
        super().__init__(name, "Hierarchical memory agent", llm_client)
        self.memory_db_path = memory_db_path
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.working_memory: List[ConversationMemory] = []
        self.working_memory_limit = 20
        self._init_memory_database()
```

### Semantic Memory Retrieval

```python
def store_memory(self, content: str, priority: MemoryPriority = MemoryPriority.MEDIUM, 
                context_tags: List[str] = None) -> str:
    """Store memory with semantic embedding and hierarchy"""
    
    memory_id = f"mem_{datetime.now().timestamp()}"
    
    # Generate semantic embedding
    embedding = self.embedder.encode(content)
    
    # Create memory object
    memory = ConversationMemory(
        id=memory_id,
        content=content,
        timestamp=datetime.now(),
        priority=priority,
        context_tags=context_tags or [],
        embedding=embedding
    )
    
    # Add to working memory
    self.working_memory.append(memory)
    
    # Manage working memory size
    if len(self.working_memory) > self.working_memory_limit:
        self._consolidate_to_long_term()
    
    # Store in persistent database
    self._store_in_database(memory)
    
    return memory_id

def retrieve_relevant_memories(self, query: str, limit: int = 5) -> List[ConversationMemory]:
    """Retrieve memories using semantic similarity and priority"""
    
    # Generate query embedding
    query_embedding = self.embedder.encode(query)
    
    # Search working memory first
    working_candidates = []
    for memory in self.working_memory:
        if memory.embedding is not None:
            similarity = np.dot(query_embedding, memory.embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(memory.embedding)
            )
            working_candidates.append((memory, similarity))
    
    # Search long-term memory
    long_term_candidates = self._search_long_term_memory(query_embedding, limit * 2)
    
    # Combine and rank by relevance and priority
    all_candidates = working_candidates + long_term_candidates
    
    # Score combining similarity and priority
    scored_candidates = []
    for memory, similarity in all_candidates:
        priority_weight = memory.priority.value / 4.0  # Normalize to 0-1
        recency_weight = self._calculate_recency_weight(memory.timestamp)
        access_weight = min(memory.access_count / 10.0, 1.0)  # Normalize access frequency
        
        combined_score = (
            similarity * 0.5 + 
            priority_weight * 0.3 + 
            recency_weight * 0.1 + 
            access_weight * 0.1
        )
        
        scored_candidates.append((memory, combined_score))
    
    # Sort by combined score and return top results
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Update access statistics
    relevant_memories = [mem for mem, score in scored_candidates[:limit]]
    for memory in relevant_memories:
        memory.access_count += 1
        memory.last_accessed = datetime.now()
        self._update_memory_access(memory)
    
    return relevant_memories

def _consolidate_to_long_term(self):
    """Move older, less important memories from working to long-term storage"""
    
    # Sort working memory by importance and recency
    sorted_memories = sorted(
        self.working_memory,
        key=lambda m: (m.priority.value, m.timestamp),
        reverse=True
    )
    
    # Keep high-priority and recent memories in working memory
    to_keep = sorted_memories[:self.working_memory_limit // 2]
    to_archive = sorted_memories[self.working_memory_limit // 2:]
    
    # Archive to long-term storage
    for memory in to_archive:
        self._archive_to_long_term(memory)
    
    # Update working memory
    self.working_memory = to_keep
    
    self.logger.info(f"Consolidated {len(to_archive)} memories to long-term storage")
```

### Memory Context Integration

```python
def generate_contextual_response(self, message: str) -> str:
    """Generate response using relevant memory context"""
    
    # Retrieve relevant memories
    relevant_memories = self.retrieve_relevant_memories(message, limit=3)
    
    # Build context from memories
    memory_context = self._build_memory_context(relevant_memories)
    
    # Generate response with memory-enhanced prompt
    enhanced_prompt = f"""
    Current message: {message}
    
    Relevant conversation history and context:
    {memory_context}
    
    Respond naturally, incorporating relevant context from the conversation history.
    Be specific about details you remember and acknowledge past interactions when relevant.
    """
    
    response = await self._call_llm(enhanced_prompt)
    
    # Store this interaction
    interaction_content = f"User: {message}\nAgent: {response}"
    self.store_memory(
        content=interaction_content,
        priority=MemoryPriority.MEDIUM,
        context_tags=["conversation", "interaction"]
    )
    
    return response

def _build_memory_context(self, memories: List[ConversationMemory]) -> str:
    """Build readable context from retrieved memories"""
    if not memories:
        return "No relevant conversation history found."
    
    context_parts = []
    for i, memory in enumerate(memories, 1):
        timestamp = memory.timestamp.strftime("%Y-%m-%d %H:%M")
        tags = ", ".join(memory.context_tags) if memory.context_tags else "general"
        
        context_parts.append(f"""
        Memory {i} ({timestamp}) - Context: {tags}
        {memory.content}
        """)
    
    return "\n".join(context_parts)
```

---

## Part 2: Agent State Persistence (10 minutes)

### Persistent State Architecture

🗂️ **File**: `src/session1/persistent_state.py` - Agent state persistence systems

```python
import pickle
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class AgentState:
    agent_id: str
    session_id: str
    timestamp: datetime
    conversation_history: List[Dict[str, Any]]
    active_goals: List[str]
    completed_tasks: List[Dict[str, Any]]
    learned_preferences: Dict[str, Any]
    tool_usage_stats: Dict[str, int]
    performance_metrics: Dict[str, float]
    custom_attributes: Dict[str, Any]

class PersistentStateAgent(BaseAgent):
    """Agent with automatic state persistence and recovery"""
    
    def __init__(self, name: str, llm_client, state_dir: str = "agent_states"):
        super().__init__(name, "Persistent state agent", llm_client)
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.state: Optional[AgentState] = None
        self.auto_save_interval = 10  # Save every N interactions
        self.interaction_count = 0
        
    def initialize_or_restore_state(self, agent_id: str) -> AgentState:
        """Initialize new state or restore from previous session"""
        
        state_file = self.state_dir / f"{agent_id}_state.json"
        
        if state_file.exists():
            # Restore previous state
            try:
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                # Convert timestamp back to datetime
                state_data['timestamp'] = datetime.fromisoformat(state_data['timestamp'])
                
                self.state = AgentState(**state_data)
                self.state.session_id = self.session_id  # Update to current session
                
                self.logger.info(f"Restored state for agent {agent_id} from {state_file}")
                return self.state
                
            except Exception as e:
                self.logger.error(f"Failed to restore state: {e}")
                # Fall through to create new state
        
        # Create new state
        self.state = AgentState(
            agent_id=agent_id,
            session_id=self.session_id,
            timestamp=datetime.now(),
            conversation_history=[],
            active_goals=[],
            completed_tasks=[],
            learned_preferences={},
            tool_usage_stats={},
            performance_metrics={},
            custom_attributes={}
        )
        
        self.logger.info(f"Created new state for agent {agent_id}")
        return self.state
    
    def save_state(self, force: bool = False) -> bool:
        """Save current state to persistent storage"""
        
        if not self.state:
            return False
        
        try:
            # Update timestamp
            self.state.timestamp = datetime.now()
            
            # Convert to dictionary for JSON serialization
            state_dict = asdict(self.state)
            state_dict['timestamp'] = self.state.timestamp.isoformat()
            
            # Save to file
            state_file = self.state_dir / f"{self.state.agent_id}_state.json"
            with open(state_file, 'w') as f:
                json.dump(state_dict, f, indent=2)
            
            # Create backup
            backup_file = self.state_dir / f"{self.state.agent_id}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w') as f:
                json.dump(state_dict, f, indent=2)
            
            # Clean old backups (keep last 5)
            self._clean_old_backups(self.state.agent_id)
            
            self.logger.info(f"Saved state to {state_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            return False
```

### State-Aware Processing

```python
async def process_message_with_state(self, message: str, goals: List[str] = None) -> Dict[str, Any]:
    """Process message while maintaining and updating state"""
    
    if not self.state:
        raise ValueError("Agent state not initialized")
    
    # Update active goals if provided
    if goals:
        self.state.active_goals.extend(goals)
        self.state.active_goals = list(set(self.state.active_goals))  # Remove duplicates
    
    # Add to conversation history
    self.state.conversation_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "user_message",
        "content": message,
        "session_id": self.session_id
    })
    
    # Generate response with state context
    state_context = self._build_state_context()
    enhanced_prompt = f"""
    User message: {message}
    
    Agent state context:
    {state_context}
    
    Respond appropriately, considering your ongoing goals and conversation history.
    """
    
    response = await self._call_llm(enhanced_prompt)
    
    # Update state with response
    self.state.conversation_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "agent_response", 
        "content": response,
        "session_id": self.session_id
    })
    
    # Check for goal completion
    completed_goals = self._check_goal_completion(message, response)
    for goal in completed_goals:
        if goal in self.state.active_goals:
            self.state.active_goals.remove(goal)
            self.state.completed_tasks.append({
                "goal": goal,
                "completed_at": datetime.now().isoformat(),
                "session_id": self.session_id
            })
    
    # Auto-save state periodically
    self.interaction_count += 1
    if self.interaction_count % self.auto_save_interval == 0:
        self.save_state()
    
    return {
        "response": response,
        "active_goals": self.state.active_goals.copy(),
        "completed_goals": completed_goals,
        "session_id": self.session_id,
        "state_saved": self.interaction_count % self.auto_save_interval == 0
    }

def _build_state_context(self) -> str:
    """Build readable context from current agent state"""
    context_parts = []
    
    # Active goals
    if self.state.active_goals:
        context_parts.append(f"Active goals: {', '.join(self.state.active_goals)}")
    
    # Recent conversation
    recent_history = self.state.conversation_history[-6:]  # Last 3 exchanges
    if recent_history:
        context_parts.append("Recent conversation:")
        for entry in recent_history:
            context_parts.append(f"  {entry['type']}: {entry['content'][:100]}...")
    
    # Completed tasks
    if self.state.completed_tasks:
        recent_tasks = self.state.completed_tasks[-3:]
        context_parts.append(f"Recently completed: {[task['goal'] for task in recent_tasks]}")
    
    # Learned preferences
    if self.state.learned_preferences:
        context_parts.append(f"Learned preferences: {self.state.learned_preferences}")
    
    return "\n".join(context_parts)
```

---

## Part 3: Dynamic Context Management (8 minutes)

### Adaptive Context Systems

🗂️ **File**: `src/session1/dynamic_context.py` - Dynamic context adaptation

```python
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio

class ContextScope(Enum):
    IMMEDIATE = "immediate"      # Current interaction
    SESSION = "session"          # Current session
    HISTORICAL = "historical"    # Across sessions
    DOMAIN = "domain"           # Subject/domain specific

@dataclass
class ContextLayer:
    scope: ContextScope
    priority: int
    content: Dict[str, Any]
    expiry_time: Optional[datetime] = None
    activation_conditions: List[str] = None

class DynamicContextAgent(BaseAgent):
    """Agent with dynamic, multi-layered context management"""
    
    def __init__(self, name: str, llm_client):
        super().__init__(name, "Dynamic context agent", llm_client)
        self.context_layers: Dict[str, ContextLayer] = {}
        self.context_activation_rules: Dict[str, Callable] = {}
        self.context_history: List[Dict[str, Any]] = []
        
    def add_context_layer(self, layer_id: str, scope: ContextScope, 
                         content: Dict[str, Any], priority: int = 1,
                         expiry_time: Optional[datetime] = None,
                         activation_conditions: List[str] = None) -> str:
        """Add a dynamic context layer"""
        
        layer = ContextLayer(
            scope=scope,
            priority=priority,
            content=content,
            expiry_time=expiry_time,
            activation_conditions=activation_conditions or []
        )
        
        self.context_layers[layer_id] = layer
        
        self.logger.info(f"Added context layer: {layer_id} (scope: {scope.value}, priority: {priority})")
        return layer_id
    
    def activate_context_dynamically(self, message: str, context_hints: List[str] = None) -> Dict[str, Any]:
        """Dynamically determine which context layers to activate"""
        
        activated_contexts = {}
        activation_log = []
        
        for layer_id, layer in self.context_layers.items():
            should_activate = self._should_activate_layer(layer, message, context_hints)
            
            if should_activate:
                # Check if layer has expired
                if layer.expiry_time and datetime.now() > layer.expiry_time:
                    self._remove_expired_layer(layer_id)
                    continue
                
                activated_contexts[layer_id] = layer.content
                activation_log.append({
                    "layer_id": layer_id,
                    "scope": layer.scope.value,
                    "priority": layer.priority,
                    "activation_reason": self._get_activation_reason(layer, message, context_hints)
                })
        
        # Sort by priority
        activation_log.sort(key=lambda x: x["priority"], reverse=True)
        
        return {
            "activated_contexts": activated_contexts,
            "activation_log": activation_log,
            "total_layers": len(activated_contexts)
        }
    
    def _should_activate_layer(self, layer: ContextLayer, message: str, 
                              context_hints: List[str] = None) -> bool:
        """Determine if a context layer should be activated"""
        
        # Always activate immediate scope
        if layer.scope == ContextScope.IMMEDIATE:
            return True
        
        # Check activation conditions
        if layer.activation_conditions:
            for condition in layer.activation_conditions:
                if condition.lower() in message.lower():
                    return True
                if context_hints and condition in context_hints:
                    return True
        
        # Check for domain-specific activation
        if layer.scope == ContextScope.DOMAIN:
            domain_keywords = layer.content.get("keywords", [])
            if any(keyword.lower() in message.lower() for keyword in domain_keywords):
                return True
        
        # Session scope - activate if session attributes match
        if layer.scope == ContextScope.SESSION:
            session_attributes = layer.content.get("session_attributes", {})
            current_session_data = self._get_current_session_data()
            
            for attr, value in session_attributes.items():
                if current_session_data.get(attr) == value:
                    return True
        
        return False

async def process_with_dynamic_context(self, message: str, context_hints: List[str] = None) -> Dict[str, Any]:
    """Process message using dynamically activated context"""
    
    # Activate relevant context layers
    context_activation = self.activate_context_dynamically(message, context_hints)
    
    # Build context prompt
    context_prompt = self._build_dynamic_context_prompt(
        message, 
        context_activation["activated_contexts"],
        context_activation["activation_log"]
    )
    
    # Generate response
    response = await self._call_llm(context_prompt)
    
    # Update context based on interaction
    self._update_context_from_interaction(message, response, context_activation)
    
    # Record context usage
    self.context_history.append({
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "activated_layers": list(context_activation["activated_contexts"].keys()),
        "response_length": len(response)
    })
    
    return {
        "response": response,
        "context_info": context_activation,
        "context_efficiency": self._calculate_context_efficiency(context_activation)
    }

def _build_dynamic_context_prompt(self, message: str, activated_contexts: Dict[str, Any], 
                                 activation_log: List[Dict[str, Any]]) -> str:
    """Build prompt incorporating dynamically activated context"""
    
    prompt_parts = [f"User message: {message}"]
    
    if activated_contexts:
        prompt_parts.append("\nRelevant context (ordered by priority):")
        
        # Sort contexts by priority from activation log
        sorted_contexts = sorted(activation_log, key=lambda x: x["priority"], reverse=True)
        
        for context_info in sorted_contexts:
            layer_id = context_info["layer_id"]
            context_data = activated_contexts[layer_id]
            
            prompt_parts.append(f"\n{context_info['scope'].title()} Context ({context_info['priority']} priority):")
            
            # Format context data based on type
            if isinstance(context_data, dict):
                for key, value in context_data.items():
                    if key != "keywords" and key != "session_attributes":  # Skip metadata
                        prompt_parts.append(f"  {key}: {value}")
            else:
                prompt_parts.append(f"  {context_data}")
    
    prompt_parts.append("\nRespond appropriately using the relevant context.")
    
    return "\n".join(prompt_parts)
```

---

## 🎯 Module Summary

You've now mastered complex state management for bare metal agents:

✅ **Conversation Memory Systems**: Built hierarchical memory with semantic retrieval and intelligent consolidation  
✅ **Agent State Persistence**: Implemented automatic state saving and recovery across sessions  
✅ **Dynamic Context Management**: Created adaptive context systems that activate relevant information dynamically  
✅ **State Synchronization**: Designed patterns for maintaining consistency across agent interactions

### Next Steps
- **Return to Core**: [Session 1 Main](Session1_Bare_Metal_Agents.md)
- **Advance to Session 2**: [LangChain Foundations](Session2_LangChain_Foundations.md)
- **Review Performance**: [Module B: Performance Optimization](Session1_ModuleB_Performance_Optimization.md)

---

**🗂️ Source Files for Module C:**
- `src/session1/conversation_memory.py` - Hierarchical memory systems with semantic retrieval
- `src/session1/persistent_state.py` - Agent state persistence and recovery
- `src/session1/dynamic_context.py` - Dynamic context activation and management