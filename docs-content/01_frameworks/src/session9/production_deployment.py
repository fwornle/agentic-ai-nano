"""
Production-Ready Multi-Agent System Architecture
Session 8: Scalable Deployment and Enterprise Integration

This module implements production-ready multi-agent system architecture with
comprehensive monitoring, fault tolerance, load balancing, and enterprise
integration capabilities for large-scale deployments.
"""

from typing import Dict, List, Any, Optional, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
import uuid
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
import weakref
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemStatus(Enum):
    """System operational status"""
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    SHUTTING_DOWN = "shutting_down"
    DOWN = "down"


class AgentStatus(Enum):
    """Individual agent status"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESOURCE_BASED = "resource_based"
    CAPABILITY_BASED = "capability_based"


class ScalingPolicy(Enum):
    """Auto-scaling policies"""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    QUEUE_LENGTH = "queue_length"
    RESPONSE_TIME = "response_time"
    CUSTOM_METRIC = "custom_metric"


@dataclass
class ProductionConfig:
    """Configuration for production multi-agent system"""
    # System limits
    max_agents: int = 100
    max_concurrent_tasks: int = 1000
    max_memory_usage_mb: int = 4096
    max_cpu_usage_percent: float = 80.0
    
    # Timeouts
    agent_startup_timeout: timedelta = timedelta(seconds=30)
    task_execution_timeout: timedelta = timedelta(minutes=10)
    health_check_interval: timedelta = timedelta(seconds=30)
    metrics_collection_interval: timedelta = timedelta(seconds=10)
    
    # Retry and fault tolerance
    max_task_retries: int = 3
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: timedelta = timedelta(minutes=1)
    
    # Persistence and caching
    enable_persistence: bool = True
    enable_caching: bool = True
    cache_ttl: timedelta = timedelta(minutes=30)
    
    # Security
    enable_authentication: bool = True
    enable_authorization: bool = True
    enable_encryption: bool = True
    
    # Monitoring and logging
    enable_detailed_metrics: bool = True
    enable_distributed_tracing: bool = True
    log_level: str = "INFO"
    
    # Load balancing and scaling
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.RESOURCE_BASED
    enable_auto_scaling: bool = True
    min_agent_instances: int = 2
    max_agent_instances: int = 20
    scaling_cooldown: timedelta = timedelta(minutes=5)


@dataclass
class SystemMetrics:
    """System performance and health metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # System resources
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_mb: float = 0.0
    network_io_bytes: Dict[str, int] = field(default_factory=dict)
    
    # Agent metrics
    total_agents: int = 0
    active_agents: int = 0
    idle_agents: int = 0
    error_agents: int = 0
    
    # Task metrics
    tasks_queued: int = 0
    tasks_processing: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_task_duration: float = 0.0
    
    # Performance metrics
    requests_per_second: float = 0.0
    average_response_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'system_resources': {
                'cpu_usage_percent': self.cpu_usage_percent,
                'memory_usage_mb': self.memory_usage_mb,
                'disk_usage_mb': self.disk_usage_mb,
                'network_io_bytes': self.network_io_bytes
            },
            'agent_metrics': {
                'total_agents': self.total_agents,
                'active_agents': self.active_agents,
                'idle_agents': self.idle_agents,
                'error_agents': self.error_agents
            },
            'task_metrics': {
                'tasks_queued': self.tasks_queued,
                'tasks_processing': self.tasks_processing,
                'tasks_completed': self.tasks_completed,
                'tasks_failed': self.tasks_failed,
                'average_task_duration': self.average_task_duration
            },
            'performance_metrics': {
                'requests_per_second': self.requests_per_second,
                'average_response_time': self.average_response_time,
                'error_rate': self.error_rate,
                'throughput': self.throughput
            }
        }


@dataclass
class AgentInstance:
    """Represents a deployed agent instance"""
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str = ""
    status: AgentStatus = AgentStatus.INITIALIZING
    capabilities: List[str] = field(default_factory=list)
    current_load: int = 0
    max_capacity: int = 10
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    health_score: float = 1.0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_healthy(self, heartbeat_timeout: timedelta = timedelta(minutes=2)) -> bool:
        """Check if agent instance is healthy"""
        return (datetime.now() - self.last_heartbeat) < heartbeat_timeout and self.status != AgentStatus.ERROR
    
    def is_available(self) -> bool:
        """Check if agent can accept new tasks"""
        return (self.status in [AgentStatus.ACTIVE, AgentStatus.IDLE] and 
                self.current_load < self.max_capacity and
                self.health_score > 0.5)
    
    def get_utilization_rate(self) -> float:
        """Get current utilization rate"""
        return self.current_load / self.max_capacity if self.max_capacity > 0 else 0.0


class CircuitBreaker:
    """Circuit breaker for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, timeout: timedelta = timedelta(minutes=1)):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == "open":
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e


class ProductionAgentManager:
    """Manages agent lifecycle in production environment"""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.agent_instances: Dict[str, AgentInstance] = {}
        self.agent_pools: Dict[str, List[str]] = {}  # Agent type -> instance IDs
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=config.max_concurrent_tasks)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.load_balancer = LoadBalancer(config.load_balancing_strategy)
        self.auto_scaler = AutoScaler(config) if config.enable_auto_scaling else None
        
        # Thread pool for blocking operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Management state
        self.is_shutting_down = False
        self.startup_complete = False
        
    async def startup(self):
        """Initialize production system"""
        logger.info("Starting production multi-agent system...")
        
        # Initialize minimum agent instances
        await self._initialize_minimum_agents()
        
        # Start background tasks
        self._start_background_tasks()
        
        self.startup_complete = True
        logger.info("Production system startup complete")
    
    async def shutdown(self):
        """Graceful shutdown of production system"""
        logger.info("Initiating graceful shutdown...")
        self.is_shutting_down = True
        
        # Stop accepting new tasks
        await self._drain_task_queue()
        
        # Terminate all agents gracefully
        await self._terminate_all_agents()
        
        # Cleanup resources
        self.executor.shutdown(wait=True)
        
        logger.info("Graceful shutdown complete")
    
    async def deploy_agent(self, agent_type: str, agent_config: Dict[str, Any]) -> str:
        """Deploy new agent instance"""
        
        if len(self.agent_instances) >= self.config.max_agents:
            raise Exception(f"Maximum agent limit ({self.config.max_agents}) reached")
        
        instance = AgentInstance(
            agent_type=agent_type,
            capabilities=agent_config.get('capabilities', []),
            max_capacity=agent_config.get('max_capacity', 10),
            metadata=agent_config.get('metadata', {})
        )
        
        # Register instance
        self.agent_instances[instance.instance_id] = instance
        
        if agent_type not in self.agent_pools:
            self.agent_pools[agent_type] = []
        self.agent_pools[agent_type].append(instance.instance_id)
        
        # Initialize agent
        try:
            await self._initialize_agent_instance(instance)
            instance.status = AgentStatus.ACTIVE
            
            logger.info(f"Deployed agent {instance.instance_id} of type {agent_type}")
            
        except Exception as e:
            instance.status = AgentStatus.ERROR
            logger.error(f"Failed to deploy agent {instance.instance_id}: {str(e)}")
            raise
        
        return instance.instance_id
    
    async def terminate_agent(self, instance_id: str):
        """Terminate specific agent instance"""
        
        if instance_id not in self.agent_instances:
            raise ValueError(f"Agent instance {instance_id} not found")
        
        instance = self.agent_instances[instance_id]
        instance.status = AgentStatus.TERMINATING
        
        # Wait for current tasks to complete
        await self._wait_for_agent_tasks_completion(instance_id)
        
        # Remove from pools
        agent_type = instance.agent_type
        if agent_type in self.agent_pools:
            self.agent_pools[agent_type].remove(instance_id)
        
        # Cleanup
        instance.status = AgentStatus.TERMINATED
        del self.agent_instances[instance_id]
        
        logger.info(f"Terminated agent {instance_id}")
    
    async def submit_task(self, task: Dict[str, Any], 
                         preferred_agent_type: Optional[str] = None) -> str:
        """Submit task for execution"""
        
        if self.is_shutting_down:
            raise Exception("System is shutting down")
        
        task_id = str(uuid.uuid4())
        task_with_metadata = {
            'task_id': task_id,
            'submitted_at': datetime.now(),
            'preferred_agent_type': preferred_agent_type,
            'task_data': task
        }
        
        await self.task_queue.put(task_with_metadata)
        
        logger.debug(f"Submitted task {task_id}")
        return task_id
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        agent_status_counts = defaultdict(int)
        for instance in self.agent_instances.values():
            agent_status_counts[instance.status.value] += 1
        
        return {
            'system_status': self._determine_system_status(),
            'agents': {
                'total': len(self.agent_instances),
                'by_status': dict(agent_status_counts),
                'by_type': {
                    agent_type: len(instances) 
                    for agent_type, instances in self.agent_pools.items()
                }
            },
            'tasks': {
                'queued': self.task_queue.qsize(),
                'processing': sum(
                    instance.current_load 
                    for instance in self.agent_instances.values()
                )
            },
            'startup_complete': self.startup_complete,
            'shutting_down': self.is_shutting_down
        }
    
    async def _initialize_minimum_agents(self):
        """Initialize minimum required agent instances"""
        
        # Deploy minimum instances of default agent type
        for i in range(self.config.min_agent_instances):
            await self.deploy_agent(
                agent_type="default_agent",
                agent_config={'capabilities': ['general'], 'max_capacity': 5}
            )
    
    async def _initialize_agent_instance(self, instance: AgentInstance):
        """Initialize individual agent instance"""
        
        # Simulate agent initialization
        await asyncio.sleep(0.1)
        
        # Set up circuit breaker for this instance
        self.circuit_breakers[instance.instance_id] = CircuitBreaker(
            self.config.circuit_breaker_threshold,
            self.config.circuit_breaker_timeout
        )
        
        instance.last_heartbeat = datetime.now()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        
        asyncio.create_task(self._task_processor())
        asyncio.create_task(self._health_monitor())
        asyncio.create_task(self._metrics_collector())
        
        if self.auto_scaler:
            asyncio.create_task(self._auto_scaling_monitor())
    
    async def _task_processor(self):
        """Process tasks from queue"""
        
        while not self.is_shutting_down:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                # Select agent for task
                agent_instance = await self._select_agent_for_task(task)
                
                if agent_instance:
                    # Execute task on selected agent
                    asyncio.create_task(
                        self._execute_task_on_agent(task, agent_instance)
                    )
                else:
                    # No available agent - requeue task
                    await self.task_queue.put(task)
                    await asyncio.sleep(0.1)  # Brief pause before retry
                    
            except asyncio.TimeoutError:
                # No tasks in queue - continue monitoring
                continue
            except Exception as e:
                logger.error(f"Task processor error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _select_agent_for_task(self, task: Dict[str, Any]) -> Optional[AgentInstance]:
        """Select best agent for task using load balancer"""
        
        preferred_type = task.get('preferred_agent_type')
        
        if preferred_type and preferred_type in self.agent_pools:
            candidate_ids = self.agent_pools[preferred_type]
        else:
            # Use all available agents
            candidate_ids = list(self.agent_instances.keys())
        
        # Filter to available agents
        available_agents = [
            self.agent_instances[agent_id] 
            for agent_id in candidate_ids
            if agent_id in self.agent_instances and 
               self.agent_instances[agent_id].is_available()
        ]
        
        if not available_agents:
            return None
        
        # Use load balancer to select best agent
        return self.load_balancer.select_agent(available_agents, task)
    
    async def _execute_task_on_agent(self, task: Dict[str, Any], agent: AgentInstance):
        """Execute task on specific agent with fault tolerance"""
        
        task_start = datetime.now()
        agent.current_load += 1
        
        try:
            circuit_breaker = self.circuit_breakers.get(agent.instance_id)
            
            if circuit_breaker:
                # Execute with circuit breaker protection
                result = await circuit_breaker.call(
                    self._execute_task_implementation, task, agent
                )
            else:
                result = await self._execute_task_implementation(task, agent)
            
            # Task completed successfully
            task_duration = (datetime.now() - task_start).total_seconds()
            
            # Update agent performance metrics
            self._update_agent_performance_metrics(agent, task_duration, success=True)
            
            logger.debug(f"Task {task['task_id']} completed on agent {agent.instance_id}")
            
        except Exception as e:
            # Task failed
            task_duration = (datetime.now() - task_start).total_seconds()
            
            self._update_agent_performance_metrics(agent, task_duration, success=False)
            
            logger.error(f"Task {task['task_id']} failed on agent {agent.instance_id}: {str(e)}")
            
            # Try to requeue task if retries available
            await self._handle_task_failure(task, e)
            
        finally:
            agent.current_load = max(0, agent.current_load - 1)
            agent.last_heartbeat = datetime.now()
    
    async def _execute_task_implementation(self, task: Dict[str, Any], 
                                         agent: AgentInstance) -> Dict[str, Any]:
        """Actual task execution implementation"""
        
        # Simulate task execution
        task_complexity = task.get('task_data', {}).get('complexity', 'medium')
        
        if task_complexity == 'simple':
            execution_time = 0.1
        elif task_complexity == 'complex':
            execution_time = 1.0
        else:
            execution_time = 0.5
        
        await asyncio.sleep(execution_time)
        
        # Simulate occasional failures
        if task.get('task_data', {}).get('should_fail', False):
            raise Exception("Simulated task failure")
        
        return {
            'task_id': task['task_id'],
            'result': 'Task completed successfully',
            'agent_id': agent.instance_id,
            'execution_time': execution_time
        }
    
    def _update_agent_performance_metrics(self, agent: AgentInstance, 
                                        task_duration: float, success: bool):
        """Update agent performance metrics"""
        
        if 'total_tasks' not in agent.performance_metrics:
            agent.performance_metrics['total_tasks'] = 0
            agent.performance_metrics['successful_tasks'] = 0
            agent.performance_metrics['average_duration'] = 0.0
        
        agent.performance_metrics['total_tasks'] += 1
        
        if success:
            agent.performance_metrics['successful_tasks'] += 1
        
        # Update average duration (exponential moving average)
        current_avg = agent.performance_metrics['average_duration']
        alpha = 0.1  # Smoothing factor
        agent.performance_metrics['average_duration'] = (
            alpha * task_duration + (1 - alpha) * current_avg
        )
        
        # Update success rate
        total_tasks = agent.performance_metrics['total_tasks']
        successful_tasks = agent.performance_metrics['successful_tasks']
        agent.performance_metrics['success_rate'] = successful_tasks / total_tasks
        
        # Update health score based on recent performance
        success_rate = agent.performance_metrics['success_rate']
        avg_duration = agent.performance_metrics['average_duration']
        
        # Health score considers success rate and performance
        duration_factor = min(1.0, 2.0 / (avg_duration + 1.0))  # Lower duration = better
        agent.health_score = (success_rate * 0.7 + duration_factor * 0.3)
    
    async def _handle_task_failure(self, task: Dict[str, Any], error: Exception):
        """Handle task execution failure with retry logic"""
        
        retry_count = task.get('retry_count', 0)
        
        if retry_count < self.config.max_task_retries:
            # Retry task
            task['retry_count'] = retry_count + 1
            task['last_error'] = str(error)
            
            # Add delay before retry
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            
            await self.task_queue.put(task)
            logger.info(f"Retrying task {task['task_id']} (attempt {retry_count + 1})")
        else:
            logger.error(f"Task {task['task_id']} failed permanently after {retry_count} retries")
    
    async def _health_monitor(self):
        """Monitor agent health and system status"""
        
        while not self.is_shutting_down:
            try:
                current_time = datetime.now()
                unhealthy_agents = []
                
                for instance_id, instance in self.agent_instances.items():
                    # Check heartbeat timeout
                    heartbeat_age = current_time - instance.last_heartbeat
                    
                    if heartbeat_age > timedelta(minutes=2):
                        instance.status = AgentStatus.ERROR
                        instance.health_score = 0.0
                        unhealthy_agents.append(instance_id)
                    
                    # Check performance degradation
                    elif instance.health_score < 0.3:
                        instance.status = AgentStatus.ERROR
                        unhealthy_agents.append(instance_id)
                    
                    elif instance.health_score < 0.7:
                        instance.status = AgentStatus.IDLE  # Degraded performance
                
                # Handle unhealthy agents
                for agent_id in unhealthy_agents:
                    await self._handle_unhealthy_agent(agent_id)
                
                await asyncio.sleep(self.config.health_check_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"Health monitor error: {str(e)}")
                await asyncio.sleep(10)
    
    async def _handle_unhealthy_agent(self, agent_id: str):
        """Handle unhealthy agent instance"""
        
        if agent_id not in self.agent_instances:
            return
        
        instance = self.agent_instances[agent_id]
        
        logger.warning(f"Agent {agent_id} is unhealthy (health: {instance.health_score:.2f})")
        
        # Try to restart agent
        try:
            await self._restart_agent_instance(instance)
            logger.info(f"Successfully restarted agent {agent_id}")
        except Exception as e:
            logger.error(f"Failed to restart agent {agent_id}: {str(e)}")
            
            # If restart fails, terminate and replace
            await self._replace_failed_agent(instance)
    
    async def _restart_agent_instance(self, instance: AgentInstance):
        """Restart failed agent instance"""
        
        instance.status = AgentStatus.INITIALIZING
        
        # Reset performance metrics
        instance.performance_metrics = {}
        instance.health_score = 1.0
        instance.current_load = 0
        
        # Reinitialize
        await self._initialize_agent_instance(instance)
        
        instance.status = AgentStatus.ACTIVE
    
    async def _replace_failed_agent(self, failed_instance: AgentInstance):
        """Replace failed agent with new instance"""
        
        agent_type = failed_instance.agent_type
        agent_config = failed_instance.metadata.copy()
        
        try:
            # Remove failed instance
            await self.terminate_agent(failed_instance.instance_id)
            
            # Deploy replacement
            await self.deploy_agent(agent_type, agent_config)
            
            logger.info(f"Replaced failed agent {failed_instance.instance_id} with new instance")
            
        except Exception as e:
            logger.error(f"Failed to replace agent {failed_instance.instance_id}: {str(e)}")
    
    async def _auto_scaling_monitor(self):
        """Monitor system load and trigger auto-scaling"""
        
        if not self.auto_scaler:
            return
        
        while not self.is_shutting_down:
            try:
                # Collect current metrics
                metrics = await self._collect_scaling_metrics()
                
                # Check if scaling action is needed
                scaling_decision = self.auto_scaler.evaluate_scaling_need(
                    metrics, self.agent_instances
                )
                
                if scaling_decision['action'] == 'scale_up':
                    await self._scale_up_agents(scaling_decision)
                elif scaling_decision['action'] == 'scale_down':
                    await self._scale_down_agents(scaling_decision)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Auto-scaling monitor error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _collect_scaling_metrics(self) -> Dict[str, Any]:
        """Collect metrics for scaling decisions"""
        
        total_agents = len(self.agent_instances)
        active_agents = sum(
            1 for instance in self.agent_instances.values()
            if instance.status == AgentStatus.ACTIVE
        )
        
        queue_size = self.task_queue.qsize()
        
        total_capacity = sum(
            instance.max_capacity 
            for instance in self.agent_instances.values()
        )
        
        current_load = sum(
            instance.current_load 
            for instance in self.agent_instances.values()
        )
        
        utilization_rate = current_load / total_capacity if total_capacity > 0 else 0
        
        # System resource usage
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        
        return {
            'total_agents': total_agents,
            'active_agents': active_agents,
            'queue_size': queue_size,
            'utilization_rate': utilization_rate,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage
        }
    
    async def _scale_up_agents(self, scaling_decision: Dict[str, Any]):
        """Scale up agent instances"""
        
        target_count = scaling_decision.get('target_count', 1)
        agent_type = scaling_decision.get('agent_type', 'default_agent')
        
        logger.info(f"Scaling up: adding {target_count} agents of type {agent_type}")
        
        for i in range(target_count):
            if len(self.agent_instances) >= self.config.max_agent_instances:
                logger.warning("Cannot scale up: maximum agent limit reached")
                break
            
            try:
                await self.deploy_agent(
                    agent_type=agent_type,
                    agent_config={'capabilities': ['general'], 'max_capacity': 5}
                )
            except Exception as e:
                logger.error(f"Failed to scale up agent: {str(e)}")
    
    async def _scale_down_agents(self, scaling_decision: Dict[str, Any]):
        """Scale down agent instances"""
        
        target_count = scaling_decision.get('target_count', 1)
        
        logger.info(f"Scaling down: removing {target_count} agents")
        
        # Find least utilized agents to remove
        agents_by_utilization = sorted(
            self.agent_instances.values(),
            key=lambda a: a.get_utilization_rate()
        )
        
        removed_count = 0
        for agent in agents_by_utilization:
            if removed_count >= target_count:
                break
            
            if (len(self.agent_instances) <= self.config.min_agent_instances or
                agent.current_load > 0):  # Don't remove busy agents
                continue
            
            try:
                await self.terminate_agent(agent.instance_id)
                removed_count += 1
            except Exception as e:
                logger.error(f"Failed to scale down agent {agent.instance_id}: {str(e)}")
    
    async def _metrics_collector(self):
        """Collect and store system metrics"""
        
        while not self.is_shutting_down:
            try:
                metrics = SystemMetrics()
                
                # System resource metrics
                metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
                metrics.memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
                metrics.disk_usage_mb = psutil.disk_usage('/').used / (1024 * 1024)
                
                # Agent metrics
                metrics.total_agents = len(self.agent_instances)
                metrics.active_agents = sum(
                    1 for i in self.agent_instances.values() 
                    if i.status == AgentStatus.ACTIVE
                )
                metrics.idle_agents = sum(
                    1 for i in self.agent_instances.values()
                    if i.status == AgentStatus.IDLE
                )
                metrics.error_agents = sum(
                    1 for i in self.agent_instances.values()
                    if i.status == AgentStatus.ERROR
                )
                
                # Task metrics
                metrics.tasks_queued = self.task_queue.qsize()
                metrics.tasks_processing = sum(
                    i.current_load for i in self.agent_instances.values()
                )
                
                # Store metrics (in production would send to monitoring system)
                logger.debug(f"Collected metrics: CPU={metrics.cpu_usage_percent:.1f}%, "
                           f"Memory={metrics.memory_usage_mb:.0f}MB, "
                           f"Agents={metrics.active_agents}/{metrics.total_agents}")
                
                await asyncio.sleep(self.config.metrics_collection_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"Metrics collector error: {str(e)}")
                await asyncio.sleep(10)
    
    def _determine_system_status(self) -> SystemStatus:
        """Determine overall system status"""
        
        if self.is_shutting_down:
            return SystemStatus.SHUTTING_DOWN
        
        if not self.startup_complete:
            return SystemStatus.STARTING
        
        total_agents = len(self.agent_instances)
        healthy_agents = sum(
            1 for instance in self.agent_instances.values()
            if instance.is_healthy()
        )
        
        if total_agents == 0:
            return SystemStatus.DOWN
        
        health_ratio = healthy_agents / total_agents
        
        if health_ratio >= 0.8:
            return SystemStatus.HEALTHY
        elif health_ratio >= 0.5:
            return SystemStatus.DEGRADED
        else:
            return SystemStatus.CRITICAL
    
    async def _drain_task_queue(self):
        """Drain task queue during shutdown"""
        
        logger.info("Draining task queue...")
        
        # Wait for current tasks to complete
        timeout = datetime.now() + timedelta(seconds=30)
        
        while datetime.now() < timeout:
            processing_tasks = sum(
                instance.current_load 
                for instance in self.agent_instances.values()
            )
            
            if processing_tasks == 0:
                break
            
            await asyncio.sleep(1)
        
        # Cancel remaining queued tasks
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                logger.warning(f"Cancelled queued task {task.get('task_id', 'unknown')}")
            except asyncio.QueueEmpty:
                break
    
    async def _terminate_all_agents(self):
        """Terminate all agent instances"""
        
        logger.info("Terminating all agents...")
        
        termination_tasks = []
        for instance_id in list(self.agent_instances.keys()):
            task = asyncio.create_task(self.terminate_agent(instance_id))
            termination_tasks.append(task)
        
        await asyncio.gather(*termination_tasks, return_exceptions=True)
    
    async def _wait_for_agent_tasks_completion(self, instance_id: str, 
                                             timeout: timedelta = timedelta(seconds=30)):
        """Wait for agent's current tasks to complete"""
        
        if instance_id not in self.agent_instances:
            return
        
        instance = self.agent_instances[instance_id]
        deadline = datetime.now() + timeout
        
        while datetime.now() < deadline and instance.current_load > 0:
            await asyncio.sleep(0.5)


class LoadBalancer:
    """Load balancer for distributing tasks across agents"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.RESOURCE_BASED):
        self.strategy = strategy
        self.round_robin_index = 0
    
    def select_agent(self, available_agents: List[AgentInstance], 
                    task: Dict[str, Any]) -> Optional[AgentInstance]:
        """Select best agent for task based on strategy"""
        
        if not available_agents:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_agents)
        
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(available_agents)
        
        elif self.strategy == LoadBalancingStrategy.RESOURCE_BASED:
            return self._resource_based_selection(available_agents)
        
        elif self.strategy == LoadBalancingStrategy.CAPABILITY_BASED:
            return self._capability_based_selection(available_agents, task)
        
        else:
            # Default to round robin
            return self._round_robin_selection(available_agents)
    
    def _round_robin_selection(self, agents: List[AgentInstance]) -> AgentInstance:
        """Simple round-robin selection"""
        
        selected_agent = agents[self.round_robin_index % len(agents)]
        self.round_robin_index += 1
        return selected_agent
    
    def _least_connections_selection(self, agents: List[AgentInstance]) -> AgentInstance:
        """Select agent with least current load"""
        
        return min(agents, key=lambda a: a.current_load)
    
    def _resource_based_selection(self, agents: List[AgentInstance]) -> AgentInstance:
        """Select agent based on resource utilization and health"""
        
        def selection_score(agent: AgentInstance) -> float:
            utilization = agent.get_utilization_rate()
            health = agent.health_score
            
            # Lower utilization and higher health = better score
            return health * (1.0 - utilization)
        
        return max(agents, key=selection_score)
    
    def _capability_based_selection(self, agents: List[AgentInstance], 
                                  task: Dict[str, Any]) -> AgentInstance:
        """Select agent based on capability match"""
        
        required_capabilities = task.get('task_data', {}).get('required_capabilities', [])
        
        def capability_score(agent: AgentInstance) -> float:
            if not required_capabilities:
                return 1.0  # No specific requirements
            
            matching_capabilities = len(
                set(agent.capabilities) & set(required_capabilities)
            )
            
            if matching_capabilities == 0:
                return 0.0  # No match
            
            match_ratio = matching_capabilities / len(required_capabilities)
            utilization_factor = 1.0 - agent.get_utilization_rate()
            health_factor = agent.health_score
            
            return match_ratio * utilization_factor * health_factor
        
        # Filter to agents with at least some capability match
        capable_agents = [a for a in agents if capability_score(a) > 0]
        
        if capable_agents:
            return max(capable_agents, key=capability_score)
        else:
            # Fall back to resource-based selection
            return self._resource_based_selection(agents)


class AutoScaler:
    """Auto-scaling system for dynamic agent provisioning"""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.last_scaling_action: Optional[datetime] = None
        self.scaling_history: deque = deque(maxlen=50)
    
    def evaluate_scaling_need(self, metrics: Dict[str, Any], 
                            agents: Dict[str, AgentInstance]) -> Dict[str, Any]:
        """Evaluate if scaling action is needed"""
        
        # Check cooldown period
        if (self.last_scaling_action and 
            datetime.now() - self.last_scaling_action < self.config.scaling_cooldown):
            return {'action': 'none', 'reason': 'cooldown_active'}
        
        # Scale up conditions
        if self._should_scale_up(metrics, agents):
            target_count = self._calculate_scale_up_count(metrics, agents)
            return {
                'action': 'scale_up',
                'target_count': target_count,
                'agent_type': 'default_agent',
                'reason': 'high_load_detected'
            }
        
        # Scale down conditions
        elif self._should_scale_down(metrics, agents):
            target_count = self._calculate_scale_down_count(metrics, agents)
            return {
                'action': 'scale_down',
                'target_count': target_count,
                'reason': 'low_load_detected'
            }
        
        return {'action': 'none', 'reason': 'no_scaling_needed'}
    
    def _should_scale_up(self, metrics: Dict[str, Any], 
                        agents: Dict[str, AgentInstance]) -> bool:
        """Determine if scale up is needed"""
        
        # Scale up if:
        # 1. Queue is building up
        # 2. High utilization rate
        # 3. High system resource usage
        
        queue_size = metrics.get('queue_size', 0)
        utilization_rate = metrics.get('utilization_rate', 0)
        cpu_usage = metrics.get('cpu_usage', 0)
        total_agents = metrics.get('total_agents', 0)
        
        scale_up_conditions = [
            queue_size > 10,  # Queue building up
            utilization_rate > 0.8,  # High utilization
            cpu_usage > 70,  # High CPU usage
            total_agents < self.config.max_agent_instances  # Can still scale up
        ]
        
        return sum(scale_up_conditions) >= 2  # At least 2 conditions met
    
    def _should_scale_down(self, metrics: Dict[str, Any], 
                          agents: Dict[str, AgentInstance]) -> bool:
        """Determine if scale down is needed"""
        
        # Scale down if:
        # 1. Low utilization for sustained period
        # 2. Empty queue
        # 3. More agents than minimum required
        
        queue_size = metrics.get('queue_size', 0)
        utilization_rate = metrics.get('utilization_rate', 0)
        total_agents = metrics.get('total_agents', 0)
        
        scale_down_conditions = [
            queue_size == 0,  # No queued tasks
            utilization_rate < 0.3,  # Low utilization
            total_agents > self.config.min_agent_instances  # Above minimum
        ]
        
        return all(scale_down_conditions)
    
    def _calculate_scale_up_count(self, metrics: Dict[str, Any], 
                                agents: Dict[str, AgentInstance]) -> int:
        """Calculate how many agents to add"""
        
        queue_size = metrics.get('queue_size', 0)
        utilization_rate = metrics.get('utilization_rate', 0)
        
        # Base scale up count on queue size and utilization
        if queue_size > 50:
            return min(5, self.config.max_agent_instances - len(agents))
        elif queue_size > 20 or utilization_rate > 0.9:
            return min(2, self.config.max_agent_instances - len(agents))
        else:
            return 1
    
    def _calculate_scale_down_count(self, metrics: Dict[str, Any], 
                                  agents: Dict[str, AgentInstance]) -> int:
        """Calculate how many agents to remove"""
        
        utilization_rate = metrics.get('utilization_rate', 0)
        total_agents = metrics.get('total_agents', 0)
        
        # Conservative scale down
        if utilization_rate < 0.1 and total_agents > self.config.min_agent_instances + 2:
            return min(2, total_agents - self.config.min_agent_instances)
        else:
            return 1


# Demonstration and testing functions
async def demonstrate_production_deployment():
    """Demonstrate production multi-agent system capabilities"""
    
    print("🏭 Production Multi-Agent System Demonstration")
    print("=" * 55)
    
    # Create production configuration
    config = ProductionConfig(
        max_agents=10,
        min_agent_instances=2,
        max_agent_instances=8,
        enable_auto_scaling=True,
        health_check_interval=timedelta(seconds=5),
        metrics_collection_interval=timedelta(seconds=3)
    )
    
    # Initialize production system
    manager = ProductionAgentManager(config)
    
    print("🚀 Starting production system...")
    await manager.startup()
    
    # Show initial status
    status = await manager.get_system_status()
    print(f"📊 Initial Status:")
    print(f"   System: {status['system_status']}")
    print(f"   Agents: {status['agents']['total']} total")
    print(f"   Tasks: {status['tasks']['queued']} queued")
    
    # Deploy additional specialized agents
    print(f"\n🔧 Deploying specialized agents...")
    
    specialist_id = await manager.deploy_agent(
        agent_type="data_processor",
        agent_config={
            'capabilities': ['data_analysis', 'ml_processing'],
            'max_capacity': 3
        }
    )
    
    analyst_id = await manager.deploy_agent(
        agent_type="business_analyst",
        agent_config={
            'capabilities': ['reporting', 'visualization'],
            'max_capacity': 2
        }
    )
    
    print(f"✅ Deployed specialist: {specialist_id}")
    print(f"✅ Deployed analyst: {analyst_id}")
    
    # Submit various tasks to test load balancing
    print(f"\n📋 Submitting test tasks...")
    
    test_tasks = [
        {'complexity': 'simple', 'required_capabilities': ['general']},
        {'complexity': 'medium', 'required_capabilities': ['data_analysis']},
        {'complexity': 'complex', 'required_capabilities': ['ml_processing']},
        {'complexity': 'simple', 'required_capabilities': ['reporting']},
        {'complexity': 'medium'},  # No specific requirements
        {'complexity': 'simple', 'should_fail': True},  # This will fail
    ]
    
    task_ids = []
    for i, task_data in enumerate(test_tasks):
        task_id = await manager.submit_task(
            task=task_data,
            preferred_agent_type='data_processor' if 'data_analysis' in task_data.get('required_capabilities', []) else None
        )
        task_ids.append(task_id)
        print(f"   Submitted task {i+1}: {task_id}")
    
    # Wait for task processing
    print(f"\n⏳ Processing tasks...")
    await asyncio.sleep(3)
    
    # Submit more tasks to trigger scaling
    print(f"\n📈 Submitting additional tasks to trigger auto-scaling...")
    
    for i in range(15):  # Submit many tasks quickly
        await manager.submit_task(
            task={'complexity': 'medium', 'batch_id': f'batch_{i}'}
        )
    
    await asyncio.sleep(2)
    
    # Check system status after load
    status = await manager.get_system_status()
    print(f"\n📊 Status Under Load:")
    print(f"   System: {status['system_status']}")
    print(f"   Agents: {status['agents']['total']} total")
    print(f"   - Active: {status['agents']['by_status'].get('active', 0)}")
    print(f"   - Idle: {status['agents']['by_status'].get('idle', 0)}")
    print(f"   - Error: {status['agents']['by_status'].get('error', 0)}")
    print(f"   Tasks: {status['tasks']['queued']} queued, {status['tasks']['processing']} processing")
    
    # Show agent details
    print(f"\n👥 Agent Instance Details:")
    for instance_id, instance in list(manager.agent_instances.items())[:5]:  # Show first 5
        print(f"   {instance_id[:8]}... ({instance.agent_type}):")
        print(f"      Status: {instance.status.value}")
        print(f"      Load: {instance.current_load}/{instance.max_capacity}")
        print(f"      Health: {instance.health_score:.2f}")
        print(f"      Utilization: {instance.get_utilization_rate():.1%}")
    
    # Wait for processing and scaling
    await asyncio.sleep(5)
    
    # Final status check
    final_status = await manager.get_system_status()
    print(f"\n📊 Final Status:")
    print(f"   System: {final_status['system_status']}")
    print(f"   Agents: {final_status['agents']['total']} total")
    print(f"   Tasks: {final_status['tasks']['queued']} queued, {final_status['tasks']['processing']} processing")
    
    # Test graceful shutdown
    print(f"\n🔄 Testing graceful shutdown...")
    await manager.shutdown()
    
    print(f"✅ Production system demonstration completed")
    
    return {
        'manager': manager,
        'final_status': final_status,
        'specialist_id': specialist_id,
        'analyst_id': analyst_id
    }


if __name__ == "__main__":
    asyncio.run(demonstrate_production_deployment())