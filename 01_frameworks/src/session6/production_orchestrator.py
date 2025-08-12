# From src/session6/production_orchestrator.py
from typing import Dict, List, Any, Optional
import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from atomic_foundation import AtomicContext, AtomicError, ExecutionError

@dataclass
class ServiceRegistration:
    """Service registration for atomic agent discovery."""
    service_id: str
    service_name: str
    agent_type: str
    endpoint: str
    health_check_url: str
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True

class MetricsCollector:
    """Collect and aggregate metrics from atomic agents."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            'service_registrations': 0,
            'service_unregistrations': 0,
            'health_checks_performed': 0,
            'health_checks_failed': 0,
            'agent_executions': 0,
            'agent_execution_errors': 0,
            'average_execution_time_ms': 0.0
        }
        self.execution_times: List[float] = []
        self.metrics_lock = asyncio.Lock()
    
    async def record_service_registration(self, service: ServiceRegistration):
        """Record service registration metrics."""
        async with self.metrics_lock:
            self.metrics['service_registrations'] += 1
    
    async def record_service_unregistration(self, service: ServiceRegistration):
        """Record service unregistration metrics."""
        async with self.metrics_lock:
            self.metrics['service_unregistrations'] += 1
    
    async def record_health_check(self, service_id: str, is_healthy: bool, response_time_ms: float):
        """Record health check results."""
        async with self.metrics_lock:
            self.metrics['health_checks_performed'] += 1
            if not is_healthy:
                self.metrics['health_checks_failed'] += 1
    
    async def record_agent_execution(self, agent_name: str, execution_time_ms: float, success: bool):
        """Record agent execution metrics."""
        async with self.metrics_lock:
            self.metrics['agent_executions'] += 1
            
            if not success:
                self.metrics['agent_execution_errors'] += 1
            
            # Update execution time metrics
            self.execution_times.append(execution_time_ms)
            
            # Keep only recent execution times (sliding window)
            if len(self.execution_times) > 1000:
                self.execution_times = self.execution_times[-1000:]
            
            # Calculate average execution time
            if self.execution_times:
                self.metrics['average_execution_time_ms'] = sum(self.execution_times) / len(self.execution_times)
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        async with self.metrics_lock:
            return {
                **self.metrics,
                'metrics_collected_at': datetime.utcnow().isoformat(),
                'recent_execution_count': len(self.execution_times)
            }

class AtomicOrchestrator:
    """Production orchestrator for atomic agent services."""
    
    def __init__(
        self, 
        service_name: str = "atomic-orchestrator",
        health_check_interval: int = 30
    ):
        self.service_name = service_name
        self.orchestrator_id = str(uuid.uuid4())
        self.health_check_interval = health_check_interval
        
        # Service registry
        self.services: Dict[str, ServiceRegistration] = {}
        self.service_lock = asyncio.Lock()
        
        # Monitoring
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(f"orchestrator.{service_name}")
        
        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the orchestrator with health checking."""
        self.logger.info(f"Starting atomic orchestrator {self.orchestrator_id}")
        
        # Start background health checking
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        self.logger.info("Orchestrator started successfully")
    
    async def stop(self):
        """Gracefully shutdown the orchestrator."""
        self.logger.info("Shutting down orchestrator...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Wait for health check task to complete
        if self._health_check_task:
            await self._health_check_task
        
        self.logger.info("Orchestrator shutdown complete")
    
    async def register_service(self, registration: ServiceRegistration):
        """Register an atomic agent service."""
        async with self.service_lock:
            self.services[registration.service_id] = registration
            
        self.logger.info(f"Registered service: {registration.service_name} ({registration.service_id})")
        
        # Record registration metric
        await self.metrics_collector.record_service_registration(registration)
    
    async def unregister_service(self, service_id: str):
        """Unregister a service."""
        async with self.service_lock:
            if service_id in self.services:
                service = self.services.pop(service_id)
                self.logger.info(f"Unregistered service: {service.service_name} ({service_id})")
                await self.metrics_collector.record_service_unregistration(service)
    
    async def discover_services(
        self, 
        agent_type: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> List[ServiceRegistration]:
        """Discover available services with optional filtering."""
        async with self.service_lock:
            services = list(self.services.values())
        
        # Filter by agent type
        if agent_type:
            services = [s for s in services if s.agent_type == agent_type]
        
        # Filter by capabilities
        if capabilities:
            services = [
                s for s in services 
                if all(cap in s.capabilities for cap in capabilities)
            ]
        
        # Only return healthy services
        services = [s for s in services if s.is_healthy]
        
        return services
    
    async def _health_check_loop(self):
        """Background health checking for all registered services."""
        import aiohttp
        
        while not self._shutdown_event.is_set():
            try:
                # Get current services
                async with self.service_lock:
                    services_to_check = list(self.services.values())
                
                # Check each service
                health_check_tasks = []
                for service in services_to_check:
                    task = asyncio.create_task(self._check_service_health(service))
                    health_check_tasks.append(task)
                
                # Wait for all health checks with timeout
                if health_check_tasks:
                    await asyncio.wait(health_check_tasks, timeout=10.0)
                
            except Exception as e:
                self.logger.error(f"Health check loop error: {str(e)}")
            
            # Wait for next check interval or shutdown
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(), 
                    timeout=self.health_check_interval
                )
                # If shutdown event is set, exit loop
                break
            except asyncio.TimeoutError:
                # Timeout is expected, continue with next health check
                continue
    
    async def _check_service_health(self, service: ServiceRegistration):
        """Check health of a single service."""
        import aiohttp
        
        start_time = datetime.utcnow()
        is_healthy = False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    service.health_check_url, 
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    is_healthy = response.status == 200
                    
        except Exception as e:
            self.logger.warning(f"Health check failed for {service.service_name}: {str(e)}")
            is_healthy = False
        
        # Calculate response time
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Update service status
        async with self.service_lock:
            if service.service_id in self.services:
                self.services[service.service_id].is_healthy = is_healthy
                self.services[service.service_id].last_health_check = datetime.utcnow()
        
        # Record metrics
        await self.metrics_collector.record_health_check(
            service.service_id, 
            is_healthy, 
            response_time
        )
        
        if not is_healthy:
            self.logger.warning(f"Service {service.service_name} is unhealthy")

class AtomicLoadBalancer:
    """Load balancer for atomic agent services."""
    
    def __init__(self, orchestrator: AtomicOrchestrator):
        self.orchestrator = orchestrator
        self.round_robin_counters: Dict[str, int] = {}
        
    async def route_request(
        self, 
        agent_type: str, 
        input_data: Any, 
        context: AtomicContext,
        strategy: str = "round_robin"
    ) -> Any:
        """Route request to available service using specified strategy."""
        
        # Discover available services
        services = await self.orchestrator.discover_services(agent_type=agent_type)
        
        if not services:
            raise ExecutionError(
                f"No healthy services available for agent type: {agent_type}",
                "LoadBalancer",
                context
            )
        
        # Select service using strategy
        if strategy == "round_robin":
            selected_service = self._round_robin_select(agent_type, services)
        elif strategy == "least_connections":
            selected_service = self._least_connections_select(services)
        else:
            # Default to first available
            selected_service = services[0]
        
        # Execute request with failover
        return await self._execute_with_failover(
            selected_service, 
            services, 
            input_data, 
            context
        )
    
    def _round_robin_select(self, agent_type: str, services: List[ServiceRegistration]) -> ServiceRegistration:
        """Select service using round-robin strategy."""
        if agent_type not in self.round_robin_counters:
            self.round_robin_counters[agent_type] = 0
        
        selected_index = self.round_robin_counters[agent_type] % len(services)
        self.round_robin_counters[agent_type] += 1
        
        return services[selected_index]
    
    def _least_connections_select(self, services: List[ServiceRegistration]) -> ServiceRegistration:
        """Select service with least connections (simplified implementation)."""
        # In a real implementation, track active connections per service
        # For now, just return the first service
        return services[0]
    
    async def _execute_with_failover(
        self, 
        primary_service: ServiceRegistration,
        all_services: List[ServiceRegistration],
        input_data: Any,
        context: AtomicContext,
        max_retries: int = 2
    ) -> Any:
        """Execute request with automatic failover."""
        import aiohttp
        
        services_to_try = [primary_service] + [s for s in all_services if s.service_id != primary_service.service_id]
        
        for attempt, service in enumerate(services_to_try[:max_retries + 1]):
            try:
                # Make HTTP request to service
                async with aiohttp.ClientSession() as session:
                    request_data = {
                        'input_data': input_data.dict() if hasattr(input_data, 'dict') else input_data,
                        'context': context.dict()
                    }
                    
                    async with session.post(
                        f"{service.endpoint}/execute",
                        json=request_data,
                        timeout=aiohttp.ClientTimeout(total=30.0)
                    ) as response:
                        
                        if response.status == 200:
                            result_data = await response.json()
                            return result_data
                        else:
                            error_text = await response.text()
                            raise aiohttp.ClientError(f"HTTP {response.status}: {error_text}")
            
            except Exception as e:
                if attempt < len(services_to_try) - 1:
                    # Try next service
                    continue
                else:
                    # Final attempt failed
                    raise ExecutionError(
                        f"All service attempts failed. Last error: {str(e)}",
                        "LoadBalancer",
                        context,
                        {"attempts": attempt + 1, "services_tried": [s.service_id for s in services_to_try[:attempt + 1]]}
                    )