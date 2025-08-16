# Session 6 - Module B: Enterprise Modular Systems (30 minutes)

**Prerequisites**: [Session 6 Core Section Complete](Session6_Atomic_Agents_Modular_Architecture.md)  
**Target Audience**: Enterprise architects and production system builders  
**Cognitive Load**: 3 enterprise concepts

---

## 🎯 Module Overview

This module explores production-scale atomic agent systems including enterprise context management, multi-tenant architectures, performance monitoring, and deployment strategies. You'll learn to build robust, scalable atomic systems that can handle enterprise workloads with comprehensive governance and observability.

### Learning Objectives
By the end of this module, you will:
- Implement enterprise context providers for business-aware agents
- Design multi-tenant atomic agent architectures with isolation and resource management
- Build comprehensive monitoring and observability systems for production deployment
- Create deployment strategies for atomic agent systems in enterprise environments

---

## Part 1: Enterprise Context Management (15 minutes)

### Advanced Context Provider Systems

🗂️ **File**: `src/session6/enterprise_context.py` - Production context management

Enterprise atomic agents require sophisticated context awareness that goes beyond simple configuration. Let's start by defining the foundational types and enums:

```python
from typing import Dict, List, Any, Optional, Protocol, runtime_checkable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum
```

The import statements establish our foundation for enterprise context management, including typing for strong contracts and asyncio for scalable operations.

Next, we define the hierarchical context scope system that enables granular control over information access:

```python
class ContextScope(Enum):
    """Scope levels for enterprise context"""
    GLOBAL = "global"          # Organization-wide context
    DIVISION = "division"      # Business division context
    DEPARTMENT = "department"  # Department-specific context
    PROJECT = "project"        # Project-level context
    USER = "user"             # User-specific context
    SESSION = "session"       # Session-specific context
```

This scope hierarchy allows agents to access context at appropriate organizational levels, ensuring security and relevance. Now we need metadata structures to track context lifecycle:

```python
@dataclass
class ContextMetadata:
    """Metadata for context entries"""
    created_at: datetime
    created_by: str
    scope: ContextScope
    priority: int = 5  # 1-10, higher is more important
    expires_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    access_control: Dict[str, List[str]] = field(default_factory=dict)
```

The metadata structure provides audit trails, expiration management, and access control - critical for enterprise compliance. Finally, we define the contract that all context providers must implement:

```python
@runtime_checkable
class EnterpriseContextProvider(Protocol):
    """Protocol for enterprise context providers"""
    
    async def get_context(self, scope: ContextScope, 
                         context_key: str, 
                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve context for specified scope and key"""
        ...
    
    async def set_context(self, scope: ContextScope, 
                         context_key: str, 
                         context_data: Dict[str, Any],
                         metadata: ContextMetadata) -> bool:
        """Set context with metadata and access control"""
        ...
    
    async def invalidate_context(self, scope: ContextScope, 
                                context_key: str) -> bool:
        """Invalidate context entry"""
        ...

Now let's implement the policy context provider that manages enterprise compliance and governance rules:

```python
class PolicyContextProvider:
    """Enterprise policy and compliance context provider"""
    
    def __init__(self, policy_store_config: Dict[str, Any]):
        self.policy_store = policy_store_config
        self.policy_cache = {}
        self.cache_ttl = timedelta(minutes=30)
        self.logger = logging.getLogger(__name__)
```

The policy provider manages enterprise governance rules with configurable caching to balance performance with policy freshness. The main context retrieval method implements intelligent caching:

```python
    async def get_context(self, scope: ContextScope, 
                         context_key: str, 
                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve policy context with caching and user-specific rules"""
        
        cache_key = f"{scope.value}:{context_key}:{user_id or 'anonymous'}"
        
        # Check cache first
        if cache_key in self.policy_cache:
            cached_entry = self.policy_cache[cache_key]
            if datetime.now() - cached_entry["timestamp"] < self.cache_ttl:
                return cached_entry["data"]
        
        # Fetch policy context
        policy_context = await self._fetch_policy_context(scope, context_key, user_id)
        
        # Cache the result
        self.policy_cache[cache_key] = {
            "data": policy_context,
            "timestamp": datetime.now()
        }
        
        return policy_context
    
The core policy fetching logic assembles comprehensive enterprise governance rules:

```python
    async def _fetch_policy_context(self, scope: ContextScope, 
                                   context_key: str, 
                                   user_id: Optional[str]) -> Dict[str, Any]:
        """Fetch policy context from enterprise systems"""
        
        base_policies = {
            "data_handling": {
                "encryption_required": True,
                "retention_period_days": 2555,  # 7 years
                "anonymization_required": True,
                "cross_border_transfer": "restricted"
            },
            "ai_governance": {
                "model_approval_required": True,
                "human_oversight_required": True,
                "bias_monitoring_enabled": True,
                "explainability_required": True
            },
            "security": {
                "authentication_required": True,
                "authorization_levels": ["read", "write", "admin"],
                "audit_logging_required": True,
                "session_timeout_minutes": 60
            }
        }
```

These base policies establish enterprise-wide standards for data protection, AI governance, and security. The system then applies contextual overrides:

```python
        # Apply user-specific overrides
        if user_id:
            user_policies = await self._get_user_specific_policies(user_id)
            base_policies.update(user_policies)
        
        # Apply scope-specific policies
        scope_policies = await self._get_scope_policies(scope, context_key)
        base_policies.update(scope_policies)
        
        return {
            "policies": base_policies,
            "enforcement_level": "strict",
            "last_updated": datetime.now().isoformat(),
            "policy_version": "2025.1",
            "compliance_frameworks": ["GDPR", "SOX", "HIPAA", "ISO27001"]
        }
    
The policy system provides role-based customization to ensure users get appropriate permissions:

```python
    async def _get_user_specific_policies(self, user_id: str) -> Dict[str, Any]:
        """Get user-specific policy overrides"""
        
        # Simulate user role-based policies
        user_roles = await self._get_user_roles(user_id)
        
        user_policies = {}
        
        if "data_scientist" in user_roles:
            user_policies["ai_governance"] = {
                "model_experimentation_allowed": True,
                "data_sampling_allowed": True,
                "model_performance_tracking": True
            }
        
        if "admin" in user_roles:
            user_policies["security"] = {
                "elevated_permissions": True,
                "system_configuration_access": True,
                "user_management_access": True
            }
        
        return user_policies
```

This role-based approach ensures that different user types get appropriate policy configurations. The role lookup system integrates with enterprise identity management:

```python
    async def _get_user_roles(self, user_id: str) -> List[str]:
        """Get user roles from identity management system"""
        # Simulate role lookup
        role_mapping = {
            "user_123": ["data_scientist", "team_lead"],
            "user_456": ["admin", "security_officer"],
            "user_789": ["business_analyst", "read_only"]
        }
        return role_mapping.get(user_id, ["user"])

Next, we implement the business context provider that gives agents awareness of market and operational conditions:

```python
class BusinessContextProvider:
    """Business context provider for market and operational awareness"""
    
    def __init__(self, business_data_sources: Dict[str, Any]):
        self.data_sources = business_data_sources
        self.context_cache = {}
        self.logger = logging.getLogger(__name__)
```

The business context provider connects agents to real-world business intelligence, making them aware of market conditions and operational constraints. The main context retrieval method routes to specialized context types:

```python
    async def get_context(self, scope: ContextScope, 
                         context_key: str, 
                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve business context including market conditions and operational state"""
        
        business_context = {}
        
        if context_key == "market_conditions":
            business_context = await self._get_market_context()
        elif context_key == "operational_metrics":
            business_context = await self._get_operational_context()
        elif context_key == "financial_constraints":
            business_context = await self._get_financial_context(scope)
        elif context_key == "regulatory_environment":
            business_context = await self._get_regulatory_context()
        
        return business_context
    
The market context method provides agents with comprehensive market intelligence:

```python
    async def _get_market_context(self) -> Dict[str, Any]:
        """Get current market conditions and trends"""
        
        return {
            "market_sentiment": "cautiously_optimistic",
            "economic_indicators": {
                "gdp_growth": 2.3,
                "unemployment_rate": 3.8,
                "inflation_rate": 2.1,
                "interest_rates": 5.25
            },
            "industry_trends": {
                "ai_adoption_rate": "accelerating",
                "automation_investment": "increasing",
                "regulatory_scrutiny": "heightened",
                "talent_shortage": "critical"
            },
            "competitive_landscape": {
                "market_competition": "high",
                "barrier_to_entry": "medium",
                "technology_disruption_risk": "high",
                "customer_switching_cost": "low"
            },
            "last_updated": datetime.now().isoformat(),
            "data_confidence": 0.85
        }
    
This market intelligence enables agents to make business-aware decisions based on current economic and competitive conditions. The operational context provides real-time system health and performance data:

```python
    async def _get_operational_context(self) -> Dict[str, Any]:
        """Get current operational metrics and system health"""
        
        return {
            "system_health": {
                "overall_status": "healthy",
                "cpu_utilization": 65.2,
                "memory_utilization": 78.1,
                "storage_utilization": 82.5,
                "network_latency_ms": 23.4
            },
            "performance_metrics": {
                "requests_per_second": 1547,
                "average_response_time_ms": 125,
                "error_rate_percent": 0.12,
                "uptime_percent": 99.97
            },
            "capacity_planning": {
                "current_load_percent": 72,
                "projected_growth_30d": 15.3,
                "scaling_threshold_percent": 85,
                "time_to_scale_minutes": 8
            },
            "operational_costs": {
                "hourly_compute_cost": 47.23,
                "daily_operational_cost": 1133.52,
                "cost_per_request": 0.0012,
                "budget_utilization_percent": 67.8
            }
        }

This operational context enables agents to make resource-aware decisions and respond to system constraints. Now we implement the orchestrator that coordinates multiple context providers:

```python
class EnterpriseContextOrchestrator:
    """Orchestrates multiple context providers for comprehensive enterprise awareness"""
    
    def __init__(self):
        self.context_providers: Dict[str, EnterpriseContextProvider] = {}
        self.context_hierarchy = {}
        self.access_policies = {}
        self.logger = logging.getLogger(__name__)
```

The orchestrator manages multiple context providers, enabling agents to access comprehensive enterprise intelligence from a single interface. Provider registration establishes priority and access control:

```python
    def register_provider(self, provider_name: str, 
                         provider: EnterpriseContextProvider,
                         priority: int = 5):
        """Register a context provider with priority"""
        
        self.context_providers[provider_name] = provider
        self.context_hierarchy[provider_name] = {
            "priority": priority,
            "enabled": True,
            "last_accessed": None
        }
    
The core orchestration method aggregates context from multiple providers based on priority:

```python
    async def get_comprehensive_context(self, scope: ContextScope,
                                      context_keys: List[str],
                                      user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive context from multiple providers"""
        
        comprehensive_context = {
            "metadata": {
                "scope": scope.value,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "providers_consulted": []
            },
            "context": {}
        }
        
        # Sort providers by priority
        sorted_providers = sorted(
            self.context_providers.items(),
            key=lambda x: self.context_hierarchy[x[0]]["priority"],
            reverse=True
        )
```

The method iterates through providers in priority order, collecting context while handling failures gracefully:

```python
        for context_key in context_keys:
            context_data = {}
            
            for provider_name, provider in sorted_providers:
                if not self.context_hierarchy[provider_name]["enabled"]:
                    continue
                
                try:
                    provider_context = await provider.get_context(scope, context_key, user_id)
                    
                    if provider_context:
                        context_data[provider_name] = provider_context
                        
                        if provider_name not in comprehensive_context["metadata"]["providers_consulted"]:
                            comprehensive_context["metadata"]["providers_consulted"].append(provider_name)
                        
                        # Update last accessed time
                        self.context_hierarchy[provider_name]["last_accessed"] = datetime.now()
                
                except Exception as e:
                    self.logger.error(f"Provider {provider_name} failed for {context_key}: {str(e)}")
                    continue
            
            comprehensive_context["context"][context_key] = context_data
        
        return comprehensive_context
    
The orchestrator also provides context integration capabilities for agent prompts:

```python
    def apply_context_to_prompt(self, base_prompt: str, 
                               context: Dict[str, Any],
                               context_integration_strategy: str = "append") -> str:
        """Apply context to agent prompts using specified strategy"""
        
        if context_integration_strategy == "append":
            return self._append_context_strategy(base_prompt, context)
        elif context_integration_strategy == "inject":
            return self._inject_context_strategy(base_prompt, context)
        elif context_integration_strategy == "template":
            return self._template_context_strategy(base_prompt, context)
        else:
            return base_prompt
```

The append strategy provides a simple but effective way to add context to agent prompts:

```python
    def _append_context_strategy(self, prompt: str, context: Dict[str, Any]) -> str:
        """Append context information to the end of the prompt"""
        
        context_section = "\n\n--- Enterprise Context ---\n"
        
        for context_key, provider_data in context.get("context", {}).items():
            context_section += f"\n{context_key.title()} Context:\n"
            
            for provider_name, data in provider_data.items():
                if isinstance(data, dict):
                    context_section += f"• {provider_name}: {self._format_context_data(data)}\n"
        
        return prompt + context_section
```

The formatting utility ensures context data is presented in a digestible format for language models:

```python
    def _format_context_data(self, data: Dict[str, Any]) -> str:
        """Format context data for prompt inclusion"""
        
        if not data:
            return "No data available"
        
        formatted_items = []
        for key, value in data.items():
            if isinstance(value, dict):
                formatted_items.append(f"{key}: {len(value)} items")
            elif isinstance(value, list):
                formatted_items.append(f"{key}: {len(value)} items")
            else:
                formatted_items.append(f"{key}: {value}")
        
        return ", ".join(formatted_items[:3])  # Limit to 3 items to avoid prompt bloat
```

---

## Part 2: Multi-Tenant Architecture and Monitoring (15 minutes)

### Production Deployment Patterns

🗂️ **File**: `src/session6/enterprise_deployment.py` - Production deployment systems

```python
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
import json
from enum import Enum
import threading
import queue

class TenantIsolationLevel(Enum):
    """Levels of tenant isolation"""
    SHARED = "shared"              # Shared infrastructure
    NAMESPACE = "namespace"        # Logical separation
    DEDICATED = "dedicated"        # Dedicated resources
    PHYSICAL = "physical"          # Physical separation

@dataclass
class TenantConfiguration:
    """Configuration for enterprise tenant"""
    tenant_id: str
    tenant_name: str
    isolation_level: TenantIsolationLevel
    resource_limits: Dict[str, Any]
    security_policies: Dict[str, Any]
    compliance_requirements: List[str]
    billing_configuration: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ResourceQuota:
    """Resource quotas for tenant isolation"""
    max_concurrent_agents: int = 10
    max_memory_mb: int = 2048
    max_cpu_cores: float = 2.0
    max_storage_gb: int = 10
    max_requests_per_minute: int = 1000
    max_execution_time_seconds: int = 300

class MultiTenantAtomicOrchestrator:
    """Enterprise multi-tenant orchestrator for atomic agents"""
    
    def __init__(self):
        self.tenants: Dict[str, TenantConfiguration] = {}
        self.tenant_resources: Dict[str, Dict[str, Any]] = {}
        self.resource_monitors: Dict[str, 'ResourceMonitor'] = {}
        self.global_metrics = {}
        self.logger = logging.getLogger(__name__)
        
    def register_tenant(self, tenant_config: TenantConfiguration):
        """Register a new tenant with isolated resources"""
        
        tenant_id = tenant_config.tenant_id
        self.tenants[tenant_id] = tenant_config
        
        # Initialize tenant resources
        self.tenant_resources[tenant_id] = {
            "active_agents": {},
            "resource_usage": {
                "memory_mb": 0,
                "cpu_usage": 0.0,
                "storage_gb": 0,
                "requests_count": 0,
                "last_reset": datetime.now()
            },
            "performance_metrics": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0,
                "last_24h_usage": []
            }
        }
        
        # Initialize resource monitor
        self.resource_monitors[tenant_id] = ResourceMonitor(
            tenant_id, 
            tenant_config.resource_limits.get("quota", ResourceQuota())
        )
        
        self.logger.info(f"Registered tenant: {tenant_id} with isolation: {tenant_config.isolation_level.value}")
    
    async def execute_agent_for_tenant(self, tenant_id: str, 
                                     agent_id: str, 
                                     input_data: Any,
                                     execution_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute atomic agent with tenant isolation and resource management"""
        
        if tenant_id not in self.tenants:
            raise ValueError(f"Tenant {tenant_id} not registered")
        
        tenant_config = self.tenants[tenant_id]
        resource_monitor = self.resource_monitors[tenant_id]
        
        # Check resource limits before execution
        resource_check = await resource_monitor.check_resource_availability(execution_context or {})
        
        if not resource_check["available"]:
            return {
                "status": "rejected",
                "reason": "Resource limits exceeded",
                "limits_exceeded": resource_check["limits_exceeded"],
                "current_usage": resource_check["current_usage"]
            }
        
        execution_start = datetime.now()
        
        try:
            # Reserve resources
            resource_reservation = await resource_monitor.reserve_resources(execution_context or {})
            
            # Execute agent with tenant context
            tenant_context = await self._prepare_tenant_context(tenant_id, execution_context or {})
            
            # Create tenant-isolated agent execution
            result = await self._execute_with_tenant_isolation(
                tenant_id, agent_id, input_data, tenant_context
            )
            
            # Record successful execution
            execution_time = (datetime.now() - execution_start).total_seconds()
            await self._record_execution_metrics(
                tenant_id, "success", execution_time, resource_reservation
            )
            
            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "resource_usage": resource_reservation,
                "tenant_id": tenant_id
            }
            
        except Exception as e:
            execution_time = (datetime.now() - execution_start).total_seconds()
            await self._record_execution_metrics(
                tenant_id, "error", execution_time, {}
            )
            
            self.logger.error(f"Agent execution failed for tenant {tenant_id}: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e),
                "execution_time": execution_time,
                "tenant_id": tenant_id
            }
        
        finally:
            # Release reserved resources
            if 'resource_reservation' in locals():
                await resource_monitor.release_resources(resource_reservation)
    
    async def _prepare_tenant_context(self, tenant_id: str, 
                                     execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tenant-specific context for agent execution"""
        
        tenant_config = self.tenants[tenant_id]
        
        tenant_context = {
            "tenant_id": tenant_id,
            "tenant_name": tenant_config.tenant_name,
            "isolation_level": tenant_config.isolation_level.value,
            "security_policies": tenant_config.security_policies,
            "compliance_requirements": tenant_config.compliance_requirements,
            "execution_environment": {
                "resource_limits": tenant_config.resource_limits,
                "execution_timestamp": datetime.now().isoformat(),
                "execution_id": f"{tenant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        }
        
        # Merge with provided execution context
        tenant_context.update(execution_context)
        
        return tenant_context

class ResourceMonitor:
    """Monitors and enforces resource usage for tenant isolation"""
    
    def __init__(self, tenant_id: str, resource_quota: ResourceQuota):
        self.tenant_id = tenant_id
        self.resource_quota = resource_quota
        self.current_usage = {
            "concurrent_agents": 0,
            "memory_mb": 0,
            "cpu_cores": 0.0,
            "storage_gb": 0,
            "requests_in_window": 0,
            "window_start": datetime.now()
        }
        self.usage_history = []
        self.lock = threading.Lock()
        
    async def check_resource_availability(self, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if resources are available for new execution"""
        
        with self.lock:
            # Reset request window if needed
            if datetime.now() - self.current_usage["window_start"] > timedelta(minutes=1):
                self.current_usage["requests_in_window"] = 0
                self.current_usage["window_start"] = datetime.now()
            
            estimated_requirements = self._estimate_resource_requirements(execution_context)
            limits_exceeded = []
            
            # Check each resource limit
            if (self.current_usage["concurrent_agents"] + 1) > self.resource_quota.max_concurrent_agents:
                limits_exceeded.append("concurrent_agents")
            
            if (self.current_usage["memory_mb"] + estimated_requirements["memory_mb"]) > self.resource_quota.max_memory_mb:
                limits_exceeded.append("memory")
            
            if (self.current_usage["cpu_cores"] + estimated_requirements["cpu_cores"]) > self.resource_quota.max_cpu_cores:
                limits_exceeded.append("cpu")
            
            if (self.current_usage["requests_in_window"] + 1) > self.resource_quota.max_requests_per_minute:
                limits_exceeded.append("request_rate")
            
            return {
                "available": len(limits_exceeded) == 0,
                "limits_exceeded": limits_exceeded,
                "current_usage": self.current_usage.copy(),
                "estimated_requirements": estimated_requirements
            }
    
    async def reserve_resources(self, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Reserve resources for execution"""
        
        estimated_requirements = self._estimate_resource_requirements(execution_context)
        
        with self.lock:
            # Update current usage
            self.current_usage["concurrent_agents"] += 1
            self.current_usage["memory_mb"] += estimated_requirements["memory_mb"]
            self.current_usage["cpu_cores"] += estimated_requirements["cpu_cores"]
            self.current_usage["requests_in_window"] += 1
            
            reservation = {
                "reservation_id": f"res_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "memory_mb": estimated_requirements["memory_mb"],
                "cpu_cores": estimated_requirements["cpu_cores"],
                "reserved_at": datetime.now()
            }
            
            return reservation
    
    async def release_resources(self, reservation: Dict[str, Any]):
        """Release reserved resources"""
        
        with self.lock:
            self.current_usage["concurrent_agents"] -= 1
            self.current_usage["memory_mb"] -= reservation["memory_mb"]
            self.current_usage["cpu_cores"] -= reservation["cpu_cores"]
            
            # Ensure we don't go negative
            self.current_usage["memory_mb"] = max(0, self.current_usage["memory_mb"])
            self.current_usage["cpu_cores"] = max(0.0, self.current_usage["cpu_cores"])
            self.current_usage["concurrent_agents"] = max(0, self.current_usage["concurrent_agents"])
    
    def _estimate_resource_requirements(self, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resource requirements based on execution context"""
        
        # Default requirements
        base_requirements = {
            "memory_mb": 256,
            "cpu_cores": 0.5,
            "estimated_duration": 30  # seconds
        }
        
        # Adjust based on context
        complexity = execution_context.get("complexity", "medium")
        model_size = execution_context.get("model_size", "standard")
        
        if complexity == "high":
            base_requirements["memory_mb"] *= 2
            base_requirements["cpu_cores"] *= 1.5
            base_requirements["estimated_duration"] *= 2
        
        if model_size == "large":
            base_requirements["memory_mb"] *= 1.5
            base_requirements["cpu_cores"] *= 1.2
        
        return base_requirements

class EnterpriseMonitoringSystem:
    """Comprehensive monitoring for enterprise atomic agent systems"""
    
    def __init__(self):
        self.metrics_store = {}
        self.alert_thresholds = {}
        self.alert_queue = queue.Queue()
        self.monitoring_enabled = True
        self.logger = logging.getLogger(__name__)
        
    def configure_monitoring(self, monitoring_config: Dict[str, Any]):
        """Configure enterprise monitoring parameters"""
        
        self.alert_thresholds = {
            "error_rate_percent": monitoring_config.get("error_rate_threshold", 5.0),
            "response_time_ms": monitoring_config.get("response_time_threshold", 1000),
            "resource_utilization_percent": monitoring_config.get("resource_threshold", 80.0),
            "tenant_quota_utilization_percent": monitoring_config.get("quota_threshold", 90.0)
        }
        
        self.monitoring_enabled = monitoring_config.get("enabled", True)
        
    async def record_execution_metrics(self, tenant_id: str, 
                                     agent_id: str, 
                                     execution_result: Dict[str, Any]):
        """Record execution metrics for monitoring and alerting"""
        
        if not self.monitoring_enabled:
            return
        
        timestamp = datetime.now()
        
        # Prepare metrics record
        metrics_record = {
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "timestamp": timestamp.isoformat(),
            "execution_time": execution_result.get("execution_time", 0),
            "status": execution_result.get("status", "unknown"),
            "resource_usage": execution_result.get("resource_usage", {}),
            "error": execution_result.get("error")
        }
        
        # Store metrics
        metrics_key = f"{tenant_id}:{agent_id}"
        if metrics_key not in self.metrics_store:
            self.metrics_store[metrics_key] = []
        
        self.metrics_store[metrics_key].append(metrics_record)
        
        # Check alert conditions
        await self._check_alert_conditions(tenant_id, agent_id, metrics_record)
        
        # Clean up old metrics (keep last 24 hours)
        cutoff_time = timestamp - timedelta(hours=24)
        self.metrics_store[metrics_key] = [
            m for m in self.metrics_store[metrics_key]
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
    
    async def _check_alert_conditions(self, tenant_id: str, 
                                    agent_id: str, 
                                    current_metrics: Dict[str, Any]):
        """Check if current metrics trigger any alerts"""
        
        metrics_key = f"{tenant_id}:{agent_id}"
        recent_metrics = self.metrics_store.get(metrics_key, [])
        
        if len(recent_metrics) < 5:  # Need enough data points
            return
        
        # Calculate recent error rate
        recent_executions = recent_metrics[-10:]  # Last 10 executions
        error_count = len([m for m in recent_executions if m["status"] == "error"])
        error_rate = (error_count / len(recent_executions)) * 100
        
        if error_rate > self.alert_thresholds["error_rate_percent"]:
            self.alert_queue.put({
                "type": "error_rate_high",
                "tenant_id": tenant_id,
                "agent_id": agent_id,
                "error_rate": error_rate,
                "threshold": self.alert_thresholds["error_rate_percent"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Check response time
        avg_response_time = sum(m["execution_time"] for m in recent_executions) / len(recent_executions)
        avg_response_time_ms = avg_response_time * 1000
        
        if avg_response_time_ms > self.alert_thresholds["response_time_ms"]:
            self.alert_queue.put({
                "type": "response_time_high",
                "tenant_id": tenant_id,
                "agent_id": agent_id,
                "avg_response_time_ms": avg_response_time_ms,
                "threshold": self.alert_thresholds["response_time_ms"],
                "timestamp": datetime.now().isoformat()
            })
```

---

## 🎯 Module Summary

You've now mastered enterprise-scale atomic agent systems:

✅ **Enterprise Context Management**: Implemented sophisticated context providers for policy, business, and operational awareness  
✅ **Multi-Tenant Architecture**: Built tenant isolation with resource quotas and security boundaries  
✅ **Production Monitoring**: Created comprehensive observability and alerting systems  
✅ **Deployment Strategies**: Designed scalable deployment patterns for enterprise environments

### Next Steps
- **Return to Core**: [Session 6 Main](Session6_Atomic_Agents_Modular_Architecture.md)
- **Advance to Session 7**: [First ADK Agent](Session7_First_ADK_Agent.md)
- **Compare with Module A**: [Advanced Composition Patterns](Session6_ModuleA_Advanced_Composition_Patterns.md)

---

**🗂️ Source Files for Module B:**
- `src/session6/enterprise_context.py` - Production context management
- `src/session6/enterprise_deployment.py` - Multi-tenant deployment systems
- `src/session6/monitoring_systems.py` - Comprehensive observability