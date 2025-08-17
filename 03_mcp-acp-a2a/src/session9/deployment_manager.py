"""
Production Deployment Manager - Session 9
Manages deployment of agent systems to production environments.
"""

import asyncio
import json
import yaml
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import logging
import hashlib
import base64

logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Deployment strategies."""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"


class DeploymentStatus(Enum):
    """Deployment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


@dataclass
class ContainerImage:
    """Container image configuration."""
    registry: str
    repository: str
    tag: str
    pull_policy: str = "IfNotPresent"
    
    @property
    def full_name(self) -> str:
        return f"{self.registry}/{self.repository}:{self.tag}"


@dataclass
class ResourceLimits:
    """Resource limits and requests."""
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"
    storage_request: str = "1Gi"


@dataclass
class ServiceConfig:
    """Service configuration."""
    name: str
    port: int
    target_port: int
    service_type: str = "ClusterIP"  # ClusterIP, NodePort, LoadBalancer
    protocol: str = "TCP"


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    name: str
    namespace: str
    replicas: int
    image: ContainerImage
    resources: ResourceLimits
    services: List[ServiceConfig]
    
    # Configuration
    environment_variables: Dict[str, str] = field(default_factory=dict)
    config_maps: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    
    # Deployment strategy
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE
    max_unavailable: str = "25%"
    max_surge: str = "25%"
    
    # Health checks
    readiness_probe_path: str = "/health/ready"
    liveness_probe_path: str = "/health/alive"
    startup_probe_path: str = "/health/startup"
    
    # Labels and annotations
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class DeploymentResult:
    """Result of deployment operation."""
    deployment_id: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Details
    deployed_resources: List[str] = field(default_factory=list)
    error_message: str = ""
    rollback_info: Optional[Dict[str, Any]] = None
    
    # Metrics
    deployment_duration: Optional[float] = None
    resources_created: int = 0
    resources_updated: int = 0


class KubernetesClient:
    """Simplified Kubernetes client for deployment operations."""
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        self.kubeconfig_path = kubeconfig_path
        self.kubectl_command = ["kubectl"]
        
        if kubeconfig_path:
            self.kubectl_command.extend(["--kubeconfig", kubeconfig_path])
    
    async def apply_resource(self, resource_yaml: str, namespace: Optional[str] = None) -> Tuple[bool, str]:
        """Apply a Kubernetes resource."""
        cmd = self.kubectl_command + ["apply", "-f", "-"]
        if namespace:
            cmd.extend(["-n", namespace])
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=resource_yaml.encode())
            
            if process.returncode == 0:
                return True, stdout.decode()
            else:
                return False, stderr.decode()
        
        except Exception as e:
            return False, str(e)
    
    async def delete_resource(self, resource_type: str, name: str, namespace: str) -> Tuple[bool, str]:
        """Delete a Kubernetes resource."""
        cmd = self.kubectl_command + ["delete", resource_type, name, "-n", namespace]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return True, stdout.decode()
            else:
                return False, stderr.decode()
        
        except Exception as e:
            return False, str(e)
    
    async def get_resource(self, resource_type: str, name: str, namespace: str) -> Tuple[bool, Dict[str, Any]]:
        """Get a Kubernetes resource."""
        cmd = self.kubectl_command + ["get", resource_type, name, "-n", namespace, "-o", "json"]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                resource_data = json.loads(stdout.decode())
                return True, resource_data
            else:
                return False, {"error": stderr.decode()}
        
        except Exception as e:
            return False, {"error": str(e)}
    
    async def wait_for_deployment(self, name: str, namespace: str, timeout: int = 300) -> bool:
        """Wait for deployment to be ready."""
        cmd = self.kubectl_command + [
            "wait", "--for=condition=available", f"deployment/{name}",
            "-n", namespace, f"--timeout={timeout}s"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
        
        except Exception as e:
            logger.error(f"Error waiting for deployment: {str(e)}")
            return False


class YAMLGenerator:
    """Generates Kubernetes YAML manifests."""
    
    def __init__(self):
        self.api_version_mappings = {
            "Deployment": "apps/v1",
            "Service": "v1",
            "ConfigMap": "v1",
            "Secret": "v1",
            "Namespace": "v1",
            "HorizontalPodAutoscaler": "autoscaling/v2",
            "NetworkPolicy": "networking.k8s.io/v1"
        }
    
    def generate_namespace(self, name: str, labels: Dict[str, str] = None) -> str:
        """Generate namespace YAML."""
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": name,
                "labels": labels or {"name": name}
            }
        }
        return yaml.dump(namespace, default_flow_style=False)
    
    def generate_deployment(self, config: DeploymentConfig) -> str:
        """Generate deployment YAML."""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
                "labels": {
                    "app": config.name,
                    **config.labels
                },
                "annotations": config.annotations
            },
            "spec": {
                "replicas": config.replicas,
                "strategy": self._get_deployment_strategy(config),
                "selector": {
                    "matchLabels": {
                        "app": config.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.name,
                            **config.labels
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": config.name,
                            "image": config.image.full_name,
                            "imagePullPolicy": config.image.pull_policy,
                            "ports": [
                                {"containerPort": service.target_port}
                                for service in config.services
                            ],
                            "env": [
                                {"name": key, "value": value}
                                for key, value in config.environment_variables.items()
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": config.resources.cpu_request,
                                    "memory": config.resources.memory_request
                                },
                                "limits": {
                                    "cpu": config.resources.cpu_limit,
                                    "memory": config.resources.memory_limit
                                }
                            },
                            "readinessProbe": self._generate_probe(
                                config.readiness_probe_path, 
                                config.services[0].target_port if config.services else 8080
                            ),
                            "livenessProbe": self._generate_probe(
                                config.liveness_probe_path,
                                config.services[0].target_port if config.services else 8080
                            ),
                            "startupProbe": self._generate_probe(
                                config.startup_probe_path,
                                config.services[0].target_port if config.services else 8080,
                                initial_delay=10,
                                period=10,
                                failure_threshold=30
                            )
                        }]
                    }
                }
            }
        }
        
        # Add config map and secret volume mounts
        if config.config_maps or config.secrets:
            volumes = []
            volume_mounts = []
            
            for config_map in config.config_maps:
                volumes.append({
                    "name": f"{config_map}-volume",
                    "configMap": {"name": config_map}
                })
                volume_mounts.append({
                    "name": f"{config_map}-volume",
                    "mountPath": f"/etc/config/{config_map}"
                })
            
            for secret in config.secrets:
                volumes.append({
                    "name": f"{secret}-volume",
                    "secret": {"secretName": secret}
                })
                volume_mounts.append({
                    "name": f"{secret}-volume",
                    "mountPath": f"/etc/secrets/{secret}"
                })
            
            deployment["spec"]["template"]["spec"]["volumes"] = volumes
            deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] = volume_mounts
        
        return yaml.dump(deployment, default_flow_style=False)
    
    def generate_service(self, config: DeploymentConfig) -> str:
        """Generate service YAML for each service in the config."""
        services_yaml = []
        
        for service in config.services:
            service_manifest = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": service.name,
                    "namespace": config.namespace,
                    "labels": {
                        "app": config.name,
                        **config.labels
                    }
                },
                "spec": {
                    "type": service.service_type,
                    "selector": {
                        "app": config.name
                    },
                    "ports": [{
                        "name": f"{service.name}-port",
                        "port": service.port,
                        "targetPort": service.target_port,
                        "protocol": service.protocol
                    }]
                }
            }
            services_yaml.append(yaml.dump(service_manifest, default_flow_style=False))
        
        return "---\n".join(services_yaml)
    
    def generate_hpa(self, config: DeploymentConfig, min_replicas: int = 1, 
                    max_replicas: int = 10, cpu_threshold: int = 70) -> str:
        """Generate Horizontal Pod Autoscaler YAML."""
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{config.name}-hpa",
                "namespace": config.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": config.name
                },
                "minReplicas": min_replicas,
                "maxReplicas": max_replicas,
                "metrics": [{
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": cpu_threshold
                        }
                    }
                }]
            }
        }
        return yaml.dump(hpa, default_flow_style=False)
    
    def generate_network_policy(self, config: DeploymentConfig, 
                               allowed_ingress: List[Dict[str, Any]] = None,
                               allowed_egress: List[Dict[str, Any]] = None) -> str:
        """Generate NetworkPolicy YAML."""
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{config.name}-network-policy",
                "namespace": config.namespace
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "app": config.name
                    }
                },
                "policyTypes": []
            }
        }
        
        if allowed_ingress:
            network_policy["spec"]["policyTypes"].append("Ingress")
            network_policy["spec"]["ingress"] = allowed_ingress
        
        if allowed_egress:
            network_policy["spec"]["policyTypes"].append("Egress")
            network_policy["spec"]["egress"] = allowed_egress
        
        return yaml.dump(network_policy, default_flow_style=False)
    
    def _get_deployment_strategy(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Get deployment strategy configuration."""
        if config.strategy == DeploymentStrategy.ROLLING_UPDATE:
            return {
                "type": "RollingUpdate",
                "rollingUpdate": {
                    "maxUnavailable": config.max_unavailable,
                    "maxSurge": config.max_surge
                }
            }
        elif config.strategy == DeploymentStrategy.RECREATE:
            return {"type": "Recreate"}
        else:
            # Default to rolling update for other strategies
            return {
                "type": "RollingUpdate",
                "rollingUpdate": {
                    "maxUnavailable": config.max_unavailable,
                    "maxSurge": config.max_surge
                }
            }
    
    def _generate_probe(self, path: str, port: int, initial_delay: int = 5,
                       period: int = 10, timeout: int = 5,
                       success_threshold: int = 1, failure_threshold: int = 3) -> Dict[str, Any]:
        """Generate probe configuration."""
        return {
            "httpGet": {
                "path": path,
                "port": port
            },
            "initialDelaySeconds": initial_delay,
            "periodSeconds": period,
            "timeoutSeconds": timeout,
            "successThreshold": success_threshold,
            "failureThreshold": failure_threshold
        }


class ProductionDeploymentManager:
    """Manages production deployments of agent systems."""
    
    def __init__(self, kubernetes_client: Optional[KubernetesClient] = None):
        self.k8s_client = kubernetes_client or KubernetesClient()
        self.yaml_generator = YAMLGenerator()
        self.deployment_history: Dict[str, DeploymentResult] = {}
        self.active_deployments: Dict[str, DeploymentConfig] = {}
    
    async def deploy(self, config: DeploymentConfig, 
                    create_namespace: bool = True,
                    enable_autoscaling: bool = True,
                    enable_network_policy: bool = True) -> DeploymentResult:
        """Deploy an agent system to production."""
        deployment_id = self._generate_deployment_id(config)
        start_time = datetime.now()
        
        result = DeploymentResult(
            deployment_id=deployment_id,
            status=DeploymentStatus.PENDING,
            start_time=start_time
        )
        
        self.deployment_history[deployment_id] = result
        
        try:
            logger.info(f"Starting deployment {deployment_id} for {config.name}")
            result.status = DeploymentStatus.IN_PROGRESS
            
            # Step 1: Create namespace if needed
            if create_namespace:
                await self._create_namespace(config.namespace, result)
            
            # Step 2: Deploy core resources
            await self._deploy_core_resources(config, result)
            
            # Step 3: Deploy services
            await self._deploy_services(config, result)
            
            # Step 4: Enable autoscaling if requested
            if enable_autoscaling:
                await self._deploy_autoscaling(config, result)
            
            # Step 5: Create network policies if requested
            if enable_network_policy:
                await self._deploy_network_policy(config, result)
            
            # Step 6: Wait for deployment to be ready
            await self._wait_for_deployment_ready(config, result)
            
            # Success
            result.status = DeploymentStatus.COMPLETED
            result.end_time = datetime.now()
            result.deployment_duration = (result.end_time - result.start_time).total_seconds()
            
            self.active_deployments[deployment_id] = config
            
            logger.info(f"Deployment {deployment_id} completed successfully")
            
        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()
            
            logger.error(f"Deployment {deployment_id} failed: {str(e)}")
            
            # Attempt rollback
            await self._rollback_deployment(config, result)
        
        return result
    
    async def rollback(self, deployment_id: str) -> DeploymentResult:
        """Rollback a deployment to previous version."""
        if deployment_id not in self.deployment_history:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        original_result = self.deployment_history[deployment_id]
        config = self.active_deployments.get(deployment_id)
        
        if not config:
            raise ValueError(f"Active deployment configuration not found for {deployment_id}")
        
        rollback_result = DeploymentResult(
            deployment_id=f"{deployment_id}-rollback",
            status=DeploymentStatus.ROLLING_BACK,
            start_time=datetime.now()
        )
        
        try:
            await self._rollback_deployment(config, rollback_result)
            rollback_result.status = DeploymentStatus.ROLLED_BACK
            rollback_result.end_time = datetime.now()
            
        except Exception as e:
            rollback_result.status = DeploymentStatus.FAILED
            rollback_result.error_message = str(e)
            rollback_result.end_time = datetime.now()
        
        return rollback_result
    
    async def scale_deployment(self, deployment_id: str, replicas: int) -> bool:
        """Scale a deployment to specified number of replicas."""
        if deployment_id not in self.active_deployments:
            return False
        
        config = self.active_deployments[deployment_id]
        
        cmd = self.k8s_client.kubectl_command + [
            "scale", f"deployment/{config.name}",
            "-n", config.namespace,
            f"--replicas={replicas}"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
        
        except Exception as e:
            logger.error(f"Failed to scale deployment: {str(e)}")
            return False
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get current deployment status."""
        if deployment_id not in self.active_deployments:
            return None
        
        config = self.active_deployments[deployment_id]
        
        # Get deployment status
        success, deployment_data = await self.k8s_client.get_resource(
            "deployment", config.name, config.namespace
        )
        
        if not success:
            return {"error": "Failed to get deployment status"}
        
        # Get pod status
        cmd = self.k8s_client.kubectl_command + [
            "get", "pods", "-l", f"app={config.name}",
            "-n", config.namespace, "-o", "json"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                pods_data = json.loads(stdout.decode())
            else:
                pods_data = {"items": []}
        
        except Exception:
            pods_data = {"items": []}
        
        return {
            "deployment_id": deployment_id,
            "deployment": deployment_data,
            "pods": pods_data.get("items", []),
            "pod_count": len(pods_data.get("items", [])),
            "ready_pods": len([
                pod for pod in pods_data.get("items", [])
                if pod.get("status", {}).get("phase") == "Running"
            ])
        }
    
    def _generate_deployment_id(self, config: DeploymentConfig) -> str:
        """Generate a unique deployment ID."""
        content = f"{config.name}-{config.namespace}-{config.image.full_name}-{datetime.now().isoformat()}"
        hash_object = hashlib.sha256(content.encode())
        return f"deploy-{hash_object.hexdigest()[:12]}"
    
    async def _create_namespace(self, namespace: str, result: DeploymentResult):
        """Create namespace if it doesn't exist."""
        namespace_yaml = self.yaml_generator.generate_namespace(namespace)
        success, output = await self.k8s_client.apply_resource(namespace_yaml)
        
        if success:
            result.deployed_resources.append(f"namespace/{namespace}")
            result.resources_created += 1
        else:
            # Namespace might already exist, which is okay
            logger.info(f"Namespace creation result: {output}")
    
    async def _deploy_core_resources(self, config: DeploymentConfig, result: DeploymentResult):
        """Deploy core deployment resources."""
        deployment_yaml = self.yaml_generator.generate_deployment(config)
        success, output = await self.k8s_client.apply_resource(deployment_yaml, config.namespace)
        
        if success:
            result.deployed_resources.append(f"deployment/{config.name}")
            result.resources_created += 1
            logger.info(f"Deployment {config.name} created successfully")
        else:
            raise RuntimeError(f"Failed to create deployment: {output}")
    
    async def _deploy_services(self, config: DeploymentConfig, result: DeploymentResult):
        """Deploy services."""
        if not config.services:
            return
        
        services_yaml = self.yaml_generator.generate_service(config)
        success, output = await self.k8s_client.apply_resource(services_yaml, config.namespace)
        
        if success:
            for service in config.services:
                result.deployed_resources.append(f"service/{service.name}")
            result.resources_created += len(config.services)
            logger.info(f"Services for {config.name} created successfully")
        else:
            raise RuntimeError(f"Failed to create services: {output}")
    
    async def _deploy_autoscaling(self, config: DeploymentConfig, result: DeploymentResult):
        """Deploy horizontal pod autoscaler."""
        hpa_yaml = self.yaml_generator.generate_hpa(config)
        success, output = await self.k8s_client.apply_resource(hpa_yaml, config.namespace)
        
        if success:
            result.deployed_resources.append(f"hpa/{config.name}-hpa")
            result.resources_created += 1
            logger.info(f"HPA for {config.name} created successfully")
        else:
            logger.warning(f"Failed to create HPA: {output}")
    
    async def _deploy_network_policy(self, config: DeploymentConfig, result: DeploymentResult):
        """Deploy network policy."""
        # Basic network policy allowing ingress on service ports
        allowed_ingress = [
            {
                "ports": [
                    {"port": service.target_port, "protocol": service.protocol}
                    for service in config.services
                ]
            }
        ]
        
        network_policy_yaml = self.yaml_generator.generate_network_policy(
            config, 
            allowed_ingress=allowed_ingress
        )
        
        success, output = await self.k8s_client.apply_resource(
            network_policy_yaml, 
            config.namespace
        )
        
        if success:
            result.deployed_resources.append(f"networkpolicy/{config.name}-network-policy")
            result.resources_created += 1
            logger.info(f"Network policy for {config.name} created successfully")
        else:
            logger.warning(f"Failed to create network policy: {output}")
    
    async def _wait_for_deployment_ready(self, config: DeploymentConfig, result: DeploymentResult):
        """Wait for deployment to be ready."""
        success = await self.k8s_client.wait_for_deployment(config.name, config.namespace)
        
        if not success:
            raise RuntimeError(f"Deployment {config.name} failed to become ready within timeout")
        
        logger.info(f"Deployment {config.name} is ready")
    
    async def _rollback_deployment(self, config: DeploymentConfig, result: DeploymentResult):
        """Rollback a failed deployment."""
        cmd = self.k8s_client.kubectl_command + [
            "rollout", "undo", f"deployment/{config.name}",
            "-n", config.namespace
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result.rollback_info = {
                    "success": True,
                    "output": stdout.decode()
                }
                logger.info(f"Rollback for {config.name} completed")
            else:
                result.rollback_info = {
                    "success": False,
                    "error": stderr.decode()
                }
                logger.error(f"Rollback for {config.name} failed: {stderr.decode()}")
        
        except Exception as e:
            result.rollback_info = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"Exception during rollback: {str(e)}")
    
    def get_deployment_history(self) -> Dict[str, DeploymentResult]:
        """Get deployment history."""
        return self.deployment_history.copy()
    
    def get_active_deployments(self) -> Dict[str, DeploymentConfig]:
        """Get active deployments."""
        return self.active_deployments.copy()