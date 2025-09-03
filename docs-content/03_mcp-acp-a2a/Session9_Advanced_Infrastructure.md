# ⚙️ Session 9 Advanced: Infrastructure & Configuration

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete [🎯📝 Session 9 - Production Agent Deployment](Session9_Production_Agent_Deployment.md)
> Time Investment: 4-6 hours
> Outcome: Master enterprise-scale infrastructure configuration and advanced deployment patterns

## Advanced Learning Outcomes

After completing this advanced module, you will master:

- Enterprise-grade Kubernetes resource management and optimization  
- Advanced service mesh configuration with sophisticated traffic policies  
- High-availability Redis clustering for production agent coordination  
- GitOps security patterns with Sealed Secrets and comprehensive audit trails  
- Production-ready resource optimization and cost management strategies  

## Comprehensive Technical Infrastructure

### Advanced Namespace Configuration

Beyond basic namespace creation, enterprise deployments require sophisticated governance and resource management:

```yaml
# k8s/namespace-production-advanced.yaml - Enterprise namespace with governance
apiVersion: v1
kind: Namespace
metadata:
  name: agentic-ai-prod
  labels:
    name: agentic-ai-prod
    environment: production
    compliance: "gdpr-hipaa"
    cost-center: "ai-operations"
    owner: "ai-platform-team"
    data-classification: "confidential"
    backup-policy: "daily-retain-30"
  annotations:
    scheduler.alpha.kubernetes.io/node-selector: "workload=ai-agents"
    kubernetes.io/managed-by: "enterprise-platform"
    cost-allocation.company.com/department: "AI-Platform"
    compliance.company.com/data-retention: "7-years"
```

This advanced namespace configuration establishes comprehensive governance boundaries for production AI workloads. The `data-classification: confidential` label triggers enhanced security policies, while `backup-policy: daily-retain-30` ensures automated data protection. The compliance annotation enables automated audit trail generation for regulatory requirements.

```yaml
---
# Advanced Resource Quota with GPU management
apiVersion: v1
kind: ResourceQuota
metadata:
  name: agentic-ai-quota-advanced
  namespace: agentic-ai-prod
  labels:
    quota-tier: "enterprise"
    resource-class: "gpu-enabled"
spec:
  hard:
    # Compute Resources
    requests.cpu: "100"                    # 100 CPU cores baseline
    requests.memory: "400Gi"               # 400GB RAM baseline
    requests.nvidia.com/gpu: "20"          # 20 GPU allocation
    limits.cpu: "200"                      # 200 CPU cores maximum
    limits.memory: "800Gi"                 # 800GB RAM maximum
    limits.nvidia.com/gpu: "20"            # GPU hard limit

    # Storage Resources
    requests.storage: "10Ti"               # 10TB storage requests
    persistentvolumeclaims: "50"           # PVC count limit

    # Network Resources
    services.loadbalancers: "5"            # Load balancer limit
    services.nodeports: "10"               # NodePort service limit

    # Object Limits
    count/pods: "200"                      # Maximum pod count
    count/secrets: "50"                    # Secret count limit
    count/configmaps: "20"                 # ConfigMap limit
```

Advanced resource quota management provides comprehensive control over both infrastructure and Kubernetes API object consumption. GPU allocation at 20 units reflects careful capacity planning for AI workloads, while storage quotas prevent unbounded data growth. Object count limits prevent namespace resource explosion while maintaining operational flexibility.

```yaml
---
# Network Policy for micro-segmentation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agentic-ai-network-policy
  namespace: agentic-ai-prod
spec:
  podSelector:
    matchLabels:
      app: mcp-agent
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: istio-system      # Allow Istio proxy traffic
    - namespaceSelector:
        matchLabels:
          name: monitoring        # Allow monitoring scraping
    - podSelector:
        matchLabels:
          app: mcp-agent          # Allow inter-agent communication
    ports:
    - protocol: TCP
      port: 8080                  # HTTP API port
    - protocol: TCP
      port: 9090                  # Metrics port
```

Network policy implementation creates micro-segmentation for enhanced security. The policy allows traffic only from Istio service mesh, monitoring systems, and peer agents while blocking all other network access. This zero-trust networking approach prevents lateral movement during security incidents.

### Enterprise Configuration Management

Advanced configuration management goes beyond simple key-value pairs to include versioning, validation, and rollback capabilities:

```yaml
# k8s/enterprise-configmap-advanced.yaml - Production configuration with versioning
apiVersion: v1
kind: ConfigMap
metadata:
  name: agentic-ai-config
  namespace: agentic-ai-prod
  labels:
    config-version: "v2.1.0"
    environment: production
    config-tier: "enterprise"
    validation-schema: "v1.0"
  annotations:
    config.company.com/last-updated: "2024-01-15T10:30:00Z"
    config.company.com/updated-by: "platform-team"
    config.company.com/change-id: "CHG-2024-001"
data:
  # Redis High-Availability Configuration
  redis.mode: "cluster"
  redis.cluster.nodes: "redis-0.redis-service:6379,redis-1.redis-service:6379,redis-2.redis-service:6379"
  redis.cluster.replicas: "1"
  redis.ssl.enabled: "true"
  redis.ssl.verify_mode: "peer"
  redis.connection_pool_size: "50"
  redis.connection_timeout: "5000"
  redis.socket_keepalive: "true"
```

Advanced Redis configuration enables clustering for high availability and horizontal scaling. The cluster mode with replicas provides fault tolerance, while SSL peer verification ensures secure inter-node communication. Connection pooling optimizes resource utilization for high-concurrency agent workloads.

```yaml
  # Advanced Monitoring and Observability
  prometheus.enabled: "true"
  prometheus.scrape_interval: "15s"
  prometheus.evaluation_interval: "15s"
  prometheus.retention: "15d"
  jaeger.enabled: "true"
  jaeger.sampler_type: "probabilistic"
  jaeger.sampler_param: "0.1"
  jaeger.endpoint: "http://jaeger-collector.monitoring:14268/api/traces"

  # Log Management Configuration
  log.level: "INFO"
  log.format: "json"
  log.output: "stdout"
  log.structured: "true"
  log.correlation_id: "true"
```

Observability configuration balances comprehensive visibility with performance impact. Prometheus 15-second intervals provide near real-time metrics, while probabilistic Jaeger sampling at 10% captures sufficient trace data without overwhelming storage. Structured JSON logging with correlation IDs enables advanced log analysis and distributed tracing correlation.

```yaml
  # Agent Performance Tuning
  agent.max_concurrent_workflows: "100"
  agent.workflow_timeout: "300"
  agent.heartbeat_interval: "15"
  agent.health_check_timeout: "5"
  agent.graceful_shutdown_timeout: "60"
  agent.memory_limit_threshold: "0.8"
  agent.cpu_limit_threshold: "0.7"

  # MCP Protocol Optimization
  mcp.server.timeout: "120"
  mcp.connection_pool_size: "50"
  mcp.max_message_size: "10485760"    # 10MB message limit
  mcp.keep_alive_interval: "30"
  mcp.reconnection_backoff: "exponential"
```

Agent performance configuration balances throughput with stability. The 100 concurrent workflow limit prevents resource exhaustion while maintaining high throughput. Memory and CPU thresholds trigger proactive scaling before resource exhaustion, while MCP protocol optimization handles large message payloads efficiently.

```yaml
  # A2A Communication Configuration
  a2a.discovery.enabled: "true"
  a2a.discovery.protocol: "dns"
  a2a.discovery.refresh_interval: "60"
  a2a.communication.encryption: "tls-1.3"
  a2a.communication.compression: "gzip"
  a2a.load_balancing: "round_robin"

  # ACP Configuration
  acp.local_registry.enabled: "true"
  acp.local_registry.cache_size: "1000"
  acp.local_registry.ttl: "3600"
  acp.capability_timeout: "30"
  acp.capability_retry_count: "3"
```

Agent-to-agent communication optimization enables efficient multi-agent coordination. DNS-based discovery with 60-second refresh provides balance between consistency and performance, while TLS 1.3 encryption ensures security. Gzip compression reduces bandwidth usage for large message exchanges between agents.

### Advanced Secrets Management with GitOps

Enterprise secret management requires GitOps compatibility while maintaining security:

```yaml
# k8s/enterprise-secrets-advanced.yaml - Comprehensive secrets management
apiVersion: v1
kind: Secret
metadata:
  name: agentic-ai-secrets
  namespace: agentic-ai-prod
  labels:
    security-tier: "high"
    rotation-schedule: "monthly"
    encryption-level: "aes-256"
    access-audit: "required"
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "agentic-ai-prod"
    secret.company.com/created-by: "vault-operator"
    secret.company.com/rotation-due: "2024-02-15"
type: Opaque
data:
  # LLM Provider API Keys with rotation metadata
  openai-api-key: <base64-encoded-key>
  openai-org-id: <base64-encoded-org-id>
  anthropic-api-key: <base64-encoded-key>
  azure-openai-endpoint: <base64-encoded-endpoint>
  azure-openai-key: <base64-encoded-key>
  azure-openai-version: <base64-encoded-version>
```

Advanced secrets management integrates with HashiCorp Vault for automated secret rotation and audit trails. The Vault agent injection ensures secrets are dynamically fetched and rotated without manual intervention, while comprehensive labeling enables automated compliance reporting.

```yaml
  # Database and Cache Credentials with encryption
  postgres-host: <base64-encoded-host>
  postgres-port: <base64-encoded-port>
  postgres-database: <base64-encoded-database>
  postgres-username: <base64-encoded-username>
  postgres-password: <base64-encoded-password>
  postgres-ssl-mode: <base64-encoded-ssl-config>

  redis-cluster-password: <base64-encoded-password>
  redis-cluster-tls-cert: <base64-encoded-certificate>
  redis-cluster-tls-key: <base64-encoded-private-key>
  redis-cluster-ca-cert: <base64-encoded-ca-certificate>
```

Database and cache credentials follow enterprise security patterns with comprehensive TLS configuration. The cluster credentials enable secure Redis clustering, while PostgreSQL SSL mode enforcement ensures encrypted database connections throughout the agent infrastructure.

```yaml
---
# Sealed Secrets for GitOps security
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: agentic-ai-sealed-secrets
  namespace: agentic-ai-prod
  labels:
    sealed-secrets.bitnami.com/managed: "true"
    gitops-compatible: "true"
spec:
  encryptedData:
    # Production database connection string
    production-db-url: AgAj8tO9...encrypted-with-cluster-key...8xL2mVp==

    # External API credentials
    monitoring-api-key: AgBy4wX1...encrypted-with-cluster-key...9nK4hQr==
    compliance-webhook-secret: AgCd2mN8...encrypted-with-cluster-key...7zM3pLw==

    # Certificate Authority private keys
    internal-ca-key: AgDf5kB2...encrypted-with-cluster-key...6yH8mCx==
    jwt-signing-key: AgEh7nM4...encrypted-with-cluster-key...5xK9dVz==
```

Sealed Secrets enable secure GitOps workflows by encrypting secrets with cluster-specific keys. These encrypted secrets can be safely stored in Git repositories and automatically decrypted by the cluster controller, enabling infrastructure-as-code practices while maintaining security compliance.

### High-Availability Redis Clustering

Production agent systems require resilient state management through Redis clustering:

```yaml
# k8s/redis-cluster-deployment.yaml - Enterprise Redis clustering
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
  namespace: agentic-ai-prod
  labels:
    app: redis-cluster
    component: data-store
    tier: persistence
spec:
  serviceName: redis-cluster-headless
  replicas: 6                           # 3 masters + 3 replicas
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
        component: data-store
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9121"      # Redis exporter port
```

Redis StatefulSet configuration creates a production-grade cluster with 6 nodes (3 masters, 3 replicas) for high availability. The headless service enables direct pod-to-pod communication required for Redis clustering, while Prometheus annotations enable comprehensive monitoring of cluster health and performance.

```yaml
    spec:
      initContainers:
      - name: redis-cluster-init
        image: redis:7-alpine
        command:
        - /bin/sh
        - -c
        - |
          # Cluster initialization script
          set -e
          echo "Starting Redis cluster initialization..."

          # Wait for all Redis instances to be ready
          for i in $(seq 0 5); do
            until redis-cli -h redis-cluster-${i}.redis-cluster-headless -p 6379 ping; do
              echo "Waiting for redis-cluster-${i}..."
              sleep 2
            done
          done

          # Create cluster configuration
          redis-cli --cluster create \
            redis-cluster-0.redis-cluster-headless:6379 \
            redis-cluster-1.redis-cluster-headless:6379 \
            redis-cluster-2.redis-cluster-headless:6379 \
            redis-cluster-3.redis-cluster-headless:6379 \
            redis-cluster-4.redis-cluster-headless:6379 \
            redis-cluster-5.redis-cluster-headless:6379 \
            --cluster-replicas 1 \
            --cluster-yes
```

The init container handles Redis cluster bootstrap automatically, waiting for all instances to become ready before creating the cluster topology. This automated approach eliminates manual cluster setup and ensures consistent cluster configuration across deployments and disaster recovery scenarios.

```yaml
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
          name: redis
        - containerPort: 16379
          name: cluster-bus
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: agentic-ai-secrets
              key: redis-cluster-password
        - name: REDIS_NODE_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

Redis container configuration enables both standard Redis communication (6379) and cluster bus communication (16379) required for multi-node coordination. Environment variables inject secure passwords and unique node identifiers that enable proper cluster membership management.

```yaml
        command:
        - redis-server
        - /opt/redis/redis.conf
        - --cluster-enabled
        - yes
        - --cluster-config-file
        - /data/nodes.conf
        - --cluster-node-timeout
        - "5000"
        - --appendonly
        - yes
        - --requirepass
        - $(REDIS_PASSWORD)
        - --maxmemory
        - 1gb
        - --maxmemory-policy
        - allkeys-lru
```

Redis startup configuration enables clustering with optimized settings for agent workloads. The 5-second node timeout provides rapid failure detection, while append-only persistence ensures data durability. LRU eviction policy manages memory efficiently when agent session data approaches capacity limits.

```yaml
        resources:
          requests:
            memory: "1.5Gi"               # Guarantee memory for data + clustering
            cpu: "1000m"                  # Full CPU core for Redis operations
          limits:
            memory: "2Gi"                 # Memory limit with headroom
            cpu: "2000m"                  # Burst capacity for cluster operations
        volumeMounts:
        - name: redis-data
          mountPath: /data
        - name: redis-config
          mountPath: /opt/redis
```

Resource allocation provides adequate capacity for both data storage and cluster coordination overhead. The 1.5GB memory request ensures sufficient space for agent session data, while 2GB limit provides headroom for clustering operations. Persistent volume mounting preserves data across pod restarts and cluster maintenance.

### Advanced Service Mesh Configuration

Enterprise service mesh deployment requires sophisticated traffic management and security policies:

```yaml
# k8s/istio-advanced-config.yaml - Enterprise service mesh configuration
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: mcp-agent-vs-advanced
  namespace: agentic-ai-prod
  labels:
    service-mesh: "istio"
    traffic-policy: "enterprise"
spec:
  hosts:
  - mcp-agent-service
  gateways:
  - agentic-ai-gateway
  http:
  # Canary deployment routing
  - match:
    - headers:
        canary-user:
          exact: "true"
    route:
    - destination:
        host: mcp-agent-service
        subset: canary
      weight: 100
```

Advanced VirtualService configuration enables sophisticated deployment strategies like canary releases. Header-based routing allows selective user exposure to new versions, while subset definitions enable precise traffic control for A/B testing and gradual rollouts.

```yaml
  # Production traffic routing with fault injection
  - match:
    - uri:
        prefix: /api/v1
    route:
    - destination:
        host: mcp-agent-service
        subset: stable
      weight: 90
    - destination:
        host: mcp-agent-service
        subset: canary
      weight: 10
    fault:
      delay:
        percentage:
          value: 0.1
        fixedDelay: 5s
      abort:
        percentage:
          value: 0.01
        httpStatus: 503
```

Production traffic configuration implements progressive deployment with 90/10 traffic split between stable and canary versions. Fault injection (0.1% delay, 0.01% abort) enables chaos engineering practices that validate system resilience under realistic failure conditions without impacting user experience.

```yaml
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
      retryOn: 5xx,reset,connect-failure,refused-stream
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: mcp-agent-dr-advanced
  namespace: agentic-ai-prod
spec:
  host: mcp-agent-service
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 10
        maxRetries: 3
        h2UpgradePolicy: UPGRADE
```

DestinationRule configuration optimizes connection management for agent workloads with least-connection load balancing and HTTP/2 upgrade policies. Connection pooling prevents resource exhaustion while enabling high concurrency required for multi-agent coordination patterns.

```yaml
    circuitBreaker:
      consecutiveErrors: 5
      consecutiveGatewayErrors: 3
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 30
    outlierDetection:
      consecutiveGatewayErrors: 3
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: stable
    labels:
      version: stable
  - name: canary
    labels:
      version: canary
```

Advanced circuit breaking and outlier detection protect against cascade failures in distributed agent systems. The configuration ejects problematic instances from the load balancer pool while maintaining minimum healthy capacity. Subset definitions enable traffic routing for deployment strategies and A/B testing scenarios.

---

## Enterprise Cost Optimization

### Resource Right-Sizing

Production systems require continuous optimization to balance performance with cost:

```yaml
# k8s/vertical-pod-autoscaler.yaml - Automated resource optimization
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: mcp-agent-vpa
  namespace: agentic-ai-prod
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-agent
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: mcp-agent
      maxAllowed:
        cpu: "4"
        memory: "8Gi"
      minAllowed:
        cpu: "500m"
        memory: "512Mi"
      controlledResources: ["cpu", "memory"]
```

Vertical Pod Autoscaler automatically optimizes resource allocation based on actual usage patterns. The configuration provides safety boundaries while allowing automatic right-sizing that can reduce costs by 20-30% through accurate resource allocation based on real workload characteristics rather than static estimates.

### GPU Resource Management

AI workloads require specialized GPU resource management for cost optimization:

```yaml
# k8s/gpu-node-pool.yaml - Specialized GPU node configuration
apiVersion: v1
kind: Node
metadata:
  name: gpu-node-001
  labels:
    kubernetes.io/instance-type: "p3.2xlarge"
    nvidia.com/gpu.family: "tesla"
    nvidia.com/gpu.product: "Tesla-V100-SXM2-16GB"
    node.kubernetes.io/workload-type: "gpu-intensive"
    cost-optimization.company.com/preemptible: "true"
spec:
  taints:
  - key: nvidia.com/gpu
    value: "true"
    effect: NoSchedule
```

GPU node configuration enables cost optimization through preemptible instances and workload-specific scheduling. Taints ensure GPU nodes only run GPU workloads, preventing expensive GPU resources from being consumed by CPU-only workloads, while preemptible instances can reduce GPU costs by 60-80%.

---

## Advanced Security Patterns

### Multi-Layer Security Architecture

Enterprise security requires defense-in-depth approaches:

```yaml
# k8s/pod-security-policy.yaml - Comprehensive pod security
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: agentic-ai-psp
  namespace: agentic-ai-prod
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  runAsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1000
        max: 65535
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1000
        max: 65535
```

Pod Security Policy implementation enforces comprehensive security constraints that prevent privilege escalation and ensure containers run with minimal privileges. This defense-in-depth approach protects against container breakout scenarios and limits blast radius during security incidents.

*Advanced infrastructure configuration requires balancing complexity with maintainability while ensuring security and cost-effectiveness remain paramount concerns.*
---

**Previous:** [Session 8 - Advanced Agent Workflows ←](Session8_Advanced_Agent_Workflows.md)
---
