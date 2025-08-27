# Session 8 - Module A: Advanced Monitoring & Observability

**Prerequisites**: [Session 8 Core Section Complete](Session8_Agno_Production_Ready_Agents.md)

## Module Overview

Comprehensive monitoring and observability for production Agno agent systems including distributed tracing, metrics collection, alerting strategies, performance profiling, and automated incident response.

---

## Part 1: Production Deployment & Monitoring Foundation

### Step 1: Understanding Production Configuration

Build the foundation for production-ready Agno agent deployments with comprehensive configuration for resource allocation and monitoring setup.

🗂️ **File**: `src/session8/production_deployment.py` - Complete production deployment patterns

Production deployment differs from development with these considerations:

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
import json
from pathlib import Path
```

### Step 2: Creating Production Configuration Schema

Build a robust configuration class for production systems:

```python
@dataclass
class ProductionConfig:
    """Complete production deployment configuration"""
    service_name: str
    version: str
    environment: str = "production"
    replicas: int = 3
    max_replicas: int = 10
```

Service identification and scaling parameters: `replicas` ensures high availability, `max_replicas` prevents runaway scaling.

### Step 3: Resource Management Configuration

Add resource constraints for cost control and performance predictability:

```python
    # Resource limits - Critical for cost control
    memory_limit: str = "2Gi"
    cpu_limit: str = "1000m"
    memory_request: str = "1Gi"
    cpu_request: str = "500m"
```

`requests` guarantee minimum resources, `limits` prevent resource overconsumption. The 2:1 ratio provides headroom for spikes.

### Step 4: Health Check Configuration

Configure comprehensive health monitoring - the lifeline of production systems:

```python
    # Health check configuration - Your monitoring lifeline
    health_check_path: str = "/health"
    ready_check_path: str = "/ready"
    health_check_interval: int = 30
    health_check_timeout: int = 5
```

Separate `health` (service alive) from `ready` (can handle traffic) to prevent routing traffic to struggling instances.

### Step 5: Observability Configuration

Enable comprehensive observability:

```python
    # Monitoring configuration - Eyes into your system
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    logging_level: str = "INFO"
```

### Step 6: Building the Production Deployment Manager

Create the main deployment orchestrator to handle all aspects of production deployment:

```python
class AgnoProductionDeployment:
    """Production deployment manager for Agno agent systems"""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.deployment_manifests = {}
        self.monitoring_stack = {}
        self.logger = logging.getLogger(__name__)
```

Keep manifests and monitoring configurations as instance variables for reuse and modification.

### Step 7: Creating Production-Ready Docker Images

Start with containerization - production Docker images need security, observability, and efficiency:

```python
    def generate_docker_configuration(self) -> str:
        """Generate production-ready Dockerfile for Agno agents"""
        
        dockerfile_content = f"""
FROM python:3.11-slim

# Set working directory
WORKDIR /app
"""
```

Use `python:3.11-slim` for smaller attack surface and faster startup times.

### Step 8: System Dependencies for Monitoring

Install essential system packages for monitoring and debugging:

```python
# Install system dependencies for monitoring
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    procps \\
    && rm -rf /var/lib/apt/lists/*
```

- `curl`: Health checks and debugging
- `procps`: Process monitoring tools
- Clean up package lists to reduce image size

### Step 9: Efficient Python Dependency Installation

Optimize Python package installation for better Docker layer caching:

```python
# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install monitoring dependencies
RUN pip install prometheus-client opentelemetry-api opentelemetry-sdk
```

Copy `requirements.txt` first so Docker can reuse this layer when only application code changes.

### Step 10: Application Code and Security Setup

Copy application and set up security:

```python
# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY monitoring/ ./monitoring/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash agno
RUN chown -R agno:agno /app
USER agno
```

Never run containers as root - create a dedicated user with minimal privileges.

### Step 11: Network Configuration and Health Checks

Configure networking and implement comprehensive health checking:

```python
# Expose application and metrics ports
EXPOSE 8000 9090

# Health check with detailed monitoring
HEALTHCHECK --interval={self.config.health_check_interval}s \\
    --timeout={self.config.health_check_timeout}s \\
    --start-period=10s \\
    --retries=3 \\
    CMD curl -f http://localhost:8000{self.config.health_check_path} || exit 1

# Start application with monitoring
CMD ["python", "-m", "src.main", "--enable-monitoring"]
"""
        return dockerfile_content.strip()
```

Use Docker's built-in health check with configurable intervals and timeouts for production-ready deployment.

### Step 12: Kubernetes Deployment Foundation

Create Kubernetes manifests for production deployment:

```python
    def create_kubernetes_manifests(self) -> Dict[str, Dict]:
        """Generate complete Kubernetes deployment with monitoring"""
        
        manifests = {
            "deployment": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": self.config.service_name,
                    "labels": {
                        "app": self.config.service_name,
                        "version": self.config.version
                    }
                },
```

Organize as dictionary for easy YAML serialization and programmatic manipulation.

### Step 13: Deployment Specification

Define replica count and pod selection:

```python
                "spec": {
                    "replicas": self.config.replicas,
                    "selector": {
                        "matchLabels": {"app": self.config.service_name}
                    },
```

The `matchLabels` ensures Kubernetes only manages pods with the specific app label.

### Step 14: Pod Template with Monitoring Annotations

Define pod template with built-in Prometheus monitoring:

```python
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": self.config.service_name,
                                "version": self.config.version
                            },
                            "annotations": {
                                "prometheus.io/scrape": "true",
                                "prometheus.io/port": "9090",
                                "prometheus.io/path": "/metrics"
                            }
                        },
```

These annotations tell Prometheus how to scrape metrics from pods automatically.

### Step 15: Container Configuration with Resource Limits

Now let's configure the actual container with proper resource management:

```python
                        "spec": {
                            "containers": [{
                                "name": "agno-agent",
                                "image": f"your-registry/{self.config.service_name}:{self.config.version}",
                                "ports": [
                                    {"containerPort": 8000, "name": "http"},
                                    {"containerPort": 9090, "name": "metrics"}
                                ],
                                "resources": {
                                    "limits": {
                                        "memory": self.config.memory_limit,
                                        "cpu": self.config.cpu_limit
                                    },
                                    "requests": {
                                        "memory": self.config.memory_request,
                                        "cpu": self.config.cpu_request
                                    }
                                },
```

**Resource philosophy**: Requests guarantee resources, limits prevent resource hogging. This ensures predictable performance.

### Step 16: Health Check Implementation

Let's implement comprehensive health checking for high availability:

```python
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": self.config.health_check_path,
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": self.config.health_check_interval
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": self.config.ready_check_path,
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 10
                                },
```

### Health check strategy

- **Liveness**: "Is the app alive?" - restarts if failing
- **Readiness**: "Can it handle traffic?" - removes from load balancer if failing

### Step 17: Environment Configuration

Finally, let's inject all necessary environment variables:

```python
                                "env": [
                                    {"name": "SERVICE_NAME", "value": self.config.service_name},
                                    {"name": "ENVIRONMENT", "value": self.config.environment},
                                    {"name": "METRICS_ENABLED", "value": str(self.config.metrics_enabled)},
                                    {"name": "TRACING_ENABLED", "value": str(self.config.tracing_enabled)},
                                    {"name": "LOG_LEVEL", "value": self.config.logging_level}
                                ]
                            }]
                        }
                    }
                }
            },
```

**Configuration approach**: We pass configuration through environment variables for 12-factor app compliance.

### Step 18: Horizontal Pod Autoscaler (HPA) Configuration

Now let's add intelligent auto-scaling based on multiple metrics. This is crucial for handling varying loads efficiently:

```python
            "hpa": {
                "apiVersion": "autoscaling/v2",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {"name": f"{self.config.service_name}-hpa"},
                "spec": {
                    "scaleTargetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": self.config.service_name
                    },
                    "minReplicas": self.config.replicas,
                    "maxReplicas": self.config.max_replicas,
```

**Scaling boundaries**: We set clear minimum and maximum replica counts to ensure both availability and cost control.

### Step 19: Multi-Metric Scaling Strategy

Let's implement scaling based on multiple metrics for more intelligent decisions:

```python
                    "metrics": [
                        {
                            "type": "Resource",
                            "resource": {
                                "name": "cpu",
                                "target": {
                                    "type": "Utilization",
                                    "averageUtilization": 70
                                }
                            }
                        },
```

**CPU scaling**: When average CPU across all pods exceeds 70%, we scale up. This prevents performance degradation.

### Step 20: Custom Metrics for Agent-Specific Scaling

Now let's add agent-specific metrics for more intelligent scaling decisions:

```python
                        {
                            "type": "Pods",
                            "pods": {
                                "metric": {
                                    "name": "agno_active_agents_count"
                                },
                                "target": {
                                    "type": "AverageValue",
                                    "averageValue": "10"
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        return manifests
```

**Agent-aware scaling**: This custom metric ensures we scale based on actual agent workload, not just CPU usage. Much more precise!

### Step 21: Building a Comprehensive Metrics System

Now let's create a metrics collection system that gives us deep visibility into our agent operations:

```python
class AgnoMetricsCollector:
    """Comprehensive metrics collection for Agno agents"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.metrics_registry = {}
        self.custom_collectors = []
```

**Metrics architecture**: We separate the registry from collectors, allowing us to add custom metrics dynamically.

### Step 22: Core Agent Performance Metrics

Let's start with the essential metrics every agent system needs:

```python
    def setup_agent_metrics(self) -> Dict[str, Any]:
        """Define comprehensive metrics for Agno agent monitoring"""
        
        metrics_config = {
            # Core agent metrics - The essentials
            "agno_agent_requests_total": {
                "type": "counter",
                "description": "Total number of agent requests processed",
                "labels": ["agent_name", "agent_type", "status", "model"]
            },
```

**Request tracking**: This counter tells us exactly how busy each agent is and success rates.

### Step 23: Response Time Monitoring

Let's add detailed latency tracking with histogram buckets:

```python
            "agno_agent_request_duration_seconds": {
                "type": "histogram", 
                "description": "Agent request processing duration",
                "labels": ["agent_name", "agent_type", "model"],
                "buckets": [0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
            },
```

**Histogram buckets**: These specific buckets let us track percentiles and identify slow requests quickly.

### Step 24: Resource Usage Monitoring

Now let's track memory consumption per agent:

```python
            "agno_agent_memory_usage_bytes": {
                "type": "gauge",
                "description": "Memory usage per agent",
                "labels": ["agent_name", "agent_type"]
            },
```

**Memory tracking**: Gauges are perfect for resource usage since they represent current state.

### Step 25: Team Collaboration Metrics

Let's add metrics specific to multi-agent workflows:

```python
            # Team and workflow metrics - Multi-agent insights
            "agno_team_execution_duration_seconds": {
                "type": "histogram",
                "description": "Team workflow execution time",
                "labels": ["team_name", "workflow_type"],
                "buckets": [1.0, 5.0, 15.0, 30.0, 60.0, 300.0]
            },
            "agno_agent_collaboration_count": {
                "type": "counter", 
                "description": "Number of agent collaborations",
                "labels": ["initiating_agent", "collaborating_agent", "task_type"]
            },
```

**Team performance**: These metrics help optimize multi-agent coordination and identify bottlenecks.

### Step 26: Tool and Model Usage Metrics

Let's track tool calls and model consumption:

```python
            # Tool and model metrics - Operational efficiency
            "agno_tool_calls_total": {
                "type": "counter",
                "description": "Total tool calls made by agents",
                "labels": ["agent_name", "tool_name", "status"]
            },
            "agno_tool_call_duration_seconds": {
                "type": "histogram",
                "description": "Tool call duration",
                "labels": ["tool_name"],
                "buckets": [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            },
            "agno_model_tokens_consumed": {
                "type": "counter",
                "description": "Total tokens consumed by model",
                "labels": ["model_name", "agent_name", "token_type"]
            },
```

**Tool performance**: These metrics help identify slow tools and optimize model usage for cost control.

### Step 27: Business and Cost Metrics

Finally, let's add business-critical metrics:

```python
            # Business metrics - What really matters
            "agno_cost_per_request_dollars": {
                "type": "gauge",
                "description": "Cost per request in dollars",
                "labels": ["agent_name", "model_name"]
            },
            "agno_user_satisfaction_score": {
                "type": "gauge",
                "description": "User satisfaction score (1-5)",
                "labels": ["agent_name", "interaction_type"]
            },
            "agno_cache_hit_ratio": {
                "type": "gauge",
                "description": "Cache hit ratio for cost optimization",
                "labels": ["cache_type", "agent_name"]
            }
        }
        
        return metrics_config
```

**Business focus**: These metrics connect technical performance to business outcomes - cost efficiency and user satisfaction.

---

## Part 2: Distributed Tracing and Advanced Observability

Add distributed tracing to track requests across multiple agents and services for debugging complex multi-agent workflows.

**File**: `src/session8/observability_stack.py` - Advanced tracing and monitoring

### Setting Up OpenTelemetry Infrastructure

Import essential components for distributed tracing. OpenTelemetry is the gold standard for observability:

```python
from typing import Dict, List, Any, Optional, Callable
import asyncio
import logging
from datetime import datetime, timedelta
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
```

OpenTelemetry is vendor-neutral, supports multiple languages, and provides complete observability in one framework.

### Distributed Tracing System Foundation

Create distributed tracing system to track requests across multiple agent services:

```python
class DistributedTracingSystem:
    """Comprehensive distributed tracing for multi-agent systems"""
    
    def __init__(self, service_name: str, jaeger_endpoint: str = "http://localhost:14268/api/traces"):
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint
        self.tracer_provider = None
        self.tracer = None
        self.logger = logging.getLogger(__name__)
```

Each agent service gets its own tracer for complete journey visibility across services.

### Tracer Provider Initialization

Set up the tracer provider to coordinate all tracing activities:

```python
    def initialize_tracing(self):
        """Initialize OpenTelemetry tracing with Jaeger export"""
        
        # Set up tracer provider
        self.tracer_provider = TracerProvider()
        trace.set_tracer_provider(self.tracer_provider)
```

The tracer provider is the factory that creates individual tracers for each service as the central coordination point.

### Jaeger Exporter Configuration

Configure Jaeger as the tracing backend for visualization and analysis:

```python
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
            collector_endpoint=self.jaeger_endpoint
        )
        
        # Add batch span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        self.tracer_provider.add_span_processor(span_processor)
```

**Batch processing**: Instead of sending each trace immediately, we batch them for better performance and reduced network overhead.

### Step 33: Getting the Service Tracer

Finally, let's get our service-specific tracer:

```python
        # Get tracer
        self.tracer = trace.get_tracer(self.service_name)
```

**Service isolation**: Each service has its own tracer, making it easy to filter and analyze traces by service.

### Step 34: Agent Execution Tracing Decorator

Now let's create a decorator that automatically traces agent execution. This gives us visibility into every agent operation:

```python
    def trace_agent_execution(self, agent_name: str, operation: str):
        """Decorator for tracing agent execution"""
        
        def decorator(func):
            async def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(
                    f"{agent_name}:{operation}",
                    attributes={
                        "agent.name": agent_name,
                        "agent.operation": operation,
                        "service.name": self.service_name
                    }
                ) as span:
```

**Span creation**: Each agent operation becomes a span with rich metadata. The naming convention makes it easy to identify operations.

### Step 35: Success Path Instrumentation

Let's handle the successful execution path with proper attribution:

```python
                    try:
                        # Execute the function
                        result = await func(*args, **kwargs)
                        
                        # Add success attributes
                        span.set_attribute("execution.status", "success")
                        span.set_attribute("execution.duration", 
                                         (datetime.now().timestamp() - span.start_time))
                        
                        return result
```

**Success tracking**: We capture execution time and mark successful operations, providing performance insights.

### Step 36: Error Path Instrumentation

Now let's handle errors with comprehensive error tracking:

```python
                    except Exception as e:
                        # Add error attributes
                        span.set_attribute("execution.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        span.record_exception(e)
                        raise
                        
            return wrapper
        return decorator
```

**Error enrichment**: We capture the full exception context, making debugging much easier when things go wrong.

### Step 37: Team Workflow Tracing

Let's add specialized tracing for multi-agent team workflows:

```python
    def trace_team_workflow(self, team_name: str, workflow_id: str):
        """Trace multi-agent team workflows"""
        
        return self.tracer.start_as_current_span(
            f"team_workflow:{team_name}",
            attributes={
                "team.name": team_name,
                "workflow.id": workflow_id,
                "workflow.type": "multi_agent_collaboration"
            }
        )
```

**Workflow visibility**: This creates parent spans for team workflows, allowing us to see how individual agent operations contribute to overall workflow performance.

### Step 38: Performance Profiler Foundation

Now let's build a performance profiler that gives us deep insights into agent performance:

```python
class PerformanceProfiler:
    """Advanced performance profiling for agent systems"""
    
    def __init__(self):
        self.profiling_data = {}
        self.performance_baselines = {}
        self.anomaly_thresholds = {}
```

**Profiler architecture**: We separate profiling data, baselines, and thresholds for clear organization and easy extensibility.

### Step 39: Performance Monitoring Configuration

Let's configure comprehensive performance monitoring across multiple dimensions:

```python
    def setup_performance_monitoring(self) -> Dict[str, Any]:
        """Configure comprehensive performance monitoring"""
        
        monitoring_config = {
            "cpu_profiling": {
                "enabled": True,
                "sampling_rate": 0.01,  # 1% sampling
                "profiling_duration": 60,  # seconds
                "output_format": "pprof"
            },
```

**CPU profiling**: We use statistical sampling (1%) to minimize overhead while still capturing performance hotspots.

### Step 40: Memory Profiling Configuration

Now let's add memory profiling for tracking memory usage patterns:

```python
            "memory_profiling": {
                "enabled": True,
                "track_allocations": True,
                "memory_threshold_mb": 1000,
                "gc_monitoring": True
            },
```

**Memory tracking**: We monitor allocations and garbage collection to identify memory leaks and optimization opportunities.

### Step 41: Latency and Throughput Monitoring

Let's configure latency percentiles and throughput monitoring:

```python
            "latency_profiling": {
                "enabled": True,
                "percentiles": [50, 90, 95, 99, 99.9],
                "histogram_buckets": [0.001, 0.01, 0.1, 1.0, 10.0]
            },
            "throughput_monitoring": {
                "enabled": True,
                "window_size_seconds": 60,
                "rate_limiting_threshold": 1000
            }
        }
        
        return monitoring_config
```

**Percentile tracking**: We track key percentiles (especially p99) to understand performance under load and identify outliers.

### Step 42: Agent Performance Profiling Implementation

Now let's implement the core profiling function that measures agent performance:

```python
    async def profile_agent_performance(self, agent_name: str, 
                                      operation_func: Callable,
                                      *args, **kwargs) -> Dict[str, Any]:
        """Profile individual agent performance comprehensively"""
        
        import time
        import psutil
        import asyncio
        
        # Capture baseline metrics
        start_time = time.perf_counter()
        start_memory = psutil.Process().memory_info().rss
```

**Baseline capture**: We capture starting conditions to measure deltas accurately. `perf_counter()` provides the highest resolution timing.

### Step 43: Performance Measurement Execution

Let's execute the operation while capturing comprehensive performance data:

```python
        try:
            # Execute operation with monitoring
            result = await operation_func(*args, **kwargs)
            
            # Capture performance metrics
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss
            
            performance_data = {
                "agent_name": agent_name,
                "execution_time": end_time - start_time,
                "memory_delta": end_memory - start_memory,
                "memory_peak": max(start_memory, end_memory),
                "timestamp": datetime.now().isoformat(),
                "result_size": len(str(result)) if result else 0,
                "status": "success"
            }
```

**Comprehensive metrics**: We capture execution time, memory usage, and result size to understand resource consumption patterns.

### Step 44: Anomaly Detection Integration

Let's add anomaly detection to automatically flag unusual performance:

```python
            # Check for performance anomalies
            anomalies = self._detect_performance_anomalies(performance_data)
            if anomalies:
                performance_data["anomalies"] = anomalies
                
            return performance_data
```

**Automated alerting**: By detecting anomalies automatically, we can proactively identify performance issues before they impact users.

### Step 45: Error Path Performance Tracking

Now let's handle error cases while still capturing performance data:

```python
        except Exception as e:
            # Capture error performance data
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss
            
            return {
                "agent_name": agent_name,
                "execution_time": end_time - start_time,
                "memory_delta": end_memory - start_memory,
                "error": str(e),
                "error_type": type(e).__name__,
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
```

**Error performance**: Even failed operations provide valuable performance insights for optimization and debugging.

### Step 46: Performance Anomaly Detection Algorithm

Let's implement statistical anomaly detection based on historical baselines:

```python
    def _detect_performance_anomalies(self, performance_data: Dict[str, Any]) -> List[str]:
        """Detect performance anomalies based on historical baselines"""
        
        anomalies = []
        agent_name = performance_data["agent_name"]
        
        # Check execution time anomalies
        if agent_name in self.performance_baselines:
            baseline = self.performance_baselines[agent_name]
            
            # Execution time anomaly (>3 standard deviations)
            if performance_data["execution_time"] > baseline.get("avg_execution_time", 0) + 3 * baseline.get("std_execution_time", 0):
                anomalies.append("high_execution_time")
```

**Statistical detection**: We use 3-sigma detection (3 standard deviations) to identify statistically significant performance anomalies.

### Step 47: Memory Anomaly Detection

Let's add memory usage anomaly detection:

```python
            # Memory usage anomaly
            if performance_data["memory_delta"] > baseline.get("avg_memory_delta", 0) + 3 * baseline.get("std_memory_delta", 0):
                anomalies.append("high_memory_usage")
        
        return anomalies
```

**Memory monitoring**: Memory anomalies often indicate memory leaks or inefficient data handling that needs attention.

### Step 48: Intelligent Alerting System Foundation

Now let's build an intelligent alerting system based on SLOs (Service Level Objectives):

```python
class AlertingSystem:
    """Intelligent alerting system for agent operations"""
    
    def __init__(self):
        self.alert_rules = {}
        self.notification_channels = {}
        self.alert_history = []
        self.suppression_rules = {}
```

**Alerting architecture**: We separate rules, channels, history, and suppression for flexible and maintainable alerting.

### Step 49: SLO-Based Alert Definitions

Let's define Service Level Objective-based alerts for production reliability:

```python
    def define_slo_based_alerts(self, service_name: str) -> Dict[str, Any]:
        """Define SLO-based alerting rules"""
        
        slo_alerts = {
            f"{service_name}_availability_slo": {
                "name": "Agent Service Availability SLO",
                "description": "Alert when service availability falls below 99.9%",
                "query": f'avg_over_time(up{{job="{service_name}"}}[5m]) < 0.999',
                "severity": "critical",
                "for": "2m",
                "error_budget_burn_rate": "fast",
```

**Availability SLO**: 99.9% availability means maximum 8.76 hours downtime per year. This is critical for production systems.

### Step 50: Latency SLO Configuration

Now let's define latency-based SLO alerts:

```python
            f"{service_name}_latency_slo": {
                "name": "Agent Response Time SLO", 
                "description": "Alert when 95% of requests exceed 2s",
                "query": f'histogram_quantile(0.95, rate(agno_agent_request_duration_seconds_bucket{{service="{service_name}"}}[5m])) > 2',
                "severity": "warning",
                "for": "5m",
                "error_budget_burn_rate": "medium",
```

**Latency SLO**: 95th percentile under 2 seconds ensures good user experience while allowing for some outliers.

### Step 51: Error Rate and Cost SLO Alerts

Let's add error rate and cost anomaly detection:

```python
            f"{service_name}_error_rate_slo": {
                "name": "Agent Error Rate SLO",
                "description": "Alert when error rate exceeds 1%", 
                "query": f'rate(agno_agent_requests_total{{service="{service_name}",status="error"}}[5m]) / rate(agno_agent_requests_total{{service="{service_name}"}}[5m]) > 0.01',
                "severity": "warning",
                "for": "3m",
            },
            
            f"{service_name}_cost_anomaly": {
                "name": "Agent Cost Anomaly Detection",
                "description": "Alert when cost per request increases significantly",
                "query": f'increase(agno_cost_per_request_dollars{{service="{service_name}"}}[1h]) > 0.1',
                "severity": "warning", 
                "for": "10m",
            }
        }
        
        return slo_alerts
```

**Business SLOs**: Error rate and cost monitoring connect technical metrics to business impact and budget control.

### Step 52: Intelligent Alert Routing System

Now let's implement intelligent alert routing based on context and severity:

```python
    async def intelligent_alert_routing(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently route alerts based on context and severity"""
        
        alert_context = {
            "alert_name": alert.get("name"),
            "severity": alert.get("severity"),
            "service": alert.get("service"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine routing strategy
        routing_strategy = self._determine_routing_strategy(alert)
```

**Context-aware routing**: We consider alert metadata, timing, and service criticality for intelligent routing decisions.

### Step 53: Alert Suppression Logic

Let's implement alert suppression to prevent alert fatigue:

```python
        # Check for suppression rules
        if self._should_suppress_alert(alert):
            return {
                "action": "suppressed",
                "reason": "suppression_rule_matched",
                "context": alert_context
            }
```

**Suppression prevents**: Duplicate alerts, maintenance window noise, and dependency cascade alerts from overwhelming teams.

### Step 54: Severity-Based Routing Implementation

Now let's implement routing logic based on alert severity:

```python
        # Route based on severity and business hours
        routing_actions = []
        
        if alert.get("severity") == "critical":
            # Immediate escalation for critical alerts
            routing_actions.extend([
                {"channel": "pagerduty", "escalation": "immediate"},
                {"channel": "slack", "channel_name": "#alerts-critical"},
                {"channel": "email", "recipients": ["oncall@company.com"]}
            ])
            
        elif alert.get("severity") == "warning":
            # Standard notification for warnings
            routing_actions.extend([
                {"channel": "slack", "channel_name": "#alerts-warning"},
                {"channel": "email", "recipients": ["team@company.com"]}
            ])
```

**Escalation strategy**: Critical alerts wake people up, warnings can wait until business hours. This prevents alert fatigue.

### Step 55: Routing Strategy Completion

Let's complete the routing system with strategy determination:

```python
        return {
            "action": "routed",
            "routing_actions": routing_actions,
            "context": alert_context,
            "strategy": routing_strategy
        }
    
    def _determine_routing_strategy(self, alert: Dict[str, Any]) -> str:
        """Determine intelligent routing strategy based on alert context"""
        
        # Business hours awareness
        current_hour = datetime.now().hour
        is_business_hours = 9 <= current_hour <= 17
        
        # Service criticality
        service = alert.get("service", "")
        is_critical_service = "production" in service.lower()
        
        if alert.get("severity") == "critical" and is_critical_service:
            return "immediate_escalation"
        elif is_business_hours:
            return "standard_notification"
        else:
            return "non_business_hours"
    
    def _should_suppress_alert(self, alert: Dict[str, Any]) -> bool:
        """Check if alert should be suppressed based on rules"""
        
        alert_name = alert.get("name")
        
        # Check maintenance windows
        # Check recent duplicate alerts
        # Check dependency failures
        
        return False  # Simplified implementation
```

**Smart routing**: The system considers time of day, service criticality, and alert severity to route appropriately without overwhelming teams.

---

## Part 3: Cost Monitoring and Business Intelligence (20 minutes)

Now let's build the most important part for any production system - intelligent cost monitoring. This system will track every penny spent and provide optimization suggestions to keep costs under control.

🗂️ **File**: `src/session8/cost_intelligence.py` - Intelligent cost monitoring and optimization

### Step 56: Cost Monitoring Foundation

First, let's set up our imports and define the cost metrics structure:

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
```

**Import strategy**: We use dataclasses for clean cost metric modeling and datetime for time-based cost aggregations.

### Step 57: Cost Metrics Data Structure

Let's define a comprehensive cost metrics structure that captures all relevant cost data:

```python
@dataclass
class CostMetrics:
    """Comprehensive cost tracking for agent operations"""
    timestamp: datetime
    service_name: str
    agent_name: str
    model_name: str
    input_tokens: int
    output_tokens: int
    cost_per_input_token: float
    cost_per_output_token: float
    total_cost: float
    request_id: str
    user_id: Optional[str] = None
    team_id: Optional[str] = None
```

**Comprehensive tracking**: We track everything needed for cost analysis - tokens, pricing, attribution to users/teams, and request correlation.

### Step 58: Intelligent Cost Monitoring System

Now let's create our main cost monitoring class:

```python
class IntelligentCostMonitoring:
    """Advanced cost monitoring with business intelligence"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.cost_history = []
        self.budget_alerts = {}
        self.cost_optimization_suggestions = []
        self.logger = logging.getLogger(__name__)
```

**System architecture**: We maintain cost history in memory for real-time analysis, plus budget alerts and optimization suggestions.

### Step 59: Cost Tracking Configuration

Let's configure our comprehensive cost tracking system:

```python
    def setup_cost_tracking(self) -> Dict[str, Any]:
        """Configure comprehensive cost tracking system"""
        
        cost_config = {
            "tracking_granularity": "per_request",
            "aggregation_windows": ["1h", "24h", "7d", "30d"],
            "cost_breakdown_dimensions": [
                "service", "agent", "model", "user", "team", "operation_type"
            ],
```

**Granular tracking**: Per-request tracking gives us maximum visibility, while multiple time windows enable trend analysis.

### Step 60: Budget Alert Configuration

Now let's set up budget limits and alert thresholds:

```python
            "budget_alerts": {
                "daily_budget": 100.0,  # $100 daily limit
                "weekly_budget": 500.0,  # $500 weekly limit
                "monthly_budget": 2000.0,  # $2000 monthly limit
                "alert_thresholds": [0.5, 0.8, 0.9, 1.0]  # 50%, 80%, 90%, 100%
            },
```

**Multi-tier budgets**: We set progressive alerts at 50%, 80%, 90%, and 100% to give early warnings before hitting limits.

### Step 61: Cost Optimization Settings

Let's configure automatic cost optimization targets:

```python
            "cost_optimization": {
                "cache_hit_target": 0.7,  # 70% cache hit rate
                "model_right_sizing": True,
                "auto_scaling_cost_aware": True
            }
        }
        
        return cost_config
```

**Optimization targets**: 70% cache hit rate significantly reduces costs, while model right-sizing ensures we use the cheapest appropriate model.

### Step 62: Agent Cost Tracking Implementation

Now let's implement the core cost tracking function:

```python
    async def track_agent_costs(self, agent_execution_data: Dict[str, Any]) -> CostMetrics:
        """Track costs for individual agent executions"""
        
        # Extract cost-relevant data
        agent_name = agent_execution_data.get("agent_name")
        model_name = agent_execution_data.get("model_name", "gpt-4")
        input_tokens = agent_execution_data.get("input_tokens", 0)
        output_tokens = agent_execution_data.get("output_tokens", 0)
```

**Data extraction**: We pull all cost-relevant data from the execution context to calculate accurate costs.

### Step 63: Model Pricing and Cost Calculation

Let's get current pricing and calculate the total cost:

```python
        # Get current pricing (simplified - in production, fetch from API)
        pricing = self._get_model_pricing(model_name)
        
        # Calculate costs
        input_cost = input_tokens * pricing["input_cost_per_token"]
        output_cost = output_tokens * pricing["output_cost_per_token"]
        total_cost = input_cost + output_cost
```

**Cost calculation**: We calculate separate input/output costs since pricing differs, then sum for total cost.

### Step 64: Cost Metrics Creation

Now let's create and store the complete cost metrics:

```python
        # Create cost metrics
        cost_metrics = CostMetrics(
            timestamp=datetime.now(),
            service_name=self.service_name,
            agent_name=agent_name,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_per_input_token=pricing["input_cost_per_token"],
            cost_per_output_token=pricing["output_cost_per_token"],
            total_cost=total_cost,
            request_id=agent_execution_data.get("request_id"),
            user_id=agent_execution_data.get("user_id"),
            team_id=agent_execution_data.get("team_id")
        )
```

**Complete attribution**: We capture everything needed for cost analysis, chargeback, and optimization.

### Step 65: Cost Storage and Analysis

Let's store the metrics and trigger analysis:

```python
        # Store for analysis
        self.cost_history.append(cost_metrics)
        
        # Check budget alerts
        await self._check_budget_alerts(cost_metrics)
        
        # Generate optimization suggestions
        optimization_suggestions = await self._generate_cost_optimizations(cost_metrics)
        
        return cost_metrics
```

**Real-time analysis**: We immediately check budgets and generate optimizations for every request to catch issues early.

### Step 66: Model Pricing Configuration

Now let's implement the pricing table for different models:

```python
    def _get_model_pricing(self, model_name: str) -> Dict[str, float]:
        """Get current model pricing (simplified)"""
        
        pricing_table = {
            "gpt-4": {
                "input_cost_per_token": 0.00003,
                "output_cost_per_token": 0.00006
            },
            "gpt-4-turbo": {
                "input_cost_per_token": 0.00001,
                "output_cost_per_token": 0.00003
            },
            "gpt-3.5-turbo": {
                "input_cost_per_token": 0.0000015,
                "output_cost_per_token": 0.000002
            }
        }
        
        return pricing_table.get(model_name, pricing_table["gpt-4"])
```

**Pricing management**: In production, this would fetch real-time pricing from provider APIs. Notice GPT-4 is 20x more expensive than GPT-3.5-turbo!

### Step 67: Budget Alert System Implementation

Let's implement comprehensive budget checking across multiple time windows:

```python
    async def _check_budget_alerts(self, cost_metrics: CostMetrics):
        """Check if budget thresholds are exceeded"""
        
        # Calculate current spend for different time windows
        now = datetime.now()
        
        # Daily spend
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_spend = sum(
            c.total_cost for c in self.cost_history 
            if c.timestamp >= daily_start
        )
```

**Time window calculation**: We calculate spending from midnight today to now for daily budget tracking.

### Step 68: Weekly and Monthly Budget Calculation

Now let's add weekly and monthly spend calculations:

```python
        # Weekly spend
        weekly_start = daily_start - timedelta(days=now.weekday())
        weekly_spend = sum(
            c.total_cost for c in self.cost_history 
            if c.timestamp >= weekly_start
        )
        
        # Monthly spend
        monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_spend = sum(
            c.total_cost for c in self.cost_history 
            if c.timestamp >= monthly_start
        )
```

**Multi-period tracking**: Weekly starts from Monday, monthly from the 1st. This gives complete budget visibility.

### Step 69: Budget Alert Generation

Let's generate alerts when budget thresholds are exceeded:

```python
        # Check thresholds and generate alerts
        alerts = []
        
        if daily_spend > 100.0 * 0.9:  # 90% of daily budget
            alerts.append({
                "type": "budget_alert",
                "severity": "warning",
                "message": f"Daily spend ({daily_spend:.2f}) approaching limit ($100.00)",
                "percentage": daily_spend / 100.0
            })
        
        # Log alerts (in production, send to alerting system)
        for alert in alerts:
            self.logger.warning(f"Budget Alert: {alert}")
```

**Progressive alerting**: We alert at 90% to give time for action before hitting the hard limit.

### Step 70: Cost Optimization Engine

Now let's implement intelligent cost optimization suggestions:

```python
    async def _generate_cost_optimizations(self, cost_metrics: CostMetrics) -> List[Dict[str, Any]]:
        """Generate intelligent cost optimization suggestions"""
        
        optimizations = []
        
        # Model selection optimization
        if cost_metrics.model_name == "gpt-4" and cost_metrics.input_tokens < 1000:
            optimizations.append({
                "type": "model_optimization",
                "suggestion": "Consider using gpt-3.5-turbo for simple requests",
                "potential_savings": cost_metrics.total_cost * 0.8,
                "confidence": 0.7
            })
```

**Model right-sizing**: For small requests (<1000 tokens), GPT-3.5-turbo often performs as well as GPT-4 at 1/20th the cost.

### Step 71: Caching Optimization Analysis

Let's implement caching potential analysis:

```python
        # Caching optimization
        recent_requests = [c for c in self.cost_history[-100:] if c.agent_name == cost_metrics.agent_name]
        if len(recent_requests) > 10:
            unique_requests = len(set(r.request_id for r in recent_requests))
            cache_potential = 1 - (unique_requests / len(recent_requests))
            
            if cache_potential > 0.3:  # 30% duplicate requests
                optimizations.append({
                    "type": "caching_optimization", 
                    "suggestion": f"Implement caching for {cost_metrics.agent_name}",
                    "potential_savings": cost_metrics.total_cost * cache_potential,
                    "confidence": 0.8
                })
        
        return optimizations
```

**Cache analysis**: If 30%+ of requests are duplicates, caching could provide significant savings.

### Step 72: Cost Dashboard Data Generation

Now let's create a comprehensive dashboard data generator:

```python
    def generate_cost_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for cost monitoring dashboard"""
        
        now = datetime.now()
        
        # Time-based aggregations
        hourly_costs = self._aggregate_costs_by_hour(24)  # Last 24 hours
        daily_costs = self._aggregate_costs_by_day(30)    # Last 30 days
        
        # Dimensional breakdowns
        cost_by_agent = self._aggregate_costs_by_dimension("agent_name")
        cost_by_model = self._aggregate_costs_by_dimension("model_name")
        cost_by_user = self._aggregate_costs_by_dimension("user_id")
```

**Multi-dimensional analysis**: We provide time-based trends and dimensional breakdowns for complete cost visibility.

### Step 73: Dashboard Summary Metrics

Let's add key summary metrics for the dashboard:

```python
        # Cost trends
        cost_trend = self._calculate_cost_trend()
        
        dashboard_data = {
            "timestamp": now.isoformat(),
            "summary": {
                "total_cost_today": sum(c.total_cost for c in self.cost_history if c.timestamp.date() == now.date()),
                "total_requests_today": len([c for c in self.cost_history if c.timestamp.date() == now.date()]),
                "average_cost_per_request": self._calculate_average_cost_per_request(),
                "cost_trend_percentage": cost_trend
            },
```

**Key metrics**: Total spend, request count, average cost per request, and trend analysis give immediate cost insight.

### Step 74: Dashboard Data Structure Completion

Let's complete the dashboard data structure:

```python
            "time_series": {
                "hourly_costs": hourly_costs,
                "daily_costs": daily_costs
            },
            "breakdowns": {
                "by_agent": cost_by_agent,
                "by_model": cost_by_model,
                "by_user": cost_by_user
            },
            "optimizations": self.cost_optimization_suggestions[-10:]  # Last 10 suggestions
        }
        
        return dashboard_data
```

**Complete visibility**: Time series for trends, breakdowns for attribution, and recent optimization suggestions for action.

### Step 75: Hourly Cost Aggregation

Now let's implement hourly cost aggregation:

```python
    def _aggregate_costs_by_hour(self, hours: int) -> List[Dict[str, Any]]:
        """Aggregate costs by hour for the specified time period"""
        
        now = datetime.now()
        hourly_data = []
        
        for i in range(hours):
            hour_start = (now - timedelta(hours=i)).replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            hour_costs = [
                c for c in self.cost_history 
                if hour_start <= c.timestamp < hour_end
            ]
```

**Time bucketing**: We create clean hourly buckets and filter costs within each time window.

### Step 76: Hourly Metrics Calculation

Let's calculate comprehensive metrics for each hour:

```python
            hourly_data.append({
                "timestamp": hour_start.isoformat(),
                "total_cost": sum(c.total_cost for c in hour_costs),
                "request_count": len(hour_costs),
                "unique_users": len(set(c.user_id for c in hour_costs if c.user_id))
            })
        
        return list(reversed(hourly_data))  # Return chronologically
```

**Hourly insights**: Cost, request count, and unique user count per hour help identify usage patterns and anomalies.

### Step 77: Dimensional Cost Aggregation

Finally, let's implement flexible dimensional aggregation:

```python
    def _aggregate_costs_by_dimension(self, dimension: str) -> List[Dict[str, Any]]:
        """Aggregate costs by specified dimension"""
        
        dimension_costs = {}
        
        for cost_metric in self.cost_history:
            dim_value = getattr(cost_metric, dimension, "unknown")
            if dim_value not in dimension_costs:
                dimension_costs[dim_value] = {
                    "total_cost": 0,
                    "request_count": 0,
                    "unique_timestamps": set()
                }
            
            dimension_costs[dim_value]["total_cost"] += cost_metric.total_cost
            dimension_costs[dim_value]["request_count"] += 1
            dimension_costs[dim_value]["unique_timestamps"].add(cost_metric.timestamp.date())
```

**Flexible aggregation**: This method works for any dimension (agent, model, user, team) to provide cost breakdowns.

### Step 78: Dimensional Results Processing

Let's complete the dimensional aggregation with result formatting:

```python
        # Convert to list and sort by cost
        result = []
        for dim_value, data in dimension_costs.items():
            result.append({
                "dimension_value": dim_value,
                "total_cost": data["total_cost"],
                "request_count": data["request_count"],
                "average_cost": data["total_cost"] / data["request_count"],
                "active_days": len(data["unique_timestamps"])
            })
        
        return sorted(result, key=lambda x: x["total_cost"], reverse=True)
```

**Cost ranking**: We sort by total cost (highest first) and include average cost per request and activity days for complete analysis.

---

## Module Summary

You've now mastered advanced monitoring and observability for production Agno systems:

✅ **Production Deployment**: Implemented containerized deployment with comprehensive health checks and monitoring  
✅ **Distributed Tracing**: Built OpenTelemetry integration with Jaeger for multi-agent workflow visibility  
✅ **Performance Profiling**: Created advanced profiling systems with anomaly detection and baseline comparison  
✅ **Intelligent Alerting**: Designed SLO-based alerting with intelligent routing and suppression rules  
✅ **Cost Intelligence**: Implemented comprehensive cost tracking with optimization suggestions and budget alerts

---

## 📝 Multiple Choice Test - Module A

Test your understanding of advanced monitoring and observability systems:

**Question 1:** What visualization capabilities does the advanced metrics dashboard provide for production monitoring?
A) Basic charts only  
B) Real-time dashboards with custom queries, alerting integration, and performance analytics  
C) Static reports only  
D) Manual data entry  

**Question 2:** How does the distributed tracing system track requests across microservices?
A) Single service tracking  
B) End-to-end trace correlation with span relationships and performance analysis  
C) Manual logging only  
D) Basic error tracking  

**Question 3:** What health check capabilities does the advanced monitoring provide?
A) Simple ping tests  
B) Multi-level health checks including service, database, and dependency status  
C) Manual status updates  
D) Binary health indicators  

**Question 4:** How does the alerting system determine notification severity and routing?
A) All alerts are the same priority  
B) Configurable severity levels with intelligent routing and escalation policies  
C) Manual alert management  
D) Email-only notifications  

**Question 5:** What performance analytics does the observability stack provide for optimization?
A) Basic counters only  
B) Comprehensive metrics including response times, error rates, and resource utilization trends  
C) Manual performance tracking  
D) Single metric monitoring  

[**🗂️ View Test Solutions →**](Session8_ModuleA_Test_Solutions.md)

### Next Steps

- **Continue to Module B**: [Enterprise Scaling & Architecture](Session8_ModuleB_Enterprise_Scaling_Architecture.md) for Kubernetes orchestration
- **Continue to Module C**: [Performance Optimization](Session8_ModuleC_Performance_Optimization.md) for caching and cost management
- **Return to Core**: [Session 8 Main](Session8_Agno_Production_Ready_Agents.md)

---

**🗂️ Source Files for Module A:**

- `src/session8/production_deployment.py` - Docker and Kubernetes deployment patterns
- `src/session8/observability_stack.py` - Distributed tracing and monitoring
- `src/session8/cost_intelligence.py` - Advanced cost monitoring and optimization
