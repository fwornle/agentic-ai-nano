# Session 7: Agent-to-Agent Communication

A2A enables multiple AI agents to communicate, coordinate, and share information across different platforms using JSON-RPC 2.0 based communication, agent discovery systems, and multi-agent orchestration patterns.

![A2A Communication Architecture](images/a2a-communication-architecture.png)

---

## Part 1: A2A Protocol Architecture

### Core Protocol Components

1. **Agent Cards**: JSON documents advertising agent capabilities, endpoints, and requirements
2. **Task Management**: Formal task lifecycle with states (pending, working, completed, failed)
3. **Message Exchange**: JSON-RPC 2.0 over HTTP(S) with streaming support via Server-Sent Events
4. **Authentication**: Enterprise-grade security with OpenAPI authentication scheme parity
5. **Distributed Coordination**: Cross-platform task coordination with unique tracking identifiers

### A2A Message Structure

JSON-RPC 2.0 based A2A protocol implementation:

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

This implementation provides task tracking with unique identifiers, formal lifecycle management, and structured artifact storage.

### Agent Card Implementation

Agent Cards for capability discovery:

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

### Agent Registry and Discovery

Dynamic service discovery, health monitoring, and intelligent agent selection based on capabilities and availability.

#### Registry Infrastructure

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

Redis provides fast, distributed storage for agent profiles and capability indices, supporting both single-node and clustered deployments.

#### Registry Class and Configuration Management

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

The registry uses prefixed keys for organization and capability indices for fast lookup. Heartbeat configuration ensures timely detection of agent failures.

#### Agent Registration

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

#### Agent Unregistration

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

#### Heartbeat Updates

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

#### Agent Discovery

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

#### Agent Filtering

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

#### Profile Retrieval

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

#### Liveness Detection

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

#### Dead Agent Cleanup

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


Complete implementation: [`src/session7/registry.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session7/registry.py)

### Message Router

#### Router Foundation

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

#### Router Class Structure

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

#### Lifecycle Management

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

#### Handler Registration

```python
    def register_handler(self, action: str, handler: Callable):
        """Register a message handler for a specific action."""
        self.message_handlers[action] = handler
        logger.info(f"Registered handler for action: {action}")
```

#### Message Sending

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

#### Broadcast Messaging

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

#### Message Processing Queue

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

#### Message Routing Logic

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

#### Agent Communication

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

#### Response Correlation

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

#### Incoming Message Processing

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


Complete implementation: [`src/session7/router.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session7/router.py)

---

## Part 2: Multi-Agent Coordination Patterns

### Orchestration Pattern

Centralized control over multi-agent workflows with a central orchestrator managing execution sequence, dependencies, and data flow.

#### Workflow Data Structures

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

#### Workflow Step Definition

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

#### Workflow Definition Structure

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

#### Orchestrator Class Initialization

```python
class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows."""
    
    def __init__(self, router: MessageRouter, registry: AgentRegistry):
        self.router = router
        self.registry = registry
        self.active_workflows: Dict[str, Dict] = {}
```

#### Workflow State Initialization

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

#### Dependency Resolution and Step Selection

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

#### Parallel Step Execution and Result Gathering

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

#### Result Processing and State Management

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

#### Workflow Completion and Status Determination

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

#### Error Handling and Workflow Cleanup

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

#### Individual Step Execution with Agent Discovery

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

#### Step Execution with Retry Logic and Fault Tolerance

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

#### Data Mapping and Transformation Utilities

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


Complete implementation: [`src/session7/orchestrator.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session7/orchestrator.py)

### Choreography Pattern

Decentralized agent coordination through event-driven patterns where agents react to events autonomously without central control.

#### Choreography Foundation

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

#### Event Pattern Definition

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

#### Choreography Engine Initialization

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

#### Event Pattern Registration and Management

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

#### Event Publishing and History Management

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

#### Event Pattern Processing and Matching

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

#### Conditional Logic Evaluation

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

#### Choreography Action Execution

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

#### Incoming Event Message Handling

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

#### Practical Choreography Example

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


Complete implementation: [`src/session7/choreography.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session7/choreography.py)

---

This session covered A2A communication system implementation including standardized messaging, message routing, orchestration patterns, choreography patterns, and distributed architecture components.

## Multiple Choice Test - Session 7

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

## Navigation

**Previous:** [Session 6 - ACP Fundamentals](Session6_ACP_Fundamentals.md)
**Next:** [Session 8 - Advanced Agent Workflows](Session8_Advanced_Agent_Workflows.md)