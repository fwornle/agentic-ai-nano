"""
Auto-scaling utilities for enterprise agent systems.
"""

import asyncio
import time
import psutil
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

class ScalingDirection(Enum):
    """Scaling direction."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_CHANGE = "no_change"

@dataclass
class ScalingMetrics:
    """Metrics used for auto-scaling decisions."""
    cpu_utilization: float
    memory_utilization: float
    request_queue_length: int
    avg_response_time: float
    active_connections: int
    error_rate: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ScalingRule:
    """Configuration for scaling rules."""
    metric_name: str
    threshold_up: float
    threshold_down: float
    evaluation_periods: int
    cooldown_seconds: int
    weight: float = 1.0

class ScalingDecisionEngine:
    """Makes intelligent scaling decisions based on multiple metrics."""
    
    def __init__(self, rules: List[ScalingRule], min_instances: int = 1, max_instances: int = 10):
        self.rules = rules
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.metrics_history: List[ScalingMetrics] = []
        self.last_scaling_action: Optional[datetime] = None
        self.current_instances = min_instances
        
    def add_metrics(self, metrics: ScalingMetrics) -> None:
        """Add new metrics for evaluation."""
        self.metrics_history.append(metrics)
        
        # Keep only recent metrics (last 2 hours)
        cutoff_time = datetime.now() - timedelta(hours=2)
        self.metrics_history = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
    
    def should_scale(self) -> ScalingDirection:
        """Determine if scaling action is needed."""
        if len(self.metrics_history) < 5:  # Need minimum history
            return ScalingDirection.NO_CHANGE
        
        # Check if we're in cooldown period
        if self.last_scaling_action:
            time_since_last_action = datetime.now() - self.last_scaling_action
            min_cooldown = min(rule.cooldown_seconds for rule in self.rules)
            if time_since_last_action.total_seconds() < min_cooldown:
                return ScalingDirection.NO_CHANGE
        
        # Evaluate each rule
        scale_up_score = 0.0
        scale_down_score = 0.0
        
        for rule in self.rules:
            recent_metrics = self._get_recent_metrics_for_rule(rule)
            if len(recent_metrics) >= rule.evaluation_periods:
                avg_value = sum(
                    self._get_metric_value(m, rule.metric_name) 
                    for m in recent_metrics
                ) / len(recent_metrics)
                
                if avg_value > rule.threshold_up:
                    scale_up_score += rule.weight * (avg_value / rule.threshold_up)
                elif avg_value < rule.threshold_down:
                    scale_down_score += rule.weight * (rule.threshold_down / avg_value if avg_value > 0 else 1)
        
        # Make decision based on scores
        if scale_up_score > scale_down_score and scale_up_score > 1.5:
            if self.current_instances < self.max_instances:
                return ScalingDirection.SCALE_UP
        elif scale_down_score > scale_up_score and scale_down_score > 1.5:
            if self.current_instances > self.min_instances:
                return ScalingDirection.SCALE_DOWN
        
        return ScalingDirection.NO_CHANGE
    
    def _get_recent_metrics_for_rule(self, rule: ScalingRule) -> List[ScalingMetrics]:
        """Get recent metrics for rule evaluation."""
        # Get metrics from the last few evaluation periods
        recent_count = rule.evaluation_periods * 2  # Extra buffer
        return self.metrics_history[-recent_count:]
    
    def _get_metric_value(self, metrics: ScalingMetrics, metric_name: str) -> float:
        """Extract metric value by name."""
        return getattr(metrics, metric_name, 0.0)
    
    def execute_scaling_action(self, direction: ScalingDirection) -> int:
        """Execute scaling action and return new instance count."""
        if direction == ScalingDirection.SCALE_UP:
            new_count = min(self.current_instances + 1, self.max_instances)
        elif direction == ScalingDirection.SCALE_DOWN:
            new_count = max(self.current_instances - 1, self.min_instances)
        else:
            return self.current_instances
        
        if new_count != self.current_instances:
            logger.info(f"Scaling {direction.value}: {self.current_instances} -> {new_count}")
            self.current_instances = new_count
            self.last_scaling_action = datetime.now()
        
        return new_count

class SystemMetricsCollector:
    """Collects system metrics for scaling decisions."""
    
    def __init__(self):
        self.request_queue = []
        self.response_times = []
        self.active_connections = 0
        self.error_count = 0
        self.total_requests = 0
        
    async def collect_metrics(self) -> ScalingMetrics:
        """Collect current system metrics."""
        # CPU utilization
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory utilization
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Request queue length (simulated)
        queue_length = len(self.request_queue)
        
        # Average response time
        avg_response_time = (
            sum(self.response_times) / len(self.response_times) 
            if self.response_times else 0.0
        )
        
        # Error rate
        error_rate = (
            (self.error_count / self.total_requests) * 100 
            if self.total_requests > 0 else 0.0
        )
        
        return ScalingMetrics(
            cpu_utilization=cpu_percent,
            memory_utilization=memory_percent,
            request_queue_length=queue_length,
            avg_response_time=avg_response_time,
            active_connections=self.active_connections,
            error_rate=error_rate
        )
    
    def record_request(self, response_time: float, is_error: bool = False):
        """Record a request for metrics calculation."""
        self.response_times.append(response_time)
        self.total_requests += 1
        
        if is_error:
            self.error_count += 1
        
        # Keep only recent response times
        if len(self.response_times) > 1000:
            self.response_times.pop(0)
    
    def add_to_queue(self, request_id: str):
        """Add request to queue."""
        self.request_queue.append({
            'id': request_id,
            'timestamp': datetime.now()
        })
    
    def remove_from_queue(self, request_id: str):
        """Remove request from queue."""
        self.request_queue = [
            req for req in self.request_queue 
            if req['id'] != request_id
        ]

class AutoScaler:
    """Main auto-scaling controller."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Create scaling rules from config
        rules = []
        for rule_config in config.get('scaling_rules', []):
            rules.append(ScalingRule(**rule_config))
        
        self.decision_engine = ScalingDecisionEngine(
            rules=rules,
            min_instances=config.get('min_instances', 1),
            max_instances=config.get('max_instances', 10)
        )
        
        self.metrics_collector = SystemMetricsCollector()
        self.scaling_callbacks: List[Callable[[int], None]] = []
        
        self.monitoring_active = False
        self.monitoring_task = None
        
    def add_scaling_callback(self, callback: Callable[[int], None]):
        """Add callback to be called when scaling occurs."""
        self.scaling_callbacks.append(callback)
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start auto-scaling monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )
        logger.info(f"Started auto-scaling monitoring (interval: {interval_seconds}s)")
    
    async def stop_monitoring(self):
        """Stop auto-scaling monitoring."""
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped auto-scaling monitoring")
    
    async def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = await self.metrics_collector.collect_metrics()
                self.decision_engine.add_metrics(metrics)
                
                # Make scaling decision
                scaling_direction = self.decision_engine.should_scale()
                
                if scaling_direction != ScalingDirection.NO_CHANGE:
                    new_instance_count = self.decision_engine.execute_scaling_action(
                        scaling_direction
                    )
                    
                    # Notify callbacks
                    for callback in self.scaling_callbacks:
                        try:
                            callback(new_instance_count)
                        except Exception as e:
                            logger.error(f"Scaling callback error: {e}")
                
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-scaling loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current auto-scaling status."""
        latest_metrics = (
            self.decision_engine.metrics_history[-1] 
            if self.decision_engine.metrics_history else None
        )
        
        return {
            "monitoring_active": self.monitoring_active,
            "current_instances": self.decision_engine.current_instances,
            "min_instances": self.decision_engine.min_instances,
            "max_instances": self.decision_engine.max_instances,
            "last_scaling_action": (
                self.decision_engine.last_scaling_action.isoformat()
                if self.decision_engine.last_scaling_action else None
            ),
            "metrics_history_count": len(self.decision_engine.metrics_history),
            "latest_metrics": {
                "cpu_utilization": latest_metrics.cpu_utilization if latest_metrics else None,
                "memory_utilization": latest_metrics.memory_utilization if latest_metrics else None,
                "request_queue_length": latest_metrics.request_queue_length if latest_metrics else None,
                "avg_response_time": latest_metrics.avg_response_time if latest_metrics else None,
                "error_rate": latest_metrics.error_rate if latest_metrics else None
            } if latest_metrics else None
        }

# Default scaling configuration
DEFAULT_SCALING_CONFIG = {
    "min_instances": 1,
    "max_instances": 10,
    "scaling_rules": [
        {
            "metric_name": "cpu_utilization",
            "threshold_up": 70.0,
            "threshold_down": 30.0,
            "evaluation_periods": 3,
            "cooldown_seconds": 300,
            "weight": 2.0
        },
        {
            "metric_name": "memory_utilization",
            "threshold_up": 80.0,
            "threshold_down": 40.0,
            "evaluation_periods": 3,
            "cooldown_seconds": 300,
            "weight": 1.5
        },
        {
            "metric_name": "avg_response_time",
            "threshold_up": 2.0,  # 2 seconds
            "threshold_down": 0.5,  # 500ms
            "evaluation_periods": 2,
            "cooldown_seconds": 180,
            "weight": 1.0
        },
        {
            "metric_name": "error_rate",
            "threshold_up": 5.0,  # 5%
            "threshold_down": 1.0,  # 1%
            "evaluation_periods": 2,
            "cooldown_seconds": 120,
            "weight": 3.0
        }
    ]
}