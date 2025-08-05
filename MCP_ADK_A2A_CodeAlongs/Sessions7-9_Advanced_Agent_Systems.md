# Sessions 7-9: Advanced Agent Systems - Code-Along Tutorials

## Session 7: Multi-Tool Agent System (2 hours)

### 🎯 Learning Objectives
- Orchestrate multiple agents and MCP servers
- Implement complex agent workflows
- Build agent coordination patterns
- Create multi-step task execution

### Part 1: Agent Orchestrator (45 minutes)

```python
# agents/orchestrator.py
import asyncio
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
import uuid
import logging

from agents.base_agent import BaseADKAgent
from agents.weather_agent import WeatherAgent

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentTask:
    """Represents a task for an agent."""
    task_id: str
    agent_id: str
    task_type: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = None
    dependencies: List[str] = None

class MultiAgentOrchestrator:
    """Orchestrates multiple agents for complex workflows."""
    
    def __init__(self):
        self.agents: Dict[str, BaseADKAgent] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
    async def register_agent(self, agent: BaseADKAgent):
        """Register an agent with the orchestrator."""
        await agent.initialize()
        self.agents[agent.agent_id] = agent
        
    async def execute_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """Execute a multi-agent workflow."""
        workflow_id = str(uuid.uuid4())
        
        # Parse workflow
        tasks = self._parse_workflow(workflow_definition)
        
        # Execute tasks
        results = await self._execute_task_graph(tasks)
        
        return {
            "workflow_id": workflow_id,
            "results": results,
            "status": "completed"
        }
    
    def _parse_workflow(self, definition: Dict[str, Any]) -> List[AgentTask]:
        """Parse workflow definition into tasks."""
        tasks = []
        
        for step in definition.get("steps", []):
            task = AgentTask(
                task_id=str(uuid.uuid4()),
                agent_id=step["agent"],
                task_type=step["action"],
                parameters=step.get("parameters", {}),
                dependencies=step.get("depends_on", [])
            )
            tasks.append(task)
        
        return tasks
    
    async def _execute_task_graph(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """Execute tasks respecting dependencies."""
        completed_tasks = {}
        pending_tasks = {task.task_id: task for task in tasks}
        
        while pending_tasks:
            # Find tasks with satisfied dependencies
            ready_tasks = []
            
            for task in pending_tasks.values():
                if not task.dependencies or all(
                    dep in completed_tasks for dep in task.dependencies
                ):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                raise Exception("Circular dependency in workflow")
            
            # Execute ready tasks in parallel
            results = await asyncio.gather(*[
                self._execute_task(task) for task in ready_tasks
            ])
            
            # Update completed tasks
            for task, result in zip(ready_tasks, results):
                completed_tasks[task.task_id] = result
                del pending_tasks[task.task_id]
        
        return completed_tasks
    
    async def _execute_task(self, task: AgentTask) -> Any:
        """Execute a single task."""
        agent = self.agents.get(task.agent_id)
        if not agent:
            raise Exception(f"Agent {task.agent_id} not found")
        
        # Route to appropriate method based on task type
        if task.task_type == "get_weather":
            return await agent.call_mcp_tool(
                "weather_get_weather", 
                task.parameters
            )
        elif task.task_type == "analyze_data":
            return await agent.call_mcp_tool(
                "data_process_data",
                task.parameters
            )
        
        return None

# Example workflow definition
TRAVEL_PLANNING_WORKFLOW = {
    "name": "Travel Planning",
    "description": "Plan travel with weather and data analysis",
    "steps": [
        {
            "id": "weather_check",
            "agent": "weather_agent",
            "action": "get_weather",
            "parameters": {"city": "Paris", "include_forecast": True}
        },
        {
            "id": "data_analysis", 
            "agent": "data_agent",
            "action": "analyze_data",
            "parameters": {"data": {"type": "travel_costs"}},
            "depends_on": ["weather_check"]
        }
    ]
}
```

### Part 2: Complex Agent Coordination (45 minutes)

```python
# agents/coordination_patterns.py
from typing import Dict, List, Any, AsyncIterator
import asyncio
from enum import Enum

class CoordinationPattern(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel" 
    PIPELINE = "pipeline"
    SCATTER_GATHER = "scatter_gather"

class AgentCoordinator:
    """Implements various agent coordination patterns."""
    
    async def execute_sequential(self, agents: List[BaseADKAgent], 
                                tasks: List[Dict[str, Any]]) -> List[Any]:
        """Execute tasks sequentially across agents."""
        results = []
        
        for i, (agent, task) in enumerate(zip(agents, tasks)):
            # Pass previous result as context
            if i > 0:
                task["context"] = results[i-1]
            
            result = await self._execute_agent_task(agent, task)
            results.append(result)
        
        return results
    
    async def execute_parallel(self, agents: List[BaseADKAgent],
                              tasks: List[Dict[str, Any]]) -> List[Any]:
        """Execute tasks in parallel across agents."""
        coroutines = [
            self._execute_agent_task(agent, task)
            for agent, task in zip(agents, tasks)
        ]
        
        return await asyncio.gather(*coroutines)
    
    async def execute_pipeline(self, agents: List[BaseADKAgent],
                              initial_data: Any) -> Any:
        """Execute pipeline pattern where output feeds next agent."""
        current_data = initial_data
        
        for agent in agents:
            current_data = await self._execute_agent_task(
                agent, {"data": current_data}
            )
        
        return current_data
    
    async def execute_scatter_gather(self, agents: List[BaseADKAgent],
                                   shared_task: Dict[str, Any]) -> Dict[str, Any]:
        """Scatter task to all agents, gather results."""
        # Scatter phase
        coroutines = [
            self._execute_agent_task(agent, shared_task.copy())
            for agent in agents
        ]
        
        results = await asyncio.gather(*coroutines)
        
        # Gather phase - combine results
        return {
            "agents": [agent.agent_id for agent in agents],
            "results": results,
            "combined": await self._combine_results(results)
        }
    
    async def _execute_agent_task(self, agent: BaseADKAgent, 
                                 task: Dict[str, Any]) -> Any:
        """Execute a task on a specific agent."""
        # Start a conversation if needed
        session_id = await agent.start_conversation("system")
        
        try:
            # Send message and get response
            message = task.get("message", "Process the provided data")
            response = await agent.send_message(session_id, message)
            
            return {
                "agent_id": agent.agent_id,
                "response": response,
                "task": task
            }
        finally:
            await agent.end_conversation(session_id)
    
    async def _combine_results(self, results: List[Any]) -> Dict[str, Any]:
        """Combine results from multiple agents."""
        return {
            "summary": f"Processed {len(results)} agent responses",
            "consensus": "Results combined successfully",
            "details": results
        }
```

### Session 7 Quiz

1. **What is the main challenge in multi-agent coordination?**
   - A) Memory usage
   - B) Dependency management and task ordering
   - C) Network latency
   - D) User authentication

2. **Which pattern is best for independent tasks?**
   - A) Sequential
   - B) Parallel
   - C) Pipeline  
   - D) Scatter-gather

---

## Session 8: Basic A2A Server (2 hours)

### 🎯 Learning Objectives
- Implement Agent-to-Agent (A2A) protocol
- Create agent discovery mechanisms
- Build A2A communication patterns
- Deploy A2A-enabled agents

### Part 1: A2A Protocol Implementation (60 minutes)

```python
# a2a/protocol.py
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, AsyncIterator
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentCard:
    """Agent Card for A2A discovery."""
    agent_id: str
    name: str
    description: str
    version: str
    capabilities: List[str]
    supported_protocols: List[str] = None
    endpoints: Dict[str, str] = None
    metadata: Dict[str, Any] = None

@dataclass
class A2AMessage:
    """A2A message structure."""
    message_id: str
    conversation_id: str
    from_agent: str
    to_agent: str
    message_type: str
    content: Any
    timestamp: str
    metadata: Dict[str, Any] = None

class A2AServer:
    """A2A protocol server implementation."""
    
    def __init__(self, agent: BaseADKAgent):
        self.agent = agent
        self.app = FastAPI(title=f"A2A Server - {agent.agent_name}")
        self.agent_card: Optional[AgentCard] = None
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up A2A protocol routes."""
        
        @self.app.get("/.well-known/agent.json")
        async def get_agent_card():
            """Return agent card for discovery."""
            if not self.agent_card:
                await self._generate_agent_card()
            
            return asdict(self.agent_card)
        
        @self.app.post("/a2a/message")
        async def receive_message(message: Dict[str, Any]):
            """Receive A2A message from another agent."""
            try:
                a2a_message = A2AMessage(**message)
                response = await self._process_a2a_message(a2a_message)
                return response
            except Exception as e:
                logger.error(f"A2A message error: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/a2a/stream")
        async def stream_conversation(request: Dict[str, Any]):
            """Handle streaming A2A conversation."""
            return StreamingResponse(
                self._stream_a2a_conversation(request),
                media_type="text/event-stream"
            )
        
        @self.app.get("/a2a/capabilities")
        async def get_capabilities():
            """Get detailed agent capabilities."""
            return await self.agent.get_agent_info()
    
    async def _generate_agent_card(self):
        """Generate agent card from agent info."""
        agent_info = await self.agent.get_agent_info()
        
        self.agent_card = AgentCard(
            agent_id=agent_info["agent_id"],
            name=agent_info["name"],
            description=agent_info["description"],
            version=agent_info.get("version", "1.0.0"),
            capabilities=agent_info["capabilities"],
            supported_protocols=["a2a-v1", "mcp"],
            endpoints={
                "message": "/a2a/message",
                "stream": "/a2a/stream",
                "capabilities": "/a2a/capabilities"
            },
            metadata={
                "category": agent_info.get("category", "general"),
                "specializations": agent_info.get("specializations", [])
            }
        )
    
    async def _process_a2a_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Process incoming A2A message."""
        # Start conversation with the agent
        session_id = await self.agent.start_conversation(message.from_agent)
        
        try:
            # Send message to agent
            response = await self.agent.send_message(
                session_id, 
                str(message.content)
            )
            
            # Create response message
            response_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                conversation_id=message.conversation_id,
                from_agent=self.agent.agent_id,
                to_agent=message.from_agent,
                message_type="response",
                content=response,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            return asdict(response_message)
            
        finally:
            await self.agent.end_conversation(session_id)
    
    async def _stream_a2a_conversation(self, request: Dict[str, Any]) -> AsyncIterator[str]:
        """Stream A2A conversation responses."""
        session_id = await self.agent.start_conversation(request.get("from_agent", "unknown"))
        
        try:
            # Simulate streaming response
            messages = request.get("messages", [])
            
            for message in messages:
                response = await self.agent.send_message(session_id, message)
                
                # Format as Server-Sent Event
                event_data = {
                    "type": "message",
                    "data": {
                        "content": response,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
                
                yield f"data: {json.dumps(event_data)}\n\n"
                await asyncio.sleep(0.1)  # Small delay for streaming effect
        
        finally:
            await self.agent.end_conversation(session_id)

class A2AClient:
    """A2A protocol client for inter-agent communication."""
    
    def __init__(self):
        self.discovered_agents: Dict[str, AgentCard] = {}
    
    async def discover_agent(self, agent_url: str) -> Optional[AgentCard]:
        """Discover an agent via A2A protocol."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{agent_url}/.well-known/agent.json") as response:
                    if response.status == 200:
                        data = await response.json()
                        agent_card = AgentCard(**data)
                        self.discovered_agents[agent_card.agent_id] = agent_card
                        return agent_card
        except Exception as e:
            logger.error(f"Agent discovery failed: {e}")
        
        return None
    
    async def send_message(self, target_agent_url: str, message: str, 
                          from_agent_id: str) -> Dict[str, Any]:
        """Send A2A message to another agent."""
        a2a_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            conversation_id=str(uuid.uuid4()),
            from_agent=from_agent_id,
            to_agent="target_agent",
            message_type="request",
            content=message,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{target_agent_url}/a2a/message",
                json=asdict(a2a_message)
            ) as response:
                return await response.json()
```

### Part 2: Agent Discovery and Communication (60 minutes)

```python
# a2a/discovery.py
from typing import Dict, List, Set
import asyncio
import aiohttp
from urllib.parse import urljoin

class AgentRegistry:
    """Registry for discovered agents."""
    
    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}
        self.capabilities_index: Dict[str, Set[str]] = {}
    
    def register_agent(self, agent_card: AgentCard):
        """Register an agent in the registry."""
        self.agents[agent_card.agent_id] = agent_card
        
        # Index by capabilities
        for capability in agent_card.capabilities:
            if capability not in self.capabilities_index:
                self.capabilities_index[capability] = set()
            self.capabilities_index[capability].add(agent_card.agent_id)
    
    def find_agents_by_capability(self, capability: str) -> List[AgentCard]:
        """Find agents with specific capability."""
        agent_ids = self.capabilities_index.get(capability, set())
        return [self.agents[agent_id] for agent_id in agent_ids]
    
    def get_all_agents(self) -> List[AgentCard]:
        """Get all registered agents."""
        return list(self.agents.values())

class AgentNetworkManager:
    """Manages agent network and communication."""
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.known_endpoints: Set[str] = set()
    
    async def discover_network(self, seed_endpoints: List[str]):
        """Discover agent network from seed endpoints."""
        to_discover = set(seed_endpoints)
        discovered = set()
        
        while to_discover:
            endpoint = to_discover.pop()
            if endpoint in discovered:
                continue
            
            discovered.add(endpoint)
            
            # Discover agent
            agent_card = await self._discover_single_agent(endpoint)
            if agent_card:
                self.registry.register_agent(agent_card)
                
                # Add any peer endpoints from metadata
                peers = agent_card.metadata.get("peers", [])
                to_discover.update(peers)
    
    async def _discover_single_agent(self, endpoint: str) -> Optional[AgentCard]:
        """Discover a single agent."""
        try:
            agent_url = urljoin(endpoint, "/.well-known/agent.json")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(agent_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return AgentCard(**data)
        except:
            pass
        
        return None
    
    async def coordinate_agents(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple agents for a task."""
        required_capabilities = task.get("required_capabilities", [])
        
        # Find suitable agents
        suitable_agents = []
        for capability in required_capabilities:
            agents = self.registry.find_agents_by_capability(capability)
            suitable_agents.extend(agents)
        
        # Remove duplicates
        unique_agents = {agent.agent_id: agent for agent in suitable_agents}
        
        return {
            "task_id": task.get("id"),
            "assigned_agents": list(unique_agents.keys()),
            "coordination_strategy": "round_robin"
        }
```

---

## Session 9: Agent Network (2 hours)

### 🎯 Learning Objectives
- Build distributed agent networks
- Implement agent mesh communication
- Create fault-tolerant agent systems
- Deploy production agent networks

### Part 1: Distributed Agent Architecture (60 minutes)

```python
# distributed/agent_mesh.py
import asyncio
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import consul
import etcd3
import json

@dataclass 
class AgentNode:
    """Represents an agent node in the mesh."""
    node_id: str
    agent_id: str
    address: str
    port: int
    health_status: str
    capabilities: List[str]
    load: float = 0.0

class AgentMesh:
    """Manages distributed agent mesh network."""
    
    def __init__(self, service_discovery: str = "consul"):
        self.service_discovery = service_discovery
        self.local_agents: Dict[str, BaseADKAgent] = {}
        self.remote_nodes: Dict[str, AgentNode] = {}
        
        # Initialize service discovery
        if service_discovery == "consul":
            self.consul = consul.Consul()
        elif service_discovery == "etcd":
            self.etcd = etcd3.client()
    
    async def join_mesh(self, node_info: AgentNode):
        """Join the agent mesh network."""
        # Register with service discovery
        await self._register_node(node_info)
        
        # Discover existing nodes
        await self._discover_nodes()
        
        # Start health monitoring
        asyncio.create_task(self._health_monitor())
    
    async def _register_node(self, node: AgentNode):
        """Register node with service discovery."""
        if self.service_discovery == "consul":
            self.consul.agent.service.register(
                name="agent-mesh",
                service_id=node.node_id,
                address=node.address,
                port=node.port,
                tags=node.capabilities,
                check=consul.Check.http(f"http://{node.address}:{node.port}/health", "10s")
            )
    
    async def _discover_nodes(self):
        """Discover other nodes in the mesh."""
        if self.service_discovery == "consul":
            _, services = self.consul.health.service("agent-mesh", passing=True)
            
            for service in services:
                node_id = service['Service']['ID']
                if node_id not in self.remote_nodes:
                    node = AgentNode(
                        node_id=node_id,
                        agent_id=service['Service']['Tags'][0] if service['Service']['Tags'] else node_id,
                        address=service['Service']['Address'],
                        port=service['Service']['Port'],
                        health_status="healthy",
                        capabilities=service['Service']['Tags']
                    )
                    self.remote_nodes[node_id] = node
    
    async def route_message(self, target_capability: str, message: str) -> Optional[str]:
        """Route message to agent with specific capability."""
        # Find suitable nodes
        suitable_nodes = [
            node for node in self.remote_nodes.values()
            if target_capability in node.capabilities and node.health_status == "healthy"
        ]
        
        if not suitable_nodes:
            return None
        
        # Load balancing - choose node with lowest load
        target_node = min(suitable_nodes, key=lambda n: n.load)
        
        # Send message
        return await self._send_to_node(target_node, message)
    
    async def _send_to_node(self, node: AgentNode, message: str) -> str:
        """Send message to specific node."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{node.address}:{node.port}/a2a/message",
                json={"content": message}
            ) as response:
                result = await response.json()
                return result.get("content", "")
    
    async def _health_monitor(self):
        """Monitor health of mesh nodes."""
        while True:
            await self._discover_nodes()  # Refresh node list
            await asyncio.sleep(30)  # Check every 30 seconds

class LoadBalancer:
    """Load balancer for agent mesh."""
    
    def __init__(self, mesh: AgentMesh):
        self.mesh = mesh
        self.request_counts: Dict[str, int] = {}
    
    async def select_agent(self, capability: str) -> Optional[AgentNode]:
        """Select best agent for capability."""
        suitable_nodes = [
            node for node in self.mesh.remote_nodes.values()
            if capability in node.capabilities
        ]
        
        if not suitable_nodes:
            return None
        
        # Round-robin selection
        return min(suitable_nodes, key=lambda n: self.request_counts.get(n.node_id, 0))
```

### Part 2: Fault Tolerance and Resilience (60 minutes)

```python
# distributed/resilience.py
import asyncio
from typing import Dict, List, Optional
from enum import Enum
import time
import logging

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker for agent communication."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise e

class RetryManager:
    """Retry mechanism for failed operations."""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def retry(self, func, *args, **kwargs):
        """Retry function with exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.backoff_factor ** attempt
                    await asyncio.sleep(delay)
        
        raise last_exception

class FaultTolerantAgentClient:
    """Fault-tolerant client for agent communication."""
    
    def __init__(self, mesh: AgentMesh):
        self.mesh = mesh
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_manager = RetryManager()
    
    async def send_message_with_fallback(self, capability: str, message: str, 
                                       fallback_agents: List[str] = None) -> Optional[str]:
        """Send message with fallback options."""
        # Primary attempt
        try:
            return await self._send_with_circuit_breaker(capability, message)
        except Exception as e:
            logging.warning(f"Primary send failed: {e}")
        
        # Fallback attempts
        if fallback_agents:
            for fallback_capability in fallback_agents:
                try:
                    return await self._send_with_circuit_breaker(fallback_capability, message)
                except:
                    continue
        
        return None
    
    async def _send_with_circuit_breaker(self, capability: str, message: str) -> str:
        """Send message with circuit breaker protection."""
        if capability not in self.circuit_breakers:
            self.circuit_breakers[capability] = CircuitBreaker()
        
        circuit_breaker = self.circuit_breakers[capability]
        
        return await circuit_breaker.call(
            self.retry_manager.retry,
            self.mesh.route_message,
            capability,
            message
        )
```

### Session 9 Capstone: Complete Agent Network

```python
# main.py - Complete example
async def main():
    """Run complete agent network demo."""
    
    # Create agents
    weather_agent = WeatherAgent()
    
    # Create A2A servers
    weather_a2a = A2AServer(weather_agent)
    
    # Create mesh
    mesh = AgentMesh()
    
    # Create network manager
    network_manager = AgentNetworkManager()
    
    # Start discovery
    await network_manager.discover_network([
        "http://localhost:8080",
        "http://localhost:8081"
    ])
    
    # Demonstrate coordination
    task = {
        "id": "travel_planning",
        "required_capabilities": ["weather", "data_analysis"]
    }
    
    coordination_result = await network_manager.coordinate_agents(task)
    print(f"Coordination result: {coordination_result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Session 7-9 Quiz

1. **What is the main benefit of agent orchestration?**
   - A) Reduced memory usage
   - B) Coordinated multi-step workflows
   - C) Faster response times
   - D) Better security

2. **How does A2A protocol enable agent discovery?**
   - A) Database queries
   - B) Agent cards at well-known URLs
   - C) Broadcast messages
   - D) Configuration files

3. **What is the purpose of circuit breakers in agent networks?**
   - A) Load balancing
   - B) Fault tolerance and preventing cascade failures
   - C) Message routing
   - D) Authentication

4. **Which service discovery system is commonly used for agent mesh?**
   - A) DNS
   - B) Consul or etcd
   - C) LDAP
   - D) HTTP

## Final Assessment

Create a complete distributed agent system that:
1. Has 3+ specialized agents (weather, data, travel planning)
2. Uses A2A protocol for discovery and communication
3. Implements fault tolerance with circuit breakers
4. Deploys to cloud platform with monitoring
5. Demonstrates complex multi-agent workflows

Your system should handle agent failures gracefully and provide comprehensive logging and monitoring.

---

## 📝 Complete Course Summary

You've mastered:
- ✅ MCP protocol implementation and deployment
- ✅ ADK agent development with Vertex AI
- ✅ A2A inter-agent communication
- ✅ Production deployment and security
- ✅ Distributed agent networks
- ✅ Fault tolerance and resilience patterns

### Career Readiness
You can now build production-ready agentic AI systems using industry-standard protocols and patterns.

---

## Additional Resources
- [A2A Protocol Specification](https://a2aprotocol.ai/)
- [Google Cloud Agent Builder](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder)
- [Consul Service Discovery](https://www.consul.io/)
- [Production Agent Patterns](https://github.com/agentic-patterns)