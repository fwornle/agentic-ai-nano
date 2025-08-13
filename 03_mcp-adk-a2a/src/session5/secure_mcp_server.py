"""Main secure MCP server implementation with integrated security features."""

import os
import redis
import logging
from typing import Dict, List, Any
from fastapi import HTTPException, Request

# MCP imports (pseudo-imports for demonstration)
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Fallback for environments without MCP
    class FastMCP:
        def __init__(self, name):
            self.name = name
            self._tools = {}
        
        def tool(self):
            def decorator(func):
                self._tools[func.__name__] = func
                return func
            return decorator

from .auth.jwt_auth import JWTManager
from .auth.permissions import require_permission, Permission, get_user_permissions
from .auth.middleware import MCPAuthMiddleware
from .security.rate_limiter import TokenBucketRateLimiter, RateLimitMiddleware
from .security.audit_system import SecurityAuditSystem, SecurityEventType
from .config import SecurityConfig


class SecureMCPServer:
    """MCP server with comprehensive security features."""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.mcp = FastMCP("Secure MCP Server")
        
        # Initialize security components
        self.redis_client = self._setup_redis()
        self.jwt_manager = JWTManager(redis_client=self.redis_client)
        self.auth_middleware = MCPAuthMiddleware(self.jwt_manager)
        self.rate_limiter = TokenBucketRateLimiter(self.redis_client)
        self.rate_limit_middleware = RateLimitMiddleware(self.rate_limiter)
        self.audit_system = SecurityAuditSystem(self.redis_client)
        
        # Setup secure tools
        self._setup_secure_tools()
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_redis(self):
        """Setup Redis connection for security features."""
        try:
            return redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                password=self.config.redis_password,
                decode_responses=True
            )
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
            return None
    
    def _setup_secure_tools(self):
        """Setup MCP tools with security controls."""
        
        @self.mcp.tool()
        @require_permission(Permission.READ_WEATHER)
        async def get_weather(city: str) -> Dict:
            """Get weather data - requires weather:read permission."""
            # Validate input
            if not city or len(city.strip()) == 0:
                raise HTTPException(status_code=400, detail="City name required")
            
            # Log access
            self.audit_system.log_security_event(
                SecurityEventType.API_KEY_USED,
                details={"tool": "get_weather", "city": city}
            )
            
            # Mock weather data
            return {
                "city": city.strip(),
                "temperature": 22,
                "condition": "Sunny",
                "humidity": 65
            }
        
        @self.mcp.tool()
        @require_permission(Permission.WRITE_FILES)
        async def write_file(path: str, content: str) -> Dict:
            """Write file - requires files:write permission."""
            # Validate file path for security
            if not self._validate_file_path(path):
                self.audit_system.log_security_event(
                    SecurityEventType.INVALID_REQUEST,
                    details={"tool": "write_file", "path": path, "reason": "invalid_path"}
                )
                raise HTTPException(status_code=400, detail="Invalid file path")
            
            # Content validation
            if len(content) > self.config.max_file_size:
                raise HTTPException(status_code=400, detail="File content too large")
            
            return {"success": True, "path": path, "size": len(content)}
        
        @self.mcp.tool()
        @require_permission(Permission.ADMIN_USERS)
        async def list_users() -> List[Dict]:
            """List users - admin only."""
            self.audit_system.log_security_event(
                SecurityEventType.API_KEY_USED,
                details={"tool": "list_users", "admin_access": True}
            )
            
            # Mock user list
            return [
                {"id": 1, "username": "admin", "role": "admin"},
                {"id": 2, "username": "user1", "role": "user"}
            ]
    
    def _validate_file_path(self, path: str) -> bool:
        """Validate file path for security."""
        # Prevent directory traversal
        if ".." in path or path.startswith("/"):
            return False
        
        # Only allow specific extensions
        allowed_extensions = {".txt", ".json", ".csv", ".md"}
        if not any(path.endswith(ext) for ext in allowed_extensions):
            return False
        
        return True
    
    async def authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate and authorize request."""
        try:
            # Authenticate user
            user_data = await self.auth_middleware.authenticate_request(request)
            
            # Check rate limits
            await self.rate_limit_middleware.check_rate_limit(request, user_data)
            
            # Log successful authentication
            self.audit_system.log_security_event(
                SecurityEventType.LOGIN_SUCCESS,
                user_id=user_data.get("sub"),
                details={"username": user_data.get("username")}
            )
            
            return user_data
            
        except HTTPException as e:
            # Log authentication failure
            self.audit_system.log_security_event(
                SecurityEventType.LOGIN_FAILURE,
                details={"error": str(e.detail), "status_code": e.status_code}
            )
            raise
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status and metrics."""
        return {
            "server_name": self.mcp.name,
            "security_features": {
                "jwt_auth": True,
                "rate_limiting": True,
                "audit_logging": True,
                "rbac": True
            },
            "metrics": self.audit_system.get_security_metrics(),
            "redis_connected": self.redis_client is not None
        }