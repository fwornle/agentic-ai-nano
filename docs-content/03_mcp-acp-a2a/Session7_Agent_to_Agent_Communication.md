# Session 7: Agent-to-Agent Communication

## The Grand Alliance: When Digital Minds Must Unite

Picture this: You're witnessing the formation of the United Nations, but instead of human diplomats around a conference table, you're watching AI agents from different organizations, platforms, and purposes coming together for the first time. Each agent speaks its own technical dialect, operates under different protocols, and serves different masters—yet they must find a way to collaborate on challenges too complex for any single mind to solve.

This is the reality of modern AI systems. Your weather prediction agent in the cloud needs to coordinate with a logistics agent on a factory floor. Your data analysis agent running in a hospital must collaborate with research agents in laboratories across the world. Your financial trading agent has to work with risk assessment agents, market data agents, and compliance agents in real-time harmony.

*Welcome to Agent-to-Agent (A2A) Communication—where artificial minds learn the art of diplomacy, cooperation, and collective intelligence.*

![A2A Communication Architecture](images/a2a-communication-architecture.png)

---

## Part 1: The Universal Language of Digital Diplomacy

Before agents can collaborate, they need to establish diplomatic protocols—a universal language that transcends the boundaries of individual platforms, organizations, and technical implementations.

### The Five Pillars of A2A Civilization

Think of A2A as the constitution for a society of digital minds:

1. **Agent Cards**: Like diplomatic credentials, these JSON documents announce what each agent can do, where to find them, and how to work with them
2. **Task Management**: A formal lifecycle that tracks every collaboration from initial request to final resolution
3. **Message Exchange**: JSON-RPC 2.0 over HTTP(S)—the diplomatic language that any agent can speak and understand
4. **Authentication**: Enterprise-grade security that ensures only authorized agents can participate in sensitive collaborations
5. **Distributed Coordination**: The ability to track complex, multi-step collaborations across organizational boundaries

### The DNA of Agent Diplomacy: Message Structure

Every conversation between agents follows a carefully designed diplomatic protocol. Like formal diplomatic correspondence, each message contains essential metadata for proper routing, processing, and response:

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

This implementation provides task tracking with unique identifiers, formal lifecycle management, and structured artifact storage—everything needed for enterprise-scale collaboration.

### Digital Passports: Agent Card Implementation

Each agent in the A2A ecosystem carries a digital passport—an Agent Card that serves as both identification and capability advertisement:

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

This Agent Card is like a business card, resume, and service contract all rolled into one. Other agents can examine it to understand not just what this agent can do, but how to work with it professionally.

---

## Part 2: The Embassy System: Agent Registry and Discovery

Imagine a world where every embassy maintains a comprehensive directory of all diplomatic personnel from every nation. That's exactly what the Agent Registry provides—a living, breathing directory where agents announce their presence, capabilities, and availability.

### The Heart of Digital Diplomacy

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

Redis provides the backbone of our embassy system—fast, distributed storage that can scale from a single server to a global network of interconnected registries.

### The Registry Architecture: Managing Digital Citizens

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

The registry uses a sophisticated indexing system. Not only does it store complete agent profiles, but it also maintains capability indices—think of them as specialized phone books where you can look up "who can analyze financial data" or "which agents speak multiple languages."

### The Registration Ceremony: Joining the Digital Society

When an agent joins the A2A network, it goes through a formal registration process, much like a diplomat presenting credentials at a new embassy:

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

### Graceful Departures: The Unregistration Process

When an agent needs to leave the network—whether for maintenance, shutdown, or migration—it can formally announce its departure:

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

### The Pulse of Digital Life: Heartbeat Management

Like embassies maintaining contact with their home countries, agents must regularly send heartbeats to prove they're still operational:

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

### Intelligent Discovery: Finding the Right Partner

The discovery process is like having a master diplomat who knows exactly which expert to call for any given challenge:

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

### Maintaining the Digital Census

The registry automatically maintains its accuracy by detecting and removing agents that have gone silent:

```python
    def _is_agent_alive(self, profile: AgentProfile) -> bool:
        """Check if agent is still alive based on heartbeat."""
        try:
            last_heartbeat = datetime.fromisoformat(profile.last_heartbeat)
            now = datetime.now()
            
            return (now - last_heartbeat).total_seconds() < self.heartbeat_timeout
            
        except Exception:
            return False

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

---

## Part 3: The Message Routing Network: Digital Post Office

Think of the Message Router as the world's most sophisticated post office, capable of routing millions of messages between agents while ensuring perfect delivery, handling timeouts, and managing responses.

### The Foundation of Digital Communication

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

### The Router's Brain: Message Management

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

The router maintains several critical data structures: a registry for finding agents, handlers for processing different message types, pending requests for tracking responses, and a queue for managing message flow.

### The Art of Message Sending

Sending a message in the A2A world is like sending a diplomatic cable—it must be properly formatted, routed through the correct channels, and tracked until completion:

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

### Broadcasting: Speaking to the Masses

Sometimes, an agent needs to communicate with multiple agents simultaneously—like a UN secretary-general addressing all member nations:

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

### The Message Processing Engine

Behind the scenes, a dedicated task continuously processes the message queue, ensuring that every message reaches its intended destination:

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

---

## Part 4: The Art of Orchestration - Conducting Digital Symphonies

Orchestration in A2A systems is like conducting a symphony orchestra where each musician is an AI agent with unique capabilities. The conductor doesn't play any instruments but ensures that all parts come together to create something beautiful.

### The Symphony Framework

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

### Defining Musical Movements: Workflow Steps

Each step in a workflow is like a movement in a symphony—it has specific requirements, depends on what came before, and contributes to the overall composition:

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

### The Master Conductor: Workflow Orchestrator

The orchestrator manages the entire performance, ensuring each agent enters at the right time with the right information:

```python
class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows."""
    
    def __init__(self, router: MessageRouter, registry: AgentRegistry):
        self.router = router
        self.registry = registry
        self.active_workflows: Dict[str, Dict] = {}

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

### The Performance: Dependency Resolution and Execution

The orchestrator carefully manages which steps can run in parallel and which must wait for others to complete:

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

                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    task = asyncio.create_task(
                        self._execute_step(workflow, step, workflow_state)
                    )
                    tasks.append(task)
                
                # Wait for all ready steps to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)

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

### Individual Performance: Step Execution

Each step is executed with careful attention to failure handling, retries, and agent selection:

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

---

## Part 5: The Dance of Autonomy - Choreography Patterns

While orchestration is like conducting a symphony, choreography is like a perfectly synchronized dance where each performer knows their role and responds to the movements of others without a central conductor.

### The Philosophy of Distributed Harmony

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

### Defining Dance Steps: Event Patterns

Each event pattern is like a dance move that triggers when specific conditions are met:

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

### The Dance Studio: Choreography Engine

The choreography engine watches for events and triggers appropriate responses, like a dance instructor who recognizes when it's time for the next movement:

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

### Publishing Events: Broadcasting Dance Cues

When something significant happens, agents can publish events that may trigger coordinated responses from other agents:

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

### The Intelligence of Pattern Recognition

The engine evaluates complex conditions to determine when patterns should trigger:

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

### A Real-World Dance: Travel Planning Choreography

Here's how choreography works in practice—imagine a travel planning system where different agents respond to events in sequence:

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

This creates a beautiful chain reaction: when someone requests a trip, it triggers weather forecasting, which enables accommodation search, which enables transportation booking, which enables itinerary creation, which triggers confirmation—all without any central coordinator managing the process.

---

## The Future of Digital Collaboration

As we conclude this exploration of Agent-to-Agent communication, let's reflect on what we've built and why it matters for the future of AI.

### What We've Accomplished

We've created a comprehensive framework for digital minds to collaborate across any boundary:

- **Universal Communication**: A standardized protocol that works regardless of platform, language, or implementation
- **Intelligent Discovery**: Agents can find each other based on capabilities rather than hardcoded connections
- **Flexible Coordination**: Both centralized orchestration and distributed choreography patterns
- **Enterprise Reliability**: Task tracking, retry logic, heartbeat monitoring, and graceful failure handling
- **Scalable Architecture**: From local networks to global enterprise deployments

### The Transformation of AI Systems

We've moved from isolated, single-purpose AI systems to collaborative networks of specialized agents that can:

- **Self-Organize**: Agents discover and coordinate with each other automatically
- **Adapt to Failure**: When agents go offline, others can pick up their responsibilities
- **Scale Dynamically**: New capabilities can be added by simply introducing new agents
- **Work Across Boundaries**: Organizational, technical, and geographical barriers become irrelevant

### The Promise of Tomorrow

The A2A framework we've built opens the door to AI systems that truly reflect the collaborative nature of human intelligence. Just as humans accomplish great things by working together, AI agents can now form dynamic teams that are greater than the sum of their parts.

Imagine emergency response systems where medical AI agents automatically coordinate with logistics agents, weather agents, and resource management agents during disasters. Picture research environments where data analysis agents from different institutions collaborate in real-time to accelerate scientific discoveries. Envision business systems where agents from different companies can negotiate, collaborate, and execute complex transactions autonomously.

This isn't science fiction—it's the natural evolution of AI systems from isolated tools to collaborative partners.

---

## Test Your Diplomatic Skills

Before we venture into advanced workflows, let's ensure you've mastered the art of agent diplomacy:

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
