# ⚙️ Session 4 Advanced: Enterprise Resilience Patterns - Bulletproof Production Systems

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths
> Time Investment: 3-4 hours
> Outcome: Master enterprise resilience patterns including circuit breakers, chaos engineering, and production resilience testing

## Advanced Learning Outcomes

After completing this module, you will master:

- Circuit breaker patterns for cascade failure prevention  
- Chaos engineering principles for proactive resilience testing  
- Blue-green deployment strategies for zero-downtime updates  
- Production load testing frameworks for capacity validation  

## Circuit Breaker Pattern Implementation

### The Foundation of Resilient Systems

Circuit breakers are your first line of defense against cascade failures in production systems. They prevent a failing service from bringing down your entire system by automatically detecting failures and temporarily blocking requests to failing services.

Here's a comprehensive circuit breaker implementation designed for production MCP servers:

```python
# resilience/circuit_breaker.py - Production Circuit Breaker Implementation
import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

# Production logging setup
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation, monitoring for failures
    OPEN = "open"          # Blocking requests, service is failing
    HALF_OPEN = "half_open"  # Testing recovery, limited requests allowed

@dataclass
class CircuitBreakerMetrics:
    """Comprehensive metrics for circuit breaker monitoring."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeouts: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
```

### Advanced Circuit Breaker Implementation

```python
class ProductionCircuitBreaker:
    """
    Production Circuit Breaker: Your Defense Against Cascade Failures

    This implementation provides:
    - Intelligent failure detection with sliding time windows
    - Exponential backoff for recovery attempts
    - Comprehensive metrics and logging
    - Configurable fallback response generation
    - Integration with monitoring systems
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 3,
        timeout_duration: float = 10.0,
        monitoring_window: int = 300  # 5 minutes
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.timeout_duration = timeout_duration
        self.monitoring_window = monitoring_window

        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.last_failure_time = None
        self.failure_count = 0
        self.success_count = 0

        # Failure tracking with sliding window
        self.recent_failures: List[datetime] = []

        # Prometheus metrics integration
        self._setup_metrics()

    def _setup_metrics(self):
        """Initialize Prometheus metrics for comprehensive monitoring."""
        from prometheus_client import Counter, Gauge, Histogram

        self.request_counter = Counter(
            'circuit_breaker_requests_total',
            'Total requests through circuit breaker',
            ['circuit_name', 'state', 'outcome']
        )

        self.state_gauge = Gauge(
            'circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['circuit_name']
        )

        self.failure_rate = Gauge(
            'circuit_breaker_failure_rate',
            'Current failure rate percentage',
            ['circuit_name']
        )
```

### Core Circuit Breaker Logic

The main call method orchestrates all circuit breaker functionality:

```python
async def call(self, operation: Callable, *args, **kwargs) -> Any:
    """
    Execute operation with circuit breaker protection.

    This method handles:
    - State management (CLOSED, OPEN, HALF_OPEN)
    - Failure detection and counting
    - Automatic recovery attempts
    - Fallback response generation
    - Comprehensive metrics collection
    """
    # Update state based on current conditions
    await self._update_state()

    # Handle different circuit states
    if self.state == CircuitState.OPEN:
        return await self._handle_open_circuit(operation)

    elif self.state == CircuitState.HALF_OPEN:
        return await self._handle_half_open_circuit(operation, *args, **kwargs)

    else:  # CLOSED state
        return await self._handle_closed_circuit(operation, *args, **kwargs)

async def _handle_closed_circuit(self, operation: Callable, *args, **kwargs) -> Any:
    """Handle requests when circuit is closed (normal operation)."""
    try:
        # Execute operation with timeout protection
        result = await asyncio.wait_for(
            operation(*args, **kwargs),
            timeout=self.timeout_duration
        )

        # Record successful execution
        await self._record_success()
        self.request_counter.labels(
            circuit_name=self.name,
            state='closed',
            outcome='success'
        ).inc()

        logger.debug(f"Circuit breaker {self.name}: Successful execution")
        return result

    except asyncio.TimeoutError:
        await self._record_timeout()
        raise CircuitBreakerTimeoutError(
            f"Operation timed out after {self.timeout_duration}s"
        )

    except Exception as e:
        await self._record_failure(e)
        raise
```

Handle open circuit state with intelligent fallback:

```python
async def _handle_open_circuit(self, operation: Callable) -> Any:
    """Handle requests when circuit is open (blocking requests)."""

    self.request_counter.labels(
        circuit_name=self.name,
        state='open',
        outcome='blocked'
    ).inc()

    logger.warning(
        f"Circuit breaker {self.name}: Request blocked - circuit is OPEN",
        failure_count=self.failure_count,
        last_failure=self.last_failure_time
    )

    # Generate intelligent fallback response
    fallback_response = await self._generate_fallback_response(operation)
    if fallback_response is not None:
        return fallback_response

    # No fallback available - raise circuit breaker exception
    raise CircuitBreakerOpenError(
        f"Circuit breaker {self.name} is OPEN. "
        f"Service has failed {self.failure_count} times. "
        f"Next retry in {self._time_until_retry()}s"
    )

async def _handle_half_open_circuit(self, operation: Callable, *args, **kwargs) -> Any:
    """Handle requests when circuit is half-open (testing recovery)."""
    try:
        # Allow limited requests to test service recovery
        logger.info(f"Circuit breaker {self.name}: Testing service recovery")

        result = await asyncio.wait_for(
            operation(*args, **kwargs),
            timeout=self.timeout_duration
        )

        # Success in half-open state
        await self._record_recovery_success()
        self.request_counter.labels(
            circuit_name=self.name,
            state='half_open',
            outcome='success'
        ).inc()

        return result

    except Exception as e:
        # Failure in half-open state - back to open
        await self._record_recovery_failure(e)
        raise
```

### State Management and Recovery Logic

Intelligent state transitions based on failure patterns:

```python
async def _update_state(self):
    """Update circuit breaker state based on current conditions."""
    current_time = datetime.now()

    # Clean old failures from sliding window
    self._clean_old_failures()

    if self.state == CircuitState.CLOSED:
        # Check if we should open the circuit
        if self._should_open_circuit():
            await self._open_circuit()

    elif self.state == CircuitState.OPEN:
        # Check if we should attempt recovery
        if self._should_attempt_recovery():
            await self._transition_to_half_open()

    elif self.state == CircuitState.HALF_OPEN:
        # Circuit will close automatically on sufficient successes
        # or open automatically on any failure
        pass

def _should_open_circuit(self) -> bool:
    """Determine if circuit should be opened based on failure patterns."""
    # Multiple failure detection strategies

    # Strategy 1: Consecutive failures
    if self.metrics.consecutive_failures >= self.failure_threshold:
        logger.warning(
            f"Circuit breaker {self.name}: Opening due to consecutive failures",
            consecutive_failures=self.metrics.consecutive_failures,
            threshold=self.failure_threshold
        )
        return True

    # Strategy 2: Failure rate in sliding window
    if len(self.recent_failures) >= self.failure_threshold:
        window_start = datetime.now() - timedelta(seconds=self.monitoring_window)
        recent_failure_count = sum(
            1 for failure_time in self.recent_failures
            if failure_time >= window_start
        )

        if recent_failure_count >= self.failure_threshold:
            failure_rate = (recent_failure_count / self.metrics.total_requests) * 100
            logger.warning(
                f"Circuit breaker {self.name}: Opening due to high failure rate",
                failure_rate=f"{failure_rate:.2f}%",
                recent_failures=recent_failure_count,
                threshold=self.failure_threshold
            )
            return True

    return False

def _should_attempt_recovery(self) -> bool:
    """Check if enough time has passed to attempt recovery."""
    if self.last_failure_time is None:
        return True

    time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()

    # Exponential backoff for recovery attempts
    backoff_time = self.recovery_timeout * (2 ** min(self.metrics.circuit_opens - 1, 5))

    return time_since_failure >= backoff_time
```

### Metrics and State Recording

Comprehensive tracking for observability and debugging:

```python
async def _record_success(self):
    """Record successful operation execution."""
    self.metrics.successful_requests += 1
    self.metrics.total_requests += 1
    self.metrics.consecutive_successes += 1
    self.metrics.consecutive_failures = 0
    self.metrics.last_success_time = datetime.now()

    # Reset success counter in half-open state
    if self.state == CircuitState.HALF_OPEN:
        self.success_count += 1

        # Close circuit if enough successes
        if self.success_count >= self.success_threshold:
            await self._close_circuit()

async def _record_failure(self, exception: Exception):
    """Record failed operation execution."""
    current_time = datetime.now()

    self.metrics.failed_requests += 1
    self.metrics.total_requests += 1
    self.metrics.consecutive_failures += 1
    self.metrics.consecutive_successes = 0
    self.metrics.last_failure_time = current_time

    # Track recent failures for sliding window analysis
    self.recent_failures.append(current_time)

    # Update failure rate metrics
    if self.metrics.total_requests > 0:
        failure_rate = (self.metrics.failed_requests / self.metrics.total_requests) * 100
        self.failure_rate.labels(circuit_name=self.name).set(failure_rate)

    self.request_counter.labels(
        circuit_name=self.name,
        state=self.state.value,
        outcome='failure'
    ).inc()

    logger.error(
        f"Circuit breaker {self.name}: Operation failed",
        error=str(exception),
        consecutive_failures=self.metrics.consecutive_failures,
        total_failures=self.metrics.failed_requests
    )

async def _record_timeout(self):
    """Record timeout as a special type of failure."""
    self.metrics.timeouts += 1
    await self._record_failure(asyncio.TimeoutError("Operation timeout"))

async def _open_circuit(self):
    """Transition circuit to OPEN state."""
    self.state = CircuitState.OPEN
    self.metrics.circuit_opens += 1
    self.last_failure_time = datetime.now()

    self.state_gauge.labels(circuit_name=self.name).set(1)

    logger.error(
        f"Circuit breaker {self.name}: Circuit OPENED",
        total_failures=self.metrics.failed_requests,
        failure_rate=f"{(self.metrics.failed_requests / max(self.metrics.total_requests, 1)) * 100:.2f}%"
    )

async def _close_circuit(self):
    """Transition circuit to CLOSED state."""
    self.state = CircuitState.CLOSED
    self.metrics.circuit_closes += 1
    self.failure_count = 0
    self.success_count = 0

    self.state_gauge.labels(circuit_name=self.name).set(0)

    logger.info(
        f"Circuit breaker {self.name}: Circuit CLOSED - Service recovered",
        recovery_successes=self.metrics.consecutive_successes
    )

async def _transition_to_half_open(self):
    """Transition circuit to HALF_OPEN state."""
    self.state = CircuitState.HALF_OPEN
    self.success_count = 0

    self.state_gauge.labels(circuit_name=self.name).set(2)

    logger.info(
        f"Circuit breaker {self.name}: Circuit HALF_OPEN - Testing recovery",
        time_since_failure=self._time_since_last_failure()
    )
```

### Fallback Response Generation

Intelligent fallback responses for different operation types:

```python
async def _generate_fallback_response(self, operation: Callable) -> Optional[Any]:
    """Generate intelligent fallback responses based on operation type."""

    # Check if operation has custom fallback
    if hasattr(operation, '__circuit_breaker_fallback__'):
        try:
            return await operation.__circuit_breaker_fallback__()
        except Exception as e:
            logger.warning(f"Fallback function failed: {e}")

    # Generate default fallbacks based on operation name/type
    operation_name = getattr(operation, '__name__', 'unknown')

    if 'health' in operation_name.lower():
        return {
            "status": "degraded",
            "message": "Service temporarily unavailable",
            "circuit_breaker": "open",
            "timestamp": datetime.now().isoformat()
        }

    elif 'process' in operation_name.lower() or 'data' in operation_name.lower():
        return {
            "error": "Service temporarily unavailable",
            "fallback": True,
            "retry_after": self._time_until_retry(),
            "circuit_breaker_status": self.state.value
        }

    # No suitable fallback
    return None

def _time_until_retry(self) -> int:
    """Calculate seconds until next retry attempt."""
    if self.last_failure_time is None:
        return 0

    time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
    backoff_time = self.recovery_timeout * (2 ** min(self.metrics.circuit_opens - 1, 5))

    return max(0, int(backoff_time - time_since_failure))

def _clean_old_failures(self):
    """Remove failures outside the monitoring window."""
    cutoff_time = datetime.now() - timedelta(seconds=self.monitoring_window)
    self.recent_failures = [
        failure_time for failure_time in self.recent_failures
        if failure_time >= cutoff_time
    ]
```

## Chaos Engineering for Production Resilience

### Proactive Resilience Testing

Chaos engineering is the practice of intentionally introducing failures into your production system to identify weaknesses before they cause actual outages. Here's how to implement safe, controlled chaos testing:

```python
# chaos/chaos_engineer.py - Production Chaos Engineering Framework
import asyncio
import random
import logging
from typing import List, Dict, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ChaosExperimentType(Enum):
    NETWORK_LATENCY = "network_latency"
    SERVICE_FAILURE = "service_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"

@dataclass
class ChaosExperiment:
    """Definition of a chaos engineering experiment."""
    name: str
    experiment_type: ChaosExperimentType
    target_service: str
    duration_seconds: int
    intensity: float  # 0.0 to 1.0
    conditions: Dict[str, Any]
    safety_checks: List[Callable]
    rollback_plan: Callable

class ProductionChaosEngineer:
    """
    Production Chaos Engineering: Controlled Failure Introduction

    This system provides:
    - Safe, controlled failure introduction
    - Comprehensive safety checks and rollback mechanisms
    - Real-time monitoring and automatic experiment termination
    - Detailed experiment reporting and analysis
    """

    def __init__(self, monitoring_system, circuit_breakers: Dict[str, ProductionCircuitBreaker]):
        self.monitoring_system = monitoring_system
        self.circuit_breakers = circuit_breakers
        self.active_experiments: List[ChaosExperiment] = []
        self.experiment_results: List[Dict] = []

    async def run_experiment(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """Execute a controlled chaos engineering experiment."""

        experiment_id = f"{experiment.name}_{int(time.time())}"
        start_time = datetime.now()

        logger.info(
            f"Starting chaos experiment: {experiment.name}",
            experiment_id=experiment_id,
            target=experiment.target_service,
            duration=experiment.duration_seconds
        )

        # Pre-experiment safety checks
        if not await self._safety_checks_pass(experiment):
            logger.error(f"Safety checks failed for experiment {experiment.name}")
            return {"status": "aborted", "reason": "safety_checks_failed"}

        # Record baseline metrics
        baseline_metrics = await self._collect_baseline_metrics(experiment)

        try:
            # Start the experiment
            self.active_experiments.append(experiment)
            experiment_task = asyncio.create_task(
                self._execute_experiment(experiment, experiment_id)
            )

            # Monitor experiment progress
            monitoring_task = asyncio.create_task(
                self._monitor_experiment(experiment, experiment_id)
            )

            # Wait for experiment completion or early termination
            done, pending = await asyncio.wait(
                [experiment_task, monitoring_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()

            # Collect results
            end_time = datetime.now()
            final_metrics = await self._collect_final_metrics(experiment)

            result = {
                "experiment_id": experiment_id,
                "name": experiment.name,
                "status": "completed",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": (end_time - start_time).total_seconds(),
                "baseline_metrics": baseline_metrics,
                "final_metrics": final_metrics,
                "impact_analysis": self._analyze_impact(baseline_metrics, final_metrics)
            }

            self.experiment_results.append(result)
            return result

        except Exception as e:
            logger.error(f"Experiment {experiment.name} failed", error=str(e))
            await self._emergency_rollback(experiment)

            return {
                "experiment_id": experiment_id,
                "status": "failed",
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }

        finally:
            # Cleanup
            if experiment in self.active_experiments:
                self.active_experiments.remove(experiment)

            # Execute rollback plan
            await experiment.rollback_plan()
```

### Specific Chaos Experiments

Implementation of different types of chaos experiments:

```python
async def _execute_network_latency_experiment(
    self,
    experiment: ChaosExperiment,
    experiment_id: str
):
    """Introduce network latency to test timeout handling."""

    target_delay = experiment.intensity * 5.0  # Max 5 second delay

    # Monkey patch network calls to add latency
    original_aiohttp_request = aiohttp.ClientSession._request

    async def delayed_request(self, method, url, **kwargs):
        # Add random latency
        delay = random.uniform(0, target_delay)
        await asyncio.sleep(delay)
        return await original_aiohttp_request(self, method, url, **kwargs)

    # Apply the chaos
    aiohttp.ClientSession._request = delayed_request

    logger.info(
        f"Network latency experiment active",
        experiment_id=experiment_id,
        max_delay=target_delay
    )

    # Run for specified duration
    await asyncio.sleep(experiment.duration_seconds)

    # Restore original behavior
    aiohttp.ClientSession._request = original_aiohttp_request

    logger.info(f"Network latency experiment completed", experiment_id=experiment_id)

async def _execute_service_failure_experiment(
    self,
    experiment: ChaosExperiment,
    experiment_id: str
):
    """Simulate service failures to test circuit breaker behavior."""

    failure_rate = experiment.intensity  # 0.0 to 1.0
    target_service = experiment.target_service

    if target_service not in self.circuit_breakers:
        logger.error(f"No circuit breaker found for {target_service}")
        return

    circuit_breaker = self.circuit_breakers[target_service]

    # Override circuit breaker to inject failures
    original_call = circuit_breaker.call

    async def failing_call(operation, *args, **kwargs):
        if random.random() < failure_rate:
            logger.debug(f"Chaos: Injecting failure in {target_service}")
            raise Exception(f"Chaos experiment failure: {experiment_id}")
        return await original_call(operation, *args, **kwargs)

    circuit_breaker.call = failing_call

    logger.info(
        f"Service failure experiment active",
        experiment_id=experiment_id,
        failure_rate=f"{failure_rate * 100:.1f}%"
    )

    await asyncio.sleep(experiment.duration_seconds)

    # Restore original behavior
    circuit_breaker.call = original_call

    logger.info(f"Service failure experiment completed", experiment_id=experiment_id)
```

## Blue-Green Deployment Strategy

### Zero-Downtime Production Updates

Blue-green deployment is a technique that reduces downtime and risk by running two identical production environments called Blue and Green:

```python
# deployment/blue_green.py - Zero-Downtime Deployment System
import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import aiohttp
import time

logger = logging.getLogger(__name__)

class DeploymentEnvironment(Enum):
    BLUE = "blue"
    GREEN = "green"

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class EnvironmentHealth:
    """Health status of a deployment environment."""
    environment: DeploymentEnvironment
    status: HealthStatus
    response_time: float
    error_rate: float
    last_check: datetime
    details: Dict[str, Any]

class BlueGreenDeploymentManager:
    """
    Blue-Green Deployment: Zero-Downtime Production Updates

    This system manages:
    - Dual environment orchestration
    - Health validation and traffic switching
    - Automatic rollback on deployment failure
    - Comprehensive deployment monitoring
    """

    def __init__(
        self,
        blue_endpoint: str,
        green_endpoint: str,
        load_balancer_api: str,
        health_check_path: str = "/health"
    ):
        self.blue_endpoint = blue_endpoint
        self.green_endpoint = green_endpoint
        self.load_balancer_api = load_balancer_api
        self.health_check_path = health_check_path

        self.current_active = DeploymentEnvironment.BLUE
        self.deployment_in_progress = False

    async def deploy_new_version(
        self,
        version: str,
        deployment_artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy new version using blue-green strategy."""

        if self.deployment_in_progress:
            raise Exception("Deployment already in progress")

        self.deployment_in_progress = True
        deployment_start = time.time()

        # Determine target environment
        target_env = (DeploymentEnvironment.GREEN
                     if self.current_active == DeploymentEnvironment.BLUE
                     else DeploymentEnvironment.BLUE)

        logger.info(
            f"Starting blue-green deployment",
            version=version,
            current_active=self.current_active.value,
            target_environment=target_env.value
        )

        try:
            # Phase 1: Deploy to target environment
            await self._deploy_to_environment(target_env, version, deployment_artifacts)

            # Phase 2: Health validation
            health_check_passed = await self._validate_environment_health(
                target_env,
                required_checks=5,
                timeout_minutes=5
            )

            if not health_check_passed:
                raise Exception(f"Health checks failed for {target_env.value} environment")

            # Phase 3: Gradual traffic shift
            await self._perform_gradual_traffic_shift(target_env)

            # Phase 4: Final validation
            final_health = await self._validate_environment_health(
                target_env,
                required_checks=3,
                timeout_minutes=2
            )

            if not final_health:
                # Rollback immediately
                await self._rollback_traffic()
                raise Exception("Final health check failed - deployment rolled back")

            # Success - update active environment
            old_active = self.current_active
            self.current_active = target_env

            # Phase 5: Cleanup old environment
            await self._cleanup_old_environment(old_active)

            deployment_time = time.time() - deployment_start

            result = {
                "status": "success",
                "version": version,
                "old_environment": old_active.value,
                "new_environment": target_env.value,
                "deployment_time": deployment_time,
                "rollback_available": True
            }

            logger.info(
                "Blue-green deployment completed successfully",
                **result
            )

            return result

        except Exception as e:
            logger.error(f"Deployment failed: {e}")

            # Emergency rollback
            await self._emergency_rollback(target_env)

            return {
                "status": "failed",
                "error": str(e),
                "deployment_time": time.time() - deployment_start,
                "rollback_completed": True
            }

        finally:
            self.deployment_in_progress = False
```

### Traffic Shifting and Health Validation

The core logic for safe traffic transitions:

```python
async def _perform_gradual_traffic_shift(self, target_env: DeploymentEnvironment) -> None:
    """Perform gradual traffic shift with monitoring."""

    # Traffic shift percentages
    shift_stages = [10, 25, 50, 75, 100]

    for percentage in shift_stages:
        logger.info(f"Shifting {percentage}% traffic to {target_env.value}")

        # Update load balancer configuration
        await self._update_load_balancer_weights(target_env, percentage)

        # Monitor for issues
        await asyncio.sleep(30)  # Let traffic stabilize

        # Health check after traffic shift
        health = await self._check_environment_health(target_env)

        if health.status != HealthStatus.HEALTHY:
            logger.error(
                f"Health degraded at {percentage}% traffic",
                error_rate=health.error_rate,
                response_time=health.response_time
            )
            # Rollback to previous percentage
            await self._rollback_traffic()
            raise Exception(f"Health degraded during traffic shift at {percentage}%")

        logger.info(
            f"Traffic shift to {percentage}% successful",
            response_time=health.response_time,
            error_rate=health.error_rate
        )

async def _validate_environment_health(
    self,
    environment: DeploymentEnvironment,
    required_checks: int,
    timeout_minutes: int
) -> bool:
    """Validate environment health with multiple checks."""

    endpoint = (self.blue_endpoint if environment == DeploymentEnvironment.BLUE
               else self.green_endpoint)

    successful_checks = 0
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60

    while successful_checks < required_checks:
        if time.time() - start_time > timeout_seconds:
            logger.error(
                f"Health validation timeout for {environment.value}",
                successful_checks=successful_checks,
                required_checks=required_checks
            )
            return False

        try:
            health = await self._check_environment_health(environment)

            if health.status == HealthStatus.HEALTHY:
                successful_checks += 1
                logger.info(
                    f"Health check {successful_checks}/{required_checks} passed",
                    environment=environment.value,
                    response_time=health.response_time
                )
            else:
                # Reset counter on failure
                successful_checks = 0
                logger.warning(
                    f"Health check failed for {environment.value}",
                    status=health.status.value,
                    error_rate=health.error_rate
                )

        except Exception as e:
            successful_checks = 0
            logger.error(f"Health check error: {e}")

        await asyncio.sleep(10)  # Wait between checks

    return True

async def _check_environment_health(self, environment: DeploymentEnvironment) -> EnvironmentHealth:
    """Check health of specific environment."""
    endpoint = (self.blue_endpoint if environment == DeploymentEnvironment.BLUE
               else self.green_endpoint)

    start_time = time.time()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{endpoint}{self.health_check_path}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:

                response_time = time.time() - start_time

                if response.status == 200:
                    health_data = await response.json()

                    # Parse health details
                    status = HealthStatus.HEALTHY
                    if health_data.get("status") == "degraded":
                        status = HealthStatus.DEGRADED

                    return EnvironmentHealth(
                        environment=environment,
                        status=status,
                        response_time=response_time,
                        error_rate=0.0,  # Calculate from metrics
                        last_check=datetime.now(),
                        details=health_data
                    )
                else:
                    return EnvironmentHealth(
                        environment=environment,
                        status=HealthStatus.UNHEALTHY,
                        response_time=response_time,
                        error_rate=1.0,
                        last_check=datetime.now(),
                        details={"http_status": response.status}
                    )

    except Exception as e:
        return EnvironmentHealth(
            environment=environment,
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            error_rate=1.0,
            last_check=datetime.now(),
            details={"error": str(e)}
        )
```

## Production Load Testing Framework

### Capacity Validation and SLA Testing

Production systems need to be validated under realistic load conditions. Here's a comprehensive load testing framework:

```python
# testing/load_tester.py - Production Load Testing Framework
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class LoadTestResult:
    """Comprehensive load test results."""
    test_name: str
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    timeout_requests: int
    requests_per_second: float
    average_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    error_rate: float
    throughput_mbps: float
    response_times: List[float] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)

class ProductionLoadTester:
    """
    Production Load Testing: SLA Validation and Capacity Planning

    This framework provides:
    - Realistic traffic pattern simulation
    - Comprehensive performance metrics collection
    - SLA validation and alerting
    - Capacity planning analysis
    - Automated test reporting
    """

    def __init__(
        self,
        target_endpoint: str,
        max_concurrent_requests: int = 100,
        test_duration_minutes: int = 10
    ):
        self.target_endpoint = target_endpoint
        self.max_concurrent_requests = max_concurrent_requests
        self.test_duration_seconds = test_duration_minutes * 60
        self.results_history: List[LoadTestResult] = []

    async def run_load_test(
        self,
        test_name: str,
        request_generator: Callable,
        target_rps: int,
        sla_requirements: Dict[str, float]
    ) -> LoadTestResult:
        """Execute comprehensive load test with SLA validation."""

        logger.info(
            f"Starting load test: {test_name}",
            target_endpoint=self.target_endpoint,
            target_rps=target_rps,
            duration=f"{self.test_duration_seconds}s"
        )

        # Initialize metrics collection
        response_times = []
        errors = []
        successful_requests = 0
        failed_requests = 0
        timeout_requests = 0
        bytes_transferred = 0

        start_time = time.time()
        end_time = start_time + self.test_duration_seconds

        # Rate limiting setup
        request_interval = 1.0 / target_rps
        last_request_time = start_time

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        async def execute_request() -> Dict:
            """Execute single request with comprehensive error handling."""
            nonlocal successful_requests, failed_requests, timeout_requests, bytes_transferred

            async with semaphore:
                request_start = time.time()

                try:
                    # Generate request parameters
                    method, url, headers, data = await request_generator()

                    async with aiohttp.ClientSession() as session:
                        async with session.request(
                            method=method,
                            url=f"{self.target_endpoint}{url}",
                            headers=headers,
                            json=data,
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:

                            response_body = await response.read()
                            response_time = time.time() - request_start
                            response_times.append(response_time)
                            bytes_transferred += len(response_body)

                            if 200 <= response.status < 400:
                                successful_requests += 1
                            else:
                                failed_requests += 1
                                errors.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "status_code": response.status,
                                    "response_time": response_time,
                                    "error": f"HTTP {response.status}"
                                })

                            return {
                                "status": "success",
                                "response_time": response_time,
                                "status_code": response.status
                            }

                except asyncio.TimeoutError:
                    timeout_requests += 1
                    response_time = time.time() - request_start
                    response_times.append(response_time)

                    errors.append({
                        "timestamp": datetime.now().isoformat(),
                        "error": "Request timeout",
                        "response_time": response_time
                    })

                    return {"status": "timeout", "response_time": response_time}

                except Exception as e:
                    failed_requests += 1
                    response_time = time.time() - request_start
                    response_times.append(response_time)

                    errors.append({
                        "timestamp": datetime.now().isoformat(),
                        "error": str(e),
                        "response_time": response_time
                    })

                    return {"status": "error", "error": str(e), "response_time": response_time}

        # Execute load test
        tasks = []
        current_time = time.time()

        while current_time < end_time:
            # Rate limiting
            if current_time - last_request_time >= request_interval:
                task = asyncio.create_task(execute_request())
                tasks.append(task)
                last_request_time = current_time

            # Clean up completed tasks
            if len(tasks) >= self.max_concurrent_requests:
                done_tasks = [task for task in tasks if task.done()]
                for task in done_tasks:
                    tasks.remove(task)

                if not done_tasks:
                    await asyncio.sleep(0.01)  # Prevent busy waiting

            current_time = time.time()

        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate final metrics
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests + timeout_requests

        if response_times:
            response_times.sort()
            avg_response_time = statistics.mean(response_times)
            p50 = response_times[int(len(response_times) * 0.5)]
            p95 = response_times[int(len(response_times) * 0.95)]
            p99 = response_times[int(len(response_times) * 0.99)]
        else:
            avg_response_time = p50 = p95 = p99 = 0.0

        result = LoadTestResult(
            test_name=test_name,
            duration_seconds=total_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            timeout_requests=timeout_requests,
            requests_per_second=total_requests / total_time if total_time > 0 else 0,
            average_response_time=avg_response_time,
            p50_response_time=p50,
            p95_response_time=p95,
            p99_response_time=p99,
            error_rate=(failed_requests + timeout_requests) / max(total_requests, 1),
            throughput_mbps=(bytes_transferred / (1024 * 1024)) / max(total_time, 1),
            response_times=response_times[:1000],  # Keep sample for analysis
            errors=errors[:100]  # Keep sample errors
        )

        # SLA validation
        sla_violations = self._validate_sla(result, sla_requirements)

        logger.info(
            f"Load test completed: {test_name}",
            rps=f"{result.requests_per_second:.2f}",
            avg_response_time=f"{result.average_response_time:.3f}s",
            p95_response_time=f"{result.p95_response_time:.3f}s",
            error_rate=f"{result.error_rate * 100:.2f}%",
            sla_violations=len(sla_violations)
        )

        if sla_violations:
            logger.error(
                f"SLA violations detected in {test_name}",
                violations=sla_violations
            )

        self.results_history.append(result)
        return result

    def _validate_sla(self, result: LoadTestResult, requirements: Dict[str, float]) -> List[str]:
        """Validate test results against SLA requirements."""
        violations = []

        if "max_response_time_p95" in requirements:
            if result.p95_response_time > requirements["max_response_time_p95"]:
                violations.append(
                    f"P95 response time {result.p95_response_time:.3f}s exceeds "
                    f"SLA requirement {requirements['max_response_time_p95']:.3f}s"
                )

        if "max_error_rate" in requirements:
            if result.error_rate > requirements["max_error_rate"]:
                violations.append(
                    f"Error rate {result.error_rate * 100:.2f}% exceeds "
                    f"SLA requirement {requirements['max_error_rate'] * 100:.2f}%"
                )

        if "min_throughput_rps" in requirements:
            if result.requests_per_second < requirements["min_throughput_rps"]:
                violations.append(
                    f"Throughput {result.requests_per_second:.2f} RPS below "
                    f"SLA requirement {requirements['min_throughput_rps']:.2f} RPS"
                )

        return violations

# Example usage for MCP server load testing
async def mcp_request_generator():
    """Generate realistic MCP server requests for load testing."""

    # Mix of different request types
    request_types = [
        ("POST", "/mcp", {"Content-Type": "application/json"}, {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }),
        ("POST", "/mcp", {"Content-Type": "application/json"}, {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "process_data",
                "arguments": {"data": {"test": "data"}, "operation": "transform"}
            },
            "id": 2
        }),
        ("GET", "/health", {}, None),
        ("GET", "/metrics", {}, None)
    ]

    return random.choice(request_types)
```

This comprehensive enterprise resilience framework provides production-ready patterns for building bulletproof MCP servers that can withstand real-world failures and scale to meet enterprise demands. The combination of circuit breakers, chaos engineering, blue-green deployments, and comprehensive load testing ensures your production systems are truly resilient.

---

## 🧭 Navigation

**Previous:** [Session 3 - Advanced Patterns →](Session3_LangChain_MCP_Integration.md)  
**Next:** [Session 5 - Type-Safe Development →](Session5_Security_Monitoring.md)

---
