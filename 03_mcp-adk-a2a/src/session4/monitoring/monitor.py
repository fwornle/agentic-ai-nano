# monitoring/monitor.py
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import time
import asyncio
import aiohttp
from typing import List, Dict, Optional
import logging
import json
from dataclasses import dataclass
from datetime import datetime, timedelta

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ServerHealthStatus:
    """Represents the health status of a single MCP server."""
    url: str
    status: str  # 'healthy', 'unhealthy', 'error'
    response_time: Optional[float]
    last_check: datetime
    error_message: Optional[str] = None
    details: Optional[Dict] = None

class MCPServerMonitor:
    """
    Comprehensive monitoring system for MCP servers.
    
    This monitor provides:
    - Health checking with configurable intervals
    - Prometheus metrics collection
    - Alerting when servers become unhealthy
    - Historical data tracking
    """
    
    def __init__(self, server_urls: List[str], check_interval: int = 30):
        self.server_urls = server_urls
        self.check_interval = check_interval
        self.server_status: Dict[str, ServerHealthStatus] = {}
        
        # Prometheus metrics for comprehensive monitoring
        self.health_check_total = Counter(
            'mcp_health_checks_total',
            'Total health checks performed',
            ['server', 'status']
        )
        
        self.response_time = Histogram(
            'mcp_response_time_seconds',
            'Response time for MCP requests',
            ['server', 'method'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf')]
        )
        
        self.server_availability = Gauge(
            'mcp_server_availability',
            'Server availability (1=up, 0=down)',
            ['server']
        )
        
        self.consecutive_failures = Gauge(
            'mcp_consecutive_failures',
            'Number of consecutive failures',
            ['server']
        )
        
        # Track failure counts for alerting
        self.failure_counts: Dict[str, int] = {url: 0 for url in server_urls}
    
    async def check_health(self, session: aiohttp.ClientSession, url: str) -> ServerHealthStatus:
        """
        Perform comprehensive health check on a single server.
        """
        start_time = time.time()
        
        try:
            # Make health check request with timeout
            async with session.get(
                f"{url}/health", 
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    # Parse health check response
                    try:
                        health_data = await response.json()
                        
                        # Reset failure count on success
                        self.failure_counts[url] = 0
                        
                        # Update metrics
                        self.health_check_total.labels(server=url, status='success').inc()
                        self.server_availability.labels(server=url).set(1)
                        self.response_time.labels(server=url, method='health').observe(response_time)
                        self.consecutive_failures.labels(server=url).set(0)
                        
                        return ServerHealthStatus(
                            url=url,
                            status='healthy',
                            response_time=response_time,
                            last_check=datetime.now(),
                            details=health_data
                        )
                        
                    except json.JSONDecodeError:
                        return ServerHealthStatus(
                            url=url,
                            status='unhealthy',
                            response_time=response_time,
                            last_check=datetime.now(),
                            error_message="Invalid JSON response"
                        )
                else:
                    # HTTP error status
                    self.failure_counts[url] += 1
                    self.health_check_total.labels(server=url, status='error').inc()
                    self.server_availability.labels(server=url).set(0)
                    self.consecutive_failures.labels(server=url).set(self.failure_counts[url])
                    
                    return ServerHealthStatus(
                        url=url,
                        status='unhealthy',
                        response_time=response_time,
                        last_check=datetime.now(),
                        error_message=f"HTTP {response.status}"
                    )
                    
        except asyncio.TimeoutError:
            self.failure_counts[url] += 1
            self.health_check_total.labels(server=url, status='timeout').inc()
            self.server_availability.labels(server=url).set(0)
            self.consecutive_failures.labels(server=url).set(self.failure_counts[url])
            
            return ServerHealthStatus(
                url=url,
                status='error',
                response_time=time.time() - start_time,
                last_check=datetime.now(),
                error_message="Request timeout"
            )
            
        except Exception as e:
            self.failure_counts[url] += 1
            self.health_check_total.labels(server=url, status='error').inc()
            self.server_availability.labels(server=url).set(0)
            self.consecutive_failures.labels(server=url).set(self.failure_counts[url])
            
            return ServerHealthStatus(
                url=url,
                status='error',
                response_time=time.time() - start_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_all_servers(self, session: aiohttp.ClientSession) -> List[ServerHealthStatus]:
        """Check health of all configured servers concurrently."""
        tasks = [
            self.check_health(session, url)
            for url in self.server_urls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions from the gather
        health_statuses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error status for failed check
                health_statuses.append(ServerHealthStatus(
                    url=self.server_urls[i],
                    status='error',
                    response_time=None,
                    last_check=datetime.now(),
                    error_message=str(result)
                ))
            else:
                health_statuses.append(result)
        
        return health_statuses
    
    async def monitor_loop(self):
        """
        Main monitoring loop that runs continuously.
        """
        logger.info(f"Starting monitoring loop for {len(self.server_urls)} servers")
        
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    # Check all servers
                    health_statuses = await self.check_all_servers(session)
                    
                    # Update internal state
                    for status in health_statuses:
                        self.server_status[status.url] = status
                    
                    # Log significant events
                    unhealthy_servers = [s for s in health_statuses if s.status != 'healthy']
                    if unhealthy_servers:
                        for server in unhealthy_servers:
                            logger.warning(
                                f"Server {server.url} is {server.status}: {server.error_message}"
                            )
                    
                    # Log summary
                    healthy_count = len([s for s in health_statuses if s.status == 'healthy'])
                    logger.info(f"Health check complete: {healthy_count}/{len(health_statuses)} servers healthy")
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
    
    def start(self, metrics_port: int = 9092):
        """Start the monitoring system."""
        # Start Prometheus metrics server
        start_http_server(metrics_port)
        logger.info(f"Prometheus metrics server started on port {metrics_port}")
        
        # Start monitoring loop
        logger.info("Starting MCP server monitoring...")
        asyncio.run(self.monitor_loop())

# Example usage
if __name__ == "__main__":
    # Configure servers to monitor
    servers = [
        "http://localhost:8080",
        "https://mcp-server-abc123.run.app",
        "https://api.example.com"
    ]
    
    # Create and start monitor
    monitor = MCPServerMonitor(servers, check_interval=30)
    monitor.start()