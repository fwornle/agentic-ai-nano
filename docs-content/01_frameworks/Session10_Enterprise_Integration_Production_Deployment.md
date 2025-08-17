# Session 10: Enterprise Integration & Production Deployment

## 🎯 Learning Navigation Hub
**Total Time Investment**: 95 minutes (Core) + 50-160 minutes (Optional)
**Your Learning Path**: Choose your engagement level

### Quick Start Guide
- **👀 Observer (55 min)**: Read enterprise concepts + examine deployment patterns
- **🙋‍♂️ Participant (95 min)**: Follow exercises + build production systems
- **🛠️ Implementer (160 min)**: Create enterprise solutions + explore advanced operations

---

## 📋 SESSION OVERVIEW DASHBOARD

### Core Learning Track (95 minutes) - REQUIRED
| Section | Concept Load | Time | Skills |
|---------|--------------|------|--------|
| 🏗️ Enterprise Integration | 4 concepts | 30 min | Understanding |
| 🚀 Production Deployment | 4 concepts | 25 min | Implementation |
| 🔒 Security Fundamentals | 3 concepts | 25 min | Application |
| 📊 Basic Monitoring | 3 concepts | 15 min | Operations |

### Optional Deep Dive Modules (Choose Your Adventure)
- 🔬 **[Module A: Advanced Security & Compliance →](Session10_ModuleA_Advanced_Security_Compliance.md)** (80 min) - GDPR, RBAC, encryption
- 🏭 **[Module B: Enterprise Operations & Scaling →](Session10_ModuleB_Enterprise_Operations_Scaling.md)** (80 min) - Auto-scaling, performance optimization

**🗂️ Code Files**: All examples use files in [`src/session10/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session10)
**🚀 Quick Start**: Run `cd src/session10 && python enterprise_architecture.py` to see enterprise integration

---

## 🧭 CORE SECTION (Required - 95 minutes)

### Part 1: Enterprise Integration Fundamentals (30 minutes)
**Cognitive Load**: 4 new concepts
**Learning Mode**: Conceptual Understanding

#### Understanding Enterprise Systems (8 minutes)
Enterprise environments are complex ecosystems of interconnected systems requiring robust integration patterns, authentication mechanisms, and fault tolerance. This foundation code demonstrates the protocols and configurations needed for reliable enterprise integration:

🗂️ **File**: [`src/session10/enterprise_architecture.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/enterprise_architecture.py) - Enterprise integration patterns

```python
from typing import Dict, Any, List, Protocol
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta

class IntegrationPattern(Enum):
    """Common enterprise integration patterns."""
    REQUEST_REPLY = "request_reply"
    PUBLISH_SUBSCRIBE = "publish_subscribe" 
    MESSAGE_QUEUE = "message_queue"
    API_GATEWAY = "api_gateway"
    SERVICE_MESH = "service_mesh"

@dataclass
class SystemConnection:
    """Configuration for enterprise system connections."""
    system_name: str
    endpoint: str
    auth_method: str
    credentials: Dict[str, Any]
    retry_policy: Dict[str, int] = field(default_factory=dict)
    circuit_breaker: bool = True
    timeout_seconds: int = 30
    rate_limit: Optional[int] = None

# Standard adapter interface for enterprise systems
class EnterpriseSystemAdapter(Protocol):
    """Protocol for enterprise system adapters."""
    
    async def connect(self) -> bool:
        """Establish connection to enterprise system."""
        ...
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with enterprise system."""
        ...
    
    async def execute_operation(self, operation: str, 
                               params: Dict[str, Any]) -> Any:
        """Execute operation on enterprise system."""
        ...
    
    async def health_check(self) -> bool:
        """Check system health and connectivity."""
        ...
```

**Key Concepts:**
1. **Integration Patterns**: Standard communication patterns for enterprise systems
2. **Connection Management**: Robust configuration with circuit breakers and retry policies
3. **Adapter Protocol**: Consistent interface for all enterprise system integrations
4. **Health Monitoring**: Built-in health checks for system reliability

#### ERP System Integration (12 minutes)
Enterprise Resource Planning systems are the backbone of most organizations, requiring specialized adapters that handle authentication, session management, and data transformation. This SAP integration demonstrates OAuth 2.0 authentication, connection pooling, and proper error handling:

🗂️ **File**: [`src/session10/erp_integration.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/erp_integration.py) - SAP/ERP integration patterns

```python
class SAPIntegrationAdapter:
    """Adapter for SAP ERP system integration."""
    
    def __init__(self, base_url: str, credentials: Dict[str, Any]):
        self.base_url = base_url.rstrip('/')
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> bool:
        """Establish connection to SAP system with enterprise configuration."""
        try:
            # Configure TCP connector with enterprise settings
            connector = aiohttp.TCPConnector(
                limit=50,  # Total connection pool size
                limit_per_host=10,  # Connections per host
                keepalive_timeout=30  # Keep connections alive
            )

            # HTTP session configuration
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "EnterpriseAgent-SAP/1.0",
                    "Accept": "application/json"
                }
            )
            return await self.authenticate(self.credentials)
        except Exception as e:
            self.logger.error(f"SAP connection failed: {e}")
            return False

    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with SAP using OAuth 2.0."""
        auth_url = f"{self.base_url}/oauth/token"
        
        # Prepare OAuth 2.0 client credentials grant
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "scope": credentials.get("scope", "read write")
        }

        try:
            async with self.session.post(auth_url, data=auth_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.auth_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                    
                    # Update session headers with bearer token
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    return True
                else:
                    self.logger.error(f"SAP auth failed: {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"SAP authentication error: {e}")
            return False

    async def get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve customer data from SAP."""
        if not customer_id:
            raise ValueError("customer_id is required")
        
        # Ensure we have valid authentication
        if not await self._ensure_authenticated():
            raise Exception("Authentication failed")

        # Build SAP OData URL
        service_url = f"{self.base_url}/sap/opu/odata/sap/ZCustomerService"
        entity_url = f"{service_url}/CustomerSet('{customer_id}')"

        try:
            async with self.session.get(entity_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._transform_customer_data(data)
                elif response.status == 404:
                    return {"error": "Customer not found", "customer_id": customer_id}
                else:
                    error_text = await response.text()
                    raise Exception(f"SAP API error: {response.status} - {error_text}")
        except Exception as e:
            self.logger.error(f"Customer data retrieval failed: {e}")
            raise

    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid authentication token."""
        if not self.auth_token:
            return await self.authenticate(self.credentials)
        
        # Check if token is about to expire (refresh 5 minutes early)
        if self.token_expires:
            time_until_expiry = self.token_expires - datetime.now()
            if time_until_expiry.total_seconds() < 300:  # 5 minutes
                self.logger.info("Token expiring soon, refreshing...")
                return await self.authenticate(self.credentials)
        
        return True
```

#### Database Integration Patterns (10 minutes)
Enterprise agents often need to interact with multiple databases with different engines, connection requirements, and performance characteristics. This database manager handles connection pooling, transaction management, and multi-database coordination:

🗂️ **File**: [`src/session10/erp_integration.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/erp_integration.py) - Multi-database management patterns

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

class EnterpriseDatabase:
    """Enterprise database connection manager."""
    
    def __init__(self, database_configs: Dict[str, Dict[str, Any]]):
        self.configs = database_configs
        self.engines = {}
        self.session_factories = {}
        
    async def initialize_connections(self):
        """Initialize all configured database connections."""
        for db_name, config in self.configs.items():
            await self._setup_database(db_name, config)

    async def _setup_postgresql(self, db_name: str, config: Dict[str, Any]):
        """Setup PostgreSQL connection with enterprise configuration."""
        connection_string = (
            f"postgresql+asyncpg://{config['username']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
        )

        # Database engine configuration
        engine = create_async_engine(
            connection_string,
            pool_size=config.get("pool_size", 10),
            max_overflow=config.get("max_overflow", 20),
            pool_pre_ping=True,  # Validate connections before use
            pool_recycle=3600,   # Recycle connections every hour
            echo=config.get("debug", False)
        )

        # Session factory setup
        self.engines[db_name] = engine
        self.session_factories[db_name] = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
```

---

### Part 2: Production Deployment Essentials (25 minutes)
**Cognitive Load**: 4 new concepts
**Learning Mode**: Implementation & Practice

#### Container Strategy (8 minutes)
Production containerization requires multi-stage builds and security hardening to minimize attack surface, reduce image size, and ensure secure runtime environments. This Dockerfile demonstrates security best practices including non-root users and minimal base images:

🗂️ **File**: [`src/session10/deployment/docker_config.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/deployment/docker_config.py) - Docker configuration

```dockerfile
# Multi-stage Dockerfile - Build stage
FROM python:3.11-slim as builder

# Build stage for dependencies
WORKDIR /build
COPY requirements.txt .

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Multi-stage Dockerfile - Runtime stage
FROM python:3.11-slim as runtime

# Runtime stage with minimal footprint
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r agent && useradd -r -g agent agent
RUN mkdir -p /app/logs /app/data && \
    chown -R agent:agent /app

# Copy application code
COPY --chown=agent:agent src/ ./src/
COPY --chown=agent:agent config/ ./config/

# Switch to non-root user
USER agent

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "src/main.py"]
```

#### Kubernetes Deployment (10 minutes)
Enterprise Kubernetes configuration with high availability requires proper resource management, health checks, and rolling update strategies. This configuration demonstrates production-ready Kubernetes deployment with security contexts and monitoring:

🗂️ **File**: [`src/session10/deployment/k8s-deployment.yaml`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/deployment/k8s-deployment.yaml) - Kubernetes deployment

```yaml
# Kubernetes Deployment Configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: enterprise-agent
  namespace: agents
  labels:
    app: enterprise-agent
    version: v1.0.0
    tier: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: enterprise-agent
  template:
    metadata:
      labels:
        app: enterprise-agent
        version: v1.0.0
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
      - name: agent
        image: enterprise-agent:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: enterprise-agent-service
  namespace: agents
spec:
  selector:
    app: enterprise-agent
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: ClusterIP
```

#### CI/CD Pipeline (7 minutes)
Automated deployment with security scanning ensures code quality, vulnerability detection, and reliable deployments. This GitHub Actions pipeline demonstrates comprehensive CI/CD with security scanning, testing, and staged deployment:

🗂️ **File**: [`src/session10/deployment/.github/workflows/deploy.yml`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/deployment/.github/workflows/deploy.yml) - CI/CD pipeline

```yaml
# GitHub Actions CI/CD Pipeline
name: Production Deployment
on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: enterprise-agent

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

  test:
    runs-on: ubuntu-latest
    needs: security-scan
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
        - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: pytest tests/ -v

  deploy:
    runs-on: ubuntu-latest
    needs: [security-scan, test]
    environment: production
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Deploy to EKS
      run: |
        aws eks update-kubeconfig --region us-west-2 --name production-cluster
        kubectl set image deployment/enterprise-agent \
          agent=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.ref_name }}
        kubectl rollout status deployment/enterprise-agent --timeout=600s
    
    - name: Validate deployment
      run: |
        kubectl wait --for=condition=available \
          deployment/enterprise-agent --timeout=300s
```

---

### Part 3: Security Fundamentals (25 minutes)
**Cognitive Load**: 3 new concepts
**Learning Mode**: Application & Security

#### Authentication & Authorization (10 minutes)
Enterprise-grade security with multiple authentication methods:

🗂️ **File**: [`src/session10/security/enterprise_auth.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/security/enterprise_auth.py) - Authentication framework

```python
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import jwt
import bcrypt
from enum import Enum
from dataclasses import dataclass

class AuthenticationMethod(Enum):
    """Supported authentication methods."""
    BASIC = "basic"
    OAUTH2 = "oauth2"
    SAML = "saml"
    LDAP = "ldap"
    MFA = "mfa"
    CERTIFICATE = "certificate"

@dataclass
class UserContext:
    """User context with comprehensive attributes."""
    user_id: str
    username: str
    email: str
    roles: Set[str]
    permissions: Set[str]
    department: str
    security_clearance: str
    mfa_verified: bool = False
    last_authenticated: Optional[datetime] = None
    session_expires: Optional[datetime] = None

class EnterpriseAuthManager:
    """Comprehensive authentication and authorization manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_sessions: Dict[str, UserContext] = {}
        self.failed_attempts: Dict[str, int] = {}
        self.blacklisted_tokens: Set[str] = set()

    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[UserContext]:
        """Authenticate user with multiple factor support."""
        auth_method = credentials.get("method", "basic")
        username = credentials.get("username")
        
        # Check for account lockout
        if self._is_account_locked(username):
            raise AuthenticationError("Account locked due to failed attempts")

        try:
            if auth_method == AuthenticationMethod.BASIC.value:
                return await self._authenticate_basic(credentials)
            elif auth_method == AuthenticationMethod.OAUTH2.value:
                return await self._authenticate_oauth2(credentials)
            elif auth_method == AuthenticationMethod.LDAP.value:
                return await self._authenticate_ldap(credentials)
            else:
                raise AuthenticationError(f"Unsupported auth method: {auth_method}")
        except AuthenticationError:
            self._record_failed_attempt(username)
            raise

    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts."""
        attempts = self.failed_attempts.get(username, 0)
        return attempts >= 5  # Lock after 5 failed attempts

    def _record_failed_attempt(self, username: str):
        """Record failed authentication attempt."""
        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
```

#### Role-Based Access Control (8 minutes)
Fine-grained permission management:

```python
from enum import Enum

class Permission(Enum):
    """System permissions with hierarchical structure."""
    # Agent operations
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_EXECUTE = "agent:execute"
    
    # Data access by classification
    DATA_READ_PUBLIC = "data:read:public"
    DATA_READ_INTERNAL = "data:read:internal"
    DATA_READ_CONFIDENTIAL = "data:read:confidential"
    DATA_READ_SECRET = "data:read:secret"
    
    # System administration
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_ADMIN = "system:admin"

@dataclass
class Role:
    """Role definition with permissions and constraints."""
    name: str
    permissions: Set[Permission]
    constraints: Dict[str, Any] = field(default_factory=dict)
    inherits_from: List[str] = field(default_factory=list)

class RBACManager:
    """Role-Based Access Control manager."""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        self._initialize_default_roles()

    def _initialize_default_roles(self):
        """Initialize standard enterprise roles."""
        # Data Analyst role
        self.roles["data_analyst"] = Role(
            name="data_analyst",
            permissions={
                Permission.AGENT_READ,
                Permission.AGENT_EXECUTE,
                Permission.DATA_READ_PUBLIC,
                Permission.DATA_READ_INTERNAL
            },
            constraints={
                "time_restriction": "business_hours",
                "ip_whitelist": ["10.0.0.0/8"],
                "max_concurrent_sessions": 3
            }
        )

        # System Administrator role
        self.roles["system_admin"] = Role(
            name="system_admin",
            permissions={
                Permission.AGENT_CREATE,
                Permission.AGENT_READ,
                Permission.AGENT_UPDATE,
                Permission.AGENT_DELETE,
                Permission.SYSTEM_CONFIG,
                Permission.SYSTEM_MONITOR,
                Permission.SYSTEM_ADMIN
            }
        )
```

#### Data Encryption (7 minutes)
Classification-based data protection:

🗂️ **File**: [`src/session10/security/data_protection.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/security/data_protection.py) - Encryption systems

```python
from cryptography.fernet import Fernet, MultiFernet
import os
import base64
import json

class EnterpriseEncryption:
    """Enterprise-grade encryption service."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.symmetric_keys = self._initialize_symmetric_keys()
        self.key_rotation_interval = config.get("key_rotation_hours", 24)

    def _initialize_symmetric_keys(self) -> MultiFernet:
        """Initialize symmetric encryption with key rotation support."""
        keys = []
        
        # Primary key (current)
        primary_key = os.environ.get("ENCRYPTION_KEY_PRIMARY")
        if primary_key:
            keys.append(Fernet(primary_key.encode()))
        else:
            # Generate new key if none provided
            keys.append(Fernet(Fernet.generate_key()))
        
        # Secondary key (for rotation)
        secondary_key = os.environ.get("ENCRYPTION_KEY_SECONDARY")
        if secondary_key:
            keys.append(Fernet(secondary_key.encode()))
            
        return MultiFernet(keys)

    async def encrypt_sensitive_data(self, data: Dict[str, Any], 
                                   classification: str = "internal") -> Dict[str, Any]:
        """Encrypt data based on classification level."""
        encrypted_data = {}
        
        for key, value in data.items():
            field_classification = self._get_field_classification(key, classification)

            if field_classification in ["confidential", "secret"]:
                # Use asymmetric encryption for highly sensitive data
                encrypted_value = self._asymmetric_encrypt(str(value))
                encrypted_data[key] = {
                    "value": encrypted_value,
                    "encrypted": True,
                    "method": "asymmetric",
                    "classification": field_classification
                }
            elif field_classification == "internal":
                # Use symmetric encryption for internal data
                encrypted_value = self.symmetric_keys.encrypt(str(value).encode())
                encrypted_data[key] = {
                    "value": base64.b64encode(encrypted_value).decode(),
                    "encrypted": True,
                    "method": "symmetric",
                    "classification": field_classification
                }
            else:
                # Public data doesn't need encryption
                encrypted_data[key] = {
                    "value": value,
                    "encrypted": False,
                    "classification": field_classification
                }
        
        return encrypted_data
```

---

### Part 4: Basic Monitoring & Operations (15 minutes)
**Cognitive Load**: 3 new concepts
**Learning Mode**: Operations & Monitoring

#### Basic Metrics Collection (6 minutes)
Essential monitoring for production systems:

🗂️ **File**: [`src/session10/monitoring/observability.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/monitoring/observability.py) - Monitoring system

```python
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"      # Monotonically increasing values
    GAUGE = "gauge"          # Snapshot values that can go up or down
    HISTOGRAM = "histogram"  # Distribution of values with buckets
    SUMMARY = "summary"      # Distribution with quantiles

@dataclass
class Metric:
    """Individual metric definition."""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""

class BasicMonitoring:
    """Basic monitoring system for production agents."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_store: Dict[str, List[Metric]] = {}

    async def collect_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Collect basic agent performance metrics."""
        metrics = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "performance": await self._collect_performance_metrics(agent_id),
            "health": await self._collect_health_metrics(agent_id),
            "errors": await self._collect_error_metrics(agent_id)
        }
        
        return metrics

    async def _collect_performance_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Collect agent performance metrics."""
        return {
            "cpu_usage_percent": 0.0,  # Implement actual collection
            "memory_usage_mb": 0.0,
            "request_latency_ms": 0.0,
            "throughput_rps": 0.0,
            "error_rate_percent": 0.0
        }
```

#### Health Checks (5 minutes)
Production health monitoring:

```python
class HealthChecker:
    """Production health monitoring system."""
    
    def __init__(self, system_components: Dict[str, Any]):
        self.components = system_components
        
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check."""
        health_status = {
            "overall_status": "unknown",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        all_healthy = True
        
        # Check database connectivity
        db_health = await self._check_database_health()
        health_status["components"]["database"] = db_health
        if not db_health["healthy"]:
            all_healthy = False
        
        # Check external API connectivity
        api_health = await self._check_api_health()
        health_status["components"]["external_apis"] = api_health
        if not api_health["healthy"]:
            all_healthy = False
        
        # Check system resources
        resource_health = await self._check_system_resources()
        health_status["components"]["resources"] = resource_health
        if not resource_health["healthy"]:
            all_healthy = False
        
        health_status["overall_status"] = "healthy" if all_healthy else "unhealthy"
        return health_status

    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            # Implement actual database health check
            return {"healthy": True, "response_time_ms": 10}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
```

#### Basic Alerting (4 minutes)
Simple alerting for critical conditions:

```python
from enum import Enum

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """Basic alert definition."""
    alert_id: str
    name: str
    description: str
    severity: AlertSeverity
    triggered_at: datetime
    resolved_at: Optional[datetime] = None

class BasicAlertManager:
    """Basic alert management system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "error_rate": 5.0,
            "response_time": 2000.0  # milliseconds
        }

    async def evaluate_alerts(self, metrics: Dict[str, Any]):
        """Evaluate metrics against alert thresholds."""
        performance = metrics.get("performance", {})
        
        # Check CPU usage
        cpu_usage = performance.get("cpu_usage_percent", 0)
        if cpu_usage > self.alert_thresholds["cpu_usage"]:
            await self._create_alert(
                "high_cpu_usage",
                f"High CPU usage: {cpu_usage}%",
                AlertSeverity.WARNING
            )

    async def _create_alert(self, alert_name: str, description: str, 
                           severity: AlertSeverity):
        """Create and store alert."""
        alert_id = f"{alert_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = Alert(
            alert_id=alert_id,
            name=alert_name,
            description=description,
            severity=severity,
            triggered_at=datetime.now()
        )
        
        self.active_alerts[alert_id] = alert
        await self._send_notification(alert)

    async def _send_notification(self, alert: Alert):
        """Send alert notification (implement based on your needs)."""
        print(f"ALERT: {alert.severity.value.upper()} - {alert.description}")
```

---

## ✅ Core Section Validation (5 minutes)

### Quick Implementation Exercise
🗂️ **Exercise Files**: 
- [`src/session10/enterprise_architecture.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session10/enterprise_architecture.py) - Complete integration example
- [`src/session10/deployment/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session10/deployment/) - Production deployment configs

```bash
# Try the examples:
cd src/session10
python enterprise_architecture.py        # Enterprise integration
python -m pytest test_integration.py     # Integration tests

# Deploy with Docker
docker build -t enterprise-agent .
docker run -p 8000:8000 enterprise-agent

# Deploy to Kubernetes (if available)
kubectl apply -f k8s-deployment.yaml
kubectl get pods -l app=enterprise-agent
```

### Self-Assessment Checklist
- [ ] I understand enterprise integration patterns and challenges
- [ ] I can create production-ready Docker containers with security
- [ ] I can implement basic authentication and authorization
- [ ] I understand monitoring and health check requirements
- [ ] I'm ready for advanced modules or production deployment

**Session Complete**: ✅ You've mastered enterprise integration fundamentals
**Ready for**: Advanced modules or real-world implementation

---

# 🎛️ OPTIONAL MODULES (Choose Your Adventure)

## 🔬 Module A: Advanced Security & Compliance (80 minutes)
**Prerequisites**: Core Section Complete
**Target Audience**: Security engineers and compliance teams
**Cognitive Load**: 6 advanced concepts

### A1: GDPR & Compliance Frameworks (40 minutes)
🗂️ **Files**: Advanced compliance examples in [`src/session10/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session10)

Comprehensive GDPR implementation, data retention policies, consent management, audit logging, and multi-framework compliance (HIPAA, SOC 2, PCI-DSS).

### A2: Advanced Encryption & Key Management (40 minutes)
Asymmetric encryption, key rotation strategies, certificate management, data classification systems, and enterprise secret management.

---

## 🏭 Module B: Enterprise Operations & Scaling (80 minutes)
**Prerequisites**: Core Section Complete
**Target Audience**: DevOps engineers and platform architects
**Cognitive Load**: 5 operational concepts

### B1: Auto-Scaling & Performance Optimization (45 minutes)
🗂️ **Files**: Scaling examples in [`src/session10/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session10)

Intelligent auto-scaling with multi-factor decision making, Redis caching strategies, connection pooling, and performance profiling.

### B2: Advanced Monitoring & Troubleshooting (35 minutes)
Distributed tracing with OpenTelemetry, comprehensive alerting systems, log aggregation, performance analysis, and incident response procedures.

---

## 📊 Progress Tracking

### Completion Status
- [ ] Core Section (95 min) - Complete enterprise foundation
- [ ] [Module A: Advanced Security & Compliance](Session10_ModuleA_Advanced_Security_Compliance.md) (80 min)
- [ ] [Module B: Enterprise Operations & Scaling](Session10_ModuleB_Enterprise_Operations_Scaling.md) (80 min)

**🗂️ All Code Examples**: Available in [`src/session10/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session10) - Complete enterprise implementation!

---

## 📝 Multiple Choice Test - Session 10 (15 minutes)

Test your understanding of enterprise integration and production deployment.

### Question 1
**What is the primary challenge in enterprise agent integration?**

A) Code complexity  
B) Connecting with legacy systems and ensuring security  
C) Performance optimization  
D) User interface design  

### Question 2
**Which pattern is most effective for ERP system integration?**

A) Direct database access  
B) Adapter pattern with OAuth 2.0 authentication  
C) File-based integration  
D) Screen scraping  

### Question 3
**What is the main benefit of multi-stage Docker builds for agent deployment?**

A) Faster builds  
B) Reduced image size and improved security  
C) Better documentation  
D) Easier debugging  

### Question 4
**How should you handle secrets and credentials in production deployments?**

A) Environment variables  
B) Encrypted secret management systems with rotation  
C) Configuration files  
D) Code comments  

### Question 5
**What is the purpose of health checks in production agent systems?**

A) Performance monitoring only  
B) Comprehensive system and dependency validation  
C) User authentication  
D) Cost optimization  

### Question 6
**Which deployment strategy minimizes downtime during updates?**

A) All-at-once deployment  
B) Rolling updates with health checks  
C) Maintenance windows  
D) Manual deployment  

### Question 7
**What is the most important aspect of enterprise security for agents?**

A) Password complexity  
B) Zero-trust architecture with encryption and audit logging  
C) VPN access  
D) Firewall rules  

### Question 8
**How should you approach monitoring in enterprise agent systems?**

A) Log files only  
B) Comprehensive observability with metrics, traces, and alerts  
C) Manual monitoring  
D) Error counting  

### Question 9
**What makes Kubernetes suitable for enterprise agent deployment?**

A) Simple configuration  
B) Auto-scaling, self-healing, and enterprise orchestration  
C) Low cost  
D) Better performance  

### Question 10
**Which approach is best for handling enterprise agent failures?**

A) Immediate restart  
B) Circuit breakers, graceful degradation, and compensation patterns  
C) Manual intervention  
D) System shutdown  

---

[**🗂️ View Test Solutions →**](Session10_Test_Solutions.md)

## 🧭 Navigation

**Previous:** [Session 9 - Multi-Agent Patterns](Session9_Multi_Agent_Patterns.md)

**Optional Deep Dive Modules:**

- 🔒 **[Module A: Advanced Security & Compliance](Session10_ModuleA_Advanced_Security_Compliance.md)** - Enterprise security patterns
- 🏭 **[Module B: Enterprise Operations & Scaling](Session10_ModuleB_Enterprise_Operations_Scaling.md)** - Production operations

**Next:** [Module 2 - RAG Architecture →](../02_rag/index.md)

---

**🏆 Frameworks Module Complete!** You've successfully completed the Agent Frameworks Module and are now ready to build production-ready, enterprise-grade agent systems!
