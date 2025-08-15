# Session 8 - Module A: Advanced Monitoring & Observability (65 minutes)

**Prerequisites**: [Session 8 Core Section Complete](Session8_Agno_Production_Ready_Agents.md)  
**Target Audience**: DevOps engineers and SREs managing production agent systems  
**Cognitive Load**: 5 advanced concepts

---

## 🎯 Module Overview

This module explores comprehensive monitoring and observability for production Agno agent systems including distributed tracing, metrics collection, alerting strategies, performance profiling, and automated incident response. You'll learn to build robust observability stacks that provide deep visibility into agent performance, costs, and reliability.

### Learning Objectives
By the end of this module, you will:
- Implement comprehensive metrics collection and distributed tracing for agent systems
- Design alerting strategies with SLOs/SLIs and incident response automation
- Build performance profiling systems for agent optimization and cost management
- Create automated observability dashboards with business and technical metrics

---

## Part 1: Production Deployment & Monitoring Foundation (25 minutes)

### Containerized Deployment with Observability

🗂️ **File**: `src/session8/production_deployment.py` - Complete production deployment patterns

Production Agno systems require robust deployment strategies with built-in observability:

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
import json
from pathlib import Path

@dataclass
class ProductionConfig:
    """Complete production deployment configuration"""
    service_name: str
    version: str
    environment: str = "production"
    replicas: int = 3
    max_replicas: int = 10
    
    # Resource limits
    memory_limit: str = "2Gi"
    cpu_limit: str = "1000m"
    memory_request: str = "1Gi"
    cpu_request: str = "500m"
    
    # Health check configuration
    health_check_path: str = "/health"
    ready_check_path: str = "/ready"
    health_check_interval: int = 30
    health_check_timeout: int = 5
    
    # Monitoring configuration
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    logging_level: str = "INFO"

class AgnoProductionDeployment:
    """Production deployment manager for Agno agent systems"""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.deployment_manifests = {}
        self.monitoring_stack = {}
        self.logger = logging.getLogger(__name__)
        
    def generate_docker_configuration(self) -> str:
        """Generate production-ready Dockerfile for Agno agents"""
        
        dockerfile_content = f"""
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for monitoring
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    procps \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install monitoring dependencies
RUN pip install prometheus-client opentelemetry-api opentelemetry-sdk

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY monitoring/ ./monitoring/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash agno
RUN chown -R agno:agno /app
USER agno

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
                "spec": {
                    "replicas": self.config.replicas,
                    "selector": {
                        "matchLabels": {"app": self.config.service_name}
                    },
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

class AgnoMetricsCollector:
    """Comprehensive metrics collection for Agno agents"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.metrics_registry = {}
        self.custom_collectors = []
        
    def setup_agent_metrics(self) -> Dict[str, Any]:
        """Define comprehensive metrics for Agno agent monitoring"""
        
        metrics_config = {
            # Core agent metrics
            "agno_agent_requests_total": {
                "type": "counter",
                "description": "Total number of agent requests processed",
                "labels": ["agent_name", "agent_type", "status", "model"]
            },
            "agno_agent_request_duration_seconds": {
                "type": "histogram", 
                "description": "Agent request processing duration",
                "labels": ["agent_name", "agent_type", "model"],
                "buckets": [0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
            },
            "agno_agent_memory_usage_bytes": {
                "type": "gauge",
                "description": "Memory usage per agent",
                "labels": ["agent_name", "agent_type"]
            },
            
            # Team and workflow metrics
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
            
            # Tool and model metrics
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
            
            # Business metrics
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

---

## Part 2: Distributed Tracing and Advanced Observability (20 minutes)

### OpenTelemetry Integration

🗂️ **File**: `src/session8/observability_stack.py` - Advanced tracing and monitoring

```python
from typing import Dict, List, Any, Optional, Callable
import asyncio
import logging
from datetime import datetime, timedelta
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

class DistributedTracingSystem:
    """Comprehensive distributed tracing for multi-agent systems"""
    
    def __init__(self, service_name: str, jaeger_endpoint: str = "http://localhost:14268/api/traces"):
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint
        self.tracer_provider = None
        self.tracer = None
        self.logger = logging.getLogger(__name__)
        
    def initialize_tracing(self):
        """Initialize OpenTelemetry tracing with Jaeger export"""
        
        # Set up tracer provider
        self.tracer_provider = TracerProvider()
        trace.set_tracer_provider(self.tracer_provider)
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
            collector_endpoint=self.jaeger_endpoint
        )
        
        # Add batch span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        self.tracer_provider.add_span_processor(span_processor)
        
        # Get tracer
        self.tracer = trace.get_tracer(self.service_name)
        
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
                    try:
                        # Execute the function
                        result = await func(*args, **kwargs)
                        
                        # Add success attributes
                        span.set_attribute("execution.status", "success")
                        span.set_attribute("execution.duration", 
                                         (datetime.now().timestamp() - span.start_time))
                        
                        return result
                        
                    except Exception as e:
                        # Add error attributes
                        span.set_attribute("execution.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        span.record_exception(e)
                        raise
                        
            return wrapper
        return decorator
    
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

class PerformanceProfiler:
    """Advanced performance profiling for agent systems"""
    
    def __init__(self):
        self.profiling_data = {}
        self.performance_baselines = {}
        self.anomaly_thresholds = {}
        
    def setup_performance_monitoring(self) -> Dict[str, Any]:
        """Configure comprehensive performance monitoring"""
        
        monitoring_config = {
            "cpu_profiling": {
                "enabled": True,
                "sampling_rate": 0.01,  # 1% sampling
                "profiling_duration": 60,  # seconds
                "output_format": "pprof"
            },
            "memory_profiling": {
                "enabled": True,
                "track_allocations": True,
                "memory_threshold_mb": 1000,
                "gc_monitoring": True
            },
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
            
            # Check for performance anomalies
            anomalies = self._detect_performance_anomalies(performance_data)
            if anomalies:
                performance_data["anomalies"] = anomalies
                
            return performance_data
            
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
                
            # Memory usage anomaly
            if performance_data["memory_delta"] > baseline.get("avg_memory_delta", 0) + 3 * baseline.get("std_memory_delta", 0):
                anomalies.append("high_memory_usage")
        
        return anomalies

class AlertingSystem:
    """Intelligent alerting system for agent operations"""
    
    def __init__(self):
        self.alert_rules = {}
        self.notification_channels = {}
        self.alert_history = []
        self.suppression_rules = {}
        
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
                "annotations": {
                    "summary": f"{service_name} availability SLO violation",
                    "description": f"Service availability is below 99.9% SLO threshold"
                }
            },
            
            f"{service_name}_latency_slo": {
                "name": "Agent Response Time SLO", 
                "description": "Alert when 95% of requests exceed 2s",
                "query": f'histogram_quantile(0.95, rate(agno_agent_request_duration_seconds_bucket{{service="{service_name}"}}[5m])) > 2',
                "severity": "warning",
                "for": "5m",
                "error_budget_burn_rate": "medium",
                "annotations": {
                    "summary": f"{service_name} response time SLO violation",
                    "description": "95th percentile response time exceeds 2s SLO"
                }
            },
            
            f"{service_name}_error_rate_slo": {
                "name": "Agent Error Rate SLO",
                "description": "Alert when error rate exceeds 1%", 
                "query": f'rate(agno_agent_requests_total{{service="{service_name}",status="error"}}[5m]) / rate(agno_agent_requests_total{{service="{service_name}"}}[5m]) > 0.01',
                "severity": "warning",
                "for": "3m",
                "error_budget_burn_rate": "medium",
                "annotations": {
                    "summary": f"{service_name} error rate SLO violation",
                    "description": "Error rate exceeds 1% SLO threshold"
                }
            },
            
            f"{service_name}_cost_anomaly": {
                "name": "Agent Cost Anomaly Detection",
                "description": "Alert when cost per request increases significantly",
                "query": f'increase(agno_cost_per_request_dollars{{service="{service_name}"}}[1h]) > 0.1',
                "severity": "warning", 
                "for": "10m",
                "annotations": {
                    "summary": f"{service_name} cost anomaly detected",
                    "description": "Cost per request has increased by more than $0.10 in the last hour"
                }
            }
        }
        
        return slo_alerts
    
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
        
        # Check for suppression rules
        if self._should_suppress_alert(alert):
            return {
                "action": "suppressed",
                "reason": "suppression_rule_matched",
                "context": alert_context
            }
        
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

---

## Part 3: Cost Monitoring and Business Intelligence (20 minutes)

### Advanced Cost Management

🗂️ **File**: `src/session8/cost_intelligence.py` - Intelligent cost monitoring and optimization

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging

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

class IntelligentCostMonitoring:
    """Advanced cost monitoring with business intelligence"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.cost_history = []
        self.budget_alerts = {}
        self.cost_optimization_suggestions = []
        self.logger = logging.getLogger(__name__)
        
    def setup_cost_tracking(self) -> Dict[str, Any]:
        """Configure comprehensive cost tracking system"""
        
        cost_config = {
            "tracking_granularity": "per_request",
            "aggregation_windows": ["1h", "24h", "7d", "30d"],
            "cost_breakdown_dimensions": [
                "service", "agent", "model", "user", "team", "operation_type"
            ],
            "budget_alerts": {
                "daily_budget": 100.0,  # $100 daily limit
                "weekly_budget": 500.0,  # $500 weekly limit
                "monthly_budget": 2000.0,  # $2000 monthly limit
                "alert_thresholds": [0.5, 0.8, 0.9, 1.0]  # 50%, 80%, 90%, 100%
            },
            "cost_optimization": {
                "cache_hit_target": 0.7,  # 70% cache hit rate
                "model_right_sizing": True,
                "auto_scaling_cost_aware": True
            }
        }
        
        return cost_config
    
    async def track_agent_costs(self, agent_execution_data: Dict[str, Any]) -> CostMetrics:
        """Track costs for individual agent executions"""
        
        # Extract cost-relevant data
        agent_name = agent_execution_data.get("agent_name")
        model_name = agent_execution_data.get("model_name", "gpt-4")
        input_tokens = agent_execution_data.get("input_tokens", 0)
        output_tokens = agent_execution_data.get("output_tokens", 0)
        
        # Get current pricing (simplified - in production, fetch from API)
        pricing = self._get_model_pricing(model_name)
        
        # Calculate costs
        input_cost = input_tokens * pricing["input_cost_per_token"]
        output_cost = output_tokens * pricing["output_cost_per_token"]
        total_cost = input_cost + output_cost
        
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
        
        # Store for analysis
        self.cost_history.append(cost_metrics)
        
        # Check budget alerts
        await self._check_budget_alerts(cost_metrics)
        
        # Generate optimization suggestions
        optimization_suggestions = await self._generate_cost_optimizations(cost_metrics)
        
        return cost_metrics
    
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
            
            hourly_data.append({
                "timestamp": hour_start.isoformat(),
                "total_cost": sum(c.total_cost for c in hour_costs),
                "request_count": len(hour_costs),
                "unique_users": len(set(c.user_id for c in hour_costs if c.user_id))
            })
        
        return list(reversed(hourly_data))  # Return chronologically
    
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

---

## 🎯 Module Summary

You've now mastered advanced monitoring and observability for production Agno systems:

✅ **Production Deployment**: Implemented containerized deployment with comprehensive health checks and monitoring  
✅ **Distributed Tracing**: Built OpenTelemetry integration with Jaeger for multi-agent workflow visibility  
✅ **Performance Profiling**: Created advanced profiling systems with anomaly detection and baseline comparison  
✅ **Intelligent Alerting**: Designed SLO-based alerting with intelligent routing and suppression rules  
✅ **Cost Intelligence**: Implemented comprehensive cost tracking with optimization suggestions and budget alerts

### Next Steps
- **Continue to Module B**: [Enterprise Scaling & Architecture](Session8_ModuleB_Enterprise_Scaling_Architecture.md) for Kubernetes orchestration
- **Continue to Module C**: [Performance Optimization](Session8_ModuleC_Performance_Optimization.md) for caching and cost management
- **Return to Core**: [Session 8 Main](Session8_Agno_Production_Ready_Agents.md)

---

**🗂️ Source Files for Module A:**
- `src/session8/production_deployment.py` - Docker and Kubernetes deployment patterns
- `src/session8/observability_stack.py` - Distributed tracing and monitoring
- `src/session8/cost_intelligence.py` - Advanced cost monitoring and optimization