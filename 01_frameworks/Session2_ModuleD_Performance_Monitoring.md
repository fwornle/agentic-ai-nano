# Session 2 - Module D: Performance & Monitoring (50 minutes)

**Prerequisites**: [Session 2 Core Section Complete](Session2_LangChain_Foundations.md)  
**Target Audience**: Production-focused developers  
**Cognitive Load**: 6 optimization concepts

---

## 🎯 Module Overview

This module focuses on performance benchmarking, monitoring, and cost optimization for production LangChain applications. You'll learn how to measure performance, implement comprehensive monitoring, and optimize resource usage for enterprise-scale deployments.

### Learning Objectives
By the end of this module, you will:
- Implement performance benchmarking and optimization strategies for LangChain agents
- Set up comprehensive monitoring and observability systems for production applications
- Design cost optimization strategies for API usage and resource management
- Create real-time performance dashboards and alerting systems

---

## Part 1: Performance Benchmarking & Optimization (20 minutes)

### Comprehensive Performance Measurement

🗂️ **File**: `src/session2/performance_benchmarking.py` - Performance measurement and optimization

Production LangChain applications require systematic performance measurement across multiple dimensions to ensure optimal user experience and resource utilization:

```python
import time
import asyncio
import statistics
import psutil
import tracemalloc
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics for LangChain agents"""
    
    # Response Time Metrics
    avg_response_time: float = 0.0
    p50_response_time: float = 0.0
    p90_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # Throughput Metrics
    requests_per_second: float = 0.0
    concurrent_requests_handled: int = 0
    max_concurrent_capacity: int = 0
    
    # Resource Utilization
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_peak_mb: float = 0.0
    
    # LLM-Specific Metrics
    tokens_per_second: float = 0.0
    avg_prompt_tokens: float = 0.0
    avg_completion_tokens: float = 0.0
    llm_api_latency: float = 0.0
    
    # Tool Usage Metrics
    tool_execution_time: float = 0.0
    tool_success_rate: float = 0.0
    cache_hit_rate: float = 0.0
    
    # Error Metrics
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    retry_rate: float = 0.0
    
    # Quality Metrics
    response_quality_score: float = 0.0
    user_satisfaction_score: float = 0.0
    
    # Operational Metrics
    uptime_percentage: float = 0.0
    deployment_frequency: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.now)

class PerformanceBenchmarkSuite:
    """Comprehensive performance benchmarking for LangChain agents"""
    
    def __init__(self, agent_factory: Callable, config: Dict[str, Any]):
        self.agent_factory = agent_factory
        self.config = config
        self.performance_history: List[PerformanceMetrics] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize monitoring
        tracemalloc.start()
        
    async def run_comprehensive_benchmark(self, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute comprehensive performance benchmark across multiple scenarios"""
        
        benchmark_results = {
            "benchmark_id": f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now(),
            "config": self.config,
            "scenarios": {},
            "summary": {},
            "recommendations": []
        }
        
        try:
            # Run each test scenario
            for scenario in test_scenarios:
                scenario_name = scenario["name"]
                self.logger.info(f"Running benchmark scenario: {scenario_name}")
                
                scenario_results = await self._run_scenario_benchmark(scenario)
                benchmark_results["scenarios"][scenario_name] = scenario_results
            
            # Generate summary and recommendations
            benchmark_results["summary"] = self._generate_benchmark_summary(benchmark_results["scenarios"])
            benchmark_results["recommendations"] = self._generate_optimization_recommendations(benchmark_results["summary"])
            
            benchmark_results["end_time"] = datetime.now()
            benchmark_results["total_duration"] = (benchmark_results["end_time"] - benchmark_results["start_time"]).total_seconds()
            
            return benchmark_results
            
        except Exception as e:
            self.logger.error(f"Benchmark failed: {str(e)}")
            benchmark_results["error"] = str(e)
            return benchmark_results
    
    async def _run_scenario_benchmark(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run performance benchmark for a specific scenario"""
        
        scenario_config = {
            "name": scenario["name"],
            "description": scenario.get("description", ""),
            "concurrent_users": scenario.get("concurrent_users", 1),
            "requests_per_user": scenario.get("requests_per_user", 10),
            "test_duration_seconds": scenario.get("test_duration_seconds", 60),
            "warmup_requests": scenario.get("warmup_requests", 5),
            "test_data": scenario.get("test_data", [])
        }
        
        # Start resource monitoring
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.cpu_percent()
        
        # Warmup phase
        await self._run_warmup_phase(scenario_config)
        
        # Main benchmark phase
        performance_data = await self._run_load_test(scenario_config)
        
        # Resource measurement
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        end_cpu = psutil.cpu_percent()
        
        # Calculate metrics
        metrics = self._calculate_performance_metrics(
            performance_data, 
            start_memory, end_memory, 
            start_cpu, end_cpu
        )
        
        return {
            "config": scenario_config,
            "metrics": metrics,
            "raw_data": performance_data,
            "resource_usage": {
                "memory_delta_mb": end_memory - start_memory,
                "cpu_usage_percent": end_cpu,
                "peak_memory_mb": max(performance_data.get("memory_samples", [start_memory]))
            }
        }
    
    async def _run_load_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute concurrent load test"""
        
        concurrent_users = config["concurrent_users"]
        requests_per_user = config["requests_per_user"]
        test_data = config["test_data"]
        
        # Prepare test data
        if not test_data:
            test_data = self._generate_test_data(requests_per_user * concurrent_users)
        
        # Track all performance data
        all_response_times = []
        all_token_counts = []
        error_count = 0
        timeout_count = 0
        memory_samples = []
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_users)
        
        async def run_single_request(test_input: str) -> Dict[str, Any]:
            """Execute single request with monitoring"""
            async with semaphore:
                start_time = time.time()
                
                try:
                    # Create agent instance
                    agent = self.agent_factory()
                    
                    # Monitor memory before request
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory)
                    
                    # Execute request with timeout
                    response = await asyncio.wait_for(
                        agent.arun(test_input),
                        timeout=self.config.get("request_timeout", 30)
                    )
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    # Extract token information (if available)
                    prompt_tokens = getattr(agent, 'last_prompt_tokens', 0)
                    completion_tokens = getattr(agent, 'last_completion_tokens', 0)
                    
                    return {
                        "success": True,
                        "response_time": response_time,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "response_length": len(response) if response else 0,
                        "memory_usage": current_memory
                    }
                    
                except asyncio.TimeoutError:
                    nonlocal timeout_count
                    timeout_count += 1
                    return {
                        "success": False,
                        "error_type": "timeout",
                        "response_time": time.time() - start_time
                    }
                    
                except Exception as e:
                    nonlocal error_count
                    error_count += 1
                    return {
                        "success": False,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "response_time": time.time() - start_time
                    }
        
        # Execute all requests concurrently
        tasks = [run_single_request(data) for data in test_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                successful_results.append(result)
                all_response_times.append(result["response_time"])
                all_token_counts.append(result.get("prompt_tokens", 0) + result.get("completion_tokens", 0))
        
        return {
            "response_times": all_response_times,
            "token_counts": all_token_counts,
            "successful_requests": len(successful_results),
            "total_requests": len(results),
            "error_count": error_count,
            "timeout_count": timeout_count,
            "memory_samples": memory_samples,
            "raw_results": successful_results
        }
    
    def _calculate_performance_metrics(self, performance_data: Dict[str, Any], 
                                     start_memory: float, end_memory: float,
                                     start_cpu: float, end_cpu: float) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        response_times = performance_data["response_times"]
        total_requests = performance_data["total_requests"]
        successful_requests = performance_data["successful_requests"]
        token_counts = performance_data["token_counts"]
        
        if not response_times:
            return PerformanceMetrics()  # Return empty metrics if no successful requests
        
        # Response time metrics
        sorted_times = sorted(response_times)
        avg_response_time = statistics.mean(response_times)
        p50 = sorted_times[len(sorted_times) // 2]
        p90 = sorted_times[int(len(sorted_times) * 0.9)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Throughput metrics
        total_test_time = max(response_times) if response_times else 1
        requests_per_second = successful_requests / total_test_time
        
        # Token metrics
        avg_tokens = statistics.mean(token_counts) if token_counts else 0
        tokens_per_second = sum(token_counts) / total_test_time if token_counts else 0
        
        # Error metrics
        error_rate = (total_requests - successful_requests) / total_requests if total_requests > 0 else 0
        timeout_rate = performance_data["timeout_count"] / total_requests if total_requests > 0 else 0
        
        # Memory metrics
        memory_samples = performance_data.get("memory_samples", [start_memory])
        peak_memory = max(memory_samples) if memory_samples else start_memory
        avg_memory = statistics.mean(memory_samples) if memory_samples else start_memory
        
        return PerformanceMetrics(
            avg_response_time=avg_response_time,
            p50_response_time=p50,
            p90_response_time=p90,
            p95_response_time=p95,
            p99_response_time=p99,
            requests_per_second=requests_per_second,
            concurrent_requests_handled=successful_requests,
            memory_usage_mb=avg_memory,
            memory_peak_mb=peak_memory,
            cpu_usage_percent=end_cpu,
            tokens_per_second=tokens_per_second,
            avg_prompt_tokens=avg_tokens / 2,  # Rough estimation
            avg_completion_tokens=avg_tokens / 2,
            error_rate=error_rate * 100,  # Convert to percentage
            timeout_rate=timeout_rate * 100
        )
    
    def _generate_optimization_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on benchmark results"""
        
        recommendations = []
        
        # Response time recommendations
        avg_response_time = summary.get("avg_response_time", 0)
        if avg_response_time > 5.0:
            recommendations.append("Response times are high (>5s). Consider implementing caching or optimizing prompts.")
        
        p95_response_time = summary.get("p95_response_time", 0)
        if p95_response_time > avg_response_time * 2:
            recommendations.append("High response time variance detected. Investigate outliers and implement timeout handling.")
        
        # Throughput recommendations
        requests_per_second = summary.get("requests_per_second", 0)
        if requests_per_second < 1.0:
            recommendations.append("Low throughput detected. Consider implementing connection pooling or async processing.")
        
        # Error rate recommendations
        error_rate = summary.get("error_rate", 0)
        if error_rate > 5.0:
            recommendations.append("High error rate (>5%). Implement better error handling and retry mechanisms.")
        
        # Memory recommendations
        memory_usage = summary.get("memory_usage_mb", 0)
        if memory_usage > 1000:
            recommendations.append("High memory usage detected. Consider implementing memory optimization strategies.")
        
        # Token optimization
        tokens_per_second = summary.get("tokens_per_second", 0)
        if tokens_per_second < 10:
            recommendations.append("Low token throughput. Consider optimizing prompt engineering or using faster models.")
        
        # CPU recommendations
        cpu_usage = summary.get("cpu_usage_percent", 0)
        if cpu_usage > 80:
            recommendations.append("High CPU usage detected. Consider scaling horizontally or optimizing compute-intensive operations.")
        
        if not recommendations:
            recommendations.append("Performance metrics are within acceptable ranges. Continue monitoring for trends.")
        
        return recommendations

class ContinuousPerformanceMonitor:
    """Continuous performance monitoring for production systems"""
    
    def __init__(self, monitoring_config: Dict[str, Any]):
        self.config = monitoring_config
        self.metrics_buffer: List[PerformanceMetrics] = []
        self.alert_thresholds = monitoring_config.get("alert_thresholds", {})
        self.monitoring_active = False
        self.logger = logging.getLogger(__name__)
        
    async def start_monitoring(self, agent_instance):
        """Start continuous performance monitoring"""
        
        self.monitoring_active = True
        self.logger.info("Starting continuous performance monitoring")
        
        # Start monitoring tasks
        monitoring_tasks = [
            asyncio.create_task(self._monitor_response_times(agent_instance)),
            asyncio.create_task(self._monitor_resource_usage()),
            asyncio.create_task(self._monitor_error_rates(agent_instance)),
            asyncio.create_task(self._process_metrics_buffer())
        ]
        
        try:
            await asyncio.gather(*monitoring_tasks)
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")
        finally:
            self.monitoring_active = False
    
    async def _monitor_response_times(self, agent_instance):
        """Monitor agent response times continuously"""
        
        while self.monitoring_active:
            try:
                # Inject monitoring into agent calls
                original_run = agent_instance.run
                
                def monitored_run(input_text):
                    start_time = time.time()
                    try:
                        result = original_run(input_text)
                        response_time = time.time() - start_time
                        
                        # Record metric
                        self._record_response_time_metric(response_time, True)
                        
                        return result
                    except Exception as e:
                        response_time = time.time() - start_time
                        self._record_response_time_metric(response_time, False)
                        raise e
                
                agent_instance.run = monitored_run
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Response time monitoring error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _monitor_resource_usage(self):
        """Monitor system resource usage"""
        
        while self.monitoring_active:
            try:
                # Get current resource usage
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()
                
                # Check against thresholds
                if memory_mb > self.alert_thresholds.get("memory_mb", 1000):
                    await self._send_alert("HIGH_MEMORY_USAGE", f"Memory usage: {memory_mb:.1f}MB")
                
                if cpu_percent > self.alert_thresholds.get("cpu_percent", 80):
                    await self._send_alert("HIGH_CPU_USAGE", f"CPU usage: {cpu_percent:.1f}%")
                
                # Record metrics
                self._record_resource_metric(memory_mb, cpu_percent)
                
                await asyncio.sleep(self.config.get("resource_check_interval", 10))
                
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {str(e)}")
                await asyncio.sleep(5)
    
    def _record_response_time_metric(self, response_time: float, success: bool):
        """Record response time metric"""
        
        # Add to metrics buffer for batch processing
        metric = {
            "type": "response_time",
            "value": response_time,
            "success": success,
            "timestamp": datetime.now()
        }
        
        self.metrics_buffer.append(metric)
        
        # Check real-time alerts
        if response_time > self.alert_thresholds.get("response_time_seconds", 10):
            asyncio.create_task(self._send_alert(
                "SLOW_RESPONSE", 
                f"Response time: {response_time:.2f}s"
            ))
    
    async def _send_alert(self, alert_type: str, message: str):
        """Send performance alert"""
        
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now(),
            "severity": self._determine_alert_severity(alert_type)
        }
        
        self.logger.warning(f"Performance Alert [{alert_type}]: {message}")
        
        # In production: send to monitoring system (Slack, PagerDuty, etc.)
        await self._dispatch_alert_to_monitoring_system(alert)
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time performance metrics"""
        
        if not self.metrics_buffer:
            return {"status": "no_data"}
        
        # Calculate metrics from recent buffer
        recent_metrics = [m for m in self.metrics_buffer if 
                         (datetime.now() - m["timestamp"]).total_seconds() < 300]  # Last 5 minutes
        
        if not recent_metrics:
            return {"status": "no_recent_data"}
        
        response_times = [m["value"] for m in recent_metrics if m["type"] == "response_time"]
        
        if response_times:
            return {
                "avg_response_time": statistics.mean(response_times),
                "max_response_time": max(response_times),
                "min_response_time": min(response_times),
                "total_requests": len(response_times),
                "success_rate": sum(1 for m in recent_metrics if m.get("success")) / len(recent_metrics) * 100,
                "timestamp": datetime.now()
            }
        
        return {"status": "no_response_data"}
```

---

## Part 2: Advanced Monitoring & Observability (20 minutes)

### Comprehensive Monitoring Architecture

🗂️ **File**: `src/session2/monitoring_observability.py` - Production monitoring systems

```python
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
import structlog
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from typing import Dict, Any, Optional
import json
from datetime import datetime
import asyncio

class LangChainPrometheusMetrics:
    """Prometheus metrics for LangChain applications"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        
        # Request metrics
        self.request_count = Counter(
            'langchain_requests_total',
            'Total number of requests to LangChain agents',
            ['agent_type', 'status']
        )
        
        self.request_duration = Histogram(
            'langchain_request_duration_seconds',
            'Time spent processing LangChain requests',
            ['agent_type', 'operation'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
        )
        
        # LLM metrics
        self.llm_tokens = Counter(
            'langchain_llm_tokens_total',
            'Total tokens processed by LLM',
            ['model', 'token_type']  # token_type: prompt, completion
        )
        
        self.llm_api_calls = Counter(
            'langchain_llm_api_calls_total',
            'Total API calls to LLM providers',
            ['provider', 'model', 'status']
        )
        
        self.llm_latency = Histogram(
            'langchain_llm_latency_seconds',
            'LLM API call latency',
            ['provider', 'model'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Tool metrics
        self.tool_executions = Counter(
            'langchain_tool_executions_total',
            'Total tool executions',
            ['tool_name', 'status']
        )
        
        self.tool_duration = Histogram(
            'langchain_tool_duration_seconds',
            'Tool execution duration',
            ['tool_name'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
        )
        
        # Memory and caching metrics
        self.cache_operations = Counter(
            'langchain_cache_operations_total',
            'Cache operations',
            ['operation', 'result']  # operation: get, set; result: hit, miss
        )
        
        self.memory_usage = Gauge(
            'langchain_memory_usage_bytes',
            'Current memory usage',
            ['component']
        )
        
        # Error metrics
        self.error_count = Counter(
            'langchain_errors_total',
            'Total errors in LangChain application',
            ['error_type', 'component']
        )
        
        # Quality metrics
        self.response_quality = Histogram(
            'langchain_response_quality_score',
            'Response quality scores',
            ['agent_type', 'metric_type'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
    
    def record_request(self, agent_type: str, status: str, duration: float, operation: str = "run"):
        """Record request metrics"""
        self.request_count.labels(agent_type=agent_type, status=status).inc()
        self.request_duration.labels(agent_type=agent_type, operation=operation).observe(duration)
    
    def record_llm_call(self, provider: str, model: str, status: str, latency: float,
                       prompt_tokens: int, completion_tokens: int):
        """Record LLM-specific metrics"""
        self.llm_api_calls.labels(provider=provider, model=model, status=status).inc()
        self.llm_latency.labels(provider=provider, model=model).observe(latency)
        self.llm_tokens.labels(model=model, token_type="prompt").inc(prompt_tokens)
        self.llm_tokens.labels(model=model, token_type="completion").inc(completion_tokens)
    
    def record_tool_execution(self, tool_name: str, status: str, duration: float):
        """Record tool execution metrics"""
        self.tool_executions.labels(tool_name=tool_name, status=status).inc()
        self.tool_duration.labels(tool_name=tool_name).observe(duration)
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation metrics"""
        self.cache_operations.labels(operation=operation, result=result).inc()
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics"""
        self.error_count.labels(error_type=error_type, component=component).inc()
    
    def update_memory_usage(self, component: str, bytes_used: float):
        """Update memory usage metrics"""
        self.memory_usage.labels(component=component).set(bytes_used)
    
    def record_quality_score(self, agent_type: str, metric_type: str, score: float):
        """Record response quality metrics"""
        self.response_quality.labels(agent_type=agent_type, metric_type=metric_type).observe(score)

class StructuredLogging:
    """Structured logging for LangChain applications"""
    
    def __init__(self, service_name: str, log_level: str = "INFO"):
        self.service_name = service_name
        
        # Configure structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger(service_name)
    
    def log_request(self, request_id: str, agent_type: str, input_text: str, 
                   response: str, duration: float, status: str, **kwargs):
        """Log request with structured data"""
        
        self.logger.info(
            "agent_request_completed",
            request_id=request_id,
            agent_type=agent_type,
            input_length=len(input_text),
            response_length=len(response) if response else 0,
            duration_seconds=duration,
            status=status,
            service=self.service_name,
            **kwargs
        )
    
    def log_llm_call(self, request_id: str, provider: str, model: str, 
                    prompt_tokens: int, completion_tokens: int, latency: float, **kwargs):
        """Log LLM call with structured data"""
        
        self.logger.info(
            "llm_api_call",
            request_id=request_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_seconds=latency,
            cost_estimate=self._calculate_cost_estimate(model, prompt_tokens, completion_tokens),
            service=self.service_name,
            **kwargs
        )
    
    def log_tool_execution(self, request_id: str, tool_name: str, 
                          input_params: Dict[str, Any], result: Any, 
                          duration: float, status: str, **kwargs):
        """Log tool execution with structured data"""
        
        self.logger.info(
            "tool_execution",
            request_id=request_id,
            tool_name=tool_name,
            input_params=input_params,
            result_type=type(result).__name__,
            result_size=len(str(result)) if result else 0,
            duration_seconds=duration,
            status=status,
            service=self.service_name,
            **kwargs
        )
    
    def log_error(self, request_id: str, error_type: str, error_message: str, 
                 component: str, stack_trace: str = None, **kwargs):
        """Log error with structured data"""
        
        self.logger.error(
            "application_error",
            request_id=request_id,
            error_type=error_type,
            error_message=error_message,
            component=component,
            stack_trace=stack_trace,
            service=self.service_name,
            **kwargs
        )
    
    def log_performance_alert(self, alert_type: str, metric_name: str, 
                            current_value: float, threshold: float, **kwargs):
        """Log performance alert"""
        
        self.logger.warning(
            "performance_alert",
            alert_type=alert_type,
            metric_name=metric_name,
            current_value=current_value,
            threshold=threshold,
            service=self.service_name,
            **kwargs
        )
    
    def _calculate_cost_estimate(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost for LLM call"""
        
        # Simplified cost calculation - update with actual pricing
        cost_per_1k_tokens = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "claude-3-sonnet": 0.015,
            "claude-3-haiku": 0.0025
        }
        
        rate = cost_per_1k_tokens.get(model, 0.01)  # Default rate
        total_tokens = prompt_tokens + completion_tokens
        return (total_tokens / 1000) * rate

class DistributedTracing:
    """Distributed tracing for LangChain applications"""
    
    def __init__(self, service_name: str, jaeger_endpoint: str = None):
        self.service_name = service_name
        
        # Initialize tracing
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        
        # Configure Jaeger exporter if endpoint provided
        if jaeger_endpoint:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
        
        self.tracer = tracer
    
    def trace_agent_request(self, request_id: str, agent_type: str):
        """Create trace span for agent request"""
        
        return self.tracer.start_span(
            f"agent_request:{agent_type}",
            attributes={
                "service.name": self.service_name,
                "request.id": request_id,
                "agent.type": agent_type
            }
        )
    
    def trace_llm_call(self, request_id: str, provider: str, model: str):
        """Create trace span for LLM call"""
        
        return self.tracer.start_span(
            f"llm_call:{provider}",
            attributes={
                "service.name": self.service_name,
                "request.id": request_id,
                "llm.provider": provider,
                "llm.model": model
            }
        )
    
    def trace_tool_execution(self, request_id: str, tool_name: str):
        """Create trace span for tool execution"""
        
        return self.tracer.start_span(
            f"tool_execution:{tool_name}",
            attributes={
                "service.name": self.service_name,
                "request.id": request_id,
                "tool.name": tool_name
            }
        )

class MonitoringDashboard:
    """Real-time monitoring dashboard for LangChain applications"""
    
    def __init__(self, metrics: LangChainPrometheusMetrics, 
                 logging: StructuredLogging):
        self.metrics = metrics
        self.logging = logging
        self.dashboard_data = {}
        
    async def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        
        current_time = datetime.now()
        
        # Collect metrics from Prometheus
        dashboard_data = {
            "timestamp": current_time.isoformat(),
            "service_health": await self._get_service_health(),
            "request_metrics": await self._get_request_metrics(),
            "llm_metrics": await self._get_llm_metrics(),
            "tool_metrics": await self._get_tool_metrics(),
            "performance_metrics": await self._get_performance_metrics(),
            "error_metrics": await self._get_error_metrics(),
            "resource_usage": await self._get_resource_usage(),
            "alerts": await self._get_active_alerts()
        }
        
        return dashboard_data
    
    async def _get_service_health(self) -> Dict[str, Any]:
        """Get overall service health status"""
        
        # Calculate health based on error rates and response times
        recent_errors = 0  # Would query from Prometheus
        recent_requests = 100  # Would query from Prometheus
        avg_response_time = 1.5  # Would query from Prometheus
        
        error_rate = recent_errors / recent_requests if recent_requests > 0 else 0
        
        if error_rate > 0.1 or avg_response_time > 10:
            health_status = "unhealthy"
        elif error_rate > 0.05 or avg_response_time > 5:
            health_status = "degraded"
        else:
            health_status = "healthy"
        
        return {
            "status": health_status,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "uptime_percentage": 99.5  # Would calculate from actual data
        }
    
    async def _get_request_metrics(self) -> Dict[str, Any]:
        """Get request-related metrics"""
        
        return {
            "requests_per_minute": 45,  # Would query from Prometheus
            "avg_response_time": 2.1,
            "p95_response_time": 4.5,
            "success_rate": 98.2,
            "concurrent_requests": 12
        }
    
    async def _get_llm_metrics(self) -> Dict[str, Any]:
        """Get LLM-specific metrics"""
        
        return {
            "total_tokens_processed": 125000,  # Would query from Prometheus
            "tokens_per_minute": 2500,
            "avg_llm_latency": 1.8,
            "api_calls_per_minute": 50,
            "cost_per_hour": 12.50,
            "model_distribution": {
                "gpt-4": 60,
                "gpt-3.5-turbo": 40
            }
        }
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        
        return {
            "cpu_usage_percent": 45.2,
            "memory_usage_mb": 512.8,
            "cache_hit_rate": 78.5,
            "throughput_requests_per_second": 0.75
        }
```

---

## Part 3: Cost Optimization & Resource Management (10 minutes)

### Intelligent Cost Management

🗂️ **File**: `src/session2/cost_optimization.py` - Cost optimization strategies

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import json

@dataclass
class CostMetrics:
    """Cost tracking metrics for LangChain applications"""
    
    # Token costs
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_token_cost: float = 0.0
    
    # API call costs
    total_api_calls: int = 0
    total_api_cost: float = 0.0
    
    # Resource costs
    compute_cost_per_hour: float = 0.0
    storage_cost_per_hour: float = 0.0
    
    # Time period
    period_start: datetime = None
    period_end: datetime = None
    
    # Cost breakdown by model
    cost_by_model: Dict[str, float] = None
    
    # Optimization metrics
    cache_savings: float = 0.0
    optimization_savings: float = 0.0

class CostOptimizationManager:
    """Intelligent cost optimization for LangChain applications"""
    
    def __init__(self, cost_config: Dict[str, Any]):
        self.cost_config = cost_config
        self.cost_tracking = {}
        self.optimization_rules = []
        self.cost_alerts = []
        
        # Initialize cost rates
        self.token_costs = cost_config.get("token_costs", {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
            "claude-3-sonnet": {"prompt": 0.015, "completion": 0.015}
        })
        
        self.daily_budget = cost_config.get("daily_budget", 100.0)
        self.monthly_budget = cost_config.get("monthly_budget", 3000.0)
    
    def track_llm_cost(self, model: str, prompt_tokens: int, completion_tokens: int,
                      provider: str = "openai") -> float:
        """Track cost for LLM usage"""
        
        if model not in self.token_costs:
            model = "gpt-3.5-turbo"  # Default fallback
        
        rates = self.token_costs[model]
        prompt_cost = (prompt_tokens / 1000) * rates["prompt"]
        completion_cost = (completion_tokens / 1000) * rates["completion"]
        total_cost = prompt_cost + completion_cost
        
        # Track in daily/monthly buckets
        today = datetime.now().date()
        if today not in self.cost_tracking:
            self.cost_tracking[today] = CostMetrics(
                period_start=datetime.combine(today, datetime.min.time()),
                cost_by_model={}
            )
        
        daily_metrics = self.cost_tracking[today]
        daily_metrics.total_prompt_tokens += prompt_tokens
        daily_metrics.total_completion_tokens += completion_tokens
        daily_metrics.total_token_cost += total_cost
        daily_metrics.total_api_calls += 1
        
        # Track by model
        if model not in daily_metrics.cost_by_model:
            daily_metrics.cost_by_model[model] = 0.0
        daily_metrics.cost_by_model[model] += total_cost
        
        # Check budget alerts
        self._check_budget_alerts(daily_metrics, total_cost)
        
        return total_cost
    
    def _check_budget_alerts(self, daily_metrics: CostMetrics, new_cost: float):
        """Check if budget thresholds are exceeded"""
        
        daily_total = daily_metrics.total_token_cost
        
        # Daily budget alerts
        if daily_total > self.daily_budget * 0.8:  # 80% threshold
            self._create_budget_alert("DAILY_BUDGET_WARNING", daily_total, self.daily_budget)
        
        if daily_total > self.daily_budget:
            self._create_budget_alert("DAILY_BUDGET_EXCEEDED", daily_total, self.daily_budget)
        
        # Monthly budget calculation
        month_start = datetime.now().replace(day=1).date()
        monthly_total = sum(
            metrics.total_token_cost 
            for date, metrics in self.cost_tracking.items()
            if date >= month_start
        )
        
        if monthly_total > self.monthly_budget * 0.8:
            self._create_budget_alert("MONTHLY_BUDGET_WARNING", monthly_total, self.monthly_budget)
    
    def optimize_model_selection(self, task_complexity: str, required_quality: float) -> str:
        """Suggest optimal model based on task requirements and cost"""
        
        model_capabilities = {
            "gpt-4": {"quality": 0.95, "cost_per_1k": 0.045, "speed": 0.7},
            "gpt-3.5-turbo": {"quality": 0.85, "cost_per_1k": 0.002, "speed": 0.9},
            "claude-3-sonnet": {"quality": 0.90, "cost_per_1k": 0.015, "speed": 0.8}
        }
        
        # Filter models that meet quality requirements
        suitable_models = {
            model: specs for model, specs in model_capabilities.items()
            if specs["quality"] >= required_quality
        }
        
        if not suitable_models:
            return "gpt-4"  # Fallback to highest quality
        
        # Simple task complexity scoring
        complexity_weights = {
            "simple": {"cost": 0.7, "speed": 0.3, "quality": 0.0},
            "medium": {"cost": 0.5, "speed": 0.2, "quality": 0.3},
            "complex": {"cost": 0.2, "speed": 0.1, "quality": 0.7}
        }
        
        weights = complexity_weights.get(task_complexity, complexity_weights["medium"])
        
        # Calculate weighted scores
        best_model = None
        best_score = -1
        
        for model, specs in suitable_models.items():
            # Normalize metrics (lower cost is better, higher speed/quality is better)
            cost_score = 1 - (specs["cost_per_1k"] / max(s["cost_per_1k"] for s in suitable_models.values()))
            speed_score = specs["speed"]
            quality_score = specs["quality"]
            
            total_score = (
                cost_score * weights["cost"] +
                speed_score * weights["speed"] +
                quality_score * weights["quality"]
            )
            
            if total_score > best_score:
                best_score = total_score
                best_model = model
        
        return best_model or "gpt-3.5-turbo"
    
    def get_cost_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        
        # Analyze recent cost patterns
        recent_costs = self._get_recent_cost_analysis()
        
        # High-cost model recommendations
        if recent_costs.get("gpt-4_percentage", 0) > 60:
            recommendations.append({
                "type": "model_optimization",
                "priority": "high",
                "title": "Reduce GPT-4 Usage",
                "description": "Consider using GPT-3.5-turbo for simpler tasks",
                "potential_savings": recent_costs.get("gpt-4_cost", 0) * 0.3,
                "implementation": "Implement task complexity analysis"
            })
        
        # Token optimization recommendations
        avg_tokens = recent_costs.get("avg_tokens_per_request", 0)
        if avg_tokens > 2000:
            recommendations.append({
                "type": "prompt_optimization",
                "priority": "medium", 
                "title": "Optimize Prompt Length",
                "description": "Reduce average prompt length to decrease token costs",
                "potential_savings": recent_costs.get("daily_cost", 0) * 0.15,
                "implementation": "Implement prompt compression and caching"
            })
        
        # Caching recommendations
        cache_hit_rate = recent_costs.get("cache_hit_rate", 0)
        if cache_hit_rate < 30:
            recommendations.append({
                "type": "caching_optimization",
                "priority": "high",
                "title": "Improve Caching Strategy", 
                "description": "Implement better caching to reduce redundant API calls",
                "potential_savings": recent_costs.get("daily_cost", 0) * 0.25,
                "implementation": "Add semantic caching and increase cache TTL"
            })
        
        return recommendations
    
    def _get_recent_cost_analysis(self) -> Dict[str, Any]:
        """Analyze recent cost patterns"""
        
        # Get last 7 days of data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        total_cost = 0
        total_tokens = 0
        total_calls = 0
        model_costs = {}
        
        for date in [start_date + timedelta(days=x) for x in range(8)]:
            if date in self.cost_tracking:
                metrics = self.cost_tracking[date]
                total_cost += metrics.total_token_cost
                total_tokens += metrics.total_prompt_tokens + metrics.total_completion_tokens
                total_calls += metrics.total_api_calls
                
                for model, cost in (metrics.cost_by_model or {}).items():
                    model_costs[model] = model_costs.get(model, 0) + cost
        
        return {
            "daily_cost": total_cost / 7,
            "avg_tokens_per_request": total_tokens / total_calls if total_calls > 0 else 0,
            "gpt-4_cost": model_costs.get("gpt-4", 0),
            "gpt-4_percentage": (model_costs.get("gpt-4", 0) / total_cost * 100) if total_cost > 0 else 0,
            "cache_hit_rate": 25  # Would get from actual metrics
        }
    
    def get_cost_dashboard_data(self) -> Dict[str, Any]:
        """Generate cost dashboard data"""
        
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        # Daily costs
        daily_metrics = self.cost_tracking.get(today, CostMetrics())
        
        # Monthly costs
        monthly_cost = sum(
            metrics.total_token_cost 
            for date, metrics in self.cost_tracking.items()
            if date >= month_start
        )
        
        # Cost projections
        days_in_month = (today.replace(month=today.month + 1) - month_start).days
        days_elapsed = (today - month_start).days + 1
        projected_monthly = (monthly_cost / days_elapsed) * days_in_month if days_elapsed > 0 else 0
        
        return {
            "current_costs": {
                "daily": daily_metrics.total_token_cost,
                "monthly": monthly_cost,
                "projected_monthly": projected_monthly
            },
            "budget_status": {
                "daily_budget": self.daily_budget,
                "monthly_budget": self.monthly_budget,
                "daily_utilization": (daily_metrics.total_token_cost / self.daily_budget * 100),
                "monthly_utilization": (monthly_cost / self.monthly_budget * 100)
            },
            "usage_breakdown": {
                "total_tokens": daily_metrics.total_prompt_tokens + daily_metrics.total_completion_tokens,
                "api_calls": daily_metrics.total_api_calls,
                "cost_by_model": daily_metrics.cost_by_model or {}
            },
            "optimization_metrics": {
                "cache_savings": daily_metrics.cache_savings,
                "total_savings": daily_metrics.optimization_savings
            }
        }
```

---

## 🎯 Module Summary

You've now mastered performance optimization and monitoring for production LangChain systems:

✅ **Performance Benchmarking & Optimization**: Implemented comprehensive performance measurement and optimization strategies  
✅ **Advanced Monitoring & Observability**: Set up Prometheus metrics, structured logging, and distributed tracing  
✅ **Cost Optimization & Resource Management**: Created intelligent cost tracking and optimization systems  
✅ **Real-time Dashboards**: Built monitoring dashboards with alerting and performance analytics

### Next Steps
- **Return to Core**: [Session 2 Main](Session2_LangChain_Foundations.md)
- **Advance to Session 3**: [LangGraph Multi-Agent Workflows](Session3_LangGraph_Multi_Agent_Workflows.md)
- **Review Production**: [Module B: Production Deployment Strategies](Session2_ModuleB_Production_Deployment_Strategies.md)

---

**🗂️ Source Files for Module D:**
- `src/session2/performance_benchmarking.py` - Performance measurement and optimization
- `src/session2/monitoring_observability.py` - Comprehensive monitoring systems
- `src/session2/cost_optimization.py` - Cost tracking and optimization strategies