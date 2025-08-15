# Session 7 - Module B: Enterprise Agent Systems (30 minutes)

**Prerequisites**: [Session 7 Core Section Complete](Session7_First_ADK_Agent.md)  
**Target Audience**: DevOps engineers and enterprise architects building production ADK systems  
**Cognitive Load**: 3 enterprise concepts

---

## 🎯 Module Overview

This module explores production-scale ADK agent deployment including container orchestration, load balancing, monitoring systems, security hardening, and enterprise integration patterns. You'll learn to deploy robust, scalable ADK agents that can handle enterprise workloads with comprehensive observability and security.

### Learning Objectives
By the end of this module, you will:
- Implement containerized ADK agent deployment with Kubernetes orchestration
- Design load balancing and auto-scaling systems for high-availability agent services
- Build comprehensive monitoring and observability systems for production agents
- Create security frameworks for enterprise ADK deployments with compliance requirements

---

## Part 1: Production Deployment Architecture (15 minutes)

### Containerized ADK Agent Deployment

🗂️ **File**: `src/session7/enterprise_deployment.py` - Production deployment patterns

Production ADK agents require sophisticated deployment architectures that can handle enterprise-scale workloads with reliability and security:

```python
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
import json
import os
import yaml
from pathlib import Path
from enum import Enum

class DeploymentStrategy(Enum):
    """ADK agent deployment strategies"""
    BLUE_GREEN = "blue_green"          # Zero-downtime deployments
    ROLLING = "rolling"                # Gradual instance replacement
    CANARY = "canary"                 # Progressive traffic routing
    A_B_TESTING = "ab_testing"        # Split traffic for testing

@dataclass
class ContainerConfiguration:
    """Container configuration for ADK agents"""
    image: str
    tag: str = "latest"
    cpu_request: str = "500m"
    cpu_limit: str = "1000m"
    memory_request: str = "512Mi"
    memory_limit: str = "1Gi"
    environment_variables: Dict[str, str] = field(default_factory=dict)
    secrets: List[str] = field(default_factory=list)
    health_check_path: str = "/health"
    ready_check_path: str = "/ready"
    port: int = 8080

@dataclass
class ServiceConfiguration:
    """Service configuration for ADK agent deployment"""
    service_name: str
    namespace: str = "adk-agents"
    replicas: int = 3
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    deployment_strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    load_balancer_type: str = "Application"  # Application, Network, or Classic

class EnterpriseADKDeployment:
    """Enterprise deployment manager for ADK agents"""
    
    def __init__(self, cluster_config: Dict[str, Any]):
        self.cluster_config = cluster_config
        self.deployment_templates = {}
        self.monitoring_config = {}
        self.security_policies = {}
        self.logger = logging.getLogger(__name__)
        
    def generate_kubernetes_manifests(self, 
                                    container_config: ContainerConfiguration,
                                    service_config: ServiceConfiguration) -> Dict[str, Any]:
        """Generate complete Kubernetes deployment manifests for ADK agents"""
        
        manifests = {
            "deployment": self._create_deployment_manifest(container_config, service_config),
            "service": self._create_service_manifest(service_config),
            "hpa": self._create_hpa_manifest(service_config),
            "ingress": self._create_ingress_manifest(service_config),
            "configmap": self._create_configmap_manifest(container_config, service_config),
            "secret": self._create_secret_manifest(container_config),
            "service_account": self._create_service_account_manifest(service_config),
            "network_policy": self._create_network_policy_manifest(service_config)
        }
        
        return manifests
    
    def _create_deployment_manifest(self, 
                                  container_config: ContainerConfiguration,
                                  service_config: ServiceConfiguration) -> Dict[str, Any]:
        """Create Kubernetes Deployment manifest for ADK agents"""
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": service_config.service_name,
                "namespace": service_config.namespace,
                "labels": {
                    "app": service_config.service_name,
                    "component": "adk-agent",
                    "version": container_config.tag,
                    "managed-by": "adk-deployment-manager"
                }
            },
            "spec": {
                "replicas": service_config.replicas,
                "strategy": {
                    "type": "RollingUpdate" if service_config.deployment_strategy == DeploymentStrategy.ROLLING else "Recreate",
                    "rollingUpdate": {
                        "maxUnavailable": 1,
                        "maxSurge": 1
                    }
                },
                "selector": {
                    "matchLabels": {
                        "app": service_config.service_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_config.service_name,
                            "component": "adk-agent",
                            "version": container_config.tag
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": str(container_config.port),
                            "prometheus.io/path": "/metrics"
                        }
                    },
                    "spec": {
                        "serviceAccountName": f"{service_config.service_name}-sa",
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 1000,
                            "fsGroup": 2000
                        },
                        "containers": [{
                            "name": "adk-agent",
                            "image": f"{container_config.image}:{container_config.tag}",
                            "imagePullPolicy": "Always",
                            "ports": [{
                                "containerPort": container_config.port,
                                "protocol": "TCP"
                            }],
                            "env": [
                                {"name": key, "value": value} 
                                for key, value in container_config.environment_variables.items()
                            ] + [
                                {
                                    "name": "POD_NAME",
                                    "valueFrom": {
                                        "fieldRef": {
                                            "fieldPath": "metadata.name"
                                        }
                                    }
                                },
                                {
                                    "name": "POD_NAMESPACE",
                                    "valueFrom": {
                                        "fieldRef": {
                                            "fieldPath": "metadata.namespace"
                                        }
                                    }
                                }
                            ],
                            "envFrom": [{
                                "configMapRef": {
                                    "name": f"{service_config.service_name}-config"
                                }
                            }, {
                                "secretRef": {
                                    "name": f"{service_config.service_name}-secrets"
                                }
                            }],
                            "resources": {
                                "requests": {
                                    "cpu": container_config.cpu_request,
                                    "memory": container_config.memory_request
                                },
                                "limits": {
                                    "cpu": container_config.cpu_limit,
                                    "memory": container_config.memory_limit
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": container_config.health_check_path,
                                    "port": container_config.port
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10,
                                "timeoutSeconds": 5,
                                "failureThreshold": 3
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": container_config.ready_check_path,
                                    "port": container_config.port
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5,
                                "timeoutSeconds": 3,
                                "failureThreshold": 1
                            },
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "readOnlyRootFilesystem": True,
                                "capabilities": {
                                    "drop": ["ALL"]
                                }
                            }
                        }],
                        "volumes": [{
                            "name": "tmp",
                            "emptyDir": {}
                        }]
                    }
                }
            }
        }
    
    def _create_hpa_manifest(self, service_config: ServiceConfiguration) -> Dict[str, Any]:
        """Create Horizontal Pod Autoscaler manifest"""
        
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{service_config.service_name}-hpa",
                "namespace": service_config.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": service_config.service_name
                },
                "minReplicas": service_config.replicas,
                "maxReplicas": service_config.max_replicas,
                "metrics": [{
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": service_config.target_cpu_utilization
                        }
                    }
                }, {
                    "type": "Resource",
                    "resource": {
                        "name": "memory",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": 80
                        }
                    }
                }],
                "behavior": {
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [{
                            "type": "Percent",
                            "value": 10,
                            "periodSeconds": 60
                        }]
                    },
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [{
                            "type": "Percent",
                            "value": 50,
                            "periodSeconds": 60
                        }]
                    }
                }
            }
        }

class LoadBalancerManager:
    """Manages load balancing and traffic routing for ADK agents"""
    
    def __init__(self, cloud_provider: str = "gcp"):
        self.cloud_provider = cloud_provider
        self.load_balancer_configs = {}
        self.traffic_routing_rules = {}
        self.health_check_configs = {}
        self.logger = logging.getLogger(__name__)
        
    def create_application_load_balancer(self, 
                                       service_name: str,
                                       target_groups: List[Dict[str, Any]],
                                       routing_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create application load balancer configuration for ADK agents"""
        
        lb_config = {
            "load_balancer": {
                "name": f"{service_name}-alb",
                "type": "application",
                "scheme": "internet-facing",
                "security_groups": [f"{service_name}-lb-sg"],
                "subnets": ["subnet-public-1", "subnet-public-2"],
                "tags": {
                    "Environment": "production",
                    "Service": service_name,
                    "ManagedBy": "adk-deployment"
                }
            },
            "listeners": [{
                "port": 443,
                "protocol": "HTTPS",
                "ssl_policy": "ELBSecurityPolicy-TLS-1-2-2019-07",
                "certificate_arn": f"arn:aws:acm:region:account:certificate/{service_name}",
                "default_actions": [{
                    "type": "forward",
                    "target_group_arn": target_groups[0]["arn"]
                }],
                "rules": routing_rules
            }, {
                "port": 80,
                "protocol": "HTTP",
                "default_actions": [{
                    "type": "redirect",
                    "redirect_config": {
                        "protocol": "HTTPS",
                        "port": "443",
                        "status_code": "HTTP_301"
                    }
                }]
            }],
            "target_groups": target_groups
        }
        
        self.load_balancer_configs[service_name] = lb_config
        return lb_config
    
    def create_canary_deployment_routing(self, 
                                       service_name: str,
                                       stable_weight: int = 90,
                                       canary_weight: int = 10) -> Dict[str, Any]:
        """Create canary deployment traffic routing configuration"""
        
        canary_config = {
            "routing_strategy": "weighted",
            "total_weight": 100,
            "targets": [{
                "target_group": f"{service_name}-stable",
                "weight": stable_weight,
                "version": "stable",
                "health_check": {
                    "path": "/health",
                    "interval": 30,
                    "timeout": 5,
                    "healthy_threshold": 2,
                    "unhealthy_threshold": 3
                }
            }, {
                "target_group": f"{service_name}-canary",
                "weight": canary_weight,
                "version": "canary",
                "health_check": {
                    "path": "/health",
                    "interval": 30,
                    "timeout": 5,
                    "healthy_threshold": 2,
                    "unhealthy_threshold": 3
                }
            }],
            "monitoring": {
                "success_rate_threshold": 99.0,
                "error_rate_threshold": 1.0,
                "response_time_threshold_ms": 500,
                "minimum_traffic_sample": 100
            },
            "automation": {
                "promote_on_success": True,
                "rollback_on_failure": True,
                "evaluation_duration_minutes": 30,
                "promotion_criteria": {
                    "success_rate_min": 99.5,
                    "error_rate_max": 0.5,
                    "response_time_p95_max": 300
                }
            }
        }
        
        return canary_config

class EnterpriseMonitoring:
    """Comprehensive monitoring system for production ADK agents"""
    
    def __init__(self, monitoring_stack: str = "prometheus"):
        self.monitoring_stack = monitoring_stack
        self.metric_definitions = {}
        self.alert_rules = {}
        self.dashboard_configs = {}
        self.logger = logging.getLogger(__name__)
        
    def setup_agent_metrics(self) -> Dict[str, Any]:
        """Define comprehensive metrics collection for ADK agents"""
        
        metrics_config = {
            "application_metrics": {
                "adk_agent_requests_total": {
                    "type": "counter",
                    "description": "Total number of requests processed by ADK agent",
                    "labels": ["agent_id", "method", "endpoint", "status_code"]
                },
                "adk_agent_request_duration_seconds": {
                    "type": "histogram",
                    "description": "Request duration in seconds",
                    "labels": ["agent_id", "method", "endpoint"],
                    "buckets": [0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
                },
                "adk_agent_active_conversations": {
                    "type": "gauge",
                    "description": "Number of active conversations",
                    "labels": ["agent_id"]
                },
                "adk_agent_memory_usage_bytes": {
                    "type": "gauge",
                    "description": "Memory usage by conversation memory system",
                    "labels": ["agent_id", "memory_type"]
                },
                "adk_agent_mcp_calls_total": {
                    "type": "counter",
                    "description": "Total MCP server calls",
                    "labels": ["agent_id", "mcp_server", "method", "status"]
                },
                "adk_agent_mcp_call_duration_seconds": {
                    "type": "histogram",
                    "description": "MCP call duration in seconds",
                    "labels": ["agent_id", "mcp_server", "method"],
                    "buckets": [0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
                }
            },
            "infrastructure_metrics": {
                "adk_container_cpu_usage_percent": {
                    "type": "gauge",
                    "description": "Container CPU usage percentage",
                    "labels": ["pod_name", "container_name"]
                },
                "adk_container_memory_usage_bytes": {
                    "type": "gauge",
                    "description": "Container memory usage in bytes",
                    "labels": ["pod_name", "container_name"]
                },
                "adk_container_restarts_total": {
                    "type": "counter",
                    "description": "Total container restarts",
                    "labels": ["pod_name", "container_name"]
                }
            },
            "business_metrics": {
                "adk_successful_interactions_total": {
                    "type": "counter",
                    "description": "Total successful user interactions",
                    "labels": ["agent_id", "interaction_type"]
                },
                "adk_user_satisfaction_score": {
                    "type": "gauge",
                    "description": "User satisfaction score",
                    "labels": ["agent_id"]
                },
                "adk_cost_per_interaction": {
                    "type": "gauge",
                    "description": "Cost per user interaction in dollars",
                    "labels": ["agent_id", "cost_center"]
                }
            }
        }
        
        self.metric_definitions = metrics_config
        return metrics_config
    
    def create_alerting_rules(self) -> List[Dict[str, Any]]:
        """Create comprehensive alerting rules for ADK agents"""
        
        alert_rules = [
            {
                "alert": "ADKAgentHighErrorRate",
                "expr": 'rate(adk_agent_requests_total{status_code=~"5.."}[5m]) / rate(adk_agent_requests_total[5m]) > 0.05',
                "for": "2m",
                "labels": {
                    "severity": "critical",
                    "component": "adk-agent"
                },
                "annotations": {
                    "summary": "ADK Agent {{ $labels.agent_id }} has high error rate",
                    "description": "ADK Agent {{ $labels.agent_id }} error rate is {{ $value | humanizePercentage }} which is above 5% threshold"
                }
            },
            {
                "alert": "ADKAgentHighLatency",
                "expr": 'histogram_quantile(0.95, rate(adk_agent_request_duration_seconds_bucket[5m])) > 2',
                "for": "5m",
                "labels": {
                    "severity": "warning",
                    "component": "adk-agent"
                },
                "annotations": {
                    "summary": "ADK Agent {{ $labels.agent_id }} has high latency",
                    "description": "ADK Agent {{ $labels.agent_id }} 95th percentile latency is {{ $value }}s which is above 2s threshold"
                }
            },
            {
                "alert": "ADKAgentMCPCallFailures",
                "expr": 'rate(adk_agent_mcp_calls_total{status="error"}[5m]) > 0.1',
                "for": "3m",
                "labels": {
                    "severity": "warning",
                    "component": "adk-agent"
                },
                "annotations": {
                    "summary": "ADK Agent {{ $labels.agent_id }} has high MCP call failure rate",
                    "description": "ADK Agent {{ $labels.agent_id }} MCP calls to {{ $labels.mcp_server }} are failing at {{ $value }} calls per second"
                }
            },
            {
                "alert": "ADKAgentMemoryLeak",
                "expr": 'increase(adk_agent_memory_usage_bytes[30m]) > 104857600',  # 100MB increase
                "for": "10m",
                "labels": {
                    "severity": "warning",
                    "component": "adk-agent"
                },
                "annotations": {
                    "summary": "Potential memory leak in ADK Agent {{ $labels.agent_id }}",
                    "description": "ADK Agent {{ $labels.agent_id }} memory usage has increased by {{ $value | humanizeBytes }} in the last 30 minutes"
                }
            },
            {
                "alert": "ADKContainerCPUThrottling",
                "expr": 'adk_container_cpu_usage_percent > 90',
                "for": "10m",
                "labels": {
                    "severity": "warning",
                    "component": "adk-container"
                },
                "annotations": {
                    "summary": "ADK Container {{ $labels.pod_name }} is experiencing CPU throttling",
                    "description": "Container {{ $labels.container_name }} in pod {{ $labels.pod_name }} has been using {{ $value }}% CPU for more than 10 minutes"
                }
            }
        ]
        
        self.alert_rules = alert_rules
        return alert_rules

class SecurityManager:
    """Enterprise security management for ADK agent deployments"""
    
    def __init__(self):
        self.security_policies = {}
        self.compliance_frameworks = ["SOC2", "GDPR", "HIPAA", "PCI-DSS"]
        self.encryption_configs = {}
        self.access_control_policies = {}
        self.logger = logging.getLogger(__name__)
        
    def create_security_policies(self) -> Dict[str, Any]:
        """Create comprehensive security policies for ADK agents"""
        
        security_config = {
            "network_policies": {
                "default_deny": True,
                "ingress_rules": [
                    {
                        "description": "Allow ingress from load balancer",
                        "ports": [{"protocol": "TCP", "port": 8080}],
                        "sources": [{"namespaceSelector": {"matchLabels": {"name": "ingress-nginx"}}}]
                    },
                    {
                        "description": "Allow ingress from monitoring",
                        "ports": [{"protocol": "TCP", "port": 9090}],
                        "sources": [{"namespaceSelector": {"matchLabels": {"name": "monitoring"}}}]
                    }
                ],
                "egress_rules": [
                    {
                        "description": "Allow DNS resolution",
                        "ports": [{"protocol": "UDP", "port": 53}],
                        "destinations": [{"namespaceSelector": {"matchLabels": {"name": "kube-system"}}}]
                    },
                    {
                        "description": "Allow HTTPS to external APIs",
                        "ports": [{"protocol": "TCP", "port": 443}],
                        "destinations": [{}]  # Allow all external HTTPS
                    }
                ]
            },
            "pod_security_standards": {
                "security_context": {
                    "runAsNonRoot": True,
                    "runAsUser": 1000,
                    "runAsGroup": 2000,
                    "fsGroup": 2000,
                    "seccompProfile": {
                        "type": "RuntimeDefault"
                    }
                },
                "container_security": {
                    "allowPrivilegeEscalation": False,
                    "readOnlyRootFilesystem": True,
                    "capabilities": {
                        "drop": ["ALL"]
                    }
                }
            },
            "secrets_management": {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "secret_rotation": {
                    "enabled": True,
                    "rotation_period_days": 90
                },
                "secret_scanning": {
                    "enabled": True,
                    "scan_frequency": "daily"
                }
            },
            "compliance_controls": {
                "audit_logging": {
                    "enabled": True,
                    "retention_days": 365,
                    "log_level": "INFO"
                },
                "data_classification": {
                    "enabled": True,
                    "classification_levels": ["public", "internal", "confidential", "restricted"]
                },
                "access_controls": {
                    "rbac_enabled": True,
                    "service_account_tokens": False,
                    "pod_security_admission": "enforce"
                }
            }
        }
        
        return security_config
```

---

## Part 2: Advanced Monitoring and Observability (15 minutes)

### Production Observability Stack

🗂️ **File**: `src/session7/observability_stack.py` - Comprehensive monitoring systems

```python
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import json

class DistributedTracingManager:
    """Manages distributed tracing for ADK agent interactions"""
    
    def __init__(self, tracing_backend: str = "jaeger"):
        self.tracing_backend = tracing_backend
        self.trace_configs = {}
        self.sampling_strategies = {}
        self.logger = logging.getLogger(__name__)
        
    def configure_tracing(self, service_name: str) -> Dict[str, Any]:
        """Configure distributed tracing for ADK agent service"""
        
        tracing_config = {
            "service_name": service_name,
            "tracing_backend": self.tracing_backend,
            "sampling_strategy": {
                "type": "probabilistic",
                "param": 0.1  # Sample 10% of traces
            },
            "span_attributes": {
                "service.name": service_name,
                "service.version": "1.0.0",
                "deployment.environment": "production"
            },
            "instrumentation": {
                "http_requests": True,
                "database_calls": True,
                "external_apis": True,
                "mcp_calls": True,
                "conversation_flows": True
            },
            "exporters": [{
                "type": "jaeger",
                "endpoint": "http://jaeger-collector:14268/api/traces",
                "headers": {
                    "X-Service-Name": service_name
                }
            }, {
                "type": "console",
                "enabled": False  # Disable for production
            }]
        }
        
        return tracing_config

class LogAggregationManager:
    """Manages centralized logging for ADK agent systems"""
    
    def __init__(self, log_backend: str = "elasticsearch"):
        self.log_backend = log_backend
        self.log_configs = {}
        self.retention_policies = {}
        self.logger = logging.getLogger(__name__)
        
    def configure_structured_logging(self, service_name: str) -> Dict[str, Any]:
        """Configure structured logging for ADK agents"""
        
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
                },
                "detailed": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "json",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "detailed",
                    "filename": f"/var/log/{service_name}.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                },
                "fluentd": {
                    "class": "fluent.handler.FluentHandler",
                    "level": "INFO",
                    "formatter": "json",
                    "tag": f"adk.{service_name}",
                    "host": "fluentd-service",
                    "port": 24224
                }
            },
            "loggers": {
                service_name: {
                    "level": "INFO",
                    "handlers": ["console", "fluentd"],
                    "propagate": False
                },
                "adk.agents": {
                    "level": "DEBUG",
                    "handlers": ["console", "file", "fluentd"],
                    "propagate": False
                },
                "adk.mcp": {
                    "level": "INFO",
                    "handlers": ["console", "fluentd"],
                    "propagate": False
                }
            },
            "root": {
                "level": "WARNING",
                "handlers": ["console"]
            }
        }
        
        return logging_config

class SLOManager:
    """Manages Service Level Objectives for ADK agents"""
    
    def __init__(self):
        self.slo_definitions = {}
        self.sli_queries = {}
        self.error_budgets = {}
        self.logger = logging.getLogger(__name__)
        
    def define_agent_slos(self, service_name: str) -> Dict[str, Any]:
        """Define comprehensive SLOs for ADK agent service"""
        
        slo_config = {
            "service_name": service_name,
            "slo_period_days": 30,
            "objectives": [
                {
                    "name": "availability",
                    "description": "ADK agent service availability",
                    "target": 99.9,  # 99.9% availability
                    "sli_query": f'avg_over_time(up{{job="{service_name}"}}[5m])',
                    "error_budget_minutes": 43.2  # 0.1% of 30 days
                },
                {
                    "name": "latency",
                    "description": "95th percentile response time under 500ms",
                    "target": 95.0,  # 95% of requests under 500ms
                    "sli_query": f'histogram_quantile(0.95, rate(adk_agent_request_duration_seconds_bucket{{service="{service_name}"}}[5m])) < 0.5',
                    "error_budget_requests": 5.0  # 5% error budget
                },
                {
                    "name": "quality",
                    "description": "Request success rate",
                    "target": 99.5,  # 99.5% success rate
                    "sli_query": f'rate(adk_agent_requests_total{{service="{service_name}",status_code!~"5.."}}[5m]) / rate(adk_agent_requests_total{{service="{service_name}"}}[5m])',
                    "error_budget_requests": 0.5  # 0.5% error budget
                },
                {
                    "name": "user_satisfaction",
                    "description": "User satisfaction score above 4.0",
                    "target": 90.0,  # 90% of users rate > 4.0
                    "sli_query": f'avg_over_time(adk_user_satisfaction_score{{service="{service_name}"}}[1h]) > 4.0',
                    "error_budget_satisfaction": 10.0  # 10% can be below threshold
                }
            ],
            "alerting": {
                "burn_rate_alerts": [
                    {
                        "alert_name": f"{service_name}_ErrorBudgetBurn_Fast",
                        "burn_rate_threshold": 14.4,  # 2% in 1 hour
                        "lookback_window": "1h",
                        "severity": "critical"
                    },
                    {
                        "alert_name": f"{service_name}_ErrorBudgetBurn_Slow",
                        "burn_rate_threshold": 6.0,  # 5% in 6 hours
                        "lookback_window": "6h",
                        "severity": "warning"
                    }
                ]
            }
        }
        
        return slo_config
```

---

## 🎯 Module Summary

You've now mastered enterprise-scale ADK agent deployment:

✅ **Production Deployment**: Implemented containerized deployment with Kubernetes orchestration and auto-scaling  
✅ **Load Balancing**: Built sophisticated traffic routing with canary deployments and health monitoring  
✅ **Security Framework**: Created comprehensive security policies with compliance controls  
✅ **Observability Stack**: Designed distributed tracing, structured logging, and SLO management systems

### Next Steps
- **Return to Core**: [Session 7 Main](Session7_First_ADK_Agent.md)
- **Advance to Session 8**: [Agno Production Ready Agents](Session8_Agno_Production_Ready_Agents.md)
- **Compare with Module A**: [Advanced ADK Integration](Session7_ModuleA_Advanced_ADK_Integration.md)

---

**🗂️ Source Files for Module B:**
- `src/session7/enterprise_deployment.py` - Production deployment systems
- `src/session7/observability_stack.py` - Comprehensive monitoring
- `src/session7/security_manager.py` - Enterprise security controls