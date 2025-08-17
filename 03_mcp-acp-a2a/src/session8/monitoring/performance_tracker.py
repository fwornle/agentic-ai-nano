"""
Performance Tracking System - Session 8
Advanced monitoring and performance analysis for workflow systems.
"""

import asyncio
import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics."""
    COUNTER = "counter"           # Monotonically increasing values
    GAUGE = "gauge"               # Current value at a point in time
    HISTOGRAM = "histogram"       # Distribution of values
    TIMER = "timer"              # Execution time measurements
    RATE = "rate"                # Rate of change over time


@dataclass
class MetricPoint:
    """Single metric measurement point."""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert configuration and state."""
    id: str
    name: str
    metric_name: str
    condition: str               # e.g., "value > 100", "avg_5m > 50"
    threshold: float
    enabled: bool = True
    alert_count: int = 0
    last_triggered: Optional[datetime] = None
    cooldown_seconds: int = 300  # 5 minutes default cooldown


class MetricCollector:
    """Collects and stores performance metrics."""
    
    def __init__(self, max_points_per_metric: int = 10000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points_per_metric))
        self.metric_types: Dict[str, MetricType] = {}
        self.lock = threading.RLock()
        self.collection_start_time = datetime.now()
    
    def register_metric(self, name: str, metric_type: MetricType, description: str = ""):
        """Register a new metric."""
        with self.lock:
            self.metric_types[name] = metric_type
            logger.info(f"Registered metric '{name}' of type {metric_type.value}")
    
    def record_metric(self, name: str, value: float, 
                     labels: Dict[str, str] = None,
                     metadata: Dict[str, Any] = None):
        """Record a metric value."""
        with self.lock:
            if name not in self.metric_types:
                # Auto-register as gauge
                self.register_metric(name, MetricType.GAUGE, "Auto-registered metric")
            
            point = MetricPoint(
                timestamp=datetime.now(),
                value=value,
                labels=labels or {},
                metadata=metadata or {}
            )
            
            self.metrics[name].append(point)
    
    def increment_counter(self, name: str, amount: float = 1.0,
                         labels: Dict[str, str] = None):
        """Increment a counter metric."""
        if name not in self.metric_types:
            self.register_metric(name, MetricType.COUNTER)
        
        # For counters, we add to the last value or start from 0
        with self.lock:
            last_value = 0.0
            if self.metrics[name]:
                last_value = self.metrics[name][-1].value
            
            self.record_metric(name, last_value + amount, labels)
    
    def set_gauge(self, name: str, value: float,
                  labels: Dict[str, str] = None):
        """Set a gauge metric value."""
        if name not in self.metric_types:
            self.register_metric(name, MetricType.GAUGE)
        
        self.record_metric(name, value, labels)
    
    def record_timer(self, name: str, duration_seconds: float,
                    labels: Dict[str, str] = None):
        """Record a timing measurement."""
        if name not in self.metric_types:
            self.register_metric(name, MetricType.TIMER)
        
        self.record_metric(name, duration_seconds, labels, {"unit": "seconds"})
    
    def get_metric_values(self, name: str, 
                         time_range: Optional[timedelta] = None) -> List[MetricPoint]:
        """Get metric values, optionally filtered by time range."""
        with self.lock:
            if name not in self.metrics:
                return []
            
            points = list(self.metrics[name])
            
            if time_range:
                cutoff_time = datetime.now() - time_range
                points = [p for p in points if p.timestamp >= cutoff_time]
            
            return points
    
    def get_metric_summary(self, name: str, 
                          time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get statistical summary of a metric."""
        points = self.get_metric_values(name, time_range)
        
        if not points:
            return {"error": f"No data for metric '{name}'"}
        
        values = [p.value for p in points]
        
        return {
            "metric_name": name,
            "metric_type": self.metric_types.get(name, MetricType.GAUGE).value,
            "data_points": len(values),
            "time_range": {
                "start": points[0].timestamp.isoformat(),
                "end": points[-1].timestamp.isoformat(),
                "duration_seconds": (points[-1].timestamp - points[0].timestamp).total_seconds()
            },
            "statistics": {
                "current": values[-1],
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "median": sorted(values)[len(values) // 2] if values else 0,
                "first": values[0],
                "last": values[-1]
            }
        }


class SystemMonitor:
    """Monitors system-level performance metrics."""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.monitor_interval = 5.0  # seconds
    
    def start_monitoring(self):
        """Start system monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Started system monitoring")
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        if self.monitoring_active:
            self.monitoring_active = False
            if self.monitor_task:
                self.monitor_task.cancel()
            logger.info("Stopped system monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.monitor_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system monitoring: {str(e)}")
                await asyncio.sleep(self.monitor_interval)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        self.collector.set_gauge("system.cpu.usage_percent", cpu_percent)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.collector.set_gauge("system.memory.usage_percent", memory.percent)
        self.collector.set_gauge("system.memory.available_bytes", memory.available)
        self.collector.set_gauge("system.memory.used_bytes", memory.used)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.collector.set_gauge("system.disk.usage_percent", 
                               (disk.used / disk.total) * 100)
        self.collector.set_gauge("system.disk.free_bytes", disk.free)
        
        # Process metrics
        process = psutil.Process()
        self.collector.set_gauge("process.cpu.usage_percent", process.cpu_percent())
        self.collector.set_gauge("process.memory.rss_bytes", process.memory_info().rss)
        self.collector.set_gauge("process.memory.vms_bytes", process.memory_info().vms)
        self.collector.set_gauge("process.threads.count", process.num_threads())


class WorkflowPerformanceTracker:
    """Tracks performance metrics specifically for workflows."""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.active_steps: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
    
    def start_workflow_tracking(self, workflow_id: str, execution_id: str,
                               workflow_name: str = "", step_count: int = 0):
        """Start tracking a workflow execution."""
        with self.lock:
            tracking_key = f"{workflow_id}:{execution_id}"
            
            self.active_workflows[tracking_key] = {
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "workflow_name": workflow_name,
                "start_time": time.time(),
                "step_count": step_count,
                "completed_steps": 0,
                "failed_steps": 0
            }
            
            self.collector.increment_counter("workflow.started.total",
                                           labels={"workflow_name": workflow_name})
    
    def start_step_tracking(self, workflow_id: str, execution_id: str,
                           step_id: str, step_name: str = ""):
        """Start tracking a workflow step."""
        with self.lock:
            tracking_key = f"{workflow_id}:{execution_id}:{step_id}"
            
            self.active_steps[tracking_key] = {
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "step_id": step_id,
                "step_name": step_name,
                "start_time": time.time()
            }
            
            self.collector.increment_counter("workflow.step.started.total",
                                           labels={
                                               "workflow_id": workflow_id,
                                               "step_name": step_name
                                           })
    
    def complete_step_tracking(self, workflow_id: str, execution_id: str,
                              step_id: str, success: bool = True,
                              error_message: str = ""):
        """Complete tracking for a workflow step."""
        with self.lock:
            tracking_key = f"{workflow_id}:{execution_id}:{step_id}"
            workflow_key = f"{workflow_id}:{execution_id}"
            
            if tracking_key in self.active_steps:
                step_info = self.active_steps[tracking_key]
                duration = time.time() - step_info["start_time"]
                
                # Record step timing
                self.collector.record_timer(
                    "workflow.step.duration.seconds",
                    duration,
                    labels={
                        "workflow_id": workflow_id,
                        "step_name": step_info["step_name"],
                        "success": str(success)
                    }
                )
                
                # Record step completion
                if success:
                    self.collector.increment_counter(
                        "workflow.step.completed.total",
                        labels={
                            "workflow_id": workflow_id,
                            "step_name": step_info["step_name"]
                        }
                    )
                    
                    # Update workflow tracking
                    if workflow_key in self.active_workflows:
                        self.active_workflows[workflow_key]["completed_steps"] += 1
                else:
                    self.collector.increment_counter(
                        "workflow.step.failed.total",
                        labels={
                            "workflow_id": workflow_id,
                            "step_name": step_info["step_name"],
                            "error": error_message[:100]  # Truncate long error messages
                        }
                    )
                    
                    # Update workflow tracking
                    if workflow_key in self.active_workflows:
                        self.active_workflows[workflow_key]["failed_steps"] += 1
                
                del self.active_steps[tracking_key]
    
    def complete_workflow_tracking(self, workflow_id: str, execution_id: str,
                                  success: bool = True, error_message: str = ""):
        """Complete tracking for a workflow execution."""
        with self.lock:
            tracking_key = f"{workflow_id}:{execution_id}"
            
            if tracking_key in self.active_workflows:
                workflow_info = self.active_workflows[tracking_key]
                duration = time.time() - workflow_info["start_time"]
                
                # Record workflow timing
                self.collector.record_timer(
                    "workflow.execution.duration.seconds",
                    duration,
                    labels={
                        "workflow_id": workflow_id,
                        "workflow_name": workflow_info["workflow_name"],
                        "success": str(success)
                    }
                )
                
                # Record workflow completion
                if success:
                    self.collector.increment_counter(
                        "workflow.completed.total",
                        labels={"workflow_name": workflow_info["workflow_name"]}
                    )
                else:
                    self.collector.increment_counter(
                        "workflow.failed.total",
                        labels={
                            "workflow_name": workflow_info["workflow_name"],
                            "error": error_message[:100]
                        }
                    )
                
                # Record step statistics
                self.collector.set_gauge(
                    "workflow.steps.completed",
                    workflow_info["completed_steps"],
                    labels={"execution_id": execution_id}
                )
                
                self.collector.set_gauge(
                    "workflow.steps.failed",
                    workflow_info["failed_steps"],
                    labels={"execution_id": execution_id}
                )
                
                del self.active_workflows[tracking_key]
    
    def get_active_workflows_count(self) -> int:
        """Get number of currently active workflows."""
        with self.lock:
            return len(self.active_workflows)
    
    def get_active_steps_count(self) -> int:
        """Get number of currently active steps."""
        with self.lock:
            return len(self.active_steps)


class AlertManager:
    """Manages performance alerts and notifications."""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.alert_handlers: List[Callable[[PerformanceAlert, float], None]] = []
        self.checking_active = False
        self.check_task: Optional[asyncio.Task] = None
        self.check_interval = 30.0  # seconds
    
    def add_alert(self, alert: PerformanceAlert):
        """Add a performance alert."""
        self.alerts[alert.id] = alert
        logger.info(f"Added alert '{alert.name}' for metric '{alert.metric_name}'")
    
    def remove_alert(self, alert_id: str) -> bool:
        """Remove a performance alert."""
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            logger.info(f"Removed alert '{alert_id}'")
            return True
        return False
    
    def add_alert_handler(self, handler: Callable[[PerformanceAlert, float], None]):
        """Add an alert handler function."""
        self.alert_handlers.append(handler)
    
    def start_alert_checking(self):
        """Start checking alerts."""
        if not self.checking_active:
            self.checking_active = True
            self.check_task = asyncio.create_task(self._alert_checking_loop())
            logger.info("Started alert checking")
    
    def stop_alert_checking(self):
        """Stop checking alerts."""
        if self.checking_active:
            self.checking_active = False
            if self.check_task:
                self.check_task.cancel()
            logger.info("Stopped alert checking")
    
    async def _alert_checking_loop(self):
        """Main alert checking loop."""
        while self.checking_active:
            try:
                await self._check_all_alerts()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert checking: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_all_alerts(self):
        """Check all configured alerts."""
        for alert in self.alerts.values():
            if not alert.enabled:
                continue
            
            # Check cooldown
            if (alert.last_triggered and 
                datetime.now() - alert.last_triggered < timedelta(seconds=alert.cooldown_seconds)):
                continue
            
            # Get metric data
            metric_summary = self.collector.get_metric_summary(
                alert.metric_name,
                timedelta(minutes=5)  # Look at last 5 minutes
            )
            
            if "error" in metric_summary:
                continue
            
            # Evaluate condition
            triggered, current_value = self._evaluate_alert_condition(alert, metric_summary)
            
            if triggered:
                alert.last_triggered = datetime.now()
                alert.alert_count += 1
                
                logger.warning(f"Alert triggered: {alert.name} - "
                             f"Current value: {current_value}, Threshold: {alert.threshold}")
                
                # Call alert handlers
                for handler in self.alert_handlers:
                    try:
                        handler(alert, current_value)
                    except Exception as e:
                        logger.error(f"Alert handler failed: {str(e)}")
    
    def _evaluate_alert_condition(self, alert: PerformanceAlert, 
                                 metric_summary: Dict[str, Any]) -> tuple[bool, float]:
        """Evaluate if an alert condition is met."""
        stats = metric_summary.get("statistics", {})
        
        # Simple condition parsing (in real implementation, use proper expression parser)
        condition = alert.condition.lower()
        current_value = stats.get("current", 0)
        
        if "avg" in condition:
            current_value = stats.get("avg", 0)
        elif "max" in condition:
            current_value = stats.get("max", 0)
        elif "min" in condition:
            current_value = stats.get("min", 0)
        
        if ">" in condition:
            return current_value > alert.threshold, current_value
        elif "<" in condition:
            return current_value < alert.threshold, current_value
        elif "=" in condition:
            return abs(current_value - alert.threshold) < 0.01, current_value
        
        return False, current_value


class PerformanceReporter:
    """Generates performance reports and dashboards."""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
    
    def generate_workflow_report(self, time_range: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Generate a comprehensive workflow performance report."""
        report = {
            "report_generated": datetime.now().isoformat(),
            "time_range_hours": time_range.total_seconds() / 3600,
            "workflow_metrics": {},
            "system_metrics": {},
            "performance_summary": {}
        }
        
        # Workflow metrics
        workflow_metrics = [
            "workflow.started.total",
            "workflow.completed.total", 
            "workflow.failed.total",
            "workflow.execution.duration.seconds",
            "workflow.step.duration.seconds"
        ]
        
        for metric_name in workflow_metrics:
            summary = self.collector.get_metric_summary(metric_name, time_range)
            if "error" not in summary:
                report["workflow_metrics"][metric_name] = summary
        
        # System metrics
        system_metrics = [
            "system.cpu.usage_percent",
            "system.memory.usage_percent",
            "system.disk.usage_percent",
            "process.cpu.usage_percent",
            "process.memory.rss_bytes"
        ]
        
        for metric_name in system_metrics:
            summary = self.collector.get_metric_summary(metric_name, time_range)
            if "error" not in summary:
                report["system_metrics"][metric_name] = summary
        
        # Performance summary
        report["performance_summary"] = self._calculate_performance_summary(report)
        
        return report
    
    def _calculate_performance_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate high-level performance summary."""
        summary = {
            "workflow_success_rate": 0.0,
            "average_execution_time": 0.0,
            "system_health_score": 0.0,
            "recommendations": []
        }
        
        # Calculate success rate
        started = report["workflow_metrics"].get("workflow.started.total", {})
        completed = report["workflow_metrics"].get("workflow.completed.total", {})
        failed = report["workflow_metrics"].get("workflow.failed.total", {})
        
        if started and "statistics" in started:
            total_started = started["statistics"].get("current", 0)
            total_completed = completed.get("statistics", {}).get("current", 0) if completed else 0
            
            if total_started > 0:
                summary["workflow_success_rate"] = (total_completed / total_started) * 100
        
        # Calculate average execution time
        execution_time = report["workflow_metrics"].get("workflow.execution.duration.seconds", {})
        if execution_time and "statistics" in execution_time:
            summary["average_execution_time"] = execution_time["statistics"].get("avg", 0)
        
        # Calculate system health score (simplified)
        cpu_usage = report["system_metrics"].get("system.cpu.usage_percent", {})
        memory_usage = report["system_metrics"].get("system.memory.usage_percent", {})
        
        if cpu_usage and memory_usage:
            cpu_avg = cpu_usage.get("statistics", {}).get("avg", 0)
            mem_avg = memory_usage.get("statistics", {}).get("avg", 0)
            
            # Simple health score calculation
            health_score = 100 - (cpu_avg * 0.5 + mem_avg * 0.5)
            summary["system_health_score"] = max(0, health_score)
        
        # Generate recommendations
        if summary["workflow_success_rate"] < 95:
            summary["recommendations"].append("Low workflow success rate - investigate failed workflows")
        
        if summary["average_execution_time"] > 300:  # 5 minutes
            summary["recommendations"].append("Long average execution times - consider optimization")
        
        if summary["system_health_score"] < 70:
            summary["recommendations"].append("System resource usage is high - consider scaling")
        
        return summary


# Example alert handler
def console_alert_handler(alert: PerformanceAlert, current_value: float):
    """Simple console alert handler."""
    print(f"🚨 ALERT: {alert.name}")
    print(f"   Metric: {alert.metric_name}")
    print(f"   Current Value: {current_value}")
    print(f"   Threshold: {alert.threshold}")
    print(f"   Condition: {alert.condition}")
    print(f"   Alert Count: {alert.alert_count}")