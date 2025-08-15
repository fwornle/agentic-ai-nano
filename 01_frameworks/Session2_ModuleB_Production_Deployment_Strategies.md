# Session 2 - Module B: Production Deployment Strategies (70 minutes)

**Prerequisites**: [Session 2 Core Section Complete](Session2_LangChain_Foundations.md)  
**Target Audience**: Those building real systems  
**Cognitive Load**: 7 production concepts

---

## 🎯 Module Overview

This module focuses on deploying LangChain agents to production environments with enterprise-grade reliability, monitoring, and performance. You'll learn cloud deployment patterns, performance optimization, and comprehensive monitoring strategies.

### Learning Objectives
By the end of this module, you will:
- Deploy LangChain agents to cloud platforms with automated infrastructure
- Implement performance optimization and caching strategies for production workloads
- Set up comprehensive monitoring and observability for agent systems
- Design enterprise deployment architectures with high availability and scaling

---

## Part 1: LangGraph Integration & Production Patterns (25 minutes)

### Cloud Deployment Architecture

🗂️ **File**: `src/session2/cloud_deployment.py` - Production deployment automation

Modern agent deployment requires sophisticated infrastructure management and automated provisioning:

```python
from typing import Dict, List, Any, Optional
import yaml
import json
from datetime import datetime
import boto3
import kubernetes
from dataclasses import dataclass
import logging

@dataclass
class DeploymentConfig:
    name: str
    environment: str
    replicas: int
    cpu_request: str
    cpu_limit: str
    memory_request: str
    memory_limit: str
    image: str
    port: int
    health_check_path: str
    environment_variables: Dict[str, str]

class CloudDeploymentManager:
    """Manage cloud deployment of LangChain agents with enterprise reliability"""
    
    def __init__(self, cloud_provider: str):
        self.cloud_provider = cloud_provider
        self.deployment_config = self._load_deployment_config()
        self.security_config = self._load_security_config()
        self.logger = logging.getLogger(__name__)
        
    def deploy_agent_to_production(self, agent_config: DeploymentConfig) -> Dict[str, Any]:
        """Deploy LangChain agent to production cloud environment"""
        
        deployment_id = f"{agent_config.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        try:
            # Step 1: Generate infrastructure manifests
            manifests = self.generate_kubernetes_manifests(agent_config)
            
            # Step 2: Create cloud resources
            cloud_resources = self._provision_cloud_resources(agent_config)
            
            # Step 3: Deploy to Kubernetes
            deployment_result = self._deploy_to_kubernetes(manifests)
            
            # Step 4: Configure monitoring and alerting
            monitoring_config = self._setup_monitoring(agent_config)
            
            # Step 5: Configure auto-scaling
            scaling_config = self._setup_auto_scaling(agent_config)
            
            return {
                "deployment_id": deployment_id,
                "status": "deployed",
                "cloud_resources": cloud_resources,
                "kubernetes_deployment": deployment_result,
                "monitoring": monitoring_config,
                "scaling": scaling_config,
                "endpoint": self._get_service_endpoint(agent_config),
                "health_check_url": f"{self._get_service_endpoint(agent_config)}{agent_config.health_check_path}"
            }
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            return {
                "deployment_id": deployment_id,
                "status": "failed",
                "error": str(e),
                "rollback_initiated": self._initiate_rollback(deployment_id)
            }

    def generate_kubernetes_manifests(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Generate complete Kubernetes deployment package"""
        
        return {
            "deployment": self._create_deployment_manifest(config),
            "service": self._create_service_manifest(config),
            "configmap": self._create_configmap_manifest(config),
            "ingress": self._create_ingress_manifest(config),
            "hpa": self._create_hpa_manifest(config),  # Horizontal Pod Autoscaler
            "pdb": self._create_pdb_manifest(config)   # Pod Disruption Budget
        }
    
    def _create_deployment_manifest(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Create Kubernetes deployment manifest with production best practices"""
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{config.name}-deployment",
                "labels": {
                    "app": config.name,
                    "environment": config.environment,
                    "version": "v1"
                },
                "annotations": {
                    "deployment.kubernetes.io/revision": "1",
                    "description": f"LangChain agent deployment for {config.name}"
                }
            },
            "spec": {
                "replicas": config.replicas,
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": 1,
                        "maxSurge": 1
                    }
                },
                "selector": {
                    "matchLabels": {
                        "app": config.name,
                        "environment": config.environment
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.name,
                            "environment": config.environment,
                            "version": "v1"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": config.name,
                            "image": config.image,
                            "ports": [{"containerPort": config.port}],
                            "env": [
                                {"name": key, "value": value}
                                for key, value in config.environment_variables.items()
                            ],
                            "resources": {
                                "requests": {
                                    "memory": config.memory_request,
                                    "cpu": config.cpu_request
                                },
                                "limits": {
                                    "memory": config.memory_limit,
                                    "cpu": config.cpu_limit
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": config.health_check_path,
                                    "port": config.port
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10,
                                "timeoutSeconds": 5,
                                "failureThreshold": 3
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": config.port
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5,
                                "timeoutSeconds": 3,
                                "failureThreshold": 3
                            },
                            "securityContext": {
                                "runAsNonRoot": True,
                                "runAsUser": 1000,
                                "allowPrivilegeEscalation": False,
                                "readOnlyRootFilesystem": True
                            }
                        }],
                        "securityContext": {
                            "fsGroup": 2000
                        },
                        "serviceAccountName": f"{config.name}-serviceaccount"
                    }
                }
            }
        }
    
    def _create_service_manifest(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Create Kubernetes service manifest for load balancing"""
        
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{config.name}-service",
                "labels": {
                    "app": config.name,
                    "environment": config.environment
                }
            },
            "spec": {
                "selector": {
                    "app": config.name,
                    "environment": config.environment
                },
                "ports": [{
                    "port": 80,
                    "targetPort": config.port,
                    "protocol": "TCP"
                }],
                "type": "ClusterIP"
            }
        }
    
    def _create_hpa_manifest(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Create Horizontal Pod Autoscaler for automatic scaling"""
        
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{config.name}-hpa",
                "labels": {
                    "app": config.name,
                    "environment": config.environment
                }
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"{config.name}-deployment"
                },
                "minReplicas": max(2, config.replicas),
                "maxReplicas": config.replicas * 3,
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
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 80
                            }
                        }
                    }
                ],
                "behavior": {
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [{
                            "type": "Percent",
                            "value": 50,
                            "periodSeconds": 60
                        }]
                    },
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [{
                            "type": "Percent",
                            "value": 10,
                            "periodSeconds": 60
                        }]
                    }
                }
            }
        }
```

### LangGraph Production Integration

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated
import operator

class ProductionAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_step: str
    iterations: int
    context: Dict[str, Any]
    performance_metrics: Dict[str, float]
    error_state: Optional[str]

class ProductionLangGraphAgent:
    """Production-ready LangGraph agent with enterprise features"""
    
    def __init__(self, llm, tools: List[BaseTool], config: Dict[str, Any]):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.config = config
        
        # Set up persistent checkpointing
        self.checkpointer = SqliteSaver.from_conn_string(
            config.get("checkpoint_db", ":memory:")
        )
        
        # Build production workflow
        self.workflow = self._build_production_workflow()
        
    def _build_production_workflow(self) -> StateGraph:
        """Build production workflow with error handling and monitoring"""
        
        workflow = StateGraph(ProductionAgentState)
        
        # Add nodes with production features
        workflow.add_node("agent", self._agent_node_with_monitoring)
        workflow.add_node("tools", self._tools_node_with_retry)
        workflow.add_node("reflection", self._reflection_node_with_validation)
        workflow.add_node("error_handler", self._error_handler_node)
        workflow.add_node("performance_tracker", self._performance_tracker_node)
        
        # Define conditional edges with error handling
        workflow.add_conditional_edges(
            "agent",
            self._should_continue_with_error_check,
            {
                "continue": "tools",
                "reflect": "reflection",
                "error": "error_handler",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "tools",
            self._tools_result_router,
            {
                "success": "performance_tracker",
                "retry": "tools",
                "error": "error_handler",
                "agent": "agent"
            }
        )
        
        workflow.add_edge("reflection", "agent")
        workflow.add_edge("error_handler", END)
        workflow.add_edge("performance_tracker", "agent")
        
        workflow.set_entry_point("agent")
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _agent_node_with_monitoring(self, state: ProductionAgentState) -> ProductionAgentState:
        """Agent node with comprehensive monitoring and error tracking"""
        
        start_time = time.time()
        
        try:
            # Update performance metrics
            state["performance_metrics"]["agent_calls"] = state["performance_metrics"].get("agent_calls", 0) + 1
            
            # Build context-aware prompt
            context_prompt = self._build_context_prompt(state)
            
            # Call LLM with timeout
            response = asyncio.wait_for(
                self.llm.ainvoke(context_prompt),
                timeout=self.config.get("llm_timeout", 30)
            )
            
            # Track performance
            execution_time = time.time() - start_time
            state["performance_metrics"]["avg_agent_time"] = self._update_average(
                state["performance_metrics"].get("avg_agent_time", 0),
                execution_time,
                state["performance_metrics"]["agent_calls"]
            )
            
            # Update state
            state["messages"].append(response)
            state["iterations"] += 1
            state["error_state"] = None
            
            return state
            
        except asyncio.TimeoutError:
            state["error_state"] = "agent_timeout"
            return state
        except Exception as e:
            state["error_state"] = f"agent_error: {str(e)}"
            return state
    
    def _tools_node_with_retry(self, state: ProductionAgentState) -> ProductionAgentState:
        """Tools node with retry logic and performance monitoring"""
        
        max_retries = self.config.get("tool_max_retries", 3)
        retry_delay = self.config.get("tool_retry_delay", 1.0)
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                # Extract tool call from last message
                last_message = state["messages"][-1]
                tool_calls = self._extract_tool_calls(last_message)
                
                if not tool_calls:
                    state["current_step"] = "no_tools_needed"
                    return state
                
                # Execute tools with monitoring
                tool_results = []
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    if tool_name in self.tools:
                        result = self.tools[tool_name].run(tool_args)
                        tool_results.append({
                            "tool": tool_name,
                            "result": result,
                            "success": True
                        })
                    else:
                        tool_results.append({
                            "tool": tool_name,
                            "result": f"Tool {tool_name} not found",
                            "success": False
                        })
                
                # Update performance metrics
                execution_time = time.time() - start_time
                state["performance_metrics"]["tool_calls"] = state["performance_metrics"].get("tool_calls", 0) + len(tool_calls)
                state["performance_metrics"]["avg_tool_time"] = self._update_average(
                    state["performance_metrics"].get("avg_tool_time", 0),
                    execution_time,
                    state["performance_metrics"]["tool_calls"]
                )
                
                # Add results to state
                state["context"]["tool_results"] = tool_results
                state["current_step"] = "tools_completed"
                state["error_state"] = None
                
                return state
                
            except Exception as e:
                if attempt == max_retries - 1:
                    state["error_state"] = f"tool_error_max_retries: {str(e)}"
                    return state
                
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
        
        return state
```

---

## Part 2: Performance Optimization & Monitoring (25 minutes)

### Advanced Caching Strategies

🗂️ **File**: `src/session2/performance_optimization.py` - Production performance patterns

```python
from functools import lru_cache, wraps
import redis
import json
import hashlib
import asyncio
from typing import Any, Dict, Optional, Callable
import time
from datetime import datetime, timedelta

class ProductionCacheManager:
    """Multi-layer caching system for LangChain agents"""
    
    def __init__(self, redis_config: Optional[Dict[str, Any]] = None):
        self.redis_client = None
        if redis_config:
            self.redis_client = redis.Redis(**redis_config)
        
        self.memory_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "memory_hits": 0,
            "redis_hits": 0
        }
    
    def cache_with_ttl(self, ttl_seconds: int = 3600, use_redis: bool = True):
        """Decorator for caching function results with TTL"""
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try memory cache first
                cached_result = self._get_from_memory_cache(cache_key)
                if cached_result is not None:
                    self.cache_stats["hits"] += 1
                    self.cache_stats["memory_hits"] += 1
                    return cached_result
                
                # Try Redis cache
                if use_redis and self.redis_client:
                    cached_result = self._get_from_redis_cache(cache_key)
                    if cached_result is not None:
                        # Store in memory cache for faster access
                        self._store_in_memory_cache(cache_key, cached_result, ttl_seconds)
                        self.cache_stats["hits"] += 1
                        self.cache_stats["redis_hits"] += 1
                        return cached_result
                
                # Cache miss - execute function
                self.cache_stats["misses"] += 1
                result = await func(*args, **kwargs)
                
                # Store in caches
                self._store_in_memory_cache(cache_key, result, ttl_seconds)
                if use_redis and self.redis_client:
                    self._store_in_redis_cache(cache_key, result, ttl_seconds)
                
                return result
            
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate deterministic cache key"""
        key_data = {
            "function": func_name,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_from_memory_cache(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        if key in self.memory_cache:
            value, expiry = self.memory_cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self.memory_cache[key]
        return None
    
    def _store_in_memory_cache(self, key: str, value: Any, ttl_seconds: int):
        """Store value in memory cache"""
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self.memory_cache[key] = (value, expiry)
        
        # Cleanup expired entries periodically
        if len(self.memory_cache) % 100 == 0:
            self._cleanup_memory_cache()
    
    def _get_from_redis_cache(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Redis get error: {e}")
        return None
    
    def _store_in_redis_cache(self, key: str, value: Any, ttl_seconds: int):
        """Store value in Redis cache"""
        try:
            self.redis_client.setex(
                key,
                ttl_seconds,
                json.dumps(value, default=str)
            )
        except Exception as e:
            print(f"Redis set error: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_rate_percentage": round(hit_rate, 2),
            "total_requests": total_requests,
            "cache_hits": self.cache_stats["hits"],
            "cache_misses": self.cache_stats["misses"],
            "memory_hits": self.cache_stats["memory_hits"],
            "redis_hits": self.cache_stats["redis_hits"],
            "memory_cache_size": len(self.memory_cache)
        }

class PerformanceOptimizedAgent:
    """LangChain agent with comprehensive performance optimizations"""
    
    def __init__(self, llm, tools: List[BaseTool], performance_config: Dict[str, Any]):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.performance_config = performance_config
        
        # Initialize caching
        self.cache_manager = ProductionCacheManager(
            performance_config.get("redis_config")
        )
        
        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "avg_response_time": 0,
            "llm_calls": 0,
            "tool_calls": 0,
            "cache_hits": 0,
            "errors": 0
        }
        
        # Rate limiting
        self.rate_limiter = self._setup_rate_limiting()
    
    @property
    def cached_llm_call(self):
        """Cached LLM call with performance tracking"""
        return self.cache_manager.cache_with_ttl(
            ttl_seconds=self.performance_config.get("llm_cache_ttl", 3600)
        )(self._execute_llm_call)
    
    async def _execute_llm_call(self, prompt: str, **kwargs) -> str:
        """Execute LLM call with performance monitoring"""
        start_time = time.time()
        
        try:
            response = await self.llm.ainvoke(prompt, **kwargs)
            
            # Update metrics
            execution_time = time.time() - start_time
            self.performance_metrics["llm_calls"] += 1
            self.performance_metrics["avg_response_time"] = self._update_average(
                self.performance_metrics["avg_response_time"],
                execution_time,
                self.performance_metrics["llm_calls"]
            )
            
            return response.content
            
        except Exception as e:
            self.performance_metrics["errors"] += 1
            raise e
    
    async def process_with_optimization(self, message: str) -> Dict[str, Any]:
        """Process message with full performance optimization"""
        
        start_time = time.time()
        self.performance_metrics["total_requests"] += 1
        
        try:
            # Rate limiting check
            if not await self._check_rate_limit():
                return {
                    "error": "Rate limit exceeded",
                    "retry_after": self._get_retry_after()
                }
            
            # Parallel execution of independent operations
            tasks = [
                self._analyze_message_intent(message),
                self._get_relevant_context(message),
                self._check_tool_requirements(message)
            ]
            
            intent_analysis, context, tool_requirements = await asyncio.gather(*tasks)
            
            # Generate response with caching
            response = await self.cached_llm_call(
                self._build_optimized_prompt(message, intent_analysis, context, tool_requirements)
            )
            
            # Execute tools if needed (with parallel execution)
            if tool_requirements["needs_tools"]:
                tool_results = await self._execute_tools_parallel(tool_requirements["tools"])
                
                # Generate final response with tool results
                final_response = await self.cached_llm_call(
                    self._build_final_prompt(message, response, tool_results)
                )
            else:
                final_response = response
            
            # Calculate total processing time
            total_time = time.time() - start_time
            
            return {
                "response": final_response,
                "processing_time": total_time,
                "performance_metrics": self.get_performance_summary(),
                "cache_stats": self.cache_manager.get_cache_stats()
            }
            
        except Exception as e:
            self.performance_metrics["errors"] += 1
            return {
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _execute_tools_parallel(self, tool_specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple tools in parallel for better performance"""
        
        async def execute_single_tool(tool_spec):
            tool_name = tool_spec["name"]
            tool_args = tool_spec["args"]
            
            if tool_name in self.tools:
                try:
                    # Use cached tool execution
                    result = await self._cached_tool_execution(tool_name, tool_args)
                    return {"tool": tool_name, "result": result, "success": True}
                except Exception as e:
                    return {"tool": tool_name, "error": str(e), "success": False}
            else:
                return {"tool": tool_name, "error": "Tool not found", "success": False}
        
        # Execute all tools in parallel
        tool_tasks = [execute_single_tool(spec) for spec in tool_specs]
        results = await asyncio.gather(*tool_tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_results = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_results.append({"error": str(result), "success": False})
            elif result["success"]:
                successful_results.append(result)
            else:
                failed_results.append(result)
        
        self.performance_metrics["tool_calls"] += len(tool_specs)
        
        return {
            "successful": successful_results,
            "failed": failed_results,
            "total_tools": len(tool_specs),
            "success_rate": len(successful_results) / len(tool_specs) if tool_specs else 1.0
        }
    
    async def _cached_tool_execution(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """Execute tool with caching"""
        cache_key = f"tool_{tool_name}_{hashlib.md5(json.dumps(tool_args, sort_keys=True).encode()).hexdigest()}"
        
        # Check cache first
        cached_result = self.cache_manager._get_from_memory_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute tool
        result = self.tools[tool_name].run(tool_args)
        
        # Cache result
        self.cache_manager._store_in_memory_cache(
            cache_key, 
            result, 
            self.performance_config.get("tool_cache_ttl", 1800)
        )
        
        return result
```

---

## Part 3: Enterprise Deployment Architecture (20 minutes)

### High Availability Infrastructure

🗂️ **File**: `src/session2/enterprise_deployment.py` - Enterprise-grade deployment patterns

```python
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import yaml
import json
from datetime import datetime
import prometheus_client
from kubernetes import client, config as k8s_config

@dataclass
class EnterpriseConfig:
    cluster_name: str
    environment: str
    high_availability: bool
    backup_strategy: str
    disaster_recovery: bool
    compliance_level: str
    monitoring_level: str
    security_profile: str

class EnterpriseDeploymentOrchestrator:
    """Enterprise-grade deployment orchestration for LangChain agents"""
    
    def __init__(self, enterprise_config: EnterpriseConfig):
        self.config = enterprise_config
        self.k8s_client = self._initialize_kubernetes_client()
        self.prometheus_registry = prometheus_client.CollectorRegistry()
        self._setup_metrics()
        
    def deploy_enterprise_agent_platform(self, agents_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deploy complete enterprise agent platform"""
        
        deployment_result = {
            "platform_id": f"enterprise-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "environment": self.config.environment,
            "components": {},
            "monitoring": {},
            "security": {},
            "backup": {},
            "status": "deploying"
        }
        
        try:
            # Step 1: Deploy core infrastructure
            infrastructure_result = self._deploy_core_infrastructure()
            deployment_result["components"]["infrastructure"] = infrastructure_result
            
            # Step 2: Deploy monitoring and observability
            monitoring_result = self._deploy_monitoring_stack()
            deployment_result["monitoring"] = monitoring_result
            
            # Step 3: Deploy security components
            security_result = self._deploy_security_stack()
            deployment_result["security"] = security_result
            
            # Step 4: Deploy agent services
            agents_result = self._deploy_agent_services(agents_config)
            deployment_result["components"]["agents"] = agents_result
            
            # Step 5: Configure high availability
            if self.config.high_availability:
                ha_result = self._configure_high_availability()
                deployment_result["components"]["high_availability"] = ha_result
            
            # Step 6: Setup backup and disaster recovery
            backup_result = self._setup_backup_disaster_recovery()
            deployment_result["backup"] = backup_result
            
            # Step 7: Run deployment validation
            validation_result = self._validate_deployment(deployment_result)
            deployment_result["validation"] = validation_result
            
            deployment_result["status"] = "deployed" if validation_result["success"] else "failed"
            
            return deployment_result
            
        except Exception as e:
            deployment_result["status"] = "failed"
            deployment_result["error"] = str(e)
            self._initiate_rollback(deployment_result)
            return deployment_result
    
    def _deploy_core_infrastructure(self) -> Dict[str, Any]:
        """Deploy core infrastructure components"""
        
        infrastructure_manifests = {
            "namespace": self._create_namespace_manifest(),
            "rbac": self._create_rbac_manifests(),
            "network_policies": self._create_network_policy_manifests(),
            "storage": self._create_storage_manifests(),
            "ingress_controller": self._create_ingress_controller_manifest()
        }
        
        deployment_results = {}
        
        for component, manifest in infrastructure_manifests.items():
            try:
                result = self._apply_kubernetes_manifest(manifest)
                deployment_results[component] = {
                    "status": "deployed",
                    "details": result
                }
            except Exception as e:
                deployment_results[component] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return deployment_results
    
    def _deploy_monitoring_stack(self) -> Dict[str, Any]:
        """Deploy comprehensive monitoring and observability"""
        
        monitoring_components = {
            "prometheus": self._deploy_prometheus(),
            "grafana": self._deploy_grafana(),
            "alertmanager": self._deploy_alertmanager(),
            "jaeger": self._deploy_jaeger_tracing(),
            "fluentd": self._deploy_log_aggregation()
        }
        
        # Configure custom dashboards for LangChain agents
        agent_dashboards = self._create_agent_specific_dashboards()
        monitoring_components["agent_dashboards"] = agent_dashboards
        
        # Setup alerting rules
        alerting_rules = self._create_alerting_rules()
        monitoring_components["alerting_rules"] = alerting_rules
        
        return monitoring_components
    
    def _deploy_security_stack(self) -> Dict[str, Any]:
        """Deploy enterprise security components"""
        
        security_components = {
            "pod_security_standards": self._configure_pod_security_standards(),
            "network_segmentation": self._configure_network_segmentation(),
            "secrets_management": self._deploy_secrets_manager(),
            "vulnerability_scanning": self._deploy_vulnerability_scanner(),
            "policy_engine": self._deploy_policy_engine()
        }
        
        # Configure compliance based on requirements
        if self.config.compliance_level in ["SOC2", "HIPAA", "PCI-DSS"]:
            compliance_config = self._configure_compliance_controls()
            security_components["compliance"] = compliance_config
        
        return security_components
    
    def _deploy_agent_services(self, agents_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deploy individual agent services with enterprise patterns"""
        
        agent_deployments = {}
        
        for agent_config in agents_config:
            agent_name = agent_config["name"]
            
            try:
                # Create enterprise-ready deployment
                deployment_manifest = self._create_enterprise_agent_deployment(agent_config)
                
                # Deploy with blue-green strategy
                deployment_result = self._deploy_with_blue_green(deployment_manifest)
                
                # Configure monitoring for this agent
                monitoring_config = self._configure_agent_monitoring(agent_config)
                
                # Setup autoscaling
                autoscaling_config = self._configure_agent_autoscaling(agent_config)
                
                agent_deployments[agent_name] = {
                    "deployment": deployment_result,
                    "monitoring": monitoring_config,
                    "autoscaling": autoscaling_config,
                    "status": "deployed"
                }
                
            except Exception as e:
                agent_deployments[agent_name] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return agent_deployments
    
    def _create_enterprise_agent_deployment(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create enterprise-ready agent deployment manifest"""
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{agent_config['name']}-deployment",
                "labels": {
                    "app": agent_config["name"],
                    "environment": self.config.environment,
                    "tier": "production",
                    "compliance": self.config.compliance_level
                },
                "annotations": {
                    "deployment.kubernetes.io/revision": "1",
                    "security.policy/enforce": "strict",
                    "monitoring.prometheus.io/scrape": "true"
                }
            },
            "spec": {
                "replicas": agent_config.get("replicas", 3),
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": "25%",
                        "maxSurge": "25%"
                    }
                },
                "selector": {
                    "matchLabels": {
                        "app": agent_config["name"],
                        "environment": self.config.environment
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": agent_config["name"],
                            "environment": self.config.environment,
                            "version": agent_config.get("version", "v1")
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": "8080",
                            "prometheus.io/path": "/metrics"
                        }
                    },
                    "spec": {
                        "serviceAccountName": f"{agent_config['name']}-serviceaccount",
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 1000,
                            "fsGroup": 2000,
                            "seccompProfile": {
                                "type": "RuntimeDefault"
                            }
                        },
                        "containers": [{
                            "name": agent_config["name"],
                            "image": agent_config["image"],
                            "imagePullPolicy": "Always",
                            "ports": [
                                {"containerPort": agent_config.get("port", 8000), "name": "http"},
                                {"containerPort": 8080, "name": "metrics"}
                            ],
                            "env": self._create_enterprise_env_vars(agent_config),
                            "resources": {
                                "requests": {
                                    "memory": agent_config.get("memory_request", "1Gi"),
                                    "cpu": agent_config.get("cpu_request", "500m")
                                },
                                "limits": {
                                    "memory": agent_config.get("memory_limit", "2Gi"),
                                    "cpu": agent_config.get("cpu_limit", "1000m")
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": agent_config.get("port", 8000)
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10,
                                "timeoutSeconds": 5,
                                "failureThreshold": 3
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": agent_config.get("port", 8000)
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5,
                                "timeoutSeconds": 3,
                                "failureThreshold": 3
                            },
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "readOnlyRootFilesystem": True,
                                "runAsNonRoot": True,
                                "capabilities": {
                                    "drop": ["ALL"]
                                }
                            },
                            "volumeMounts": [
                                {
                                    "name": "tmp",
                                    "mountPath": "/tmp"
                                },
                                {
                                    "name": "cache",
                                    "mountPath": "/app/cache"
                                }
                            ]
                        }],
                        "volumes": [
                            {
                                "name": "tmp",
                                "emptyDir": {}
                            },
                            {
                                "name": "cache",
                                "emptyDir": {
                                    "sizeLimit": "1Gi"
                                }
                            }
                        ],
                        "affinity": {
                            "podAntiAffinity": {
                                "preferredDuringSchedulingIgnoredDuringExecution": [{
                                    "weight": 100,
                                    "podAffinityTerm": {
                                        "labelSelector": {
                                            "matchExpressions": [{
                                                "key": "app",
                                                "operator": "In",
                                                "values": [agent_config["name"]]
                                            }]
                                        },
                                        "topologyKey": "kubernetes.io/hostname"
                                    }
                                }]
                            }
                        },
                        "tolerations": [
                            {
                                "key": "node.kubernetes.io/not-ready",
                                "operator": "Exists",
                                "effect": "NoExecute",
                                "tolerationSeconds": 300
                            }
                        ]
                    }
                }
            }
        }
```

---

## 🎯 Module Summary

You've now mastered production deployment strategies for LangChain systems:

✅ **LangGraph Integration & Production Patterns**: Built enterprise-ready workflows with automated cloud deployment  
✅ **Performance Optimization & Monitoring**: Implemented multi-layer caching and comprehensive performance tracking  
✅ **Enterprise Deployment Architecture**: Designed high-availability systems with security and compliance features  
✅ **Production Operations**: Created monitoring, alerting, and disaster recovery strategies

### Next Steps
- **Continue to Module C**: [Custom Tool Development](Session2_ModuleC_Custom_Tool_Development.md) for specialized tools
- **Continue to Module D**: [Performance & Monitoring](Session2_ModuleD_Performance_Monitoring.md) for optimization
- **Return to Core**: [Session 2 Main](Session2_LangChain_Foundations.md)
- **Advance to Session 3**: [LangGraph Multi-Agent Workflows](Session3_LangGraph_Multi_Agent_Workflows.md)

---

**🗂️ Source Files for Module B:**
- `src/session2/cloud_deployment.py` - Cloud deployment automation
- `src/session2/performance_optimization.py` - Performance and caching strategies
- `src/session2/enterprise_deployment.py` - Enterprise deployment patterns