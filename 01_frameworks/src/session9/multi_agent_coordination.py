"""
Multi-Agent Coordination Systems
Session 8: Advanced Communication and Coordination Protocols

This module implements sophisticated multi-agent coordination patterns including
communication hubs, hierarchical coordination, and competitive task allocation
mechanisms for scalable agent collaboration.
"""

from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import uuid
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of inter-agent messages"""
    REQUEST = "request"
    RESPONSE = "response"
    PROPOSAL = "proposal"
    VOTE = "vote"
    CONSENSUS = "consensus"
    DELEGATION = "delegation"
    STATUS_UPDATE = "status_update"
    EMERGENCY = "emergency"
    COORDINATION = "coordination"
    NOTIFICATION = "notification"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class AgentRole(Enum):
    """Agent roles in coordination hierarchy"""
    COORDINATOR = "coordinator"
    WORKER = "worker"
    SPECIALIST = "specialist"
    MONITOR = "monitor"
    MEDIATOR = "mediator"


class CoordinationStrategy(Enum):
    """Coordination strategies"""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"
    DEMOCRATIC = "democratic"
    COMPETITIVE = "competitive"


@dataclass
class AgentMessage:
    """Structured message for inter-agent communication"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""
    message_type: MessageType = MessageType.REQUEST
    priority: MessagePriority = MessagePriority.NORMAL
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    requires_response: bool = True
    conversation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        return self.expires_at is not None and datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'message_type': self.message_type.value,
            'priority': self.priority.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'requires_response': self.requires_response,
            'conversation_id': self.conversation_id,
            'metadata': self.metadata
        }


@dataclass
class AgentCapability:
    """Represents an agent's capability for task allocation"""
    capability_id: str
    name: str
    skill_level: float  # 0.0 to 1.0
    capacity: int  # How many tasks can handle simultaneously
    cost_per_task: float
    availability: float  # 0.0 to 1.0
    specializations: List[str] = field(default_factory=list)


class BaseCoordinationAgent:
    """Base agent class for coordination systems"""
    
    def __init__(self, agent_id: str, role: AgentRole, capabilities: List[AgentCapability] = None):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities or []
        self.status = "active"
        self.communication_hub: Optional['CommunicationHub'] = None
        self.message_history: List[AgentMessage] = []
        self.task_queue: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {
            'tasks_completed': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'average_response_time': 0.0,
            'success_rate': 1.0
        }
    
    async def set_communication_hub(self, hub: 'CommunicationHub'):
        """Set the communication hub for this agent"""
        self.communication_hub = hub
    
    async def receive_message(self, message: AgentMessage) -> bool:
        """Receive and process incoming message"""
        try:
            if message.is_expired():
                logger.warning(f"Agent {self.agent_id} received expired message {message.message_id}")
                return False
            
            self.message_history.append(message)
            self.performance_metrics['messages_received'] += 1
            
            # Process message based on type
            await self._process_message(message)
            
            # Send response if required
            if message.requires_response:
                response = await self._generate_response(message)
                if response and self.communication_hub:
                    await self.communication_hub.send_message(response)
            
            return True
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed to process message: {str(e)}")
            return False
    
    async def send_message(self, recipient_id: str, message_type: MessageType, 
                          content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL) -> bool:
        """Send message to another agent"""
        
        if not self.communication_hub:
            logger.error(f"Agent {self.agent_id} has no communication hub")
            return False
        
        message = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            priority=priority,
            content=content
        )
        
        success = await self.communication_hub.send_message(message)
        if success:
            self.performance_metrics['messages_sent'] += 1
        
        return success
    
    async def broadcast_message(self, message_type: MessageType, content: Dict[str, Any], 
                               exclude_self: bool = True) -> Dict[str, bool]:
        """Broadcast message to all agents"""
        
        if not self.communication_hub:
            return {}
        
        results = {}
        for agent_id in self.communication_hub.agents.keys():
            if exclude_self and agent_id == self.agent_id:
                continue
                
            success = await self.send_message(agent_id, message_type, content)
            results[agent_id] = success
        
        return results
    
    async def _process_message(self, message: AgentMessage):
        """Process received message based on type"""
        
        if message.message_type == MessageType.REQUEST:
            await self._handle_request(message)
        elif message.message_type == MessageType.PROPOSAL:
            await self._handle_proposal(message)
        elif message.message_type == MessageType.VOTE:
            await self._handle_vote(message)
        elif message.message_type == MessageType.DELEGATION:
            await self._handle_delegation(message)
        elif message.message_type == MessageType.STATUS_UPDATE:
            await self._handle_status_update(message)
        elif message.message_type == MessageType.EMERGENCY:
            await self._handle_emergency(message)
        else:
            await self._handle_generic_message(message)
    
    async def _handle_request(self, message: AgentMessage):
        """Handle request message"""
        request_type = message.content.get('request_type')
        logger.info(f"Agent {self.agent_id} handling request: {request_type}")
        
        if request_type == 'capability_inquiry':
            # Respond with capabilities
            await self._respond_with_capabilities(message)
        elif request_type == 'task_assignment':
            # Handle task assignment
            await self._handle_task_assignment(message)
        elif request_type == 'status_inquiry':
            # Respond with status
            await self._respond_with_status(message)
    
    async def _handle_proposal(self, message: AgentMessage):
        """Handle proposal message"""
        proposal = message.content.get('proposal')
        logger.info(f"Agent {self.agent_id} evaluating proposal: {proposal}")
        
        # Evaluate proposal based on agent's criteria
        evaluation = await self._evaluate_proposal(proposal)
        
        # Send vote response
        vote_content = {
            'proposal_id': message.content.get('proposal_id'),
            'vote': evaluation['vote'],
            'rationale': evaluation['rationale']
        }
        
        await self.send_message(
            message.sender_id, MessageType.VOTE, vote_content
        )
    
    async def _generate_response(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Generate appropriate response to message"""
        
        if message.message_type == MessageType.REQUEST:
            return AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content={'status': 'processed', 'original_message_id': message.message_id},
                requires_response=False
            )
        
        return None
    
    async def _respond_with_capabilities(self, message: AgentMessage):
        """Respond with agent capabilities"""
        
        capabilities_data = [
            {
                'capability_id': cap.capability_id,
                'name': cap.name,
                'skill_level': cap.skill_level,
                'capacity': cap.capacity,
                'availability': cap.availability
            } for cap in self.capabilities
        ]
        
        response_content = {
            'agent_id': self.agent_id,
            'role': self.role.value,
            'capabilities': capabilities_data,
            'status': self.status,
            'current_load': len(self.task_queue)
        }
        
        await self.send_message(
            message.sender_id, MessageType.RESPONSE, response_content
        )
    
    async def _evaluate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a proposal and return vote decision"""
        
        # Simple evaluation based on agent's role and capabilities
        if self.role == AgentRole.COORDINATOR:
            # Coordinators evaluate based on strategic fit
            vote = "approve" if proposal.get('strategic_value', 0) > 0.5 else "reject"
        elif self.role == AgentRole.WORKER:
            # Workers evaluate based on feasibility
            vote = "approve" if proposal.get('feasibility', 0) > 0.6 else "reject"
        else:
            # Default evaluation
            vote = "approve" if proposal.get('overall_score', 0) > 0.5 else "abstain"
        
        return {
            'vote': vote,
            'rationale': f"Evaluated based on {self.role.value} criteria"
        }
    
    async def _handle_task_assignment(self, message: AgentMessage):
        """Handle task assignment request"""
        task = message.content.get('task')
        if task:
            self.task_queue.append(task)
            logger.info(f"Agent {self.agent_id} accepted task: {task.get('task_id', 'unknown')}")
    
    async def _handle_delegation(self, message: AgentMessage):
        """Handle delegation message"""
        delegation = message.content.get('delegation')
        logger.info(f"Agent {self.agent_id} received delegation: {delegation}")
    
    async def _handle_status_update(self, message: AgentMessage):
        """Handle status update message"""
        update = message.content.get('update')
        logger.info(f"Agent {self.agent_id} received status update: {update}")
    
    async def _handle_emergency(self, message: AgentMessage):
        """Handle emergency message"""
        emergency = message.content.get('emergency')
        logger.warning(f"Agent {self.agent_id} handling emergency: {emergency}")
        # Implement emergency response logic
    
    async def _respond_with_status(self, message: AgentMessage):
        """Respond with current status"""
        status_content = {
            'agent_id': self.agent_id,
            'status': self.status,
            'role': self.role.value,
            'current_tasks': len(self.task_queue),
            'performance_metrics': self.performance_metrics
        }
        
        await self.send_message(
            message.sender_id, MessageType.RESPONSE, status_content
        )
    
    async def _handle_generic_message(self, message: AgentMessage):
        """Handle generic message types"""
        logger.info(f"Agent {self.agent_id} received generic message of type {message.message_type}")


class CommunicationHub:
    """Central coordination hub for multi-agent communication"""
    
    def __init__(self, max_agents: int = 100):
        self.agents: Dict[str, BaseCoordinationAgent] = {}
        self.max_agents = max_agents
        self.message_queue: List[AgentMessage] = []
        self.active_conversations: Dict[str, List[AgentMessage]] = {}
        self.delivery_confirmations: Dict[str, bool] = {}
        self.message_stats: Dict[str, int] = {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0
        }
        self.routing_rules: List[Callable[[AgentMessage], bool]] = []
        self.message_filters: List[Callable[[AgentMessage], bool]] = []
    
    async def register_agent(self, agent: BaseCoordinationAgent) -> bool:
        """Register agent with communication hub"""
        
        if len(self.agents) >= self.max_agents:
            logger.error(f"Cannot register agent {agent.agent_id}: Hub at capacity")
            return False
        
        if agent.agent_id in self.agents:
            logger.warning(f"Agent {agent.agent_id} already registered")
            return False
        
        self.agents[agent.agent_id] = agent
        await agent.set_communication_hub(self)
        
        logger.info(f"Agent {agent.agent_id} registered with hub")
        return True
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister agent from hub"""
        
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} unregistered from hub")
            return True
        
        return False
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send message with delivery confirmation and routing"""
        
        try:
            self.message_stats['total_sent'] += 1
            
            # Apply message filters
            for filter_func in self.message_filters:
                if not filter_func(message):
                    logger.warning(f"Message {message.message_id} filtered out")
                    return False
            
            # Check if recipient exists
            if message.recipient_id not in self.agents:
                logger.error(f"Recipient {message.recipient_id} not found")
                self.message_stats['total_failed'] += 1
                return False
            
            # Handle message expiration
            if message.is_expired():
                logger.warning(f"Message {message.message_id} expired before delivery")
                self.message_stats['total_failed'] += 1
                return False
            
            # Add to conversation thread
            if message.conversation_id:
                if message.conversation_id not in self.active_conversations:
                    self.active_conversations[message.conversation_id] = []
                self.active_conversations[message.conversation_id].append(message)
            
            # Apply routing rules
            for rule in self.routing_rules:
                if not rule(message):
                    logger.info(f"Message {message.message_id} rerouted by rule")
            
            # Deliver message
            recipient = self.agents[message.recipient_id]
            success = await recipient.receive_message(message)
            
            self.delivery_confirmations[message.message_id] = success
            
            if success:
                self.message_stats['total_delivered'] += 1
            else:
                self.message_stats['total_failed'] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send message {message.message_id}: {str(e)}")
            self.message_stats['total_failed'] += 1
            return False
    
    async def broadcast_message(self, sender_id: str, message_type: MessageType, 
                               content: Dict[str, Any], exclude_sender: bool = True) -> Dict[str, bool]:
        """Broadcast message to all agents"""
        
        results = {}
        for agent_id in self.agents.keys():
            if exclude_sender and agent_id == sender_id:
                continue
            
            message = AgentMessage(
                sender_id=sender_id,
                recipient_id=agent_id,
                message_type=message_type,
                content=content
            )
            
            success = await self.send_message(message)
            results[agent_id] = success
        
        return results
    
    def add_message_filter(self, filter_func: Callable[[AgentMessage], bool]):
        """Add message filter function"""
        self.message_filters.append(filter_func)
    
    def add_routing_rule(self, rule_func: Callable[[AgentMessage], bool]):
        """Add message routing rule"""
        self.routing_rules.append(rule_func)
    
    def get_agent_list(self) -> List[str]:
        """Get list of registered agent IDs"""
        return list(self.agents.keys())
    
    def get_conversation_history(self, conversation_id: str) -> List[AgentMessage]:
        """Get conversation history by ID"""
        return self.active_conversations.get(conversation_id, [])
    
    def get_hub_statistics(self) -> Dict[str, Any]:
        """Get hub statistics"""
        return {
            'total_agents': len(self.agents),
            'message_stats': self.message_stats,
            'active_conversations': len(self.active_conversations),
            'delivery_rate': (
                self.message_stats['total_delivered'] / 
                max(1, self.message_stats['total_sent'])
            )
        }


class HierarchicalCoordinator:
    """Implements hierarchical multi-agent coordination patterns"""
    
    def __init__(self, communication_hub: CommunicationHub):
        self.hub = communication_hub
        self.coordinator_agents: Dict[str, BaseCoordinationAgent] = {}
        self.worker_agents: Dict[str, BaseCoordinationAgent] = {}
        self.hierarchy_levels: Dict[str, int] = {}
        self.delegation_rules: Dict[str, List[str]] = {}
        self.coordination_strategy = CoordinationStrategy.HIERARCHICAL
    
    async def create_coordination_hierarchy(self, task: str, 
                                          complexity_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create hierarchical coordination structure based on task complexity"""
        
        logger.info(f"Creating hierarchy for task: {task}")
        
        # Analyze task decomposition requirements
        decomposition = await self._analyze_task_decomposition(task, complexity_analysis)
        
        # Create coordinator agents for high-level planning
        coordinators = await self._create_coordinator_layer(decomposition)
        
        # Create worker agents for execution
        workers = await self._create_worker_layer(decomposition)
        
        # Establish delegation relationships
        delegation_map = await self._establish_delegation_hierarchy(
            coordinators, workers, decomposition
        )
        
        hierarchy = {
            'coordinators': coordinators,
            'workers': workers,
            'delegation_map': delegation_map,
            'hierarchy_depth': decomposition['required_levels'],
            'task': task,
            'created_at': datetime.now()
        }
        
        logger.info(f"Created hierarchy with {len(coordinators)} coordinators and {len(workers)} workers")
        return hierarchy
    
    async def execute_hierarchical_task(self, task: str, 
                                       hierarchy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using hierarchical coordination"""
        
        execution_start = datetime.now()
        execution_trace = []
        
        # Phase 1: Top-level planning by coordinators
        logger.info("Phase 1: High-level planning")
        high_level_plan = await self._create_high_level_plan(
            task, hierarchy['coordinators']
        )
        execution_trace.append(('planning', high_level_plan))
        
        # Phase 2: Task delegation and parallel execution
        logger.info("Phase 2: Task delegation")
        delegation_results = await self._execute_delegated_tasks(
            high_level_plan, hierarchy['delegation_map']
        )
        execution_trace.append(('delegation', delegation_results))
        
        # Phase 3: Result aggregation and quality assessment
        logger.info("Phase 3: Result aggregation")
        final_result = await self._aggregate_hierarchical_results(
            delegation_results, hierarchy['coordinators']
        )
        execution_trace.append(('aggregation', final_result))
        
        execution_duration = datetime.now() - execution_start
        
        return {
            'task': task,
            'result': final_result,
            'execution_trace': execution_trace,
            'duration': execution_duration,
            'hierarchy_performance': await self._assess_hierarchy_performance(
                execution_trace
            ),
            'success': final_result.get('success', False)
        }
    
    async def _analyze_task_decomposition(self, task: str, 
                                         complexity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task for hierarchical decomposition requirements"""
        
        # Simple decomposition analysis based on complexity
        required_levels = min(3, max(1, complexity.get('complexity_score', 1)))
        estimated_subtasks = complexity.get('subtask_count', 3)
        
        return {
            'required_levels': required_levels,
            'estimated_subtasks': estimated_subtasks,
            'coordination_needs': complexity.get('coordination_complexity', 'medium'),
            'parallelization_potential': complexity.get('parallel_potential', 0.7)
        }
    
    async def _create_coordinator_layer(self, decomposition: Dict[str, Any]) -> List[BaseCoordinationAgent]:
        """Create coordinator agents for high-level management"""
        
        coordinator_count = max(1, decomposition['required_levels'])
        coordinators = []
        
        for i in range(coordinator_count):
            coordinator = BaseCoordinationAgent(
                agent_id=f"coordinator_{i}",
                role=AgentRole.COORDINATOR,
                capabilities=[
                    AgentCapability(
                        capability_id=f"coordination_{i}",
                        name="Task Coordination",
                        skill_level=0.9,
                        capacity=5,
                        cost_per_task=10.0,
                        availability=1.0,
                        specializations=["planning", "delegation", "oversight"]
                    )
                ]
            )
            
            await self.hub.register_agent(coordinator)
            coordinators.append(coordinator)
            self.coordinator_agents[coordinator.agent_id] = coordinator
        
        return coordinators
    
    async def _create_worker_layer(self, decomposition: Dict[str, Any]) -> List[BaseCoordinationAgent]:
        """Create worker agents for task execution"""
        
        worker_count = decomposition['estimated_subtasks']
        workers = []
        
        for i in range(worker_count):
            worker = BaseCoordinationAgent(
                agent_id=f"worker_{i}",
                role=AgentRole.WORKER,
                capabilities=[
                    AgentCapability(
                        capability_id=f"execution_{i}",
                        name="Task Execution",
                        skill_level=0.8,
                        capacity=3,
                        cost_per_task=5.0,
                        availability=1.0,
                        specializations=["execution", "analysis", "reporting"]
                    )
                ]
            )
            
            await self.hub.register_agent(worker)
            workers.append(worker)
            self.worker_agents[worker.agent_id] = worker
        
        return workers
    
    async def _establish_delegation_hierarchy(self, coordinators: List[BaseCoordinationAgent],
                                             workers: List[BaseCoordinationAgent],
                                             decomposition: Dict[str, Any]) -> Dict[str, List[str]]:
        """Establish delegation relationships between coordinators and workers"""
        
        delegation_map = {}
        
        # Simple round-robin delegation
        workers_per_coordinator = max(1, len(workers) // len(coordinators))
        
        for i, coordinator in enumerate(coordinators):
            start_idx = i * workers_per_coordinator
            end_idx = min(len(workers), start_idx + workers_per_coordinator)
            assigned_workers = [w.agent_id for w in workers[start_idx:end_idx]]
            delegation_map[coordinator.agent_id] = assigned_workers
        
        return delegation_map
    
    async def _create_high_level_plan(self, task: str, 
                                     coordinators: List[BaseCoordinationAgent]) -> Dict[str, Any]:
        """Create high-level plan using coordinators"""
        
        # Mock high-level planning
        plan = {
            'task': task,
            'subtasks': [
                {'subtask_id': f'subtask_{i}', 'description': f'Subtask {i} for {task}'}
                for i in range(3)
            ],
            'coordination_strategy': self.coordination_strategy.value,
            'estimated_duration': timedelta(minutes=30),
            'resource_requirements': {'cpu': 'medium', 'memory': 'low'}
        }
        
        # Broadcast plan to coordinators
        for coordinator in coordinators:
            await coordinator.send_message(
                "system", MessageType.NOTIFICATION, 
                {'type': 'plan_created', 'plan': plan}
            )
        
        return plan
    
    async def _execute_delegated_tasks(self, plan: Dict[str, Any], 
                                      delegation_map: Dict[str, List[str]]) -> Dict[str, Any]:
        """Execute tasks through delegation hierarchy"""
        
        delegation_results = {}
        
        for coordinator_id, worker_ids in delegation_map.items():
            coordinator = self.coordinator_agents[coordinator_id]
            
            # Delegate subtasks to workers
            subtask_results = []
            for i, worker_id in enumerate(worker_ids):
                if i < len(plan['subtasks']):
                    subtask = plan['subtasks'][i]
                    
                    # Send delegation message
                    delegation_content = {
                        'delegation_type': 'task_assignment',
                        'task': subtask,
                        'deadline': datetime.now() + timedelta(minutes=10)
                    }
                    
                    success = await coordinator.send_message(
                        worker_id, MessageType.DELEGATION, delegation_content
                    )
                    
                    subtask_results.append({
                        'subtask_id': subtask['subtask_id'],
                        'worker_id': worker_id,
                        'delegated_successfully': success,
                        'status': 'delegated'
                    })
            
            delegation_results[coordinator_id] = subtask_results
        
        return delegation_results
    
    async def _aggregate_hierarchical_results(self, delegation_results: Dict[str, Any],
                                             coordinators: List[BaseCoordinationAgent]) -> Dict[str, Any]:
        """Aggregate results from hierarchical execution"""
        
        total_subtasks = sum(len(results) for results in delegation_results.values())
        successful_delegations = sum(
            sum(1 for r in results if r['delegated_successfully'])
            for results in delegation_results.values()
        )
        
        success_rate = successful_delegations / total_subtasks if total_subtasks > 0 else 0.0
        
        return {
            'success': success_rate > 0.8,
            'total_subtasks': total_subtasks,
            'successful_delegations': successful_delegations,
            'success_rate': success_rate,
            'coordinator_count': len(coordinators),
            'delegation_results': delegation_results
        }
    
    async def _assess_hierarchy_performance(self, execution_trace: List[Tuple[str, Any]]) -> Dict[str, Any]:
        """Assess performance of hierarchical coordination"""
        
        phase_performance = {}
        for phase_name, phase_result in execution_trace:
            if isinstance(phase_result, dict) and 'success' in phase_result:
                phase_performance[phase_name] = phase_result['success']
            else:
                phase_performance[phase_name] = True  # Assume success if no explicit indicator
        
        overall_success = all(phase_performance.values())
        
        return {
            'overall_success': overall_success,
            'phase_performance': phase_performance,
            'coordination_efficiency': sum(phase_performance.values()) / len(phase_performance),
            'phases_completed': len(execution_trace)
        }


# Demonstration and testing functions
async def demonstrate_coordination_system():
    """Demonstrate multi-agent coordination capabilities"""
    
    print("🤝 Multi-Agent Coordination System Demonstration")
    print("=" * 55)
    
    # Initialize communication hub
    hub = CommunicationHub(max_agents=20)
    
    # Create various types of agents
    coordinator = BaseCoordinationAgent("coord_1", AgentRole.COORDINATOR)
    worker1 = BaseCoordinationAgent("worker_1", AgentRole.WORKER)
    worker2 = BaseCoordinationAgent("worker_2", AgentRole.WORKER)
    specialist = BaseCoordinationAgent("spec_1", AgentRole.SPECIALIST)
    
    # Register agents with hub
    await hub.register_agent(coordinator)
    await hub.register_agent(worker1)
    await hub.register_agent(worker2)
    await hub.register_agent(specialist)
    
    print(f"📊 Registered {len(hub.agents)} agents with communication hub")
    
    # Demonstrate message passing
    print("\n💬 Testing Message Communication:")
    
    # Send request from coordinator to worker
    await coordinator.send_message(
        "worker_1", MessageType.REQUEST, 
        {'request_type': 'capability_inquiry', 'details': 'What can you do?'}
    )
    
    # Broadcast status update
    broadcast_results = await coordinator.broadcast_message(
        MessageType.STATUS_UPDATE, 
        {'status': 'coordination_active', 'timestamp': datetime.now().isoformat()}
    )
    
    print(f"✅ Broadcast sent to {sum(broadcast_results.values())} agents successfully")
    
    # Demonstrate hierarchical coordination
    print("\n🏗️ Testing Hierarchical Coordination:")
    
    hierarchical_coordinator = HierarchicalCoordinator(hub)
    
    # Create hierarchy for complex task
    task = "Analyze market trends and generate comprehensive report"
    complexity_analysis = {
        'complexity_score': 2,
        'subtask_count': 4,
        'coordination_complexity': 'high',
        'parallel_potential': 0.8
    }
    
    hierarchy = await hierarchical_coordinator.create_coordination_hierarchy(
        task, complexity_analysis
    )
    
    print(f"🎯 Created hierarchy with {hierarchy['hierarchy_depth']} levels")
    
    # Execute hierarchical task
    execution_result = await hierarchical_coordinator.execute_hierarchical_task(
        task, hierarchy
    )
    
    print(f"⚡ Task execution completed: Success={execution_result['success']}")
    print(f"⏱️  Execution time: {execution_result['duration'].total_seconds():.2f}s")
    
    # Show hub statistics
    stats = hub.get_hub_statistics()
    print(f"\n📈 Hub Statistics:")
    print(f"   Total agents: {stats['total_agents']}")
    print(f"   Messages sent: {stats['message_stats']['total_sent']}")
    print(f"   Delivery rate: {stats['delivery_rate']:.1%}")
    
    return {
        'hub': hub,
        'hierarchy_result': execution_result,
        'stats': stats
    }


if __name__ == "__main__":
    asyncio.run(demonstrate_coordination_system())