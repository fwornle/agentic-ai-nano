# Session 6 - Module A: Advanced Composition Patterns (35 minutes)

**Prerequisites**: [Session 6 Core Section Complete](Session6_Atomic_Agents_Modular_Architecture.md)  
**Target Audience**: Implementers building sophisticated atomic systems  
**Cognitive Load**: 4 advanced concepts

---

## 🎯 Module Overview

This module explores sophisticated atomic agent composition patterns including pipeline orchestration, parallel processing, dynamic agent assembly, and CLI integration for DevOps workflows. You'll learn to build complex, maintainable systems from simple atomic components using proven architectural patterns.

### Learning Objectives

By the end of this module, you will:

- Design sequential and parallel agent pipelines with robust error handling
- Implement dynamic agent composition systems that adapt to runtime requirements
- Create CLI tools for atomic agent management and DevOps integration
- Build sophisticated context-aware agent orchestration systems

---

## Part 1: Agent Pipeline Orchestration (20 minutes)

### Sequential Processing Pipelines

🗂️ **File**: `src/session6/advanced_composition.py` - Sophisticated pipeline patterns

Complex atomic systems emerge from combining simple agents through well-designed composition patterns. Let's build this step by step, starting with the foundational imports and types.

### Step 1: Foundation - Imports and Type System

First, we establish the type system and imports that will power our sophisticated pipeline:

```python
from typing import List, Dict, Any, TypeVar, Generic, Optional, Callable, Protocol
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime
from enum import Enum
from atomic_schemas import TaskInput, TaskOutput, AnalysisInput, AnalysisOutput

T_Input = TypeVar('T_Input')
T_Output = TypeVar('T_Output')
T_Intermediate = TypeVar('T_Intermediate')
```

These type variables enable us to build type-safe pipelines that can handle any data transformation while maintaining compile-time checks.

### Step 2: Pipeline Behavior Enums

Next, we define the core enums that control pipeline behavior:

```python
class ErrorPolicy(Enum):
    """Pipeline error handling policies"""
    STOP = "stop"      # Stop pipeline on first error
    SKIP = "skip"      # Skip failed stage and continue
    RETRY = "retry"    # Retry failed stage with backoff

class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"      # Pipeline waiting to start
    RUNNING = "running"      # Pipeline currently executing
    SUCCESS = "success"      # Pipeline completed successfully
    FAILED = "failed"        # Pipeline failed
    CANCELLED = "cancelled"  # Pipeline was cancelled
```

These enums provide clear, type-safe ways to handle different execution scenarios and track pipeline state throughout its lifecycle.

### Step 3: Stage Configuration System

Now we build the configuration system that makes each pipeline stage configurable and resilient:

```python
@dataclass
class StageConfiguration:
    """Configuration for pipeline stage"""
    retry_count: int = 3
    timeout_seconds: int = 60
    error_policy: ErrorPolicy = ErrorPolicy.RETRY
    
    def __post_init__(self):
        if self.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
```

This configuration class encapsulates stage-level resilience settings. The validation in `__post_init__` ensures we never have invalid configurations that could break pipeline execution.

### Step 4: Pipeline Stage Definition

Next, we define what constitutes a single stage in our pipeline:

```python
@dataclass
class PipelineStage:
    """Definition of a pipeline processing stage"""
    stage_id: str
    agent: Any  # AtomicAgent instance
    stage_name: str
    description: str
    config: StageConfiguration = field(default_factory=StageConfiguration)
    
    def __post_init__(self):
        if not self.stage_id:
            raise ValueError("stage_id cannot be empty")
        if not self.stage_name:
            raise ValueError("stage_name cannot be empty")
```

Each stage wraps an atomic agent with metadata and configuration. This design allows us to treat any atomic agent as a pipeline component with consistent error handling and monitoring.

### Step 5: Pipeline Context and Error Tracking

The pipeline context acts as the "memory" of our pipeline, tracking everything that happens during execution:

```python
@dataclass
class PipelineContext:
    """Context passed through pipeline execution"""
    pipeline_id: str
    execution_start: datetime
    stage_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_log: List[Dict[str, Any]] = field(default_factory=list)
    status: PipelineStatus = PipelineStatus.PENDING
    
    def add_error(self, error: str, stage_id: Optional[str] = None):
        """Add error to error log with timestamp"""
        self.error_log.append({
            "error": error,
            "stage_id": stage_id,
            "timestamp": datetime.now().isoformat()
        })
```

This context object travels with the pipeline execution, collecting a complete audit trail. The `add_error` method ensures all errors are timestamped and trackable to specific stages.

### Step 6: Exception Handling and Protocols

We need proper exception handling and extensibility protocols:

```python
class PipelineExecutionException(Exception):
    """Exception raised during pipeline execution"""
    def __init__(self, message: str, stage_id: Optional[str] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.stage_id = stage_id
        self.original_error = original_error
```

This custom exception preserves context about where the failure occurred and what caused it, making debugging much easier.

### Step 7: Middleware and Metrics Protocols

Next, we define the protocols that make our pipeline extensible:

```python
class MiddlewareProtocol(Protocol):
    """Protocol for pipeline middleware"""
    async def __call__(self, data: Any, stage: PipelineStage, 
                      context: PipelineContext) -> Any:
        """Process data through middleware"""
        ...

class MetricsCollector(ABC):
    """Abstract base class for metrics collection"""
    
    @abstractmethod
    async def record_stage_execution(self, stage_id: str, duration: float, status: str):
        """Record stage execution metrics"""
        pass
    
    @abstractmethod
    async def record_pipeline_execution(self, pipeline_id: str, duration: float, status: str):
        """Record pipeline execution metrics"""
        pass
```

The middleware protocol allows you to inject cross-cutting concerns (logging, authentication, transformation) at any stage. The metrics collector ensures we can plug in any monitoring system.

### Step 8: Default Metrics Implementation

We provide a simple but effective default metrics collector:

```python
class DefaultMetricsCollector(MetricsCollector):
    """Default implementation of metrics collector"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger(__name__)
    
    async def record_stage_execution(self, stage_id: str, duration: float, status: str):
        """Record stage execution metrics"""
        if stage_id not in self.metrics:
            self.metrics[stage_id] = []
        self.metrics[stage_id].append({
            "duration": duration,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        self.logger.info(f"Stage {stage_id} completed in {duration:.2f}s with status {status}")
    
    async def record_pipeline_execution(self, pipeline_id: str, duration: float, status: str):
        """Record pipeline execution metrics"""
        self.logger.info(f"Pipeline {pipeline_id} completed in {duration:.2f}s with status {status}")
```

This implementation stores metrics in memory and logs to the standard logging system. In production, you might replace this with a system that sends to Prometheus, DataDog, or your monitoring platform of choice.

### Step 9: Pipeline Class Foundation

Now we build the main pipeline orchestrator, starting with its constructor and basic stage management:

```python
class AdvancedAtomicPipeline:
    """Sophisticated pipeline orchestration with SOLID principles adherence"""
    
    def __init__(self, pipeline_id: str, metrics_collector: Optional[MetricsCollector] = None):
        if not pipeline_id:
            raise ValueError("pipeline_id cannot be empty")
            
        self.pipeline_id = pipeline_id
        self._stages: List[PipelineStage] = []
        self._middleware_functions: List[MiddlewareProtocol] = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._metrics_collector = metrics_collector or DefaultMetricsCollector()
```

The constructor establishes the pipeline's identity and core components. Notice how we inject the metrics collector as a dependency, following the Dependency Inversion Principle.

### Step 10: Fluent Interface for Pipeline Building

Next, we add methods for building pipelines with a fluent interface:

```python
    def add_stage(self, stage: PipelineStage) -> 'AdvancedAtomicPipeline':
        """Add a processing stage to the pipeline"""
        if not isinstance(stage, PipelineStage):
            raise TypeError("stage must be an instance of PipelineStage")
        self._stages.append(stage)
        return self  # Enable fluent interface
    
    def add_middleware(self, middleware_func: MiddlewareProtocol) -> 'AdvancedAtomicPipeline':
        """Add middleware function for cross-cutting concerns"""
        self._middleware_functions.append(middleware_func)
        return self
    
    @property
    def stages(self) -> List[PipelineStage]:
        """Get read-only access to stages"""
        return self._stages.copy()
```

The fluent interface allows you to chain method calls: `pipeline.add_stage(stage1).add_stage(stage2).add_middleware(auth_middleware)`. This makes pipeline construction both readable and concise.

### Step 11: Main Pipeline Execution Logic

The heart of our pipeline is the execute method. Let's break it down into understandable parts:

```python
    async def execute(self, initial_input: Any, 
                     context: Optional[PipelineContext] = None) -> Dict[str, Any]:
        """Execute the complete pipeline with comprehensive monitoring"""
        
        # Set up execution context
        if context is None:
            context = PipelineContext(
                pipeline_id=self.pipeline_id,
                execution_start=datetime.now()
            )
        
        context.status = PipelineStatus.RUNNING
        pipeline_start_time = datetime.now()
```

We start by ensuring we have a proper execution context to track our pipeline's journey.

### Step 12: Stage Execution Loop Setup

Next comes the core execution loop setup and validation:

```python
        try:
            current_data = initial_input
            execution_results = []
            
            if not self._stages:
                raise PipelineExecutionException("Pipeline has no stages to execute")
            
            # Execute each stage in sequence
            for stage_index, stage in enumerate(self._stages):
                try:
                    stage_result = await self._execute_single_stage(
                        stage, current_data, context, stage_index
                    )
                    execution_results.append(stage_result)
```

This initializes the execution environment and begins processing each stage.

### Step 12b: Stage Result Processing

For each stage result, we handle success and error cases according to configured policies:

```python
                    # Handle stage result based on error policy
                    if stage_result["status"] == "success":
                        current_data = stage_result["output"]
                        await self._metrics_collector.record_stage_execution(
                            stage.stage_id, stage_result["execution_time"], "success"
                        )
                    elif stage_result["status"] == "error":
                        await self._metrics_collector.record_stage_execution(
                            stage.stage_id, stage_result["execution_time"], "error"
                        )
                        
                        if not await self._handle_stage_error(stage, stage_result, context):
                            # Error handling determined we should stop
                            context.status = PipelineStatus.FAILED
                            break
```

The loop processes each stage sequentially, handling success and error cases according to the configured error policies.

### Step 13: Pipeline Completion and Metrics

Finally, we handle pipeline completion and record comprehensive metrics:

```python
                except PipelineExecutionException as e:
                    context.add_error(str(e), e.stage_id)
                    if stage.config.error_policy != ErrorPolicy.SKIP:
                        context.status = PipelineStatus.FAILED
                        break
                        
            # Determine final status
            if context.status == PipelineStatus.RUNNING:
                context.status = PipelineStatus.SUCCESS
                
            # Record pipeline metrics
            total_execution_time = (datetime.now() - pipeline_start_time).total_seconds()
            await self._metrics_collector.record_pipeline_execution(
                self.pipeline_id, total_execution_time, context.status.value
            )
            
            return self._build_execution_result(
                current_data, execution_results, context, total_execution_time
            )
```

Notice how we ensure metrics are recorded even when exceptions occur, providing complete observability into pipeline behavior.

### Step 14: Exception Recovery

The pipeline also handles unexpected exceptions gracefully:

```python
        except Exception as e:
            context.status = PipelineStatus.FAILED
            context.add_error(f"Pipeline execution failed: {str(e)}")
            total_execution_time = (datetime.now() - pipeline_start_time).total_seconds()
            
            await self._metrics_collector.record_pipeline_execution(
                self.pipeline_id, total_execution_time, "failed"
            )
            
            raise PipelineExecutionException(
                f"Pipeline {self.pipeline_id} execution failed", 
                original_error=e
            )
```

This ensures that even unexpected failures are properly logged and reported with metrics.

### Step 15: Single Stage Execution with Middleware

Each stage execution involves middleware processing and detailed tracking:

```python
    async def _execute_single_stage(self, stage: PipelineStage, input_data: Any, 
                                   context: PipelineContext, stage_index: int) -> Dict[str, Any]:
        """Execute a single pipeline stage with middleware and error handling"""
        stage_start_time = datetime.now()
        current_data = input_data
        
        try:
            # Apply middleware before stage execution
            for middleware in self._middleware_functions:
                current_data = await middleware(current_data, stage, context)
            
            # Execute stage with resilience
            stage_result = await self._execute_stage_with_resilience(
                stage, current_data, context
            )
```

The middleware chain allows for cross-cutting concerns like authentication, logging, or data transformation to be applied consistently across all stages.

### Step 16: Stage Result Recording and Error Handling

We maintain detailed records of each stage execution:

```python
            # Record stage execution with comprehensive metrics
            stage_duration = (datetime.now() - stage_start_time).total_seconds()
            
            stage_record = {
                "stage_index": stage_index,
                "stage_id": stage.stage_id,
                "stage_name": stage.stage_name,
                "execution_time": stage_duration,
                "status": stage_result.get("status", "unknown"),
                "input_size": len(str(current_data)),
                "output_size": len(str(stage_result.get("output", ""))),
                "timestamp": stage_start_time.isoformat(),
                "output": stage_result.get("output"),
                "error": stage_result.get("error")
            }
            
            context.stage_history.append(stage_record)
            return stage_record
```

Every stage execution, successful or failed, is recorded with timing and size metrics. This provides valuable insights for optimization and debugging.

### Step 17: Stage Exception Handling

Even when individual stages fail, we capture comprehensive error information:

```python
        except Exception as e:
            # Even failures get recorded for debugging
            stage_duration = (datetime.now() - stage_start_time).total_seconds()
            error_record = {
                "stage_index": stage_index,
                "stage_id": stage.stage_id,
                "stage_name": stage.stage_name,
                "execution_time": stage_duration,
                "status": "error",
                "error": str(e),
                "timestamp": stage_start_time.isoformat()
            }
            context.stage_history.append(error_record)
            raise PipelineExecutionException(
                f"Stage {stage.stage_id} execution failed: {str(e)}", 
                stage_id=stage.stage_id, 
                original_error=e
            )
```

This detailed error recording helps with debugging and understanding where pipeline failures occur.

### Step 18: Error Policy Implementation

How we handle stage failures depends on the configured error policy:

```python
    async def _handle_stage_error(self, stage: PipelineStage, stage_result: Dict[str, Any], 
                                 context: PipelineContext) -> bool:
        """Handle stage error based on error policy. Returns True if pipeline should continue."""
        error_policy = stage.config.error_policy
        
        if error_policy == ErrorPolicy.STOP:
            self.logger.error(f"Pipeline stopped due to stage {stage.stage_id} failure")
            return False
        elif error_policy == ErrorPolicy.SKIP:
            self.logger.warning(f"Skipping failed stage: {stage.stage_id}")
            return True
        elif error_policy == ErrorPolicy.RETRY:
            # Retries are handled in _execute_stage_with_resilience
            self.logger.error(f"Stage {stage.stage_id} failed after retries")
            return False
        
        return False
```

This method implements the three error policies: STOP halts the pipeline, SKIP continues to the next stage, and RETRY attempts the stage again with exponential backoff.

### Step 19: Results Assembly

After pipeline execution, we assemble a comprehensive result object:

```python
    def _build_execution_result(self, final_output: Any, execution_results: List[Dict[str, Any]], 
                               context: PipelineContext, total_execution_time: float) -> Dict[str, Any]:
        """Build the final execution result"""
        return {
            "pipeline_id": self.pipeline_id,
            "final_output": final_output,
            "status": context.status.value,
            "execution_summary": {
                "total_stages": len(self._stages),
                "successful_stages": len([r for r in execution_results if r["status"] == "success"]),
                "failed_stages": len([r for r in execution_results if r["status"] == "error"]),
                "total_execution_time": total_execution_time,
                "average_stage_time": total_execution_time / len(self._stages) if self._stages else 0
            },
            "stage_details": execution_results,
            "context": context,
            "performance_metrics": self._calculate_performance_metrics(execution_results)
        }
```

This result object provides everything needed for monitoring, debugging, and optimization - from high-level success metrics to detailed stage-by-stage execution data.

### Step 20: Resilient Stage Execution with Retries

The most sophisticated part of our pipeline is the resilient execution system:

```python
    async def _execute_stage_with_resilience(self, stage: PipelineStage, 
                                           input_data: Any, 
                                           context: PipelineContext) -> Dict[str, Any]:
        """Execute stage with retry logic and timeout handling"""
        
        retry_count = stage.config.retry_count
        timeout_seconds = stage.config.timeout_seconds
        last_error = None
        
        # Retry loop with exponential backoff
        for attempt in range(retry_count):
            try:
                # Execute stage with timeout protection
                stage_task = asyncio.create_task(stage.agent.process(input_data))
                output = await asyncio.wait_for(stage_task, timeout=timeout_seconds)
                
                if attempt > 0:
                    self.logger.info(f"Stage {stage.stage_id} succeeded on attempt {attempt + 1}")
                
                return {
                    "status": "success",
                    "output": output,
                    "attempt": attempt + 1,
                    "retry_needed": attempt > 0
                }
```

The retry mechanism uses `asyncio.wait_for` to enforce timeouts and tracks which attempt succeeded.

### Step 21: Timeout Handling in Retries

When timeout errors occur during retry attempts, we handle them gracefully:

```python
            except asyncio.TimeoutError as e:
                last_error = e
                error_msg = f"Stage {stage.stage_id} timed out after {timeout_seconds}s"
                self.logger.warning(f"{error_msg} (attempt {attempt + 1}/{retry_count})")
                
                if attempt == retry_count - 1:  # Last attempt
                    context.add_error(error_msg, stage.stage_id)
                    return {
                        "status": "error",
                        "error": error_msg,
                        "error_type": "timeout",
                        "attempt": attempt + 1,
                        "retry_exhausted": True
                    }
```

Timeout errors are logged with detailed context about which attempt failed and why.

### Step 21b: General Exception Handling in Retries

For all other exceptions, we provide comprehensive error tracking:

```python
            except Exception as e:
                last_error = e
                error_msg = f"Stage {stage.stage_id} failed: {str(e)}"
                self.logger.warning(f"{error_msg} (attempt {attempt + 1}/{retry_count})")
                
                if attempt == retry_count - 1:  # Last attempt
                    context.add_error(error_msg, stage.stage_id)
                    return {
                        "status": "error",
                        "error": error_msg,
                        "error_type": type(e).__name__,
                        "attempt": attempt + 1,
                        "retry_exhausted": True
                    }
```

Each retry attempt is logged, and we distinguish between timeout errors and other exceptions for better debugging.

### Step 22: Exponential Backoff Implementation

The retry system implements exponential backoff to avoid overwhelming failing services:

```python
            # Exponential backoff before retry
            if attempt < retry_count - 1:  # Don't wait after last attempt
                backoff_time = min(2 ** attempt, 10)  # Max 10 seconds
                self.logger.debug(f"Waiting {backoff_time}s before retry {attempt + 2}")
                await asyncio.sleep(backoff_time)
        
        # Safety net (should never be reached)
        return {
            "status": "error", 
            "error": f"Unexpected retry loop exit: {str(last_error)}" if last_error else "Unknown error",
            "retry_exhausted": True
        }
```

The exponential backoff (2^attempt seconds, capped at 10) prevents overwhelming failing services while giving them time to recover.

### Step 23: Parallel Processing Foundation

Now let's build the parallel processing capabilities. We start with configuration and result classes:

```python
class ConcurrencyConfiguration:
    """Configuration for parallel processing"""
    
    def __init__(self, max_concurrent: int = 5, timeout_seconds: int = 300):
        if max_concurrent <= 0:
            raise ValueError("max_concurrent must be positive")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
            
        self.max_concurrent = max_concurrent
        self.timeout_seconds = timeout_seconds
```

This configuration class controls the concurrency limits, preventing resource exhaustion while maximizing throughput.

### Step 24: Batch Result Analytics

The BatchResult class provides rich analytics for parallel executions:

```python
class BatchResult:
    """Result of batch processing operation"""
    
    def __init__(self, batch_id: str, results: List[Any], metrics: Dict[str, Any]):
        self.batch_id = batch_id
        self.results = results
        self.metrics = metrics
        self.timestamp = datetime.now()
    
    @property
    def success_count(self) -> int:
        """Count of successful results"""
        return len([r for r in self.results if not isinstance(r, Exception) and r.get("status") == "success"])
    
    @property
    def failure_count(self) -> int:
        """Count of failed results"""
        return len(self.results) - self.success_count
    
    @property
    def success_rate(self) -> float:
        """Success rate as a percentage"""
        if not self.results:
            return 0.0
        return self.success_count / len(self.results)
```

These computed properties provide instant insights into batch execution quality without needing to manually calculate success rates.

### Step 25: Parallel Processor Setup

The ParallelAtomicProcessor handles concurrent execution of multiple agents:

```python
class ParallelAtomicProcessor:
    """Advanced parallel processing with load balancing and fault tolerance"""
    
    def __init__(self, config: ConcurrencyConfiguration, 
                 metrics_collector: Optional[MetricsCollector] = None):
        self._config = config
        self._semaphore = asyncio.Semaphore(config.max_concurrent)
        self._metrics_collector = metrics_collector or DefaultMetricsCollector()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
```

The semaphore is the key to controlling concurrency - it ensures we never exceed the configured maximum concurrent agents, preventing resource exhaustion.

### Step 26: Batch Processing Orchestration

The main batch processing method coordinates parallel execution:

```python
    async def process_batch(self, agent_input_pairs: List[tuple], 
                          batch_context: Optional[Dict[str, Any]] = None) -> BatchResult:
        """Process multiple agent-input pairs with sophisticated load balancing"""
        
        if not agent_input_pairs:
            raise ValueError("agent_input_pairs cannot be empty")
        
        # Set up batch context with unique ID
        if batch_context is None:
            batch_context = {"batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}
        
        batch_id = batch_context["batch_id"]
        batch_start_time = datetime.now()
```

We start by establishing the batch context and timing.

### Step 27: Task Creation and Execution

Next, we create and execute all tasks in parallel:

```python
        try:
            # Create processing tasks with semaphore control
            tasks = [
                self._process_with_semaphore(agent, input_data, f"task_{i}", batch_context)
                for i, (agent, input_data) in enumerate(agent_input_pairs)
            ]
            
            # Execute all tasks with timeout and progress monitoring
            results = await asyncio.wait_for(
                self._execute_with_monitoring(tasks, batch_context),
                timeout=self._config.timeout_seconds
            )
            
            # Calculate comprehensive batch metrics
            batch_duration = (datetime.now() - batch_start_time).total_seconds()
            metrics = self._calculate_batch_metrics(results, batch_duration, len(agent_input_pairs))
            
            # Record successful batch execution
            await self._metrics_collector.record_pipeline_execution(
                batch_id, batch_duration, "success" if metrics["success_rate"] > 0.5 else "failed"
            )
            
            return BatchResult(batch_id, results, metrics)
```

All tasks are created upfront and then executed with monitoring and timeout protection.

### Step 28: Batch Error Handling

We handle various failure scenarios gracefully:

```python
        except asyncio.TimeoutError:
            batch_duration = (datetime.now() - batch_start_time).total_seconds()
            await self._metrics_collector.record_pipeline_execution(
                batch_id, batch_duration, "timeout"
            )
            raise PipelineExecutionException(
                f"Batch {batch_id} timed out after {self._config.timeout_seconds}s"
            )
        except Exception as e:
            batch_duration = (datetime.now() - batch_start_time).total_seconds()
            await self._metrics_collector.record_pipeline_execution(
                batch_id, batch_duration, "error"
            )
            raise PipelineExecutionException(
                f"Batch {batch_id} execution failed: {str(e)}", 
                original_error=e
            )
```

Even when batches fail, we ensure metrics are recorded for observability.

### Step 29: Semaphore-Controlled Task Execution

Each individual task executes within semaphore constraints:

```python
    async def _process_with_semaphore(self, agent: Any, input_data: Any, 
                                    task_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process single agent with semaphore-controlled concurrency"""
        
        async with self._semaphore:
            task_start_time = datetime.now()
            
            try:
                result = await agent.process(input_data)
                task_duration = (datetime.now() - task_start_time).total_seconds()
                
                # Record individual task success
                await self._metrics_collector.record_stage_execution(
                    task_id, task_duration, "success"
                )
                
                return {
                    "task_id": task_id,
                    "status": "success",
                    "result": result,
                    "execution_time": task_duration,
                    "agent_id": getattr(agent, 'agent_id', 'unknown'),
                    "timestamp": task_start_time.isoformat()
                }
```

The `async with self._semaphore:` ensures only the configured number of agents run concurrently, preventing resource exhaustion.

### Step 30: Task-Level Error Handling

Individual task failures are handled gracefully:

```python
            except Exception as e:
                task_duration = (datetime.now() - task_start_time).total_seconds()
                self.logger.error(f"Task {task_id} failed: {str(e)}")
                
                # Record individual task failure for monitoring
                await self._metrics_collector.record_stage_execution(
                    task_id, task_duration, "error"
                )
                
                return {
                    "task_id": task_id,
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time": task_duration,
                    "agent_id": getattr(agent, 'agent_id', 'unknown'),
                    "timestamp": task_start_time.isoformat()
                }
```

Task failures don't stop the batch - they're recorded and the batch continues with other tasks.

### Step 31: Progress Monitoring and Completion Tracking

The monitoring system provides real-time feedback on batch progress:

```python
    async def _execute_with_monitoring(self, tasks: List, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute tasks with progress monitoring and graceful error handling"""
        
        results = []
        completed = 0
        total_tasks = len(tasks)
        
        # Log batch start for observability
        self.logger.info(f"Starting batch execution of {total_tasks} tasks with max concurrency {self._config.max_concurrent}")
        
        # Use asyncio.as_completed for real-time progress monitoring
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                results.append(result)
                completed += 1
                
                # Log progress at 10% intervals
                if completed % max(1, total_tasks // 10) == 0 or completed == total_tasks:
                    progress = (completed / total_tasks) * 100
                    self.logger.info(f"Batch progress: {completed}/{total_tasks} ({progress:.1f}%)")
```

The `asyncio.as_completed` approach gives us results as soon as they're available, rather than waiting for all tasks to complete.

### Step 32: Graceful Error Handling in Batch Processing

Even when individual tasks fail, the batch continues:

```python
            except Exception as e:
                # Create error result for failed tasks
                error_result = {
                    "task_id": f"unknown_task_{completed}",
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
                results.append(error_result)
                completed += 1
                self.logger.error(f"Task failed in batch: {str(e)}")
        
        return results
```

This ensures one failing task doesn't bring down the entire batch operation.

### Step 33: Comprehensive Batch Metrics Calculation

We calculate detailed metrics to understand batch performance:

```python
    def _calculate_batch_metrics(self, results: List[Dict[str, Any]], 
                                batch_duration: float, total_tasks: int) -> Dict[str, Any]:
        """Calculate comprehensive batch execution metrics"""
        
        successful_tasks = len([r for r in results if r.get("status") == "success"])
        failed_tasks = len(results) - successful_tasks
        
        # Calculate timing metrics for performance analysis
        execution_times = [r.get("execution_time", 0.0) for r in results if "execution_time" in r]
        avg_task_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0.0,
            "batch_duration": batch_duration,
            "average_task_time": avg_task_time,
            "concurrency_used": min(total_tasks, self._config.max_concurrent),
            "throughput_tasks_per_second": total_tasks / batch_duration if batch_duration > 0 else 0.0,
            "efficiency": (successful_tasks / total_tasks) * (avg_task_time / batch_duration) if batch_duration > 0 and total_tasks > 0 else 0.0
        }
```

These metrics help you understand not just whether the batch succeeded, but how efficiently it used resources and where optimization opportunities might exist.

### Step 34: Pipeline Performance Analytics

Finally, we provide comprehensive performance analytics for pipeline optimization:

```python
    def _calculate_performance_metrics(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics for pipeline execution"""
        
        if not execution_results:
            return {"error": "No execution results to analyze"}
        
        execution_times = [r.get("execution_time", 0.0) for r in execution_results]
        successful_stages = [r for r in execution_results if r.get("status") == "success"]
        
        return {
            "total_stages": len(execution_results),
            "successful_stages": len(successful_stages),
            "failure_rate": (len(execution_results) - len(successful_stages)) / len(execution_results),
            "average_stage_time": sum(execution_times) / len(execution_times) if execution_times else 0.0,
            "min_stage_time": min(execution_times) if execution_times else 0.0,
            "max_stage_time": max(execution_times) if execution_times else 0.0,
            "total_execution_time": sum(execution_times),
            "stage_efficiency": len(successful_stages) / len(execution_results) if execution_results else 0.0
        }
```

These metrics help identify bottlenecks, optimize resource allocation, and improve overall pipeline performance.

---

## Part 2: Dynamic Agent Assembly and CLI Integration (15 minutes)

### Runtime Agent Composition

🗂️ **File**: `src/session6/dynamic_assembly.py` - Runtime composition systems

Dynamic agent assembly allows us to build pipelines at runtime based on capabilities and requirements. Let's explore this powerful concept step by step.

### Step 35: Foundation - Capability System

First, we establish the capability framework that enables intelligent agent selection:

```python
from typing import Dict, List, Any, Type, Optional
import importlib
import inspect
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json

class AgentCapability(Enum):
    """Standard atomic agent capabilities"""
    TASK_PROCESSING = "task_processing"           # General task execution
    CONTENT_ANALYSIS = "content_analysis"         # Text/content analysis
    DATA_TRANSFORMATION = "data_transformation"   # Data format conversion
    COMMUNICATION = "communication"               # External system interaction
    VALIDATION = "validation"                     # Data/result validation
    REPORTING = "reporting"                       # Report generation
```

This capability system allows the dynamic assembly to understand what each agent can do, enabling intelligent pipeline construction.

### Step 36: Agent Definition Schema

Next, we define how agents are described for dynamic instantiation:

```python
@dataclass
class AgentDefinition:
    """Runtime agent definition"""
    agent_class: str                             # Class name to instantiate
    module_path: str                             # Python module path
    capabilities: List[AgentCapability]          # What this agent can do
    input_schema: str                            # Expected input format
    output_schema: str                           # Produced output format
    configuration: Dict[str, Any]                # Default configuration
    resource_requirements: Dict[str, Any]        # Resource needs (memory, CPU)
```

This definition acts as a "recipe" for creating agent instances, including everything needed for instantiation and compatibility checking.

### Step 37: Dynamic Agent Registry Setup

The registry acts as a smart catalog of available agents with sophisticated indexing:

```python
class DynamicAgentRegistry:
    """Registry for dynamic agent discovery and instantiation"""
    
    def __init__(self):
        self.registered_agents: Dict[str, AgentDefinition] = {}
        self.capability_index: Dict[AgentCapability, List[str]] = {}
        self.schema_compatibility: Dict[str, List[str]] = {}
```

The registry maintains three key data structures: the main agent definitions, capability-based indexing for fast lookup, and schema compatibility mapping for pipeline chaining.

### Step 38: Intelligent Agent Registration

Agent registration builds multiple indices for efficient discovery:

```python
    def register_agent(self, agent_id: str, definition: AgentDefinition):
        """Register an agent definition for dynamic instantiation"""
        
        self.registered_agents[agent_id] = definition
        
        # Build capability-based index for fast lookup
        for capability in definition.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = []
            self.capability_index[capability].append(agent_id)
        
        # Build schema compatibility index
        output_schema = definition.output_schema
        if output_schema not in self.schema_compatibility:
            self.schema_compatibility[output_schema] = []
        
        # Find agents that can consume this agent's output
        for other_id, other_def in self.registered_agents.items():
            if other_def.input_schema == output_schema:
                self.schema_compatibility[output_schema].append(other_id)
```

The indexing system enables O(1) lookup by capability and automatic discovery of compatible agent chains.

### Step 39: Agent Discovery Methods

The registry provides multiple ways to find agents based on different criteria:

```python
    def find_agents_by_capability(self, capability: AgentCapability) -> List[str]:
        """Find all agents with specified capability"""
        return self.capability_index.get(capability, [])
    
    def find_compatible_agents(self, output_schema: str) -> List[str]:
        """Find agents compatible with given output schema"""
        return self.schema_compatibility.get(output_schema, [])
```

These methods enable capability-driven and schema-driven agent discovery, essential for automatic pipeline construction.

### Step 40: Dynamic Agent Instantiation

The registry can instantiate agents at runtime with custom configuration:

```python
    async def instantiate_agent(self, agent_id: str, 
                               configuration_overrides: Dict[str, Any] = None) -> Any:
        """Dynamically instantiate an agent from its definition"""
        
        if agent_id not in self.registered_agents:
            raise ValueError(f"Agent {agent_id} not registered")
        
        definition = self.registered_agents[agent_id]
        
        # Load agent class dynamically using Python's import system
        module = importlib.import_module(definition.module_path)
        agent_class = getattr(module, definition.agent_class)
        
        # Merge default config with runtime overrides
        config = definition.configuration.copy()
        if configuration_overrides:
            config.update(configuration_overrides)
        
        # Create and return the agent instance
        return agent_class(**config)
```

This method demonstrates the power of Python's reflection capabilities - we can instantiate any class at runtime given its module path and name.

### Step 41: Intelligent Pipeline Suggestion

The registry can automatically suggest pipeline configurations based on desired capabilities:

```python
    def suggest_pipeline(self, start_capability: AgentCapability, 
                        end_capability: AgentCapability) -> List[List[str]]:
        """Suggest agent pipeline from start to end capability"""
        
        start_agents = self.find_agents_by_capability(start_capability)
        end_agents = self.find_agents_by_capability(end_capability)
        
        pipeline_suggestions = []
        
        # Try direct two-agent pipelines first
        for start_agent_id in start_agents:
            start_def = self.registered_agents[start_agent_id]
            compatible_agents = self.find_compatible_agents(start_def.output_schema)
            
            for middle_agent_id in compatible_agents:
                middle_def = self.registered_agents[middle_agent_id]
                if end_capability in middle_def.capabilities:
                    pipeline_suggestions.append([start_agent_id, middle_agent_id])
```

This algorithm starts with simple two-agent pipelines, trying to connect start and end capabilities directly.

### Step 42: Three-Agent Pipeline Discovery

If direct connections aren't possible, we expand to three-agent pipelines:

```python
                else:
                    # Try three-agent pipelines if direct connection isn't possible
                    final_compatible = self.find_compatible_agents(middle_def.output_schema)
                    for end_agent_id in final_compatible:
                        end_def = self.registered_agents[end_agent_id]
                        if end_capability in end_def.capabilities:
                            pipeline_suggestions.append([start_agent_id, middle_agent_id, end_agent_id])
        
        return pipeline_suggestions
```

This breadth-first approach finds the shortest possible pipelines that connect start and end capabilities. More sophisticated graph algorithms could be implemented for complex scenarios.

### Step 43: CLI Foundation

Now let's build the CLI system that makes dynamic assembly accessible to DevOps teams:

```python
class AtomicCLI:
    """Advanced CLI for atomic agent management and DevOps integration"""
    
    def __init__(self, config_path: str = "atomic_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.agent_registry = DynamicAgentRegistry()
        self.logger = logging.getLogger(__name__)
```

The CLI provides a user-friendly interface for managing atomic agents in production environments, bridging the gap between code and operations.

### Step 44: Configuration Management

The CLI uses a sophisticated configuration system with sensible defaults:

```python
    def _load_config(self) -> Dict[str, Any]:
        """Load atomic agent configuration with schema validation"""
        
        # Define comprehensive default configuration
        default_config = {
            "agents": {},                    # Registered agent definitions
            "pipelines": {},                # Saved pipeline configurations
            "providers": {},                # External service providers
            "cli_settings": {
                "log_level": "INFO",
                "output_format": "json",
                "auto_save": True
            },
            "monitoring": {
                "enabled": True,
                "metrics_retention_days": 7,
                "performance_alerts": True
            }
        }
```

This comprehensive default configuration ensures the CLI works out-of-the-box for common scenarios.

### Step 45: Configuration Loading and Error Handling

The configuration system handles missing files and parsing errors gracefully:

```python
        # Load existing config or use defaults
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                return default_config
        else:
            return default_config
```

This ensures the CLI is resilient to configuration issues and always starts with valid defaults.

### Step 46: Built-in Agent Registration

The CLI comes with pre-configured agents for common use cases:

```python
    def register_builtin_agents(self):
        """Register common atomic agent types"""
        
        # Task Processing Agent - General purpose task execution
        self.agent_registry.register_agent("task_processor", AgentDefinition(
            agent_class="TaskProcessorAgent",
            module_path="atomic_agents.task_processor",
            capabilities=[AgentCapability.TASK_PROCESSING],
            input_schema="TaskInput",
            output_schema="TaskOutput",
            configuration={"model": "gpt-4o-mini", "temperature": 0.3},
            resource_requirements={"memory_mb": 512, "cpu_cores": 1}
        ))
```

Task processing agents handle general-purpose work with balanced model settings.

### Step 47: Content Analysis Agent Registration

The content analyzer is specialized for text analysis tasks:

```python
        # Content Analysis Agent - Specialized for text analysis
        self.agent_registry.register_agent("content_analyzer", AgentDefinition(
            agent_class="ContentAnalysisAgent",
            module_path="atomic_agents.content_analysis",
            capabilities=[AgentCapability.CONTENT_ANALYSIS],
            input_schema="AnalysisInput",
            output_schema="AnalysisOutput",
            configuration={"model": "gpt-4o", "temperature": 0.1},
            resource_requirements={"memory_mb": 1024, "cpu_cores": 1}
        ))
```

Notice the lower temperature (0.1) for more consistent analysis results.

### Step 48: Data Transformation Agent Registration

The data transformer handles format conversions with deterministic settings:

```python
        # Data Transformer Agent - Format conversion and transformation
        self.agent_registry.register_agent("data_transformer", AgentDefinition(
            agent_class="DataTransformerAgent",
            module_path="atomic_agents.data_transformer",
            capabilities=[AgentCapability.DATA_TRANSFORMATION],
            input_schema="TransformInput",
            output_schema="TransformOutput",
            configuration={"model": "gpt-4o-mini", "temperature": 0.0},
            resource_requirements={"memory_mb": 256, "cpu_cores": 1}
        ))
```

Temperature 0.0 ensures deterministic transformations, crucial for data consistency.

### Step 49: Dynamic Pipeline Creation Setup

The most powerful feature - creating pipelines automatically from capability requirements:

```python
    async def create_dynamic_pipeline(self, capability_sequence: List[AgentCapability]) -> AdvancedAtomicPipeline:
        """Create pipeline dynamically based on capability requirements"""
        
        if len(capability_sequence) < 2:
            raise ValueError("Pipeline requires at least 2 capabilities")
        
        pipeline = AdvancedAtomicPipeline(f"dynamic_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Step 1: Find compatible agents for each capability
        selected_agents = []
        for i, capability in enumerate(capability_sequence):
            candidates = self.agent_registry.find_agents_by_capability(capability)
            
            if not candidates:
                raise ValueError(f"No agents found for capability: {capability}")
            
            # Select best agent (could use more sophisticated selection logic)
            selected_agent_id = candidates[0]  # Simple: pick first
```

The dynamic pipeline creation starts by finding agents that match each required capability.

### Step 50: Schema Compatibility Validation

We ensure the selected agents can work together:

```python
            # Step 2: Validate schema compatibility with previous agent
            if i > 0:
                prev_agent_def = self.agent_registry.registered_agents[selected_agents[-1]]
                current_agent_def = self.agent_registry.registered_agents[selected_agent_id]
                
                if prev_agent_def.output_schema != current_agent_def.input_schema:
                    # Try to find compatible agent
                    compatible_agents = self.agent_registry.find_compatible_agents(prev_agent_def.output_schema)
                    capability_compatible = [
                        agent_id for agent_id in compatible_agents
                        if capability in self.agent_registry.registered_agents[agent_id].capabilities
                    ]
                    
                    if capability_compatible:
                        selected_agent_id = capability_compatible[0]
                    else:
                        raise ValueError(f"No schema-compatible agents found for {capability}")
            
            selected_agents.append(selected_agent_id)
```

This ensures data can flow properly between pipeline stages.

### Step 51: Pipeline Assembly and Stage Creation

Finally, we instantiate agents and build the complete pipeline:

```python
        # Step 3: Instantiate agents and build pipeline
        for i, agent_id in enumerate(selected_agents):
            agent_instance = await self.agent_registry.instantiate_agent(agent_id)
            
            stage = PipelineStage(
                stage_id=f"stage_{i}_{agent_id}",
                agent=agent_instance,
                stage_name=f"Stage {i+1}: {agent_id}",
                description=f"Process using {agent_id} agent",
                config=StageConfiguration(error_policy=ErrorPolicy.RETRY, retry_count=2)
            )
            
            pipeline.add_stage(stage)
        
        return pipeline
```

This method demonstrates the full power of dynamic composition - from capability requirements to a fully functional pipeline, all generated automatically with schema validation and error handling.

---

## 🎯 Module Summary

You've now mastered advanced atomic agent composition patterns:

✅ **Pipeline Orchestration**: Built sophisticated sequential processing with error handling and monitoring  
✅ **Parallel Processing**: Implemented load-balanced parallel execution with fault tolerance  
✅ **Dynamic Assembly**: Created runtime agent composition systems with capability-based selection  
✅ **CLI Integration**: Designed DevOps-friendly command-line tools for atomic agent management

---

## 📝 Multiple Choice Test - Module A

Test your understanding of advanced atomic agent composition patterns:

**Question 1:** What method does the PipelineOrchestrator use to handle errors during stage execution?
A) Stop pipeline execution immediately  
B) Skip failed stages and continue  
C) Retry with exponential backoff and circuit breaker protection  
D) Log errors but ignore them  

**Question 2:** How does the ParallelProcessor determine agent assignment for balanced load distribution?
A) Random assignment only  
B) Round-robin assignment based on agent IDs  
C) Workload calculation considering active tasks and agent capacity  
D) First-available agent selection  

**Question 3:** What factors does the DynamicAssembly system consider when selecting agents for capability matching?
A) Agent name only  
B) Capability scores, performance metrics, and availability status  
C) Creation timestamp  
D) Memory usage only  

**Question 4:** What information does the AtomicCLI provide when displaying pipeline status?
A) Just success/failure status  
B) Comprehensive execution details including stage status, timing, and error information  
C) Agent names only  
D) Memory consumption  

**Question 5:** How does the error handling in advanced composition patterns ensure pipeline reliability?
A) Single retry attempt  
B) Circuit breaker integration with configurable retry policies and failure tracking  
C) Manual intervention required  
D) No error handling  

[**🗂️ View Test Solutions →**](Session6_ModuleA_Test_Solutions.md)

### Next Steps

- **Continue to Module B**: [Enterprise Modular Systems](Session6_ModuleB_Enterprise_Modular_Systems.md) for production-scale architectures
- **Return to Core**: [Session 6 Main](Session6_Atomic_Agents_Modular_Architecture.md)
- **Advance to Session 7**: [First ADK Agent](Session7_First_ADK_Agent.md)

---

**🗂️ Source Files for Module A:**

- `src/session6/advanced_composition.py` - Sophisticated pipeline patterns
- `src/session6/dynamic_assembly.py` - Runtime composition systems
- `src/session6/atomic_cli.py` - DevOps CLI integration
