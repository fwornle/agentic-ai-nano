# Production load balancing and auto-scaling
from typing import Dict, Any, List, Optional, Callable
import asyncio
import time
import logging


class RAGLoadBalancer:
    """Intelligent load balancer for RAG services."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.service_instances = {}
        self.health_status = {}
        self.load_metrics = {}
        
        # Load balancing strategies
        self.strategies = {
            'round_robin': self._round_robin_selection,
            'least_connections': self._least_connections_selection,
            'response_time': self._response_time_selection,
            'resource_usage': self._resource_usage_selection
        }
        
        self.current_strategy = self.config.get('strategy', 'response_time')
        self.logger = logging.getLogger(__name__)
        
    async def configure_services(self, services: Dict[str, Any]):
        """Configure services for load balancing."""
        
        for service_name, service_instances in services.items():
            if not isinstance(service_instances, list):
                service_instances = [service_instances]
            
            self.service_instances[service_name] = service_instances
            self.health_status[service_name] = {
                instance: ServiceStatus.HEALTHY 
                for instance in service_instances
            }
            self.load_metrics[service_name] = {
                instance: {
                    'active_connections': 0,
                    'avg_response_time': 0.0,
                    'cpu_usage': 0.0,
                    'memory_usage': 0.0,
                    'error_rate': 0.0
                }
                for instance in service_instances
            }
    
    async def get_service_instance(self, service_name: str) -> Optional[Any]:
        """Get optimal service instance based on current strategy."""
        
        if service_name not in self.service_instances:
            return None
        
        # Filter healthy instances
        healthy_instances = [
            instance for instance in self.service_instances[service_name]
            if self.health_status[service_name][instance] == ServiceStatus.HEALTHY
        ]
        
        if not healthy_instances:
            self.logger.warning(f"No healthy instances available for {service_name}")
            return None
        
        # Apply load balancing strategy
        selected_instance = await self.strategies[self.current_strategy](
            service_name, healthy_instances
        )
        
        # Update connection count
        if selected_instance:
            self.load_metrics[service_name][selected_instance]['active_connections'] += 1
        
        return selected_instance
    
    async def _response_time_selection(self, service_name: str, 
                                     healthy_instances: List[Any]) -> Any:
        """Select instance with best average response time."""
        
        best_instance = None
        best_response_time = float('inf')
        
        for instance in healthy_instances:
            metrics = self.load_metrics[service_name][instance]
            avg_response_time = metrics['avg_response_time']
            
            # Consider both response time and current load
            adjusted_time = avg_response_time * (1 + metrics['active_connections'] * 0.1)
            
            if adjusted_time < best_response_time:
                best_response_time = adjusted_time
                best_instance = instance
        
        return best_instance
    
    async def _least_connections_selection(self, service_name: str, 
                                         healthy_instances: List[Any]) -> Any:
        """Select instance with least active connections."""
        
        return min(
            healthy_instances,
            key=lambda instance: self.load_metrics[service_name][instance]['active_connections']
        )
    
    async def _round_robin_selection(self, service_name: str, 
                                   healthy_instances: List[Any]) -> Any:
        """Simple round-robin selection."""
        
        # Simple round-robin implementation
        if not hasattr(self, '_round_robin_counters'):
            self._round_robin_counters = {}
        
        if service_name not in self._round_robin_counters:
            self._round_robin_counters[service_name] = 0
        
        instance_index = self._round_robin_counters[service_name] % len(healthy_instances)
        self._round_robin_counters[service_name] += 1
        
        return healthy_instances[instance_index]
    
    async def _resource_usage_selection(self, service_name: str, 
                                      healthy_instances: List[Any]) -> Any:
        """Select instance based on resource usage."""
        
        best_instance = None
        lowest_usage = float('inf')
        
        for instance in healthy_instances:
            metrics = self.load_metrics[service_name][instance]
            # Combined resource usage score
            usage_score = (metrics['cpu_usage'] + metrics['memory_usage']) / 2
            
            if usage_score < lowest_usage:
                lowest_usage = usage_score
                best_instance = instance
        
        return best_instance
    
    async def release_service_instance(self, service_name: str, instance: Any):
        """Release service instance and update metrics."""
        
        if (service_name in self.load_metrics and 
            instance in self.load_metrics[service_name]):
            self.load_metrics[service_name][instance]['active_connections'] = max(
                0, self.load_metrics[service_name][instance]['active_connections'] - 1
            )
    
    def update_instance_metrics(self, service_name: str, instance: Any, 
                              metrics: Dict[str, float]):
        """Update metrics for a service instance."""
        
        if (service_name in self.load_metrics and 
            instance in self.load_metrics[service_name]):
            self.load_metrics[service_name][instance].update(metrics)


class RAGAutoScaler:
    """Auto-scaling system for RAG services based on load and performance metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scaling_policies = {}
        self.monitoring_interval = config.get('monitoring_interval', 30)  # seconds
        
        # Scaling thresholds
        self.scale_up_thresholds = config.get('scale_up', {
            'cpu_threshold': 70.0,
            'memory_threshold': 80.0,
            'response_time_threshold': 2.0,
            'queue_size_threshold': 100,
            'error_rate_threshold': 5.0
        })
        
        self.scale_down_thresholds = config.get('scale_down', {
            'cpu_threshold': 30.0,
            'memory_threshold': 40.0,
            'response_time_threshold': 0.5,
            'queue_size_threshold': 10,
            'stable_duration': 300  # 5 minutes of stability
        })
        
        self.logger = logging.getLogger(__name__)
        
        # Start monitoring
        self.monitoring_task = asyncio.create_task(self._continuous_monitoring())
        
    async def register_service_for_scaling(self, service_name: str, 
                                         scaling_config: Dict[str, Any]):
        """Register service for auto-scaling with specific configuration."""
        
        self.scaling_policies[service_name] = {
            'min_instances': scaling_config.get('min_instances', 1),
            'max_instances': scaling_config.get('max_instances', 10),
            'current_instances': scaling_config.get('current_instances', 1),
            'scaling_cooldown': scaling_config.get('cooldown', 300),  # 5 minutes
            'last_scaling_action': 0,
            'stability_window': [],
            'custom_thresholds': scaling_config.get('thresholds', {})
        }
    
    async def _continuous_monitoring(self):
        """Continuously monitor services and trigger scaling decisions."""
        
        while True:
            try:
                for service_name in self.scaling_policies.keys():
                    # Collect current metrics
                    current_metrics = await self._collect_service_metrics(service_name)
                    
                    # Make scaling decision
                    scaling_decision = await self._evaluate_scaling_decision(
                        service_name, current_metrics
                    )
                    
                    if scaling_decision['action'] != 'none':
                        await self._execute_scaling_action(service_name, scaling_decision)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Auto-scaling monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Collect current metrics for a service."""
        
        # This would integrate with your monitoring system
        # For now, return simulated metrics
        import random
        
        return {
            'cpu_usage': random.uniform(20, 90),
            'memory_usage': random.uniform(30, 85),
            'avg_response_time': random.uniform(0.2, 3.0),
            'queue_size': random.randint(0, 150),
            'error_rate': random.uniform(0, 10),
            'active_connections': random.randint(5, 200)
        }
    
    async def _evaluate_scaling_decision(self, service_name: str, 
                                       metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate whether scaling action is needed."""
        
        policy = self.scaling_policies[service_name]
        current_time = time.time()
        
        # Check cooldown period
        if current_time - policy['last_scaling_action'] < policy['scaling_cooldown']:
            return {'action': 'none', 'reason': 'cooldown_active'}
        
        # Merge custom thresholds with default ones
        scale_up_thresholds = {**self.scale_up_thresholds, **policy.get('custom_thresholds', {})}
        
        # Check scale-up conditions
        scale_up_triggered = (
            metrics['cpu_usage'] > scale_up_thresholds['cpu_threshold'] or
            metrics['memory_usage'] > scale_up_thresholds['memory_threshold'] or
            metrics['avg_response_time'] > scale_up_thresholds['response_time_threshold'] or
            metrics['queue_size'] > scale_up_thresholds['queue_size_threshold'] or
            metrics['error_rate'] > scale_up_thresholds['error_rate_threshold']
        )
        
        if scale_up_triggered and policy['current_instances'] < policy['max_instances']:
            return {
                'action': 'scale_up',
                'target_instances': min(
                    policy['current_instances'] + 1,
                    policy['max_instances']
                ),
                'reason': 'high_load_detected',
                'metrics': metrics
            }
        
        # Check scale-down conditions (requires sustained low usage)
        scale_down_conditions = (
            metrics['cpu_usage'] < self.scale_down_thresholds['cpu_threshold'] and
            metrics['memory_usage'] < self.scale_down_thresholds['memory_threshold'] and
            metrics['avg_response_time'] < self.scale_down_thresholds['response_time_threshold'] and
            metrics['queue_size'] < self.scale_down_thresholds['queue_size_threshold']
        )
        
        # Track stability window
        policy['stability_window'].append({
            'timestamp': current_time,
            'stable': scale_down_conditions
        })
        
        # Keep only recent measurements
        stable_duration = self.scale_down_thresholds['stable_duration']
        policy['stability_window'] = [
            measurement for measurement in policy['stability_window']
            if current_time - measurement['timestamp'] <= stable_duration
        ]
        
        # Check if we have sustained stability for scale-down
        if (len(policy['stability_window']) > 0 and
            all(m['stable'] for m in policy['stability_window']) and
            policy['current_instances'] > policy['min_instances'] and
            current_time - policy['stability_window'][0]['timestamp'] >= stable_duration):
            
            return {
                'action': 'scale_down',
                'target_instances': max(
                    policy['current_instances'] - 1,
                    policy['min_instances']
                ),
                'reason': 'sustained_low_usage',
                'stability_duration': current_time - policy['stability_window'][0]['timestamp']
            }
        
        return {'action': 'none', 'reason': 'no_scaling_needed'}
    
    async def _execute_scaling_action(self, service_name: str, decision: Dict[str, Any]):
        """Execute the scaling action."""
        
        policy = self.scaling_policies[service_name]
        action = decision['action']
        target_instances = decision['target_instances']
        
        self.logger.info(
            f"Executing {action} for {service_name}: {policy['current_instances']} -> {target_instances}"
        )
        
        try:
            if action == 'scale_up':
                await self._scale_up_service(service_name, target_instances)
            elif action == 'scale_down':
                await self._scale_down_service(service_name, target_instances)
            
            # Update policy
            policy['current_instances'] = target_instances
            policy['last_scaling_action'] = time.time()
            
            self.logger.info(f"Successfully scaled {service_name} to {target_instances} instances")
            
        except Exception as e:
            self.logger.error(f"Scaling action failed for {service_name}: {e}")
    
    async def _scale_up_service(self, service_name: str, target_instances: int):
        """Scale up service instances."""
        
        # This would integrate with your container orchestration system
        # For example, with Kubernetes:
        # await self._update_kubernetes_deployment(service_name, target_instances)
        
        self.logger.info(f"Scaling up {service_name} to {target_instances} instances")
        
        # Simulate scaling delay
        await asyncio.sleep(2)
    
    async def _scale_down_service(self, service_name: str, target_instances: int):
        """Scale down service instances gracefully."""
        
        # This would integrate with your container orchestration system
        # Ensure graceful shutdown of instances
        
        self.logger.info(f"Scaling down {service_name} to {target_instances} instances")
        
        # Simulate scaling delay
        await asyncio.sleep(1)
    
    def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status for all services."""
        
        status = {}
        
        for service_name, policy in self.scaling_policies.items():
            status[service_name] = {
                'current_instances': policy['current_instances'],
                'min_instances': policy['min_instances'],
                'max_instances': policy['max_instances'],
                'last_scaling_action': policy['last_scaling_action'],
                'stability_window_size': len(policy['stability_window'])
            }
        
        return status
    
    async def manual_scale(self, service_name: str, target_instances: int) -> Dict[str, Any]:
        """Manually scale a service to target instance count."""
        
        if service_name not in self.scaling_policies:
            return {'success': False, 'error': f'Service {service_name} not registered'}
        
        policy = self.scaling_policies[service_name]
        
        if target_instances < policy['min_instances'] or target_instances > policy['max_instances']:
            return {
                'success': False, 
                'error': f'Target instances {target_instances} outside allowed range {policy["min_instances"]}-{policy["max_instances"]}'
            }
        
        try:
            current_instances = policy['current_instances']
            
            if target_instances > current_instances:
                await self._scale_up_service(service_name, target_instances)
            elif target_instances < current_instances:
                await self._scale_down_service(service_name, target_instances)
            
            policy['current_instances'] = target_instances
            policy['last_scaling_action'] = time.time()
            
            return {
                'success': True,
                'previous_instances': current_instances,
                'new_instances': target_instances,
                'scaling_action': 'manual'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Import the ServiceStatus enum (it should be defined elsewhere)
from enum import Enum

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"