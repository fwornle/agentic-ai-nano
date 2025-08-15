# Session 9 - Module B: Production Multi-Agent Systems (70 minutes)

**Prerequisites**: [Session 9 Core Section Complete](Session9_Multi_Agent_Patterns.md)  
**Target Audience**: Production engineers and DevOps teams deploying multi-agent systems  
**Cognitive Load**: 5 production concepts

---

## 🎯 Module Overview

This module explores enterprise-grade production deployment patterns for multi-agent systems including distributed monitoring, scalable orchestration, container-based deployment, service mesh integration, and operational excellence practices. You'll learn to build production-ready multi-agent systems that can handle enterprise scale and operational requirements.

### Learning Objectives
By the end of this module, you will:
- Implement comprehensive monitoring and observability for multi-agent systems
- Design scalable deployment patterns with container orchestration
- Create distributed coordination mechanisms with fault tolerance
- Build operational excellence practices for multi-agent system maintenance

---

## Part 1: Enterprise Monitoring & Observability (40 minutes)

### Distributed Multi-Agent Monitoring

🗂️ **File**: `src/session9/distributed_monitoring.py` - Comprehensive monitoring for multi-agent systems

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import json
import logging
from enum import Enum
from collections import defaultdict, deque
import time
import psutil
import aiohttp

class MetricType(Enum):
    """Types of metrics for multi-agent systems"""
    COUNTER = "counter"
    GAUGE = "gauge" 
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class AgentMetric:
    """Individual agent metric"""
    agent_id: str
    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class SystemAlert:
    """System alert definition"""
    alert_id: str
    alert_name: str
    severity: AlertSeverity
    description: str
    affected_agents: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None

class DistributedMetricsCollector:
    """Centralized metrics collection for multi-agent systems"""
    
    def __init__(self, collection_interval: float = 30.0):
        self.collection_interval = collection_interval
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.metric_aggregations: Dict[str, List[float]] = defaultdict(list)
        self.collection_tasks: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger(__name__)
        
        # Alerting system
        self.active_alerts: Dict[str, SystemAlert] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.alert_handlers = []
        
    async def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register agent for monitoring"""
        
        self.agent_registry[agent_id] = {
            'agent_info': agent_info,
            'registration_time': datetime.now(),
            'last_heartbeat': datetime.now(),
            'status': 'active',
            'metrics_endpoint': agent_info.get('metrics_endpoint'),
            'health_endpoint': agent_info.get('health_endpoint')
        }
        
        # Start metric collection for this agent
        if agent_id not in self.collection_tasks:
            task = asyncio.create_task(self._collect_agent_metrics(agent_id))
            self.collection_tasks[agent_id] = task
        
        self.logger.info(f"Registered agent {agent_id} for monitoring")
    
    async def _collect_agent_metrics(self, agent_id: str):
        """Collect metrics from individual agent"""
        
        while agent_id in self.agent_registry:
            try:
                agent_info = self.agent_registry[agent_id]
                metrics_endpoint = agent_info.get('metrics_endpoint')
                
                if metrics_endpoint:
                    # Collect custom metrics from agent
                    custom_metrics = await self._fetch_agent_metrics(agent_id, metrics_endpoint)
                    
                    for metric in custom_metrics:
                        await self._process_metric(metric)
                
                # Collect system metrics
                system_metrics = await self._collect_system_metrics(agent_id)
                for metric in system_metrics:
                    await self._process_metric(metric)
                
                # Update heartbeat
                self.agent_registry[agent_id]['last_heartbeat'] = datetime.now()
                self.agent_registry[agent_id]['status'] = 'active'
                
            except Exception as e:
                self.logger.error(f"Failed to collect metrics from agent {agent_id}: {e}")
                self.agent_registry[agent_id]['status'] = 'unhealthy'
                
                # Generate alert for unhealthy agent
                await self._generate_agent_health_alert(agent_id, str(e))
            
            await asyncio.sleep(self.collection_interval)
    
    async def _fetch_agent_metrics(self, agent_id: str, endpoint: str) -> List[AgentMetric]:
        """Fetch metrics from agent endpoint"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        metrics = []
                        for metric_data in data.get('metrics', []):
                            metric = AgentMetric(
                                agent_id=agent_id,
                                metric_name=metric_data['name'],
                                metric_type=MetricType(metric_data.get('type', 'gauge')),
                                value=float(metric_data['value']),
                                labels=metric_data.get('labels', {})
                            )
                            metrics.append(metric)
                        
                        return metrics
                        
        except Exception as e:
            self.logger.warning(f"Failed to fetch metrics from {endpoint}: {e}")
            
        return []
    
    async def _collect_system_metrics(self, agent_id: str) -> List[AgentMetric]:
        """Collect system-level metrics for agent"""
        
        # In a real implementation, this would collect from the actual agent process
        # Here we simulate with local system metrics
        
        metrics = []
        
        # CPU usage
        cpu_usage = psutil.cpu_percent()
        metrics.append(AgentMetric(
            agent_id=agent_id,
            metric_name="system_cpu_usage",
            metric_type=MetricType.GAUGE,
            value=cpu_usage,
            labels={"unit": "percent"}
        ))
        
        # Memory usage
        memory = psutil.virtual_memory()
        metrics.append(AgentMetric(
            agent_id=agent_id,
            metric_name="system_memory_usage",
            metric_type=MetricType.GAUGE,
            value=memory.percent,
            labels={"unit": "percent"}
        ))
        
        # Network I/O
        network = psutil.net_io_counters()
        metrics.append(AgentMetric(
            agent_id=agent_id,
            metric_name="network_bytes_sent",
            metric_type=MetricType.COUNTER,
            value=float(network.bytes_sent),
            labels={"direction": "sent"}
        ))
        
        metrics.append(AgentMetric(
            agent_id=agent_id,
            metric_name="network_bytes_recv",
            metric_type=MetricType.COUNTER,
            value=float(network.bytes_recv),
            labels={"direction": "received"}
        ))
        
        return metrics
    
    async def _process_metric(self, metric: AgentMetric):
        """Process and store metric"""
        
        # Add to buffer
        self.metrics_buffer.append(metric)
        
        # Update aggregations
        self.metric_aggregations[f"{metric.agent_id}:{metric.metric_name}"].append(metric.value)
        
        # Keep only recent values for aggregation
        if len(self.metric_aggregations[f"{metric.agent_id}:{metric.metric_name}"]) > 100:
            self.metric_aggregations[f"{metric.agent_id}:{metric.metric_name}"] = \
                self.metric_aggregations[f"{metric.agent_id}:{metric.metric_name}"][-50:]
        
        # Check alert rules
        await self._check_alert_rules(metric)
    
    async def _check_alert_rules(self, metric: AgentMetric):
        """Check if metric triggers any alert rules"""
        
        for rule in self.alert_rules:
            if await self._evaluate_alert_rule(rule, metric):
                await self._trigger_alert(rule, metric)
    
    async def _evaluate_alert_rule(self, rule: Dict[str, Any], metric: AgentMetric) -> bool:
        """Evaluate if metric satisfies alert rule condition"""
        
        # Check if rule applies to this metric
        if rule.get('metric_name') and rule['metric_name'] != metric.metric_name:
            return False
        
        if rule.get('agent_id') and rule['agent_id'] != metric.agent_id:
            return False
        
        # Evaluate condition
        condition_type = rule.get('condition_type', 'threshold')
        
        if condition_type == 'threshold':
            operator = rule.get('operator', '>')
            threshold = rule.get('threshold', 0)
            
            if operator == '>':
                return metric.value > threshold
            elif operator == '<':
                return metric.value < threshold
            elif operator == '>=':
                return metric.value >= threshold
            elif operator == '<=':
                return metric.value <= threshold
            elif operator == '==':
                return metric.value == threshold
            elif operator == '!=':
                return metric.value != threshold
        
        elif condition_type == 'rate_of_change':
            # Check rate of change over time window
            metric_key = f"{metric.agent_id}:{metric.metric_name}"
            recent_values = self.metric_aggregations.get(metric_key, [])
            
            if len(recent_values) >= 2:
                rate = (recent_values[-1] - recent_values[-2]) / self.collection_interval
                return rate > rule.get('rate_threshold', 0)
        
        return False
    
    async def _trigger_alert(self, rule: Dict[str, Any], metric: AgentMetric):
        """Trigger alert based on rule and metric"""
        
        alert_id = f"{rule['name']}:{metric.agent_id}:{metric.metric_name}"
        
        # Check if alert already active
        if alert_id in self.active_alerts and not self.active_alerts[alert_id].resolved:
            return  # Alert already active
        
        alert = SystemAlert(
            alert_id=alert_id,
            alert_name=rule['name'],
            severity=AlertSeverity(rule.get('severity', 'warning')),
            description=rule['description'].format(
                agent_id=metric.agent_id,
                metric_name=metric.metric_name,
                value=metric.value
            ),
            affected_agents=[metric.agent_id]
        )
        
        self.active_alerts[alert_id] = alert
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")
        
        self.logger.warning(f"Alert triggered: {alert.alert_name} for agent {metric.agent_id}")
    
    async def _generate_agent_health_alert(self, agent_id: str, error: str):
        """Generate alert for agent health issues"""
        
        alert_id = f"agent_health:{agent_id}"
        
        if alert_id not in self.active_alerts or self.active_alerts[alert_id].resolved:
            alert = SystemAlert(
                alert_id=alert_id,
                alert_name="Agent Health Issue",
                severity=AlertSeverity.CRITICAL,
                description=f"Agent {agent_id} is experiencing health issues: {error}",
                affected_agents=[agent_id]
            )
            
            self.active_alerts[alert_id] = alert
            
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    self.logger.error(f"Alert handler failed: {e}")
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add new alert rule"""
        
        required_fields = ['name', 'description', 'condition_type']
        if not all(field in rule for field in required_fields):
            raise ValueError(f"Alert rule must contain: {required_fields}")
        
        self.alert_rules.append(rule)
        self.logger.info(f"Added alert rule: {rule['name']}")
    
    def add_alert_handler(self, handler: callable):
        """Add alert handler function"""
        
        self.alert_handlers.append(handler)
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        
        now = datetime.now()
        
        # Agent status summary
        agent_status = {
            'total_agents': len(self.agent_registry),
            'active_agents': sum(1 for info in self.agent_registry.values() 
                               if info['status'] == 'active'),
            'unhealthy_agents': sum(1 for info in self.agent_registry.values() 
                                  if info['status'] == 'unhealthy'),
            'agents_detail': {}
        }
        
        for agent_id, info in self.agent_registry.items():
            last_heartbeat = info['last_heartbeat']
            heartbeat_age = (now - last_heartbeat).total_seconds()
            
            agent_status['agents_detail'][agent_id] = {
                'status': info['status'],
                'last_heartbeat_seconds_ago': heartbeat_age,
                'registration_time': info['registration_time'].isoformat()
            }
        
        # Alert summary
        alert_summary = {
            'total_alerts': len(self.active_alerts),
            'active_alerts': sum(1 for alert in self.active_alerts.values() 
                               if not alert.resolved),
            'critical_alerts': sum(1 for alert in self.active_alerts.values() 
                                 if alert.severity == AlertSeverity.CRITICAL and not alert.resolved),
            'warning_alerts': sum(1 for alert in self.active_alerts.values() 
                                if alert.severity == AlertSeverity.WARNING and not alert.resolved)
        }
        
        # Metrics summary
        metrics_summary = {
            'total_metrics_collected': len(self.metrics_buffer),
            'unique_metric_types': len(set(f"{metric.agent_id}:{metric.metric_name}" 
                                         for metric in self.metrics_buffer)),
            'collection_interval_seconds': self.collection_interval
        }
        
        return {
            'system_overview': {
                'timestamp': now.isoformat(),
                'agents': agent_status,
                'alerts': alert_summary,
                'metrics': metrics_summary
            }
        }
    
    async def generate_performance_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Filter metrics within time window
        recent_metrics = [metric for metric in self.metrics_buffer 
                         if metric.timestamp >= cutoff_time]
        
        # Agent performance analysis
        agent_performance = {}
        
        for agent_id in self.agent_registry.keys():
            agent_metrics = [m for m in recent_metrics if m.agent_id == agent_id]
            
            if agent_metrics:
                # Calculate performance indicators
                cpu_metrics = [m.value for m in agent_metrics if m.metric_name == 'system_cpu_usage']
                memory_metrics = [m.value for m in agent_metrics if m.metric_name == 'system_memory_usage']
                
                performance = {
                    'total_metrics': len(agent_metrics),
                    'avg_cpu_usage': sum(cpu_metrics) / len(cpu_metrics) if cpu_metrics else 0,
                    'max_cpu_usage': max(cpu_metrics) if cpu_metrics else 0,
                    'avg_memory_usage': sum(memory_metrics) / len(memory_metrics) if memory_metrics else 0,
                    'max_memory_usage': max(memory_metrics) if memory_metrics else 0,
                    'health_score': self._calculate_agent_health_score(agent_id, agent_metrics)
                }
                
                agent_performance[agent_id] = performance
        
        # System-wide trends
        system_trends = {
            'total_metrics_in_window': len(recent_metrics),
            'average_system_cpu': sum(m.value for m in recent_metrics 
                                    if m.metric_name == 'system_cpu_usage') / 
                               max(1, len([m for m in recent_metrics 
                                         if m.metric_name == 'system_cpu_usage'])),
            'average_system_memory': sum(m.value for m in recent_metrics 
                                       if m.metric_name == 'system_memory_usage') / 
                                  max(1, len([m for m in recent_metrics 
                                            if m.metric_name == 'system_memory_usage']))
        }
        
        return {
            'performance_report': {
                'time_window_hours': time_window_hours,
                'report_timestamp': datetime.now().isoformat(),
                'agent_performance': agent_performance,
                'system_trends': system_trends,
                'recommendations': self._generate_performance_recommendations(agent_performance)
            }
        }
    
    def _calculate_agent_health_score(self, agent_id: str, 
                                    recent_metrics: List[AgentMetric]) -> float:
        """Calculate health score for agent based on recent metrics"""
        
        if not recent_metrics:
            return 0.0
        
        # Factors for health score
        cpu_metrics = [m.value for m in recent_metrics if m.metric_name == 'system_cpu_usage']
        memory_metrics = [m.value for m in recent_metrics if m.metric_name == 'system_memory_usage']
        
        health_score = 100.0
        
        # CPU health (penalize high CPU usage)
        if cpu_metrics:
            avg_cpu = sum(cpu_metrics) / len(cpu_metrics)
            if avg_cpu > 80:
                health_score -= 30
            elif avg_cpu > 60:
                health_score -= 15
        
        # Memory health (penalize high memory usage)
        if memory_metrics:
            avg_memory = sum(memory_metrics) / len(memory_metrics)
            if avg_memory > 85:
                health_score -= 25
            elif avg_memory > 70:
                health_score -= 10
        
        # Agent status health
        agent_info = self.agent_registry.get(agent_id, {})
        if agent_info.get('status') != 'active':
            health_score -= 50
        
        # Recent alerts health
        agent_alerts = [alert for alert in self.active_alerts.values() 
                       if agent_id in alert.affected_agents and not alert.resolved]
        health_score -= len(agent_alerts) * 10
        
        return max(0.0, min(100.0, health_score))
    
    def _generate_performance_recommendations(self, 
                                           agent_performance: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        
        recommendations = []
        
        for agent_id, perf in agent_performance.items():
            if perf['health_score'] < 70:
                recommendations.append(f"Agent {agent_id} has low health score ({perf['health_score']:.1f}), investigate resource usage")
            
            if perf['avg_cpu_usage'] > 70:
                recommendations.append(f"Agent {agent_id} showing high CPU usage ({perf['avg_cpu_usage']:.1f}%), consider scaling")
            
            if perf['avg_memory_usage'] > 80:
                recommendations.append(f"Agent {agent_id} showing high memory usage ({perf['avg_memory_usage']:.1f}%), check for memory leaks")
        
        # System-wide recommendations
        unhealthy_count = sum(1 for perf in agent_performance.values() if perf['health_score'] < 70)
        if unhealthy_count > len(agent_performance) * 0.3:
            recommendations.append("More than 30% of agents are unhealthy, investigate system-wide issues")
        
        return recommendations

class DistributedTracing:
    """Distributed tracing for multi-agent interactions"""
    
    def __init__(self):
        self.traces: Dict[str, Dict[str, Any]] = {}
        self.span_buffer: deque = deque(maxlen=10000)
        
    async def start_trace(self, trace_id: str, operation: str, 
                         agent_id: str, metadata: Dict[str, Any] = None) -> str:
        """Start a new distributed trace"""
        
        span_id = f"{trace_id}:{agent_id}:{int(time.time() * 1000)}"
        
        span = {
            'trace_id': trace_id,
            'span_id': span_id,
            'parent_span_id': None,
            'operation': operation,
            'agent_id': agent_id,
            'start_time': datetime.now(),
            'end_time': None,
            'duration_ms': None,
            'status': 'active',
            'metadata': metadata or {},
            'logs': []
        }
        
        if trace_id not in self.traces:
            self.traces[trace_id] = {
                'trace_id': trace_id,
                'start_time': datetime.now(),
                'spans': {}
            }
        
        self.traces[trace_id]['spans'][span_id] = span
        self.span_buffer.append(span)
        
        return span_id
    
    async def finish_span(self, span_id: str, status: str = 'completed', 
                         metadata: Dict[str, Any] = None):
        """Finish a trace span"""
        
        # Find span in traces
        span = None
        for trace in self.traces.values():
            if span_id in trace['spans']:
                span = trace['spans'][span_id]
                break
        
        if span:
            span['end_time'] = datetime.now()
            span['duration_ms'] = (span['end_time'] - span['start_time']).total_seconds() * 1000
            span['status'] = status
            
            if metadata:
                span['metadata'].update(metadata)
    
    def get_trace_analysis(self, trace_id: str) -> Dict[str, Any]:
        """Analyze a specific trace"""
        
        if trace_id not in self.traces:
            return {'error': 'Trace not found'}
        
        trace = self.traces[trace_id]
        spans = trace['spans']
        
        # Calculate trace statistics
        completed_spans = [s for s in spans.values() if s['status'] == 'completed']
        
        if not completed_spans:
            return {'error': 'No completed spans in trace'}
        
        total_duration = max(s['duration_ms'] for s in completed_spans)
        avg_duration = sum(s['duration_ms'] for s in completed_spans) / len(completed_spans)
        
        # Agent participation
        agent_participation = {}
        for span in completed_spans:
            agent_id = span['agent_id']
            if agent_id not in agent_participation:
                agent_participation[agent_id] = {
                    'span_count': 0,
                    'total_duration_ms': 0,
                    'operations': []
                }
            
            agent_participation[agent_id]['span_count'] += 1
            agent_participation[agent_id]['total_duration_ms'] += span['duration_ms']
            agent_participation[agent_id]['operations'].append(span['operation'])
        
        return {
            'trace_id': trace_id,
            'total_spans': len(spans),
            'completed_spans': len(completed_spans),
            'total_duration_ms': total_duration,
            'average_span_duration_ms': avg_duration,
            'agent_participation': agent_participation,
            'critical_path': self._find_critical_path(completed_spans)
        }
    
    def _find_critical_path(self, spans: List[Dict[str, Any]]) -> List[str]:
        """Find critical path through trace spans"""
        
        # Simplified critical path - longest duration spans
        sorted_spans = sorted(spans, key=lambda s: s['duration_ms'], reverse=True)
        
        return [f"{s['agent_id']}:{s['operation']}" for s in sorted_spans[:3]]
```

---

## Part 2: Scalable Deployment Patterns (30 minutes)

### Container Orchestration and Service Mesh

🗂️ **File**: `src/session9/scalable_deployment.py` - Production deployment patterns

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import yaml
import json
import asyncio
from datetime import datetime

@dataclass
class ContainerConfig:
    """Container configuration for agent deployment"""
    image: str
    tag: str = "latest"
    resources: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    ports: List[int] = field(default_factory=list)
    health_check: Dict[str, Any] = field(default_factory=dict)

class KubernetesDeploymentManager:
    """Kubernetes deployment manager for multi-agent systems"""
    
    def __init__(self, namespace: str = "multi-agents"):
        self.namespace = namespace
        self.deployment_templates = {}
        
    def generate_agent_deployment(self, agent_id: str, 
                                config: ContainerConfig,
                                replicas: int = 3) -> Dict[str, Any]:
        """Generate Kubernetes deployment configuration for agent"""
        
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': f'agent-{agent_id}',
                'namespace': self.namespace,
                'labels': {
                    'app': 'multi-agent-system',
                    'agent-id': agent_id,
                    'component': 'agent'
                }
            },
            'spec': {
                'replicas': replicas,
                'selector': {
                    'matchLabels': {
                        'app': 'multi-agent-system',
                        'agent-id': agent_id
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'multi-agent-system',
                            'agent-id': agent_id,
                            'component': 'agent'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': f'agent-{agent_id}',
                            'image': f'{config.image}:{config.tag}',
                            'ports': [{'containerPort': port} for port in config.ports],
                            'env': [
                                {'name': 'AGENT_ID', 'value': agent_id},
                                {'name': 'NAMESPACE', 'value': self.namespace}
                            ] + [
                                {'name': k, 'value': v} 
                                for k, v in config.environment.items()
                            ],
                            'resources': {
                                'requests': {
                                    'cpu': config.resources.get('cpu_request', '100m'),
                                    'memory': config.resources.get('memory_request', '256Mi')
                                },
                                'limits': {
                                    'cpu': config.resources.get('cpu_limit', '500m'),
                                    'memory': config.resources.get('memory_limit', '1Gi')
                                }
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': config.health_check.get('path', '/health'),
                                    'port': config.health_check.get('port', 8080)
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': config.health_check.get('readiness_path', '/ready'),
                                    'port': config.health_check.get('port', 8080)
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }],
                        'serviceAccountName': 'multi-agent-service-account'
                    }
                }
            }
        }
        
        return deployment
    
    def generate_service_configuration(self, agent_id: str, 
                                     ports: List[int]) -> Dict[str, Any]:
        """Generate Kubernetes service configuration"""
        
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f'agent-{agent_id}-service',
                'namespace': self.namespace,
                'labels': {
                    'app': 'multi-agent-system',
                    'agent-id': agent_id
                }
            },
            'spec': {
                'selector': {
                    'app': 'multi-agent-system',
                    'agent-id': agent_id
                },
                'ports': [
                    {
                        'name': f'port-{port}',
                        'port': port,
                        'targetPort': port,
                        'protocol': 'TCP'
                    }
                    for port in ports
                ],
                'type': 'ClusterIP'
            }
        }
        
        return service
    
    def generate_hpa_configuration(self, agent_id: str,
                                 min_replicas: int = 2,
                                 max_replicas: int = 10,
                                 target_cpu: int = 70) -> Dict[str, Any]:
        """Generate Horizontal Pod Autoscaler configuration"""
        
        hpa = {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': f'agent-{agent_id}-hpa',
                'namespace': self.namespace
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': f'agent-{agent_id}'
                },
                'minReplicas': min_replicas,
                'maxReplicas': max_replicas,
                'metrics': [
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'cpu',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': target_cpu
                            }
                        }
                    },
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'memory',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': 80
                            }
                        }
                    }
                ]
            }
        }
        
        return hpa
    
    def generate_complete_agent_manifests(self, agent_id: str,
                                        config: ContainerConfig,
                                        scaling_config: Dict[str, Any] = None) -> str:
        """Generate complete Kubernetes manifests for agent"""
        
        scaling_config = scaling_config or {}
        
        # Generate all configurations
        deployment = self.generate_agent_deployment(
            agent_id, config, 
            scaling_config.get('initial_replicas', 3)
        )
        
        service = self.generate_service_configuration(agent_id, config.ports)
        
        hpa = self.generate_hpa_configuration(
            agent_id,
            scaling_config.get('min_replicas', 2),
            scaling_config.get('max_replicas', 10),
            scaling_config.get('target_cpu', 70)
        )
        
        # Combine into single YAML document
        manifests = [deployment, service, hpa]
        yaml_output = '\n---\n'.join(yaml.dump(manifest) for manifest in manifests)
        
        return yaml_output

class ServiceMeshIntegration:
    """Service mesh integration for multi-agent communication"""
    
    def __init__(self, mesh_type: str = "istio"):
        self.mesh_type = mesh_type
        
    def generate_virtual_service(self, agent_id: str,
                               routing_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Istio VirtualService for agent routing"""
        
        virtual_service = {
            'apiVersion': 'networking.istio.io/v1beta1',
            'kind': 'VirtualService',
            'metadata': {
                'name': f'agent-{agent_id}-vs',
                'namespace': 'multi-agents'
            },
            'spec': {
                'hosts': [f'agent-{agent_id}-service'],
                'http': []
            }
        }
        
        for rule in routing_rules:
            http_rule = {
                'match': [
                    {
                        'headers': rule.get('headers', {}),
                        'uri': {
                            'prefix': rule.get('path_prefix', '/')
                        }
                    }
                ],
                'route': [
                    {
                        'destination': {
                            'host': f'agent-{agent_id}-service',
                            'port': {
                                'number': rule.get('port', 8080)
                            }
                        },
                        'weight': rule.get('weight', 100)
                    }
                ]
            }
            
            # Add fault injection if specified
            if rule.get('fault_injection'):
                http_rule['fault'] = rule['fault_injection']
            
            # Add retry policy if specified
            if rule.get('retry_policy'):
                http_rule['retries'] = rule['retry_policy']
            
            virtual_service['spec']['http'].append(http_rule)
        
        return virtual_service
    
    def generate_destination_rule(self, agent_id: str,
                                load_balancer_policy: str = "ROUND_ROBIN") -> Dict[str, Any]:
        """Generate Istio DestinationRule for agent traffic policy"""
        
        destination_rule = {
            'apiVersion': 'networking.istio.io/v1beta1',
            'kind': 'DestinationRule',
            'metadata': {
                'name': f'agent-{agent_id}-dr',
                'namespace': 'multi-agents'
            },
            'spec': {
                'host': f'agent-{agent_id}-service',
                'trafficPolicy': {
                    'loadBalancer': {
                        'simple': load_balancer_policy
                    },
                    'connectionPool': {
                        'tcp': {
                            'maxConnections': 100
                        },
                        'http': {
                            'http1MaxPendingRequests': 50,
                            'maxRequestsPerConnection': 10
                        }
                    },
                    'outlierDetection': {
                        'consecutiveErrors': 5,
                        'interval': '30s',
                        'baseEjectionTime': '30s',
                        'maxEjectionPercent': 50,
                        'minHealthPercent': 30
                    }
                }
            }
        }
        
        return destination_rule
    
    def generate_peer_authentication(self, namespace: str = "multi-agents") -> Dict[str, Any]:
        """Generate Istio PeerAuthentication for mutual TLS"""
        
        peer_auth = {
            'apiVersion': 'security.istio.io/v1beta1',
            'kind': 'PeerAuthentication',
            'metadata': {
                'name': 'multi-agent-mtls',
                'namespace': namespace
            },
            'spec': {
                'mtls': {
                    'mode': 'STRICT'
                }
            }
        }
        
        return peer_auth

class MultiAgentOrchestrator:
    """High-level orchestrator for multi-agent system deployment"""
    
    def __init__(self):
        self.k8s_manager = KubernetesDeploymentManager()
        self.service_mesh = ServiceMeshIntegration()
        self.deployed_agents: Dict[str, Dict[str, Any]] = {}
        
    async def deploy_multi_agent_system(self, system_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy complete multi-agent system"""
        
        deployment_results = {
            'deployment_id': f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'agents': {},
            'service_mesh_configs': {},
            'monitoring_setup': {},
            'success': True,
            'errors': []
        }
        
        try:
            # Deploy each agent
            for agent_config in system_config.get('agents', []):
                agent_id = agent_config['agent_id']
                
                # Generate Kubernetes manifests
                container_config = ContainerConfig(
                    image=agent_config['image'],
                    tag=agent_config.get('tag', 'latest'),
                    resources=agent_config.get('resources', {}),
                    environment=agent_config.get('environment', {}),
                    ports=agent_config.get('ports', [8080]),
                    health_check=agent_config.get('health_check', {})
                )
                
                manifests = self.k8s_manager.generate_complete_agent_manifests(
                    agent_id, container_config, agent_config.get('scaling', {})
                )
                
                deployment_results['agents'][agent_id] = {
                    'manifests': manifests,
                    'status': 'deployed',
                    'replicas': agent_config.get('scaling', {}).get('initial_replicas', 3)
                }
                
                # Generate service mesh configurations
                routing_rules = agent_config.get('routing_rules', [])
                if routing_rules:
                    virtual_service = self.service_mesh.generate_virtual_service(
                        agent_id, routing_rules
                    )
                    destination_rule = self.service_mesh.generate_destination_rule(
                        agent_id, agent_config.get('load_balancer', 'ROUND_ROBIN')
                    )
                    
                    deployment_results['service_mesh_configs'][agent_id] = {
                        'virtual_service': virtual_service,
                        'destination_rule': destination_rule
                    }
            
            # Generate global service mesh configurations
            peer_auth = self.service_mesh.generate_peer_authentication()
            deployment_results['service_mesh_configs']['global'] = {
                'peer_authentication': peer_auth
            }
            
            # Setup monitoring
            monitoring_config = await self._setup_system_monitoring(system_config)
            deployment_results['monitoring_setup'] = monitoring_config
            
        except Exception as e:
            deployment_results['success'] = False
            deployment_results['errors'].append(str(e))
        
        return deployment_results
    
    async def _setup_system_monitoring(self, system_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup monitoring for the multi-agent system"""
        
        monitoring_setup = {
            'prometheus_config': self._generate_prometheus_config(),
            'grafana_dashboards': self._generate_grafana_dashboards(),
            'alert_rules': self._generate_alert_rules(),
            'service_monitor': self._generate_service_monitor()
        }
        
        return monitoring_setup
    
    def _generate_prometheus_config(self) -> Dict[str, Any]:
        """Generate Prometheus configuration for agent monitoring"""
        
        return {
            'scrape_configs': [
                {
                    'job_name': 'multi-agent-system',
                    'kubernetes_sd_configs': [
                        {
                            'role': 'pod',
                            'namespaces': {
                                'names': ['multi-agents']
                            }
                        }
                    ],
                    'relabel_configs': [
                        {
                            'source_labels': ['__meta_kubernetes_pod_label_app'],
                            'action': 'keep',
                            'regex': 'multi-agent-system'
                        }
                    ]
                }
            ]
        }
    
    def _generate_grafana_dashboards(self) -> List[Dict[str, Any]]:
        """Generate Grafana dashboards for system visualization"""
        
        dashboard = {
            'dashboard': {
                'title': 'Multi-Agent System Overview',
                'panels': [
                    {
                        'title': 'Agent Health Status',
                        'type': 'stat',
                        'targets': [
                            {
                                'expr': 'up{job="multi-agent-system"}',
                                'legendFormat': '{{agent_id}}'
                            }
                        ]
                    },
                    {
                        'title': 'Agent CPU Usage',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'system_cpu_usage{job="multi-agent-system"}',
                                'legendFormat': '{{agent_id}}'
                            }
                        ]
                    },
                    {
                        'title': 'Agent Memory Usage',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'system_memory_usage{job="multi-agent-system"}',
                                'legendFormat': '{{agent_id}}'
                            }
                        ]
                    },
                    {
                        'title': 'Inter-Agent Communication',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'rate(agent_messages_sent_total{job="multi-agent-system"}[5m])',
                                'legendFormat': '{{agent_id}} sent'
                            },
                            {
                                'expr': 'rate(agent_messages_received_total{job="multi-agent-system"}[5m])',
                                'legendFormat': '{{agent_id}} received'
                            }
                        ]
                    }
                ]
            }
        }
        
        return [dashboard]
    
    def _generate_alert_rules(self) -> List[Dict[str, Any]]:
        """Generate alerting rules for the system"""
        
        return [
            {
                'alert': 'AgentDown',
                'expr': 'up{job="multi-agent-system"} == 0',
                'for': '1m',
                'labels': {
                    'severity': 'critical'
                },
                'annotations': {
                    'summary': 'Agent {{$labels.agent_id}} is down',
                    'description': 'Agent {{$labels.agent_id}} has been down for more than 1 minute'
                }
            },
            {
                'alert': 'HighCpuUsage',
                'expr': 'system_cpu_usage{job="multi-agent-system"} > 85',
                'for': '5m',
                'labels': {
                    'severity': 'warning'
                },
                'annotations': {
                    'summary': 'High CPU usage on agent {{$labels.agent_id}}',
                    'description': 'Agent {{$labels.agent_id}} CPU usage is {{$value}}%'
                }
            },
            {
                'alert': 'HighMemoryUsage',
                'expr': 'system_memory_usage{job="multi-agent-system"} > 90',
                'for': '5m',
                'labels': {
                    'severity': 'warning'
                },
                'annotations': {
                    'summary': 'High memory usage on agent {{$labels.agent_id}}',
                    'description': 'Agent {{$labels.agent_id}} memory usage is {{$value}}%'
                }
            }
        ]
    
    def _generate_service_monitor(self) -> Dict[str, Any]:
        """Generate ServiceMonitor for Prometheus operator"""
        
        return {
            'apiVersion': 'monitoring.coreos.com/v1',
            'kind': 'ServiceMonitor',
            'metadata': {
                'name': 'multi-agent-system',
                'namespace': 'multi-agents'
            },
            'spec': {
                'selector': {
                    'matchLabels': {
                        'app': 'multi-agent-system'
                    }
                },
                'endpoints': [
                    {
                        'port': 'metrics',
                        'interval': '30s',
                        'path': '/metrics'
                    }
                ]
            }
        }
```

---

## 🎯 Module Summary

You've now mastered production deployment patterns for multi-agent systems:

✅ **Distributed Monitoring**: Implemented comprehensive monitoring with metrics, alerts, and tracing  
✅ **Container Orchestration**: Built Kubernetes deployment patterns with auto-scaling  
✅ **Service Mesh Integration**: Created Istio configurations for secure inter-agent communication  
✅ **Operational Excellence**: Designed monitoring dashboards and alerting systems  
✅ **Production Readiness**: Built complete deployment orchestration with fault tolerance

### Next Steps
- **Return to Core**: [Session 9 Main](Session9_Multi_Agent_Patterns.md)
- **Continue to Module A**: [Advanced Consensus Algorithms](Session9_ModuleA_Advanced_Consensus_Algorithms.md)
- **Next Session**: [Session 10 - Enterprise Integration](Session10_Enterprise_Integration_Production_Deployment.md)

---

**🗂️ Source Files for Module B:**
- `src/session9/distributed_monitoring.py` - Enterprise monitoring and observability
- `src/session9/scalable_deployment.py` - Container orchestration and service mesh patterns