# Session 7: Agent-to-Agent Communication (A2A) - Enterprise Multi-Agent Orchestration

## Learning Outcomes

By the end of this session, you will be able to:
- **Understand** the Agent2Agent (A2A) protocol standard and Google's multi-agent orchestration framework
- **Implement** JSON-RPC 2.0 based agent communication with enterprise security
- **Create** agent discovery systems using standardized Agent Cards
- **Build** collaborative agent teams with distributed task management
- **Deploy** scalable multi-agent networks with Microsoft Azure AI Foundry integration

## Chapter Overview

### What You'll Learn: The A2A Protocol Standard

In this session, we'll implement the Agent2Agent (A2A) protocol - the first open standard designed specifically for AI agent collaboration. A2A enables multiple AI agents to communicate, coordinate, and share information across different platforms and organizational boundaries while maintaining enterprise-grade security and observability.

### Why This Matters: The 2024-2025 Multi-Agent Revolution

Based on industry research, A2A represents a critical advancement in enterprise AI:

- **Industry Consortium**: Google launched A2A with support from 50+ technology partners including Atlassian, Box, Cohere, Intuit, LangChain, MongoDB, PayPal, Salesforce, SAP, ServiceNow, and major consulting firms (Accenture, BCG, McKinsey, PwC, Deloitte)
- **Enterprise Integration**: Microsoft committed to A2A support in Azure AI Foundry and Copilot Studio for cross-cloud agent collaboration
- **Protocol Foundation**: Built on JSON-RPC 2.0 and HTTP(S) with enterprise features like streaming, push notifications, and standard authentication
- **Task Management Standard**: Formal task lifecycle management (submitted, working, completed, failed) with tracking IDs
- **Distributed Memory**: Standardized protocol for agents to exchange task-specific information and maintain coherent interaction history

### How A2A Stands Out: Enterprise-Grade Agent Orchestration

The Agent2Agent protocol differentiates itself through standardized enterprise features:
- **Agent Cards**: Machine-readable JSON documents advertising capabilities, endpoints, and authentication requirements
- **Task Lifecycle Management**: Structured workflows with states (pending, in progress, completed) and message exchanges
- **Transport Flexibility**: HTTP(S) for standard communication, Server-Sent Events (SSE) for real-time streaming
- **Security Integration**: Enterprise authentication with parity to OpenAPI's authentication schemes
- **Cross-Platform Compatibility**: Enables collaboration across clouds, platforms, and organizational boundaries

### Where You'll Apply This: Enterprise Multi-Agent Use Cases

A2A excels in complex enterprise scenarios requiring agent collaboration:
- **Enterprise Workflow Automation**: Agents coordinating across CRM, ERP, and business intelligence systems
- **Cross-Organizational Collaboration**: Secure agent communication between different companies and platforms
- **Distributed Decision Making**: Multiple specialized agents contributing to complex business decisions
- **Scalable AI Operations**: Agent networks that can grow and adapt with changing business requirements
- **Compliance and Auditing**: Standardized communication patterns that support regulatory requirements

![A2A Communication Architecture](images/a2a-communication-architecture.png)
*Figure 1: A2A enterprise architecture showing Agent Cards for discovery, JSON-RPC 2.0 communication, distributed task management, and cross-platform coordination enabling scalable multi-agent collaboration*

### Learning Path Options

**Observer Path (30 minutes)**: Understand A2A protocol concepts and enterprise patterns
- Focus: Quick insights into Agent Cards, task management, and distributed coordination
- Best for: Getting oriented with enterprise multi-agent architectures

**📝 Participant Path (55 minutes)**: Implement working A2A agents and coordination systems  
- Focus: Hands-on Agent Card creation, JSON-RPC communication, and task lifecycle management
- Best for: Building practical enterprise multi-agent systems

**⚙️ Implementer Path (85 minutes)**: Advanced enterprise deployment and cross-platform integration
- Focus: Azure AI Foundry integration, security patterns, and scalable orchestration
- Best for: Enterprise multi-agent architecture and platform integration

---

## Part 1: A2A Protocol Architecture (Observer: 10 min | Participant: 22 min)

### The Enterprise Multi-Agent Challenge

As organizations deploy multiple AI agents across different platforms and departments, they face the fundamental challenge of enabling secure, standardized communication between heterogeneous agent systems. A2A solves this through formal protocol standardization.

**Enterprise Requirements Addressed:**
1. **Cross-Platform Discovery**: Finding and registering agents across different cloud environments
2. **Standardized Communication**: JSON-RPC 2.0 based message exchange with enterprise security
3. **Task Coordination**: Formal lifecycle management for complex multi-agent workflows
4. **Distributed Memory**: Maintaining coherent interaction history across agent networks
5. **Audit and Compliance**: Traceable communication patterns for regulatory requirements

### **OBSERVER PATH**: A2A Protocol Standards

**Google's A2A Foundation (2024-2025):**
The Agent2Agent protocol emerged as the first open standard specifically for AI agent collaboration, addressing the collaboration challenges when agents are developed by different organizations.

**Core Protocol Components:**
1. **Agent Cards**: JSON documents advertising agent capabilities, endpoints, and requirements
2. **Task Management**: Formal task lifecycle with states (pending, working, completed, failed)
3. **Message Exchange**: JSON-RPC 2.0 over HTTP(S) with streaming support via Server-Sent Events
4. **Authentication**: Enterprise-grade security with OpenAPI authentication scheme parity
5. **Distributed Coordination**: Cross-platform task coordination with unique tracking identifiers

**Industry Consortium Support:**
With 50+ technology partners including major enterprise platforms (Salesforce, SAP, ServiceNow) and consulting firms (McKinsey, PwC, Deloitte), A2A provides production-ready enterprise adoption.

### **PARTICIPANT PATH**: Implementing A2A JSON-RPC Protocol

**Step 1: Standard A2A Message Structure**

Implement the JSON-RPC 2.0 based A2A protocol following Google's specification:

```python

# a2a/protocol.py - Google A2A Standard Implementation

from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import json
from jsonrpc import JSONRPCRequestManager, dispatcher

class TaskState(Enum):
    """A2A standard task lifecycle states."""
    SUBMITTED = "submitted"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MessagePriority(Enum):
    """A2A message priority levels for enterprise workflows."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class A2ATask:
    """A2A standard task with formal lifecycle management."""
    
    # Task identification (A2A standard)
    task_id: str
    session_id: str = None
    correlation_id: str = None
    
    # Task lifecycle
    state: TaskState = TaskState.SUBMITTED
    created_at: datetime = None
    updated_at: datetime = None
    
    # Task content
    task_type: str = None
    description: str = None
    requirements: Dict[str, Any] = None
    context: Dict[str, Any] = None
    
    # Agent routing
    requesting_agent: str = None
    assigned_agent: str = None
    
    # Results and artifacts
    result: Any = None
    artifacts: List[Dict[str, Any]] = None
    error_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
        if not self.artifacts:
            self.artifacts = []
```

**A2A Standard Benefits:**
- **Task Tracking**: Unique identifiers enable distributed task coordination
- **Lifecycle Management**: Formal states provide clear workflow progression
- **Artifact Support**: Structured storage for task outputs and intermediate results
- **Enterprise Integration**: Compatible with existing enterprise task management systems

**Step 2: Agent Card Implementation**

Implement standardized Agent Cards for discovery:

```python
@dataclass
class AgentCard:
    """A2A standard Agent Card for capability advertisement."""
    
    # Agent identity
    agent_id: str
    name: str
    version: str
    description: str
    
    # Capabilities and endpoints
    capabilities: List[str]  # What the agent can do
    endpoints: Dict[str, str]  # Available API endpoints
    supported_protocols: List[str] = None  # ["jsonrpc-2.0", "http", "sse"]
    
    # Authentication and security
    authentication: Dict[str, Any] = None  # Auth requirements
    rate_limits: Dict[str, Any] = None     # Usage limits
    
    # Operational metadata
    availability: str = "24/7"  # Availability schedule
    response_time_sla: str = "<1s"  # Expected response time
    max_concurrent_tasks: int = 10
    
    # Contact and governance
    owner: str = None
    contact_email: str = None
    documentation_url: str = None
    
    def to_json(self) -> str:
        """Export Agent Card as JSON for A2A discovery."""
        return json.dumps(asdict(self), indent=2, default=str)
```
    
    # Message metadata
    timestamp: str = None
    priority: Priority = Priority.NORMAL
    ttl: int = 300             # Time to live in seconds
    
    # Content
    action: str = None          # What action to perform
    payload: Dict[str, Any] = None
    capabilities_required: List[str] = None
    
    # Response handling
    requires_response: bool = False
    timeout: int = 30          # Response timeout in seconds
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.payload is None:
            self.payload = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        data = asdict(self)
        # Convert enums to their values
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary."""
        # Convert enum values back to enums
        if 'message_type' in data:
            data['message_type'] = MessageType(data['message_type'])
        if 'priority' in data:
            data['priority'] = Priority(data['priority'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Serialize message to JSON."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'A2AMessage':
        """Deserialize message from JSON."""
        return cls.from_dict(json.loads(json_str))

@dataclass
class AgentCapability:
    """Describes an agent's capability."""
    
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    cost: float = 0.0           # Resource cost
    latency: float = 1.0        # Expected latency in seconds
    reliability: float = 0.95   # Reliability score (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AgentProfile:
    """Agent profile for discovery and coordination."""
    
    agent_id: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    endpoint: str               # How to reach this agent
    status: str = "active"      # active, busy, maintenance, offline
    load: float = 0.0          # Current load (0-1)  
    last_heartbeat: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['capabilities'] = [cap.to_dict() for cap in self.capabilities]
        return data
```

### Step 1.2: Agent Registry and Discovery

The agent registry serves as the central directory for agent discovery and capability matching in an A2A network. It provides dynamic service discovery, health monitoring, and intelligent agent selection based on capabilities and availability.

#### 1.2.1: Registry Foundation and Infrastructure Setup

First, let's establish the registry infrastructure with Redis for scalable, distributed storage:

```python

# a2a/registry.py - Registry Foundation

import asyncio
import json
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import redis
import logging
from a2a.protocol import AgentProfile, AgentCapability, A2AMessage, MessageType

logger = logging.getLogger(__name__)
```

**Key Concepts**: Redis provides fast, distributed storage for agent profiles and capability indices. The foundation supports both single-node and clustered Redis deployments for scalability.

#### 1.2.2: Registry Class and Configuration Management

The registry class manages configuration and connection state for distributed agent tracking:

```python
class AgentRegistry:
    """Centralized agent registry for discovery and coordination."""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.registry_prefix = "agent_registry:"
        self.capability_index = "capability_index:"
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 90   # seconds
        
        # Start background tasks
        self._heartbeat_task = None
        self._cleanup_task = None
```

**Key Concepts**: The registry uses prefixed keys for organization and capability indices for fast lookup. Heartbeat configuration ensures timely detection of agent failures.

#### 1.2.3: Agent Registration with Capability Indexing

Agent registration creates both profile storage and capability indices for efficient discovery:

```python
    async def register_agent(self, profile: AgentProfile) -> bool:
        """Register an agent in the registry."""
        try:
            # Store agent profile
            profile_key = f"{self.registry_prefix}{profile.agent_id}"
            profile_data = json.dumps(profile.to_dict())
            
            self.redis_client.set(profile_key, profile_data)
            self.redis_client.expire(profile_key, self.heartbeat_timeout)
            
            # Index capabilities for fast lookup
            for capability in profile.capabilities:
                cap_key = f"{self.capability_index}{capability.name}"
                self.redis_client.sadd(cap_key, profile.agent_id)
                self.redis_client.expire(cap_key, self.heartbeat_timeout)
            
            logger.info(f"Registered agent {profile.agent_id} with {len(profile.capabilities)} capabilities")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {profile.agent_id}: {e}")
            return False
```

**Key Concepts**: Registration creates both profile storage and reverse capability indices. TTL expiration ensures automatic cleanup of dead agents, while capability indexing enables fast discovery queries.

#### 1.2.4: Agent Unregistration and Cleanup

Proper unregistration removes both profile data and capability index entries:

```python
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry."""
        try:
            # Get agent profile first to clean up capability indices
            profile = await self.get_agent_profile(agent_id)
            
            if profile:
                # Remove from capability indices
                for capability in profile.capabilities:
                    cap_key = f"{self.capability_index}{capability.name}"
                    self.redis_client.srem(cap_key, agent_id)
            
            # Remove agent profile
            profile_key = f"{self.registry_prefix}{agent_id}"
            self.redis_client.delete(profile_key)
            
            logger.info(f"Unregistered agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
```

**Key Concepts**: Unregistration requires cleanup of both profile data and capability indices to prevent orphaned references. This ensures accurate discovery results.

#### 1.2.5: Heartbeat Updates and Status Management

Heartbeat updates maintain agent liveness information and current status:

```python
    async def update_heartbeat(self, agent_id: str, load: float = None, 
                             status: str = None) -> bool:
        """Update agent heartbeat and status."""
        try:
            profile = await self.get_agent_profile(agent_id)
            if not profile:
                return False
            
            # Update profile with new information
            profile.last_heartbeat = datetime.now().isoformat()
            if load is not None:
                profile.load = load
            if status is not None:
                profile.status = status
            
            # Store updated profile
            profile_key = f"{self.registry_prefix}{agent_id}"
            profile_data = json.dumps(profile.to_dict())
            
            self.redis_client.set(profile_key, profile_data)
            self.redis_client.expire(profile_key, self.heartbeat_timeout)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update heartbeat for {agent_id}: {e}")
            return False
```

**Key Concepts**: Heartbeats update both liveness timestamps and dynamic status information like current load. This enables intelligent load balancing and availability decisions.

#### 1.2.6: Capability-Based Agent Discovery

Agent discovery uses capability indices for efficient matching of requirements to available agents:

```python
    async def discover_agents(self, required_capabilities: List[str] = None,
                            status_filter: str = "active",
                            max_load: float = 0.8) -> List[AgentProfile]:
        """Discover agents matching the specified criteria."""
        try:
            candidate_agents = set()
            
            if required_capabilities:
                # Find agents with required capabilities
                for capability in required_capabilities:
                    cap_key = f"{self.capability_index}{capability}"
                    agents_with_cap = self.redis_client.smembers(cap_key)
                    
                    if not candidate_agents:
                        candidate_agents = set(agents_with_cap)
                    else:
                        # Intersection - agents must have ALL required capabilities
                        candidate_agents = candidate_agents.intersection(agents_with_cap)
            else:
                # Get all registered agents
                pattern = f"{self.registry_prefix}*"
                keys = self.redis_client.keys(pattern)
                candidate_agents = {key.decode().split(':')[-1] for key in keys}
```

**Key Concepts**: Discovery uses set intersection to find agents with ALL required capabilities. Capability indices make this operation very fast even with many agents.

#### 1.2.7: Agent Filtering and Selection

After capability matching, additional filters ensure only suitable agents are selected:

```python
            # Filter by status and load
            matching_agents = []
            for agent_id in candidate_agents:
                profile = await self.get_agent_profile(agent_id.decode() if isinstance(agent_id, bytes) else agent_id)
                
                if profile:
                    # Check if agent meets criteria
                    if (profile.status == status_filter and 
                        profile.load <= max_load and
                        self._is_agent_alive(profile)):
                        matching_agents.append(profile)
            
            # Sort by load (prefer less loaded agents)
            matching_agents.sort(key=lambda x: x.load)
            
            return matching_agents
            
        except Exception as e:
            logger.error(f"Failed to discover agents: {e}")
            return []
```

**Key Concepts**: Multi-criteria filtering considers status, load, and liveness. Load-based sorting enables intelligent work distribution across available agents.

#### 1.2.8: Profile Retrieval and Data Reconstruction

Profile retrieval reconstructs agent objects from stored JSON data:

```python
    async def get_agent_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get detailed profile for a specific agent."""
        try:
            profile_key = f"{self.registry_prefix}{agent_id}"
            profile_data = self.redis_client.get(profile_key)
            
            if profile_data:
                data = json.loads(profile_data)
                
                # Reconstruct AgentCapability objects
                capabilities = []
                for cap_data in data['capabilities']:
                    capabilities.append(AgentCapability(**cap_data))
                
                data['capabilities'] = capabilities
                return AgentProfile(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get profile for agent {agent_id}: {e}")
            return None
```

**Key Concepts**: Profile retrieval handles JSON deserialization and object reconstruction, ensuring type safety and proper data structure restoration.

#### 1.2.9: Agent Liveness Detection

Liveness checking determines if agents are still responsive based on heartbeat timing:

```python
    def _is_agent_alive(self, profile: AgentProfile) -> bool:
        """Check if agent is still alive based on heartbeat."""
        try:
            last_heartbeat = datetime.fromisoformat(profile.last_heartbeat)
            now = datetime.now()
            
            return (now - last_heartbeat).total_seconds() < self.heartbeat_timeout
            
        except Exception:
            return False
```

**Key Concepts**: Liveness detection uses configurable timeout thresholds to determine agent availability. This prevents routing to dead or unresponsive agents.

#### 1.2.10: Dead Agent Cleanup and Maintenance

Automatic cleanup removes agents that have stopped sending heartbeats:

```python
    async def cleanup_dead_agents(self):
        """Remove agents that haven't sent heartbeats."""
        try:
            pattern = f"{self.registry_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                agent_id = key.decode().split(':')[-1]
                profile = await self.get_agent_profile(agent_id)
                
                if profile and not self._is_agent_alive(profile):
                    await self.unregister_agent(agent_id)
                    logger.info(f"Cleaned up dead agent: {agent_id}")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
```

**Key Concepts**: Cleanup operations maintain registry hygiene by removing dead agents. This should run periodically to prevent accumulation of stale entries.

**Complete Implementation**: For advanced registry features including clustering and metrics, see [`src/session7/registry.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session7/registry.py) in the course materials.

### Step 1.3: Message Router

The message router is the core component responsible for intelligent message routing between agents in an A2A network. Let's build it step by step, demonstrating the communication progression from discovery to coordination.

#### 1.3.1: Router Foundation and Initialization

First, let's establish the basic router infrastructure with dependency management:

```python

# a2a/router.py - Router Foundation

import asyncio
import json
from typing import Dict, List, Optional, Callable, Any
import aiohttp
import logging
from datetime import datetime, timedelta

from a2a.protocol import A2AMessage, MessageType, Priority
from a2a.registry import AgentRegistry

logger = logging.getLogger(__name__)
```

**Key Concepts**: This foundation imports all necessary components for asynchronous message handling, HTTP communication, and integration with our A2A protocol and registry systems.

#### 1.3.2: Router Class Structure and State Management

Next, we define the router class with essential state management for tracking connections and pending operations:

```python
class MessageRouter:
    """Routes messages between agents in an A2A network."""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.session: Optional[aiohttp.ClientSession] = None
        self._processor_task = None
```

**Key Concepts**: The router maintains several critical data structures:
- `message_handlers`: Maps actions to their handling functions
- `pending_requests`: Tracks ongoing request-response pairs using futures
- `message_queue`: Asynchronous queue for message processing
- `session`: HTTP session for agent communication

#### 1.3.3: Router Lifecycle Management

Lifecycle management ensures proper startup and cleanup of the router's asynchronous components:

```python
    async def start(self):
        """Start the message router."""
        self.session = aiohttp.ClientSession()
        self._processor_task = asyncio.create_task(self._process_messages())
        logger.info("Message router started")
    
    async def stop(self):
        """Stop the message router."""
        if self._processor_task:
            self._processor_task.cancel()
        
        if self.session:
            await self.session.close()
        
        logger.info("Message router stopped")
```

**Key Concepts**: Proper lifecycle management prevents resource leaks and ensures graceful shutdown. The router starts a background task for message processing and maintains an HTTP session pool.

#### 1.3.4: Handler Registration for Action Mapping

Agent capabilities are exposed through registered handlers that map actions to executable functions:

```python
    def register_handler(self, action: str, handler: Callable):
        """Register a message handler for a specific action."""
        self.message_handlers[action] = handler
        logger.info(f"Registered handler for action: {action}")
```

**Key Concepts**: This registration system allows agents to expose their capabilities dynamically. When an agent receives a message with a specific action, the router can invoke the appropriate handler.

#### 1.3.5: Direct Message Sending with Response Handling

The core message sending functionality handles both fire-and-forget and request-response patterns:

```python
    async def send_message(self, message: A2AMessage, 
                         wait_for_response: bool = None) -> Optional[A2AMessage]:
        """Send a message to another agent."""
        
        if wait_for_response is None:
            wait_for_response = message.requires_response
        
        try:
            # Add to message queue for processing
            await self.message_queue.put(message)
            
            # If response is required, wait for it
            if wait_for_response:
                future = asyncio.Future()
                self.pending_requests[message.message_id] = future
                
                try:
                    response = await asyncio.wait_for(future, timeout=message.timeout)
                    return response
                except asyncio.TimeoutError:
                    logger.warning(f"Message {message.message_id} timed out")
                    return None
                finally:
                    self.pending_requests.pop(message.message_id, None)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
```

**Key Concepts**: This method demonstrates the request-response pattern in A2A communication. It uses asyncio.Future to handle asynchronous responses and implements timeout handling for reliability.

#### 1.3.6: Broadcast Messaging for Group Coordination

Broadcast functionality enables one-to-many communication for coordinating multiple agents:

```python
    async def broadcast_message(self, message: A2AMessage, 
                              capability_filter: List[str] = None) -> int:
        """Broadcast a message to multiple agents."""
        
        # Discover target agents
        agents = await self.registry.discover_agents(
            required_capabilities=capability_filter
        )
        
        sent_count = 0
        for agent in agents:
            # Create individual message for each agent
            agent_message = A2AMessage(
                message_type=MessageType.BROADCAST,
                sender_id=message.sender_id,
                recipient_id=agent.agent_id,
                action=message.action,
                payload=message.payload,
                priority=message.priority
            )
            
            try:
                await self._route_message(agent_message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send broadcast to {agent.agent_id}: {e}")
        
        logger.info(f"Broadcast sent to {sent_count} agents")
        return sent_count
```

**Key Concepts**: Broadcasting uses agent discovery to find suitable recipients based on capabilities. Each agent receives an individual message, allowing for personalized communication while maintaining broadcast semantics.

#### 1.3.7: Asynchronous Message Processing Queue

The message processing queue ensures all messages are handled efficiently without blocking:

```python
    async def _process_messages(self):
        """Process messages from the queue."""
        while True:
            try:
                message = await self.message_queue.get()
                await self._route_message(message)
                self.message_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
```

**Key Concepts**: This background task continuously processes messages from the queue, ensuring non-blocking operation. Error handling prevents one failed message from stopping the entire router.

#### 1.3.8: Intelligent Message Routing Logic

The routing logic determines the best agent to handle each message based on capabilities and availability:

```python
    async def _route_message(self, message: A2AMessage):
        """Route a message to its destination."""
        
        if message.recipient_id:
            # Direct message to specific agent
            await self._send_to_agent(message, message.recipient_id)
        else:
            # Discover suitable agents
            agents = await self.registry.discover_agents(
                required_capabilities=message.capabilities_required
            )
            
            if agents:
                # Send to the best available agent (lowest load)
                await self._send_to_agent(message, agents[0].agent_id)
            else:
                logger.warning(f"No suitable agents found for message {message.message_id}")
```

**Key Concepts**: Routing implements both direct (recipient specified) and capability-based routing. The system automatically selects the best available agent when no specific recipient is provided.

#### 1.3.9: Agent Communication and Error Handling

Actual agent communication uses HTTP to deliver messages and handle responses:

```python
    async def _send_to_agent(self, message: A2AMessage, agent_id: str):
        """Send message to a specific agent."""
        
        # Get agent endpoint
        profile = await self.registry.get_agent_profile(agent_id)
        if not profile:
            logger.error(f"Agent {agent_id} not found in registry")
            return
        
        try:
            # Send HTTP request to agent endpoint
            async with self.session.post(
                f"{profile.endpoint}/a2a/message",
                json=message.to_dict(),
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Handle response if this was a request
                    if message.requires_response:
                        response_message = A2AMessage.from_dict(response_data)
                        await self._handle_response(response_message)
                else:
                    logger.error(f"Failed to send message to {agent_id}: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error sending message to {agent_id}: {e}")
```

**Key Concepts**: HTTP-based communication allows agents to run on different machines. The method handles network errors gracefully and processes responses for request-response patterns.

#### 1.3.10: Response Correlation and Future Resolution

Response handling links incoming responses to their original requests using correlation IDs:

```python
    async def _handle_response(self, response: A2AMessage):
        """Handle a response message."""
        
        # Check if we have a pending request for this response
        correlation_id = response.correlation_id
        
        if correlation_id in self.pending_requests:
            future = self.pending_requests[correlation_id]
            if not future.done():
                future.set_result(response)
```

**Key Concepts**: Correlation IDs enable asynchronous request-response patterns. When a response arrives, the router uses the correlation ID to complete the corresponding Future, unblocking the waiting sender.

#### 1.3.11: Incoming Message Processing and Action Dispatch

Incoming messages are processed through registered handlers, enabling agents to respond to requests:

```python
    async def handle_incoming_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming message from another agent."""
        
        try:
            message = A2AMessage.from_dict(message_data)
            
            # Check if this is a response to our request
            if message.message_type == MessageType.RESPONSE:
                await self._handle_response(message)
                return {"status": "response_processed"}
            
            # Handle the message using registered handlers
            if message.action in self.message_handlers:
                handler = self.message_handlers[message.action]
                result = await handler(message)
                
                # Send response if required
                if message.requires_response:
                    response = A2AMessage(
                        message_type=MessageType.RESPONSE,
                        correlation_id=message.message_id,
                        sender_id=message.recipient_id,
                        recipient_id=message.sender_id,
                        payload=result
                    )
                    
                    return response.to_dict()
                
                return {"status": "message_processed"}
            else:
                logger.warning(f"No handler for action: {message.action}")
                return {"error": f"No handler for action: {message.action}"}
                
        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")
            return {"error": str(e)}
```

**Key Concepts**: This method completes the communication cycle by processing incoming messages, dispatching them to appropriate handlers, and generating responses when required. The message type determines whether to process as a new request or as a response to an existing request.

**Complete Implementation**: For the complete router implementation, see [`src/session7/router.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session7/router.py) in the course materials.

---

## Part 2: Multi-Agent Coordination Patterns (25 minutes)

### Step 2.1: Orchestration Pattern

Orchestration provides centralized control over multi-agent workflows, enabling complex coordination patterns where a central orchestrator manages the execution sequence, dependencies, and data flow between agents. Let's build a comprehensive orchestration system step by step.

#### 2.1.1: Workflow Data Structures and Foundation

First, let's define the core data structures that represent workflow steps and overall workflows:

```python

# a2a/orchestrator.py - Foundation and Data Structures

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from a2a.protocol import A2AMessage, MessageType, Priority
from a2a.router import MessageRouter
from a2a.registry import AgentRegistry

logger = logging.getLogger(__name__)
```

**Key Concepts**: The foundation imports support asynchronous orchestration with proper logging, type hints, and integration with our A2A communication components.

#### 2.1.2: Workflow Step Definition

Each workflow step represents a unit of work that requires specific agent capabilities:

```python
@dataclass
class WorkflowStep:
    """Represents a step in a workflow."""
    step_id: str
    action: str
    agent_capability: str
    input_mapping: Dict[str, str]  # Map workflow data to step input
    output_mapping: Dict[str, str] # Map step output to workflow data
    dependencies: List[str] = None # Other steps that must complete first
    timeout: int = 30
    retry_count: int = 2
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
```

**Key Concepts**: Workflow steps define the mapping between workflow data and agent inputs/outputs, enabling data flow through the workflow. Dependencies ensure proper execution order.

#### 2.1.3: Workflow Definition Structure

A workflow combines multiple steps with their dependencies and initial data:

```python
@dataclass
class Workflow:
    """Defines a multi-agent workflow."""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    initial_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.initial_data is None:
            self.initial_data = {}
```

**Key Concepts**: Workflows encapsulate the complete definition of a multi-agent process, including metadata and initial context data that flows through the execution.

#### 2.1.4: Orchestrator Class Initialization

The orchestrator manages workflow execution with access to the agent registry and message router:

```python
class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows."""
    
    def __init__(self, router: MessageRouter, registry: AgentRegistry):
        self.router = router
        self.registry = registry
        self.active_workflows: Dict[str, Dict] = {}
```

**Key Concepts**: The orchestrator serves as the central coordination point, maintaining state for active workflows and using the router and registry for agent communication and discovery.

#### 2.1.5: Workflow State Initialization

When starting a workflow, we establish comprehensive state tracking:

```python
    async def execute_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a multi-agent workflow."""
        
        workflow_state = {
            "workflow_id": workflow.workflow_id,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "data": workflow.initial_data.copy(),
            "completed_steps": set(),
            "failed_steps": set(),
            "step_outputs": {}
        }
        
        self.active_workflows[workflow.workflow_id] = workflow_state
```

**Key Concepts**: Workflow state tracks execution progress, data transformations, and step completion status. This enables recovery, monitoring, and debugging of complex workflows.

#### 2.1.6: Dependency Resolution and Step Selection

The orchestrator continuously evaluates which steps can execute based on dependency satisfaction:

```python
        try:
            # Execute steps based on dependencies
            remaining_steps = workflow.steps.copy()
            
            while remaining_steps:
                # Find steps that can be executed (all dependencies met)
                ready_steps = [
                    step for step in remaining_steps
                    if all(dep in workflow_state["completed_steps"] 
                          for dep in step.dependencies)
                ]
                
                if not ready_steps:
                    # Check if we have failed steps blocking progress
                    if workflow_state["failed_steps"]:
                        workflow_state["status"] = "failed"
                        break
                    
                    # Wait for more steps to complete
                    await asyncio.sleep(1)
                    continue
```

**Key Concepts**: Dependency resolution ensures proper execution order while enabling parallel execution of independent steps. Failed step detection prevents infinite waiting.

#### 2.1.7: Parallel Step Execution and Result Gathering

Ready steps execute in parallel for optimal performance:

```python
                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    task = asyncio.create_task(
                        self._execute_step(workflow, step, workflow_state)
                    )
                    tasks.append(task)
                
                # Wait for all ready steps to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
```

**Key Concepts**: Parallel execution maximizes throughput while maintaining dependency constraints. Exception handling ensures one failed step doesn't crash the entire workflow.

#### 2.1.8: Result Processing and State Management

Step results update workflow state and enable data flow to dependent steps:

```python
                # Process results
                for i, result in enumerate(results):
                    step = ready_steps[i]
                    
                    if isinstance(result, Exception):
                        logger.error(f"Step {step.step_id} failed: {result}")
                        workflow_state["failed_steps"].add(step.step_id)
                    else:
                        workflow_state["completed_steps"].add(step.step_id)
                        workflow_state["step_outputs"][step.step_id] = result
                        
                        # Apply output mapping to workflow data
                        self._apply_output_mapping(step, result, workflow_state["data"])
                
                # Remove completed and failed steps
                remaining_steps = [
                    step for step in remaining_steps
                    if step.step_id not in workflow_state["completed_steps"] 
                    and step.step_id not in workflow_state["failed_steps"]
                ]
```

**Key Concepts**: Result processing updates workflow state, applies output mappings for data flow, and removes completed steps from the execution queue.

#### 2.1.9: Workflow Completion and Status Determination

Final workflow status reflects the overall execution outcome:

```python
            # Determine final status
            if workflow_state["failed_steps"]:
                workflow_state["status"] = "failed"
            else:
                workflow_state["status"] = "completed"
            
            workflow_state["completed_at"] = datetime.now().isoformat()
            
            return {
                "workflow_id": workflow.workflow_id,
                "status": workflow_state["status"],
                "data": workflow_state["data"],
                "execution_time": workflow_state["completed_at"],
                "completed_steps": len(workflow_state["completed_steps"]),
                "failed_steps": len(workflow_state["failed_steps"])
            }
```

**Key Concepts**: Workflow completion provides comprehensive execution results including final data state, timing information, and success metrics.

#### 2.1.10: Error Handling and Workflow Cleanup

Proper error handling ensures graceful failure recovery:

```python
        except Exception as e:
            logger.error(f"Workflow {workflow.workflow_id} execution failed: {e}")
            workflow_state["status"] = "error"
            workflow_state["error"] = str(e)
            
            return {
                "workflow_id": workflow.workflow_id,
                "status": "error",
                "error": str(e)
            }
        
        finally:
            # Cleanup
            self.active_workflows.pop(workflow.workflow_id, None)
```

**Key Concepts**: Exception handling captures unexpected errors while cleanup ensures no resource leaks from abandoned workflows.

#### 2.1.11: Individual Step Execution with Agent Discovery

Each step executes by discovering suitable agents and delegating work:

```python
    async def _execute_step(self, workflow: Workflow, step: WorkflowStep, 
                          workflow_state: Dict) -> Any:
        """Execute a single workflow step."""
        
        # Prepare step input data
        step_input = self._prepare_step_input(step, workflow_state["data"])
        
        # Find suitable agent
        agents = await self.registry.discover_agents(
            required_capabilities=[step.agent_capability]
        )
        
        if not agents:
            raise Exception(f"No agents found with capability: {step.agent_capability}")
```

**Key Concepts**: Step execution begins with input preparation and agent discovery, ensuring the right agent handles each task based on required capabilities.

#### 2.1.12: Step Execution with Retry Logic and Fault Tolerance

Robust step execution includes retry mechanisms and error handling:

```python
        # Try executing with retries
        last_error = None
        for attempt in range(step.retry_count + 1):
            try:
                # Create message for agent
                message = A2AMessage(
                    sender_id="orchestrator",
                    recipient_id=agents[0].agent_id,  # Use best available agent
                    action=step.action,
                    payload=step_input,
                    requires_response=True,
                    timeout=step.timeout,
                    priority=Priority.HIGH
                )
                
                # Send message and wait for response
                response = await self.router.send_message(message, wait_for_response=True)
                
                if response and response.payload:
                    logger.info(f"Step {step.step_id} completed successfully")
                    return response.payload
                else:
                    raise Exception("No response received from agent")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Step {step.step_id} attempt {attempt + 1} failed: {e}")
                
                if attempt < step.retry_count:
                    # Try with next available agent if available
                    if len(agents) > attempt + 1:
                        continue
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise last_error
```

**Key Concepts**: Retry logic with exponential backoff and agent failover provides resilience against transient failures and agent unavailability.

#### 2.1.13: Data Mapping and Transformation Utilities

Helper methods handle data flow between workflow context and step inputs/outputs:

```python
    def _prepare_step_input(self, step: WorkflowStep, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for a workflow step."""
        step_input = {}
        
        for step_param, workflow_key in step.input_mapping.items():
            if workflow_key in workflow_data:
                step_input[step_param] = workflow_data[workflow_key]
        
        return step_input
    
    def _apply_output_mapping(self, step: WorkflowStep, step_output: Dict[str, Any], 
                            workflow_data: Dict[str, Any]):
        """Apply step output to workflow data."""
        
        for workflow_key, step_param in step.output_mapping.items():
            if step_param in step_output:
                workflow_data[workflow_key] = step_output[step_param]
```

**Key Concepts**: Data mapping enables seamless data flow through the workflow by transforming between step-specific formats and the shared workflow context.

**Complete Implementation**: For complete orchestrator examples and advanced patterns, see [`src/session7/orchestrator.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session7/orchestrator.py) in the course materials.

### Step 2.2: Choreography Pattern

Choreography enables decentralized agent coordination through event-driven patterns, where agents react to events autonomously without central control. This creates flexible, loosely-coupled systems that can adapt dynamically to changing conditions.

#### 2.2.1: Choreography Foundation and Event Structures

First, let's establish the foundation for event-driven coordination:

```python

# a2a/choreography.py - Foundation

import asyncio
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from a2a.protocol import A2AMessage, MessageType
from a2a.router import MessageRouter

logger = logging.getLogger(__name__)
```

**Key Concepts**: Choreography relies on event-driven architecture where agents publish events and subscribe to patterns, creating reactive coordination without central orchestration.

#### 2.2.2: Event Pattern Definition

Event patterns define the triggers and actions that enable autonomous agent coordination:

```python
@dataclass
class EventPattern:
    """Defines an event pattern that triggers agent actions."""
    event_type: str
    condition: str              # Python expression to evaluate
    action: str                 # Action to perform when pattern matches
    target_capability: str      # Required capability for handling agent
    priority: int = 1           # Pattern priority (higher = more important)
```

**Key Concepts**: Event patterns map event types to actions through conditional logic. Priority ordering ensures important events are processed first during high-load scenarios.

#### 2.2.3: Choreography Engine Initialization

The choreography engine manages event patterns, handlers, and event history:

```python
class ChoreographyEngine:
    """Event-driven choreography engine for agent coordination."""
    
    def __init__(self, router: MessageRouter):
        self.router = router
        self.event_patterns: List[EventPattern] = []
        self.event_handlers: Dict[str, Callable] = {}
        self.event_history: List[Dict] = []
        self.max_history = 1000
        
        # Register default message handler
        self.router.register_handler("choreography_event", self._handle_choreography_event)
```

**Key Concepts**: The engine maintains event patterns for triggering actions, handlers for processing events, and history for context-aware decision making.

#### 2.2.4: Event Pattern Registration and Management

Pattern registration enables dynamic configuration of choreography behaviors:

```python
    def register_event_pattern(self, pattern: EventPattern):
        """Register an event pattern for choreography."""
        self.event_patterns.append(pattern)
        # Sort by priority (higher priority first)
        self.event_patterns.sort(key=lambda x: x.priority, reverse=True)
        logger.info(f"Registered event pattern: {pattern.event_type}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register a handler for specific event types."""
        self.event_handlers[event_type] = handler
        logger.info(f"Registered event handler: {event_type}")
```

**Key Concepts**: Pattern registration supports dynamic choreography reconfiguration. Priority-based sorting ensures critical patterns are evaluated first.

#### 2.2.5: Event Publishing and History Management

Event publishing triggers the choreography process and maintains context history:

```python
    async def publish_event(self, event_type: str, event_data: Dict[str, Any], 
                          source_agent: str = None):
        """Publish an event that may trigger choreographed actions."""
        
        event = {
            "event_id": f"evt_{int(datetime.now().timestamp() * 1000)}",
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "source_agent": source_agent,
            "data": event_data
        }
        
        # Add to event history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        logger.info(f"Published event: {event_type} from {source_agent}")
        
        # Check event patterns and trigger actions
        await self._process_event_patterns(event)
```

**Key Concepts**: Event publishing creates structured event records with unique IDs and timestamps. History management enables pattern matching based on event sequences.

#### 2.2.6: Event Pattern Processing and Matching

Pattern processing evaluates events against registered patterns to determine triggered actions:

```python
    async def _process_event_patterns(self, event: Dict[str, Any]):
        """Process event against registered patterns."""
        
        triggered_actions = []
        
        for pattern in self.event_patterns:
            if pattern.event_type == event["event_type"] or pattern.event_type == "*":
                # Evaluate condition
                if self._evaluate_condition(pattern.condition, event):
                    triggered_actions.append(pattern)
        
        # Execute triggered actions
        for pattern in triggered_actions:
            await self._execute_choreography_action(pattern, event)
```

**Key Concepts**: Pattern matching supports both specific event types and wildcard patterns. Condition evaluation enables sophisticated trigger logic based on event content.

#### 2.2.7: Conditional Logic Evaluation

Condition evaluation determines whether patterns should trigger based on event content and context:

```python
    def _evaluate_condition(self, condition: str, event: Dict[str, Any]) -> bool:
        """Evaluate a condition expression against event data."""
        
        if not condition or condition == "true":
            return True
        
        try:
            # Create evaluation context
            context = {
                "event": event,
                "data": event["data"],
                "source": event.get("source_agent"),
                "recent_events": self.event_history[-10:]  # Last 10 events
            }
            
            # Evaluate condition (be careful with eval in production!)
            result = eval(condition, {"__builtins__": {}}, context)
            return bool(result)
            
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False
```

**Key Concepts**: Condition evaluation provides a rich context including current event data, source agent, and recent event history. Safe evaluation prevents malicious code execution.

#### 2.2.8: Choreography Action Execution

Action execution translates triggered patterns into concrete agent messages:

```python
    async def _execute_choreography_action(self, pattern: EventPattern, event: Dict[str, Any]):
        """Execute a choreography action triggered by an event pattern."""
        
        try:
            # Create action message
            action_message = A2AMessage(
                sender_id="choreography_engine",
                action=pattern.action,
                payload={
                    "trigger_event": event,
                    "pattern": {
                        "event_type": pattern.event_type,
                        "action": pattern.action
                    }
                },
                capabilities_required=[pattern.target_capability],
                requires_response=False  # Fire and forget for choreography
            )
            
            # Send to appropriate agent(s)
            await self.router.send_message(action_message)
            
            logger.info(f"Executed choreography action: {pattern.action}")
            
        except Exception as e:
            logger.error(f"Failed to execute choreography action {pattern.action}: {e}")
```

**Key Concepts**: Action execution creates A2A messages with trigger context. Fire-and-forget messaging supports asynchronous, decoupled coordination.

#### 2.2.9: Incoming Event Message Handling

Event message handling processes choreography events received from other agents:

```python
    async def _handle_choreography_event(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle incoming choreography event messages."""
        
        event_type = message.payload.get("event_type")
        event_data = message.payload.get("event_data", {})
        
        if event_type and event_type in self.event_handlers:
            handler = self.event_handlers[event_type]
            result = await handler(message)
            return result
        
        # Default handling - just acknowledge
        return {"status": "event_received", "event_type": event_type}
```

**Key Concepts**: Message handling enables agents to receive and process choreography events from other agents, supporting distributed event-driven coordination.

#### 2.2.10: Practical Choreography Example

Let's see a complete choreography pattern for travel planning coordination:

```python

# Example choreography patterns

def create_travel_planning_choreography() -> List[EventPattern]:
    """Create choreography patterns for travel planning scenario."""
    
    return [
        EventPattern(
            event_type="trip_requested",
            condition="data.get('destination') is not None",
            action="get_weather_forecast",
            target_capability="weather_forecasting",
            priority=5
        ),
        EventPattern(
            event_type="weather_obtained",
            condition="data.get('temperature') is not None",
            action="find_accommodations", 
            target_capability="accommodation_search",
            priority=4
        ),
        EventPattern(
            event_type="accommodations_found",
            condition="len(data.get('hotels', [])) > 0",
            action="book_transportation",
            target_capability="transportation_booking",
            priority=3
        ),
        EventPattern(
            event_type="transportation_booked",
            condition="data.get('booking_confirmed') == True",
            action="create_itinerary",
            target_capability="itinerary_planning",
            priority=2
        ),
        EventPattern(
            event_type="itinerary_ready",
            condition="data.get('itinerary') is not None",
            action="send_confirmation",
            target_capability="notification_service",
            priority=1
        )
    ]
```

**Key Concepts**: This example demonstrates a complete travel planning workflow where each event triggers the next step. Agents coordinate autonomously based on event-driven patterns, creating a flexible, decentralized process.

**Complete Implementation**: For advanced choreography patterns and complex event processing, see [`src/session7/choreography.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session7/choreography.py) in the course materials.

---

## Chapter Summary

Congratulations! You've built a comprehensive A2A communication system with the following capabilities:

### Communication Infrastructure Implemented

#### **Protocol Layer**

- **Standardized messaging** with A2AMessage protocol
- **Agent profiles** with capability descriptions  
- **Message routing** with priority and timeout handling
- **Service discovery** through centralized registry

#### **Coordination Patterns**

- **Orchestration** for centralized workflow management
- **Choreography** for event-driven agent coordination
- **Multi-step workflows** with dependency management
- **Fault tolerance** with retries and error handling

#### **Distributed Architecture**

- **Agent registry** with heartbeat monitoring
- **Message broadcasting** for group coordination
- **Load balancing** based on agent availability
- **Event patterns** for reactive behavior

---

## Testing Your Understanding

### Quick Check Questions

1. **What is the primary advantage of A2A communication over direct API calls?**
   - A) Better performance
   - B) Dynamic discovery and loose coupling
   - C) Simpler implementation
   - D) Lower latency

2. **In orchestration patterns, who controls the workflow execution?**
   - A) Each individual agent
   - B) The first agent in the chain
   - C) A central orchestrator
   - D) The user interface

3. **What triggers actions in choreography patterns?**
   - A) Direct commands
   - B) Scheduled timers
   - C) Published events
   - D) User requests

4. **How does agent discovery work in the A2A system?**
   - A) Fixed configuration files
   - B) Capability-based matching in registry
   - C) Random selection
   - D) First-come-first-served

5. **What is the purpose of message correlation IDs?**
   - A) Security authentication
   - B) Performance optimization
   - C) Linking requests with responses
   - D) Message encryption

### Practical Exercise

Create a multi-agent customer service system:

```python
class CustomerServiceChoreography:
    """Multi-agent customer service with A2A coordination."""
    
    def __init__(self, choreography_engine: ChoreographyEngine):
        self.engine = choreography_engine
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Set up choreography patterns for customer service."""
        
        patterns = [
            # TODO: Define patterns for:
            # 1. Customer inquiry received -> Route to appropriate agent
            # 2. Technical issue detected -> Escalate to technical support
            # 3. Resolution provided -> Update customer and close ticket
            # 4. Escalation needed -> Notify supervisor agent
        ]
        
        for pattern in patterns:
            self.engine.register_event_pattern(pattern)
```

**Hint:** Check the [**🗂️ View Test Solutions →**](Session7_Test_Solutions.md) for complete implementations and advanced patterns.

---

## Next Session Preview

In Session 8, we'll explore **Advanced Agent Workflows** including:
- Complex multi-agent orchestration patterns
- Agent specialization and role-based coordination  
- Performance optimization for large agent networks
- Monitoring and observability for distributed agent systems

### Homework

1. **Implement peer-to-peer agent discovery** without centralized registry
2. **Create conflict resolution mechanisms** for competing agent requests
3. **Add message encryption** for secure agent communication
4. **Build agent load balancing** with health-based routing

---

## Test Your Knowledge

Ready to test your understanding of Agent-to-Agent Communication? Take our comprehensive multiple-choice test to verify your mastery of the concepts.

## Multiple Choice Test - Session 7

Test your understanding of Agent-to-Agent Communication:

**Question 1:** What is the primary purpose of Agent-to-Agent (A2A) communication?

A) To reduce computational costs  
B) To improve individual agent performance  
C) To enable multiple agents to collaborate and coordinate actions  
D) To replace human operators  

**Question 2:** Which message type is used for finding agents with specific capabilities?

A) RESPONSE  
B) HEARTBEAT  
C) DISCOVERY  
D) REQUEST  

**Question 3:** What information is essential for proper A2A message routing?

A) Just the timestamp  
B) Only the priority level  
C) Only the message content  
D) Sender ID, recipient ID, and message type  

**Question 4:** What is the difference between orchestration and choreography in multi-agent systems?

A) Orchestration uses centralized control, choreography uses distributed coordination  
B) Choreography requires more memory  
C) There is no difference  
D) Orchestration is faster than choreography  

**Question 5:** How do agents announce their capabilities in an A2A system?

A) Using ANNOUNCEMENT messages with capability metadata  
B) Through manual configuration  
C) Via external databases only  
D) Through file-based configurations  

**Question 6:** What mechanism ensures A2A communication reliability when agents become unavailable?

A) Faster processing  
B) Increased memory allocation  
C) Message queuing with retry logic and timeouts  
D) Multiple network interfaces  

**Question 7:** What is the purpose of capability negotiation in A2A systems?

A) To improve performance  
B) To match agent capabilities with task requirements  
C) To simplify configuration  
D) To reduce costs  

**Question 8:** When should URGENT priority be used for A2A messages?

A) For time-critical operations requiring immediate attention  
B) For data backup operations  
C) For routine status updates  
D) For all important messages  

**Question 9:** What is the purpose of correlation IDs in A2A messaging?

A) To validate message integrity  
B) To encrypt messages  
C) To compress message content  
D) To link related messages in multi-step workflows  

**Question 10:** What is a key benefit of collaborative agent teams in A2A systems?

A) Diverse expertise and parallel problem-solving capabilities  
B) Lower computational requirements  
C) Reduced network traffic  
D) Simpler implementation  

[**🗂️ View Test Solutions →**](Session7_Test_Solutions.md)

---

## Additional Resources

- [Multi-Agent Systems Design Patterns](https://example.com/mas-patterns)
- [Distributed Systems Consensus Algorithms](https://example.com/consensus)
- [Message Queue Architectures](https://example.com/message-queues)
- [Event-Driven Architecture Patterns](https://example.com/eda-patterns)

Remember: Great multi-agent systems balance autonomy with coordination, enabling agents to work together while maintaining their independence! 🤖🤝🤖