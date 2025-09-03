# 📝 Session 5 Participant Path: Practical Implementation

> **📝 PARTICIPANT PATH CONTENT**
> Prerequisites: Complete 🎯 Observer Path in [Session5_PydanticAI_Type_Safe_Agents.md](Session5_PydanticAI_Type_Safe_Agents.md)
> Time Investment: 2-3 hours
> Outcome: Build production-ready type-safe agents with advanced tools

## Learning Outcomes

After completing this practical implementation guide, you will:

- Build complex agents with dependency injection patterns  
- Create sophisticated tool chains for data processing workflows  
- Implement comprehensive error recovery systems  
- Deploy type-safe agents with monitoring and observability  

## Advanced Agent Architecture Patterns

### Dependency Injection for Production Systems

Real data processing applications require clean separation of concerns and testable architecture. Here's how to implement advanced dependency injection patterns:

First, create comprehensive service dependencies:

```python
from typing import Protocol
import asyncio
import httpx

class DataServiceProtocol(Protocol):
    async def save_job(self, job_data: dict) -> str: ...
    async def get_pipeline_status(self, pipeline_id: str) -> dict: ...
    async def execute_query(self, query: str) -> dict: ...

class ProductionDataService:
    def __init__(self, warehouse_url: str, api_key: str):
        self.warehouse_url = warehouse_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={"Authorization": f"Bearer {api_key}"}
        )

    async def save_job(self, job_data: dict) -> str:
        # Real implementation would save to data warehouse
        response = await self.client.post(
            f"{self.warehouse_url}/jobs",
            json=job_data
        )
        return response.json()["job_id"]

    async def get_pipeline_status(self, pipeline_id: str) -> dict:
        response = await self.client.get(
            f"{self.warehouse_url}/pipelines/{pipeline_id}/status"
        )
        return response.json()
```

Create agents with sophisticated dependency management:

```python
from pydantic_ai import Agent, RunContext

class EnhancedFeatureExtractionResponse(BaseModel):
    extraction_id: str
    status: str = Field(..., regex=r'^(queued|processing|completed|failed)$')
    estimated_completion: str
    feature_pipeline_steps: List[str]
    job_url: str
    pipeline_id: Optional[str] = None
    metrics: Optional[dict] = None

production_feature_agent = Agent(
    'openai:gpt-4',
    result_type=EnhancedFeatureExtractionResponse,
    deps_type=ProductionDataService
)

@production_feature_agent.system_prompt
def enhanced_system_prompt(ctx: RunContext[ProductionDataService]) -> str:
    return f"""
    You are a production data processing assistant with access to:
    - Data warehouse at {ctx.deps.warehouse_url}
    - Pipeline monitoring capabilities
    - Job scheduling and tracking

    Always include realistic pipeline steps, job URLs, and status information.
    Estimate completion times based on data processing complexity.
    """
```

### Advanced Tool Integration Patterns

Complex data processing requires sophisticated tool orchestration. Here's how to build advanced tool systems:

Create comprehensive tool schemas:

```python
class AdvancedQueryInput(BaseModel):
    sql_query: str = Field(..., min_length=10)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    format: str = Field(default="json", regex=r'^(json|csv|parquet)$')
    cache_duration: int = Field(default=300, ge=0, le=3600)
    priority: str = Field(default="normal", regex=r'^(low|normal|high|critical)$')

class AdvancedQueryOutput(BaseModel):
    query_id: str
    row_count: int
    columns: List[str]
    execution_time: float
    result_preview: str
    cache_hit: bool
    cost_estimate: float
    performance_metrics: dict = Field(default_factory=dict)
```

Implement advanced tool logic with error handling:

```python
def create_advanced_query_tool() -> Tool:
    async def execute_advanced_query(input_data: AdvancedQueryInput) -> AdvancedQueryOutput:
        try:
            import time
            import random
            import hashlib

            start_time = time.time()

            # Simulate caching logic
            query_hash = hashlib.md5(input_data.sql_query.encode()).hexdigest()[:8]
            cache_hit = random.choice([True, False])

            # Simulate different execution times based on cache
            if cache_hit:
                await asyncio.sleep(0.01)  # Cache hit - fast response
            else:
                # Simulate query complexity-based execution time
                complexity_factor = len(input_data.sql_query) / 1000.0
                await asyncio.sleep(min(complexity_factor, 2.0))

            execution_time = time.time() - start_time

            # Generate realistic performance metrics
            performance_metrics = {
                "cpu_usage_percent": random.uniform(20, 80),
                "memory_usage_mb": random.randint(100, 1000),
                "disk_io_mb": random.randint(10, 500),
                "network_io_mb": random.randint(5, 100)
            }

            return AdvancedQueryOutput(
                query_id=f"query_{query_hash}",
                row_count=random.randint(1000, 10000000),
                columns=["user_id", "event_type", "timestamp", "feature_value"],
                execution_time=execution_time,
                result_preview="user_id,event_type,timestamp,feature_value\n123,click,2024-01-01,0.85\n456,view,2024-01-01,0.72",
                cache_hit=cache_hit,
                cost_estimate=random.uniform(0.01, 10.0),
                performance_metrics=performance_metrics
            )

        except Exception as e:
            raise ValueError(f"Advanced query execution failed: {e}")

    return Tool(execute_advanced_query, takes=AdvancedQueryInput, returns=AdvancedQueryOutput)
```

## Production-Ready Error Handling Systems

### Comprehensive Error Classification

Production systems need sophisticated error handling that provides actionable diagnostics:

```python
from enum import Enum
from typing import Union, Any
import logging
import traceback

class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK = "network"
    DATA_CORRUPTION = "data_corruption"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    UNKNOWN = "unknown"

class DetailedErrorResponse(BaseModel):
    success: bool = False
    error_category: ErrorCategory
    error_severity: ErrorSeverity
    error_message: str
    error_code: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    request_id: str
    retry_after_seconds: Optional[int] = None
    fallback_available: bool = False
    support_reference: Optional[str] = None
```

Implement comprehensive error handling:

```python
import uuid
from datetime import datetime

async def execute_with_comprehensive_error_handling(
    agent: Agent,
    query: str,
    deps: Any = None,
    request_id: str = None
) -> Union[Any, DetailedErrorResponse]:
    """Execute agent with comprehensive error handling and classification"""

    if request_id is None:
        request_id = str(uuid.uuid4())

    try:
        if deps:
            result = await agent.run(query, deps=deps)
        else:
            result = await agent.run(query)

        return {"success": True, "data": result, "request_id": request_id}

    except ValidationError as e:
        return DetailedErrorResponse(
            error_category=ErrorCategory.VALIDATION,
            error_severity=ErrorSeverity.MEDIUM,
            error_message=f"Data validation failed: {str(e)}",
            error_code="VALIDATION_001",
            request_id=request_id,
            retry_after_seconds=None,
            fallback_available=True,
            support_reference=f"REF_{request_id[:8]}"
        )

    except httpx.TimeoutException as e:
        return DetailedErrorResponse(
            error_category=ErrorCategory.TIMEOUT,
            error_severity=ErrorSeverity.HIGH,
            error_message="Request timed out - external service not responding",
            error_code="TIMEOUT_001",
            request_id=request_id,
            retry_after_seconds=30,
            fallback_available=True,
            support_reference=f"REF_{request_id[:8]}"
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return DetailedErrorResponse(
                error_category=ErrorCategory.RATE_LIMIT,
                error_severity=ErrorSeverity.MEDIUM,
                error_message="Rate limit exceeded - too many requests",
                error_code="RATE_LIMIT_001",
                request_id=request_id,
                retry_after_seconds=60,
                fallback_available=False,
                support_reference=f"REF_{request_id[:8]}"
            )
        else:
            return DetailedErrorResponse(
                error_category=ErrorCategory.NETWORK,
                error_severity=ErrorSeverity.HIGH,
                error_message=f"HTTP error {e.response.status_code}: {e.response.text}",
                error_code=f"HTTP_{e.response.status_code}",
                request_id=request_id,
                retry_after_seconds=10,
                fallback_available=True,
                support_reference=f"REF_{request_id[:8]}"
            )

    except Exception as e:
        # Log unexpected errors for debugging
        logging.error(f"Unexpected error in request {request_id}: {traceback.format_exc()}")

        return DetailedErrorResponse(
            error_category=ErrorCategory.UNKNOWN,
            error_severity=ErrorSeverity.CRITICAL,
            error_message=f"Unexpected system error: {type(e).__name__}",
            error_code="UNKNOWN_001",
            request_id=request_id,
            retry_after_seconds=120,
            fallback_available=False,
            support_reference=f"REF_{request_id[:8]}"
        )
```

### Advanced Retry and Circuit Breaker Patterns

Implement sophisticated resilience patterns:

```python
import asyncio
from typing import Callable, TypeVar, Generic
from datetime import datetime, timedelta

T = TypeVar('T')

class CircuitBreakerState(str, Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing - blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker(Generic[T]):
    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    async def __call__(self, func: Callable[[], T]) -> T:
        """Execute function with circuit breaker protection"""

        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker OPEN - service unavailable")

        try:
            result = await func()
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

class AdvancedRetryHandler:
    def __init__(self,
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.circuit_breaker = CircuitBreaker()

    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with advanced retry logic and circuit breaker"""

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                # Use circuit breaker to protect against cascading failures
                return await self.circuit_breaker(lambda: func(*args, **kwargs))

            except Exception as e:
                last_exception = e

                if attempt == self.max_retries:
                    break

                # Calculate exponential backoff delay
                delay = min(
                    self.base_delay * (self.exponential_base ** attempt),
                    self.max_delay
                )

                # Add jitter to prevent thundering herd
                if self.jitter:
                    delay *= random.uniform(0.5, 1.5)

                logging.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s"
                )

                await asyncio.sleep(delay)

        raise last_exception
```

## Real-World Implementation Example

### Building a Complete Data Processing Agent

Here's a comprehensive example that combines all concepts:

```python
class ProductionDataProcessingAgent:
    def __init__(self, config: dict):
        self.config = config
        self.data_service = ProductionDataService(
            warehouse_url=config["warehouse_url"],
            api_key=config["api_key"]
        )
        self.retry_handler = AdvancedRetryHandler(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0
        )

        # Create tools
        self.query_tool = create_advanced_query_tool()

        # Create main agent
        self.agent = Agent(
            config["model_name"],
            result_type=EnhancedFeatureExtractionResponse,
            deps_type=ProductionDataService,
            tools=[self.query_tool]
        )

    async def process_feature_request(self, request: FeatureExtractionRequest) -> dict:
        """Main entry point for feature processing requests"""

        request_id = str(uuid.uuid4())

        try:
            # Use retry handler for resilience
            result = await self.retry_handler.execute_with_retry(
                self._execute_feature_extraction,
                request,
                request_id
            )

            return {
                "success": True,
                "data": result,
                "request_id": request_id,
                "processing_time": result.get("processing_time", 0)
            }

        except Exception as e:
            # Comprehensive error handling
            error_response = await execute_with_comprehensive_error_handling(
                self.agent,
                self._build_query(request),
                self.data_service,
                request_id
            )

            return error_response

    async def _execute_feature_extraction(self, request: FeatureExtractionRequest, request_id: str):
        """Internal feature extraction logic"""

        query = self._build_query(request)

        result = await self.agent.run(
            query,
            deps=self.data_service
        )

        # Save job to data warehouse
        job_data = {
            "request_id": request_id,
            "dataset_id": request.dataset_id,
            "feature_description": request.feature_description,
            "quality_threshold": request.quality_threshold.value,
            "extraction_id": result.extraction_id,
            "created_at": datetime.utcnow().isoformat()
        }

        await self.data_service.save_job(job_data)

        return result

    def _build_query(self, request: FeatureExtractionRequest) -> str:
        return f"""
        Plan a comprehensive feature extraction pipeline for:
        - Dataset: {request.dataset_id}
        - Description: {request.feature_description}
        - Quality Threshold: {request.quality_threshold.value}
        - Completion Date: {request.completion_date or 'Not specified'}

        Include realistic pipeline steps, job scheduling, and monitoring setup.
        Provide accurate time estimates based on data complexity.
        """
```

### Production Usage Example

```python
# Configuration for production deployment
production_config = {
    "model_name": "openai:gpt-4",
    "warehouse_url": "https://warehouse.company.com/api/v1",
    "api_key": os.getenv("DATA_WAREHOUSE_API_KEY"),
    "max_retries": 3,
    "timeout_seconds": 30
}

# Initialize production agent
processing_agent = ProductionDataProcessingAgent(production_config)

# Process feature extraction request
request = FeatureExtractionRequest(
    dataset_id="customer_behavior_2024_q4",
    feature_description="Extract click-through and conversion features for recommendation engine",
    quality_threshold=DataQuality.HIGH,
    completion_date="2025-02-01"
)

result = await processing_agent.process_feature_request(request)

if result["success"]:
    extraction_data = result["data"]
    print(f"✅ Feature extraction planned: {extraction_data.extraction_id}")
    print(f"📊 Pipeline steps: {len(extraction_data.feature_pipeline_steps)}")
    print(f"⏱️ Estimated completion: {extraction_data.estimated_completion}")
else:
    error = result
    print(f"❌ Error: {error.error_category} - {error.error_message}")
    print(f"🔄 Retry after: {error.retry_after_seconds}s")
    print(f"📞 Support reference: {error.support_reference}")
```

## 📝 Participant Path Practice Exercise

Build your own production-ready data processing agent:

1. **Create Enhanced Models**: Define comprehensive request/response models with validation  
2. **Implement Service Layer**: Build dependency injection with real service integration  
3. **Add Error Handling**: Implement comprehensive error classification and recovery  
4. **Create Tool Chain**: Build multiple interconnected tools with validation  
5. **Test Resilience**: Verify retry logic, circuit breaker, and error scenarios  

### Validation Checklist

- [ ] Agent handles complex dependencies correctly  
- [ ] Error handling provides actionable diagnostics  
- [ ] Tools integrate seamlessly with validation  
- [ ] Retry logic works with exponential backoff  
- [ ] Circuit breaker prevents cascading failures  
- [ ] All code follows production quality standards  

---

## Next Steps: Production Deployment

Ready to deploy your type-safe agents? Continue with:
📝 [Production Deployment Guide](Session5_Production_Deployment.md)
---

**Next:** [Session 6 - Atomic Agents Modular Architecture →](Session6_Atomic_Agents_Modular_Architecture.md)

---
