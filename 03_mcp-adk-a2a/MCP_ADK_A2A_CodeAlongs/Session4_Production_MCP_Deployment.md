# Session 4: Production MCP Deployment - Code-Along Tutorial

## 🎯 Learning Objectives
- Containerize MCP servers with Docker
- Deploy to cloud platforms (AWS Lambda, Google Cloud Run)
- Implement health checks and monitoring
- Configure auto-scaling and load balancing
- Set up CI/CD pipelines for MCP servers

## 📚 Pre-Session Reading
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)

---

## Part 1: Containerizing MCP Servers (20 minutes)

### Step 1.1: Project Structure for Production
```bash
# Create production-ready structure
mkdir mcp-production-deployment
cd mcp-production-deployment

# Project structure
mkdir -p {src,tests,scripts,deployments,monitoring}
```

### Step 1.2: Production-Ready MCP Server
```python
# src/production_mcp_server.py
import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
import aioredis
import asyncio
from prometheus_client import Counter, Histogram, Gauge
import time

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/mcp/server.log')
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter('mcp_requests_total', 'Total MCP requests', ['method', 'status'])
request_duration = Histogram('mcp_request_duration_seconds', 'MCP request duration', ['method'])
active_connections = Gauge('mcp_active_connections', 'Active MCP connections')
error_count = Counter('mcp_errors_total', 'Total MCP errors', ['error_type'])

class ProductionMCPServer:
    """Production-ready MCP server with monitoring and caching."""
    
    def __init__(self, name: str = "Production MCP Server"):
        self.mcp = FastMCP(name)
        self.redis_client: Optional[aioredis.Redis] = None
        self.cache_ttl = int(os.getenv('CACHE_TTL', '300'))
        self.start_time = time.time()
        
        # Configuration from environment
        self.config = {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            'max_request_size': int(os.getenv('MAX_REQUEST_SIZE', '1048576')),  # 1MB
            'rate_limit': int(os.getenv('RATE_LIMIT', '100')),  # requests per minute
            'environment': os.getenv('ENVIRONMENT', 'development')
        }
        
        self._setup_tools()
        self._setup_monitoring()
    
    async def initialize(self):
        """Initialize async resources."""
        try:
            self.redis_client = await aioredis.from_url(
                self.config['redis_url'],
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
    
    def _setup_tools(self):
        """Set up MCP tools with decorators for monitoring."""
        
        @self.mcp.tool()
        @self._monitor_tool
        async def process_data(data: Dict[str, Any], operation: str = "transform") -> Dict:
            """
            Process data with specified operation.
            
            Args:
                data: Input data to process
                operation: Operation type (transform, validate, analyze)
            
            Returns:
                Processed data result
            """
            # Check cache first
            cache_key = f"process:{operation}:{hash(json.dumps(data, sort_keys=True))}"
            cached = await self._get_cache(cache_key)
            if cached:
                return cached
            
            # Simulate processing
            result = {
                "operation": operation,
                "input_size": len(json.dumps(data)),
                "processed_at": datetime.now().isoformat(),
                "result": self._perform_operation(data, operation)
            }
            
            # Cache result
            await self._set_cache(cache_key, result)
            
            return result
        
        @self.mcp.tool()
        @self._monitor_tool
        async def health_check() -> Dict:
            """Health check endpoint for monitoring."""
            checks = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": time.time() - self.start_time,
                "environment": self.config['environment']
            }
            
            # Check Redis
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    checks["redis"] = "connected"
                except:
                    checks["redis"] = "disconnected"
                    checks["status"] = "degraded"
            
            return checks
    
    def _monitor_tool(self, func):
        """Decorator to monitor tool execution."""
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method_name = func.__name__
            
            try:
                active_connections.inc()
                result = await func(*args, **kwargs)
                request_count.labels(method=method_name, status='success').inc()
                return result
            except Exception as e:
                request_count.labels(method=method_name, status='error').inc()
                error_count.labels(error_type=type(e).__name__).inc()
                logger.error(f"Error in {method_name}: {str(e)}")
                raise
            finally:
                duration = time.time() - start_time
                request_duration.labels(method=method_name).observe(duration)
                active_connections.dec()
        
        return wrapper
    
    def _perform_operation(self, data: Dict, operation: str) -> Any:
        """Perform the actual data operation."""
        if operation == "transform":
            return {k: v.upper() if isinstance(v, str) else v for k, v in data.items()}
        elif operation == "validate":
            return {"valid": all(v is not None for v in data.values())}
        elif operation == "analyze":
            return {
                "keys": list(data.keys()),
                "types": {k: type(v).__name__ for k, v in data.items()}
            }
        else:
            return data
    
    async def _get_cache(self, key: str) -> Optional[Dict]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def _set_cache(self, key: str, value: Dict):
        """Set value in cache."""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.setex(
                key,
                self.cache_ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    def _setup_monitoring(self):
        """Set up monitoring endpoints."""
        
        @self.mcp.resource("monitoring://metrics")
        async def get_metrics() -> Dict:
            """Get Prometheus metrics."""
            # In production, use prometheus_client.generate_latest()
            return {
                "request_count": request_count._value._value,
                "active_connections": active_connections._value._value,
                "uptime": time.time() - self.start_time
            }

# Create and configure server
server = ProductionMCPServer()

# Run initialization before starting
async def start_server():
    await server.initialize()
    server.mcp.run()

if __name__ == "__main__":
    asyncio.run(start_server())
```

### Step 1.3: Dockerfile for MCP Server
```dockerfile
# deployments/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 mcpuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create log directory
RUN mkdir -p /var/log/mcp && chown mcpuser:mcpuser /var/log/mcp

# Switch to non-root user
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python scripts/health_check.py || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MCP_LOG_LEVEL=INFO

# Expose metrics port
EXPOSE 9090

# Run the server
CMD ["python", "-m", "src.production_mcp_server"]
```

### Step 1.4: Docker Compose for Local Testing
```yaml
# deployments/docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build:
      context: ..
      dockerfile: deployments/Dockerfile
    ports:
      - "8080:8080"
      - "9090:9090"  # Prometheus metrics
    environment:
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
      - CACHE_TTL=300
      - RATE_LIMIT=100
    depends_on:
      - redis
    volumes:
      - ./logs:/var/log/mcp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "scripts/health_check.py"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9091:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

volumes:
  redis_data:
  prometheus_data:
```

---

## Part 2: Cloud Deployment - Google Cloud Run (20 minutes)

### Step 2.1: Cloud Run Adapter
```python
# src/cloud_run_adapter.py
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
import json
import asyncio
from typing import AsyncIterator
import os

from src.production_mcp_server import ProductionMCPServer

app = FastAPI(title="MCP Server on Cloud Run")
server = ProductionMCPServer()

@app.on_event("startup")
async def startup_event():
    """Initialize server on startup."""
    await server.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if server.redis_client:
        await server.redis_client.close()

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP requests over HTTP."""
    try:
        body = await request.json()
        
        # Route to appropriate handler
        method = body.get("method", "")
        params = body.get("params", {})
        
        if method == "tools/list":
            tools = server.mcp.list_tools()
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": tools,
                "id": body.get("id")
            })
        
        elif method.startswith("tools/call"):
            tool_name = params.get("name")
            tool_params = params.get("arguments", {})
            
            # Find and execute tool
            tool = server.mcp.get_tool(tool_name)
            if tool:
                result = await tool(**tool_params)
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": body.get("id")
                })
            else:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": "Tool not found"},
                        "id": body.get("id")
                    },
                    status_code=404
                )
        
        else:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": body.get("id")
                },
                status_code=404
            )
            
    except Exception as e:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": body.get("id", None)
            },
            status_code=500
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health = await server.mcp.get_tool("health_check")()
    return health

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest
    return Response(content=generate_latest(), media_type="text/plain")

# Streaming support for SSE
@app.post("/mcp/stream")
async def handle_mcp_stream(request: Request):
    """Handle streaming MCP requests."""
    
    async def event_generator() -> AsyncIterator[str]:
        """Generate SSE events."""
        body = await request.json()
        
        # Simulate streaming response
        for i in range(5):
            data = {
                "event": "progress",
                "data": {"progress": i * 20, "message": f"Processing step {i+1}"}
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1)
        
        # Final result
        yield f"data: {json.dumps({'event': 'complete', 'data': {'result': 'Success'}})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### Step 2.2: Cloud Run Deployment Configuration
```yaml
# deployments/cloudbuild.yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/mcp-server:$COMMIT_SHA', '-f', 'deployments/Dockerfile', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/mcp-server:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'mcp-server'
      - '--image'
      - 'gcr.io/$PROJECT_ID/mcp-server:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'ENVIRONMENT=production,REDIS_URL=${_REDIS_URL}'
      - '--memory'
      - '512Mi'
      - '--cpu'
      - '1'
      - '--timeout'
      - '300'
      - '--concurrency'
      - '100'
      - '--max-instances'
      - '10'

# Substitutions
substitutions:
  _REDIS_URL: 'redis://10.0.0.3:6379'  # Replace with your Redis URL

options:
  logging: CLOUD_LOGGING_ONLY
```

### Step 2.3: Terraform Infrastructure
```hcl
# deployments/terraform/main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Run Service
resource "google_cloud_run_service" "mcp_server" {
  name     = "mcp-server"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/mcp-server:latest"
        
        resources {
          limits = {
            cpu    = "2"
            memory = "1Gi"
          }
        }
        
        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        
        env {
          name = "REDIS_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.redis_url.secret_id
              key  = "latest"
            }
          }
        }
        
        ports {
          container_port = 8080
        }
      }
      
      service_account_name = google_service_account.mcp_server.email
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "100"
        "autoscaling.knative.dev/minScale" = "1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Service Account
resource "google_service_account" "mcp_server" {
  account_id   = "mcp-server"
  display_name = "MCP Server Service Account"
}

# IAM Binding
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_service.mcp_server.name
  location = google_cloud_run_service.mcp_server.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Secret Manager for Redis URL
resource "google_secret_manager_secret" "redis_url" {
  secret_id = "redis-url"
  
  replication {
    automatic = true
  }
}

# Output the service URL
output "service_url" {
  value = google_cloud_run_service.mcp_server.status[0].url
}
```

---

## Part 3: AWS Lambda Deployment (15 minutes)

### Step 3.1: Lambda Handler
```python
# src/lambda_handler.py
import json
import os
import asyncio
from typing import Dict, Any
import logging
from mangum import Mangum

from src.cloud_run_adapter import app

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create Mangum handler for ASGI
handler = Mangum(app)

# Alternative: Direct Lambda handler
def lambda_handler_direct(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Direct Lambda handler for MCP requests.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Response dictionary
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        method = body.get('method', '')
        
        # Route based on method
        if method == 'tools/list':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'jsonrpc': '2.0',
                    'result': list_tools(),
                    'id': body.get('id')
                })
            }
        
        elif method.startswith('tools/call'):
            result = asyncio.run(execute_tool(body))
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result)
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'jsonrpc': '2.0',
                    'error': {'code': -32601, 'message': 'Method not found'},
                    'id': body.get('id')
                })
            }
            
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'jsonrpc': '2.0',
                'error': {'code': -32603, 'message': str(e)}
            })
        }
```

### Step 3.2: Lambda Dockerfile
```dockerfile
# deployments/Dockerfile.lambda
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Set the handler
CMD ["src.lambda_handler.handler"]
```

### Step 3.3: SAM Template
```yaml
# deployments/template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: MCP Server on AWS Lambda

Globals:
  Function:
    Timeout: 300
    MemorySize: 512
    Environment:
      Variables:
        ENVIRONMENT: production

Resources:
  MCPServerFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: mcp-server
      PackageType: Image
      ImageConfig:
        Command: ["src.lambda_handler.handler"]
      Architectures:
        - x86_64
      Environment:
        Variables:
          REDIS_URL: !Sub '{{resolve:secretsmanager:redis-url:SecretString}}'
      Events:
        MCPApi:
          Type: Api
          Properties:
            Path: /mcp
            Method: POST
        HealthCheck:
          Type: Api
          Properties:
            Path: /health
            Method: GET
      Policies:
        - AWSSecretsManagerGetSecretValuePolicy:
            SecretArn: !Ref RedisUrlSecret
    Metadata:
      DockerTag: latest
      DockerContext: ../
      Dockerfile: deployments/Dockerfile.lambda

  RedisUrlSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: redis-url
      Description: Redis connection URL
      SecretString: !Sub |
        {
          "url": "redis://your-redis-endpoint:6379"
        }

Outputs:
  MCPServerApi:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/'
```

---

## Part 4: Monitoring and Observability (15 minutes)

### Step 4.1: Monitoring Setup
```python
# monitoring/monitor.py
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import time
import asyncio
import aiohttp
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class MCPServerMonitor:
    """Monitor MCP server health and performance."""
    
    def __init__(self, server_urls: List[str]):
        self.server_urls = server_urls
        
        # Metrics
        self.health_check_total = Counter(
            'mcp_health_checks_total',
            'Total health checks performed',
            ['server', 'status']
        )
        
        self.response_time = Histogram(
            'mcp_response_time_seconds',
            'Response time for MCP requests',
            ['server', 'method']
        )
        
        self.server_availability = Gauge(
            'mcp_server_availability',
            'Server availability (1=up, 0=down)',
            ['server']
        )
    
    async def check_health(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """Check health of a single server."""
        try:
            start = time.time()
            async with session.get(f"{url}/health", timeout=10) as response:
                duration = time.time() - start
                
                if response.status == 200:
                    data = await response.json()
                    self.health_check_total.labels(server=url, status='success').inc()
                    self.server_availability.labels(server=url).set(1)
                    self.response_time.labels(server=url, method='health').observe(duration)
                    
                    return {
                        'url': url,
                        'status': 'healthy',
                        'response_time': duration,
                        'details': data
                    }
                else:
                    self.health_check_total.labels(server=url, status='error').inc()
                    self.server_availability.labels(server=url).set(0)
                    
                    return {
                        'url': url,
                        'status': 'unhealthy',
                        'response_time': duration,
                        'http_status': response.status
                    }
                    
        except Exception as e:
            self.health_check_total.labels(server=url, status='error').inc()
            self.server_availability.labels(server=url).set(0)
            
            return {
                'url': url,
                'status': 'error',
                'error': str(e)
            }
    
    async def monitor_loop(self):
        """Main monitoring loop."""
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [
                    self.check_health(session, url)
                    for url in self.server_urls
                ]
                
                results = await asyncio.gather(*tasks)
                
                # Log results
                for result in results:
                    if result['status'] != 'healthy':
                        logger.warning(f"Server unhealthy: {result}")
                
                # Wait before next check
                await asyncio.sleep(30)
    
    def start(self):
        """Start monitoring."""
        # Start Prometheus metrics server
        start_http_server(9092)
        logger.info("Metrics server started on port 9092")
        
        # Start monitoring loop
        asyncio.run(self.monitor_loop())

if __name__ == "__main__":
    servers = [
        "http://localhost:8080",
        "https://mcp-server-abc123.run.app"
    ]
    
    monitor = MCPServerMonitor(servers)
    monitor.start()
```

### Step 4.2: Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "MCP Server Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{
          "expr": "rate(mcp_requests_total[5m])"
        }]
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "rate(mcp_errors_total[5m])"
        }]
      },
      {
        "title": "Response Time",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(mcp_request_duration_seconds_bucket[5m]))"
        }]
      },
      {
        "title": "Server Availability",
        "targets": [{
          "expr": "mcp_server_availability"
        }]
      }
    ]
  }
}
```

---

## 🧪 Testing Your Understanding

### Quick Check Questions

1. **What is the primary purpose of health checks in production MCP servers?**
   - A) Improve performance
   - B) Enable auto-scaling and monitoring
   - C) Reduce costs
   - D) Increase security

2. **Which cloud service automatically scales based on request volume?**
   - A) EC2
   - B) Cloud Run
   - C) Compute Engine
   - D) Virtual Machines

3. **What format does Prometheus use for metrics?**
   - A) JSON
   - B) XML
   - C) Plain text with specific format
   - D) Binary

4. **How does the Lambda handler communicate with MCP servers?**
   - A) Direct function calls
   - B) HTTP/JSON-RPC protocol
   - C) gRPC
   - D) WebSockets

5. **What's the benefit of using Redis cache in MCP servers?**
   - A) Security
   - B) Reduced latency and load
   - C) Better logging
   - D) Simpler deployment

### Practical Exercise

Implement a circuit breaker pattern for MCP server resilience:

```python
class CircuitBreaker:
    """Circuit breaker for MCP server calls."""
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        # TODO: Implement circuit breaker logic
        pass
    
    async def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection."""
        # TODO: Implement call logic
        pass
```

---

## 📝 Session Summary

You've learned to:
- ✅ Containerize MCP servers with Docker
- ✅ Deploy to Google Cloud Run with auto-scaling
- ✅ Create AWS Lambda deployments
- ✅ Implement health checks and monitoring
- ✅ Set up Prometheus metrics and Grafana dashboards
- ✅ Handle production concerns (caching, logging, errors)

### Next Session Preview
In Session 5, we'll secure MCP servers with:
- JWT authentication
- API key management
- Rate limiting
- Input validation
- Encryption and TLS

### Homework
1. Add distributed tracing with OpenTelemetry
2. Implement blue-green deployment strategy
3. Create load testing scripts
4. Add automatic failover between regions

### Answer Key
1. B) Enable auto-scaling and monitoring
2. B) Cloud Run
3. C) Plain text with specific format
4. B) HTTP/JSON-RPC protocol
5. B) Reduced latency and load

---

## Additional Resources
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/tips)
- [Lambda Container Images](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)