"""
Agno Production Deployment Configuration
Session 7: Agno Production-Ready Agents

This module provides comprehensive deployment configurations for Docker, Kubernetes,
and cloud platforms with production-ready security, scaling, and monitoring.
"""

import os
import yaml
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DockerConfig:
    """Docker container configuration"""
    image_name: str = "agno-production"
    image_tag: str = "latest"
    registry: str = "your-registry.com"
    base_image: str = "python:3.11-slim"
    
    # Resource limits
    memory_limit: str = "2Gi"
    cpu_limit: str = "1000m"
    memory_request: str = "1Gi"
    cpu_request: str = "500m"
    
    # Application configuration
    app_port: int = 8000
    health_check_path: str = "/health"
    
    # Environment variables
    environment: Dict[str, str] = field(default_factory=lambda: {
        "ENVIRONMENT": "production",
        "LOG_LEVEL": "INFO",
        "PYTHONPATH": "/app",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "DATABASE_URL": "${DATABASE_URL}",
        "REDIS_URL": "${REDIS_URL}"
    })
    
    # Security settings
    security_context: Dict[str, Any] = field(default_factory=lambda: {
        "run_as_non_root": True,
        "run_as_user": 1000,
        "run_as_group": 1000,
        "read_only_root_filesystem": True,
        "allow_privilege_escalation": False,
        "capabilities": {
            "drop": ["ALL"]
        }
    })

@dataclass
class KubernetesConfig:
    """Kubernetes deployment configuration"""
    namespace: str = "agno-production"
    app_name: str = "agno-agent-service"
    
    # Deployment settings
    replicas: int = 3
    max_surge: str = "25%"
    max_unavailable: str = "0%"
    revision_history_limit: int = 5
    
    # Service configuration
    service_type: str = "ClusterIP"
    service_port: int = 80
    target_port: int = 8000
    
    # Horizontal Pod Autoscaler
    hpa_enabled: bool = True
    min_replicas: int = 3
    max_replicas: int = 50
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    
    # Pod Disruption Budget
    pdb_enabled: bool = True
    min_available: str = "50%"
    
    # Ingress configuration
    ingress_enabled: bool = True
    ingress_class: str = "nginx"
    tls_enabled: bool = True
    domain: str = "agents.your-company.com"
    
    # Storage configuration
    persistent_volume_enabled: bool = True
    storage_class: str = "fast-ssd"
    storage_size: str = "10Gi"

@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    # Prometheus monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    prometheus_path: str = "/metrics"
    
    # Grafana dashboards
    grafana_enabled: bool = True
    
    # Distributed tracing
    jaeger_enabled: bool = True
    jaeger_endpoint: str = "http://jaeger-collector:14268/api/traces"
    
    # Log aggregation
    fluentd_enabled: bool = True
    log_format: str = "json"
    
    # Alerting
    alertmanager_enabled: bool = True
    alert_rules: List[str] = field(default_factory=lambda: [
        "HighErrorRate",
        "HighLatency", 
        "ServiceDown",
        "HighMemoryUsage",
        "HighCPUUsage"
    ])

@dataclass
class SecurityConfig:
    """Security configuration"""
    # RBAC settings
    rbac_enabled: bool = True
    service_account: str = "agno-service-account"
    
    # Network policies
    network_policies_enabled: bool = True
    
    # Pod security policies
    pod_security_standards: str = "restricted"
    
    # Secrets management
    secrets_provider: str = "kubernetes"  # or "vault", "aws-secrets-manager"
    
    # TLS configuration
    tls_cert_manager: bool = True
    cert_issuer: str = "letsencrypt-prod"

class DeploymentConfigGenerator:
    """Generate deployment configurations for various platforms"""
    
    def __init__(self, 
                 docker_config: DockerConfig,
                 k8s_config: KubernetesConfig,
                 monitoring_config: MonitoringConfig,
                 security_config: SecurityConfig):
        self.docker_config = docker_config
        self.k8s_config = k8s_config
        self.monitoring_config = monitoring_config
        self.security_config = security_config
    
    def generate_dockerfile(self) -> str:
        """Generate production Dockerfile"""
        dockerfile_content = f"""# Production Dockerfile for Agno Agent Service
FROM {self.docker_config.base_image}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Create non-root user for security
RUN groupadd -r agno && useradd --no-log-init -r -g agno agno

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY entrypoint.sh ./

# Set proper permissions
RUN chown -R agno:agno /app \\
    && chmod +x entrypoint.sh

# Create required directories
RUN mkdir -p /app/logs /app/tmp \\
    && chown -R agno:agno /app/logs /app/tmp

# Switch to non-root user
USER agno

# Expose application port
EXPOSE {self.docker_config.app_port}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{self.docker_config.app_port}{self.docker_config.health_check_path} || exit 1

# Environment variables
{self._generate_env_vars()}

# Start application
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "-m", "src.main"]
"""
        return dockerfile_content
    
    def generate_docker_compose(self) -> str:
        """Generate Docker Compose configuration for local development"""
        compose_config = {
            "version": "3.8",
            "services": {
                "agno-agent": {
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile"
                    },
                    "image": f"{self.docker_config.registry}/{self.docker_config.image_name}:{self.docker_config.image_tag}",
                    "container_name": "agno-production-agent",
                    "ports": [f"{self.docker_config.app_port}:{self.docker_config.app_port}"],
                    "environment": self.docker_config.environment,
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": self.docker_config.cpu_limit.rstrip('m'),
                                "memory": self.docker_config.memory_limit
                            },
                            "reservations": {
                                "cpus": self.docker_config.cpu_request.rstrip('m'),
                                "memory": self.docker_config.memory_request
                            }
                        }
                    },
                    "healthcheck": {
                        "test": f"curl -f http://localhost:{self.docker_config.app_port}{self.docker_config.health_check_path}",
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "30s"
                    },
                    "restart": "unless-stopped",
                    "depends_on": ["postgres", "redis"]
                },
                "postgres": {
                    "image": "postgres:15-alpine",
                    "container_name": "agno-postgres",
                    "environment": {
                        "POSTGRES_DB": "agno_production",
                        "POSTGRES_USER": "agno_user",
                        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}"
                    },
                    "volumes": [
                        "postgres_data:/var/lib/postgresql/data",
                        "./init.sql:/docker-entrypoint-initdb.d/init.sql"
                    ],
                    "ports": ["5432:5432"],
                    "restart": "unless-stopped"
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "container_name": "agno-redis",
                    "command": "redis-server --appendonly yes",
                    "volumes": ["redis_data:/data"],
                    "ports": ["6379:6379"],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "postgres_data": {},
                "redis_data": {}
            },
            "networks": {
                "default": {
                    "name": "agno-network"
                }
            }
        }
        
        if self.monitoring_config.prometheus_enabled:
            compose_config["services"]["prometheus"] = {
                "image": "prom/prometheus:latest",
                "container_name": "agno-prometheus",
                "ports": ["9090:9090"],
                "volumes": ["./prometheus.yml:/etc/prometheus/prometheus.yml"],
                "restart": "unless-stopped"
            }
        
        if self.monitoring_config.grafana_enabled:
            compose_config["services"]["grafana"] = {
                "image": "grafana/grafana:latest",
                "container_name": "agno-grafana",
                "ports": ["3000:3000"],
                "environment": {
                    "GF_SECURITY_ADMIN_PASSWORD": "${GRAFANA_PASSWORD}"
                },
                "volumes": ["grafana_data:/var/lib/grafana"],
                "restart": "unless-stopped"
            }
            compose_config["volumes"]["grafana_data"] = {}
        
        return yaml.dump(compose_config, default_flow_style=False, sort_keys=False)
    
    def generate_kubernetes_manifests(self) -> Dict[str, str]:
        """Generate complete Kubernetes manifests"""
        manifests = {}
        
        # Namespace
        manifests["namespace.yaml"] = self._generate_namespace()
        
        # Deployment
        manifests["deployment.yaml"] = self._generate_deployment()
        
        # Service
        manifests["service.yaml"] = self._generate_service()
        
        # ConfigMap
        manifests["configmap.yaml"] = self._generate_configmap()
        
        # Secret
        manifests["secret.yaml"] = self._generate_secret()
        
        # ServiceAccount and RBAC
        if self.security_config.rbac_enabled:
            manifests["rbac.yaml"] = self._generate_rbac()
        
        # HorizontalPodAutoscaler
        if self.k8s_config.hpa_enabled:
            manifests["hpa.yaml"] = self._generate_hpa()
        
        # PodDisruptionBudget
        if self.k8s_config.pdb_enabled:
            manifests["pdb.yaml"] = self._generate_pdb()
        
        # Ingress
        if self.k8s_config.ingress_enabled:
            manifests["ingress.yaml"] = self._generate_ingress()
        
        # PersistentVolumeClaim
        if self.k8s_config.persistent_volume_enabled:
            manifests["pvc.yaml"] = self._generate_pvc()
        
        # NetworkPolicy
        if self.security_config.network_policies_enabled:
            manifests["networkpolicy.yaml"] = self._generate_network_policy()
        
        # Monitoring resources
        if self.monitoring_config.prometheus_enabled:
            manifests["servicemonitor.yaml"] = self._generate_service_monitor()
            manifests["prometheusrule.yaml"] = self._generate_prometheus_rules()
        
        return manifests
    
    def _generate_env_vars(self) -> str:
        """Generate environment variables for Dockerfile"""
        env_lines = []
        for key, value in self.docker_config.environment.items():
            env_lines.append(f"ENV {key}={value}")
        return "\\n".join(env_lines)
    
    def _generate_namespace(self) -> str:
        """Generate Kubernetes namespace"""
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.k8s_config.namespace,
                "labels": {
                    "name": self.k8s_config.namespace,
                    "app": self.k8s_config.app_name
                }
            }
        }
        return yaml.dump(namespace, default_flow_style=False)
    
    def _generate_deployment(self) -> str:
        """Generate Kubernetes deployment"""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self.k8s_config.app_name,
                "namespace": self.k8s_config.namespace,
                "labels": {
                    "app": self.k8s_config.app_name,
                    "version": self.docker_config.image_tag
                }
            },
            "spec": {
                "replicas": self.k8s_config.replicas,
                "revisionHistoryLimit": self.k8s_config.revision_history_limit,
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxSurge": self.k8s_config.max_surge,
                        "maxUnavailable": self.k8s_config.max_unavailable
                    }
                },
                "selector": {
                    "matchLabels": {
                        "app": self.k8s_config.app_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": self.k8s_config.app_name,
                            "version": self.docker_config.image_tag
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": str(self.monitoring_config.prometheus_port),
                            "prometheus.io/path": self.monitoring_config.prometheus_path
                        }
                    },
                    "spec": {
                        "serviceAccountName": self.security_config.service_account,
                        "securityContext": {
                            "runAsNonRoot": self.docker_config.security_context["run_as_non_root"],
                            "runAsUser": self.docker_config.security_context["run_as_user"],
                            "runAsGroup": self.docker_config.security_context["run_as_group"],
                            "fsGroup": 2000,
                            "seccompProfile": {
                                "type": "RuntimeDefault"
                            }
                        },
                        "containers": [
                            {
                                "name": "agno-agent",
                                "image": f"{self.docker_config.registry}/{self.docker_config.image_name}:{self.docker_config.image_tag}",
                                "imagePullPolicy": "Always",
                                "ports": [
                                    {"name": "http", "containerPort": self.docker_config.app_port},
                                    {"name": "metrics", "containerPort": self.monitoring_config.prometheus_port}
                                ],
                                "env": [
                                    {"name": key, "valueFrom": {"secretKeyRef": {"name": "agno-secrets", "key": key.lower().replace("_", "-")}}}
                                    if "${" in value else {"name": key, "value": value}
                                    for key, value in self.docker_config.environment.items()
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": self.docker_config.memory_request,
                                        "cpu": self.docker_config.cpu_request
                                    },
                                    "limits": {
                                        "memory": self.docker_config.memory_limit,
                                        "cpu": self.docker_config.cpu_limit
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": self.docker_config.health_check_path,
                                        "port": "http"
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                    "timeoutSeconds": 5,
                                    "successThreshold": 1,
                                    "failureThreshold": 3
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": "http"
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                    "timeoutSeconds": 3,
                                    "successThreshold": 1,
                                    "failureThreshold": 3
                                },
                                "securityContext": {
                                    "allowPrivilegeEscalation": False,
                                    "readOnlyRootFilesystem": True,
                                    "capabilities": {
                                        "drop": ["ALL"]
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        # Add volume mounts if persistent storage is enabled
        if self.k8s_config.persistent_volume_enabled:
            deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] = [
                {
                    "name": "agno-storage",
                    "mountPath": "/app/data"
                }
            ]
            deployment["spec"]["template"]["spec"]["volumes"] = [
                {
                    "name": "agno-storage",
                    "persistentVolumeClaim": {
                        "claimName": f"{self.k8s_config.app_name}-pvc"
                    }
                }
            ]
        
        return yaml.dump(deployment, default_flow_style=False)
    
    def _generate_service(self) -> str:
        """Generate Kubernetes service"""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.k8s_config.app_name}-service",
                "namespace": self.k8s_config.namespace,
                "labels": {
                    "app": self.k8s_config.app_name
                }
            },
            "spec": {
                "type": self.k8s_config.service_type,
                "ports": [
                    {
                        "name": "http",
                        "port": self.k8s_config.service_port,
                        "targetPort": "http",
                        "protocol": "TCP"
                    },
                    {
                        "name": "metrics",
                        "port": self.monitoring_config.prometheus_port,
                        "targetPort": "metrics",
                        "protocol": "TCP"
                    }
                ],
                "selector": {
                    "app": self.k8s_config.app_name
                }
            }
        }
        return yaml.dump(service, default_flow_style=False)
    
    def _generate_configmap(self) -> str:
        """Generate Kubernetes ConfigMap"""
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.k8s_config.app_name}-config",
                "namespace": self.k8s_config.namespace
            },
            "data": {
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "INFO",
                "LOG_FORMAT": self.monitoring_config.log_format,
                "PROMETHEUS_ENABLED": str(self.monitoring_config.prometheus_enabled).lower(),
                "JAEGER_ENDPOINT": self.monitoring_config.jaeger_endpoint if self.monitoring_config.jaeger_enabled else "",
                "APP_PORT": str(self.docker_config.app_port),
                "METRICS_PORT": str(self.monitoring_config.prometheus_port)
            }
        }
        return yaml.dump(configmap, default_flow_style=False)
    
    def _generate_secret(self) -> str:
        """Generate Kubernetes Secret template"""
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "agno-secrets",
                "namespace": self.k8s_config.namespace
            },
            "type": "Opaque",
            "data": {
                # Base64 encoded values - replace with actual values
                "openai-api-key": "base64-encoded-openai-api-key",
                "database-url": "base64-encoded-database-url",
                "redis-url": "base64-encoded-redis-url"
            }
        }
        return yaml.dump(secret, default_flow_style=False)
    
    def _generate_rbac(self) -> str:
        """Generate RBAC configuration"""
        rbac_resources = [
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": self.security_config.service_account,
                    "namespace": self.k8s_config.namespace
                }
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "name": f"{self.k8s_config.app_name}-role"
                },
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["pods", "services", "endpoints"],
                        "verbs": ["get", "list", "watch"]
                    },
                    {
                        "apiGroups": ["apps"],
                        "resources": ["deployments", "replicasets"],
                        "verbs": ["get", "list", "watch"]
                    }
                ]
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "name": f"{self.k8s_config.app_name}-binding"
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": self.security_config.service_account,
                        "namespace": self.k8s_config.namespace
                    }
                ],
                "roleRef": {
                    "kind": "ClusterRole",
                    "name": f"{self.k8s_config.app_name}-role",
                    "apiGroup": "rbac.authorization.k8s.io"
                }
            }
        ]
        
        return yaml.dump_all(rbac_resources, default_flow_style=False)
    
    def _generate_hpa(self) -> str:
        """Generate Horizontal Pod Autoscaler"""
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{self.k8s_config.app_name}-hpa",
                "namespace": self.k8s_config.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": self.k8s_config.app_name
                },
                "minReplicas": self.k8s_config.min_replicas,
                "maxReplicas": self.k8s_config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": self.k8s_config.target_cpu_utilization
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization", 
                                "averageUtilization": self.k8s_config.target_memory_utilization
                            }
                        }
                    }
                ],
                "behavior": {
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 10,
                                "periodSeconds": 60
                            }
                        ]
                    },
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 50,
                                "periodSeconds": 60
                            },
                            {
                                "type": "Pods",
                                "value": 2,
                                "periodSeconds": 60
                            }
                        ]
                    }
                }
            }
        }
        return yaml.dump(hpa, default_flow_style=False)
    
    def _generate_pdb(self) -> str:
        """Generate Pod Disruption Budget"""
        pdb = {
            "apiVersion": "policy/v1",
            "kind": "PodDisruptionBudget",
            "metadata": {
                "name": f"{self.k8s_config.app_name}-pdb",
                "namespace": self.k8s_config.namespace
            },
            "spec": {
                "minAvailable": self.k8s_config.min_available,
                "selector": {
                    "matchLabels": {
                        "app": self.k8s_config.app_name
                    }
                }
            }
        }
        return yaml.dump(pdb, default_flow_style=False)
    
    def _generate_ingress(self) -> str:
        """Generate Ingress configuration"""
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{self.k8s_config.app_name}-ingress",
                "namespace": self.k8s_config.namespace,
                "annotations": {
                    "kubernetes.io/ingress.class": self.k8s_config.ingress_class,
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/force-ssl-redirect": "true"
                }
            },
            "spec": {
                "rules": [
                    {
                        "host": self.k8s_config.domain,
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": f"{self.k8s_config.app_name}-service",
                                            "port": {
                                                "number": self.k8s_config.service_port
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        
        if self.k8s_config.tls_enabled:
            ingress["metadata"]["annotations"]["cert-manager.io/cluster-issuer"] = self.security_config.cert_issuer
            ingress["spec"]["tls"] = [
                {
                    "hosts": [self.k8s_config.domain],
                    "secretName": f"{self.k8s_config.app_name}-tls"
                }
            ]
        
        return yaml.dump(ingress, default_flow_style=False)
    
    def _generate_pvc(self) -> str:
        """Generate PersistentVolumeClaim"""
        pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"{self.k8s_config.app_name}-pvc",
                "namespace": self.k8s_config.namespace
            },
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "storageClassName": self.k8s_config.storage_class,
                "resources": {
                    "requests": {
                        "storage": self.k8s_config.storage_size
                    }
                }
            }
        }
        return yaml.dump(pvc, default_flow_style=False)
    
    def _generate_network_policy(self) -> str:
        """Generate NetworkPolicy"""
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{self.k8s_config.app_name}-netpol",
                "namespace": self.k8s_config.namespace
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "app": self.k8s_config.app_name
                    }
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "name": "ingress-nginx"
                                    }
                                }
                            },
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "name": "monitoring"
                                    }
                                }
                            }
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": self.docker_config.app_port},
                            {"protocol": "TCP", "port": self.monitoring_config.prometheus_port}
                        ]
                    }
                ],
                "egress": [
                    {
                        "to": [],
                        "ports": [
                            {"protocol": "TCP", "port": 80},
                            {"protocol": "TCP", "port": 443},
                            {"protocol": "TCP", "port": 5432},
                            {"protocol": "TCP", "port": 6379}
                        ]
                    }
                ]
            }
        }
        return yaml.dump(network_policy, default_flow_style=False)
    
    def _generate_service_monitor(self) -> str:
        """Generate ServiceMonitor for Prometheus"""
        service_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": f"{self.k8s_config.app_name}-monitor",
                "namespace": self.k8s_config.namespace,
                "labels": {
                    "app": self.k8s_config.app_name
                }
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": self.k8s_config.app_name
                    }
                },
                "endpoints": [
                    {
                        "port": "metrics",
                        "path": self.monitoring_config.prometheus_path,
                        "interval": "30s"
                    }
                ]
            }
        }
        return yaml.dump(service_monitor, default_flow_style=False)
    
    def _generate_prometheus_rules(self) -> str:
        """Generate PrometheusRule for alerting"""
        prometheus_rule = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "PrometheusRule",
            "metadata": {
                "name": f"{self.k8s_config.app_name}-alerts",
                "namespace": self.k8s_config.namespace
            },
            "spec": {
                "groups": [
                    {
                        "name": f"{self.k8s_config.app_name}.rules",
                        "rules": [
                            {
                                "alert": "HighErrorRate",
                                "expr": f"rate(agno_requests_total{{status='error',service='{self.k8s_config.app_name}'}}[5m]) > 0.1",
                                "for": "2m",
                                "labels": {
                                    "severity": "critical"
                                },
                                "annotations": {
                                    "summary": "High error rate detected",
                                    "description": "Error rate is above 10% for {{ $labels.service }}"
                                }
                            },
                            {
                                "alert": "HighLatency",
                                "expr": f"agno_response_time_seconds{{quantile='0.95',service='{self.k8s_config.app_name}'}} > 30",
                                "for": "5m",
                                "labels": {
                                    "severity": "warning"
                                },
                                "annotations": {
                                    "summary": "High latency detected",
                                    "description": "95th percentile latency is above 30 seconds"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        return yaml.dump(prometheus_rule, default_flow_style=False)
    
    def generate_helm_chart(self) -> Dict[str, str]:
        """Generate Helm chart structure"""
        chart_files = {}
        
        # Chart.yaml
        chart_files["Chart.yaml"] = yaml.dump({
            "apiVersion": "v2",
            "name": self.k8s_config.app_name,
            "description": "Agno Production Agent Service Helm Chart",
            "type": "application",
            "version": "0.1.0",
            "appVersion": self.docker_config.image_tag,
            "maintainers": [
                {
                    "name": "Agno Team",
                    "email": "team@agno.com"
                }
            ]
        }, default_flow_style=False)
        
        # values.yaml
        chart_files["values.yaml"] = yaml.dump({
            "image": {
                "repository": f"{self.docker_config.registry}/{self.docker_config.image_name}",
                "tag": self.docker_config.image_tag,
                "pullPolicy": "Always"
            },
            "replicaCount": self.k8s_config.replicas,
            "service": {
                "type": self.k8s_config.service_type,
                "port": self.k8s_config.service_port,
                "targetPort": self.k8s_config.target_port
            },
            "resources": {
                "limits": {
                    "cpu": self.docker_config.cpu_limit,
                    "memory": self.docker_config.memory_limit
                },
                "requests": {
                    "cpu": self.docker_config.cpu_request,
                    "memory": self.docker_config.memory_request
                }
            },
            "autoscaling": {
                "enabled": self.k8s_config.hpa_enabled,
                "minReplicas": self.k8s_config.min_replicas,
                "maxReplicas": self.k8s_config.max_replicas,
                "targetCPUUtilizationPercentage": self.k8s_config.target_cpu_utilization
            },
            "monitoring": {
                "enabled": self.monitoring_config.prometheus_enabled,
                "serviceMonitor": {
                    "enabled": True
                }
            }
        }, default_flow_style=False)
        
        return chart_files
    
    def save_all_configs(self, output_dir: str = "deployment"):
        """Save all deployment configurations to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Docker configurations
        docker_dir = output_path / "docker"
        docker_dir.mkdir(exist_ok=True)
        
        with open(docker_dir / "Dockerfile", "w") as f:
            f.write(self.generate_dockerfile())
        
        with open(docker_dir / "docker-compose.yml", "w") as f:
            f.write(self.generate_docker_compose())
        
        # Kubernetes configurations
        k8s_dir = output_path / "kubernetes"
        k8s_dir.mkdir(exist_ok=True)
        
        k8s_manifests = self.generate_kubernetes_manifests()
        for filename, content in k8s_manifests.items():
            with open(k8s_dir / filename, "w") as f:
                f.write(content)
        
        # Helm chart
        helm_dir = output_path / "helm" / self.k8s_config.app_name
        helm_dir.mkdir(parents=True, exist_ok=True)
        
        helm_files = self.generate_helm_chart()
        for filename, content in helm_files.items():
            with open(helm_dir / filename, "w") as f:
                f.write(content)
        
        logger.info(f"All deployment configurations saved to {output_dir}/")

def demonstrate_deployment_config():
    """Demonstrate deployment configuration generation"""
    print("=" * 80)
    print("AGNO DEPLOYMENT CONFIGURATION DEMONSTRATION")
    print("=" * 80)
    
    # Create configuration objects
    docker_config = DockerConfig(
        image_name="agno-production-agent",
        image_tag="v1.0.0",
        registry="registry.company.com",
        memory_limit="4Gi",
        cpu_limit="2000m"
    )
    
    k8s_config = KubernetesConfig(
        namespace="agno-production",
        app_name="agno-agent-service",
        replicas=5,
        max_replicas=20,
        domain="agents.company.com"
    )
    
    monitoring_config = MonitoringConfig(
        prometheus_enabled=True,
        grafana_enabled=True,
        jaeger_enabled=True,
        alertmanager_enabled=True
    )
    
    security_config = SecurityConfig(
        rbac_enabled=True,
        network_policies_enabled=True,
        pod_security_standards="restricted",
        tls_cert_manager=True
    )
    
    # Create deployment generator
    deployment_gen = DeploymentConfigGenerator(
        docker_config, k8s_config, monitoring_config, security_config
    )
    
    print(f"\n1. Configuration Summary")
    print("-" * 30)
    print(f"Application: {k8s_config.app_name}")
    print(f"Namespace: {k8s_config.namespace}")
    print(f"Image: {docker_config.registry}/{docker_config.image_name}:{docker_config.image_tag}")
    print(f"Replicas: {k8s_config.replicas} (min) to {k8s_config.max_replicas} (max)")
    print(f"Resources: {docker_config.cpu_request}-{docker_config.cpu_limit} CPU, {docker_config.memory_request}-{docker_config.memory_limit} Memory")
    print(f"Domain: {k8s_config.domain}")
    
    print(f"\n2. Feature Configuration")
    print("-" * 30)
    print(f"Monitoring: {'✓' if monitoring_config.prometheus_enabled else '✗'} Prometheus")
    print(f"           {'✓' if monitoring_config.grafana_enabled else '✗'} Grafana")
    print(f"           {'✓' if monitoring_config.jaeger_enabled else '✗'} Jaeger Tracing")
    print(f"Security:   {'✓' if security_config.rbac_enabled else '✗'} RBAC")
    print(f"           {'✓' if security_config.network_policies_enabled else '✗'} Network Policies")
    print(f"           {'✓' if security_config.tls_cert_manager else '✗'} TLS with Cert Manager")
    print(f"Scaling:    {'✓' if k8s_config.hpa_enabled else '✗'} Horizontal Pod Autoscaler")
    print(f"           {'✓' if k8s_config.pdb_enabled else '✗'} Pod Disruption Budget")
    print(f"Storage:    {'✓' if k8s_config.persistent_volume_enabled else '✗'} Persistent Volumes")
    
    print(f"\n3. Generated Configurations")
    print("-" * 35)
    
    # Generate and display sample configurations
    k8s_manifests = deployment_gen.generate_kubernetes_manifests()
    print(f"Kubernetes Manifests: {len(k8s_manifests)} files")
    for filename in sorted(k8s_manifests.keys()):
        print(f"  - {filename}")
    
    helm_files = deployment_gen.generate_helm_chart()
    print(f"Helm Chart Files: {len(helm_files)} files")
    for filename in sorted(helm_files.keys()):
        print(f"  - {filename}")
    
    print(f"\n4. Docker Configuration Sample")
    print("-" * 35)
    dockerfile_lines = deployment_gen.generate_dockerfile().split('\n')
    print("Dockerfile (first 15 lines):")
    for i, line in enumerate(dockerfile_lines[:15], 1):
        print(f"{i:2}: {line}")
    print("...")
    
    print(f"\n5. Kubernetes Deployment Sample")
    print("-" * 40)
    deployment_yaml = deployment_gen._generate_deployment()
    deployment_lines = deployment_yaml.split('\n')
    print("deployment.yaml (first 20 lines):")
    for i, line in enumerate(deployment_lines[:20], 1):
        print(f"{i:2}: {line}")
    print("...")
    
    print(f"\n6. Save All Configurations")
    print("-" * 35)
    
    # Save configurations to files
    deployment_gen.save_all_configs("deployment_demo")
    print("✓ All deployment configurations saved to deployment_demo/")
    print("  - deployment_demo/docker/")
    print("  - deployment_demo/kubernetes/")  
    print("  - deployment_demo/helm/")
    
    print(f"\n" + "=" * 80)
    print("DEPLOYMENT CONFIGURATION DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Deployment Features:")
    print("- Production-ready Docker containers with security best practices")
    print("- Comprehensive Kubernetes manifests with RBAC and Network Policies")
    print("- Horizontal Pod Autoscaling and Pod Disruption Budgets")
    print("- Integrated monitoring with Prometheus and Grafana")
    print("- TLS termination with automated certificate management")
    print("- Helm charts for templated deployments")
    print("- Docker Compose for local development")

if __name__ == "__main__":
    demonstrate_deployment_config()