# ⚙️ Session 2: Production Memory Systems

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete [🎯 Observer Path](Session2_LangChain_Foundations.md) and [📝 Participant Path](Session2_Practical_Implementation.md)
> Time Investment: 2-3 hours
> Outcome: Master enterprise-grade memory management, state persistence, and context optimization

## Advanced Learning Outcomes

After completing this production memory systems module, you will master:

- Enterprise-grade memory persistence and recovery strategies  
- Advanced context management techniques for long-running conversations  
- Memory optimization patterns for high-performance agent deployments  
- Distributed memory architectures for multi-agent coordination  
- Compliance and audit-ready conversation logging systems  

## Enterprise Memory Architecture Patterns

Production agent systems require sophisticated memory management that goes beyond simple conversation buffers, implementing persistent storage, distributed synchronization, and intelligent context optimization.

### Distributed Memory Coordination

For multi-agent systems operating across distributed infrastructure, memory synchronization becomes critical for maintaining consistent context and coordination state:

```python
import redis
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

class DistributedMemoryManager:
    """Enterprise memory manager with distributed coordination capabilities"""

    def __init__(self, redis_url: str, memory_namespace: str = "agent_memory"):
        self.redis_client = redis.from_url(redis_url)
        self.namespace = memory_namespace
        self.local_cache = {}
        self.sync_interval = 30  # seconds
        self.last_sync = {}

    def create_agent_memory(self, agent_id: str, memory_type: str = "buffer") -> 'DistributedConversationMemory':
        """Create distributed memory instance for specific agent"""

        memory_key = f"{self.namespace}:agent:{agent_id}:conversation"

        if memory_type == "buffer":
            return DistributedConversationMemory(
                redis_client=self.redis_client,
                memory_key=memory_key,
                agent_id=agent_id
            )
        elif memory_type == "summary":
            return DistributedSummaryMemory(
                redis_client=self.redis_client,
                memory_key=memory_key,
                agent_id=agent_id
            )
        else:
            raise ValueError(f"Unsupported memory type: {memory_type}")

    def sync_memories_across_agents(self, agent_ids: List[str]) -> Dict[str, Any]:
        """Synchronize memory state across multiple agents for coordination"""

        sync_results = {}

        for agent_id in agent_ids:
            try:
                memory_key = f"{self.namespace}:agent:{agent_id}:conversation"

                # Get latest memory state
                memory_data = self.redis_client.get(memory_key)
                if memory_data:
                    memory_state = json.loads(memory_data)
                    sync_results[agent_id] = {
                        "status": "synced",
                        "message_count": len(memory_state.get("messages", [])),
                        "last_update": memory_state.get("last_update"),
                        "context_summary": memory_state.get("context_summary", "")[:100]
                    }
                else:
                    sync_results[agent_id] = {
                        "status": "no_memory_found",
                        "message_count": 0
                    }

            except Exception as e:
                sync_results[agent_id] = {
                    "status": "sync_error",
                    "error": str(e)
                }

        return sync_results

    def create_shared_context(self, context_id: str, initial_context: Dict[str, Any]) -> str:
        """Create shared context accessible by multiple agents"""

        context_key = f"{self.namespace}:shared_context:{context_id}"

        shared_context = {
            "context_id": context_id,
            "created_at": datetime.now().isoformat(),
            "data": initial_context,
            "access_log": [],
            "version": 1
        }

        self.redis_client.set(context_key, json.dumps(shared_context))
        return context_key

    def update_shared_context(self, context_id: str, updates: Dict[str, Any], agent_id: str) -> bool:
        """Update shared context with version control and access logging"""

        context_key = f"{self.namespace}:shared_context:{context_id}"

        try:
            # Get current context with lock
            current_data = self.redis_client.get(context_key)
            if not current_data:
                return False

            context = json.loads(current_data)

            # Update data and metadata
            context["data"].update(updates)
            context["version"] += 1
            context["last_updated"] = datetime.now().isoformat()
            context["access_log"].append({
                "agent_id": agent_id,
                "action": "update",
                "timestamp": datetime.now().isoformat(),
                "changes": list(updates.keys())
            })

            # Save updated context
            self.redis_client.set(context_key, json.dumps(context))
            return True

        except Exception as e:
            print(f"Failed to update shared context: {e}")
            return False

class DistributedConversationMemory(ConversationBufferMemory):
    """Conversation memory with distributed persistence and synchronization"""

    def __init__(self, redis_client: redis.Redis, memory_key: str, agent_id: str, max_token_limit: int = 4000):
        super().__init__(return_messages=True)
        self.redis_client = redis_client
        self.memory_key = memory_key
        self.agent_id = agent_id
        self.max_token_limit = max_token_limit
        self.local_cache_ttl = 300  # 5 minutes
        self.last_persistence = None

        # Load existing memory on initialization
        self._load_from_distributed_storage()

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save conversation context to both local and distributed storage"""

        # Save to local memory first
        super().save_context(inputs, outputs)

        # Persist to distributed storage
        self._persist_to_distributed_storage()

    def _persist_to_distributed_storage(self):
        """Persist current memory state to distributed storage"""

        try:
            messages_data = []

            for message in self.chat_memory.messages:
                messages_data.append({
                    "type": type(message).__name__,
                    "content": message.content,
                    "timestamp": datetime.now().isoformat()
                })

            memory_state = {
                "agent_id": self.agent_id,
                "messages": messages_data,
                "message_count": len(messages_data),
                "last_update": datetime.now().isoformat(),
                "token_estimate": self._estimate_token_count(),
                "context_summary": self._generate_context_summary()
            }

            # Set with TTL for automatic cleanup
            self.redis_client.setex(
                self.memory_key,
                timedelta(hours=24),
                json.dumps(memory_state)
            )

            self.last_persistence = datetime.now()

        except Exception as e:
            print(f"Failed to persist memory: {e}")

    def _load_from_distributed_storage(self):
        """Load memory state from distributed storage"""

        try:
            stored_data = self.redis_client.get(self.memory_key)
            if not stored_data:
                return

            memory_state = json.loads(stored_data)

            # Reconstruct messages
            self.chat_memory.messages = []

            for msg_data in memory_state.get("messages", []):
                if msg_data["type"] == "HumanMessage":
                    message = HumanMessage(content=msg_data["content"])
                elif msg_data["type"] == "AIMessage":
                    message = AIMessage(content=msg_data["content"])
                else:
                    continue  # Skip unknown message types

                self.chat_memory.messages.append(message)

            print(f"Loaded {len(self.chat_memory.messages)} messages from distributed storage")

        except Exception as e:
            print(f"Failed to load memory from distributed storage: {e}")

    def _estimate_token_count(self) -> int:
        """Estimate token count for current conversation"""

        total_content = ""
        for message in self.chat_memory.messages:
            total_content += message.content

        # Rough estimation: ~4 characters per token
        return len(total_content) // 4

    def _generate_context_summary(self) -> str:
        """Generate brief summary of current conversation context"""

        if not self.chat_memory.messages:
            return "Empty conversation"

        recent_messages = self.chat_memory.messages[-3:]  # Last 3 messages
        summary_parts = []

        for msg in recent_messages:
            content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            message_type = "Human" if isinstance(msg, HumanMessage) else "AI"
            summary_parts.append(f"{message_type}: {content_preview}")

        return " | ".join(summary_parts)

    def optimize_memory_for_tokens(self):
        """Optimize memory to stay within token limits"""

        current_tokens = self._estimate_token_count()

        if current_tokens > self.max_token_limit:
            # Remove oldest messages until within limit
            while current_tokens > self.max_token_limit and len(self.chat_memory.messages) > 1:
                removed_message = self.chat_memory.messages.pop(0)
                current_tokens = self._estimate_token_count()

                print(f"Removed message to stay within token limit: {removed_message.content[:50]}...")

            # Persist optimized memory
            self._persist_to_distributed_storage()
```

## Advanced Context Optimization

Sophisticated context management ensures agents maintain relevant information while optimizing for performance and cost efficiency.

### Intelligent Context Summarization

Implement AI-driven context summarization that preserves critical information while reducing token consumption:

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class IntelligentContextManager:
    """Advanced context management with AI-driven summarization and optimization"""

    def __init__(self, llm, context_config: Dict[str, Any] = None):
        self.llm = llm
        self.config = context_config or {
            "max_context_tokens": 2000,
            "summary_trigger_tokens": 3000,
            "importance_threshold": 0.7,
            "context_categories": ["technical", "business", "data_quality", "performance"]
        }

        self.summarization_chain = self._create_summarization_chain()
        self.importance_chain = self._create_importance_chain()

    def _create_summarization_chain(self) -> LLMChain:
        """Create specialized chain for intelligent context summarization"""

        template = """
        You are an expert at summarizing technical conversations while preserving critical information.

        Conversation History:
        {conversation_text}

        Create a comprehensive summary that:
        1. Preserves all technical details, metrics, and specific findings
        2. Maintains decision points and their reasoning
        3. Keeps action items and recommendations
        4. Summarizes background context concisely
        5. Structures information by importance and category

        Categories to preserve: {categories}

        Generate a structured summary that maintains technical precision while reducing length by ~70%.
        """

        return LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=template,
                input_variables=["conversation_text", "categories"]
            )
        )

    def _create_importance_chain(self) -> LLMChain:
        """Create chain for evaluating message importance"""

        template = """
        Evaluate the importance of this conversation message for ongoing data engineering context:

        Message: {message_text}
        Context: {current_context}

        Rate importance (0.0-1.0) and explain reasoning:

        High importance (0.8-1.0): Critical decisions, specific metrics, error conditions, action items
        Medium importance (0.4-0.7): General analysis, contextual information, process descriptions
        Low importance (0.0-0.3): Casual remarks, acknowledgments, routine confirmations

        Return JSON: {{"importance": 0.X, "reasoning": "explanation", "categories": ["category1", "category2"]}}
        """

        return LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=template,
                input_variables=["message_text", "current_context"]
            )
        )

    def optimize_conversation_context(self, messages: List[BaseMessage], current_context: str = "") -> Dict[str, Any]:
        """Intelligently optimize conversation context for efficiency"""

        # Estimate current token usage
        total_tokens = self._estimate_total_tokens(messages)

        if total_tokens <= self.config["max_context_tokens"]:
            return {
                "optimized_messages": messages,
                "summary": None,
                "optimization_applied": False,
                "token_reduction": 0
            }

        # Analyze message importance
        message_analysis = []

        for i, message in enumerate(messages):
            try:
                importance_result = self.importance_chain.run({
                    "message_text": message.content[:500],  # Limit for efficiency
                    "current_context": current_context[:200]
                })

                # Parse importance score (simplified)
                importance_score = 0.5  # Default fallback
                try:
                    if "importance" in importance_result:
                        # Extract numeric score (simplified parsing)
                        score_str = importance_result.split('"importance":')[1].split(',')[0].strip()
                        importance_score = float(score_str.replace('"', ''))
                except:
                    pass

                message_analysis.append({
                    "index": i,
                    "message": message,
                    "importance": importance_score,
                    "token_estimate": len(message.content) // 4
                })

            except Exception as e:
                print(f"Error analyzing message importance: {e}")
                # Keep message with medium importance as fallback
                message_analysis.append({
                    "index": i,
                    "message": message,
                    "importance": 0.5,
                    "token_estimate": len(message.content) // 4
                })

        # Sort by importance (descending)
        message_analysis.sort(key=lambda x: x["importance"], reverse=True)

        # Select most important messages within token limit
        optimized_messages = []
        token_count = 0
        summarization_candidates = []

        for analysis in message_analysis:
            if (token_count + analysis["token_estimate"] <= self.config["max_context_tokens"]
                and analysis["importance"] >= self.config["importance_threshold"]):

                optimized_messages.append(analysis["message"])
                token_count += analysis["token_estimate"]
            else:
                summarization_candidates.append(analysis["message"])

        # Create summary of less important messages
        summary = None
        if summarization_candidates:
            summary_text = "\n".join([msg.content for msg in summarization_candidates])

            try:
                summary = self.summarization_chain.run({
                    "conversation_text": summary_text,
                    "categories": self.config["context_categories"]
                })
            except Exception as e:
                print(f"Summarization failed: {e}")
                summary = "Context summary unavailable due to processing error"

        token_reduction = total_tokens - self._estimate_total_tokens(optimized_messages)

        return {
            "optimized_messages": optimized_messages,
            "summary": summary,
            "optimization_applied": True,
            "token_reduction": token_reduction,
            "messages_summarized": len(summarization_candidates),
            "messages_retained": len(optimized_messages)
        }

    def _estimate_total_tokens(self, messages: List[BaseMessage]) -> int:
        """Estimate total tokens for message list"""

        total_content = ""
        for message in messages:
            total_content += message.content

        return len(total_content) // 4  # Rough estimation

class ContextAwareMemory(ConversationBufferMemory):
    """Memory with intelligent context optimization"""

    def __init__(self, llm, context_manager: IntelligentContextManager = None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.context_manager = context_manager or IntelligentContextManager(llm)
        self.optimization_history = []

    def get_optimized_context(self) -> str:
        """Get optimized conversation context"""

        if not self.chat_memory.messages:
            return ""

        optimization_result = self.context_manager.optimize_conversation_context(
            self.chat_memory.messages,
            current_context=self._get_current_context_summary()
        )

        # Record optimization metrics
        self.optimization_history.append({
            "timestamp": datetime.now().isoformat(),
            "optimization_applied": optimization_result["optimization_applied"],
            "token_reduction": optimization_result.get("token_reduction", 0),
            "messages_retained": optimization_result.get("messages_retained", len(self.chat_memory.messages))
        })

        # Build optimized context
        context_parts = []

        if optimization_result["summary"]:
            context_parts.append(f"CONVERSATION SUMMARY:\n{optimization_result['summary']}\n")

        context_parts.append("RECENT CONVERSATION:")
        for message in optimization_result["optimized_messages"]:
            message_type = "Human" if isinstance(message, HumanMessage) else "AI"
            context_parts.append(f"{message_type}: {message.content}")

        return "\n".join(context_parts)

    def _get_current_context_summary(self) -> str:
        """Generate brief summary of current conversation state"""

        if not self.chat_memory.messages:
            return "New conversation"

        message_count = len(self.chat_memory.messages)
        recent_message = self.chat_memory.messages[-1].content[:100]

        return f"Conversation with {message_count} messages. Latest: {recent_message}..."

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get context optimization performance statistics"""

        if not self.optimization_history:
            return {"optimizations_performed": 0}

        total_optimizations = len(self.optimization_history)
        applied_optimizations = sum(1 for opt in self.optimization_history if opt["optimization_applied"])
        total_token_reduction = sum(opt["token_reduction"] for opt in self.optimization_history)

        return {
            "optimizations_performed": total_optimizations,
            "optimizations_applied": applied_optimizations,
            "optimization_rate": f"{applied_optimizations / max(1, total_optimizations):.1%}",
            "total_token_reduction": total_token_reduction,
            "avg_token_reduction": total_token_reduction / max(1, applied_optimizations)
        }
```

## Multi-Tenancy and Isolation

Enterprise deployments require robust memory isolation and multi-tenancy support to ensure data privacy and compliance across different organizations and user groups.

### Tenant-Isolated Memory Architecture

Implement comprehensive tenant isolation for memory systems:

```python
from typing import Set
import hashlib
from enum import Enum

class IsolationLevel(Enum):
    STRICT = "strict"          # Complete isolation, no shared resources
    MODERATE = "moderate"      # Shared infrastructure, isolated data
    MINIMAL = "minimal"        # Basic separation, shared optimizations

class TenantMemoryManager:
    """Enterprise memory manager with comprehensive tenant isolation"""

    def __init__(self, redis_client: redis.Redis, encryption_key: str, isolation_level: IsolationLevel = IsolationLevel.STRICT):
        self.redis_client = redis_client
        self.encryption_key = encryption_key
        self.isolation_level = isolation_level
        self.tenant_configurations = {}
        self.access_control = TenantAccessControl()

    def register_tenant(self, tenant_id: str, config: Dict[str, Any]) -> bool:
        """Register new tenant with specific configuration"""

        try:
            tenant_config = {
                "tenant_id": tenant_id,
                "created_at": datetime.now().isoformat(),
                "isolation_level": self.isolation_level.value,
                "memory_quota": config.get("memory_quota", 1000),  # MB
                "retention_days": config.get("retention_days", 30),
                "encryption_enabled": config.get("encryption_enabled", True),
                "audit_enabled": config.get("audit_enabled", True),
                "allowed_agents": config.get("allowed_agents", []),
                "data_residency": config.get("data_residency", "default")
            }

            # Create tenant namespace
            tenant_key = f"tenant:{tenant_id}:config"
            self.redis_client.set(tenant_key, json.dumps(tenant_config))

            # Initialize tenant memory spaces
            self._initialize_tenant_spaces(tenant_id, tenant_config)

            self.tenant_configurations[tenant_id] = tenant_config
            return True

        except Exception as e:
            print(f"Failed to register tenant {tenant_id}: {e}")
            return False

    def create_tenant_memory(self, tenant_id: str, agent_id: str, user_id: str) -> 'TenantIsolatedMemory':
        """Create isolated memory instance for specific tenant, agent, and user"""

        if tenant_id not in self.tenant_configurations:
            raise ValueError(f"Tenant {tenant_id} not registered")

        tenant_config = self.tenant_configurations[tenant_id]

        # Validate agent authorization
        if tenant_config["allowed_agents"] and agent_id not in tenant_config["allowed_agents"]:
            raise PermissionError(f"Agent {agent_id} not authorized for tenant {tenant_id}")

        # Create isolated memory key
        memory_key = self._generate_isolated_key(tenant_id, agent_id, user_id)

        return TenantIsolatedMemory(
            redis_client=self.redis_client,
            memory_key=memory_key,
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            encryption_key=self.encryption_key,
            tenant_config=tenant_config
        )

    def _initialize_tenant_spaces(self, tenant_id: str, config: Dict[str, Any]):
        """Initialize isolated spaces for tenant"""

        spaces = {
            "conversations": f"tenant:{tenant_id}:conversations",
            "shared_context": f"tenant:{tenant_id}:shared_context",
            "audit_log": f"tenant:{tenant_id}:audit",
            "usage_metrics": f"tenant:{tenant_id}:metrics"
        }

        for space_name, space_key in spaces.items():
            self.redis_client.set(
                f"{space_key}:initialized",
                json.dumps({
                    "created_at": datetime.now().isoformat(),
                    "space_type": space_name,
                    "tenant_id": tenant_id
                })
            )

    def _generate_isolated_key(self, tenant_id: str, agent_id: str, user_id: str) -> str:
        """Generate cryptographically isolated memory key"""

        if self.isolation_level == IsolationLevel.STRICT:
            # Include all identifiers for complete isolation
            key_data = f"{tenant_id}:{agent_id}:{user_id}:{self.encryption_key}"
        elif self.isolation_level == IsolationLevel.MODERATE:
            # Tenant and user isolation
            key_data = f"{tenant_id}:{user_id}:{self.encryption_key}"
        else:
            # Basic tenant isolation
            key_data = f"{tenant_id}:{self.encryption_key}"

        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"tenant:{tenant_id}:memory:{key_hash}"

    def get_tenant_usage_report(self, tenant_id: str) -> Dict[str, Any]:
        """Generate usage report for specific tenant"""

        if tenant_id not in self.tenant_configurations:
            raise ValueError(f"Tenant {tenant_id} not found")

        try:
            # Get all tenant keys
            pattern = f"tenant:{tenant_id}:*"
            tenant_keys = self.redis_client.keys(pattern)

            # Calculate memory usage
            total_memory = 0
            conversation_count = 0

            for key in tenant_keys:
                memory_info = self.redis_client.memory_usage(key)
                if memory_info:
                    total_memory += memory_info

                if b"conversations" in key:
                    conversation_count += 1

            # Get usage metrics
            metrics_key = f"tenant:{tenant_id}:metrics"
            metrics_data = self.redis_client.get(metrics_key)
            metrics = json.loads(metrics_data) if metrics_data else {}

            return {
                "tenant_id": tenant_id,
                "memory_usage_bytes": total_memory,
                "memory_usage_mb": total_memory / (1024 * 1024),
                "conversation_count": conversation_count,
                "quota_usage": (total_memory / (1024 * 1024)) / self.tenant_configurations[tenant_id]["memory_quota"],
                "metrics": metrics,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Failed to generate usage report: {str(e)}"}

class TenantIsolatedMemory(ConversationBufferMemory):
    """Conversation memory with complete tenant isolation and encryption"""

    def __init__(self, redis_client: redis.Redis, memory_key: str, tenant_id: str,
                 agent_id: str, user_id: str, encryption_key: str, tenant_config: Dict[str, Any]):
        super().__init__(return_messages=True)

        self.redis_client = redis_client
        self.memory_key = memory_key
        self.tenant_id = tenant_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.encryption_key = encryption_key
        self.tenant_config = tenant_config
        self.audit_logger = TenantAuditLogger(redis_client, tenant_id) if tenant_config["audit_enabled"] else None

        # Load existing conversation
        self._load_tenant_conversation()

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context with tenant isolation and auditing"""

        # Save to local memory
        super().save_context(inputs, outputs)

        # Audit logging
        if self.audit_logger:
            self.audit_logger.log_memory_operation(
                "save_context",
                {
                    "agent_id": self.agent_id,
                    "user_id": self.user_id,
                    "inputs_keys": list(inputs.keys()),
                    "outputs_keys": list(outputs.keys())
                }
            )

        # Persist with encryption
        self._persist_encrypted_conversation()

        # Update usage metrics
        self._update_tenant_metrics()

    def _load_tenant_conversation(self):
        """Load conversation with tenant isolation validation"""

        try:
            encrypted_data = self.redis_client.get(self.memory_key)
            if not encrypted_data:
                return

            # Decrypt and load conversation
            conversation_data = self._decrypt_conversation_data(encrypted_data)

            # Validate tenant ownership
            if conversation_data.get("tenant_id") != self.tenant_id:
                raise SecurityError(f"Tenant mismatch: expected {self.tenant_id}, got {conversation_data.get('tenant_id')}")

            # Reconstruct messages
            self.chat_memory.messages = []
            for msg_data in conversation_data.get("messages", []):
                if msg_data["type"] == "HumanMessage":
                    message = HumanMessage(content=msg_data["content"])
                elif msg_data["type"] == "AIMessage":
                    message = AIMessage(content=msg_data["content"])
                else:
                    continue

                self.chat_memory.messages.append(message)

            if self.audit_logger:
                self.audit_logger.log_memory_operation(
                    "load_conversation",
                    {"messages_loaded": len(self.chat_memory.messages)}
                )

        except Exception as e:
            print(f"Failed to load tenant conversation: {e}")
            if self.audit_logger:
                self.audit_logger.log_memory_operation("load_error", {"error": str(e)})

    def _persist_encrypted_conversation(self):
        """Persist conversation with encryption and tenant metadata"""

        try:
            messages_data = []
            for message in self.chat_memory.messages:
                messages_data.append({
                    "type": type(message).__name__,
                    "content": message.content,
                    "timestamp": datetime.now().isoformat()
                })

            conversation_data = {
                "tenant_id": self.tenant_id,
                "agent_id": self.agent_id,
                "user_id": self.user_id,
                "messages": messages_data,
                "last_update": datetime.now().isoformat(),
                "encryption_version": "1.0"
            }

            # Encrypt conversation data
            encrypted_data = self._encrypt_conversation_data(conversation_data)

            # Set with tenant-specific TTL
            ttl_days = self.tenant_config.get("retention_days", 30)
            self.redis_client.setex(
                self.memory_key,
                timedelta(days=ttl_days),
                encrypted_data
            )

        except Exception as e:
            if self.audit_logger:
                self.audit_logger.log_memory_operation("persist_error", {"error": str(e)})
            raise e

    def _encrypt_conversation_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt conversation data using tenant-specific encryption"""

        if not self.tenant_config.get("encryption_enabled", True):
            return json.dumps(data).encode()

        # Simplified encryption (use proper encryption in production)
        from cryptography.fernet import Fernet

        key_hash = hashlib.sha256(f"{self.encryption_key}:{self.tenant_id}".encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_hash)
        fernet = Fernet(fernet_key)

        data_bytes = json.dumps(data).encode()
        return fernet.encrypt(data_bytes)

    def _decrypt_conversation_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt conversation data using tenant-specific decryption"""

        if not self.tenant_config.get("encryption_enabled", True):
            return json.loads(encrypted_data.decode())

        # Simplified decryption (use proper encryption in production)
        from cryptography.fernet import Fernet

        key_hash = hashlib.sha256(f"{self.encryption_key}:{self.tenant_id}".encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_hash)
        fernet = Fernet(fernet_key)

        decrypted_bytes = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_bytes.decode())

    def _update_tenant_metrics(self):
        """Update tenant-specific usage metrics"""

        try:
            metrics_key = f"tenant:{self.tenant_id}:metrics"

            # Get current metrics
            current_metrics = self.redis_client.get(metrics_key)
            metrics = json.loads(current_metrics) if current_metrics else {}

            # Update metrics
            metrics.update({
                "last_activity": datetime.now().isoformat(),
                "total_messages": metrics.get("total_messages", 0) + 1,
                "active_conversations": metrics.get("active_conversations", 0) + (1 if len(self.chat_memory.messages) == 1 else 0)
            })

            # Save updated metrics
            self.redis_client.set(metrics_key, json.dumps(metrics))

        except Exception as e:
            print(f"Failed to update tenant metrics: {e}")

class TenantAuditLogger:
    """Audit logging system for tenant memory operations"""

    def __init__(self, redis_client: redis.Redis, tenant_id: str):
        self.redis_client = redis_client
        self.tenant_id = tenant_id
        self.audit_key = f"tenant:{tenant_id}:audit"

    def log_memory_operation(self, operation: str, details: Dict[str, Any]):
        """Log memory operation for compliance and monitoring"""

        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "tenant_id": self.tenant_id
        }

        # Add to audit log list
        self.redis_client.lpush(
            self.audit_key,
            json.dumps(audit_entry)
        )

        # Keep only last 1000 entries per tenant
        self.redis_client.ltrim(self.audit_key, 0, 999)
```

## Compliance and Audit-Ready Memory Systems

Enterprise deployments must support comprehensive audit trails, data retention policies, and compliance reporting for regulatory requirements.

### Comprehensive Audit and Compliance Framework

Implement enterprise-grade audit trails with compliance reporting:

```python
from dataclasses import dataclass
from typing import Union
import base64

@dataclass
class AuditEvent:
    event_id: str
    timestamp: str
    tenant_id: str
    user_id: str
    agent_id: str
    event_type: str
    event_data: Dict[str, Any]
    compliance_tags: List[str]
    retention_policy: str

class ComplianceMemoryManager:
    """Memory manager with comprehensive compliance and audit capabilities"""

    def __init__(self, redis_client: redis.Redis, compliance_config: Dict[str, Any]):
        self.redis_client = redis_client
        self.compliance_config = compliance_config
        self.audit_buffer = []
        self.retention_policies = self._load_retention_policies()

    def _load_retention_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load data retention policies for different compliance frameworks"""

        return {
            "GDPR": {
                "default_retention_days": 365,
                "deletion_on_request": True,
                "data_portability": True,
                "consent_required": True
            },
            "HIPAA": {
                "default_retention_days": 2555,  # 7 years
                "encryption_required": True,
                "access_logging": True,
                "data_integrity": True
            },
            "SOX": {
                "default_retention_days": 2555,  # 7 years
                "immutable_audit": True,
                "access_controls": True,
                "change_tracking": True
            },
            "PCI_DSS": {
                "default_retention_days": 365,
                "encryption_required": True,
                "access_monitoring": True,
                "data_masking": True
            }
        }

    def create_compliant_memory(self, tenant_id: str, user_id: str, agent_id: str,
                               compliance_frameworks: List[str]) -> 'ComplianceAwareMemory':
        """Create memory instance with compliance controls"""

        # Determine strictest retention policy
        retention_days = max(
            self.retention_policies[framework]["default_retention_days"]
            for framework in compliance_frameworks
            if framework in self.retention_policies
        )

        # Determine required compliance features
        compliance_features = {
            "encryption_required": any(
                self.retention_policies.get(framework, {}).get("encryption_required", False)
                for framework in compliance_frameworks
            ),
            "access_logging": any(
                self.retention_policies.get(framework, {}).get("access_logging", False)
                for framework in compliance_frameworks
            ),
            "deletion_on_request": any(
                self.retention_policies.get(framework, {}).get("deletion_on_request", False)
                for framework in compliance_frameworks
            ),
            "data_portability": any(
                self.retention_policies.get(framework, {}).get("data_portability", False)
                for framework in compliance_frameworks
            )
        }

        memory_key = f"compliant:{tenant_id}:{user_id}:{agent_id}"

        return ComplianceAwareMemory(
            redis_client=self.redis_client,
            memory_key=memory_key,
            tenant_id=tenant_id,
            user_id=user_id,
            agent_id=agent_id,
            compliance_frameworks=compliance_frameworks,
            compliance_features=compliance_features,
            retention_days=retention_days,
            audit_manager=self
        )

    def record_audit_event(self, event: AuditEvent):
        """Record audit event with compliance metadata"""

        audit_key = f"audit:{event.tenant_id}:{datetime.now().strftime('%Y-%m')}"

        audit_record = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "tenant_id": event.tenant_id,
            "user_id": event.user_id,
            "agent_id": event.agent_id,
            "event_type": event.event_type,
            "event_data": event.event_data,
            "compliance_tags": event.compliance_tags,
            "retention_policy": event.retention_policy,
            "recorded_at": datetime.now().isoformat()
        }

        # Store audit record
        self.redis_client.lpush(audit_key, json.dumps(audit_record))

        # Set retention based on compliance requirements
        if event.retention_policy in self.retention_policies:
            retention_days = self.retention_policies[event.retention_policy]["default_retention_days"]
            self.redis_client.expire(audit_key, timedelta(days=retention_days))

    def generate_compliance_report(self, tenant_id: str, frameworks: List[str],
                                 start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""

        report = {
            "tenant_id": tenant_id,
            "frameworks": frameworks,
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.now().isoformat(),
            "compliance_status": {},
            "audit_summary": {},
            "recommendations": []
        }

        # Analyze compliance for each framework
        for framework in frameworks:
            if framework not in self.retention_policies:
                continue

            framework_status = self._analyze_framework_compliance(
                tenant_id, framework, start_date, end_date
            )

            report["compliance_status"][framework] = framework_status

        # Generate audit summary
        report["audit_summary"] = self._generate_audit_summary(tenant_id, start_date, end_date)

        # Generate recommendations
        report["recommendations"] = self._generate_compliance_recommendations(report)

        return report

    def _analyze_framework_compliance(self, tenant_id: str, framework: str,
                                    start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze compliance status for specific framework"""

        policy = self.retention_policies[framework]

        # Get audit events for period
        audit_events = self._get_audit_events_for_period(tenant_id, start_date, end_date)

        analysis = {
            "framework": framework,
            "total_events": len(audit_events),
            "compliance_score": 0.0,
            "violations": [],
            "requirements_met": [],
            "data_retention_status": "compliant"
        }

        # Check specific requirements
        if policy.get("encryption_required"):
            encryption_events = [e for e in audit_events if "encryption" in e.get("compliance_tags", [])]
            analysis["requirements_met"].append(f"Encryption: {len(encryption_events)} events")

        if policy.get("access_logging"):
            access_events = [e for e in audit_events if e.get("event_type") in ["memory_access", "data_retrieval"]]
            analysis["requirements_met"].append(f"Access logging: {len(access_events)} events")

        # Calculate compliance score (simplified)
        analysis["compliance_score"] = min(1.0, len(analysis["requirements_met"]) / 3.0)

        return analysis

    def _get_audit_events_for_period(self, tenant_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Retrieve audit events for specified period"""

        events = []

        # Get audit keys for the period (month-based)
        current_date = start_date.replace(day=1)  # Start of month

        while current_date <= end_date:
            audit_key = f"audit:{tenant_id}:{current_date.strftime('%Y-%m')}"

            # Get all events for the month
            raw_events = self.redis_client.lrange(audit_key, 0, -1)

            for raw_event in raw_events:
                try:
                    event = json.loads(raw_event)
                    event_timestamp = datetime.fromisoformat(event["timestamp"])

                    if start_date <= event_timestamp <= end_date:
                        events.append(event)
                except:
                    continue

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return events

    def _generate_audit_summary(self, tenant_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate audit trail summary"""

        events = self._get_audit_events_for_period(tenant_id, start_date, end_date)

        # Categorize events
        event_categories = {}
        for event in events:
            category = event.get("event_type", "unknown")
            event_categories[category] = event_categories.get(category, 0) + 1

        return {
            "total_events": len(events),
            "event_categories": event_categories,
            "unique_users": len(set(e.get("user_id") for e in events if e.get("user_id"))),
            "unique_agents": len(set(e.get("agent_id") for e in events if e.get("agent_id"))),
            "period_coverage": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }

    def _generate_compliance_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate compliance improvement recommendations"""

        recommendations = []

        for framework, status in report["compliance_status"].items():
            if status["compliance_score"] < 0.8:
                recommendations.append(f"Improve {framework} compliance score (currently {status['compliance_score']:.1%})")

            if status.get("violations"):
                recommendations.append(f"Address {len(status['violations'])} {framework} violations")

        if report["audit_summary"]["total_events"] == 0:
            recommendations.append("Enable comprehensive audit logging for all memory operations")

        return recommendations

class ComplianceAwareMemory(ConversationBufferMemory):
    """Memory with comprehensive compliance controls and audit trails"""

    def __init__(self, redis_client: redis.Redis, memory_key: str, tenant_id: str,
                 user_id: str, agent_id: str, compliance_frameworks: List[str],
                 compliance_features: Dict[str, bool], retention_days: int,
                 audit_manager: ComplianceMemoryManager):
        super().__init__(return_messages=True)

        self.redis_client = redis_client
        self.memory_key = memory_key
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.agent_id = agent_id
        self.compliance_frameworks = compliance_frameworks
        self.compliance_features = compliance_features
        self.retention_days = retention_days
        self.audit_manager = audit_manager

        # Load existing memory
        self._load_compliant_memory()

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context with comprehensive compliance controls"""

        # Record audit event
        audit_event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            agent_id=self.agent_id,
            event_type="memory_save",
            event_data={
                "inputs_keys": list(inputs.keys()),
                "outputs_keys": list(outputs.keys()),
                "message_count": len(self.chat_memory.messages) + 1
            },
            compliance_tags=self.compliance_frameworks + ["memory_operation"],
            retention_policy=self.compliance_frameworks[0] if self.compliance_frameworks else "default"
        )

        self.audit_manager.record_audit_event(audit_event)

        # Save to local memory
        super().save_context(inputs, outputs)

        # Persist with compliance controls
        self._persist_compliant_memory()

    def _persist_compliant_memory(self):
        """Persist memory with compliance controls"""

        conversation_data = {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "compliance_frameworks": self.compliance_frameworks,
            "messages": [],
            "metadata": {
                "last_update": datetime.now().isoformat(),
                "retention_until": (datetime.now() + timedelta(days=self.retention_days)).isoformat(),
                "compliance_version": "1.0"
            }
        }

        # Add messages with compliance metadata
        for message in self.chat_memory.messages:
            message_data = {
                "type": type(message).__name__,
                "content": message.content,
                "timestamp": datetime.now().isoformat(),
                "compliance_tags": self.compliance_frameworks
            }

            # Apply data masking if required
            if self.compliance_features.get("data_masking"):
                message_data["content"] = self._apply_data_masking(message_data["content"])

            conversation_data["messages"].append(message_data)

        # Encrypt if required
        if self.compliance_features.get("encryption_required"):
            serialized_data = self._encrypt_compliant_data(conversation_data)
        else:
            serialized_data = json.dumps(conversation_data).encode()

        # Store with compliance retention
        self.redis_client.setex(
            self.memory_key,
            timedelta(days=self.retention_days),
            serialized_data
        )

    def _apply_data_masking(self, content: str) -> str:
        """Apply data masking for sensitive information"""
        import re

        # Mask common sensitive patterns
        # Email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', content)

        # Phone numbers (simplified)
        content = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '***-***-****', content)
        content = re.sub(r'\b\(\d{3}\)\s*\d{3}-\d{4}\b', '(***) ***-****', content)

        # SSN (simplified)
        content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****', content)

        return content

    def _encrypt_compliant_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt data according to compliance requirements"""

        # Use enterprise-grade encryption in production
        from cryptography.fernet import Fernet
        import base64

        # Generate compliance-specific encryption key
        key_material = f"{self.tenant_id}:{':'.join(self.compliance_frameworks)}:memory_encryption"
        key_hash = hashlib.sha256(key_material.encode()).digest()
        encryption_key = base64.urlsafe_b64encode(key_hash)

        fernet = Fernet(encryption_key)
        data_bytes = json.dumps(data).encode()

        return fernet.encrypt(data_bytes)

    def request_data_deletion(self, user_consent: bool = False) -> Dict[str, Any]:
        """Handle data deletion request (GDPR right to be forgotten)"""

        if not self.compliance_features.get("deletion_on_request"):
            return {
                "status": "denied",
                "reason": "Data deletion not permitted under current compliance framework"
            }

        if not user_consent:
            return {
                "status": "consent_required",
                "reason": "User consent required for data deletion"
            }

        try:
            # Record deletion request
            audit_event = AuditEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                agent_id=self.agent_id,
                event_type="data_deletion_request",
                event_data={"consent_provided": user_consent},
                compliance_tags=self.compliance_frameworks + ["data_deletion"],
                retention_policy="GDPR"
            )

            self.audit_manager.record_audit_event(audit_event)

            # Delete memory data
            self.redis_client.delete(self.memory_key)

            # Clear local memory
            self.chat_memory.messages = []

            return {
                "status": "completed",
                "deleted_at": datetime.now().isoformat(),
                "confirmation_id": audit_event.event_id
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def export_data_for_portability(self) -> Dict[str, Any]:
        """Export user data for portability (GDPR)"""

        if not self.compliance_features.get("data_portability"):
            return {
                "status": "denied",
                "reason": "Data portability not supported under current compliance framework"
            }

        # Record data export request
        audit_event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            agent_id=self.agent_id,
            event_type="data_export_request",
            event_data={"export_format": "json"},
            compliance_tags=self.compliance_frameworks + ["data_portability"],
            retention_policy="GDPR"
        )

        self.audit_manager.record_audit_event(audit_event)

        # Export conversation data
        export_data = {
            "export_metadata": {
                "tenant_id": self.tenant_id,
                "user_id": self.user_id,
                "agent_id": self.agent_id,
                "exported_at": datetime.now().isoformat(),
                "compliance_frameworks": self.compliance_frameworks,
                "export_id": audit_event.event_id
            },
            "conversations": []
        }

        for message in self.chat_memory.messages:
            export_data["conversations"].append({
                "message_type": type(message).__name__,
                "content": message.content,
                "estimated_timestamp": datetime.now().isoformat()  # Simplified
            })

        return {
            "status": "completed",
            "data": export_data,
            "format": "json"
        }
```

## 🎯📝 Prerequisites Review

Before implementing production memory systems, ensure you have solid understanding of:

**Foundation Knowledge:**  
- [🎯 LangChain Memory Basics](Session2_LangChain_Foundations.md) - Memory types and basic configuration  
- [📝 Production Implementation](Session2_Practical_Implementation.md) - Practical memory management patterns  

## ⚙️ Continue Advanced Learning

Explore complementary advanced topics:

**Related Advanced Modules:**  
- [⚙️ Advanced Agent Architecture](Session2_Advanced_Agent_Architecture.md) - Sophisticated orchestration patterns  
- [⚙️ Enterprise Tool Development](Session2_Enterprise_Tool_Development.md) - Custom integrations and specialized capabilities  

**Legacy Advanced Modules:**  
- [Advanced LangChain Patterns](Session2_ModuleA_Advanced_LangChain_Patterns.md) - Complex workflows & optimization  
- [Production Deployment Strategies](Session2_ModuleB_Production_Deployment_Strategies.md) - Enterprise deployment & monitoring  
---

**Next:** [Session 3 - LangGraph Multi-Agent Workflows →](Session3_LangGraph_Multi_Agent_Workflows.md)

---
