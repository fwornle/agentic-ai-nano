"""
Agno Comprehensive Monitoring and Alerting System
Session 7: Agno Production-Ready Agents

This module implements enterprise-grade monitoring, observability, and alerting
with Prometheus metrics, distributed tracing, structured logging, and dashboards.
"""

import asyncio
import logging
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
from collections import defaultdict, deque
import statistics

try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary, Info
    from prometheus_client import CollectorRegistry, generate_latest
    from prometheus_client.exposition import start_http_server
except ImportError:
    print("Warning: prometheus_client not available, using mock implementation")
    prometheus_client = None

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class AlertRule:
    """Alert rule definition"""
    name: str
    description: str
    condition: str  # Prometheus query expression
    severity: AlertSeverity
    duration: str = "5m"  # How long condition must be true
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class Alert:
    """Active alert instance"""
    rule_name: str
    severity: AlertSeverity
    message: str
    labels: Dict[str, str]
    started_at: datetime
    resolved_at: Optional[datetime] = None
    
    @property
    def is_active(self) -> bool:
        return self.resolved_at is None
    
    @property
    def duration(self) -> float:
        end_time = self.resolved_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()

@dataclass
class HealthMetrics:
    """System health metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    response_time_p95: float
    error_rate: float
    throughput: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

class PrometheusMetricsCollector:
    """Advanced Prometheus metrics collector for Agno agents"""
    
    def __init__(self, service_name: str = "agno-agent", registry: Optional[prometheus_client.CollectorRegistry] = None):
        self.service_name = service_name
        self.registry = registry or prometheus_client.CollectorRegistry()
        
        # Initialize core metrics
        self._initialize_core_metrics()
        
        # Custom metrics storage
        self.custom_metrics: Dict[str, Any] = {}
        
        # Metrics cache for aggregation
        self.metrics_cache = deque(maxlen=1000)
        
        logger.info(f"Initialized Prometheus metrics collector for {service_name}")
    
    def _initialize_core_metrics(self):
        """Initialize core application metrics"""
        
        # Request metrics
        self.requests_total = Counter(
            'agno_requests_total',
            'Total number of requests processed',
            ['agent_name', 'status', 'method'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'agno_request_duration_seconds',
            'Request processing time in seconds',
            ['agent_name', 'method'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        # Agent-specific metrics
        self.active_agents = Gauge(
            'agno_active_agents',
            'Number of active agent instances',
            ['agent_type'],
            registry=self.registry
        )
        
        self.agent_memory_usage = Gauge(
            'agno_agent_memory_bytes',
            'Memory usage per agent in bytes',
            ['agent_name'],
            registry=self.registry
        )
        
        # Model and cost metrics
        self.model_calls_total = Counter(
            'agno_model_calls_total',
            'Total API calls to language models',
            ['provider', 'model', 'agent_name'],
            registry=self.registry
        )
        
        self.token_usage_total = Counter(
            'agno_tokens_used_total',
            'Total tokens consumed',
            ['type', 'model', 'agent_name'],
            registry=self.registry
        )
        
        self.api_cost_total = Counter(
            'agno_api_cost_dollars_total',
            'Total API costs in USD',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # Quality and performance metrics
        self.response_quality = Histogram(
            'agno_response_quality_score',
            'Quality scores for agent responses',
            ['agent_name', 'evaluation_method'],
            buckets=[0.0, 0.2, 0.4, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0],
            registry=self.registry
        )
        
        self.cache_hits_total = Counter(
            'agno_cache_hits_total',
            'Total cache hits',
            ['cache_type', 'agent_name'],
            registry=self.registry
        )
        
        self.cache_misses_total = Counter(
            'agno_cache_misses_total',
            'Total cache misses',
            ['cache_type', 'agent_name'],
            registry=self.registry
        )
        
        # Circuit breaker metrics
        self.circuit_breaker_state = Gauge(
            'agno_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half-open)',
            ['agent_name', 'circuit_name'],
            registry=self.registry
        )
        
        # System health metrics
        self.health_check_duration = Histogram(
            'agno_health_check_duration_seconds',
            'Health check duration in seconds',
            ['agent_name'],
            registry=self.registry
        )
        
        self.health_status = Gauge(
            'agno_health_status',
            'Health status (1=healthy, 0=unhealthy)',
            ['agent_name'],
            registry=self.registry
        )
        
        # Business metrics
        self.tasks_completed = Counter(
            'agno_tasks_completed_total',
            'Total tasks completed successfully',
            ['agent_name', 'task_type'],
            registry=self.registry
        )
        
        self.workflow_duration = Histogram(
            'agno_workflow_duration_seconds',
            'Workflow execution time in seconds',
            ['workflow_type', 'success'],
            registry=self.registry
        )
    
    def record_request(self, agent_name: str, method: str, status: str, duration: float):
        """Record request metrics"""
        self.requests_total.labels(
            agent_name=agent_name, 
            status=status, 
            method=method
        ).inc()
        
        self.request_duration.labels(
            agent_name=agent_name, 
            method=method
        ).observe(duration)
    
    def record_model_usage(self, provider: str, model: str, agent_name: str, 
                          input_tokens: int, output_tokens: int, cost: float):
        """Record model usage metrics"""
        self.model_calls_total.labels(
            provider=provider, 
            model=model, 
            agent_name=agent_name
        ).inc()
        
        self.token_usage_total.labels(
            type="input", 
            model=model, 
            agent_name=agent_name
        ).inc(input_tokens)
        
        self.token_usage_total.labels(
            type="output", 
            model=model, 
            agent_name=agent_name
        ).inc(output_tokens)
        
        self.api_cost_total.labels(
            provider=provider, 
            model=model
        ).inc(cost)
    
    def record_quality_score(self, agent_name: str, evaluation_method: str, score: float):
        """Record response quality metrics"""
        self.response_quality.labels(
            agent_name=agent_name,
            evaluation_method=evaluation_method
        ).observe(score)
    
    def record_cache_hit(self, cache_type: str, agent_name: str):
        """Record cache hit"""
        self.cache_hits_total.labels(
            cache_type=cache_type,
            agent_name=agent_name
        ).inc()
    
    def record_cache_miss(self, cache_type: str, agent_name: str):
        """Record cache miss"""
        self.cache_misses_total.labels(
            cache_type=cache_type,
            agent_name=agent_name
        ).inc()
    
    def update_circuit_breaker_state(self, agent_name: str, circuit_name: str, state: int):
        """Update circuit breaker state (0=closed, 1=open, 2=half-open)"""
        self.circuit_breaker_state.labels(
            agent_name=agent_name,
            circuit_name=circuit_name
        ).set(state)
    
    def record_health_check(self, agent_name: str, duration: float, is_healthy: bool):
        """Record health check metrics"""
        self.health_check_duration.labels(agent_name=agent_name).observe(duration)
        self.health_status.labels(agent_name=agent_name).set(1 if is_healthy else 0)
    
    def record_task_completion(self, agent_name: str, task_type: str):
        """Record successful task completion"""
        self.tasks_completed.labels(
            agent_name=agent_name,
            task_type=task_type
        ).inc()
    
    def record_workflow_execution(self, workflow_type: str, duration: float, success: bool):
        """Record workflow execution metrics"""
        self.workflow_duration.labels(
            workflow_type=workflow_type,
            success=str(success).lower()
        ).observe(duration)
    
    def create_custom_metric(self, name: str, metric_type: MetricType, 
                           description: str, labels: List[str] = None) -> Any:
        """Create custom metric"""
        labels = labels or []
        
        if metric_type == MetricType.COUNTER:
            metric = Counter(name, description, labels, registry=self.registry)
        elif metric_type == MetricType.GAUGE:
            metric = Gauge(name, description, labels, registry=self.registry)
        elif metric_type == MetricType.HISTOGRAM:
            metric = Histogram(name, description, labels, registry=self.registry)
        elif metric_type == MetricType.SUMMARY:
            metric = Summary(name, description, labels, registry=self.registry)
        else:
            raise ValueError(f"Unsupported metric type: {metric_type}")
        
        self.custom_metrics[name] = metric
        logger.info(f"Created custom metric: {name} ({metric_type.value})")
        return metric
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        try:
            # Generate metrics data
            metrics_data = generate_latest(self.registry).decode('utf-8')
            
            # Parse key metrics for summary
            summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "service_name": self.service_name,
                "total_custom_metrics": len(self.custom_metrics),
                "registry_collectors": len(list(self.registry._collector_to_names.keys())),
                "metrics_size_bytes": len(metrics_data.encode('utf-8'))
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate metrics summary: {e}")
            return {"error": str(e)}

class DistributedTracing:
    """Distributed tracing system for multi-agent workflows"""
    
    def __init__(self, service_name: str = "agno-agent"):
        self.service_name = service_name
        self.active_traces: Dict[str, Dict] = {}
        self.completed_traces: deque = deque(maxlen=1000)
        
        # Trace correlation
        self.trace_correlations: Dict[str, List[str]] = defaultdict(list)
        
    def start_trace(self, trace_id: str, operation_name: str, 
                   parent_span_id: Optional[str] = None) -> Dict[str, Any]:
        """Start a new distributed trace"""
        span = {
            "trace_id": trace_id,
            "span_id": f"{trace_id}_{len(self.active_traces)}",
            "parent_span_id": parent_span_id,
            "operation_name": operation_name,
            "service_name": self.service_name,
            "start_time": datetime.utcnow(),
            "tags": {},
            "logs": [],
            "status": "active"
        }
        
        self.active_traces[span["span_id"]] = span
        
        if parent_span_id:
            self.trace_correlations[trace_id].append(span["span_id"])
        
        logger.debug(f"Started trace: {trace_id} / {span['span_id']}")
        return span
    
    def add_span_tag(self, span_id: str, key: str, value: Any):
        """Add tag to span"""
        if span_id in self.active_traces:
            self.active_traces[span_id]["tags"][key] = value
    
    def add_span_log(self, span_id: str, message: str, level: str = "info"):
        """Add log entry to span"""
        if span_id in self.active_traces:
            log_entry = {
                "timestamp": datetime.utcnow(),
                "level": level,
                "message": message
            }
            self.active_traces[span_id]["logs"].append(log_entry)
    
    def finish_trace(self, span_id: str, status: str = "completed", error: Optional[str] = None):
        """Finish a trace span"""
        if span_id in self.active_traces:
            span = self.active_traces[span_id]
            span["end_time"] = datetime.utcnow()
            span["duration"] = (span["end_time"] - span["start_time"]).total_seconds()
            span["status"] = status
            
            if error:
                span["error"] = error
                span["tags"]["error"] = True
            
            # Move to completed traces
            self.completed_traces.append(span)
            del self.active_traces[span_id]
            
            logger.debug(f"Finished trace: {span['trace_id']} / {span_id} ({span['duration']:.3f}s)")
    
    def get_trace_timeline(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get complete timeline for a trace"""
        timeline = []
        
        # Add active spans
        for span in self.active_traces.values():
            if span["trace_id"] == trace_id:
                timeline.append(span)
        
        # Add completed spans
        for span in self.completed_traces:
            if span["trace_id"] == trace_id:
                timeline.append(span)
        
        # Sort by start time
        return sorted(timeline, key=lambda x: x["start_time"])
    
    def get_trace_statistics(self) -> Dict[str, Any]:
        """Get tracing statistics"""
        return {
            "active_traces": len(self.active_traces),
            "completed_traces": len(self.completed_traces),
            "total_correlations": len(self.trace_correlations),
            "avg_trace_duration": self._calculate_avg_trace_duration(),
            "error_rate": self._calculate_trace_error_rate()
        }
    
    def _calculate_avg_trace_duration(self) -> float:
        """Calculate average trace duration"""
        durations = [span.get("duration", 0) for span in self.completed_traces 
                    if span.get("duration")]
        return statistics.mean(durations) if durations else 0.0
    
    def _calculate_trace_error_rate(self) -> float:
        """Calculate trace error rate"""
        if not self.completed_traces:
            return 0.0
        
        error_traces = sum(1 for span in self.completed_traces 
                          if span.get("error") or span.get("status") == "error")
        return error_traces / len(self.completed_traces)

class AlertManager:
    """Comprehensive alerting system"""
    
    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        
        # Alert channels
        self.notification_channels: List[Callable] = []
        
        # Silence and suppression
        self.silenced_alerts: Dict[str, datetime] = {}
        
        # Alert processing
        self.alert_processor_running = False
        
    def register_alert_rule(self, rule: AlertRule):
        """Register new alert rule"""
        self.alert_rules[rule.name] = rule
        logger.info(f"Registered alert rule: {rule.name} ({rule.severity.value})")
    
    def add_notification_channel(self, channel: Callable):
        """Add notification channel (e.g., email, Slack, webhook)"""
        self.notification_channels.append(channel)
    
    def trigger_alert(self, rule_name: str, message: str, labels: Dict[str, str] = None):
        """Trigger an alert"""
        if rule_name not in self.alert_rules:
            logger.error(f"Unknown alert rule: {rule_name}")
            return
        
        rule = self.alert_rules[rule_name]
        labels = labels or {}
        
        # Check if alert is silenced
        silence_key = f"{rule_name}:{json.dumps(sorted(labels.items()))}"
        if silence_key in self.silenced_alerts:
            if datetime.utcnow() < self.silenced_alerts[silence_key]:
                logger.debug(f"Alert silenced: {rule_name}")
                return
            else:
                del self.silenced_alerts[silence_key]
        
        # Create alert
        alert = Alert(
            rule_name=rule_name,
            severity=rule.severity,
            message=message,
            labels=labels,
            started_at=datetime.utcnow()
        )
        
        alert_key = f"{rule_name}:{hash(json.dumps(sorted(labels.items())))}"
        
        # Check if alert is already active
        if alert_key not in self.active_alerts:
            self.active_alerts[alert_key] = alert
            self.alert_history.append(alert)
            
            # Send notifications
            asyncio.create_task(self._send_alert_notifications(alert))
            
            logger.warning(f"Alert triggered: {rule_name} - {message}")
    
    def resolve_alert(self, rule_name: str, labels: Dict[str, str] = None):
        """Resolve an active alert"""
        labels = labels or {}
        alert_key = f"{rule_name}:{hash(json.dumps(sorted(labels.items())))}"
        
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            alert.resolved_at = datetime.utcnow()
            
            del self.active_alerts[alert_key]
            
            # Send resolution notification
            asyncio.create_task(self._send_resolution_notifications(alert))
            
            logger.info(f"Alert resolved: {rule_name} (duration: {alert.duration:.1f}s)")
    
    def silence_alert(self, rule_name: str, duration_hours: float, labels: Dict[str, str] = None):
        """Silence alert for specified duration"""
        labels = labels or {}
        silence_key = f"{rule_name}:{json.dumps(sorted(labels.items()))}"
        silence_until = datetime.utcnow() + timedelta(hours=duration_hours)
        
        self.silenced_alerts[silence_key] = silence_until
        logger.info(f"Silenced alert: {rule_name} until {silence_until}")
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications to all channels"""
        for channel in self.notification_channels:
            try:
                await channel(alert, "triggered")
            except Exception as e:
                logger.error(f"Failed to send alert notification: {e}")
    
    async def _send_resolution_notifications(self, alert: Alert):
        """Send alert resolution notifications"""
        for channel in self.notification_channels:
            try:
                await channel(alert, "resolved")
            except Exception as e:
                logger.error(f"Failed to send resolution notification: {e}")
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get current alert summary"""
        by_severity = defaultdict(int)
        for alert in self.active_alerts.values():
            by_severity[alert.severity.value] += 1
        
        recent_alerts = list(self.alert_history)[-100:]  # Last 100 alerts
        
        return {
            "active_alerts": len(self.active_alerts),
            "alerts_by_severity": dict(by_severity),
            "silenced_alerts": len(self.silenced_alerts),
            "total_alert_rules": len(self.alert_rules),
            "recent_alerts_count": len(recent_alerts),
            "avg_resolution_time": self._calculate_avg_resolution_time(recent_alerts)
        }
    
    def _calculate_avg_resolution_time(self, alerts: List[Alert]) -> float:
        """Calculate average alert resolution time"""
        resolved_alerts = [alert for alert in alerts if alert.resolved_at]
        if not resolved_alerts:
            return 0.0
        
        total_duration = sum(alert.duration for alert in resolved_alerts)
        return total_duration / len(resolved_alerts)

class HealthMonitor:
    """Comprehensive system health monitoring"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.health_checks: Dict[str, Callable] = {}
        self.health_history: deque = deque(maxlen=1000)
        self.current_health: Dict[str, Any] = {}
        
        # Built-in health checks
        self._register_builtin_checks()
        
        # Start monitoring
        self.monitoring_task = None
    
    def _register_builtin_checks(self):
        """Register built-in health checks"""
        self.health_checks["system_resources"] = self._check_system_resources
        self.health_checks["disk_space"] = self._check_disk_space
        self.health_checks["network_connectivity"] = self._check_network_connectivity
    
    def register_health_check(self, name: str, check_func: Callable):
        """Register custom health check"""
        self.health_checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    async def start_monitoring(self):
        """Start health monitoring loop"""
        if self.monitoring_task is None:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Started health monitoring")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
            logger.info("Stopped health monitoring")
    
    async def _monitoring_loop(self):
        """Main health monitoring loop"""
        while True:
            try:
                health_snapshot = await self.perform_health_checks()
                self.health_history.append(health_snapshot)
                self.current_health = health_snapshot
                
                # Check for health issues
                await self._evaluate_health_status(health_snapshot)
                
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def perform_health_checks(self) -> Dict[str, Any]:
        """Perform all registered health checks"""
        health_snapshot = {
            "timestamp": datetime.utcnow(),
            "checks": {},
            "overall_status": "healthy"
        }
        
        for check_name, check_func in self.health_checks.items():
            try:
                result = await check_func()
                health_snapshot["checks"][check_name] = result
                
                if result.get("status") != "healthy":
                    health_snapshot["overall_status"] = "unhealthy"
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                health_snapshot["checks"][check_name] = {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow()
                }
                health_snapshot["overall_status"] = "unhealthy"
        
        return health_snapshot
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            status = "healthy"
            issues = []
            
            if cpu_percent > 90:
                status = "critical"
                issues.append(f"High CPU usage: {cpu_percent}%")
            elif cpu_percent > 80:
                status = "warning"
                issues.append(f"Elevated CPU usage: {cpu_percent}%")
            
            if memory.percent > 90:
                status = "critical"
                issues.append(f"High memory usage: {memory.percent}%")
            elif memory.percent > 80:
                status = "warning" if status == "healthy" else status
                issues.append(f"Elevated memory usage: {memory.percent}%")
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "issues": issues,
                "timestamp": datetime.utcnow()
            }
            
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not available",
                "timestamp": datetime.utcnow()
            }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100
            
            status = "healthy"
            if free_percent < 10:
                status = "critical"
            elif free_percent < 20:
                status = "warning"
            
            return {
                "status": status,
                "free_percent": free_percent,
                "free_bytes": free,
                "total_bytes": total,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow()
            }
    
    async def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                start_time = time.time()
                async with session.get('https://httpbin.org/get') as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        status = "healthy" if response_time < 2.0 else "warning"
                        return {
                            "status": status,
                            "response_time": response_time,
                            "endpoint": "httpbin.org",
                            "timestamp": datetime.utcnow()
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"HTTP {response.status}",
                            "timestamp": datetime.utcnow()
                        }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow()
            }
    
    async def _evaluate_health_status(self, health_snapshot: Dict[str, Any]):
        """Evaluate health status and trigger alerts if needed"""
        if health_snapshot["overall_status"] != "healthy":
            issues = []
            for check_name, result in health_snapshot["checks"].items():
                if result.get("status") not in ["healthy", "ok"]:
                    issues.extend(result.get("issues", [result.get("message", "Unknown issue")]))
            
            # Trigger health alert (would integrate with AlertManager)
            logger.warning(f"Health issues detected: {'; '.join(issues)}")

class MonitoringDashboard:
    """Monitoring dashboard generator"""
    
    def __init__(self, metrics_collector: PrometheusMetricsCollector,
                 alert_manager: AlertManager,
                 health_monitor: HealthMonitor):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.health_monitor = health_monitor
    
    def generate_grafana_dashboard(self) -> Dict[str, Any]:
        """Generate Grafana dashboard configuration"""
        dashboard = {
            "dashboard": {
                "title": "Agno Agent Monitoring",
                "tags": ["agno", "agents", "production"],
                "timezone": "UTC",
                "refresh": "30s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": []
            }
        }
        
        # Request rate panel
        dashboard["dashboard"]["panels"].append({
            "title": "Request Rate",
            "type": "graph",
            "targets": [{
                "expr": "sum(rate(agno_requests_total[5m])) by (agent_name)",
                "legendFormat": "{{agent_name}}"
            }],
            "yAxes": [{
                "label": "Requests/sec"
            }]
        })
        
        # Response time panel
        dashboard["dashboard"]["panels"].append({
            "title": "Response Time (95th percentile)",
            "type": "graph",
            "targets": [{
                "expr": "histogram_quantile(0.95, sum(rate(agno_request_duration_seconds_bucket[5m])) by (le, agent_name))",
                "legendFormat": "{{agent_name}}"
            }],
            "yAxes": [{
                "label": "Seconds"
            }]
        })
        
        # Error rate panel
        dashboard["dashboard"]["panels"].append({
            "title": "Error Rate",
            "type": "graph",
            "targets": [{
                "expr": "sum(rate(agno_requests_total{status='error'}[5m])) / sum(rate(agno_requests_total[5m]))",
                "legendFormat": "Error Rate"
            }],
            "yAxes": [{
                "label": "Percentage",
                "max": 1.0
            }]
        })
        
        # Active agents panel
        dashboard["dashboard"]["panels"].append({
            "title": "Active Agents",
            "type": "singlestat",
            "targets": [{
                "expr": "sum(agno_active_agents)"
            }]
        })
        
        # Cost tracking panel
        dashboard["dashboard"]["panels"].append({
            "title": "API Costs",
            "type": "graph",
            "targets": [{
                "expr": "sum(rate(agno_api_cost_dollars_total[1h])) by (provider)",
                "legendFormat": "{{provider}}"
            }],
            "yAxes": [{
                "label": "USD/hour"
            }]
        })
        
        return dashboard

async def demonstrate_monitoring_system():
    """Comprehensive demonstration of monitoring system"""
    print("=" * 80)
    print("AGNO COMPREHENSIVE MONITORING SYSTEM DEMONSTRATION")
    print("=" * 80)
    
    # Initialize monitoring components
    metrics_collector = PrometheusMetricsCollector("demo-agno-service")
    tracer = DistributedTracing("demo-agno-service")
    alert_manager = AlertManager()
    health_monitor = HealthMonitor(check_interval=10)  # Faster for demo
    
    print(f"\n1. Monitoring Components Initialization")
    print("-" * 45)
    print(f"✓ Prometheus Metrics Collector")
    print(f"✓ Distributed Tracing System")
    print(f"✓ Alert Manager")
    print(f"✓ Health Monitor")
    
    # Configure alert rules
    print(f"\n2. Alert Rules Configuration")
    print("-" * 35)
    
    # High error rate alert
    high_error_alert = AlertRule(
        name="HighErrorRate",
        description="Error rate exceeds threshold",
        condition="rate(agno_requests_total{status='error'}[5m]) > 0.1",
        severity=AlertSeverity.CRITICAL,
        duration="2m"
    )
    alert_manager.register_alert_rule(high_error_alert)
    
    # High latency alert
    high_latency_alert = AlertRule(
        name="HighLatency",
        description="Response time is too high",
        condition="agno_request_duration_seconds{quantile='0.95'} > 30",
        severity=AlertSeverity.WARNING,
        duration="5m"
    )
    alert_manager.register_alert_rule(high_latency_alert)
    
    # Service down alert
    service_down_alert = AlertRule(
        name="ServiceDown", 
        description="Service is not responding",
        condition="up{job='agno-agent'} == 0",
        severity=AlertSeverity.EMERGENCY,
        duration="1m"
    )
    alert_manager.register_alert_rule(service_down_alert)
    
    print(f"Configured {len(alert_manager.alert_rules)} alert rules:")
    for rule_name, rule in alert_manager.alert_rules.items():
        print(f"  - {rule_name}: {rule.severity.value}")
    
    # Start health monitoring
    print(f"\n3. Health Monitoring")
    print("-" * 25)
    
    await health_monitor.start_monitoring()
    
    # Simulate some monitoring activity
    print("Simulating agent activity and collecting metrics...")
    
    # Simulate requests and record metrics
    agents = ["data_collector", "analyst", "writer", "reviewer"]
    
    for i in range(20):
        agent_name = agents[i % len(agents)]
        
        # Simulate request
        duration = 0.5 + (i % 10) * 0.1  # Varying response times
        status = "success" if i % 10 != 0 else "error"  # 10% error rate
        
        metrics_collector.record_request(agent_name, "process", status, duration)
        
        # Simulate model usage
        if status == "success":
            metrics_collector.record_model_usage(
                "openai", "gpt-4o", agent_name,
                input_tokens=100 + i*10,
                output_tokens=200 + i*20,
                cost=0.01 + i*0.001
            )
            
            # Record quality score
            quality_score = 0.8 + (i % 5) * 0.04  # Varying quality
            metrics_collector.record_quality_score(agent_name, "automated", quality_score)
        
        # Simulate cache activity
        if i % 3 == 0:
            metrics_collector.record_cache_hit("l1_cache", agent_name)
        else:
            metrics_collector.record_cache_miss("l1_cache", agent_name)
    
    # Simulate distributed trace
    trace_id = "trace_001"
    span1 = tracer.start_trace(trace_id, "workflow_execution")
    tracer.add_span_tag(span1["span_id"], "workflow_type", "sequential")
    tracer.add_span_log(span1["span_id"], "Starting workflow execution")
    
    # Child span
    span2 = tracer.start_trace(trace_id, "data_collection", span1["span_id"])
    tracer.add_span_tag(span2["span_id"], "agent_name", "data_collector")
    await asyncio.sleep(0.1)  # Simulate work
    tracer.finish_trace(span2["span_id"], "completed")
    
    # Another child span
    span3 = tracer.start_trace(trace_id, "analysis", span1["span_id"])
    tracer.add_span_tag(span3["span_id"], "agent_name", "analyst")
    await asyncio.sleep(0.2)  # Simulate work
    tracer.finish_trace(span3["span_id"], "completed")
    
    tracer.add_span_log(span1["span_id"], "Workflow completed successfully")
    tracer.finish_trace(span1["span_id"], "completed")
    
    # Trigger some alerts for demonstration
    alert_manager.trigger_alert("HighErrorRate", "Error rate is 15% over last 5 minutes", 
                               {"service": "demo-agno", "severity": "critical"})
    
    # Let some time pass for health checks
    await asyncio.sleep(2)
    
    # Get monitoring statistics
    print(f"\n4. Metrics Summary")
    print("-" * 25)
    
    metrics_summary = metrics_collector.get_metrics_summary()
    print(f"Service: {metrics_summary['service_name']}")
    print(f"Custom Metrics: {metrics_summary['total_custom_metrics']}")
    print(f"Registry Collectors: {metrics_summary['registry_collectors']}")
    print(f"Metrics Size: {metrics_summary['metrics_size_bytes']} bytes")
    
    print(f"\n5. Distributed Tracing Statistics")
    print("-" * 40)
    
    trace_stats = tracer.get_trace_statistics()
    print(f"Active Traces: {trace_stats['active_traces']}")
    print(f"Completed Traces: {trace_stats['completed_traces']}")
    print(f"Average Duration: {trace_stats['avg_trace_duration']:.3f}s")
    print(f"Error Rate: {trace_stats['error_rate']:.1%}")
    
    # Show trace timeline
    timeline = tracer.get_trace_timeline(trace_id)
    print(f"\nTrace Timeline for {trace_id}:")
    for span in timeline:
        duration = span.get('duration', 0)
        print(f"  {span['operation_name']}: {duration:.3f}s ({span['status']})")
    
    print(f"\n6. Alert Status")
    print("-" * 20)
    
    alert_summary = alert_manager.get_alert_summary()
    print(f"Active Alerts: {alert_summary['active_alerts']}")
    print(f"Alerts by Severity: {alert_summary['alerts_by_severity']}")
    print(f"Total Alert Rules: {alert_summary['total_alert_rules']}")
    
    if alert_manager.active_alerts:
        print("Current Active Alerts:")
        for alert in alert_manager.active_alerts.values():
            print(f"  - {alert.rule_name}: {alert.message} ({alert.severity.value})")
    
    print(f"\n7. Health Status")
    print("-" * 20)
    
    if health_monitor.current_health:
        health = health_monitor.current_health
        print(f"Overall Status: {health['overall_status']}")
        print(f"Health Checks:")
        for check_name, result in health['checks'].items():
            status = result.get('status', 'unknown')
            print(f"  - {check_name}: {status}")
            if result.get('issues'):
                for issue in result['issues']:
                    print(f"    ! {issue}")
    
    # Generate dashboard configuration
    print(f"\n8. Dashboard Generation")
    print("-" * 30)
    
    dashboard = MonitoringDashboard(metrics_collector, alert_manager, health_monitor)
    grafana_config = dashboard.generate_grafana_dashboard()
    
    print(f"Generated Grafana dashboard with {len(grafana_config['dashboard']['panels'])} panels:")
    for panel in grafana_config['dashboard']['panels']:
        print(f"  - {panel['title']} ({panel['type']})")
    
    # Cleanup
    await health_monitor.stop_monitoring()
    
    # Resolve the demo alert
    alert_manager.resolve_alert("HighErrorRate", {"service": "demo-agno", "severity": "critical"})
    
    print(f"\n" + "=" * 80)
    print("MONITORING SYSTEM DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Monitoring Capabilities Demonstrated:")
    print("- Comprehensive Prometheus metrics collection")
    print("- Distributed tracing for multi-agent workflows")
    print("- Intelligent alerting with severity levels")
    print("- System health monitoring with built-in checks")
    print("- Grafana dashboard generation")
    print("- Real-time metrics aggregation and analysis")
    print("- Alert correlation and management")

if __name__ == "__main__":
    # Run comprehensive demonstration
    asyncio.run(demonstrate_monitoring_system())