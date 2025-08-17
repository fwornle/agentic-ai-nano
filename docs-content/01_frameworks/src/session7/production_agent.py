"""
Agno Production-Ready Agent Implementation
Session 7: Agno Production-Ready Agents

This module implements a comprehensive production-ready agent with monitoring,
error handling, circuit breakers, health checks, and performance optimization.
"""

import asyncio
import logging
import time
import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import psutil

try:
    from agno import Agent
    from agno.config import AgentConfig
    from agno.monitoring import PrometheusMetrics
    from agno.storage import PostgresStorage
    from agno.resilience import CircuitBreaker, RetryPolicy
    from agno.health import HealthCheck
    import prometheus_client
except ImportError:
    # Fallback implementations for demonstration
    print("Warning: Agno production modules not available, using mock implementations")
    
    class Agent:
        def __init__(self, name: str, model: str = "gpt-4o", **kwargs):
            self.name = name
            self.model = model
            self.config = kwargs
            
        async def run(self, prompt: str) -> 'AgentResponse':
            await asyncio.sleep(0.1)  # Simulate processing
            return AgentResponse(f"Production agent {self.name} processed: {prompt}")
    
    class AgentResponse:
        def __init__(self, content: str):
            self.content = content
            self.processing_time = 0.5
            self.model = "gpt-4o"
            self.input_tokens = 100
            self.output_tokens = 200
            self.total_tokens = 300
            self.cache_hit = False
            self.quality_score = 0.85
    
    class PrometheusMetrics:
        def __init__(self, agent_name: str):
            self.agent_name = agent_name
        
        def increment_requests(self): pass
        def increment_errors(self): pass
        def track_latency(self, latency: float): pass
        def track_cost(self, cost: float): pass
    
    class PostgresStorage:
        def __init__(self, url: str):
            self.url = url
        
        async def log_interaction(self, **kwargs): pass
        async def log_error(self, error: Exception): pass
    
    import prometheus_client

# Configure structured logging
import structlog
logger = structlog.get_logger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class ProductionConfig:
    """Production agent configuration"""
    # Model configuration
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 30
    
    # Performance settings
    max_retries: int = 3
    retry_delay: float = 1.0
    batch_size: int = 10
    
    # Production features
    enable_monitoring: bool = True
    enable_caching: bool = True
    enable_circuit_breaker: bool = True
    log_level: str = "INFO"
    
    # Storage configuration
    storage_backend: str = "postgres"
    storage_url: Optional[str] = None
    
    # Circuit breaker settings
    failure_threshold: int = 5
    success_threshold: int = 3
    circuit_timeout: int = 60
    
    # Health check settings
    health_check_interval: int = 30
    health_failure_threshold: int = 3

@dataclass
class RequestMetrics:
    """Metrics for individual requests"""
    request_id: str
    timestamp: datetime
    processing_time: float
    model_used: str
    tokens_used: int
    cost: float
    success: bool
    error: Optional[str] = None
    cache_hit: bool = False
    quality_score: float = 0.0

@dataclass
class HealthCheckResult:
    """Health check result"""
    status: HealthStatus
    response_time: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class ProductionCircuitBreaker:
    """Production-ready circuit breaker implementation"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 success_threshold: int = 3,
                 timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
    def record_success(self):
        """Record successful operation"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker closed - service recovered")
        else:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.success_count = 0
            logger.warning("Circuit breaker reopened during recovery attempt")
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if (time.time() - self.last_failure_time) >= self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker half-open - attempting recovery")
                return True
            return False
        else:  # HALF_OPEN
            return True

class ProductionHealthMonitor:
    """Comprehensive health monitoring"""
    
    def __init__(self, 
                 check_interval: int = 30,
                 failure_threshold: int = 3):
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        self.consecutive_failures = 0
        self.last_check_time = None
        self.current_status = HealthStatus.HEALTHY
        self.health_history = []
        
    async def perform_health_check(self, agent: 'ProductionAgent') -> HealthCheckResult:
        """Perform comprehensive health check"""
        start_time = time.time()
        
        try:
            # Test basic functionality
            test_response = await agent._execute_with_timeout(
                agent.agent.run("Health check test - respond with OK"),
                timeout=10.0
            )
            
            response_time = time.time() - start_time
            
            # Check system resources
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            # Assess health status
            if response_time > 15.0:
                status = HealthStatus.DEGRADED
                message = f"Slow response time: {response_time:.2f}s"
            elif cpu_percent > 90 or memory_percent > 90:
                status = HealthStatus.DEGRADED
                message = f"High resource usage - CPU: {cpu_percent}%, Memory: {memory_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = "All systems operational"
                self.consecutive_failures = 0
            
            result = HealthCheckResult(
                status=status,
                response_time=response_time,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "agent_name": agent.name,
                    "model": agent.config.model
                }
            )
            
            self.current_status = status
            self.last_check_time = time.time()
            self.health_history.append(result)
            
            # Keep only recent history
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
            return result
            
        except Exception as e:
            self.consecutive_failures += 1
            response_time = time.time() - start_time
            
            if self.consecutive_failures >= self.failure_threshold:
                status = HealthStatus.UNHEALTHY
            else:
                status = HealthStatus.DEGRADED
            
            result = HealthCheckResult(
                status=status,
                response_time=response_time,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e), "consecutive_failures": self.consecutive_failures}
            )
            
            self.current_status = status
            self.health_history.append(result)
            
            return result

class ProductionAgent:
    """
    Production-ready Agno agent with comprehensive monitoring and resilience features
    
    Features:
    - Circuit breaker pattern for fault tolerance
    - Comprehensive metrics collection
    - Health monitoring and alerting
    - Request/response logging
    - Performance optimization
    - Error handling and recovery
    """
    
    def __init__(self, config: ProductionConfig, name: str = "production_agent"):
        """Initialize production agent"""
        self.name = name
        self.config = config
        self.request_count = 0
        self.start_time = datetime.utcnow()
        
        # Initialize monitoring components
        if config.enable_monitoring:
            self.metrics = PrometheusMetrics(agent_name=name)
            self.storage = PostgresStorage(config.storage_url) if config.storage_url else None
        
        # Initialize resilience components
        if config.enable_circuit_breaker:
            self.circuit_breaker = ProductionCircuitBreaker(
                failure_threshold=config.failure_threshold,
                success_threshold=config.success_threshold,
                timeout=config.circuit_timeout
            )
        
        # Initialize health monitoring
        self.health_monitor = ProductionHealthMonitor(
            check_interval=config.health_check_interval,
            failure_threshold=config.health_failure_threshold
        )
        
        # Request history for analysis
        self.request_history = []
        self.error_history = []
        
        # Initialize the underlying agent
        try:
            self.agent = Agent(
                name=self.name,
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            logger.info(f"Initialized production agent: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize production agent: {e}")
            raise
        
        # Start background monitoring
        if config.enable_monitoring:
            asyncio.create_task(self._start_health_monitoring())
    
    async def process_request(self, 
                            request: str, 
                            context: Optional[Dict] = None,
                            priority: int = 1) -> Dict[str, Any]:
        """
        Process request with full production monitoring and error handling
        
        Args:
            request: The request to process
            context: Optional context information
            priority: Request priority (1-10, higher is more priority)
            
        Returns:
            Complete response with metrics and metadata
        """
        request_id = self._generate_request_id()
        start_time = datetime.utcnow()
        
        # Log request start
        logger.info("Processing request", 
                   request_id=request_id, 
                   agent=self.name,
                   priority=priority)
        
        try:
            # Check circuit breaker
            if (hasattr(self, 'circuit_breaker') and 
                not self.circuit_breaker.can_execute()):
                raise Exception("Circuit breaker open - service unavailable")
            
            # Execute request with monitoring
            response = await self._execute_with_monitoring(request, context)
            
            # Record success metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            if hasattr(self, 'circuit_breaker'):
                self.circuit_breaker.record_success()
            
            if hasattr(self, 'metrics'):
                self.metrics.increment_requests()
                self.metrics.track_latency(processing_time)
                self.metrics.track_cost(self._calculate_request_cost(response))
            
            # Store interaction
            if hasattr(self, 'storage') and self.storage:
                await self.storage.log_interaction(
                    request_id=request_id,
                    agent_name=self.name,
                    request=request,
                    response=response.content,
                    processing_time=processing_time,
                    success=True,
                    timestamp=start_time
                )
            
            # Track metrics
            metrics = RequestMetrics(
                request_id=request_id,
                timestamp=start_time,
                processing_time=processing_time,
                model_used=response.model,
                tokens_used=getattr(response, 'total_tokens', 0),
                cost=self._calculate_request_cost(response),
                success=True,
                cache_hit=getattr(response, 'cache_hit', False),
                quality_score=getattr(response, 'quality_score', 0.8)
            )
            
            self.request_history.append(metrics)
            self.request_count += 1
            
            logger.info("Request completed successfully", 
                       request_id=request_id,
                       processing_time=processing_time,
                       tokens_used=metrics.tokens_used)
            
            return {
                "request_id": request_id,
                "success": True,
                "response": response.content,
                "metadata": {
                    "processing_time": processing_time,
                    "model_used": response.model,
                    "tokens_used": metrics.tokens_used,
                    "cost": metrics.cost,
                    "cache_hit": metrics.cache_hit,
                    "quality_score": metrics.quality_score,
                    "agent_name": self.name,
                    "timestamp": start_time.isoformat()
                }
            }
            
        except Exception as e:
            # Handle errors with full monitoring
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            if hasattr(self, 'circuit_breaker'):
                self.circuit_breaker.record_failure()
            
            if hasattr(self, 'metrics'):
                self.metrics.increment_errors()
            
            # Store error
            if hasattr(self, 'storage') and self.storage:
                await self.storage.log_error(e)
            
            # Track error metrics
            error_metrics = RequestMetrics(
                request_id=request_id,
                timestamp=start_time,
                processing_time=processing_time,
                model_used=self.config.model,
                tokens_used=0,
                cost=0.0,
                success=False,
                error=str(e)
            )
            
            self.error_history.append(error_metrics)
            
            logger.error("Request failed", 
                        request_id=request_id,
                        error=str(e),
                        processing_time=processing_time)
            
            return {
                "request_id": request_id,
                "success": False,
                "error": str(e),
                "metadata": {
                    "processing_time": processing_time,
                    "agent_name": self.name,
                    "timestamp": start_time.isoformat(),
                    "circuit_breaker_state": (
                        self.circuit_breaker.state.value 
                        if hasattr(self, 'circuit_breaker') else "disabled"
                    )
                }
            }
    
    async def _execute_with_monitoring(self, request: str, context: Optional[Dict]) -> Any:
        """Execute request with comprehensive monitoring"""
        
        # Add context to request if provided
        if context:
            enhanced_request = f"Context: {json.dumps(context)}\n\nRequest: {request}"
        else:
            enhanced_request = request
        
        # Execute with retry policy
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Execute with timeout
                result = await self._execute_with_timeout(
                    self.agent.run(enhanced_request),
                    timeout=self.config.timeout
                )
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s",
                                 error=str(e))
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All retry attempts failed", error=str(e))
        
        raise last_exception
    
    async def _execute_with_timeout(self, coro, timeout: float):
        """Execute coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise Exception(f"Request timed out after {timeout} seconds")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = str(int(time.time() * 1000000))
        counter = str(self.request_count)
        return hashlib.md5(f"{self.name}_{timestamp}_{counter}".encode()).hexdigest()[:12]
    
    def _calculate_request_cost(self, response) -> float:
        """Calculate cost for request based on token usage"""
        # Simplified cost calculation - in production, use actual pricing
        input_tokens = getattr(response, 'input_tokens', 100)
        output_tokens = getattr(response, 'output_tokens', 200)
        
        # Example pricing (per 1K tokens)
        input_cost_per_1k = 0.01  # $0.01 per 1K input tokens
        output_cost_per_1k = 0.03  # $0.03 per 1K output tokens
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return round(input_cost + output_cost, 6)
    
    async def _start_health_monitoring(self):
        """Start background health monitoring"""
        while True:
            try:
                health_result = await self.health_monitor.perform_health_check(self)
                
                if health_result.status == HealthStatus.UNHEALTHY:
                    logger.error("Agent health check failed", 
                               status=health_result.status.value,
                               message=health_result.message)
                elif health_result.status == HealthStatus.DEGRADED:
                    logger.warning("Agent health degraded", 
                                 message=health_result.message)
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error("Health monitoring error", error=str(e))
                await asyncio.sleep(self.config.health_check_interval)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        health_result = await self.health_monitor.perform_health_check(self)
        
        return {
            "status": health_result.status.value,
            "message": health_result.message,
            "response_time": health_result.response_time,
            "details": health_result.details,
            "timestamp": health_result.timestamp.isoformat(),
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "requests_processed": self.request_count,
            "circuit_breaker_state": (
                self.circuit_breaker.state.value 
                if hasattr(self, 'circuit_breaker') else "disabled"
            )
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        if not self.request_history:
            return {"error": "No request history available"}
        
        successful_requests = [r for r in self.request_history if r.success]
        failed_requests = [r for r in self.request_history if not r.success]
        
        if successful_requests:
            avg_processing_time = sum(r.processing_time for r in successful_requests) / len(successful_requests)
            avg_tokens = sum(r.tokens_used for r in successful_requests) / len(successful_requests)
            total_cost = sum(r.cost for r in successful_requests)
            cache_hits = len([r for r in successful_requests if r.cache_hit])
        else:
            avg_processing_time = 0
            avg_tokens = 0
            total_cost = 0
            cache_hits = 0
        
        return {
            "agent_name": self.name,
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "total_requests": len(self.request_history),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / len(self.request_history) if self.request_history else 0,
            "average_processing_time": avg_processing_time,
            "average_tokens_per_request": avg_tokens,
            "total_cost": total_cost,
            "cache_hit_rate": cache_hits / len(successful_requests) if successful_requests else 0,
            "current_health": self.health_monitor.current_status.value,
            "circuit_breaker_state": (
                self.circuit_breaker.state.value 
                if hasattr(self, 'circuit_breaker') else "disabled"
            )
        }
    
    async def batch_process(self, requests: List[str], context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Process multiple requests efficiently"""
        logger.info(f"Starting batch processing of {len(requests)} requests")
        
        # Limit concurrency to prevent overwhelming the system
        semaphore = asyncio.Semaphore(self.config.batch_size)
        
        async def process_single(request):
            async with semaphore:
                return await self.process_request(request, context)
        
        # Process all requests concurrently
        tasks = [process_single(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "request_id": f"batch_error_{i}",
                    "success": False,
                    "error": str(result),
                    "metadata": {
                        "agent_name": self.name,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
            else:
                processed_results.append(result)
        
        successful = len([r for r in processed_results if r["success"]])
        logger.info(f"Batch processing complete: {successful}/{len(requests)} successful")
        
        return processed_results

async def demonstrate_production_agent():
    """Demonstrate production agent capabilities"""
    print("=" * 80)
    print("AGNO PRODUCTION AGENT DEMONSTRATION")
    print("=" * 80)
    
    # Create production configuration
    config = ProductionConfig(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=1024,
        timeout=30,
        max_retries=3,
        enable_monitoring=True,
        enable_caching=True,
        enable_circuit_breaker=True,
        health_check_interval=10  # Faster for demo
    )
    
    # Initialize production agent
    production_agent = ProductionAgent(config, "demo_production_agent")
    
    print(f"\n1. Production Agent Initialization")
    print("-" * 50)
    print(f"Agent Name: {production_agent.name}")
    print(f"Model: {config.model}")
    print(f"Circuit Breaker: {config.enable_circuit_breaker}")
    print(f"Monitoring: {config.enable_monitoring}")
    print(f"Max Retries: {config.max_retries}")
    
    # Single request processing
    print(f"\n2. Single Request Processing")
    print("-" * 40)
    
    request = "Analyze the benefits of using production-ready AI agents in enterprise environments"
    context = {"department": "engineering", "priority": "high"}
    
    result = await production_agent.process_request(request, context, priority=8)
    
    print(f"Request ID: {result['request_id']}")
    print(f"Success: {result['success']}")
    print(f"Processing Time: {result['metadata']['processing_time']:.3f}s")
    print(f"Model Used: {result['metadata']['model_used']}")
    print(f"Tokens Used: {result['metadata']['tokens_used']}")
    print(f"Cost: ${result['metadata']['cost']:.6f}")
    print(f"Response Length: {len(result['response'])} characters")
    
    # Batch processing demonstration
    print(f"\n3. Batch Processing")
    print("-" * 30)
    
    batch_requests = [
        "What are the key advantages of AI agents?",
        "How do you implement proper error handling?",
        "What metrics are important for production systems?",
        "How do you ensure system reliability?",
        "What are best practices for monitoring?"
    ]
    
    batch_results = await production_agent.batch_process(batch_requests)
    
    successful_batch = [r for r in batch_results if r["success"]]
    print(f"Batch Results: {len(successful_batch)}/{len(batch_requests)} successful")
    
    if successful_batch:
        avg_time = sum(r["metadata"]["processing_time"] for r in successful_batch) / len(successful_batch)
        total_cost = sum(r["metadata"]["cost"] for r in successful_batch)
        print(f"Average Processing Time: {avg_time:.3f}s")
        print(f"Total Batch Cost: ${total_cost:.6f}")
    
    # Health status check
    print(f"\n4. Health Status Check")
    print("-" * 35)
    
    health_status = await production_agent.get_health_status()
    print(f"Health Status: {health_status['status']}")
    print(f"Message: {health_status['message']}")
    print(f"Response Time: {health_status['response_time']:.3f}s")
    print(f"Uptime: {health_status['uptime']:.1f}s")
    print(f"Requests Processed: {health_status['requests_processed']}")
    print(f"Circuit Breaker: {health_status['circuit_breaker_state']}")
    
    # Performance metrics
    print(f"\n5. Performance Metrics")
    print("-" * 35)
    
    metrics = production_agent.get_performance_metrics()
    print(f"Total Requests: {metrics['total_requests']}")
    print(f"Success Rate: {metrics['success_rate']:.1%}")
    print(f"Avg Processing Time: {metrics['average_processing_time']:.3f}s")
    print(f"Avg Tokens/Request: {metrics['average_tokens_per_request']:.0f}")
    print(f"Total Cost: ${metrics['total_cost']:.6f}")
    print(f"Cache Hit Rate: {metrics['cache_hit_rate']:.1%}")
    
    # Error simulation and circuit breaker demo
    print(f"\n6. Error Handling & Circuit Breaker")
    print("-" * 45)
    
    # Simulate some failures to test circuit breaker
    print("Simulating failures to test circuit breaker...")
    
    # Force some failures by using invalid requests
    for i in range(3):
        try:
            await production_agent.process_request("", None)  # Empty request might fail
        except:
            pass
    
    # Check circuit breaker state
    final_health = await production_agent.get_health_status()
    final_metrics = production_agent.get_performance_metrics()
    
    print(f"Final Circuit Breaker State: {final_health['circuit_breaker_state']}")
    print(f"Final Success Rate: {final_metrics['success_rate']:.1%}")
    print(f"Total Failed Requests: {final_metrics['failed_requests']}")
    
    print(f"\n" + "=" * 80)
    print("PRODUCTION AGENT DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Production Features Demonstrated:")
    print("- Comprehensive error handling and retry logic")
    print("- Circuit breaker pattern for fault tolerance")
    print("- Health monitoring and status reporting")
    print("- Performance metrics collection and analysis")
    print("- Batch processing with concurrency control")
    print("- Request/response logging and cost tracking")
    print("- Production-ready configuration management")

if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key-here")
    
    # Run demonstration
    asyncio.run(demonstrate_production_agent())