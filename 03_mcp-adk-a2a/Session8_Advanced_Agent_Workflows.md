# Session 8: Advanced Agent Workflows

## 🎯 Learning Outcomes

By the end of this session, you will be able to:
- **Design** complex multi-agent workflows with parallel processing and conditional logic
- **Implement** adaptive workflow systems that optimize themselves based on performance data
- **Create** fault-tolerant workflows with comprehensive error handling and recovery mechanisms
- **Build** workflow monitoring and observability systems for production environments
- **Deploy** scalable workflow orchestration platforms with load balancing and resource management

## 📚 Chapter Overview

Advanced agent workflows go beyond simple sequential processing to include sophisticated patterns like parallel execution, conditional branching, dynamic adaptation, and intelligent error recovery. This session explores enterprise-grade workflow patterns that can handle complex, real-world scenarios.

![Advanced Workflow Architecture](images/advanced-workflow-architecture.png)

The architecture demonstrates:
- **Parallel Processing**: Concurrent execution of independent workflow branches
- **Conditional Logic**: Dynamic routing based on data and context
- **Adaptive Optimization**: Self-improving workflows based on performance metrics
- **Fault Recovery**: Comprehensive error handling with rollback and retry mechanisms

---

## Part 1: Complex Workflow Patterns (25 minutes)

### Understanding Advanced Workflow Types

Modern agent workflows support multiple execution patterns:

1. **Sequential Workflows**: Linear step-by-step execution
2. **Parallel Workflows**: Concurrent execution with synchronization points  
3. **Conditional Workflows**: Dynamic branching based on data or context
4. **Loop Workflows**: Iterative processing with termination conditions
5. **Hybrid Workflows**: Combinations of the above patterns

### Step 1.1: Advanced Workflow Engine

Let's build a sophisticated workflow engine that supports all these patterns:

```python
# workflows/advanced_engine.py
import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

from workflows.execution_context import ExecutionContext, WorkflowState
from workflows.step_executor import StepExecutor
from workflows.monitors import WorkflowMonitor

logger = logging.getLogger(__name__)

class StepType(Enum):
    """Types of workflow steps."""
    ACTION = "action"           # Execute an action
    CONDITION = "condition"     # Conditional branching
    PARALLEL = "parallel"       # Parallel execution container
    LOOP = "loop"              # Loop container  
    WAIT = "wait"              # Wait/delay step
    HUMAN_TASK = "human_task"  # Human intervention required
    WEBHOOK = "webhook"        # External system integration

class StepStatus(Enum):
    """Status of workflow steps."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING = "waiting"
    RETRYING = "retrying"

@dataclass
class WorkflowStep:
    """Enhanced workflow step with advanced capabilities."""
    
    step_id: str
    name: str
    step_type: StepType
    
    # Execution configuration
    action: Optional[str] = None                    # Action to execute
    agent_capability: Optional[str] = None          # Required agent capability
    timeout: int = 300                             # Timeout in seconds
    
    # Input/Output configuration
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    input_validation: Dict[str, Any] = field(default_factory=dict)
    
    # Control flow
    dependencies: List[str] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    error_handlers: List[str] = field(default_factory=list)
    
    # Retry and error handling
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    rollback_actions: List[str] = field(default_factory=list)
    
    # Parallel and loop configuration
    parallel_steps: List['WorkflowStep'] = field(default_factory=list)
    loop_condition: Optional[str] = None
    loop_max_iterations: int = 100
    
    # Monitoring and observability
    metrics_enabled: bool = True
    custom_metrics: List[str] = field(default_factory=list)
    
    # Runtime state
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    execution_data: Dict[str, Any] = field(default_factory=dict)
    error_info: Optional[Dict[str, Any]] = None
    retry_count: int = 0

@dataclass
class AdvancedWorkflow:
    """Advanced workflow definition with complex patterns."""
    
    workflow_id: str
    name: str
    description: str
    version: str = "1.0"
    
    # Workflow structure
    steps: List[WorkflowStep] = field(default_factory=list)
    global_variables: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration
    timeout: int = 3600                            # Global timeout
    max_parallel_steps: int = 10                   # Max parallel execution
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    
    # Monitoring and optimization
    sla_targets: Dict[str, Any] = field(default_factory=dict)
    optimization_enabled: bool = True
    adaptive_routing: bool = True
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)

class AdvancedWorkflowEngine:
    """Advanced workflow engine with sophisticated execution patterns."""
    
    def __init__(self, step_executor: StepExecutor, monitor: WorkflowMonitor):
        self.step_executor = step_executor
        self.monitor = monitor
        self.active_workflows: Dict[str, ExecutionContext] = {}
        self.workflow_templates: Dict[str, AdvancedWorkflow] = {}
        
        # Execution control
        self.max_concurrent_workflows = 100
        self.resource_manager = ResourceManager()
        self.optimizer = WorkflowOptimizer()
        
    async def execute_workflow(self, workflow: AdvancedWorkflow, 
                             input_data: Dict[str, Any] = None,
                             execution_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an advanced workflow with full feature support."""
        
        execution_id = str(uuid.uuid4())
        input_data = input_data or {}
        execution_options = execution_options or {}
        
        # Create execution context
        context = ExecutionContext(
            execution_id=execution_id,
            workflow=workflow,
            input_data=input_data,
            options=execution_options
        )
        
        self.active_workflows[execution_id] = context
        
        try:
            # Start monitoring
            await self.monitor.start_workflow_monitoring(context)
            
            # Initialize workflow state
            context.state = WorkflowState.RUNNING
            context.start_time = datetime.now()
            
            # Execute workflow with timeout
            result = await asyncio.wait_for(
                self._execute_workflow_internal(context),
                timeout=workflow.timeout
            )
            
            # Finalize execution
            context.state = WorkflowState.COMPLETED
            context.end_time = datetime.now()
            context.result = result
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "result": result,
                "execution_time": (context.end_time - context.start_time).total_seconds(),
                "steps_executed": len([s for s in workflow.steps if s.status == StepStatus.COMPLETED]),
                "metrics": await self.monitor.get_execution_metrics(execution_id)
            }
            
        except asyncio.TimeoutError:
            context.state = WorkflowState.TIMEOUT
            logger.error(f"Workflow {execution_id} timed out after {workflow.timeout} seconds")
            
            return {
                "execution_id": execution_id,
                "status": "timeout",
                "error": "Workflow execution timed out",
                "partial_result": context.data
            }
            
        except Exception as e:
            context.state = WorkflowState.FAILED
            context.error = str(e)
            logger.error(f"Workflow {execution_id} failed: {e}")
            
            # Attempt rollback
            await self._execute_rollback(context)
            
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
                "partial_result": context.data
            }
            
        finally:
            # Cleanup
            await self.monitor.stop_workflow_monitoring(execution_id)
            self.active_workflows.pop(execution_id, None)
    
    async def _execute_workflow_internal(self, context: ExecutionContext) -> Dict[str, Any]:
        """Internal workflow execution logic."""
        
        workflow = context.workflow
        
        # Build execution graph
        execution_graph = self._build_execution_graph(workflow)
        
        # Execute steps based on dependencies and patterns
        completed_steps = set()
        failed_steps = set()
        
        while len(completed_steps) < len(workflow.steps):
            # Find ready steps (all dependencies satisfied)
            ready_steps = self._find_ready_steps(
                workflow, execution_graph, completed_steps, failed_steps
            )
            
            if not ready_steps:
                # Check for deadlock or all remaining steps failed
                remaining_steps = set(s.step_id for s in workflow.steps) - completed_steps - failed_steps
                if remaining_steps:
                    logger.warning(f"Potential deadlock detected. Remaining steps: {remaining_steps}")
                break
            
            # Execute ready steps with appropriate pattern
            execution_tasks = []
            
            for step in ready_steps:
                if step.step_type == StepType.PARALLEL:
                    # Execute parallel container
                    task = asyncio.create_task(
                        self._execute_parallel_step(step, context)
                    )
                elif step.step_type == StepType.LOOP:
                    # Execute loop container
                    task = asyncio.create_task(
                        self._execute_loop_step(step, context)
                    )
                elif step.step_type == StepType.CONDITION:
                    # Execute conditional step
                    task = asyncio.create_task(
                        self._execute_conditional_step(step, context)
                    )
                else:
                    # Execute regular step
                    task = asyncio.create_task(
                        self._execute_single_step(step, context)
                    )
                
                execution_tasks.append((step, task))
            
            # Wait for tasks to complete
            for step, task in execution_tasks:
                try:
                    result = await task
                    if result.get("success", False):
                        completed_steps.add(step.step_id)
                        step.status = StepStatus.COMPLETED
                        
                        # Apply output mapping
                        self._apply_output_mapping(step, result, context.data)
                    else:
                        failed_steps.add(step.step_id)
                        step.status = StepStatus.FAILED
                        step.error_info = result.get("error")
                        
                        # Check if failure should stop workflow
                        if not step.retry_policy.get("continue_on_failure", False):
                            raise Exception(f"Step {step.step_id} failed: {result.get('error')}")
                
                except Exception as e:
                    failed_steps.add(step.step_id)
                    step.status = StepStatus.FAILED
                    step.error_info = {"error": str(e), "timestamp": datetime.now().isoformat()}
                    
                    # Attempt error recovery
                    recovery_result = await self._handle_step_error(step, context, e)
                    if not recovery_result.get("recovered", False):
                        raise
        
        return context.data
    
    async def _execute_parallel_step(self, step: WorkflowStep, 
                                   context: ExecutionContext) -> Dict[str, Any]:
        """Execute a parallel step container."""
        
        if not step.parallel_steps:
            return {"success": True, "message": "No parallel steps to execute"}
        
        # Limit concurrent execution
        semaphore = asyncio.Semaphore(context.workflow.max_parallel_steps)
        
        async def execute_with_semaphore(parallel_step):
            async with semaphore:
                return await self._execute_single_step(parallel_step, context)
        
        # Execute all parallel steps
        tasks = [
            asyncio.create_task(execute_with_semaphore(parallel_step))
            for parallel_step in step.parallel_steps
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({
                    "step_id": step.parallel_steps[i].step_id,
                    "error": str(result)
                })
            elif result.get("success", False):
                successful_results.append(result)
            else:
                failed_results.append({
                    "step_id": step.parallel_steps[i].step_id,
                    "error": result.get("error", "Unknown error")
                })
        
        # Determine overall success
        total_steps = len(step.parallel_steps)
        successful_steps = len(successful_results)
        failure_threshold = step.retry_policy.get("parallel_failure_threshold", 0.5)
        
        success = (successful_steps / total_steps) >= failure_threshold
        
        return {
            "success": success,
            "parallel_results": {
                "total_steps": total_steps,
                "successful_steps": successful_steps,
                "failed_steps": len(failed_results),
                "success_rate": successful_steps / total_steps,
                "results": successful_results,
                "failures": failed_results
            }
        }
    
    async def _execute_loop_step(self, step: WorkflowStep, 
                               context: ExecutionContext) -> Dict[str, Any]:
        """Execute a loop step container."""
        
        if not step.loop_condition:
            return {"success": False, "error": "No loop condition specified"}
        
        iteration_count = 0
        loop_results = []
        
        while iteration_count < step.loop_max_iterations:
            # Evaluate loop condition
            should_continue = self._evaluate_condition(step.loop_condition, context.data)
            
            if not should_continue:
                break
            
            # Execute loop body (parallel steps)
            if step.parallel_steps:
                loop_result = await self._execute_parallel_step(step, context)
                loop_results.append({
                    "iteration": iteration_count + 1,
                    "result": loop_result
                })
                
                # Check if loop should continue after failure
                if not loop_result.get("success", False):
                    continue_on_failure = step.retry_policy.get("continue_on_failure", False)
                    if not continue_on_failure:
                        break
            
            iteration_count += 1
            
            # Add small delay to prevent tight loops
            await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "loop_results": {
                "iterations_completed": iteration_count,
                "max_iterations_reached": iteration_count >= step.loop_max_iterations,
                "results": loop_results
            }
        }
    
    async def _execute_conditional_step(self, step: WorkflowStep, 
                                      context: ExecutionContext) -> Dict[str, Any]:
        """Execute a conditional step with branching logic."""
        
        if not step.conditions:
            return {"success": False, "error": "No conditions specified"}
        
        # Evaluate conditions in order
        for condition in step.conditions:
            condition_expr = condition.get("expression")
            branch_steps = condition.get("steps", [])
            
            if not condition_expr:
                continue
            
            # Evaluate condition
            if self._evaluate_condition(condition_expr, context.data):
                # Execute branch steps
                branch_results = []
                
                for branch_step_id in branch_steps:
                    # Find the step definition
                    branch_step = next(
                        (s for s in context.workflow.steps if s.step_id == branch_step_id),
                        None
                    )
                    
                    if branch_step:
                        result = await self._execute_single_step(branch_step, context)
                        branch_results.append(result)
                
                return {
                    "success": True,
                    "condition_matched": condition_expr,
                    "branch_results": branch_results
                }
        
        # No conditions matched - execute else branch if available
        else_steps = step.conditions[-1].get("else_steps", []) if step.conditions else []
        
        if else_steps:
            else_results = []
            for else_step_id in else_steps:
                else_step = next(
                    (s for s in context.workflow.steps if s.step_id == else_step_id),
                    None
                )
                
                if else_step:
                    result = await self._execute_single_step(else_step, context)
                    else_results.append(result)
            
            return {
                "success": True,
                "condition_matched": "else",
                "branch_results": else_results
            }
        
        return {
            "success": True,
            "condition_matched": "none",
            "message": "No conditions matched and no else branch"
        }
    
    async def _execute_single_step(self, step: WorkflowStep, 
                                 context: ExecutionContext) -> Dict[str, Any]:
        """Execute a single workflow step."""
        
        step.status = StepStatus.RUNNING
        step.start_time = datetime.now().isoformat()
        
        try:
            # Prepare step input
            step_input = self._prepare_step_input(step, context.data)
            
            # Validate input if schema provided
            if step.input_validation:
                validation_result = self._validate_step_input(step_input, step.input_validation)
                if not validation_result.get("valid", True):
                    raise ValueError(f"Input validation failed: {validation_result.get('errors')}")
            
            # Execute step with timeout and retry
            result = await self._execute_step_with_retry(step, step_input, context)
            
            step.status = StepStatus.COMPLETED
            step.end_time = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.end_time = datetime.now().isoformat()
            step.error_info = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "retry_count": step.retry_count
            }
            
            return {"success": False, "error": str(e)}
    
    async def _execute_step_with_retry(self, step: WorkflowStep, 
                                     step_input: Dict[str, Any],
                                     context: ExecutionContext) -> Dict[str, Any]:
        """Execute step with retry logic."""
        
        retry_policy = step.retry_policy or {}
        max_retries = retry_policy.get("max_retries", 3)
        retry_delay = retry_policy.get("retry_delay", 1.0)
        backoff_multiplier = retry_policy.get("backoff_multiplier", 2.0)
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    step.status = StepStatus.RETRYING
                    step.retry_count = attempt
                    
                    # Calculate delay with exponential backoff
                    delay = retry_delay * (backoff_multiplier ** (attempt - 1))
                    await asyncio.sleep(delay)
                
                # Execute the actual step
                result = await self.step_executor.execute_step(
                    step, step_input, context
                )
                
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Step {step.step_id} attempt {attempt + 1} failed: {e}")
                
                # Check if error is retryable
                if not self._is_retryable_error(e, retry_policy):
                    break
        
        # All retries exhausted
        raise last_error
    
    def _build_execution_graph(self, workflow: AdvancedWorkflow) -> Dict[str, List[str]]:
        """Build dependency graph for execution planning."""
        
        graph = {}
        
        for step in workflow.steps:
            graph[step.step_id] = step.dependencies.copy()
        
        return graph
    
    def _find_ready_steps(self, workflow: AdvancedWorkflow, graph: Dict[str, List[str]],
                         completed: set, failed: set) -> List[WorkflowStep]:
        """Find steps ready for execution."""
        
        ready_steps = []
        
        for step in workflow.steps:
            if step.step_id in completed or step.step_id in failed:
                continue
            
            # Check if all dependencies are satisfied
            dependencies = graph.get(step.step_id, [])
            if all(dep in completed for dep in dependencies):
                ready_steps.append(step)
        
        return ready_steps
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        
        try:
            # Create safe evaluation context
            context = {
                "data": data,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "abs": abs,
                "min": min,
                "max": max
            }
            
            return bool(eval(condition, {"__builtins__": {}}, context))
            
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False
    
    def _prepare_step_input(self, step: WorkflowStep, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for step execution."""
        
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
    
    def _validate_step_input(self, step_input: Dict[str, Any], 
                           validation_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate step input against schema."""
        
        # Simplified validation - in production, use jsonschema
        errors = []
        
        required_fields = validation_schema.get("required", [])
        for field in required_fields:
            if field not in step_input:
                errors.append(f"Required field '{field}' is missing")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _is_retryable_error(self, error: Exception, retry_policy: Dict[str, Any]) -> bool:
        """Check if error is retryable based on policy."""
        
        non_retryable_errors = retry_policy.get("non_retryable_errors", [
            "ValueError", "TypeError", "AuthenticationError"
        ])
        
        error_type = type(error).__name__
        return error_type not in non_retryable_errors
    
    async def _handle_step_error(self, step: WorkflowStep, context: ExecutionContext,
                               error: Exception) -> Dict[str, Any]:
        """Handle step execution error with recovery mechanisms."""
        
        recovery_result = {"recovered": False}
        
        # Execute error handlers if defined
        for handler_id in step.error_handlers:
            try:
                handler_step = next(
                    (s for s in context.workflow.steps if s.step_id == handler_id),
                    None
                )
                
                if handler_step:
                    handler_input = {
                        "original_error": str(error),
                        "failed_step_id": step.step_id,
                        "context_data": context.data
                    }
                    
                    handler_result = await self._execute_single_step(handler_step, context)
                    
                    if handler_result.get("success") and handler_result.get("recovery_action"):
                        recovery_result["recovered"] = True
                        recovery_result["action"] = handler_result.get("recovery_action")
                        break
                        
            except Exception as handler_error:
                logger.error(f"Error handler {handler_id} failed: {handler_error}")
        
        return recovery_result
    
    async def _execute_rollback(self, context: ExecutionContext):
        """Execute rollback actions for failed workflow."""
        
        logger.info(f"Executing rollback for workflow {context.execution_id}")
        
        # Execute rollback actions for completed steps in reverse order
        completed_steps = [
            step for step in context.workflow.steps 
            if step.status == StepStatus.COMPLETED and step.rollback_actions
        ]
        
        for step in reversed(completed_steps):
            for rollback_action in step.rollback_actions:
                try:
                    # Execute rollback action
                    rollback_result = await self.step_executor.execute_rollback_action(
                        rollback_action, step, context
                    )
                    
                    logger.info(f"Rollback action {rollback_action} completed for step {step.step_id}")
                    
                except Exception as e:
                    logger.error(f"Rollback action {rollback_action} failed for step {step.step_id}: {e}")
```

---

## Part 2: Workflow Optimization and Monitoring (20 minutes)

### Step 2.1: Performance Optimization

Implement intelligent workflow optimization:

```python
# workflows/optimizer.py
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
import logging

from workflows.advanced_engine import AdvancedWorkflow, WorkflowStep
from workflows.execution_context import ExecutionContext

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for workflow optimization."""
    
    execution_time: float
    resource_usage: Dict[str, float]
    success_rate: float
    error_rate: float
    step_performance: Dict[str, Dict[str, float]]
    bottlenecks: List[str]
    optimization_score: float

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation for workflows."""
    
    recommendation_id: str
    type: str                    # parallelization, caching, routing, etc.
    description: str
    expected_improvement: float  # Expected performance improvement %
    implementation_effort: str   # low, medium, high
    risk_level: str             # low, medium, high
    specific_changes: List[Dict[str, Any]]

class WorkflowOptimizer:
    """Intelligent workflow optimizer using performance data."""
    
    def __init__(self):
        self.performance_history: Dict[str, List[PerformanceMetrics]] = {}
        self.optimization_rules: List[Dict[str, Any]] = []
        self.learning_enabled = True
        
        self._initialize_optimization_rules()
    
    def _initialize_optimization_rules(self):
        """Initialize built-in optimization rules."""
        
        self.optimization_rules = [
            {
                "name": "parallel_optimization",
                "condition": lambda metrics: self._detect_parallelization_opportunity(metrics),
                "recommendation": self._create_parallelization_recommendation,
                "priority": 9
            },
            {
                "name": "caching_optimization", 
                "condition": lambda metrics: self._detect_caching_opportunity(metrics),
                "recommendation": self._create_caching_recommendation,
                "priority": 8
            },
            {
                "name": "resource_optimization",
                "condition": lambda metrics: self._detect_resource_waste(metrics),
                "recommendation": self._create_resource_optimization_recommendation,
                "priority": 7
            },
            {
                "name": "retry_optimization",
                "condition": lambda metrics: self._detect_retry_issues(metrics),
                "recommendation": self._create_retry_optimization_recommendation,
                "priority": 6
            },
            {
                "name": "routing_optimization",
                "condition": lambda metrics: self._detect_routing_inefficiency(metrics),
                "recommendation": self._create_routing_optimization_recommendation,
                "priority": 5
            }
        ]
    
    async def analyze_workflow_performance(self, workflow: AdvancedWorkflow,
                                         execution_history: List[ExecutionContext]) -> PerformanceMetrics:
        """Analyze workflow performance and identify optimization opportunities."""
        
        if not execution_history:
            return PerformanceMetrics(
                execution_time=0,
                resource_usage={},
                success_rate=0,
                error_rate=1,
                step_performance={},
                bottlenecks=[],
                optimization_score=0
            )
        
        # Calculate execution time statistics
        execution_times = [
            (ctx.end_time - ctx.start_time).total_seconds()
            for ctx in execution_history 
            if ctx.end_time and ctx.start_time
        ]
        
        avg_execution_time = statistics.mean(execution_times) if execution_times else 0
        
        # Calculate success/error rates
        successful_executions = len([ctx for ctx in execution_history if ctx.state.value == "completed"])
        total_executions = len(execution_history)
        success_rate = successful_executions / total_executions if total_executions > 0 else 0
        error_rate = 1 - success_rate
        
        # Analyze step performance
        step_performance = self._analyze_step_performance(workflow, execution_history)
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(step_performance)
        
        # Calculate resource usage
        resource_usage = self._calculate_resource_usage(execution_history)
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            avg_execution_time, success_rate, step_performance, resource_usage
        )
        
        metrics = PerformanceMetrics(
            execution_time=avg_execution_time,
            resource_usage=resource_usage,
            success_rate=success_rate,
            error_rate=error_rate,
            step_performance=step_performance,
            bottlenecks=bottlenecks,
            optimization_score=optimization_score
        )
        
        # Store metrics for learning
        workflow_id = workflow.workflow_id
        if workflow_id not in self.performance_history:
            self.performance_history[workflow_id] = []
        
        self.performance_history[workflow_id].append(metrics)
        
        # Keep only recent history
        if len(self.performance_history[workflow_id]) > 100:
            self.performance_history[workflow_id] = self.performance_history[workflow_id][-100:]
        
        return metrics
    
    async def generate_optimization_recommendations(self, 
                                                  workflow: AdvancedWorkflow,
                                                  metrics: PerformanceMetrics) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on performance analysis."""
        
        recommendations = []
        
        # Apply optimization rules
        for rule in sorted(self.optimization_rules, key=lambda r: r["priority"], reverse=True):
            try:
                if rule["condition"](metrics):
                    recommendation = rule["recommendation"](workflow, metrics)
                    if recommendation:
                        recommendations.append(recommendation)
                        
            except Exception as e:
                logger.warning(f"Error applying optimization rule {rule['name']}: {e}")
        
        # Sort by expected improvement
        recommendations.sort(key=lambda r: r.expected_improvement, reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _analyze_step_performance(self, workflow: AdvancedWorkflow,
                                execution_history: List[ExecutionContext]) -> Dict[str, Dict[str, float]]:
        """Analyze individual step performance."""
        
        step_performance = {}
        
        for step in workflow.steps:
            step_times = []
            step_success_count = 0
            step_total_count = 0
            
            for ctx in execution_history:
                # Find step execution data in context
                step_data = ctx.step_execution_data.get(step.step_id)
                if step_data:
                    step_total_count += 1
                    
                    if step_data.get("success", False):
                        step_success_count += 1
                        
                        # Calculate execution time
                        start_time = step_data.get("start_time")
                        end_time = step_data.get("end_time")
                        
                        if start_time and end_time:
                            start_dt = datetime.fromisoformat(start_time)
                            end_dt = datetime.fromisoformat(end_time)
                            execution_time = (end_dt - start_dt).total_seconds()
                            step_times.append(execution_time)
            
            # Calculate step metrics
            if step_total_count > 0:
                step_performance[step.step_id] = {
                    "avg_execution_time": statistics.mean(step_times) if step_times else 0,
                    "max_execution_time": max(step_times) if step_times else 0,
                    "min_execution_time": min(step_times) if step_times else 0,
                    "success_rate": step_success_count / step_total_count,
                    "execution_count": step_total_count,
                    "variance": statistics.variance(step_times) if len(step_times) > 1 else 0
                }
        
        return step_performance
    
    def _identify_bottlenecks(self, step_performance: Dict[str, Dict[str, float]]) -> List[str]:
        """Identify performance bottlenecks in the workflow."""
        
        bottlenecks = []
        
        if not step_performance:
            return bottlenecks
        
        # Find steps with high execution times
        avg_times = [metrics["avg_execution_time"] for metrics in step_performance.values()]
        if avg_times:
            time_threshold = statistics.mean(avg_times) + statistics.stdev(avg_times)
            
            for step_id, metrics in step_performance.items():
                if metrics["avg_execution_time"] > time_threshold:
                    bottlenecks.append(step_id)
        
        # Find steps with high variance (inconsistent performance)
        for step_id, metrics in step_performance.items():
            if metrics["variance"] > metrics["avg_execution_time"] * 0.5:  # High variance
                if step_id not in bottlenecks:
                    bottlenecks.append(step_id)
        
        # Find steps with low success rates
        for step_id, metrics in step_performance.items():
            if metrics["success_rate"] < 0.95:  # Less than 95% success rate
                if step_id not in bottlenecks:
                    bottlenecks.append(step_id)
        
        return bottlenecks
    
    def _calculate_resource_usage(self, execution_history: List[ExecutionContext]) -> Dict[str, float]:
        """Calculate average resource usage."""
        
        resource_usage = {
            "cpu_utilization": 0.75,      # Mock data - in production, get from monitoring
            "memory_utilization": 0.60,
            "network_utilization": 0.30,
            "agent_utilization": 0.80
        }
        
        return resource_usage
    
    def _calculate_optimization_score(self, execution_time: float, success_rate: float,
                                    step_performance: Dict[str, Dict[str, float]],
                                    resource_usage: Dict[str, float]) -> float:
        """Calculate overall optimization score (0-100)."""
        
        score = 100
        
        # Penalize long execution times
        if execution_time > 300:  # More than 5 minutes
            score -= min(30, (execution_time - 300) / 10)
        
        # Penalize low success rates
        score -= (1 - success_rate) * 40
        
        # Penalize inefficient resource usage
        avg_resource_usage = statistics.mean(resource_usage.values()) if resource_usage else 0
        if avg_resource_usage > 0.8:  # High resource usage
            score -= (avg_resource_usage - 0.8) * 50
        
        # Penalize performance variance
        if step_performance:
            variances = [metrics["variance"] for metrics in step_performance.values()]
            avg_variance = statistics.mean(variances) if variances else 0
            score -= min(20, avg_variance * 10)
        
        return max(0, score)
    
    def _detect_parallelization_opportunity(self, metrics: PerformanceMetrics) -> bool:
        """Detect if workflow can benefit from parallelization."""
        
        # Check if there are sequential steps that could run in parallel
        long_running_steps = [
            step_id for step_id, perf in metrics.step_performance.items()
            if perf["avg_execution_time"] > 30  # More than 30 seconds
        ]
        
        return len(long_running_steps) >= 2
    
    def _detect_caching_opportunity(self, metrics: PerformanceMetrics) -> bool:
        """Detect if workflow can benefit from caching."""
        
        # Check for repeated operations or high execution times
        for step_id, perf in metrics.step_performance.items():
            if (perf["execution_count"] > 10 and  # Frequently executed
                perf["avg_execution_time"] > 5 and  # Takes significant time
                perf["variance"] < perf["avg_execution_time"] * 0.2):  # Consistent results
                return True
        
        return False
    
    def _detect_resource_waste(self, metrics: PerformanceMetrics) -> bool:
        """Detect if workflow is wasting resources."""
        
        avg_utilization = statistics.mean(metrics.resource_usage.values())
        return avg_utilization > 0.85  # Very high resource usage
    
    def _detect_retry_issues(self, metrics: PerformanceMetrics) -> bool:
        """Detect if retry policies need optimization."""
        
        return metrics.success_rate < 0.9  # Low success rate indicates retry issues
    
    def _detect_routing_inefficiency(self, metrics: PerformanceMetrics) -> bool:
        """Detect if agent routing can be optimized."""
        
        # Check for high variance in execution times (indicates inconsistent agent performance)
        for step_id, perf in metrics.step_performance.items():
            if perf["variance"] > perf["avg_execution_time"] * 0.3:
                return True
        
        return False
    
    def _create_parallelization_recommendation(self, workflow: AdvancedWorkflow,
                                             metrics: PerformanceMetrics) -> OptimizationRecommendation:
        """Create recommendation for parallelization."""
        
        return OptimizationRecommendation(
            recommendation_id=f"parallel_{workflow.workflow_id}_{int(datetime.now().timestamp())}",
            type="parallelization",
            description="Convert sequential steps to parallel execution to reduce overall execution time",
            expected_improvement=35.0,  # 35% improvement
            implementation_effort="medium",
            risk_level="low",
            specific_changes=[
                {
                    "action": "create_parallel_container",
                    "steps": list(metrics.bottlenecks[:3]),  # Top 3 bottleneck steps
                    "max_concurrent": 3
                }
            ]
        )
    
    def _create_caching_recommendation(self, workflow: AdvancedWorkflow,
                                     metrics: PerformanceMetrics) -> OptimizationRecommendation:
        """Create recommendation for caching."""
        
        return OptimizationRecommendation(
            recommendation_id=f"cache_{workflow.workflow_id}_{int(datetime.now().timestamp())}",
            type="caching",
            description="Implement result caching for frequently executed steps with consistent outputs",
            expected_improvement=25.0,
            implementation_effort="low",
            risk_level="low",
            specific_changes=[
                {
                    "action": "add_result_caching",
                    "steps": [step_id for step_id, perf in metrics.step_performance.items()
                             if perf["execution_count"] > 10],
                    "cache_ttl": 3600  # 1 hour
                }
            ]
        )
    
    def _create_resource_optimization_recommendation(self, workflow: AdvancedWorkflow,
                                                   metrics: PerformanceMetrics) -> OptimizationRecommendation:
        """Create recommendation for resource optimization."""
        
        return OptimizationRecommendation(
            recommendation_id=f"resource_{workflow.workflow_id}_{int(datetime.now().timestamp())}",
            type="resource_optimization",
            description="Optimize resource allocation and utilization to reduce costs and improve efficiency",
            expected_improvement=20.0,
            implementation_effort="medium",
            risk_level="medium",
            specific_changes=[
                {
                    "action": "adjust_resource_limits",
                    "target_utilization": 0.75,
                    "enable_autoscaling": True
                },
                {
                    "action": "implement_resource_pooling",
                    "pool_size": 5
                }
            ]
        )
    
    def _create_retry_optimization_recommendation(self, workflow: AdvancedWorkflow,
                                                metrics: PerformanceMetrics) -> OptimizationRecommendation:
        """Create recommendation for retry optimization."""
        
        return OptimizationRecommendation(
            recommendation_id=f"retry_{workflow.workflow_id}_{int(datetime.now().timestamp())}",
            type="retry_optimization",
            description="Optimize retry policies to improve success rates and reduce unnecessary retries",
            expected_improvement=15.0,
            implementation_effort="low",
            risk_level="low",
            specific_changes=[
                {
                    "action": "adjust_retry_policies",
                    "steps": [step_id for step_id, perf in metrics.step_performance.items()
                             if perf["success_rate"] < 0.95],
                    "max_retries": 5,
                    "backoff_multiplier": 1.5
                }
            ]
        )
    
    def _create_routing_optimization_recommendation(self, workflow: AdvancedWorkflow,
                                                  metrics: PerformanceMetrics) -> OptimizationRecommendation:
        """Create recommendation for routing optimization."""
        
        return OptimizationRecommendation(
            recommendation_id=f"routing_{workflow.workflow_id}_{int(datetime.now().timestamp())}",
            type="routing_optimization",
            description="Optimize agent routing based on performance history and current load",
            expected_improvement=18.0,
            implementation_effort="medium",
            risk_level="low",
            specific_changes=[
                {
                    "action": "implement_smart_routing",
                    "routing_algorithm": "performance_weighted",
                    "consider_agent_load": True,
                    "enable_failover": True
                }
            ]
        )
```

---

## 📝 Chapter Summary

Congratulations! You've built an enterprise-grade advanced workflow system with the following capabilities:

### Advanced Workflow Features Implemented

#### 🔄 **Complex Execution Patterns**

- ✅ **Parallel execution** with concurrent step processing and synchronization
- ✅ **Conditional branching** with dynamic routing based on data and context
- ✅ **Loop processing** with iterative execution and termination conditions
- ✅ **Hybrid workflows** combining multiple execution patterns

#### 🚀 **Performance Optimization**

- ✅ **Intelligent optimization** with automated performance analysis
- ✅ **Resource management** with efficient allocation and monitoring
- ✅ **Bottleneck detection** with automated identification and recommendations
- ✅ **Adaptive routing** based on agent performance and availability

#### 🛡️ **Enterprise Features**

- ✅ **Comprehensive error handling** with retry policies and rollback mechanisms
- ✅ **Workflow monitoring** with real-time metrics and observability
- ✅ **Input validation** with schema-based verification
- ✅ **Resource pooling** for efficient agent utilization

---

## 🧪 Testing Your Understanding

### Quick Check Questions

1. **What is the main advantage of parallel workflow execution?**
   - A) Simpler error handling
   - B) Reduced execution time through concurrency
   - C) Better resource management
   - D) Easier debugging

2. **How does conditional branching work in advanced workflows?**
   - A) Random selection between branches
   - B) User input determines the branch
   - C) Expression evaluation determines execution path
   - D) Time-based routing

3. **What triggers workflow optimization recommendations?**
   - A) Manual requests only
   - B) Performance analysis and pattern detection
   - C) Schedule-based analysis
   - D) Error thresholds

4. **How does the retry mechanism handle different error types?**
   - A) All errors are retried equally
   - B) Only timeout errors are retried
   - C) Retryable vs non-retryable errors are distinguished
   - D) No retry logic is implemented

5. **What is the purpose of workflow rollback mechanisms?**
   - A) Performance optimization
   - B) Undo changes when workflows fail
   - C) Agent load balancing
   - D) Error logging

### Practical Exercise

Create an intelligent document processing workflow:

```python
class DocumentProcessingWorkflow:
    """Advanced workflow for intelligent document processing."""
    
    def __init__(self, workflow_engine: AdvancedWorkflowEngine):
        self.engine = workflow_engine
    
    def create_document_workflow(self) -> AdvancedWorkflow:
        """Create a complex document processing workflow."""
        
        # TODO: Create workflow with:
        # 1. Parallel OCR and metadata extraction
        # 2. Conditional routing based on document type
        # 3. Loop for multi-page processing
        # 4. Error handling with human review fallback
        # 5. Quality validation with retry logic
        
        pass
```

**💡 Hint:** Check the [`Session8_Advanced_Agent_Workflows-solution.md`](Session8_Advanced_Agent_Workflows-solution.md) file for complete implementations and advanced patterns.

---

## Next Session Preview

In Session 9, we'll explore **Production Agent Deployment** including:
- Container orchestration for agent systems
- Scalable deployment architectures with Kubernetes
- Production monitoring and alerting
- Security and compliance in production environments

### Homework

1. **Implement workflow versioning** with backward compatibility
2. **Create dynamic workflow generation** from natural language descriptions
3. **Add machine learning optimization** using historical performance data
4. **Build workflow testing framework** for comprehensive validation

---

## Additional Resources

- [Workflow Orchestration Patterns](https://example.com/workflow-patterns)
- [Performance Optimization Techniques](https://example.com/perf-optimization)
- [Enterprise Workflow Architecture](https://example.com/enterprise-workflows)
- [Monitoring and Observability](https://example.com/monitoring)

Remember: Great workflows balance complexity with maintainability, providing powerful capabilities while remaining understandable and debuggable! 🔄⚡🎯