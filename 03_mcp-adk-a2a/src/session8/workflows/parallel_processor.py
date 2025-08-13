"""
Parallel Processing Engine - Session 8
High-performance parallel execution patterns for workflow steps.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
import logging
import queue
import threading
from enum import Enum

logger = logging.getLogger(__name__)


class ParallelStrategy(Enum):
    """Parallel execution strategies."""
    ASYNC_TASKS = "async_tasks"           # Asyncio tasks (default)
    THREAD_POOL = "thread_pool"           # Thread pool executor
    PROCESS_POOL = "process_pool"         # Process pool executor
    HYBRID = "hybrid"                     # Mix of strategies
    BATCH_PROCESSING = "batch_processing" # Batch parallel processing


@dataclass
class ParallelConfig:
    """Configuration for parallel execution."""
    strategy: ParallelStrategy = ParallelStrategy.ASYNC_TASKS
    max_workers: int = 10
    batch_size: int = 5
    timeout_per_task: int = 300
    enable_load_balancing: bool = True
    retry_failed_tasks: bool = True
    max_retries: int = 3


@dataclass
class TaskResult:
    """Result of a parallel task execution."""
    task_id: str
    status: str  # success, failed, timeout
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    worker_info: Optional[str] = None


class WorkerPool:
    """Intelligent worker pool with load balancing."""
    
    def __init__(self, config: ParallelConfig):
        self.config = config
        self.thread_pool = ThreadPoolExecutor(max_workers=config.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=min(config.max_workers, 4))  # Limit processes
        self.worker_stats: Dict[str, Dict[str, Any]] = {}
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
    
    async def submit_parallel_tasks(self, tasks: List[Tuple[str, Callable, Dict[str, Any]]]) -> List[TaskResult]:
        """Submit multiple tasks for parallel execution."""
        logger.info(f"Submitting {len(tasks)} tasks for parallel execution")
        
        if self.config.strategy == ParallelStrategy.ASYNC_TASKS:
            return await self._execute_async_tasks(tasks)
        elif self.config.strategy == ParallelStrategy.THREAD_POOL:
            return await self._execute_thread_pool_tasks(tasks)
        elif self.config.strategy == ParallelStrategy.PROCESS_POOL:
            return await self._execute_process_pool_tasks(tasks)
        elif self.config.strategy == ParallelStrategy.BATCH_PROCESSING:
            return await self._execute_batch_tasks(tasks)
        elif self.config.strategy == ParallelStrategy.HYBRID:
            return await self._execute_hybrid_tasks(tasks)
        else:
            raise ValueError(f"Unknown parallel strategy: {self.config.strategy}")
    
    async def _execute_async_tasks(self, tasks: List[Tuple[str, Callable, Dict[str, Any]]]) -> List[TaskResult]:
        """Execute tasks using asyncio tasks."""
        semaphore = asyncio.Semaphore(self.config.max_workers)
        results = []
        
        async def execute_single_task(task_id: str, func: Callable, kwargs: Dict[str, Any]) -> TaskResult:
            async with semaphore:
                start_time = time.time()
                try:
                    if asyncio.iscoroutinefunction(func):
                        result = await asyncio.wait_for(func(**kwargs), timeout=self.config.timeout_per_task)
                    else:
                        # Run sync function in executor
                        result = await asyncio.get_event_loop().run_in_executor(
                            self.thread_pool, lambda: func(**kwargs)
                        )
                    
                    execution_time = time.time() - start_time
                    return TaskResult(
                        task_id=task_id,
                        status="success",
                        result=result,
                        execution_time=execution_time,
                        worker_info=f"async_task_{asyncio.current_task().get_name()}"
                    )
                
                except asyncio.TimeoutError:
                    return TaskResult(
                        task_id=task_id,
                        status="timeout",
                        error=f"Task timed out after {self.config.timeout_per_task} seconds",
                        execution_time=time.time() - start_time
                    )
                except Exception as e:
                    return TaskResult(
                        task_id=task_id,
                        status="failed",
                        error=str(e),
                        execution_time=time.time() - start_time
                    )
        
        # Create and run all tasks
        task_coroutines = [execute_single_task(task_id, func, kwargs) for task_id, func, kwargs in tasks]
        results = await asyncio.gather(*task_coroutines, return_exceptions=False)
        
        return results
    
    async def _execute_thread_pool_tasks(self, tasks: List[Tuple[str, Callable, Dict[str, Any]]]) -> List[TaskResult]:
        """Execute tasks using thread pool."""
        results = []
        futures = []
        
        for task_id, func, kwargs in tasks:
            future = self.thread_pool.submit(self._execute_sync_task, task_id, func, kwargs)
            futures.append((task_id, future))
        
        # Collect results
        for task_id, future in futures:
            try:
                result = await asyncio.get_event_loop().run_in_executor(None, future.result, self.config.timeout_per_task)
                results.append(result)
            except Exception as e:
                results.append(TaskResult(
                    task_id=task_id,
                    status="failed",
                    error=str(e)
                ))
        
        return results
    
    def _execute_sync_task(self, task_id: str, func: Callable, kwargs: Dict[str, Any]) -> TaskResult:
        """Execute a synchronous task with timing and error handling."""
        start_time = time.time()
        try:
            result = func(**kwargs)
            execution_time = time.time() - start_time
            
            return TaskResult(
                task_id=task_id,
                status="success",
                result=result,
                execution_time=execution_time,
                worker_info=f"thread_{threading.current_thread().name}"
            )
        except Exception as e:
            return TaskResult(
                task_id=task_id,
                status="failed",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _execute_process_pool_tasks(self, tasks: List[Tuple[str, Callable, Dict[str, Any]]]) -> List[TaskResult]:
        """Execute tasks using process pool (for CPU-intensive work)."""
        results = []
        
        # Process pool works best with simple, pickle-able functions
        loop = asyncio.get_event_loop()
        
        for task_id, func, kwargs in tasks:
            try:
                start_time = time.time()
                result = await loop.run_in_executor(self.process_pool, func, **kwargs)
                execution_time = time.time() - start_time
                
                results.append(TaskResult(
                    task_id=task_id,
                    status="success",
                    result=result,
                    execution_time=execution_time,
                    worker_info="process_pool"
                ))
            except Exception as e:
                results.append(TaskResult(
                    task_id=task_id,
                    status="failed",
                    error=str(e)
                ))
        
        return results
    
    async def _execute_batch_tasks(self, tasks: List[Tuple[str, Callable, Dict[str, Any]]]) -> List[TaskResult]:
        """Execute tasks in batches for better resource management."""
        all_results = []
        batch_size = self.config.batch_size
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} with {len(batch)} tasks")
            
            # Execute batch using async tasks
            batch_results = await self._execute_async_tasks(batch)
            all_results.extend(batch_results)
            
            # Small delay between batches to prevent resource exhaustion
            if i + batch_size < len(tasks):
                await asyncio.sleep(0.1)
        
        return all_results
    
    async def _execute_hybrid_tasks(self, tasks: List[Tuple[str, Callable, Dict[str, Any]]]) -> List[TaskResult]:
        """Execute tasks using hybrid strategy based on task characteristics."""
        cpu_intensive_tasks = []
        io_intensive_tasks = []
        regular_tasks = []
        
        # Categorize tasks (simplified heuristics)
        for task_id, func, kwargs in tasks:
            if hasattr(func, '__name__'):
                if 'compute' in func.__name__.lower() or 'calculate' in func.__name__.lower():
                    cpu_intensive_tasks.append((task_id, func, kwargs))
                elif 'download' in func.__name__.lower() or 'fetch' in func.__name__.lower():
                    io_intensive_tasks.append((task_id, func, kwargs))
                else:
                    regular_tasks.append((task_id, func, kwargs))
            else:
                regular_tasks.append((task_id, func, kwargs))
        
        # Execute different categories with appropriate strategies
        results = []
        
        if cpu_intensive_tasks:
            logger.info(f"Executing {len(cpu_intensive_tasks)} CPU-intensive tasks with process pool")
            cpu_results = await self._execute_process_pool_tasks(cpu_intensive_tasks)
            results.extend(cpu_results)
        
        if io_intensive_tasks:
            logger.info(f"Executing {len(io_intensive_tasks)} I/O-intensive tasks with async")
            io_results = await self._execute_async_tasks(io_intensive_tasks)
            results.extend(io_results)
        
        if regular_tasks:
            logger.info(f"Executing {len(regular_tasks)} regular tasks with thread pool")
            regular_results = await self._execute_thread_pool_tasks(regular_tasks)
            results.extend(regular_results)
        
        return results
    
    def shutdown(self):
        """Clean shutdown of worker pools."""
        logger.info("Shutting down worker pools")
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


class ParallelExecutionManager:
    """High-level manager for parallel workflow execution."""
    
    def __init__(self, config: Optional[ParallelConfig] = None):
        self.config = config or ParallelConfig()
        self.worker_pool = WorkerPool(self.config)
        self.execution_metrics: Dict[str, Any] = {}
    
    async def execute_parallel_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a complete parallel workflow."""
        start_time = time.time()
        
        # Convert workflow steps to tasks
        tasks = []
        for i, step in enumerate(workflow_steps):
            task_id = step.get('id', f"task_{i}")
            func = step.get('function')
            kwargs = step.get('kwargs', {})
            
            if func:
                tasks.append((task_id, func, kwargs))
        
        logger.info(f"Starting parallel execution of {len(tasks)} tasks")
        
        # Execute tasks
        results = await self.worker_pool.submit_parallel_tasks(tasks)
        
        # Analyze results
        total_time = time.time() - start_time
        successful_tasks = [r for r in results if r.status == "success"]
        failed_tasks = [r for r in results if r.status == "failed"]
        timeout_tasks = [r for r in results if r.status == "timeout"]
        
        # Handle retries for failed tasks if enabled
        if self.config.retry_failed_tasks and failed_tasks:
            retry_tasks = []
            for failed_result in failed_tasks:
                if failed_result.retry_count < self.config.max_retries:
                    # Find original task to retry
                    for task_id, func, kwargs in tasks:
                        if task_id == failed_result.task_id:
                            retry_tasks.append((task_id, func, kwargs))
                            break
            
            if retry_tasks:
                logger.info(f"Retrying {len(retry_tasks)} failed tasks")
                retry_results = await self.worker_pool.submit_parallel_tasks(retry_tasks)
                
                # Update results
                for retry_result in retry_results:
                    retry_result.retry_count += 1
                    # Replace original failed result
                    for i, result in enumerate(results):
                        if result.task_id == retry_result.task_id:
                            results[i] = retry_result
                            break
        
        # Calculate final statistics
        final_successful = [r for r in results if r.status == "success"]
        final_failed = [r for r in results if r.status != "success"]
        
        execution_summary = {
            "total_tasks": len(tasks),
            "successful_tasks": len(final_successful),
            "failed_tasks": len(final_failed),
            "success_rate": len(final_successful) / len(tasks) * 100 if tasks else 0,
            "total_execution_time": total_time,
            "average_task_time": sum(r.execution_time for r in results) / len(results) if results else 0,
            "parallel_efficiency": (sum(r.execution_time for r in results) / total_time) if total_time > 0 else 0,
            "strategy_used": self.config.strategy.value
        }
        
        return {
            "execution_summary": execution_summary,
            "task_results": [
                {
                    "task_id": r.task_id,
                    "status": r.status,
                    "result": r.result,
                    "error": r.error,
                    "execution_time": r.execution_time,
                    "retry_count": r.retry_count,
                    "worker_info": r.worker_info
                } for r in results
            ],
            "performance_metrics": self._calculate_performance_metrics(results)
        }
    
    def _calculate_performance_metrics(self, results: List[TaskResult]) -> Dict[str, Any]:
        """Calculate detailed performance metrics."""
        if not results:
            return {}
        
        execution_times = [r.execution_time for r in results]
        successful_results = [r for r in results if r.status == "success"]
        
        return {
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "median_execution_time": sorted(execution_times)[len(execution_times) // 2],
            "total_compute_time": sum(execution_times),
            "throughput_tasks_per_second": len(successful_results) / max(sum(execution_times), 0.001),
            "error_rate": (len(results) - len(successful_results)) / len(results) * 100,
            "retry_statistics": {
                "tasks_retried": len([r for r in results if r.retry_count > 0]),
                "total_retries": sum(r.retry_count for r in results),
                "avg_retries_per_task": sum(r.retry_count for r in results) / len(results)
            }
        }
    
    async def optimize_parallel_execution(self, sample_tasks: List[Dict[str, Any]]) -> ParallelConfig:
        """Optimize parallel execution configuration based on sample tasks."""
        logger.info("Running optimization tests with different configurations")
        
        test_configs = [
            ParallelConfig(strategy=ParallelStrategy.ASYNC_TASKS, max_workers=5),
            ParallelConfig(strategy=ParallelStrategy.ASYNC_TASKS, max_workers=10),
            ParallelConfig(strategy=ParallelStrategy.THREAD_POOL, max_workers=5),
            ParallelConfig(strategy=ParallelStrategy.BATCH_PROCESSING, batch_size=3),
        ]
        
        best_config = None
        best_performance = 0
        
        for config in test_configs:
            # Run a small sample
            sample_size = min(len(sample_tasks), 10)
            test_tasks = sample_tasks[:sample_size]
            
            # Test configuration
            test_manager = ParallelExecutionManager(config)
            result = await test_manager.execute_parallel_workflow(test_tasks)
            
            # Calculate performance score (combination of speed and success rate)
            summary = result["execution_summary"]
            performance_score = (summary["success_rate"] / 100) * (1 / max(summary["total_execution_time"], 0.001))
            
            if performance_score > best_performance:
                best_performance = performance_score
                best_config = config
            
            test_manager.worker_pool.shutdown()
        
        logger.info(f"Optimal configuration found: {best_config.strategy.value} with {best_config.max_workers} workers")
        return best_config
    
    def shutdown(self):
        """Shutdown the parallel execution manager."""
        self.worker_pool.shutdown()


# Example utility functions for testing parallel execution
async def sample_async_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sample async task for testing."""
    delay = task_data.get('delay', 0.1)
    await asyncio.sleep(delay)
    return {
        "task_id": task_data.get('id'),
        "processed": True,
        "data": task_data.get('data', 'sample_data'),
        "timestamp": datetime.now().isoformat()
    }


def sample_sync_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sample sync task for testing."""
    delay = task_data.get('delay', 0.1)
    time.sleep(delay)
    return {
        "task_id": task_data.get('id'),
        "processed": True,
        "data": task_data.get('data', 'sample_data'),
        "timestamp": datetime.now().isoformat()
    }


def cpu_intensive_task(iterations: int = 100000) -> Dict[str, Any]:
    """CPU-intensive task for testing process pool."""
    result = 0
    for i in range(iterations):
        result += i * i
    
    return {
        "computation_result": result,
        "iterations": iterations,
        "timestamp": datetime.now().isoformat()
    }