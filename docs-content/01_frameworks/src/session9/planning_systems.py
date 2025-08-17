"""
Advanced Planning Systems for Multi-Agent Coordination
Session 8: Hierarchical Task Networks and Dynamic Replanning

This module implements sophisticated planning algorithms including HTN planning,
dynamic replanning systems, and adaptive planning strategies for complex
multi-agent problem solving scenarios.
"""

from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
import uuid
import copy
import heapq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks in hierarchical planning"""
    PRIMITIVE = "primitive"      # Directly executable
    COMPOUND = "compound"        # Requires decomposition
    ABSTRACT = "abstract"        # High-level goal
    CONDITIONAL = "conditional"  # Depends on conditions
    PARALLEL = "parallel"        # Can be executed in parallel
    SEQUENTIAL = "sequential"    # Must be executed in order


class PlanningState(Enum):
    """States of planning process"""
    INITIAL = "initial"
    PLANNING = "planning"
    EXECUTING = "executing"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TaskStatus(Enum):
    """Status of individual tasks"""
    PENDING = "pending"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class Condition:
    """Represents a condition for task execution"""
    condition_id: str
    name: str
    condition_type: str  # precondition, effect, invariant
    expression: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, state: Dict[str, Any]) -> bool:
        """Evaluate condition against current state"""
        # Simplified evaluation - in production would use proper logic engine
        try:
            # Basic string matching for demonstration
            if self.condition_type == "has_resource":
                resource = self.parameters.get('resource')
                return state.get('resources', {}).get(resource, 0) > 0
            elif self.condition_type == "agent_available":
                agent_id = self.parameters.get('agent_id')
                return state.get('agents', {}).get(agent_id, {}).get('status') == 'available'
            elif self.condition_type == "time_constraint":
                deadline = self.parameters.get('deadline')
                current_time = state.get('current_time', datetime.now())
                return current_time < deadline if deadline else True
            else:
                # Default to true for unknown conditions
                return True
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {str(e)}")
            return False


@dataclass
class Task:
    """Represents a task in the HTN hierarchy"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    task_type: TaskType = TaskType.PRIMITIVE
    parameters: Dict[str, Any] = field(default_factory=dict)
    preconditions: List[Condition] = field(default_factory=list)
    effects: List[Condition] = field(default_factory=list)
    estimated_duration: Optional[timedelta] = None
    actual_duration: Optional[timedelta] = None
    priority: int = 1
    cost: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    parent_task: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    decompositions: List['TaskDecomposition'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def can_execute(self, state: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if task can be executed in current state"""
        failed_conditions = []
        
        for condition in self.preconditions:
            if not condition.evaluate(state):
                failed_conditions.append(condition.name)
        
        # Check dependencies
        for dep_task_id in self.dependencies:
            dep_status = state.get('task_status', {}).get(dep_task_id)
            if dep_status != TaskStatus.COMPLETED.value:
                failed_conditions.append(f"Dependency {dep_task_id} not completed")
        
        return len(failed_conditions) == 0, failed_conditions
    
    def apply_effects(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply task effects to state"""
        new_state = copy.deepcopy(state)
        
        for effect in self.effects:
            if effect.condition_type == "add_resource":
                resource = effect.parameters.get('resource')
                amount = effect.parameters.get('amount', 1)
                if 'resources' not in new_state:
                    new_state['resources'] = {}
                new_state['resources'][resource] = new_state['resources'].get(resource, 0) + amount
            elif effect.condition_type == "remove_resource":
                resource = effect.parameters.get('resource')
                amount = effect.parameters.get('amount', 1)
                if 'resources' in new_state:
                    new_state['resources'][resource] = max(0, new_state['resources'].get(resource, 0) - amount)
            elif effect.condition_type == "set_variable":
                var_name = effect.parameters.get('variable')
                var_value = effect.parameters.get('value')
                new_state[var_name] = var_value
        
        return new_state
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'task_type': self.task_type.value,
            'parameters': self.parameters,
            'status': self.status.value,
            'priority': self.priority,
            'cost': self.cost,
            'estimated_duration': self.estimated_duration.total_seconds() if self.estimated_duration else None,
            'assigned_agent': self.assigned_agent,
            'subtasks': self.subtasks,
            'dependencies': self.dependencies,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class TaskDecomposition:
    """Represents a way to decompose a compound task"""
    decomposition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    subtasks: List[Task] = field(default_factory=list)
    ordering_constraints: List[Tuple[str, str]] = field(default_factory=list)  # (predecessor, successor)
    conditions: List[Condition] = field(default_factory=list)
    success_probability: float = 1.0
    estimated_cost: float = 0.0
    parallel_execution: bool = False
    
    def is_applicable(self, state: Dict[str, Any]) -> bool:
        """Check if decomposition is applicable in current state"""
        return all(condition.evaluate(state) for condition in self.conditions)
    
    def get_execution_order(self) -> List[List[str]]:
        """Get execution order considering constraints and parallelization"""
        if self.parallel_execution and not self.ordering_constraints:
            # All tasks can run in parallel
            return [[task.task_id for task in self.subtasks]]
        
        # Topological sort for sequential execution
        in_degree = {task.task_id: 0 for task in self.subtasks}
        adj_list = {task.task_id: [] for task in self.subtasks}
        
        for pred, succ in self.ordering_constraints:
            adj_list[pred].append(succ)
            in_degree[succ] += 1
        
        execution_levels = []
        available = [task_id for task_id in in_degree if in_degree[task_id] == 0]
        
        while available:
            current_level = available[:]
            execution_levels.append(current_level)
            available = []
            
            for task_id in current_level:
                for successor in adj_list[task_id]:
                    in_degree[successor] -= 1
                    if in_degree[successor] == 0:
                        available.append(successor)
        
        return execution_levels


class HTNPlanner:
    """Hierarchical Task Network planner with dynamic replanning capabilities"""
    
    def __init__(self, domain_knowledge: Dict[str, Any]):
        self.domain = domain_knowledge
        self.task_methods: Dict[str, List[TaskDecomposition]] = {}
        self.primitive_operators: Dict[str, Callable] = {}
        self.current_plan: Optional[List[Task]] = None
        self.execution_state: Dict[str, Any] = {}
        self.planning_history: List[Dict[str, Any]] = []
        self.performance_metrics = {
            'plans_generated': 0,
            'successful_plans': 0,
            'replanning_events': 0,
            'average_planning_time': 0.0
        }
    
    def add_method(self, task_name: str, decomposition: TaskDecomposition):
        """Add decomposition method for a task"""
        if task_name not in self.task_methods:
            self.task_methods[task_name] = []
        self.task_methods[task_name].append(decomposition)
    
    def add_operator(self, task_name: str, operator_func: Callable):
        """Add primitive operator for a task"""
        self.primitive_operators[task_name] = operator_func
    
    async def create_hierarchical_plan(self, goal: str, 
                                     initial_state: Dict[str, Any],
                                     constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create hierarchical plan using HTN methodology"""
        
        planning_start = datetime.now()
        self.performance_metrics['plans_generated'] += 1
        
        logger.info(f"Creating HTN plan for goal: {goal}")
        
        # Phase 1: Goal analysis and root task creation
        root_task = await self._create_root_task(goal, initial_state)
        
        # Phase 2: Hierarchical decomposition
        decomposition_result = await self._decompose_task_hierarchy(
            root_task, initial_state, constraints or {}
        )
        
        if not decomposition_result['success']:
            return {
                'success': False,
                'error': decomposition_result.get('error', 'Decomposition failed'),
                'planning_time': datetime.now() - planning_start
            }
        
        # Phase 3: Plan optimization and validation
        optimized_plan = await self._optimize_plan(
            decomposition_result['tasks'], initial_state, constraints or {}
        )
        
        # Phase 4: Risk assessment and contingency planning
        risk_analysis = await self._analyze_plan_risks(optimized_plan, initial_state)
        contingency_plans = await self._create_contingency_plans(optimized_plan, risk_analysis)
        
        planning_duration = datetime.now() - planning_start
        self.performance_metrics['average_planning_time'] = (
            (self.performance_metrics['average_planning_time'] * (self.performance_metrics['plans_generated'] - 1) +
             planning_duration.total_seconds()) / self.performance_metrics['plans_generated']
        )
        
        plan_metadata = {
            'planning_time': planning_duration,
            'plan_depth': decomposition_result['max_depth'],
            'task_count': len(optimized_plan),
            'estimated_duration': sum(
                t.estimated_duration or timedelta(0) for t in optimized_plan
            ),
            'estimated_cost': sum(t.cost for t in optimized_plan),
            'confidence': decomposition_result['confidence']
        }
        
        plan_result = {
            'success': True,
            'plan': optimized_plan,
            'contingencies': contingency_plans,
            'risk_analysis': risk_analysis,
            'metadata': plan_metadata,
            'root_task': root_task
        }
        
        # Store planning history
        self.planning_history.append({
            'goal': goal,
            'timestamp': datetime.now(),
            'result': plan_result,
            'initial_state': initial_state
        })
        
        self.current_plan = optimized_plan
        logger.info(f"HTN planning completed in {planning_duration.total_seconds():.2f}s")
        
        return plan_result
    
    async def _create_root_task(self, goal: str, state: Dict[str, Any]) -> Task:
        """Create root task from goal specification"""
        
        # Analyze goal to determine task type and parameters
        goal_analysis = await self._analyze_goal(goal, state)
        
        root_task = Task(
            name=f"achieve_{goal.lower().replace(' ', '_')}",
            task_type=TaskType.ABSTRACT,
            parameters={'goal_description': goal, 'analysis': goal_analysis},
            priority=10,  # Highest priority for root goal
            estimated_duration=goal_analysis.get('estimated_duration', timedelta(hours=1))
        )
        
        return root_task
    
    async def _analyze_goal(self, goal: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze goal to extract planning information"""
        
        # Simple goal analysis - in production would use NLP and domain reasoning
        analysis = {
            'complexity': 'medium',
            'estimated_duration': timedelta(minutes=30),
            'required_resources': [],
            'involved_agents': [],
            'success_criteria': []
        }
        
        # Extract keywords and map to complexity
        if any(word in goal.lower() for word in ['complex', 'comprehensive', 'detailed']):
            analysis['complexity'] = 'high'
            analysis['estimated_duration'] = timedelta(hours=2)
        elif any(word in goal.lower() for word in ['simple', 'basic', 'quick']):
            analysis['complexity'] = 'low'
            analysis['estimated_duration'] = timedelta(minutes=15)
        
        return analysis
    
    async def _decompose_task_hierarchy(self, task: Task, state: Dict[str, Any], 
                                       constraints: Dict[str, Any], depth: int = 0) -> Dict[str, Any]:
        """Recursively decompose tasks in the hierarchy"""
        
        if depth > 10:  # Prevent infinite recursion
            return {
                'success': False,
                'error': 'Maximum decomposition depth exceeded',
                'max_depth': depth
            }
        
        if task.task_type == TaskType.PRIMITIVE:
            return {
                'success': True,
                'tasks': [task],
                'max_depth': depth,
                'confidence': 1.0
            }
        
        # Find applicable decompositions
        applicable_decompositions = await self._find_applicable_decompositions(task, state)
        
        if not applicable_decompositions:
            return {
                'success': False,
                'error': f'No applicable decompositions for task {task.name}',
                'max_depth': depth
            }
        
        # Select best decomposition
        best_decomposition = await self._select_best_decomposition(
            applicable_decompositions, state, constraints
        )
        
        # Recursively decompose subtasks
        all_tasks = []
        total_confidence = 1.0
        max_subdepth = depth
        
        for subtask in best_decomposition.subtasks:
            subtask_result = await self._decompose_task_hierarchy(
                subtask, state, constraints, depth + 1
            )
            
            if subtask_result['success']:
                all_tasks.extend(subtask_result['tasks'])
                total_confidence *= subtask_result['confidence']
                max_subdepth = max(max_subdepth, subtask_result['max_depth'])
            else:
                return {
                    'success': False,
                    'error': f'Failed to decompose subtask: {subtask.name}',
                    'max_depth': depth
                }
        
        # Apply ordering constraints
        await self._apply_ordering_constraints(all_tasks, best_decomposition.ordering_constraints)
        
        return {
            'success': True,
            'tasks': all_tasks,
            'max_depth': max_subdepth,
            'confidence': total_confidence * best_decomposition.success_probability
        }
    
    async def _find_applicable_decompositions(self, task: Task, 
                                            state: Dict[str, Any]) -> List[TaskDecomposition]:
        """Find decompositions applicable to the task in current state"""
        
        applicable = []
        
        # Check registered methods
        if task.name in self.task_methods:
            for decomposition in self.task_methods[task.name]:
                if decomposition.is_applicable(state):
                    applicable.append(decomposition)
        
        # Generate default decompositions if none found
        if not applicable:
            default_decomposition = await self._generate_default_decomposition(task, state)
            if default_decomposition:
                applicable.append(default_decomposition)
        
        return applicable
    
    async def _generate_default_decomposition(self, task: Task, 
                                            state: Dict[str, Any]) -> Optional[TaskDecomposition]:
        """Generate default decomposition for unknown tasks"""
        
        # Simple heuristic decomposition based on task name and parameters
        if 'analyze' in task.name.lower():
            subtasks = [
                Task(name=f"gather_info_for_{task.name}", task_type=TaskType.PRIMITIVE),
                Task(name=f"process_data_for_{task.name}", task_type=TaskType.PRIMITIVE),
                Task(name=f"generate_report_for_{task.name}", task_type=TaskType.PRIMITIVE)
            ]
        elif 'create' in task.name.lower():
            subtasks = [
                Task(name=f"plan_{task.name}", task_type=TaskType.PRIMITIVE),
                Task(name=f"implement_{task.name}", task_type=TaskType.PRIMITIVE),
                Task(name=f"test_{task.name}", task_type=TaskType.PRIMITIVE)
            ]
        else:
            # Generic decomposition
            subtasks = [
                Task(name=f"prepare_for_{task.name}", task_type=TaskType.PRIMITIVE),
                Task(name=f"execute_{task.name}", task_type=TaskType.PRIMITIVE),
                Task(name=f"finalize_{task.name}", task_type=TaskType.PRIMITIVE)
            ]
        
        # Set estimated durations and costs
        total_duration = task.estimated_duration or timedelta(minutes=30)
        duration_per_subtask = total_duration / len(subtasks)
        
        for i, subtask in enumerate(subtasks):
            subtask.estimated_duration = duration_per_subtask
            subtask.cost = task.cost / len(subtasks)
            subtask.parent_task = task.task_id
            
            # Add dependencies for sequential execution
            if i > 0:
                subtask.dependencies.append(subtasks[i-1].task_id)
        
        return TaskDecomposition(
            name=f"default_decomposition_for_{task.name}",
            subtasks=subtasks,
            ordering_constraints=[(subtasks[i].task_id, subtasks[i+1].task_id) 
                                 for i in range(len(subtasks)-1)],
            success_probability=0.8
        )
    
    async def _select_best_decomposition(self, decompositions: List[TaskDecomposition],
                                        state: Dict[str, Any], 
                                        constraints: Dict[str, Any]) -> TaskDecomposition:
        """Select best decomposition based on multiple criteria"""
        
        if len(decompositions) == 1:
            return decompositions[0]
        
        scores = []
        for decomposition in decompositions:
            score = await self._score_decomposition(decomposition, state, constraints)
            scores.append((score, decomposition))
        
        # Sort by score (highest first)
        scores.sort(key=lambda x: x[0], reverse=True)
        
        return scores[0][1]
    
    async def _score_decomposition(self, decomposition: TaskDecomposition,
                                  state: Dict[str, Any],
                                  constraints: Dict[str, Any]) -> float:
        """Score decomposition based on multiple factors"""
        
        score = 0.0
        
        # Success probability weight
        score += decomposition.success_probability * 0.4
        
        # Cost efficiency (lower cost is better)
        max_cost = constraints.get('max_cost', float('inf'))
        if max_cost > 0:
            cost_factor = max(0, 1 - (decomposition.estimated_cost / max_cost))
            score += cost_factor * 0.3
        
        # Parallelization preference
        if decomposition.parallel_execution and constraints.get('prefer_parallel', False):
            score += 0.2
        
        # Resource availability
        resource_score = await self._calculate_resource_availability_score(
            decomposition, state
        )
        score += resource_score * 0.1
        
        return score
    
    async def _calculate_resource_availability_score(self, decomposition: TaskDecomposition,
                                                    state: Dict[str, Any]) -> float:
        """Calculate resource availability score for decomposition"""
        
        required_resources = set()
        available_resources = state.get('resources', {})
        
        for subtask in decomposition.subtasks:
            for condition in subtask.preconditions:
                if condition.condition_type == "has_resource":
                    required_resources.add(condition.parameters.get('resource'))
        
        if not required_resources:
            return 1.0
        
        available_count = sum(1 for resource in required_resources 
                            if available_resources.get(resource, 0) > 0)
        
        return available_count / len(required_resources)
    
    async def _optimize_plan(self, tasks: List[Task], state: Dict[str, Any],
                            constraints: Dict[str, Any]) -> List[Task]:
        """Optimize plan for efficiency and constraint satisfaction"""
        
        # Sort tasks by priority and dependencies
        optimized_tasks = await self._topological_sort_tasks(tasks)
        
        # Apply constraint-based optimizations
        if constraints.get('minimize_cost', False):
            optimized_tasks = await self._optimize_for_cost(optimized_tasks)
        
        if constraints.get('minimize_time', False):
            optimized_tasks = await self._optimize_for_time(optimized_tasks)
        
        # Resource allocation optimization
        optimized_tasks = await self._optimize_resource_allocation(optimized_tasks, state)
        
        return optimized_tasks
    
    async def _topological_sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks in valid execution order"""
        
        # Build dependency graph
        task_map = {task.task_id: task for task in tasks}
        in_degree = {task.task_id: len(task.dependencies) for task in tasks}
        
        # Priority queue for tasks ready to execute
        ready_tasks = []
        for task in tasks:
            if in_degree[task.task_id] == 0:
                heapq.heappush(ready_tasks, (-task.priority, task.task_id))
        
        sorted_tasks = []
        
        while ready_tasks:
            _, task_id = heapq.heappop(ready_tasks)
            task = task_map[task_id]
            sorted_tasks.append(task)
            
            # Update dependencies
            for dependent_task in tasks:
                if task_id in dependent_task.dependencies:
                    in_degree[dependent_task.task_id] -= 1
                    if in_degree[dependent_task.task_id] == 0:
                        heapq.heappush(ready_tasks, 
                                     (-dependent_task.priority, dependent_task.task_id))
        
        return sorted_tasks
    
    async def _optimize_for_cost(self, tasks: List[Task]) -> List[Task]:
        """Optimize task ordering for cost minimization"""
        
        # Simple cost optimization - prioritize lower cost tasks when possible
        optimized = []
        remaining = tasks.copy()
        
        while remaining:
            # Find tasks with no unfulfilled dependencies
            executable_tasks = []
            for task in remaining:
                dependencies_met = all(
                    dep_task.task_id not in [t.task_id for t in remaining]
                    for dep_task in tasks if task.task_id in [t.task_id for t in remaining]
                )
                if dependencies_met:
                    executable_tasks.append(task)
            
            if not executable_tasks:
                # Fallback to first available task
                executable_tasks = [remaining[0]]
            
            # Choose lowest cost task
            chosen_task = min(executable_tasks, key=lambda t: t.cost)
            optimized.append(chosen_task)
            remaining.remove(chosen_task)
        
        return optimized
    
    async def _optimize_for_time(self, tasks: List[Task]) -> List[Task]:
        """Optimize task ordering for time minimization"""
        
        # Identify parallelizable tasks
        parallel_groups = []
        sequential_tasks = []
        
        for task in tasks:
            if not task.dependencies:
                # Check if this task can run in parallel with others
                can_parallelize = task.task_type in [TaskType.PARALLEL, TaskType.PRIMITIVE]
                if can_parallelize and parallel_groups:
                    parallel_groups[-1].append(task)
                else:
                    parallel_groups.append([task])
            else:
                sequential_tasks.append(task)
        
        # Merge parallel and sequential tasks
        optimized = []
        for group in parallel_groups:
            optimized.extend(sorted(group, key=lambda t: t.priority, reverse=True))
        
        optimized.extend(sequential_tasks)
        
        return optimized
    
    async def _optimize_resource_allocation(self, tasks: List[Task], 
                                          state: Dict[str, Any]) -> List[Task]:
        """Optimize resource allocation across tasks"""
        
        available_agents = state.get('agents', {})
        
        # Simple agent assignment based on capabilities
        for task in tasks:
            if task.task_type == TaskType.PRIMITIVE and not task.assigned_agent:
                # Find best agent for this task
                best_agent = await self._find_best_agent_for_task(task, available_agents)
                if best_agent:
                    task.assigned_agent = best_agent
                    task.metadata['agent_assignment_reason'] = 'optimization'
        
        return tasks
    
    async def _find_best_agent_for_task(self, task: Task, 
                                      available_agents: Dict[str, Any]) -> Optional[str]:
        """Find best agent for a specific task"""
        
        best_agent = None
        best_score = 0.0
        
        for agent_id, agent_info in available_agents.items():
            if agent_info.get('status') == 'available':
                # Calculate suitability score
                score = 0.0
                
                # Skill match
                agent_skills = agent_info.get('skills', [])
                required_skills = task.parameters.get('required_skills', [])
                skill_match = len(set(agent_skills) & set(required_skills))
                score += skill_match * 0.5
                
                # Capacity
                agent_capacity = agent_info.get('capacity', 1)
                current_load = agent_info.get('current_load', 0)
                if current_load < agent_capacity:
                    score += 0.3
                
                # Preference for specialized agents
                if any(skill in agent_skills for skill in required_skills):
                    score += 0.2
                
                if score > best_score:
                    best_score = score
                    best_agent = agent_id
        
        return best_agent
    
    async def _apply_ordering_constraints(self, tasks: List[Task], 
                                         constraints: List[Tuple[str, str]]):
        """Apply ordering constraints to task dependencies"""
        
        task_map = {task.task_id: task for task in tasks}
        
        for pred_id, succ_id in constraints:
            if succ_id in task_map and pred_id in task_map:
                if pred_id not in task_map[succ_id].dependencies:
                    task_map[succ_id].dependencies.append(pred_id)
    
    async def _analyze_plan_risks(self, tasks: List[Task], 
                                 state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential risks in the plan"""
        
        risks = []
        risk_score = 0.0
        
        # Resource availability risks
        required_resources = {}
        available_resources = state.get('resources', {})
        
        for task in tasks:
            for condition in task.preconditions:
                if condition.condition_type == "has_resource":
                    resource = condition.parameters.get('resource')
                    required_resources[resource] = required_resources.get(resource, 0) + 1
        
        for resource, required in required_resources.items():
            available = available_resources.get(resource, 0)
            if available < required:
                risks.append({
                    'type': 'resource_shortage',
                    'resource': resource,
                    'required': required,
                    'available': available,
                    'severity': 'high' if available == 0 else 'medium'
                })
                risk_score += 0.3 if available == 0 else 0.1
        
        # Dependency chain risks
        max_chain_length = await self._calculate_max_dependency_chain(tasks)
        if max_chain_length > 10:
            risks.append({
                'type': 'long_dependency_chain',
                'chain_length': max_chain_length,
                'severity': 'medium'
            })
            risk_score += 0.2
        
        # Time constraint risks
        total_estimated_time = sum(
            (task.estimated_duration or timedelta(0)).total_seconds() 
            for task in tasks
        )
        deadline = state.get('deadline')
        if deadline:
            available_time = (deadline - datetime.now()).total_seconds()
            if total_estimated_time > available_time * 0.8:  # 80% threshold
                risks.append({
                    'type': 'time_constraint',
                    'estimated_time': total_estimated_time,
                    'available_time': available_time,
                    'severity': 'high' if total_estimated_time > available_time else 'medium'
                })
                risk_score += 0.4 if total_estimated_time > available_time else 0.2
        
        return {
            'risks': risks,
            'overall_risk_score': min(1.0, risk_score),
            'risk_level': 'high' if risk_score > 0.6 else 'medium' if risk_score > 0.3 else 'low'
        }
    
    async def _calculate_max_dependency_chain(self, tasks: List[Task]) -> int:
        """Calculate the longest dependency chain in the plan"""
        
        task_map = {task.task_id: task for task in tasks}
        memo = {}
        
        def dfs_chain_length(task_id: str) -> int:
            if task_id in memo:
                return memo[task_id]
            
            if task_id not in task_map:
                return 0
            
            task = task_map[task_id]
            if not task.dependencies:
                memo[task_id] = 1
                return 1
            
            max_dep_length = max(dfs_chain_length(dep) for dep in task.dependencies)
            memo[task_id] = max_dep_length + 1
            return memo[task_id]
        
        return max(dfs_chain_length(task.task_id) for task in tasks)
    
    async def _create_contingency_plans(self, tasks: List[Task], 
                                       risk_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create contingency plans for identified risks"""
        
        contingency_plans = []
        
        for risk in risk_analysis['risks']:
            if risk['type'] == 'resource_shortage':
                contingency_plans.append({
                    'trigger': f"resource_{risk['resource']}_unavailable",
                    'alternative_actions': [
                        f"acquire_additional_{risk['resource']}",
                        f"modify_tasks_to_reduce_{risk['resource']}_usage",
                        f"delay_tasks_requiring_{risk['resource']}"
                    ],
                    'estimated_delay': timedelta(minutes=30)
                })
            
            elif risk['type'] == 'time_constraint':
                contingency_plans.append({
                    'trigger': 'deadline_pressure',
                    'alternative_actions': [
                        'parallelize_more_tasks',
                        'reduce_task_scope',
                        'allocate_additional_agents',
                        'negotiate_deadline_extension'
                    ],
                    'estimated_delay': timedelta(0)  # May actually speed up
                })
            
            elif risk['type'] == 'long_dependency_chain':
                contingency_plans.append({
                    'trigger': 'dependency_chain_failure',
                    'alternative_actions': [
                        'create_parallel_execution_paths',
                        'reduce_inter_task_dependencies',
                        'implement_checkpoint_recovery'
                    ],
                    'estimated_delay': timedelta(minutes=15)
                })
        
        return contingency_plans


class DynamicReplanner:
    """Handles dynamic replanning during plan execution"""
    
    def __init__(self, htn_planner: HTNPlanner):
        self.planner = htn_planner
        self.monitoring_active = False
        self.replanning_triggers = []
        self.replanning_history = []
        self.execution_context = {}
    
    async def execute_with_replanning(self, plan: List[Task], 
                                     initial_state: Dict[str, Any],
                                     monitoring_interval: timedelta = timedelta(seconds=10)) -> Dict[str, Any]:
        """Execute plan with continuous monitoring and replanning"""
        
        execution_start = datetime.now()
        execution_trace = []
        current_state = initial_state.copy()
        remaining_tasks = plan.copy()
        completed_tasks = []
        
        self.monitoring_active = True
        logger.info(f"Starting plan execution with {len(plan)} tasks")
        
        # Start monitoring task
        monitoring_task = asyncio.create_task(
            self._continuous_monitoring(remaining_tasks, current_state, monitoring_interval)
        )
        
        try:
            while remaining_tasks and self.monitoring_active:
                # Get next executable task
                executable_task = await self._get_next_executable_task(remaining_tasks, current_state)
                
                if not executable_task:
                    # No executable tasks - check for replanning needs
                    replan_needed = await self._check_replanning_triggers(
                        remaining_tasks, current_state
                    )
                    
                    if replan_needed:
                        replanning_result = await self._trigger_replanning(
                            remaining_tasks, current_state, "no_executable_tasks"
                        )
                        
                        if replanning_result['success']:
                            remaining_tasks = replanning_result['new_plan']
                            execution_trace.append(('replan', replanning_result))
                            continue
                        else:
                            execution_trace.append(('failed_replan', replanning_result))
                            break
                    else:
                        # Wait and retry
                        await asyncio.sleep(1)
                        continue
                
                # Pre-execution validation
                validation_result = await self._validate_task_execution(
                    executable_task, current_state
                )
                
                if not validation_result['can_execute']:
                    replanning_result = await self._trigger_replanning(
                        remaining_tasks, current_state, 
                        f"validation_failed: {validation_result['reason']}"
                    )
                    
                    if replanning_result['success']:
                        remaining_tasks = replanning_result['new_plan']
                        execution_trace.append(('replan_validation', replanning_result))
                        continue
                    else:
                        execution_trace.append(('abort_validation', replanning_result))
                        break
                
                # Execute task
                execution_result = await self._execute_monitored_task(
                    executable_task, current_state
                )
                
                execution_trace.append(('execute', execution_result))
                
                if execution_result['success']:
                    # Update state and move task to completed
                    current_state = executable_task.apply_effects(current_state)
                    completed_tasks.append(executable_task)
                    remaining_tasks.remove(executable_task)
                    
                    # Update task status in state
                    if 'task_status' not in current_state:
                        current_state['task_status'] = {}
                    current_state['task_status'][executable_task.task_id] = TaskStatus.COMPLETED.value
                    
                else:
                    # Handle execution failure
                    failure_analysis = await self._analyze_execution_failure(
                        executable_task, execution_result
                    )
                    
                    if failure_analysis['should_replan']:
                        replanning_result = await self._trigger_replanning(
                            remaining_tasks, current_state,
                            f"task_failure: {execution_result['error']}"
                        )
                        
                        if replanning_result['success']:
                            remaining_tasks = replanning_result['new_plan']
                            execution_trace.append(('replan_failure', replanning_result))
                            continue
                    
                    execution_trace.append(('abort_failure', failure_analysis))
                    break
        
        finally:
            self.monitoring_active = False
            monitoring_task.cancel()
        
        execution_duration = datetime.now() - execution_start
        
        return {
            'completed_tasks': completed_tasks,
            'remaining_tasks': remaining_tasks,
            'final_state': current_state,
            'execution_trace': execution_trace,
            'execution_duration': execution_duration,
            'success': len(remaining_tasks) == 0,
            'completion_rate': len(completed_tasks) / len(plan) if plan else 0
        }
    
    async def _continuous_monitoring(self, tasks: List[Task], state: Dict[str, Any], 
                                    interval: timedelta):
        """Continuously monitor execution for replanning triggers"""
        
        while self.monitoring_active:
            try:
                # Check for environmental changes
                env_changes = await self._detect_environmental_changes(state)
                if env_changes:
                    self.replanning_triggers.append({
                        'type': 'environmental_change',
                        'details': env_changes,
                        'timestamp': datetime.now()
                    })
                
                # Check for resource changes
                resource_changes = await self._detect_resource_changes(state)
                if resource_changes:
                    self.replanning_triggers.append({
                        'type': 'resource_change',
                        'details': resource_changes,
                        'timestamp': datetime.now()
                    })
                
                await asyncio.sleep(interval.total_seconds())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(interval.total_seconds())
    
    async def _get_next_executable_task(self, tasks: List[Task], 
                                       state: Dict[str, Any]) -> Optional[Task]:
        """Get next task that can be executed"""
        
        executable_tasks = []
        
        for task in tasks:
            if task.status == TaskStatus.PENDING:
                can_execute, _ = task.can_execute(state)
                if can_execute:
                    executable_tasks.append(task)
        
        if not executable_tasks:
            return None
        
        # Sort by priority and return highest priority task
        executable_tasks.sort(key=lambda t: t.priority, reverse=True)
        return executable_tasks[0]
    
    async def _validate_task_execution(self, task: Task, 
                                      state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that task can be executed in current state"""
        
        can_execute, failed_conditions = task.can_execute(state)
        
        return {
            'can_execute': can_execute,
            'failed_conditions': failed_conditions,
            'reason': '; '.join(failed_conditions) if failed_conditions else None
        }
    
    async def _execute_monitored_task(self, task: Task, 
                                     state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with monitoring and error handling"""
        
        task.status = TaskStatus.EXECUTING
        task.started_at = datetime.now()
        
        try:
            # Mock task execution
            execution_time = task.estimated_duration or timedelta(seconds=5)
            await asyncio.sleep(min(execution_time.total_seconds(), 2))  # Cap at 2 seconds for demo
            
            # Simulate success rate based on task complexity
            success_rate = 0.9  # 90% base success rate
            if task.task_type == TaskType.COMPOUND:
                success_rate = 0.8
            elif task.priority > 8:
                success_rate = 0.7  # High priority tasks are often more complex
            
            success = random.random() < success_rate
            
            task.completed_at = datetime.now()
            task.actual_duration = task.completed_at - task.started_at
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            
            if success:
                return {
                    'success': True,
                    'task_id': task.task_id,
                    'execution_time': task.actual_duration,
                    'result': f"Successfully completed {task.name}"
                }
            else:
                return {
                    'success': False,
                    'task_id': task.task_id,
                    'error': f"Task {task.name} failed during execution",
                    'execution_time': task.actual_duration
                }
                
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.actual_duration = task.completed_at - task.started_at
            
            return {
                'success': False,
                'task_id': task.task_id,
                'error': str(e),
                'execution_time': task.actual_duration
            }
    
    async def _trigger_replanning(self, remaining_tasks: List[Task], 
                                 current_state: Dict[str, Any], 
                                 trigger_reason: str) -> Dict[str, Any]:
        """Trigger replanning process"""
        
        logger.info(f"Triggering replanning due to: {trigger_reason}")
        self.planner.performance_metrics['replanning_events'] += 1
        
        # Create new goal from remaining tasks
        remaining_goal = f"Complete remaining tasks: {[t.name for t in remaining_tasks]}"
        
        # Generate new plan
        planning_result = await self.planner.create_hierarchical_plan(
            remaining_goal, current_state
        )
        
        if planning_result['success']:
            new_plan = planning_result['plan']
            
            # Record replanning event
            replanning_record = {
                'trigger': trigger_reason,
                'timestamp': datetime.now(),
                'original_tasks': len(remaining_tasks),
                'new_tasks': len(new_plan),
                'planning_time': planning_result['metadata']['planning_time']
            }
            self.replanning_history.append(replanning_record)
            
            return {
                'success': True,
                'new_plan': new_plan,
                'replanning_record': replanning_record,
                'reason': trigger_reason
            }
        else:
            return {
                'success': False,
                'error': planning_result.get('error', 'Replanning failed'),
                'reason': trigger_reason
            }
    
    async def _check_replanning_triggers(self, tasks: List[Task], 
                                        state: Dict[str, Any]) -> bool:
        """Check if replanning is needed"""
        
        # Check accumulated triggers
        recent_triggers = [
            t for t in self.replanning_triggers
            if (datetime.now() - t['timestamp']) < timedelta(minutes=5)
        ]
        
        return len(recent_triggers) > 2  # Replan if multiple triggers in short time
    
    async def _detect_environmental_changes(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect changes in environment that might require replanning"""
        
        # Mock environmental change detection
        import random
        if random.random() < 0.02:  # 2% chance of environmental change
            return {
                'change_type': 'resource_availability',
                'description': 'Critical resource became unavailable'
            }
        
        return None
    
    async def _detect_resource_changes(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect changes in resource availability"""
        
        # Mock resource change detection
        import random
        if random.random() < 0.01:  # 1% chance of resource change
            return {
                'change_type': 'agent_availability',
                'description': 'Agent became unavailable'
            }
        
        return None
    
    async def _analyze_execution_failure(self, task: Task, 
                                        execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task execution failure to determine response"""
        
        error_message = execution_result.get('error', '')
        
        # Determine if replanning is needed
        should_replan = False
        recovery_options = []
        
        if 'resource' in error_message.lower():
            should_replan = True
            recovery_options.append('acquire_alternative_resources')
            recovery_options.append('modify_task_requirements')
        elif 'timeout' in error_message.lower():
            should_replan = True
            recovery_options.append('increase_time_allocation')
            recovery_options.append('simplify_task_scope')
        elif 'dependency' in error_message.lower():
            should_replan = True
            recovery_options.append('resolve_dependency_issues')
            recovery_options.append('find_alternative_execution_path')
        else:
            # Generic failure - try simple retry first
            recovery_options.append('retry_task')
            recovery_options.append('assign_different_agent')
        
        return {
            'should_replan': should_replan,
            'recovery_options': recovery_options,
            'failure_severity': 'high' if should_replan else 'medium',
            'task_id': task.task_id,
            'error_analysis': error_message
        }


# Demonstration and testing functions
import random

async def demonstrate_planning_systems():
    """Demonstrate HTN planning and dynamic replanning capabilities"""
    
    print("🎯 Advanced Planning Systems Demonstration")
    print("=" * 50)
    
    # Initialize domain knowledge
    domain_knowledge = {
        'task_types': ['analyze', 'create', 'implement', 'test'],
        'resources': ['compute', 'data', 'agents'],
        'constraints': ['time', 'cost', 'quality']
    }
    
    # Create HTN planner
    planner = HTNPlanner(domain_knowledge)
    
    # Add some decomposition methods
    analysis_decomp = TaskDecomposition(
        name="standard_analysis_method",
        subtasks=[
            Task(name="gather_requirements", task_type=TaskType.PRIMITIVE, 
                 estimated_duration=timedelta(minutes=15)),
            Task(name="analyze_data", task_type=TaskType.PRIMITIVE,
                 estimated_duration=timedelta(minutes=30)),
            Task(name="generate_insights", task_type=TaskType.PRIMITIVE,
                 estimated_duration=timedelta(minutes=20))
        ],
        success_probability=0.9
    )
    planner.add_method("analyze_market_trends", analysis_decomp)
    
    # Test complex planning scenario
    goal = "Create comprehensive market analysis report with actionable insights"
    initial_state = {
        'resources': {'data': 5, 'compute': 3, 'agents': 2},
        'agents': {
            'analyst_1': {'status': 'available', 'skills': ['analysis', 'reporting'], 'capacity': 2, 'current_load': 0},
            'analyst_2': {'status': 'available', 'skills': ['data_processing', 'visualization'], 'capacity': 3, 'current_load': 1}
        },
        'current_time': datetime.now(),
        'deadline': datetime.now() + timedelta(hours=4)
    }
    
    constraints = {
        'max_cost': 1000,
        'prefer_parallel': True,
        'minimize_time': True
    }
    
    print(f"📋 Goal: {goal}")
    print(f"⏰ Deadline: {initial_state['deadline'].strftime('%H:%M:%S')}")
    print(f"💰 Budget: ${constraints['max_cost']}")
    
    # Create hierarchical plan
    print(f"\n🔍 Creating HTN Plan...")
    planning_result = await planner.create_hierarchical_plan(goal, initial_state, constraints)
    
    if planning_result['success']:
        plan = planning_result['plan']
        metadata = planning_result['metadata']
        
        print(f"✅ Planning successful!")
        print(f"📊 Plan Details:")
        print(f"   - Tasks: {metadata['task_count']}")
        print(f"   - Estimated duration: {metadata['estimated_duration']}")
        print(f"   - Estimated cost: ${metadata['estimated_cost']:.2f}")
        print(f"   - Planning time: {metadata['planning_time'].total_seconds():.2f}s")
        print(f"   - Confidence: {metadata['confidence']:.2f}")
        
        # Show task breakdown
        print(f"\n📝 Task Breakdown:")
        for i, task in enumerate(plan[:5]):  # Show first 5 tasks
            print(f"   {i+1}. {task.name} ({task.task_type.value})")
            print(f"      Priority: {task.priority}, Cost: ${task.cost:.2f}")
            if task.assigned_agent:
                print(f"      Assigned: {task.assigned_agent}")
        
        if len(plan) > 5:
            print(f"   ... and {len(plan) - 5} more tasks")
        
        # Show risk analysis
        if planning_result['risk_analysis']['risks']:
            print(f"\n⚠️  Risk Analysis ({planning_result['risk_analysis']['risk_level']} risk):")
            for risk in planning_result['risk_analysis']['risks'][:3]:
                print(f"   - {risk['type']}: {risk.get('severity', 'unknown')} severity")
        
        # Demonstrate dynamic replanning
        print(f"\n🔄 Testing Dynamic Replanning...")
        
        replanner = DynamicReplanner(planner)
        
        # Simulate some environmental changes
        modified_state = initial_state.copy()
        modified_state['agents']['analyst_1']['status'] = 'unavailable'  # Simulate agent failure
        
        execution_result = await replanner.execute_with_replanning(
            plan[:3], modified_state, monitoring_interval=timedelta(seconds=1)  # Fast monitoring for demo
        )
        
        print(f"🎯 Execution Results:")
        print(f"   - Completion rate: {execution_result['completion_rate']:.1%}")
        print(f"   - Tasks completed: {len(execution_result['completed_tasks'])}")
        print(f"   - Execution time: {execution_result['execution_duration'].total_seconds():.2f}s")
        print(f"   - Success: {execution_result['success']}")
        
        # Show execution trace summary
        trace_summary = {}
        for event_type, _ in execution_result['execution_trace']:
            trace_summary[event_type] = trace_summary.get(event_type, 0) + 1
        
        print(f"\n📈 Execution Trace:")
        for event_type, count in trace_summary.items():
            print(f"   - {event_type}: {count} events")
        
        # Show performance metrics
        print(f"\n📊 Planning System Performance:")
        metrics = planner.performance_metrics
        print(f"   - Plans generated: {metrics['plans_generated']}")
        print(f"   - Success rate: {metrics['successful_plans']/max(1,metrics['plans_generated']):.1%}")
        print(f"   - Replanning events: {metrics['replanning_events']}")
        print(f"   - Avg planning time: {metrics['average_planning_time']:.2f}s")
        
    else:
        print(f"❌ Planning failed: {planning_result.get('error')}")
    
    return planning_result


if __name__ == "__main__":
    asyncio.run(demonstrate_planning_systems())