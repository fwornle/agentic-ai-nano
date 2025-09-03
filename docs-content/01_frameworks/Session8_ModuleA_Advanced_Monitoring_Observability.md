# ⚙️ Session 8 Module A: Advanced Monitoring & Observability

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths in [Session 8](Session8_Agno_Production_Ready_Agents.md)
> Time Investment: 3-4 hours
> Outcome: Master enterprise-scale monitoring, health checks, and observability systems for data pipelines

## Advanced Learning Outcomes

After completing this module, you will master:

- Enterprise-scale monitoring systems for production data pipelines  
- Advanced health checking with comprehensive dependency validation  
- Scaling patterns with Docker Compose and load balancing  
- Production observability with distributed tracing and alerting  

## Basic Scaling - When Data Success Becomes Your Biggest Challenge

The irony of successful data applications: the better they work, the more data they attract, and the more likely they are to collapse under their own data processing success. Twitter's data pipeline struggles during viral events. Instagram's analytics during global campaigns. Even Google has faced scaling challenges with their data processing systems.

Scaling data systems isn't just about handling more data - it's about handling data volume growth gracefully while maintaining data quality:

Here's the basic Docker Compose configuration structure:

```yaml
# docker-compose.yml for basic data processing scaling
version: '3.8'

services:
  agno-data-api:
    build: .
    ports:
      - "8000-8002:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/agno_data
```

Configure service dependencies and worker settings:

```yaml
      - REDIS_URL=redis://redis:6379
      - DATA_PROCESSING_WORKERS=4
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 3
```

Set up PostgreSQL database service for persistent storage:

```yaml
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=agno_data
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

Add Redis caching service for performance optimization:

```yaml
  redis:
    image: redis:alpine

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - agno-data-api

volumes:
  postgres_data:
```

This configuration provides basic horizontal scaling for your Agno data processing agents with load balancing, caching, and persistent storage.

## Health Monitoring - Your Data Pipeline's Vital Signs

A mission-critical data pipeline requires monitors tracking every data ingestion rate, every processing latency, every quality metric. The moment data freshness degrades or throughput drops, alerts fire and data engineers rush to prevent downstream impact.

Your production data systems deserve this level of observability. Health monitoring isn't paranoia for data pipelines - it's professional responsibility to data consumers:

```python
from agno.monitoring import HealthChecker
import asyncio

class DataProductionHealthChecker:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.health_checker = HealthChecker(agent)
```

Define comprehensive health verification that tests all data processing system components:

```python
    async def comprehensive_data_health_check(self):
        """Comprehensive data processing system health verification."""
        checks = {
            "agent_responsive": False,
            "database_connected": False,
            "cache_available": False,
            "data_processing_capacity": "unknown"
        }
```

Test agent responsiveness and database connectivity:

```python
        try:
            # Test agent responsiveness with data processing query
            response = await self.agent.arun("health check for data processing", timeout=5)
            checks["agent_responsive"] = bool(response.content)

            # Test database connection for metadata storage
            if hasattr(self.agent.storage, 'test_connection'):
                checks["database_connected"] = await self.agent.storage.test_connection()
```

Verify cache availability and system resources for data processing:

```python
            # Test cache availability for data pattern caching
            if hasattr(self.agent, 'cache'):
                checks["cache_available"] = await self.agent.cache.ping()

            # Check memory usage for data processing capacity
            import psutil
            memory = psutil.virtual_memory()
            checks["data_processing_capacity"] = f"{memory.percent}% memory used"

        except Exception as e:
            checks["error"] = str(e)

        return checks
```

FastAPI integration for detailed health endpoints for data systems:

```python
# Usage in FastAPI for data processing systems
@app.get("/health/data-detailed")
async def detailed_data_health():
    health_checker = DataProductionHealthChecker(data_production_agent)
    return await health_checker.comprehensive_data_health_check()
```

## Advanced Observability Patterns

### Distributed Tracing for Data Processing

When dealing with complex data processing pipelines, understanding the flow of data through different components becomes crucial. Distributed tracing helps track data processing requests across multiple services:

```python
from agno.tracing import DistributedTracer
import opentracing

class TracedDataAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.tracer = DistributedTracer(service_name="agno-data-pipeline")
```

Implement tracing for data processing operations:

```python
    async def traced_data_process(self, query: str, trace_id: str = None):
        """Process data with distributed tracing."""
        with self.tracer.start_span("data_processing_request") as span:
            span.set_tag("query_length", len(query))
            span.set_tag("trace_id", trace_id)

            try:
                # Process with the agent
                response = await self.agent.arun(query)
                span.set_tag("response_length", len(response.content))
                span.set_tag("status", "success")

                return response.content
```

Handle errors and span completion:

```python
            except Exception as e:
                span.set_tag("error", True)
                span.set_tag("error_message", str(e))
                span.log_kv({"event": "error", "message": str(e)})
                raise
            finally:
                span.finish()
```

### Metrics Collection and Alerting

Enterprise data processing systems need comprehensive metrics collection with alerting capabilities:

```python
from prometheus_client import Counter, Histogram, Gauge
import time

class DataProcessingMetrics:
    def __init__(self):
        # Counters for tracking processing events
        self.requests_total = Counter(
            'agno_data_requests_total',
            'Total data processing requests',
            ['status', 'query_type']
        )
```

Define latency and capacity metrics:

```python
        # Histograms for latency tracking
        self.processing_duration = Histogram(
            'agno_data_processing_seconds',
            'Data processing request duration',
            ['query_type']
        )

        # Gauges for current system state
        self.active_sessions = Gauge(
            'agno_active_sessions',
            'Number of active data processing sessions'
        )
```

Implement metric recording during data processing:

```python
    def record_processing_request(self, query_type: str, status: str, duration: float):
        """Record metrics for data processing request."""
        self.requests_total.labels(status=status, query_type=query_type).inc()
        self.processing_duration.labels(query_type=query_type).observe(duration)
```

Usage example with automatic metrics collection:

```python
# Integration with data processing agent
class MetricsCollectingAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.metrics = DataProcessingMetrics()

    async def process_with_metrics(self, query: str, query_type: str = "general"):
        start_time = time.time()
        try:
            response = await self.agent.arun(query)
            duration = time.time() - start_time
            self.metrics.record_processing_request(query_type, "success", duration)
            return response.content
        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_processing_request(query_type, "error", duration)
            raise
```

### Log Aggregation and Analysis

Production data processing systems generate massive amounts of log data. Proper log aggregation and analysis are essential for troubleshooting and optimization:

```python
import structlog
from pythonjsonlogger import jsonlogger

class DataProcessingLogger:
    def __init__(self):
        # Configure structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        self.logger = structlog.get_logger("agno.data.processing")
```

Log data processing events with structured data:

```python
    def log_processing_event(self, event_type: str, **kwargs):
        """Log structured data processing events."""
        self.logger.info(
            event_type,
            timestamp=time.time(),
            **kwargs
        )

    def log_data_quality_check(self, quality_score: float, data_size: int, issues: list):
        """Log data quality assessment results."""
        self.logger.info(
            "data_quality_check",
            quality_score=quality_score,
            data_size=data_size,
            issues_count=len(issues),
            issues=issues
        )
```

Integration with data processing workflows:

```python
# Usage in data processing agent
class LoggingDataAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.logger = DataProcessingLogger()

    async def process_with_logging(self, query: str, session_id: str):
        self.logger.log_processing_event(
            "processing_started",
            query_length=len(query),
            session_id=session_id
        )

        try:
            response = await self.agent.arun(query, session_id=session_id)

            self.logger.log_processing_event(
                "processing_completed",
                response_length=len(response.content),
                session_id=session_id
            )

            return response.content
        except Exception as e:
            self.logger.log_processing_event(
                "processing_failed",
                error=str(e),
                session_id=session_id
            )
            raise
```

## Production Deployment Monitoring

### Container Health and Resource Monitoring

When deploying Agno agents in containerized environments, monitoring container health and resource usage becomes critical:

```python
import docker
import psutil

class ContainerMonitor:
    def __init__(self):
        self.docker_client = docker.from_env()

    async def get_container_stats(self, container_name: str):
        """Get comprehensive container statistics."""
        try:
            container = self.docker_client.containers.get(container_name)
            stats = container.stats(stream=False)

            # Calculate CPU usage percentage
            cpu_stats = stats['cpu_stats']
            precpu_stats = stats['precpu_stats']

            cpu_usage = self._calculate_cpu_percent(cpu_stats, precpu_stats)
```

Calculate memory usage and network statistics:

```python
            # Memory usage
            memory_stats = stats['memory_stats']
            memory_usage = memory_stats.get('usage', 0)
            memory_limit = memory_stats.get('limit', 0)
            memory_percent = (memory_usage / memory_limit) * 100 if memory_limit else 0

            # Network I/O
            networks = stats.get('networks', {})
            rx_bytes = sum(net.get('rx_bytes', 0) for net in networks.values())
            tx_bytes = sum(net.get('tx_bytes', 0) for net in networks.values())

            return {
                "cpu_percent": cpu_usage,
                "memory_percent": memory_percent,
                "memory_usage_mb": memory_usage / (1024 * 1024),
                "network_rx_mb": rx_bytes / (1024 * 1024),
                "network_tx_mb": tx_bytes / (1024 * 1024),
                "status": container.status
            }
        except Exception as e:
            return {"error": str(e)}
```

Helper method for CPU calculation:

```python
    def _calculate_cpu_percent(self, cpu_stats, precpu_stats):
        """Calculate CPU usage percentage."""
        cpu_delta = cpu_stats['cpu_usage']['total_usage'] - precpu_stats['cpu_usage']['total_usage']
        system_delta = cpu_stats['system_cpu_usage'] - precpu_stats['system_cpu_usage']

        if system_delta > 0 and cpu_delta > 0:
            return (cpu_delta / system_delta) * len(cpu_stats['cpu_usage']['percpu_usage']) * 100
        return 0.0
```

### Application Performance Monitoring (APM)

Integrate with APM solutions for comprehensive application monitoring:

```python
from agno.apm import APMIntegration
import newrelic.agent

class APMDataAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.apm = APMIntegration(service_name="agno-data-processing")
```

Instrument data processing methods for APM tracking:

```python
    @newrelic.agent.background_task(name='data_processing', group='DataProcessing')
    async def monitored_data_process(self, query: str):
        """Data processing with APM monitoring."""
        # Custom metrics for New Relic
        newrelic.agent.add_custom_attribute('query_length', len(query))

        try:
            response = await self.agent.arun(query)

            # Record success metrics
            newrelic.agent.add_custom_attribute('response_length', len(response.content))
            newrelic.agent.add_custom_attribute('processing_status', 'success')

            return response.content
        except Exception as e:
            # Record error metrics
            newrelic.agent.add_custom_attribute('processing_status', 'error')
            newrelic.agent.add_custom_attribute('error_type', type(e).__name__)
            newrelic.agent.record_exception()
            raise
```

Custom business metrics for data processing:

```python
    def record_business_metrics(self, data_volume: int, processing_time: float, quality_score: float):
        """Record business-specific metrics."""
        newrelic.agent.record_custom_metric('Custom/DataVolume', data_volume)
        newrelic.agent.record_custom_metric('Custom/ProcessingTime', processing_time)
        newrelic.agent.record_custom_metric('Custom/QualityScore', quality_score)
```

## Advanced Health Check Patterns

### Dependency Health Verification

Production systems depend on multiple external services. Comprehensive health checks must verify all dependencies:

```python
import aiohttp
import asyncpg

class DependencyHealthChecker:
    def __init__(self):
        self.dependencies = {
            'database': self._check_database,
            'redis': self._check_redis,
            'external_api': self._check_external_api,
            'file_system': self._check_file_system
        }
```

Implement individual dependency checks:

```python
    async def _check_database(self):
        """Check PostgreSQL database connectivity."""
        try:
            conn = await asyncpg.connect(
                host="localhost", port=5432,
                user="user", password="pass", database="agno_data",
                timeout=5.0
            )
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            return {"status": "healthy", "latency_ms": "< 5000"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
```

Check Redis and external API health:

```python
    async def _check_redis(self):
        """Check Redis cache connectivity."""
        try:
            import aioredis
            redis = aioredis.from_url("redis://localhost:6379")
            await redis.ping()
            await redis.close()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def _check_external_api(self):
        """Check external API availability."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.external-service.com/health", timeout=10) as response:
                    if response.status == 200:
                        return {"status": "healthy", "response_code": response.status}
                    else:
                        return {"status": "degraded", "response_code": response.status}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
```

File system and comprehensive health check:

```python
    async def _check_file_system(self):
        """Check file system availability and space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100

            if free_percent < 10:
                return {"status": "warning", "free_percent": free_percent}
            else:
                return {"status": "healthy", "free_percent": free_percent}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_all_dependencies(self):
        """Check all dependencies and return comprehensive status."""
        results = {}
        for name, check_func in self.dependencies.items():
            results[name] = await check_func()

        # Determine overall health
        unhealthy = [name for name, status in results.items() if status.get("status") == "unhealthy"]
        warning = [name for name, status in results.items() if status.get("status") == "warning"]

        overall_status = "healthy"
        if unhealthy:
            overall_status = "unhealthy"
        elif warning:
            overall_status = "degraded"

        return {
            "overall_status": overall_status,
            "dependencies": results,
            "unhealthy_count": len(unhealthy),
            "warning_count": len(warning)
        }
```

---

**Next:** [Session 9 - Multi-Agent Patterns →](Session9_Multi_Agent_Patterns.md)

---
