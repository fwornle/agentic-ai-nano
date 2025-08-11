# src/session5/monitoring_and_health.py
"""
Health monitoring and observability system for PydanticAI agents.
Includes health checks, metrics collection, alerting, and dashboard capabilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic, Tuple, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import time
import psutil
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
import uuid
import statistics
import socket
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class MetricType(str, Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Core monitoring models

class HealthCheckResult(BaseModel):
    """Result of a health check."""
    check_name: str = Field(..., description="Name of the health check")
    status: HealthStatus = Field(..., description="Health status")
    message: str = Field(..., description="Status message")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def is_healthy(self) -> bool:
        """Check if status indicates health."""
        return self.status == HealthStatus.HEALTHY

class Metric(BaseModel):
    """A monitoring metric."""
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    metric_type: MetricType = Field(..., description="Type of metric")
    unit: str = Field(..., description="Unit of measurement")
    tags: Dict[str, str] = Field(default_factory=dict, description="Metric tags")
    timestamp: datetime = Field(default_factory=datetime.now)

class Alert(BaseModel):
    """An alert notification."""
    alert_id: str = Field(..., description="Unique alert identifier")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    severity: AlertSeverity = Field(..., description="Alert severity")
    source: str = Field(..., description="Source of the alert")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional data")
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    
    def is_active(self) -> bool:
        """Check if alert is still active."""
        return self.resolved_at is None

class SystemMetrics(BaseModel):
    """System-level metrics."""
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    disk_percent: float = Field(..., description="Disk usage percentage")
    network_bytes_sent: int = Field(..., description="Network bytes sent")
    network_bytes_recv: int = Field(..., description="Network bytes received")
    process_count: int = Field(..., description="Number of processes")
    load_average: List[float] = Field(..., description="System load averages")
    timestamp: datetime = Field(default_factory=datetime.now)

# Abstract interfaces

class HealthCheck(ABC):
    """Abstract base class for health checks."""
    
    def __init__(self, name: str, timeout_seconds: float = 5.0):
        self.name = name
        self.timeout_seconds = timeout_seconds
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def check_health(self) -> HealthCheckResult:
        """Perform the health check."""
        pass

class AlertHandler(ABC):
    """Abstract base class for alert handlers."""
    
    @abstractmethod
    async def handle_alert(self, alert: Alert) -> bool:
        """Handle an alert notification."""
        pass

# Concrete health check implementations

class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity."""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__("database", **kwargs)
        self.connection_string = connection_string
    
    async def check_health(self) -> HealthCheckResult:
        """Check database health."""
        start_time = time.time()
        
        try:
            # Simulate database check
            await asyncio.sleep(0.01)  # Simulate connection time
            
            # In real implementation, would actually connect to database
            if "invalid" in self.connection_string:
                raise Exception("Invalid connection string")
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                response_time_ms=response_time,
                metadata={"connection_string": self.connection_string[:50] + "..."}
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=response_time,
                metadata={"error": str(e)}
            )

class ExternalServiceHealthCheck(HealthCheck):
    """Health check for external service dependencies."""
    
    def __init__(self, service_url: str, **kwargs):
        super().__init__("external_service", **kwargs)
        self.service_url = service_url
    
    async def check_health(self) -> HealthCheckResult:
        """Check external service health."""
        start_time = time.time()
        
        try:
            # Simulate HTTP request to external service
            await asyncio.sleep(0.02)  # Simulate network call
            
            # Simulate various response scenarios
            if "unreachable" in self.service_url:
                raise Exception("Service unreachable")
            elif "slow" in self.service_url:
                await asyncio.sleep(0.5)  # Simulate slow response
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on response time
            if response_time > 1000:
                status = HealthStatus.WARNING
                message = f"Service responding slowly ({response_time:.0f}ms)"
            else:
                status = HealthStatus.HEALTHY
                message = "Service responding normally"
            
            return HealthCheckResult(
                check_name=self.name,
                status=status,
                message=message,
                response_time_ms=response_time,
                metadata={"service_url": self.service_url}
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Service check failed: {str(e)}",
                response_time_ms=response_time,
                metadata={"service_url": self.service_url, "error": str(e)}
            )

class ResourceHealthCheck(HealthCheck):
    """Health check for system resources."""
    
    def __init__(self, **kwargs):
        super().__init__("resources", **kwargs)
    
    async def check_health(self) -> HealthCheckResult:
        """Check system resource health."""
        start_time = time.time()
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine overall status
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                issues.append(f"CPU usage critical: {cpu_percent:.1f}%")
            elif cpu_percent > 80:
                status = HealthStatus.WARNING
                issues.append(f"CPU usage high: {cpu_percent:.1f}%")
            
            if memory.percent > 90:
                status = HealthStatus.CRITICAL
                issues.append(f"Memory usage critical: {memory.percent:.1f}%")
            elif memory.percent > 80:
                status = HealthStatus.WARNING
                issues.append(f"Memory usage high: {memory.percent:.1f}%")
            
            if disk.percent > 95:
                status = HealthStatus.CRITICAL
                issues.append(f"Disk usage critical: {disk.percent:.1f}%")
            elif disk.percent > 90:
                status = HealthStatus.WARNING
                issues.append(f"Disk usage high: {disk.percent:.1f}%")
            
            if issues:
                message = "; ".join(issues)
            else:
                message = "System resources normal"
            
            return HealthCheckResult(
                check_name=self.name,
                status=status,
                message=message,
                response_time_ms=response_time,
                metadata={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent
                }
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"Resource check failed: {str(e)}",
                response_time_ms=response_time,
                metadata={"error": str(e)}
            )

# Alert handlers

class LogAlertHandler(AlertHandler):
    """Logs alerts to the logging system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".LogAlertHandler")
    
    async def handle_alert(self, alert: Alert) -> bool:
        """Log the alert."""
        try:
            log_level = {
                AlertSeverity.INFO: logging.INFO,
                AlertSeverity.WARNING: logging.WARNING,
                AlertSeverity.ERROR: logging.ERROR,
                AlertSeverity.CRITICAL: logging.CRITICAL
            }.get(alert.severity, logging.INFO)
            
            self.logger.log(
                log_level,
                f"ALERT [{alert.severity.upper()}] {alert.title}: {alert.message} "
                f"(source: {alert.source}, id: {alert.alert_id})"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to log alert: {str(e)}")
            return False

class EmailAlertHandler(AlertHandler):
    """Sends alerts via email (simulated)."""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = smtp_config
        self.logger = logging.getLogger(__name__ + ".EmailAlertHandler")
    
    async def handle_alert(self, alert: Alert) -> bool:
        """Send alert via email (simulated)."""
        try:
            # Simulate email sending
            await asyncio.sleep(0.1)
            
            self.logger.info(
                f"Email sent for alert {alert.alert_id}: {alert.title} "
                f"to {self.smtp_config.get('recipients', ['admin@example.com'])}"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
            return False

# Main monitoring system

class MonitoringSystem:
    """Comprehensive monitoring and health system."""
    
    def __init__(self, check_interval_seconds: int = 30):
        self.check_interval = check_interval_seconds
        self.health_checks: List[HealthCheck] = []
        self.alert_handlers: List[AlertHandler] = []
        self.metrics: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self.alerts: deque = deque(maxlen=1000)  # Keep last 1k alerts
        self.health_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(__name__ + ".MonitoringSystem")
    
    def add_health_check(self, health_check: HealthCheck) -> 'MonitoringSystem':
        """Add a health check to the system."""
        self.health_checks.append(health_check)
        return self
    
    def add_alert_handler(self, alert_handler: AlertHandler) -> 'MonitoringSystem':
        """Add an alert handler to the system."""
        self.alert_handlers.append(alert_handler)
        return self
    
    async def start_monitoring(self):
        """Start the monitoring loop."""
        if self.running:
            return
        
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Monitoring system started")
    
    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.running = False
        
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Monitoring system stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                await self._run_health_checks()
                await self._collect_system_metrics()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _run_health_checks(self):
        """Run all health checks."""
        if not self.health_checks:
            return
        
        # Run health checks concurrently
        tasks = [
            asyncio.create_task(self._run_single_health_check(check))
            for check in self.health_checks
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for check, result in zip(self.health_checks, results):
            if isinstance(result, Exception):
                self.logger.error(f"Health check {check.name} failed: {str(result)}")
            elif isinstance(result, HealthCheckResult):
                await self._process_health_result(result)
    
    async def _run_single_health_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Run a single health check with timeout."""
        try:
            return await asyncio.wait_for(
                health_check.check_health(),
                timeout=health_check.timeout_seconds
            )
        except asyncio.TimeoutError:
            return HealthCheckResult(
                check_name=health_check.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {health_check.timeout_seconds}s",
                response_time_ms=health_check.timeout_seconds * 1000
            )
    
    async def _process_health_result(self, result: HealthCheckResult):
        """Process health check result and trigger alerts if needed."""
        # Store in history
        self.health_history[result.check_name].append(result)
        
        # Check if we need to send alerts
        if not result.is_healthy():
            await self._create_alert(
                title=f"Health Check Failed: {result.check_name}",
                message=result.message,
                severity=self._map_health_to_alert_severity(result.status),
                source="health_check",
                metadata=result.dict()
            )
    
    def _map_health_to_alert_severity(self, health_status: HealthStatus) -> AlertSeverity:
        """Map health status to alert severity."""
        mapping = {
            HealthStatus.WARNING: AlertSeverity.WARNING,
            HealthStatus.UNHEALTHY: AlertSeverity.ERROR,
            HealthStatus.CRITICAL: AlertSeverity.CRITICAL,
            HealthStatus.UNKNOWN: AlertSeverity.WARNING
        }
        return mapping.get(health_status, AlertSeverity.INFO)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            await self._record_metric("system.cpu.percent", cpu_percent, MetricType.GAUGE, "percent")
            
            # Memory metrics
            memory = psutil.virtual_memory()
            await self._record_metric("system.memory.percent", memory.percent, MetricType.GAUGE, "percent")
            await self._record_metric("system.memory.available", memory.available, MetricType.GAUGE, "bytes")
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            await self._record_metric("system.disk.percent", disk.percent, MetricType.GAUGE, "percent")
            await self._record_metric("system.disk.free", disk.free, MetricType.GAUGE, "bytes")
            
            # Network metrics (if available)
            try:
                net_io = psutil.net_io_counters()
                await self._record_metric("system.network.bytes_sent", net_io.bytes_sent, MetricType.COUNTER, "bytes")
                await self._record_metric("system.network.bytes_recv", net_io.bytes_recv, MetricType.COUNTER, "bytes")
            except:
                pass  # Network metrics might not be available
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {str(e)}")
    
    async def _record_metric(self, name: str, value: float, metric_type: MetricType, unit: str, tags: Optional[Dict] = None):
        """Record a metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            unit=unit,
            tags=tags or {}
        )
        
        self.metrics.append(metric)
    
    async def _create_alert(self, title: str, message: str, severity: AlertSeverity, 
                          source: str, metadata: Optional[Dict] = None):
        """Create and dispatch an alert."""
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            title=title,
            message=message,
            severity=severity,
            source=source,
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        
        # Send to all alert handlers
        for handler in self.alert_handlers:
            try:
                await handler.handle_alert(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {str(e)}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary."""
        if not self.health_history:
            return {"status": "unknown", "checks": []}
        
        check_summaries = []
        overall_status = HealthStatus.HEALTHY
        
        for check_name, history in self.health_history.items():
            if not history:
                continue
            
            latest = history[-1]
            check_summaries.append({
                "name": check_name,
                "status": latest.status,
                "message": latest.message,
                "response_time_ms": latest.response_time_ms,
                "last_check": latest.timestamp
            })
            
            # Update overall status
            if latest.status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
            elif latest.status == HealthStatus.UNHEALTHY and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.UNHEALTHY
            elif latest.status == HealthStatus.WARNING and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.WARNING
        
        return {
            "status": overall_status,
            "checks": check_summaries,
            "total_checks": len(check_summaries),
            "last_updated": datetime.now()
        }
    
    def get_metrics_summary(self, time_window_minutes: int = 10) -> Dict[str, Any]:
        """Get metrics summary for the specified time window."""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        
        metrics_by_name = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_name[metric.name].append(metric.value)
        
        summary = {}
        for name, values in metrics_by_name.items():
            if values:
                summary[name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": statistics.mean(values),
                    "latest": values[-1]
                }
        
        return {
            "time_window_minutes": time_window_minutes,
            "metrics": summary,
            "total_metrics": len(recent_metrics)
        }

# Example usage and demonstrations

def demo_monitoring_system():
    """Demonstrate monitoring system usage."""
    print("\n=== Monitoring and Health System Demo ===")
    
    async def run_demo():
        # Create monitoring system
        monitor = MonitoringSystem(check_interval_seconds=5)
        
        # Add health checks
        monitor.add_health_check(DatabaseHealthCheck("postgresql://localhost/mydb"))
        monitor.add_health_check(ExternalServiceHealthCheck("https://api.example.com"))
        monitor.add_health_check(ResourceHealthCheck())
        
        # Add alert handlers
        monitor.add_alert_handler(LogAlertHandler())
        
        # Start monitoring
        await monitor.start_monitoring()
        
        print("Monitoring system started. Running for 15 seconds...")
        
        # Let it run for a bit
        await asyncio.sleep(15)
        
        # Get health summary
        print("\nHealth Summary:")
        health_summary = monitor.get_health_summary()
        print(json.dumps(health_summary, indent=2, default=str))
        
        # Get metrics summary
        print("\nMetrics Summary:")
        metrics_summary = monitor.get_metrics_summary(time_window_minutes=1)
        print(json.dumps(metrics_summary, indent=2))
        
        # Stop monitoring
        await monitor.stop_monitoring()
        print("\nMonitoring system stopped.")
    
    # Run the async demo
    asyncio.run(run_demo())

if __name__ == "__main__":
    demo_monitoring_system()