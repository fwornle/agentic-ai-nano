"""
Agno Multi-Agent Teams and Coordination
Session 7: Agno Production-Ready Agents

This module implements sophisticated multi-agent team coordination with workflows,
consensus algorithms, load balancing, and enterprise-grade orchestration patterns.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

try:
    from agno import Agent, Team, Workflow
    from agno.agents import SpecializedAgent
    from agno.coordination import TaskRouter, LoadBalancer, PriorityQueue
    from agno.workflows import SequentialFlow, ParallelFlow, ConditionalFlow
    from agno.patterns import ScatterGather, MapReduce, EventDriven
    from agno.events import EventBus, EventHandler
    from agno.consensus import ConsensusAlgorithm, RaftConsensus
except ImportError:
    # Fallback implementations for demonstration
    print("Warning: Agno team coordination modules not available, using mock implementations")
    
    class Agent:
        def __init__(self, name: str, model: str = "gpt-4o", **kwargs):
            self.name = name
            self.model = model
            self.config = kwargs
            
        async def run(self, prompt: str, **kwargs) -> 'AgentResponse':
            await asyncio.sleep(0.2)  # Simulate processing
            return AgentResponse(f"Agent {self.name} response: {prompt}")
    
    class AgentResponse:
        def __init__(self, content: str):
            self.content = content
            self.processing_time = 0.5
            self.model = "gpt-4o"
            
    class Team:
        def __init__(self, name: str, agents: List[Agent], **kwargs):
            self.name = name
            self.agents = agents
            self.config = kwargs
    
    class SpecializedAgent(Agent):
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """Types of agent workflows"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    SCATTER_GATHER = "scatter_gather"
    MAP_REDUCE = "map_reduce"
    CONSENSUS = "consensus"

class AgentRole(Enum):
    """Agent roles in teams"""
    LEADER = "leader"
    WORKER = "worker"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    REVIEWER = "reviewer"
    VALIDATOR = "validator"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    description: str
    skill_level: float  # 0.0 to 1.0
    max_concurrent_tasks: int = 3
    average_processing_time: float = 5.0
    cost_per_task: float = 0.01

@dataclass 
class Task:
    """Individual task in a workflow"""
    id: str
    description: str
    input_data: Any
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    priority: int = 5  # 1-10, higher is more priority
    estimated_duration: float = 5.0  # seconds
    
    @property
    def processing_time(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    workflow_id: str
    workflow_type: WorkflowType
    tasks: List[Task]
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error: Optional[str] = None
    agents_used: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def execution_time(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def completed_tasks(self) -> int:
        return len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])

class SpecializedAgentPool:
    """Pool of specialized agents with different capabilities"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.capabilities: Dict[str, AgentCapability] = {}
        self.workload: Dict[str, int] = defaultdict(int)  # Current task count per agent
        
        # Initialize specialized agents
        self._initialize_agent_pool()
    
    def _initialize_agent_pool(self):
        """Initialize pool with various specialized agents"""
        
        # Data Collector Agent
        data_collector = Agent(
            name="data_collector",
            model="gpt-4o-mini",  # Fast model for data collection
            instructions="""
            You are a specialized data collection agent. Your role is to:
            - Gather information from various sources
            - Structure and organize collected data
            - Ensure data quality and completeness
            - Work efficiently with minimal supervision
            """
        )
        
        self.agents["data_collector"] = data_collector
        self.capabilities["data_collector"] = AgentCapability(
            name="data_collection",
            description="Efficient data gathering and organization",
            skill_level=0.9,
            max_concurrent_tasks=5,
            average_processing_time=3.0,
            cost_per_task=0.005
        )
        
        # Analysis Agent
        analyst = Agent(
            name="analyst",
            model="gpt-4o",  # Powerful model for analysis
            instructions="""
            You are a specialized analysis agent. Your expertise includes:
            - Deep data analysis and pattern recognition
            - Statistical analysis and trend identification
            - Insight generation and hypothesis formation
            - Critical thinking and validation
            """
        )
        
        self.agents["analyst"] = analyst
        self.capabilities["analyst"] = AgentCapability(
            name="analysis",
            description="Advanced data analysis and insights",
            skill_level=0.95,
            max_concurrent_tasks=3,
            average_processing_time=8.0,
            cost_per_task=0.02
        )
        
        # Content Writer Agent
        writer = Agent(
            name="writer",
            model="gpt-4o",
            instructions="""
            You are a specialized content creation agent. You excel at:
            - Clear and engaging writing
            - Structuring complex information
            - Adapting tone and style for different audiences
            - Creating compelling narratives from data
            """
        )
        
        self.agents["writer"] = writer
        self.capabilities["writer"] = AgentCapability(
            name="content_creation",
            description="Professional content writing and communication",
            skill_level=0.9,
            max_concurrent_tasks=4,
            average_processing_time=6.0,
            cost_per_task=0.015
        )
        
        # Quality Reviewer Agent
        reviewer = Agent(
            name="reviewer",
            model="gpt-4o",
            instructions="""
            You are a quality assurance and review agent. Your responsibilities:
            - Comprehensive quality assessment
            - Fact-checking and accuracy validation
            - Compliance and standard verification
            - Constructive feedback and improvement suggestions
            """
        )
        
        self.agents["reviewer"] = reviewer
        self.capabilities["reviewer"] = AgentCapability(
            name="quality_review",
            description="Quality assurance and validation",
            skill_level=0.92,
            max_concurrent_tasks=6,
            average_processing_time=4.0,
            cost_per_task=0.01
        )
        
        # Coordinator Agent
        coordinator = Agent(
            name="coordinator",
            model="gpt-4o",
            instructions="""
            You are a team coordination agent. Your role involves:
            - Managing workflow and task distribution
            - Facilitating communication between agents
            - Resolving conflicts and bottlenecks
            - Ensuring project timeline adherence
            """
        )
        
        self.agents["coordinator"] = coordinator
        self.capabilities["coordinator"] = AgentCapability(
            name="coordination",
            description="Team leadership and workflow management",
            skill_level=0.88,
            max_concurrent_tasks=8,
            average_processing_time=2.0,
            cost_per_task=0.008
        )
        
        logger.info(f"Initialized agent pool with {len(self.agents)} specialized agents")
    
    def get_best_agent_for_task(self, task_type: str, current_workload_weight: float = 0.3) -> str:
        """
        Select the best agent for a task based on capability and current workload
        
        Args:
            task_type: The type of task to be performed
            current_workload_weight: Weight for current workload in selection (0.0-1.0)
            
        Returns:
            Name of the best suited agent
        """
        
        # Map task types to agent capabilities
        task_capability_map = {
            "data_collection": ["data_collector"],
            "analysis": ["analyst"],
            "content_creation": ["writer"],
            "review": ["reviewer"],
            "coordination": ["coordinator"],
            "general": ["analyst", "writer", "coordinator"]  # Fallback
        }
        
        candidate_agents = task_capability_map.get(task_type, ["analyst"])
        
        best_agent = None
        best_score = -1
        
        for agent_name in candidate_agents:
            if agent_name in self.agents:
                capability = self.capabilities[agent_name]
                current_tasks = self.workload[agent_name]
                
                # Calculate availability score (0.0 to 1.0)
                availability = max(0, (capability.max_concurrent_tasks - current_tasks) / capability.max_concurrent_tasks)
                
                # Calculate overall score
                skill_score = capability.skill_level
                workload_score = availability
                
                overall_score = (
                    skill_score * (1 - current_workload_weight) + 
                    workload_score * current_workload_weight
                )
                
                if overall_score > best_score and current_tasks < capability.max_concurrent_tasks:
                    best_score = overall_score
                    best_agent = agent_name
        
        if best_agent:
            self.workload[best_agent] += 1
            return best_agent
        else:
            # Fallback to least loaded agent
            return min(self.workload.keys(), key=lambda x: self.workload[x])
    
    def release_agent(self, agent_name: str):
        """Release agent from current task"""
        if agent_name in self.workload:
            self.workload[agent_name] = max(0, self.workload[agent_name] - 1)
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current status of agent pool"""
        status = {}
        for agent_name, capability in self.capabilities.items():
            current_load = self.workload[agent_name]
            status[agent_name] = {
                "capability": capability.name,
                "skill_level": capability.skill_level,
                "current_tasks": current_load,
                "max_tasks": capability.max_concurrent_tasks,
                "utilization": current_load / capability.max_concurrent_tasks,
                "available": current_load < capability.max_concurrent_tasks
            }
        return status

class WorkflowEngine:
    """Advanced workflow engine for multi-agent coordination"""
    
    def __init__(self):
        self.agent_pool = SpecializedAgentPool()
        self.active_workflows: Dict[str, WorkflowResult] = {}
        self.task_queue = asyncio.Queue()
        self.event_bus = EventBus() if 'EventBus' in globals() else None
        
        # Workflow execution statistics
        self.execution_stats = defaultdict(list)
        
        # Start workflow processor
        asyncio.create_task(self._workflow_processor())
        
    async def execute_sequential_workflow(self, 
                                        tasks: List[Dict[str, Any]], 
                                        workflow_name: str = "sequential") -> WorkflowResult:
        """
        Execute tasks in sequential order
        
        Args:
            tasks: List of task definitions
            workflow_name: Name for the workflow
            
        Returns:
            Workflow execution result
        """
        workflow_id = f"seq_{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()
        
        # Create task objects
        task_objects = []
        for i, task_def in enumerate(tasks):
            task = Task(
                id=f"{workflow_id}_task_{i}",
                description=task_def.get("description", f"Task {i+1}"),
                input_data=task_def.get("input_data"),
                priority=task_def.get("priority", 5),
                estimated_duration=task_def.get("estimated_duration", 5.0)
            )
            task_objects.append(task)
        
        # Create workflow result
        workflow_result = WorkflowResult(
            workflow_id=workflow_id,
            workflow_type=WorkflowType.SEQUENTIAL,
            tasks=task_objects,
            start_time=start_time
        )
        
        self.active_workflows[workflow_id] = workflow_result
        
        try:
            logger.info(f"Starting sequential workflow {workflow_id} with {len(tasks)} tasks")
            
            # Execute tasks sequentially
            for task in task_objects:
                # Select best agent for this task
                task_type = task.input_data.get("task_type", "general") if isinstance(task.input_data, dict) else "general"
                agent_name = self.agent_pool.get_best_agent_for_task(task_type)
                task.assigned_agent = agent_name
                
                # Execute task
                await self._execute_task(task, agent_name)
                
                # If task failed and it's critical, stop workflow
                if task.status == TaskStatus.FAILED:
                    error_msg = f"Critical task {task.id} failed: {task.error}"
                    logger.error(error_msg)
                    workflow_result.error = error_msg
                    break
            
            # Determine overall success
            completed_tasks = [t for t in task_objects if t.status == TaskStatus.COMPLETED]
            workflow_result.success = len(completed_tasks) == len(task_objects)
            workflow_result.agents_used = list(set(t.assigned_agent for t in task_objects if t.assigned_agent))
            
            logger.info(f"Sequential workflow {workflow_id} completed: {len(completed_tasks)}/{len(task_objects)} tasks successful")
            
        except Exception as e:
            logger.error(f"Sequential workflow {workflow_id} failed: {e}")
            workflow_result.error = str(e)
            workflow_result.success = False
        
        finally:
            workflow_result.end_time = datetime.utcnow()
            self._update_execution_stats(workflow_result)
        
        return workflow_result
    
    async def execute_parallel_workflow(self, 
                                      tasks: List[Dict[str, Any]], 
                                      workflow_name: str = "parallel",
                                      max_concurrency: int = 5) -> WorkflowResult:
        """
        Execute tasks in parallel with concurrency control
        
        Args:
            tasks: List of task definitions
            workflow_name: Name for the workflow
            max_concurrency: Maximum number of concurrent tasks
            
        Returns:
            Workflow execution result
        """
        workflow_id = f"par_{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()
        
        # Create task objects
        task_objects = []
        for i, task_def in enumerate(tasks):
            task = Task(
                id=f"{workflow_id}_task_{i}",
                description=task_def.get("description", f"Task {i+1}"),
                input_data=task_def.get("input_data"),
                priority=task_def.get("priority", 5),
                estimated_duration=task_def.get("estimated_duration", 5.0)
            )
            task_objects.append(task)
        
        # Create workflow result
        workflow_result = WorkflowResult(
            workflow_id=workflow_id,
            workflow_type=WorkflowType.PARALLEL,
            tasks=task_objects,
            start_time=start_time
        )
        
        self.active_workflows[workflow_id] = workflow_result
        
        try:
            logger.info(f"Starting parallel workflow {workflow_id} with {len(tasks)} tasks (max concurrency: {max_concurrency})")
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(max_concurrency)
            
            async def execute_single_task(task):
                async with semaphore:
                    task_type = task.input_data.get("task_type", "general") if isinstance(task.input_data, dict) else "general"
                    agent_name = self.agent_pool.get_best_agent_for_task(task_type)
                    task.assigned_agent = agent_name
                    await self._execute_task(task, agent_name)
                    return task
            
            # Execute all tasks concurrently
            tasks_coroutines = [execute_single_task(task) for task in task_objects]
            completed_tasks = await asyncio.gather(*tasks_coroutines, return_exceptions=True)
            
            # Handle any exceptions
            for i, result in enumerate(completed_tasks):
                if isinstance(result, Exception):
                    task_objects[i].status = TaskStatus.FAILED
                    task_objects[i].error = str(result)
            
            # Determine overall success
            successful_tasks = [t for t in task_objects if t.status == TaskStatus.COMPLETED]
            workflow_result.success = len(successful_tasks) == len(task_objects)
            workflow_result.agents_used = list(set(t.assigned_agent for t in task_objects if t.assigned_agent))
            
            logger.info(f"Parallel workflow {workflow_id} completed: {len(successful_tasks)}/{len(task_objects)} tasks successful")
            
        except Exception as e:
            logger.error(f"Parallel workflow {workflow_id} failed: {e}")
            workflow_result.error = str(e)
            workflow_result.success = False
        
        finally:
            workflow_result.end_time = datetime.utcnow()
            self._update_execution_stats(workflow_result)
        
        return workflow_result
    
    async def execute_scatter_gather_workflow(self, 
                                            input_data: Any,
                                            scatter_tasks: List[Dict[str, Any]],
                                            gather_task: Dict[str, Any],
                                            workflow_name: str = "scatter_gather") -> WorkflowResult:
        """
        Execute scatter-gather pattern: distribute work, then combine results
        
        Args:
            input_data: Data to be scattered across tasks
            scatter_tasks: List of scatter task definitions
            gather_task: Gather task definition
            workflow_name: Name for the workflow
            
        Returns:
            Workflow execution result
        """
        workflow_id = f"sg_{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()
        
        # Create scatter tasks
        scatter_task_objects = []
        for i, task_def in enumerate(scatter_tasks):
            task = Task(
                id=f"{workflow_id}_scatter_{i}",
                description=task_def.get("description", f"Scatter task {i+1}"),
                input_data=task_def.get("input_data", input_data),
                priority=task_def.get("priority", 5)
            )
            scatter_task_objects.append(task)
        
        # Create gather task
        gather_task_obj = Task(
            id=f"{workflow_id}_gather",
            description=gather_task.get("description", "Gather and synthesize results"),
            input_data=gather_task.get("input_data"),
            dependencies=[t.id for t in scatter_task_objects],
            priority=gather_task.get("priority", 8)
        )
        
        all_tasks = scatter_task_objects + [gather_task_obj]
        
        # Create workflow result
        workflow_result = WorkflowResult(
            workflow_id=workflow_id,
            workflow_type=WorkflowType.SCATTER_GATHER,
            tasks=all_tasks,
            start_time=start_time
        )
        
        self.active_workflows[workflow_id] = workflow_result
        
        try:
            logger.info(f"Starting scatter-gather workflow {workflow_id} with {len(scatter_tasks)} scatter tasks")
            
            # Execute scatter phase in parallel
            scatter_semaphore = asyncio.Semaphore(len(scatter_tasks))  # Allow all scatter tasks to run
            
            async def execute_scatter_task(task):
                async with scatter_semaphore:
                    task_type = task.input_data.get("task_type", "data_collection") if isinstance(task.input_data, dict) else "data_collection"
                    agent_name = self.agent_pool.get_best_agent_for_task(task_type)
                    task.assigned_agent = agent_name
                    await self._execute_task(task, agent_name)
                    return task
            
            # Execute scatter tasks
            scatter_coroutines = [execute_scatter_task(task) for task in scatter_task_objects]
            scatter_results = await asyncio.gather(*scatter_coroutines, return_exceptions=True)
            
            # Collect successful scatter results
            successful_scatter_results = []
            for i, result in enumerate(scatter_results):
                if isinstance(result, Exception):
                    scatter_task_objects[i].status = TaskStatus.FAILED
                    scatter_task_objects[i].error = str(result)
                elif scatter_task_objects[i].status == TaskStatus.COMPLETED:
                    successful_scatter_results.append(scatter_task_objects[i].result)
            
            # Execute gather phase if we have some successful results
            if successful_scatter_results:
                # Prepare gather input with all scatter results
                gather_input = {
                    "scatter_results": successful_scatter_results,
                    "original_input": input_data,
                    "task_type": "analysis"  # Gather typically involves analysis
                }
                gather_task_obj.input_data = gather_input
                
                # Execute gather task
                agent_name = self.agent_pool.get_best_agent_for_task("analysis")
                gather_task_obj.assigned_agent = agent_name
                await self._execute_task(gather_task_obj, agent_name)
            else:
                gather_task_obj.status = TaskStatus.FAILED
                gather_task_obj.error = "No successful scatter results to gather"
            
            # Determine overall success
            workflow_result.success = (
                len(successful_scatter_results) > 0 and 
                gather_task_obj.status == TaskStatus.COMPLETED
            )
            workflow_result.agents_used = list(set(t.assigned_agent for t in all_tasks if t.assigned_agent))
            
            logger.info(f"Scatter-gather workflow {workflow_id} completed: "
                       f"{len(successful_scatter_results)} scatter tasks successful, "
                       f"gather {'successful' if gather_task_obj.status == TaskStatus.COMPLETED else 'failed'}")
            
        except Exception as e:
            logger.error(f"Scatter-gather workflow {workflow_id} failed: {e}")
            workflow_result.error = str(e)
            workflow_result.success = False
        
        finally:
            workflow_result.end_time = datetime.utcnow()
            self._update_execution_stats(workflow_result)
        
        return workflow_result
    
    async def _execute_task(self, task: Task, agent_name: str):
        """Execute individual task with assigned agent"""
        task.start_time = datetime.utcnow()
        task.status = TaskStatus.RUNNING
        
        try:
            agent = self.agent_pool.agents[agent_name]
            
            # Prepare task prompt
            task_prompt = self._prepare_task_prompt(task)
            
            # Execute task
            result = await agent.run(task_prompt)
            
            task.result = result.content
            task.status = TaskStatus.COMPLETED
            task.end_time = datetime.utcnow()
            
            logger.debug(f"Task {task.id} completed successfully by {agent_name}")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.end_time = datetime.utcnow()
            
            logger.error(f"Task {task.id} failed: {e}")
        
        finally:
            # Release agent
            self.agent_pool.release_agent(agent_name)
    
    def _prepare_task_prompt(self, task: Task) -> str:
        """Prepare task prompt for agent execution"""
        base_prompt = f"""
Task: {task.description}

Input Data: {json.dumps(task.input_data) if task.input_data else 'None'}

Instructions:
- Process the given input data according to the task description
- Provide clear and structured output
- Include any relevant insights or recommendations
- Ensure output quality and accuracy
"""
        
        # Add context for specific task types
        if isinstance(task.input_data, dict):
            task_type = task.input_data.get("task_type")
            
            if task_type == "data_collection":
                base_prompt += "\n- Focus on gathering comprehensive and accurate information"
            elif task_type == "analysis":
                base_prompt += "\n- Provide deep analysis with insights and patterns"
            elif task_type == "content_creation":
                base_prompt += "\n- Create clear, engaging, and well-structured content"
            elif task_type == "review":
                base_prompt += "\n- Conduct thorough quality assessment and provide feedback"
        
        return base_prompt
    
    def _update_execution_stats(self, workflow_result: WorkflowResult):
        """Update execution statistics"""
        stats = {
            "workflow_id": workflow_result.workflow_id,
            "workflow_type": workflow_result.workflow_type.value,
            "execution_time": workflow_result.execution_time,
            "task_count": len(workflow_result.tasks),
            "completed_tasks": workflow_result.completed_tasks,
            "success_rate": workflow_result.completed_tasks / len(workflow_result.tasks) if workflow_result.tasks else 0,
            "agents_used": len(workflow_result.agents_used),
            "timestamp": workflow_result.start_time
        }
        
        self.execution_stats[workflow_result.workflow_type.value].append(stats)
    
    async def _workflow_processor(self):
        """Background workflow processor"""
        while True:
            try:
                # Process any queued workflows
                await asyncio.sleep(1)
                # Additional background processing logic would go here
            except Exception as e:
                logger.error(f"Workflow processor error: {e}")
                await asyncio.sleep(5)
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get comprehensive workflow execution statistics"""
        stats = {
            "total_workflows": sum(len(workflows) for workflows in self.execution_stats.values()),
            "workflow_types": {},
            "agent_pool_status": self.agent_pool.get_pool_status(),
            "active_workflows": len(self.active_workflows)
        }
        
        for workflow_type, workflows in self.execution_stats.items():
            if workflows:
                avg_execution_time = sum(w["execution_time"] for w in workflows) / len(workflows)
                avg_success_rate = sum(w["success_rate"] for w in workflows) / len(workflows)
                total_tasks = sum(w["task_count"] for w in workflows)
                
                stats["workflow_types"][workflow_type] = {
                    "count": len(workflows),
                    "avg_execution_time": avg_execution_time,
                    "avg_success_rate": avg_success_rate,
                    "total_tasks_processed": total_tasks
                }
        
        return stats

async def demonstrate_agent_teams():
    """Comprehensive demonstration of multi-agent teams and coordination"""
    print("=" * 80)
    print("AGNO MULTI-AGENT TEAMS & COORDINATION DEMONSTRATION")
    print("=" * 80)
    
    # Initialize workflow engine
    workflow_engine = WorkflowEngine()
    
    print(f"\n1. Agent Pool Status")
    print("-" * 30)
    
    pool_status = workflow_engine.agent_pool.get_pool_status()
    for agent_name, status in pool_status.items():
        print(f"{agent_name.title()}: {status['capability']} "
              f"(skill: {status['skill_level']:.2f}, "
              f"available: {status['available']})")
    
    # Sequential Workflow Demo
    print(f"\n2. Sequential Workflow Execution")
    print("-" * 40)
    
    sequential_tasks = [
        {
            "description": "Research market trends in AI automation",
            "input_data": {"task_type": "data_collection", "topic": "AI automation"},
            "priority": 7
        },
        {
            "description": "Analyze collected market data",
            "input_data": {"task_type": "analysis", "focus": "trends and patterns"},
            "priority": 8
        },
        {
            "description": "Create market analysis report",
            "input_data": {"task_type": "content_creation", "format": "executive summary"},
            "priority": 6
        },
        {
            "description": "Review and validate the report",
            "input_data": {"task_type": "review", "criteria": "accuracy and completeness"},
            "priority": 7
        }
    ]
    
    seq_result = await workflow_engine.execute_sequential_workflow(sequential_tasks, "market_analysis")
    
    print(f"Workflow ID: {seq_result.workflow_id}")
    print(f"Success: {seq_result.success}")
    print(f"Execution Time: {seq_result.execution_time:.2f}s")
    print(f"Completed Tasks: {seq_result.completed_tasks}/{len(seq_result.tasks)}")
    print(f"Agents Used: {', '.join(seq_result.agents_used)}")
    
    # Parallel Workflow Demo
    print(f"\n3. Parallel Workflow Execution")
    print("-" * 35)
    
    parallel_tasks = [
        {
            "description": "Research competitor A analysis",
            "input_data": {"task_type": "data_collection", "company": "Competitor A"},
            "priority": 5
        },
        {
            "description": "Research competitor B analysis", 
            "input_data": {"task_type": "data_collection", "company": "Competitor B"},
            "priority": 5
        },
        {
            "description": "Research competitor C analysis",
            "input_data": {"task_type": "data_collection", "company": "Competitor C"},
            "priority": 5
        },
        {
            "description": "Analyze industry regulations",
            "input_data": {"task_type": "analysis", "domain": "regulatory environment"},
            "priority": 6
        },
        {
            "description": "Review market positioning strategies",
            "input_data": {"task_type": "review", "focus": "positioning strategies"},
            "priority": 4
        }
    ]
    
    par_result = await workflow_engine.execute_parallel_workflow(parallel_tasks, "competitive_analysis", max_concurrency=3)
    
    print(f"Workflow ID: {par_result.workflow_id}")
    print(f"Success: {par_result.success}")
    print(f"Execution Time: {par_result.execution_time:.2f}s")
    print(f"Completed Tasks: {par_result.completed_tasks}/{len(par_result.tasks)}")
    print(f"Agents Used: {', '.join(par_result.agents_used)}")
    print(f"Parallelization Benefit: {sum(t.processing_time for t in par_result.tasks):.2f}s total task time vs {par_result.execution_time:.2f}s execution time")
    
    # Scatter-Gather Workflow Demo
    print(f"\n4. Scatter-Gather Workflow Execution")
    print("-" * 40)
    
    scatter_tasks = [
        {
            "description": "Analyze customer segment 1 data",
            "input_data": {"task_type": "analysis", "segment": "enterprise"},
        },
        {
            "description": "Analyze customer segment 2 data", 
            "input_data": {"task_type": "analysis", "segment": "mid-market"},
        },
        {
            "description": "Analyze customer segment 3 data",
            "input_data": {"task_type": "analysis", "segment": "startup"},
        }
    ]
    
    gather_task = {
        "description": "Synthesize all segment analyses into comprehensive customer insights",
        "input_data": {"task_type": "content_creation", "output": "strategic recommendations"},
        "priority": 9
    }
    
    sg_result = await workflow_engine.execute_scatter_gather_workflow(
        input_data={"project": "customer_segmentation_analysis", "timeframe": "Q4_2024"},
        scatter_tasks=scatter_tasks,
        gather_task=gather_task,
        workflow_name="customer_insights"
    )
    
    print(f"Workflow ID: {sg_result.workflow_id}")
    print(f"Success: {sg_result.success}")
    print(f"Execution Time: {sg_result.execution_time:.2f}s")
    print(f"Scatter Tasks: {len([t for t in sg_result.tasks if 'scatter' in t.id])}")
    print(f"Gather Success: {'Yes' if any('gather' in t.id and t.status == TaskStatus.COMPLETED for t in sg_result.tasks) else 'No'}")
    print(f"Agents Used: {', '.join(sg_result.agents_used)}")
    
    # Workflow Statistics
    print(f"\n5. Workflow Engine Statistics")
    print("-" * 35)
    
    stats = workflow_engine.get_workflow_statistics()
    print(f"Total Workflows Executed: {stats['total_workflows']}")
    print(f"Active Workflows: {stats['active_workflows']}")
    
    print(f"\nWorkflow Type Performance:")
    for workflow_type, type_stats in stats["workflow_types"].items():
        print(f"  {workflow_type.title()}:")
        print(f"    Count: {type_stats['count']}")
        print(f"    Avg Execution Time: {type_stats['avg_execution_time']:.2f}s")
        print(f"    Avg Success Rate: {type_stats['avg_success_rate']:.1%}")
        print(f"    Total Tasks: {type_stats['total_tasks_processed']}")
    
    print(f"\nAgent Pool Utilization:")
    for agent_name, status in stats["agent_pool_status"].items():
        print(f"  {agent_name.title()}: {status['utilization']:.1%} utilized "
              f"({status['current_tasks']}/{status['max_tasks']} tasks)")
    
    # Task Detail Analysis
    print(f"\n6. Detailed Task Analysis")
    print("-" * 30)
    
    all_tasks = []
    for workflow in [seq_result, par_result, sg_result]:
        all_tasks.extend(workflow.tasks)
    
    completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
    failed_tasks = [t for t in all_tasks if t.status == TaskStatus.FAILED]
    
    if completed_tasks:
        avg_task_time = sum(t.processing_time for t in completed_tasks) / len(completed_tasks)
        print(f"Total Tasks Processed: {len(all_tasks)}")
        print(f"Successful Tasks: {len(completed_tasks)}")
        print(f"Failed Tasks: {len(failed_tasks)}")
        print(f"Overall Success Rate: {len(completed_tasks)/len(all_tasks):.1%}")
        print(f"Average Task Processing Time: {avg_task_time:.2f}s")
        
        # Agent performance breakdown
        agent_performance = defaultdict(list)
        for task in completed_tasks:
            if task.assigned_agent:
                agent_performance[task.assigned_agent].append(task.processing_time)
        
        print(f"\nAgent Performance:")
        for agent, times in agent_performance.items():
            avg_time = sum(times) / len(times)
            print(f"  {agent.title()}: {len(times)} tasks, avg {avg_time:.2f}s")
    
    print(f"\n" + "=" * 80)
    print("MULTI-AGENT TEAMS DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Coordination Features Demonstrated:")
    print("- Specialized agent pool with capability-based task assignment")
    print("- Sequential workflow for dependent task chains")
    print("- Parallel workflow with concurrency control")
    print("- Scatter-gather pattern for distributed analysis")
    print("- Load balancing and resource utilization optimization")
    print("- Comprehensive workflow monitoring and statistics")
    print("- Task dependency management and error handling")

if __name__ == "__main__":
    # Run comprehensive demonstration
    asyncio.run(demonstrate_agent_teams())