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

# Configure structured logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/mcp/server.log')
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics - these provide observability into our server's performance
request_count = Counter('mcp_requests_total', 'Total MCP requests', ['method', 'status'])
request_duration = Histogram('mcp_request_duration_seconds', 'MCP request duration', ['method'])
active_connections = Gauge('mcp_active_connections', 'Active MCP connections')
error_count = Counter('mcp_errors_total', 'Total MCP errors', ['error_type'])

class ProductionMCPServer:
    """
    Production-ready MCP server with comprehensive monitoring and caching.
    
    This server includes all the features needed for production deployment:
    - Redis caching for improved performance
    - Prometheus metrics for monitoring
    - Structured logging for debugging
    - Health checks for load balancers
    - Environment-based configuration
    """
    
    def __init__(self, name: str = "Production MCP Server"):
        self.mcp = FastMCP(name)
        self.redis_client: Optional[aioredis.Redis] = None
        self.cache_ttl = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes default
        self.start_time = time.time()
        
        # Configuration from environment variables - essential for cloud deployment
        self.config = {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            'max_request_size': int(os.getenv('MAX_REQUEST_SIZE', '1048576')),  # 1MB
            'rate_limit': int(os.getenv('RATE_LIMIT', '100')),  # requests per minute
            'environment': os.getenv('ENVIRONMENT', 'development')
        }
        
        self._setup_tools()
        self._setup_monitoring()
    
    async def initialize(self):
        """
        Initialize async resources like Redis connections.
        
        This separation allows the server to start synchronously but
        initialize expensive resources asynchronously.
        """
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
            Process data with specified operation, demonstrating caching patterns.
            
            This tool shows how to implement caching in production MCP servers.
            The cache key is based on the input data hash, ensuring consistency.
            
            Args:
                data: Input data to process
                operation: Operation type (transform, validate, analyze)
            
            Returns:
                Processed data result with metadata
            """
            # Generate deterministic cache key based on input
            cache_key = f"process:{operation}:{hash(json.dumps(data, sort_keys=True))}"
            
            # Check cache first - this can dramatically improve response times
            cached = await self._get_cache(cache_key)
            if cached:
                logger.info(f"Cache hit for operation: {operation}")
                return cached
            
            # Perform actual processing
            logger.info(f"Processing data with operation: {operation}")
            result = {
                "operation": operation,
                "input_size": len(json.dumps(data)),
                "processed_at": datetime.now().isoformat(),
                "result": self._perform_operation(data, operation),
                "cache_status": "miss"
            }
            
            # Cache the result for future requests
            await self._set_cache(cache_key, result)
            
            return result
        
        @self.mcp.tool()
        @self._monitor_tool
        async def health_check() -> Dict:
            """
            Health check endpoint for load balancers and monitoring systems.
            
            This is crucial for production deployment - load balancers use this
            to determine if the server is ready to handle requests.
            """
            checks = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": time.time() - self.start_time,
                "environment": self.config['environment'],
                "version": "1.0.0"
            }
            
            # Check external dependency health
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    checks["redis"] = "connected"
                except Exception as e:
                    checks["redis"] = "disconnected"
                    checks["status"] = "degraded"
                    logger.warning(f"Redis health check failed: {e}")
            else:
                checks["redis"] = "not_configured"
            
            return checks
    
    def _monitor_tool(self, func):
        """
        Decorator to monitor tool execution with Prometheus metrics.
        
        This decorator automatically tracks:
        - Request counts by method and status
        - Request duration histograms
        - Active connection counts
        - Error rates by type
        """
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method_name = func.__name__
            
            try:
                active_connections.inc()
                result = await func(*args, **kwargs)
                
                # Record successful request
                request_count.labels(method=method_name, status='success').inc()
                logger.info(f"Successfully executed {method_name}")
                
                return result
                
            except Exception as e:
                # Record error metrics
                request_count.labels(method=method_name, status='error').inc()
                error_count.labels(error_type=type(e).__name__).inc()
                logger.error(f"Error in {method_name}: {str(e)}")
                raise
                
            finally:
                # Always record duration and decrement active connections
                duration = time.time() - start_time
                request_duration.labels(method=method_name).observe(duration)
                active_connections.dec()
        
        return wrapper
    
    def _perform_operation(self, data: Dict, operation: str) -> Any:
        """
        Perform the actual data operation.
        
        In a real production server, this would contain your business logic.
        """
        if operation == "transform":
            return {k: v.upper() if isinstance(v, str) else v for k, v in data.items()}
        elif operation == "validate":
            return {"valid": all(v is not None for v in data.values())}
        elif operation == "analyze":
            return {
                "keys": list(data.keys()),
                "types": {k: type(v).__name__ for k, v in data.items()},
                "summary": f"Analyzed {len(data)} fields"
            }
        else:
            return data
    
    async def _get_cache(self, key: str) -> Optional[Dict]:
        """Get value from Redis cache with error handling."""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def _set_cache(self, key: str, value: Dict):
        """Set value in Redis cache with TTL."""
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
        """Set up monitoring endpoints and resources."""
        
        @self.mcp.resource("monitoring://metrics")
        async def get_metrics() -> Dict:
            """
            Expose Prometheus metrics as MCP resource.
            
            This allows MCP clients to query server metrics directly.
            """
            return {
                "request_count": request_count._value._value,
                "active_connections": active_connections._value._value,
                "uptime": time.time() - self.start_time,
                "cache_enabled": self.redis_client is not None
            }

# Global server instance
server = ProductionMCPServer()

async def start_server():
    """
    Startup sequence for the production server.
    
    This ensures proper initialization order:
    1. Initialize async resources (Redis, etc.)
    2. Start the MCP server
    """
    logger.info("Starting production MCP server...")
    await server.initialize()
    logger.info("Server initialization complete")
    server.mcp.run()

if __name__ == "__main__":
    asyncio.run(start_server())