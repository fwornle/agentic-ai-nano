# src/session5/benchmarking_suite.py
"""
Comprehensive benchmarking suite for PydanticAI agents.
Provides performance measurement, comparison, and analysis tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, TypeVar, Tuple, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import time
import statistics
import json
import psutil
import gc
import memory_profiler
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
import functools
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')

class BenchmarkType(str, Enum):
    """Types of benchmarks."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY = "memory"
    CPU = "cpu"
    CONCURRENCY = "concurrency"
    SCALABILITY = "scalability"

class MetricUnit(str, Enum):
    """Units for metrics."""
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    NANOSECONDS = "nanoseconds"
    REQUESTS_PER_SECOND = "requests_per_second"
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    PERCENT = "percent"

# Benchmark result models

class BenchmarkResult(BaseModel):
    """Result of a single benchmark measurement."""
    benchmark_name: str = Field(..., description="Name of the benchmark")
    benchmark_type: BenchmarkType = Field(..., description="Type of benchmark")
    value: float = Field(..., description="Measured value")
    unit: MetricUnit = Field(..., description="Unit of measurement")
    execution_time: float = Field(..., description="Execution time in seconds")
    memory_used: Optional[float] = Field(None, description="Peak memory usage in MB")
    cpu_usage: Optional[float] = Field(None, description="Average CPU usage percentage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now)

class BenchmarkSuite(BaseModel):
    """Collection of benchmark results."""
    suite_name: str = Field(..., description="Name of the benchmark suite")
    results: List[BenchmarkResult] = Field(default_factory=list, description="Benchmark results")
    system_info: Dict[str, Any] = Field(default_factory=dict, description="System information")
    created_at: datetime = Field(default_factory=datetime.now)
    
    def add_result(self, result: BenchmarkResult):
        """Add a benchmark result to the suite."""
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the suite."""
        if not self.results:
            return {}
        
        summary = {
            "total_benchmarks": len(self.results),
            "types": {},
            "execution_summary": {}
        }
        
        # Group by type
        by_type = {}
        for result in self.results:
            if result.benchmark_type not in by_type:
                by_type[result.benchmark_type] = []
            by_type[result.benchmark_type.value].append(result)
        
        # Calculate statistics by type
        for benchmark_type, results in by_type.items():
            values = [r.value for r in results]
            execution_times = [r.execution_time for r in results]
            
            summary["types"][benchmark_type] = {
                "count": len(results),
                "value_stats": {
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0
                },
                "execution_time_stats": {
                    "min": min(execution_times),
                    "max": max(execution_times),
                    "mean": statistics.mean(execution_times),
                    "total": sum(execution_times)
                }
            }
        
        return summary

class ComparisonResult(BaseModel):
    """Result of comparing benchmark suites."""
    baseline_suite: str = Field(..., description="Name of baseline suite")
    comparison_suite: str = Field(..., description="Name of comparison suite")
    improvements: List[Dict[str, Any]] = Field(default_factory=list, description="Performance improvements")
    regressions: List[Dict[str, Any]] = Field(default_factory=list, description="Performance regressions")
    overall_improvement: float = Field(default=0.0, description="Overall improvement percentage")
    timestamp: datetime = Field(default_factory=datetime.now)

# Benchmark execution framework

class Benchmark(ABC):
    """Abstract base class for benchmarks."""
    
    def __init__(self, name: str, benchmark_type: BenchmarkType):
        self.name = name
        self.benchmark_type = benchmark_type
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> BenchmarkResult:
        """Execute the benchmark."""
        pass
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "available_memory_mb": psutil.virtual_memory().available / (1024 * 1024)
        }

class LatencyBenchmark(Benchmark):
    """Benchmark for measuring operation latency."""
    
    def __init__(self, name: str, operation: Callable, warmup_iterations: int = 10):
        super().__init__(name, BenchmarkType.LATENCY)
        self.operation = operation
        self.warmup_iterations = warmup_iterations
    
    async def run(self, iterations: int = 100, *args, **kwargs) -> BenchmarkResult:
        """Run latency benchmark."""
        # Warmup
        for _ in range(self.warmup_iterations):
            try:
                if asyncio.iscoroutinefunction(self.operation):
                    await self.operation(*args, **kwargs)
                else:
                    self.operation(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Warmup iteration failed: {str(e)}")
        
        # Force garbage collection
        gc.collect()
        
        # Actual benchmark
        start_time = time.time()
        system_start = self._get_system_metrics()
        latencies = []
        
        for i in range(iterations):
            iteration_start = time.perf_counter()
            
            try:
                if asyncio.iscoroutinefunction(self.operation):
                    await self.operation(*args, **kwargs)
                else:
                    self.operation(*args, **kwargs)
                
                iteration_end = time.perf_counter()
                latencies.append((iteration_end - iteration_start) * 1000)  # Convert to ms
                
            except Exception as e:
                self.logger.error(f"Benchmark iteration {i} failed: {str(e)}")
        
        end_time = time.time()
        system_end = self._get_system_metrics()
        
        if not latencies:
            raise ValueError("All benchmark iterations failed")
        
        # Calculate metrics
        avg_latency = statistics.mean(latencies)
        execution_time = end_time - start_time
        avg_cpu = (system_start["cpu_percent"] + system_end["cpu_percent"]) / 2
        
        return BenchmarkResult(
            benchmark_name=self.name,
            benchmark_type=self.benchmark_type,
            value=avg_latency,
            unit=MetricUnit.MILLISECONDS,
            execution_time=execution_time,
            cpu_usage=avg_cpu,
            metadata={
                "iterations": iterations,
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "median_latency": statistics.median(latencies),
                "p95_latency": sorted(latencies)[int(0.95 * len(latencies))],
                "p99_latency": sorted(latencies)[int(0.99 * len(latencies))],
                "stdev_latency": statistics.stdev(latencies) if len(latencies) > 1 else 0
            }
        )

class ThroughputBenchmark(Benchmark):
    """Benchmark for measuring throughput."""
    
    def __init__(self, name: str, operation: Callable, warmup_duration: float = 1.0):
        super().__init__(name, BenchmarkType.THROUGHPUT)
        self.operation = operation
        self.warmup_duration = warmup_duration
    
    async def run(self, duration_seconds: float = 10.0, concurrency: int = 1, 
                  *args, **kwargs) -> BenchmarkResult:
        """Run throughput benchmark."""
        # Warmup
        warmup_end = time.time() + self.warmup_duration
        while time.time() < warmup_end:
            try:
                if asyncio.iscoroutinefunction(self.operation):
                    await self.operation(*args, **kwargs)
                else:
                    self.operation(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Warmup operation failed: {str(e)}")
        
        # Force garbage collection
        gc.collect()
        
        # Actual benchmark
        start_time = time.time()
        system_start = self._get_system_metrics()
        successful_operations = 0
        failed_operations = 0
        
        async def worker():
            nonlocal successful_operations, failed_operations
            end_time = start_time + duration_seconds
            
            while time.time() < end_time:
                try:
                    if asyncio.iscoroutinefunction(self.operation):
                        await self.operation(*args, **kwargs)
                    else:
                        self.operation(*args, **kwargs)
                    successful_operations += 1
                except Exception as e:
                    failed_operations += 1
                    self.logger.debug(f"Operation failed: {str(e)}")
        
        # Run concurrent workers
        if concurrency > 1:
            tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]
            await asyncio.gather(*tasks)
        else:
            await worker()
        
        actual_duration = time.time() - start_time
        system_end = self._get_system_metrics()
        
        # Calculate throughput
        throughput = successful_operations / actual_duration
        avg_cpu = (system_start["cpu_percent"] + system_end["cpu_percent"]) / 2
        
        return BenchmarkResult(
            benchmark_name=self.name,
            benchmark_type=self.benchmark_type,
            value=throughput,
            unit=MetricUnit.REQUESTS_PER_SECOND,
            execution_time=actual_duration,
            cpu_usage=avg_cpu,
            metadata={
                "successful_operations": successful_operations,
                "failed_operations": failed_operations,
                "success_rate": successful_operations / (successful_operations + failed_operations),
                "concurrency": concurrency,
                "duration_seconds": duration_seconds
            }
        )

class MemoryBenchmark(Benchmark):
    """Benchmark for measuring memory usage."""
    
    def __init__(self, name: str, operation: Callable):
        super().__init__(name, BenchmarkType.MEMORY)
        self.operation = operation
    
    @memory_profiler.profile
    async def _profile_memory(self, *args, **kwargs):
        """Profile memory usage of operation."""
        if asyncio.iscoroutinefunction(self.operation):
            return await self.operation(*args, **kwargs)
        else:
            return self.operation(*args, **kwargs)
    
    async def run(self, iterations: int = 10, *args, **kwargs) -> BenchmarkResult:
        """Run memory benchmark."""
        import tracemalloc
        
        # Start memory tracing
        tracemalloc.start()
        gc.collect()
        
        start_time = time.time()
        baseline_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        
        # Run operations
        for i in range(iterations):
            try:
                if asyncio.iscoroutinefunction(self.operation):
                    await self.operation(*args, **kwargs)
                else:
                    self.operation(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Memory benchmark iteration {i} failed: {str(e)}")
        
        # Measure peak memory
        current_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        execution_time = time.time() - start_time
        memory_used = max(current_memory - baseline_memory, peak / (1024 * 1024))
        
        return BenchmarkResult(
            benchmark_name=self.name,
            benchmark_type=self.benchmark_type,
            value=memory_used,
            unit=MetricUnit.MEGABYTES,
            execution_time=execution_time,
            memory_used=memory_used,
            metadata={
                "iterations": iterations,
                "baseline_memory_mb": baseline_memory,
                "final_memory_mb": current_memory,
                "traced_current_mb": current / (1024 * 1024),
                "traced_peak_mb": peak / (1024 * 1024)
            }
        )

# Benchmark runner and suite manager

class BenchmarkRunner:
    """Executes and manages benchmark suites."""
    
    def __init__(self):
        self.suites: Dict[str, BenchmarkSuite] = {}
        self.logger = logging.getLogger(__name__ + ".BenchmarkRunner")
    
    def create_suite(self, name: str) -> BenchmarkSuite:
        """Create a new benchmark suite."""
        suite = BenchmarkSuite(
            suite_name=name,
            system_info=self._get_system_info()
        )
        self.suites[name] = suite
        return suite
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        import platform
        
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": psutil.virtual_memory().total / (1024**3),
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_benchmark(self, suite_name: str, benchmark: Benchmark, 
                          *args, **kwargs) -> BenchmarkResult:
        """Run a single benchmark and add to suite."""
        if suite_name not in self.suites:
            self.create_suite(suite_name)
        
        self.logger.info(f"Running benchmark: {benchmark.name}")
        result = await benchmark.run(*args, **kwargs)
        
        self.suites[suite_name].add_result(result)
        self.logger.info(f"Completed benchmark: {benchmark.name} = {result.value:.2f} {result.unit.value}")
        
        return result
    
    async def run_multiple_benchmarks(self, suite_name: str, benchmarks: List[Tuple[Benchmark, tuple, dict]]):
        """Run multiple benchmarks in sequence."""
        results = []
        
        for benchmark, args, kwargs in benchmarks:
            try:
                result = await self.run_benchmark(suite_name, benchmark, *args, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to run benchmark {benchmark.name}: {str(e)}")
        
        return results
    
    def compare_suites(self, baseline_name: str, comparison_name: str) -> ComparisonResult:
        """Compare two benchmark suites."""
        if baseline_name not in self.suites or comparison_name not in self.suites:
            raise ValueError("Both suites must exist for comparison")
        
        baseline = self.suites[baseline_name]
        comparison = self.suites[comparison_name]
        
        improvements = []
        regressions = []
        
        # Create lookup for baseline results
        baseline_lookup = {r.benchmark_name: r for r in baseline.results}
        
        for comp_result in comparison.results:
            if comp_result.benchmark_name in baseline_lookup:
                baseline_result = baseline_lookup[comp_result.benchmark_name]
                
                # Calculate improvement/regression
                if baseline_result.benchmark_type in [BenchmarkType.LATENCY, BenchmarkType.MEMORY]:
                    # Lower is better
                    change_percent = ((baseline_result.value - comp_result.value) / baseline_result.value) * 100
                else:
                    # Higher is better (throughput)
                    change_percent = ((comp_result.value - baseline_result.value) / baseline_result.value) * 100
                
                change_data = {
                    "benchmark_name": comp_result.benchmark_name,
                    "baseline_value": baseline_result.value,
                    "comparison_value": comp_result.value,
                    "change_percent": change_percent,
                    "unit": comp_result.unit.value
                }
                
                if change_percent > 0:
                    improvements.append(change_data)
                else:
                    regressions.append(change_data)
        
        # Calculate overall improvement
        all_changes = [item["change_percent"] for item in improvements + regressions]
        overall_improvement = statistics.mean(all_changes) if all_changes else 0.0
        
        return ComparisonResult(
            baseline_suite=baseline_name,
            comparison_suite=comparison_name,
            improvements=improvements,
            regressions=regressions,
            overall_improvement=overall_improvement
        )
    
    def generate_report(self, suite_name: str) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        if suite_name not in self.suites:
            raise ValueError(f"Suite {suite_name} not found")
        
        suite = self.suites[suite_name]
        summary = suite.get_summary()
        
        return {
            "suite_name": suite_name,
            "system_info": suite.system_info,
            "summary": summary,
            "detailed_results": [result.dict() for result in suite.results],
            "generated_at": datetime.now().isoformat()
        }
    
    def save_report(self, suite_name: str, filename: str):
        """Save benchmark report to file."""
        report = self.generate_report(suite_name)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Benchmark report saved to {filename}")

# Example benchmarks and demonstrations

async def example_async_operation(duration: float = 0.01):
    """Example async operation for benchmarking."""
    await asyncio.sleep(duration)
    return "completed"

def example_cpu_intensive_operation(iterations: int = 1000):
    """Example CPU-intensive operation."""
    result = 0
    for i in range(iterations):
        result += i ** 2
    return result

def example_memory_intensive_operation(size_mb: int = 10):
    """Example memory-intensive operation."""
    # Allocate memory
    data = [0] * (size_mb * 1024 * 128)  # Roughly size_mb MB
    return len(data)

def demo_benchmarking_suite():
    """Demonstrate benchmarking suite usage."""
    print("\n=== Benchmarking Suite Demo ===")
    
    async def run_demo():
        runner = BenchmarkRunner()
        
        # Create benchmark suite
        suite = runner.create_suite("performance_test")
        
        print("Running latency benchmarks...")
        
        # Latency benchmark for async operation
        async_latency = LatencyBenchmark("async_operation_latency", example_async_operation)
        await runner.run_benchmark("performance_test", async_latency, iterations=50, duration=0.005)
        
        # Latency benchmark for CPU operation
        cpu_latency = LatencyBenchmark("cpu_operation_latency", example_cpu_intensive_operation)
        await runner.run_benchmark("performance_test", cpu_latency, iterations=20, iterations_arg=500)
        
        print("Running throughput benchmarks...")
        
        # Throughput benchmark
        throughput = ThroughputBenchmark("async_throughput", example_async_operation)
        await runner.run_benchmark("performance_test", throughput, duration_seconds=3.0, concurrency=5, duration=0.001)
        
        print("Running memory benchmarks...")
        
        # Memory benchmark
        memory = MemoryBenchmark("memory_usage", example_memory_intensive_operation)
        await runner.run_benchmark("performance_test", memory, iterations=5, size_mb=5)
        
        print("Generating report...")
        
        # Generate and display report
        report = runner.generate_report("performance_test")
        print(json.dumps(report["summary"], indent=2))
        
        # Save report
        runner.save_report("performance_test", "benchmark_report.json")
        
        # Create second suite for comparison
        suite2 = runner.create_suite("performance_test_optimized")
        
        # Run "optimized" versions (simulated)
        optimized_async = LatencyBenchmark("async_operation_latency", example_async_operation)
        await runner.run_benchmark("performance_test_optimized", optimized_async, iterations=50, duration=0.003)
        
        optimized_cpu = LatencyBenchmark("cpu_operation_latency", example_cpu_intensive_operation)
        await runner.run_benchmark("performance_test_optimized", optimized_cpu, iterations=20, iterations_arg=300)
        
        print("Comparing suites...")
        
        # Compare suites
        comparison = runner.compare_suites("performance_test", "performance_test_optimized")
        
        print(f"\nOverall improvement: {comparison.overall_improvement:.1f}%")
        
        if comparison.improvements:
            print("\nImprovements:")
            for imp in comparison.improvements:
                print(f"  {imp['benchmark_name']}: {imp['change_percent']:.1f}% better")
        
        if comparison.regressions:
            print("\nRegressions:")
            for reg in comparison.regressions:
                print(f"  {reg['benchmark_name']}: {abs(reg['change_percent']):.1f}% worse")
    
    # Run the async demo
    asyncio.run(run_demo())

if __name__ == "__main__":
    demo_benchmarking_suite()