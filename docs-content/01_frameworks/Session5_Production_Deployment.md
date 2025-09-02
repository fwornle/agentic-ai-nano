# 📝 Session 5 Participant Path: Production Deployment

> **📝 PARTICIPANT PATH CONTENT**  
> Prerequisites: Complete [Practical Implementation](Session5_Practical_Implementation.md)  
> Time Investment: 2-3 hours  
> Outcome: Deploy type-safe agents with monitoring, scaling, and observability  

## Learning Outcomes

After completing this production deployment guide, you will:  

- Deploy type-safe agents with FastAPI and containerization  
- Implement comprehensive monitoring and observability  
- Configure auto-scaling and load balancing for agent services  
- Set up production-grade configuration and secrets management  

## FastAPI Production Deployment

### Advanced FastAPI Application Structure

Build a production-ready FastAPI application with comprehensive features:  

```python
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import time
import uuid
from typing import Optional

# Lifespan management for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting PydanticAI Agent Service")
    
    # Initialize services
    await initialize_monitoring()
    await initialize_database_connections()
    await warm_up_models()
    
    yield
    
    # Shutdown
    print("🛑 Shutting down PydanticAI Agent Service")
    await cleanup_resources()

app = FastAPI(
    title="PydanticAI Data Processing Service",
    description="Production-ready type-safe agent APIs for data processing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Security middleware
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.company.com", "https://api.company.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["api.company.com", "*.company.com"]
)
```

### Advanced Configuration Management

Implement comprehensive configuration with environment-specific settings:  

```python
from pydantic import BaseSettings, Field
from typing import List
import os

class DatabaseSettings(BaseSettings):
    url: str = Field(..., env="DATABASE_URL")
    pool_size: int = Field(10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(20, env="DATABASE_MAX_OVERFLOW")
    pool_timeout: int = Field(30, env="DATABASE_POOL_TIMEOUT")

class RedisSettings(BaseSettings):
    url: str = Field(..., env="REDIS_URL")
    password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    db: int = Field(0, env="REDIS_DB")
    max_connections: int = Field(100, env="REDIS_MAX_CONNECTIONS")

class ModelSettings(BaseSettings):
    primary_model: str = Field("openai:gpt-4", env="PRIMARY_MODEL")
    fallback_model: str = Field("openai:gpt-3.5-turbo", env="FALLBACK_MODEL")
    max_tokens: int = Field(2000, env="MODEL_MAX_TOKENS")
    temperature: float = Field(0.3, env="MODEL_TEMPERATURE")
    api_key: str = Field(..., env="OPENAI_API_KEY")

class MonitoringSettings(BaseSettings):
    prometheus_enabled: bool = Field(True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(8090, env="PROMETHEUS_PORT")
    jaeger_enabled: bool = Field(True, env="JAEGER_ENABLED")
    jaeger_endpoint: str = Field(..., env="JAEGER_ENDPOINT")
    log_level: str = Field("INFO", env="LOG_LEVEL")

class SecuritySettings(BaseSettings):
    jwt_secret: str = Field(..., env="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    api_key_header: str = Field("X-API-Key", env="API_KEY_HEADER")
    rate_limit_per_minute: int = Field(100, env="RATE_LIMIT_PER_MINUTE")

class ProductionConfig(BaseSettings):
    environment: str = Field("production", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    workers: int = Field(4, env="WORKERS")
    
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    model: ModelSettings = ModelSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    security: SecuritySettings = SecuritySettings()
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Load configuration
config = ProductionConfig()
```

### Authentication and Security

Implement comprehensive authentication and authorization:  

```python
from fastapi import Security, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
redis_client = redis.from_url(config.redis.url)

class AuthenticationService:
    def __init__(self):
        self.secret_key = config.security.jwt_secret
        self.algorithm = config.security.jwt_algorithm
        self.access_token_expire_minutes = 30
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key against Redis cache or database"""
        try:
            # Check Redis cache first
            cached_key = redis_client.get(f"api_key:{api_key}")
            if cached_key:
                return cached_key.decode() == "valid"
            
            # Fallback to database verification
            # In production, query your user database
            valid_keys = os.getenv("VALID_API_KEYS", "").split(",")
            is_valid = api_key in valid_keys
            
            # Cache result for 5 minutes
            redis_client.setex(f"api_key:{api_key}", 300, "valid" if is_valid else "invalid")
            
            return is_valid
            
        except Exception as e:
            print(f"API key verification failed: {e}")
            return False
    
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

auth_service = AuthenticationService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Dependency to get current authenticated user"""
    
    # Try JWT token first
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return {"user_id": payload.get("sub"), "auth_type": "jwt"}
    except HTTPException:
        pass
    
    # Fall back to API key verification
    if auth_service.verify_api_key(credentials.credentials):
        return {"user_id": "api_user", "auth_type": "api_key"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials"
    )
```

### Production API Endpoints

Implement comprehensive API endpoints with validation, monitoring, and error handling:  

```python
from prometheus_client import Counter, Histogram, generate_latest
import logging

# Metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')

# Initialize production agent
production_agent = None

@app.on_event("startup")
async def initialize_agent():
    global production_agent
    production_agent = ProductionDataProcessingAgent(config.dict())

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request timing and monitoring"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Add request ID to headers
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    # Record metrics
    REQUEST_DURATION.observe(process_time)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

@app.post("/api/v1/extract-features", response_model=dict)
async def extract_features(
    request: FeatureExtractionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Main feature extraction endpoint with comprehensive error handling"""
    
    try:
        # Validate user permissions
        if not await check_user_permissions(current_user["user_id"], "feature_extraction"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for feature extraction"
            )
        
        # Process request
        result = await production_agent.process_feature_request(request)
        
        # Add background task for cleanup/notification
        background_tasks.add_task(
            notify_completion, 
            current_user["user_id"], 
            result["request_id"]
        )
        
        if result["success"]:
            return {
                "status": "success",
                "data": result["data"],
                "request_id": result["request_id"],
                "processing_time": result.get("processing_time", 0)
            }
        else:
            # Structured error response
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error_category": result.error_category,
                    "error_message": result.error_message,
                    "error_code": result.error_code,
                    "retry_after": result.retry_after_seconds,
                    "support_reference": result.support_reference
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error in feature extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error - please contact support"
        )

@app.get("/api/v1/extraction/{extraction_id}/status")
async def get_extraction_status(
    extraction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get status of feature extraction job"""
    
    try:
        # Query job status from database/cache
        status_data = await get_job_status(extraction_id)
        
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extraction job {extraction_id} not found"
            )
        
        return {
            "extraction_id": extraction_id,
            "status": status_data["status"],
            "progress": status_data.get("progress", 0),
            "estimated_completion": status_data.get("estimated_completion"),
            "error_message": status_data.get("error_message")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting extraction status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving extraction status"
        )

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {}
    }
    
    # Check database connection
    try:
        await check_database_health()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check Redis connection
    try:
        redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check model service
    try:
        await check_model_health()
        health_status["services"]["ai_model"] = "healthy"
    except Exception as e:
        health_status["services"]["ai_model"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if not config.monitoring.prometheus_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metrics endpoint disabled"
        )
    
    return Response(
        generate_latest(),
        media_type="text/plain"
    )
```

## Container and Orchestration Setup

### Dockerfile for Production

Create an optimized Docker container:  

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Kubernetes Deployment

Create comprehensive Kubernetes manifests:  

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pydantic-ai-service
  labels:
    app: pydantic-ai-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pydantic-ai-service
  template:
    metadata:
      labels:
        app: pydantic-ai-service
    spec:
      containers:
      - name: api
        image: company/pydantic-ai-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-credentials
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: pydantic-ai-service
spec:
  selector:
    app: pydantic-ai-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP

---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: pydantic-ai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: pydantic-ai-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Monitoring and Observability

### Comprehensive Logging

Implement structured logging with correlation IDs:  

```python
import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, service_name: str, version: str):
        self.service_name = service_name
        self.version = version
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(getattr(logging, config.monitoring.log_level))
        
        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self.JSONFormatter())
        self.logger.addHandler(handler)
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "service": "pydantic-ai-service",
                "version": "1.0.0"
            }
            
            # Add extra fields
            if hasattr(record, 'request_id'):
                log_entry["request_id"] = record.request_id
            if hasattr(record, 'user_id'):
                log_entry["user_id"] = record.user_id
            if hasattr(record, 'extraction_id'):
                log_entry["extraction_id"] = record.extraction_id
                
            return json.dumps(log_entry)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)

# Initialize logger
structured_logger = StructuredLogger("pydantic-ai-service", "1.0.0")
```

### Metrics Collection

Implement detailed metrics collection:  

```python
from prometheus_client import Counter, Histogram, Gauge, Info
import time

# Application metrics
FEATURE_EXTRACTIONS_TOTAL = Counter(
    'feature_extractions_total', 
    'Total feature extractions', 
    ['status', 'quality_threshold']
)

FEATURE_EXTRACTION_DURATION = Histogram(
    'feature_extraction_duration_seconds',
    'Feature extraction duration',
    buckets=[1, 5, 10, 30, 60, 300, 600]
)

ACTIVE_EXTRACTIONS = Gauge(
    'active_extractions',
    'Number of active feature extractions'
)

MODEL_REQUESTS_TOTAL = Counter(
    'model_requests_total',
    'Total AI model requests',
    ['model', 'status']
)

MODEL_REQUEST_DURATION = Histogram(
    'model_request_duration_seconds',
    'AI model request duration'
)

APPLICATION_INFO = Info(
    'application_info',
    'Application information'
)

# Initialize application info
APPLICATION_INFO.info({
    'version': '1.0.0',
    'environment': config.environment
})

class MetricsCollector:
    @staticmethod
    def record_feature_extraction(status: str, quality_threshold: str, duration: float):
        FEATURE_EXTRACTIONS_TOTAL.labels(
            status=status, 
            quality_threshold=quality_threshold
        ).inc()
        FEATURE_EXTRACTION_DURATION.observe(duration)
    
    @staticmethod
    def increment_active_extractions():
        ACTIVE_EXTRACTIONS.inc()
    
    @staticmethod
    def decrement_active_extractions():
        ACTIVE_EXTRACTIONS.dec()
    
    @staticmethod
    def record_model_request(model: str, status: str, duration: float):
        MODEL_REQUESTS_TOTAL.labels(model=model, status=status).inc()
        MODEL_REQUEST_DURATION.observe(duration)

metrics = MetricsCollector()
```

## Performance Optimization

### Caching Strategy

Implement multi-level caching:  

```python
from functools import wraps
import pickle
import hashlib

class CacheManager:
    def __init__(self, redis_client, default_ttl: int = 300):
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    def cache_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate cache key from function name and arguments"""
        key_data = f"{func_name}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str):
        """Get cached value"""
        try:
            data = self.redis.get(key)
            return pickle.loads(data) if data else None
        except Exception as e:
            logging.warning(f"Cache get failed: {e}")
            return None
    
    async def set(self, key: str, value, ttl: int = None):
        """Set cached value"""
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, pickle.dumps(value))
        except Exception as e:
            logging.warning(f"Cache set failed: {e}")
    
    def cached(self, ttl: int = None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = self.cache_key(func.__name__, *args, **kwargs)
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.set(cache_key, result, ttl or self.default_ttl)
                
                return result
            return wrapper
        return decorator

cache_manager = CacheManager(redis_client)
```

## 📝 Production Deployment Checklist

Ensure your deployment is production-ready:  

### Security Checklist
- [ ] Authentication and authorization implemented  
- [ ] API keys securely managed  
- [ ] HTTPS/TLS encryption enabled  
- [ ] Input validation comprehensive  
- [ ] Rate limiting configured  
- [ ] CORS policies restrictive  

### Performance Checklist
- [ ] Caching strategy implemented  
- [ ] Database connection pooling configured  
- [ ] Auto-scaling rules defined  
- [ ] Resource limits set appropriately  
- [ ] Circuit breakers protecting external services  

### Monitoring Checklist
- [ ] Structured logging implemented  
- [ ] Metrics collection comprehensive  
- [ ] Health checks functional  
- [ ] Alerting rules configured  
- [ ] Tracing enabled for debugging  

### Reliability Checklist
- [ ] Retry logic with exponential backoff  
- [ ] Graceful degradation on failures  
- [ ] Database migrations automated  
- [ ] Backup and disaster recovery planned  
- [ ] Load testing completed  

---

## Next Steps

You've successfully implemented production-ready type-safe agents! For advanced topics:  

- 🎯📝⚙️ Complete the [testing strategies](Session5_ModuleD_Testing_Benchmarking.md)  
- ⚙️ Explore [enterprise patterns](Session5_ModuleB_Enterprise_PydanticAI.md)  
- ⚙️ Master [custom validation systems](Session5_ModuleC_Custom_Validation_Systems.md)  

---

## Navigation

[← Back to Practical Implementation](Session5_Practical_Implementation.md) | [Session Hub](Session5_PydanticAI_Type_Safe_Agents.md) | [Advanced Modules →](Session5_ModuleA_Advanced_Type_Systems.md)