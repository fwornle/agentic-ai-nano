"""
Advanced Workflow Engine - Session 8
Sophisticated workflow orchestration with parallel processing and conditional logic.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StepType(Enum):
    """Types of workflow steps."""
    ACTION = "action"           # Execute an action
    CONDITION = "condition"     # Conditional branching
    PARALLEL = "parallel"       # Parallel execution
    LOOP = "loop"              # Iterative processing
    MERGE = "merge"            # Merge parallel results


class StepStatus(Enum):
    """Status of workflow steps."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class WorkflowState(Enum):
    """Overall workflow states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Enhanced workflow step with advanced capabilities."""
    
    # Basic properties
    id: str
    name: str
    type: StepType
    action: Optional[Callable] = None
    
    # Control flow
    dependencies: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    parallel_steps: List['WorkflowStep'] = field(default_factory=list)
    
    # Configuration
    timeout: int = 300
    retry_count: int = 3
    retry_delay: int = 5
    
    # Monitoring and observability
    metrics_enabled: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class AdvancedWorkflow:
    """Advanced workflow definition with complex patterns."""
    
    # Basic properties
    id: str
    name: str
    version: str
    steps: List[WorkflowStep]
    
    # Configuration
    timeout: int = 3600
    max_parallel: int = 10
    failure_strategy: str = "fail_fast"  # fail_fast, continue, retry
    
    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionContext:
    """Workflow execution context with state management."""
    
    workflow_id: str
    execution_id: str
    state: WorkflowState = WorkflowState.PENDING
    
    # Data flow
    input_data: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    step_status: Dict[str, StepStatus] = field(default_factory=dict)
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class StepExecutor:
    """Step executor with enhanced capabilities."""
    
    def __init__(self):
        self.registered_actions: Dict[str, Callable] = {}
    
    def register_action(self, name: str, action: Callable):
        """Register a custom action."""
        self.registered_actions[name] = action
    
    async def execute_step(self, step: WorkflowStep, 
                          context: ExecutionContext) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            logger.info(f"Executing step: {step.name} ({step.type.value})")
            
            if step.type == StepType.ACTION:
                return await self._execute_action_step(step, context)
            elif step.type == StepType.CONDITION:
                return await self._execute_condition_step(step, context)
            elif step.type == StepType.PARALLEL:
                return await self._execute_parallel_step(step, context)
            elif step.type == StepType.LOOP:
                return await self._execute_loop_step(step, context)
            elif step.type == StepType.MERGE:
                return await self._execute_merge_step(step, context)
            else:
                raise ValueError(f"Unknown step type: {step.type}")
        
        except Exception as e:
            logger.error(f"Step execution failed: {step.name} - {str(e)}")
            raise
    
    async def _execute_action_step(self, step: WorkflowStep, 
                                  context: ExecutionContext) -> Dict[str, Any]:
        """Execute an action step."""
        if step.action:
            return await step.action(context.step_results, context.variables)
        elif step.name in self.registered_actions:
            action = self.registered_actions[step.name]
            return await action(context.step_results, context.variables)
        else:
            # Default mock action for demonstration
            await asyncio.sleep(0.1)  # Simulate work
            return {"result": f"Action {step.name} completed", "timestamp": datetime.now().isoformat()}
    
    async def _execute_condition_step(self, step: WorkflowStep,
                                     context: ExecutionContext) -> Dict[str, Any]:
        """Execute a conditional step."""
        # Evaluate conditions based on context
        for condition_key, condition_value in step.conditions.items():
            if condition_key in context.variables:
                if context.variables[condition_key] == condition_value:
                    return {"condition_result": True, "matched_condition": condition_key}
        
        return {"condition_result": False, "matched_condition": None}
    
    async def _execute_parallel_step(self, step: WorkflowStep,
                                    context: ExecutionContext) -> Dict[str, Any]:
        """Execute parallel steps."""
        tasks = []
        for parallel_step in step.parallel_steps:
            task = asyncio.create_task(self.execute_step(parallel_step, context))
            tasks.append((parallel_step.id, task))
        
        results = {}
        for step_id, task in tasks:
            try:
                result = await task
                results[step_id] = result
            except Exception as e:
                results[step_id] = {"error": str(e)}
        
        return {"parallel_results": results}
    
    async def _execute_loop_step(self, step: WorkflowStep,
                                context: ExecutionContext) -> Dict[str, Any]:
        """Execute a loop step."""
        loop_results = []
        loop_count = step.conditions.get("max_iterations", 5)
        
        for i in range(loop_count):
            # Check termination condition
            if step.conditions.get("termination_condition"):
                condition_key = step.conditions["termination_condition"]
                if context.variables.get(condition_key):
                    break
            
            # Execute loop body (first parallel step as loop body)
            if step.parallel_steps:
                body_result = await self.execute_step(step.parallel_steps[0], context)
                loop_results.append({"iteration": i, "result": body_result})
            
            await asyncio.sleep(0.05)  # Prevent tight loops
        
        return {"loop_results": loop_results, "iterations": len(loop_results)}
    
    async def _execute_merge_step(self, step: WorkflowStep,
                                 context: ExecutionContext) -> Dict[str, Any]:
        """Execute a merge step to combine results."""
        merged_data = {}
        
        # Merge results from dependencies
        for dep_id in step.dependencies:
            if dep_id in context.step_results:
                dep_result = context.step_results[dep_id]
                if isinstance(dep_result, dict):
                    merged_data.update(dep_result)
                else:
                    merged_data[dep_id] = dep_result
        
        return {"merged_results": merged_data, "merge_count": len(step.dependencies)}


class WorkflowMonitor:
    """Workflow monitoring and metrics collection."""
    
    def __init__(self):
        self.execution_metrics: Dict[str, Dict[str, Any]] = {}
    
    def start_workflow_monitoring(self, execution_id: str):
        """Start monitoring a workflow execution."""
        self.execution_metrics[execution_id] = {
            "start_time": datetime.now(),
            "step_metrics": {},
            "performance_data": []
        }
    
    def record_step_execution(self, execution_id: str, step_id: str, 
                            duration: float, status: StepStatus):
        """Record step execution metrics."""
        if execution_id in self.execution_metrics:
            self.execution_metrics[execution_id]["step_metrics"][step_id] = {
                "duration": duration,
                "status": status.value,
                "timestamp": datetime.now().isoformat()
            }
    
    def end_workflow_monitoring(self, execution_id: str, final_state: WorkflowState):
        """End workflow monitoring and calculate final metrics."""
        if execution_id in self.execution_metrics:
            metrics = self.execution_metrics[execution_id]
            metrics["end_time"] = datetime.now()
            metrics["total_duration"] = (metrics["end_time"] - metrics["start_time"]).total_seconds()
            metrics["final_state"] = final_state.value
            metrics["step_count"] = len(metrics["step_metrics"])
    
    def get_execution_summary(self, execution_id: str) -> Dict[str, Any]:
        """Get execution summary for analysis."""
        if execution_id not in self.execution_metrics:
            return {}
        
        metrics = self.execution_metrics[execution_id]
        return {
            "execution_id": execution_id,
            "total_duration": metrics.get("total_duration", 0),
            "step_count": metrics.get("step_count", 0),
            "final_state": metrics.get("final_state", "unknown"),
            "step_performance": metrics.get("step_metrics", {})
        }


class AdvancedWorkflowEngine:
    """Advanced workflow engine with sophisticated execution patterns."""
    
    def __init__(self, step_executor: Optional[StepExecutor] = None, 
                 monitor: Optional[WorkflowMonitor] = None):
        self.step_executor = step_executor or StepExecutor()
        self.monitor = monitor or WorkflowMonitor()
        self.active_executions: Dict[str, ExecutionContext] = {}
    
    async def execute_workflow(self, workflow: AdvancedWorkflow, 
                             input_data: Dict[str, Any] = None,
                             execution_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow with advanced patterns."""
        execution_id = str(uuid.uuid4())
        context = ExecutionContext(
            workflow_id=workflow.id,
            execution_id=execution_id,
            input_data=input_data or {},
            state=WorkflowState.PENDING
        )
        
        self.active_executions[execution_id] = context
        
        try:
            # Start monitoring
            self.monitor.start_workflow_monitoring(execution_id)
            context.state = WorkflowState.RUNNING
            context.start_time = datetime.now()
            
            # Execute workflow with timeout
            result = await asyncio.wait_for(
                self._execute_workflow_internal(context, workflow),
                timeout=workflow.timeout
            )
            
            context.state = WorkflowState.COMPLETED
            context.end_time = datetime.now()
            
            # End monitoring
            self.monitor.end_workflow_monitoring(execution_id, WorkflowState.COMPLETED)
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "result": result,
                "execution_summary": self.monitor.get_execution_summary(execution_id)
            }
            
        except asyncio.TimeoutError:
            context.state = WorkflowState.TIMEOUT
            self.monitor.end_workflow_monitoring(execution_id, WorkflowState.TIMEOUT)
            return {
                "execution_id": execution_id,
                "status": "timeout",
                "error": f"Workflow timed out after {workflow.timeout} seconds"
            }
        except Exception as e:
            context.state = WorkflowState.FAILED
            context.errors.append(str(e))
            self.monitor.end_workflow_monitoring(execution_id, WorkflowState.FAILED)
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
                "execution_summary": self.monitor.get_execution_summary(execution_id)
            }
        finally:
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _execute_workflow_internal(self, context: ExecutionContext, 
                                       workflow: AdvancedWorkflow) -> Dict[str, Any]:
        """Internal workflow execution logic."""
        
        # Initialize step status
        for step in workflow.steps:
            context.step_status[step.id] = StepStatus.PENDING
        
        completed_steps = set()
        max_concurrent = workflow.max_parallel
        
        while len(completed_steps) < len(workflow.steps):
            # Find steps ready to execute
            ready_steps = self._find_ready_steps(workflow.steps, completed_steps, context)
            
            if not ready_steps:
                # Check if we're stuck
                pending_steps = [s for s in workflow.steps if s.id not in completed_steps]
                if pending_steps:
                    raise RuntimeError(f"Workflow stuck - cannot execute remaining steps: {[s.name for s in pending_steps]}")
                break
            
            # Execute ready steps with concurrency limit
            semaphore = asyncio.Semaphore(max_concurrent)
            execution_tasks = []
            
            for step in ready_steps[:max_concurrent]:
                context.step_status[step.id] = StepStatus.RUNNING
                task = asyncio.create_task(self._execute_step_with_monitoring(step, context, semaphore))
                execution_tasks.append((step, task))
            
            # Wait for tasks to complete
            for step, task in execution_tasks:
                try:
                    start_time = datetime.now()
                    result = await task
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    # Store results
                    context.step_results[step.id] = result
                    context.step_status[step.id] = StepStatus.COMPLETED
                    completed_steps.add(step.id)
                    
                    # Record metrics
                    self.monitor.record_step_execution(context.execution_id, step.id, duration, StepStatus.COMPLETED)
                    
                except Exception as e:
                    context.step_status[step.id] = StepStatus.FAILED
                    context.errors.append(f"Step {step.name} failed: {str(e)}")
                    
                    # Record failure metrics
                    self.monitor.record_step_execution(context.execution_id, step.id, 0, StepStatus.FAILED)
                    
                    # Handle failure based on strategy
                    if workflow.failure_strategy == "fail_fast":
                        raise RuntimeError(f"Workflow failed at step {step.name}: {str(e)}")
                    elif workflow.failure_strategy == "continue":
                        logger.warning(f"Step {step.name} failed, continuing: {str(e)}")
                        completed_steps.add(step.id)  # Mark as completed to continue
        
        return {
            "workflow_id": workflow.id,
            "execution_id": context.execution_id,
            "completed_steps": len(completed_steps),
            "total_steps": len(workflow.steps),
            "step_results": context.step_results,
            "execution_time": (datetime.now() - context.start_time).total_seconds() if context.start_time else 0
        }
    
    def _find_ready_steps(self, steps: List[WorkflowStep], 
                         completed_steps: set, context: ExecutionContext) -> List[WorkflowStep]:
        """Find steps ready for execution."""
        ready_steps = []
        
        for step in steps:
            if (step.id not in completed_steps and 
                context.step_status[step.id] != StepStatus.RUNNING and
                all(dep in completed_steps for dep in step.dependencies)):
                ready_steps.append(step)
        
        return ready_steps
    
    async def _execute_step_with_monitoring(self, step: WorkflowStep, 
                                          context: ExecutionContext,
                                          semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Execute step with concurrency control and monitoring."""
        async with semaphore:
            return await self.step_executor.execute_step(step, context)