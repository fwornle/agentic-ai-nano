"""
Enterprise Monitoring and Observability System
Comprehensive monitoring for production agent systems.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
import time
import psutil
import threading
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"      # Monotonically increasing values
    GAUGE = "gauge"          # Snapshot values that can go up or down
    HISTOGRAM = "histogram"  # Distribution of values with buckets
    SUMMARY = "summary"      # Distribution with quantiles

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    """Individual metric definition."""
    name: str
    type: MetricType
    value: Union[float, int]
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    unit: str = ""

@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: bool
    message: str = ""
    response_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    """Collects and stores metrics with time-series data."""
    
    def __init__(self, retention_hours: int = 24, max_metrics_per_key: int = 10000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque())
        self.retention_hours = retention_hours
        self.retention_seconds = retention_hours * 3600
        self.max_metrics_per_key = max_metrics_per_key
        self._lock = threading.Lock()
        self._cleanup_counter = 0
        self._cleanup_interval = 100  # Clean up every 100 metric insertions
        
    def record_metric(self, metric: Metric) -> None:
        """Record a metric value with memory management."""
        with self._lock:
            key = f"{metric.name}:{json.dumps(metric.labels, sort_keys=True)}"
            metrics_deque = self.metrics[key]
            
            # Add the new metric
            metrics_deque.append(metric)
            
            # Enforce size limit to prevent unbounded growth
            if len(metrics_deque) > self.max_metrics_per_key:
                metrics_deque.popleft()
            
            # Periodic cleanup based on time retention
            self._cleanup_counter += 1
            if self._cleanup_counter >= self._cleanup_interval:
                self._cleanup_old_metrics()
                self._cleanup_counter = 0
    
    def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics across all keys."""
        cutoff_time = datetime.now() - timedelta(seconds=self.retention_seconds)
        
        # Clean up metrics in all keys
        keys_to_remove = []
        for key, metrics_deque in self.metrics.items():
            # Remove old metrics from the front of the deque
            while metrics_deque and metrics_deque[0].timestamp < cutoff_time:
                metrics_deque.popleft()
            
            # If deque is empty, mark key for removal
            if not metrics_deque:
                keys_to_remove.append(key)
        
        # Remove empty keys to free memory
        for key in keys_to_remove:
            del self.metrics[key]
    
    def get_metric_history(self, metric_name: str, 
                          labels: Dict[str, str] = None,
                          hours: int = 1) -> List[Metric]:
        """Get metric history for the specified time range."""
        with self._lock:
            key = f"{metric_name}:{json.dumps(labels or {}, sort_keys=True)}"
            
            if key not in self.metrics:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [m for m in self.metrics[key] if m.timestamp >= cutoff_time]
    
    def get_current_value(self, metric_name: str, 
                         labels: Dict[str, str] = None) -> Optional[float]:
        """Get the most recent value for a metric."""
        history = self.get_metric_history(metric_name, labels, hours=24)
        return history[-1].value if history else None
    
    def calculate_aggregates(self, metric_name: str,
                           labels: Dict[str, str] = None,
                           hours: int = 1) -> Dict[str, float]:
        """Calculate aggregate statistics for a metric."""
        history = self.get_metric_history(metric_name, labels, hours)
        
        if not history:
            return {}
        
        values = [m.value for m in history]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
            "latest": values[-1] if values else 0
        }

class SystemMetricsCollector:
    """Collects system-level metrics (CPU, memory, disk, network)."""
    
    def __init__(self):
        self.process = psutil.Process()
        
    def collect_system_metrics(self) -> List[Metric]:
        """Collect comprehensive system metrics."""
        metrics = []
        now = datetime.now()
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics.append(Metric(
                name="system_cpu_usage_percent",
                type=MetricType.GAUGE,
                value=cpu_percent,
                timestamp=now,
                description="System CPU usage percentage",
                unit="percent"
            ))
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.extend([
                Metric(
                    name="system_memory_usage_bytes",
                    type=MetricType.GAUGE,
                    value=memory.used,
                    timestamp=now,
                    description="System memory usage in bytes",
                    unit="bytes"
                ),
                Metric(
                    name="system_memory_usage_percent",
                    type=MetricType.GAUGE,
                    value=memory.percent,
                    timestamp=now,
                    description="System memory usage percentage",
                    unit="percent"
                ),
                Metric(
                    name="system_memory_available_bytes",
                    type=MetricType.GAUGE,
                    value=memory.available,
                    timestamp=now,
                    description="System memory available in bytes",
                    unit="bytes"
                )
            ])
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            metrics.extend([
                Metric(
                    name="system_disk_usage_bytes",
                    type=MetricType.GAUGE,
                    value=disk_usage.used,
                    timestamp=now,
                    description="System disk usage in bytes",
                    unit="bytes"
                ),
                Metric(
                    name="system_disk_usage_percent",
                    type=MetricType.GAUGE,
                    value=(disk_usage.used / disk_usage.total) * 100,
                    timestamp=now,
                    description="System disk usage percentage",
                    unit="percent"
                )
            ])
            
            # Process-specific metrics
            process_memory = self.process.memory_info()
            metrics.extend([
                Metric(
                    name="process_memory_rss_bytes",
                    type=MetricType.GAUGE,
                    value=process_memory.rss,
                    timestamp=now,
                    description="Process resident set size",
                    unit="bytes"
                ),
                Metric(
                    name="process_cpu_percent",
                    type=MetricType.GAUGE,
                    value=self.process.cpu_percent(),
                    timestamp=now,
                    description="Process CPU usage percentage",
                    unit="percent"
                )
            ])
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
        
        return metrics

class ApplicationMetricsCollector:
    """Collects application-specific metrics."""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.active_connections = 0
        
    def record_request(self, endpoint: str, method: str, 
                      status_code: int, response_time: float) -> None:
        """Record an HTTP request metric."""
        labels = {
            "endpoint": endpoint,
            "method": method,
            "status": str(status_code)
        }
        
        key = json.dumps(labels, sort_keys=True)
        self.request_counts[key] += 1
        self.response_times[key].append(response_time)
        
        if status_code >= 400:
            self.error_counts[key] += 1
    
    def get_application_metrics(self) -> List[Metric]:
        """Get current application metrics."""
        metrics = []
        now = datetime.now()
        
        # Request count metrics
        for key, count in self.request_counts.items():
            labels = json.loads(key)
            metrics.append(Metric(
                name="http_requests_total",
                type=MetricType.COUNTER,
                value=count,
                labels=labels,
                timestamp=now,
                description="Total HTTP requests"
            ))
        
        # Response time metrics
        for key, times in self.response_times.items():
            if times:
                labels = json.loads(key)
                metrics.extend([
                    Metric(
                        name="http_request_duration_avg",
                        type=MetricType.GAUGE,
                        value=sum(times) / len(times),
                        labels=labels,
                        timestamp=now,
                        description="Average HTTP request duration",
                        unit="seconds"
                    ),
                    Metric(
                        name="http_request_duration_max",
                        type=MetricType.GAUGE,
                        value=max(times),
                        labels=labels,
                        timestamp=now,
                        description="Maximum HTTP request duration",
                        unit="seconds"
                    )
                ])
        
        # Error rate metrics
        for key, errors in self.error_counts.items():
            if errors > 0:
                labels = json.loads(key)
                total_requests = self.request_counts[key]
                error_rate = (errors / total_requests) * 100
                
                metrics.append(Metric(
                    name="http_error_rate_percent",
                    type=MetricType.GAUGE,
                    value=error_rate,
                    labels=labels,
                    timestamp=now,
                    description="HTTP error rate percentage",
                    unit="percent"
                ))
        
        # Connection metrics
        metrics.append(Metric(
            name="active_connections",
            type=MetricType.GAUGE,
            value=self.active_connections,
            timestamp=now,
            description="Number of active connections"
        ))
        
        return metrics

class HealthCheckManager:
    """Manages health checks for various system components."""
    
    def __init__(self):
        self.health_checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, HealthCheck] = {}
        
    def register_health_check(self, name: str, 
                            check_function: Callable[[], bool],
                            description: str = "") -> None:
        """Register a health check function."""
        self.health_checks[name] = {
            "function": check_function,
            "description": description
        }
        logger.info(f"Registered health check: {name}")
    
    async def run_health_check(self, name: str) -> HealthCheck:
        """Run a specific health check."""
        if name not in self.health_checks:
            return HealthCheck(
                name=name,
                status=False,
                message=f"Health check '{name}' not found"
            )
        
        start_time = time.time()
        
        try:
            check_info = self.health_checks[name]
            check_function = check_info["function"]
            
            # Run the health check
            if asyncio.iscoroutinefunction(check_function):
                result = await check_function()
            else:
                result = check_function()
            
            response_time = time.time() - start_time
            
            health_check = HealthCheck(
                name=name,
                status=bool(result),
                message="Health check passed" if result else "Health check failed",
                response_time=response_time,
                metadata={"description": check_info["description"]}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            health_check = HealthCheck(
                name=name,
                status=False,
                message=f"Health check error: {str(e)}",
                response_time=response_time
            )
            logger.error(f"Health check '{name}' failed: {e}")
        
        self.last_results[name] = health_check
        return health_check
    
    async def run_all_health_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks."""
        results = {}
        
        tasks = []
        for name in self.health_checks.keys():
            tasks.append(self.run_health_check(name))
        
        health_checks = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, name in enumerate(self.health_checks.keys()):
            if isinstance(health_checks[i], Exception):
                results[name] = HealthCheck(
                    name=name,
                    status=False,
                    message=f"Health check exception: {str(health_checks[i])}"
                )
            else:
                results[name] = health_checks[i]
        
        return results
    
    def get_overall_health(self) -> bool:
        """Get overall system health status."""
        if not self.last_results:
            return False
        
        return all(check.status for check in self.last_results.values())

class EnterpriseMonitoring:
    """Comprehensive monitoring and observability system."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_collector = MetricsCollector(
            retention_hours=self.config.get("retention_hours", 24)
        )
        self.system_collector = SystemMetricsCollector()
        self.app_collector = ApplicationMetricsCollector()
        self.health_manager = HealthCheckManager()
        
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.notification_handlers: List[Callable] = []
        
        self._monitoring_active = False
        self._monitoring_task = None
        
        # Register default health checks
        self._register_default_health_checks()
    
    def _register_default_health_checks(self) -> None:
        """Register default system health checks."""
        
        def check_memory():
            memory = psutil.virtual_memory()
            return memory.percent < 90  # Alert if memory usage > 90%
        
        def check_disk():
            disk = psutil.disk_usage('/')
            usage_percent = (disk.used / disk.total) * 100
            return usage_percent < 85  # Alert if disk usage > 85%
        
        def check_cpu():
            cpu_percent = psutil.cpu_percent(interval=1)
            return cpu_percent < 80  # Alert if CPU usage > 80%
        
        self.health_manager.register_health_check(
            "memory_usage", check_memory, "System memory usage check"
        )
        self.health_manager.register_health_check(
            "disk_usage", check_disk, "System disk usage check"
        )
        self.health_manager.register_health_check(
            "cpu_usage", check_cpu, "System CPU usage check"
        )
    
    async def start_monitoring(self, interval_seconds: int = 30) -> None:
        """Start continuous monitoring."""
        if self._monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )
        logger.info(f"Started monitoring with {interval_seconds}s interval")
    
    async def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        self._monitoring_active = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped monitoring")
    
    async def _monitoring_loop(self, interval_seconds: int) -> None:
        """Main monitoring loop with comprehensive error handling."""
        consecutive_errors = 0
        max_consecutive_errors = 5
        error_backoff_multiplier = 1.5
        
        while self._monitoring_active:
            try:
                # Collect system metrics with error handling
                try:
                    system_metrics = self.system_collector.collect_system_metrics()
                    for metric in system_metrics:
                        self.metrics_collector.record_metric(metric)
                except Exception as e:
                    logger.warning(f"Failed to collect system metrics: {e}")
                
                # Collect application metrics with error handling
                try:
                    app_metrics = self.app_collector.get_application_metrics()
                    for metric in app_metrics:
                        self.metrics_collector.record_metric(metric)
                except Exception as e:
                    logger.warning(f"Failed to collect application metrics: {e}")
                
                # Run health checks with error handling
                try:
                    health_results = await self.health_manager.run_all_health_checks()
                except Exception as e:
                    logger.warning(f"Failed to run health checks: {e}")
                    health_results = {}
                
                # Check alert conditions with error handling
                try:
                    await self._evaluate_alerts(health_results)
                except Exception as e:
                    logger.warning(f"Failed to evaluate alerts: {e}")
                
                # Reset error counter on successful iteration
                consecutive_errors = 0
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                consecutive_errors += 1
                error_msg = f"Critical error in monitoring loop (attempt {consecutive_errors}): {e}"
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical(f"{error_msg} - Stopping monitoring due to too many consecutive errors")
                    self._monitoring_active = False
                    break
                else:
                    logger.error(error_msg)
                    
                    # Exponential backoff for error recovery
                    error_sleep = interval_seconds * (error_backoff_multiplier ** consecutive_errors)
                    await asyncio.sleep(min(error_sleep, 300))  # Cap at 5 minutes
    
    async def _evaluate_alerts(self, health_results: Dict[str, HealthCheck]) -> None:
        """Evaluate alert conditions and trigger notifications."""
        # Check health-based alerts
        for name, health_check in health_results.items():
            if not health_check.status:
                alert_id = f"health_{name}"
                if alert_id not in self.active_alerts:
                    alert = {
                        "id": alert_id,
                        "type": "health_check_failure",
                        "severity": AlertSeverity.ERROR,
                        "message": f"Health check failed: {health_check.message}",
                        "timestamp": datetime.now(),
                        "source": name
                    }
                    self.active_alerts[alert_id] = alert
                    await self._send_alert_notifications(alert)
        
        # Check metric-based alerts (simplified example)
        cpu_usage = self.metrics_collector.get_current_value("system_cpu_usage_percent")
        if cpu_usage and cpu_usage > 90:
            alert_id = "high_cpu_usage"
            if alert_id not in self.active_alerts:
                alert = {
                    "id": alert_id,
                    "type": "high_resource_usage",
                    "severity": AlertSeverity.CRITICAL,
                    "message": f"High CPU usage detected: {cpu_usage:.1f}%",
                    "timestamp": datetime.now(),
                    "source": "system_monitor"
                }
                self.active_alerts[alert_id] = alert
                await self._send_alert_notifications(alert)
    
    async def _send_alert_notifications(self, alert: Dict[str, Any]) -> None:
        """Send alert notifications to registered handlers."""
        for handler in self.notification_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error sending alert notification: {e}")
    
    def add_notification_handler(self, handler: Callable) -> None:
        """Add a notification handler for alerts."""
        self.notification_handlers.append(handler)
        logger.info("Added notification handler")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        # Get latest health check results
        health_status = {
            name: check.status 
            for name, check in self.health_manager.last_results.items()
        }
        
        # Get key metrics
        key_metrics = {}
        for metric_name in ["system_cpu_usage_percent", "system_memory_usage_percent", 
                          "system_disk_usage_percent"]:
            value = self.metrics_collector.get_current_value(metric_name)
            if value is not None:
                key_metrics[metric_name] = value
        
        return {
            "overall_healthy": self.health_manager.get_overall_health(),
            "health_checks": health_status,
            "key_metrics": key_metrics,
            "active_alerts": len(self.active_alerts),
            "monitoring_active": self._monitoring_active,
            "timestamp": datetime.now().isoformat()
        }

# Example usage and demo
async def demo_enterprise_monitoring():
    """Demonstrate enterprise monitoring capabilities."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    import asyncio
    
    console = Console()
    
    console.print(Panel.fit(
        "📊 Enterprise Monitoring System Demo\n"
        "Real-time system monitoring and alerting",
        title="Observability Platform",
        border_style="blue"
    ))
    
    # Create monitoring system
    monitoring = EnterpriseMonitoring({
        "retention_hours": 1  # Short retention for demo
    })
    
    # Add notification handler
    def alert_handler(alert):
        severity_emoji = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️", 
            AlertSeverity.ERROR: "🚨",
            AlertSeverity.CRITICAL: "🔥"
        }
        emoji = severity_emoji.get(alert["severity"], "📢")
        console.print(f"{emoji} ALERT: {alert['message']}")
    
    monitoring.add_notification_handler(alert_handler)
    
    # Simulate some application metrics
    app_collector = monitoring.app_collector
    app_collector.record_request("/api/health", "GET", 200, 0.05)
    app_collector.record_request("/api/users", "GET", 200, 0.12)
    app_collector.record_request("/api/users", "POST", 201, 0.08)
    app_collector.record_request("/api/data", "GET", 500, 0.25)  # Error for demo
    app_collector.active_connections = 15
    
    # Start monitoring
    await monitoring.start_monitoring(interval_seconds=5)
    
    # Run demo for 30 seconds
    console.print("\n🔍 Starting real-time monitoring (30 seconds)...")
    
    try:
        for i in range(6):  # 6 iterations of 5 seconds each
            await asyncio.sleep(5)
            
            # Get current status
            status = monitoring.get_system_status()
            
            # Create status table
            status_table = Table(title=f"System Status - Update {i+1}")
            status_table.add_column("Component", style="cyan")
            status_table.add_column("Status", style="green")
            status_table.add_column("Value", style="yellow")
            
            # Health checks
            for name, healthy in status["health_checks"].items():
                status_icon = "🟢" if healthy else "🔴"
                status_table.add_row(
                    f"Health: {name}",
                    status_icon,
                    "Healthy" if healthy else "Unhealthy"
                )
            
            # Key metrics
            for name, value in status["key_metrics"].items():
                metric_name = name.replace("system_", "").replace("_", " ").title()
                if "percent" in name:
                    status_table.add_row(
                        metric_name,
                        "📊",
                        f"{value:.1f}%"
                    )
            
            # Overall status
            overall_icon = "🟢" if status["overall_healthy"] else "🔴"
            status_table.add_row(
                "Overall Status",
                overall_icon,
                "Healthy" if status["overall_healthy"] else "Unhealthy"
            )
            
            console.print(status_table)
            console.print(f"Active Alerts: {status['active_alerts']}")
            console.print("---")
    
    finally:
        await monitoring.stop_monitoring()
    
    console.print("✅ Monitoring demo completed")

if __name__ == "__main__":
    asyncio.run(demo_enterprise_monitoring())