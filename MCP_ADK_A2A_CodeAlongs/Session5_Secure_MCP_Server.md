# Session 5: Secure MCP Server - Code-Along Tutorial

## 🎯 Learning Objectives
- Implement JWT authentication for MCP servers
- Add API key management and rotation
- Configure rate limiting and DDoS protection
- Secure data transmission with TLS
- Implement input validation and sanitization
- Add audit logging and security monitoring

## 📚 Pre-Session Reading
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [JWT Security Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [MCP Security Considerations](https://modelcontextprotocol.io/docs/concepts/security)

---

## Part 1: Authentication and Authorization (25 minutes)

### Step 1.1: JWT Authentication System
```python
# src/auth/jwt_auth.py
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
import json
import secrets
import os

class JWTManager:
    """JWT token management with Redis-based token blacklisting."""
    
    def __init__(self, secret_key: str = None, redis_client = None):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', self._generate_secret())
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.redis_client = redis_client
        
        # Ensure secret key is secure
        if len(self.secret_key) < 32:
            raise ValueError("JWT secret key must be at least 32 characters")
    
    def _generate_secret(self) -> str:
        """Generate a secure random secret key."""
        return secrets.token_urlsafe(64)
    
    def create_tokens(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Create access and refresh tokens."""
        now = datetime.now(timezone.utc)
        
        # Access token
        access_payload = {
            "sub": user_data["user_id"],
            "username": user_data["username"],
            "roles": user_data.get("roles", ["user"]),
            "permissions": user_data.get("permissions", []),
            "iat": now,
            "exp": now + timedelta(minutes=self.access_token_expire_minutes),
            "type": "access"
        }
        
        # Refresh token
        refresh_payload = {
            "sub": user_data["user_id"],
            "iat": now,
            "exp": now + timedelta(days=self.refresh_token_expire_days),
            "type": "refresh"
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            # Check if token is blacklisted
            if self._is_token_blacklisted(token):
                raise HTTPException(status_code=401, detail="Token has been revoked")
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Create new access token from refresh token."""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Get user data (simplified - in production, fetch from database)
            user_data = {
                "user_id": payload["sub"],
                "username": "user",  # Would fetch from DB
                "roles": ["user"],
                "permissions": []
            }
            
            return self.create_tokens(user_data)
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    def blacklist_token(self, token: str):
        """Add token to blacklist."""
        if not self.redis_client:
            return
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], 
                              options={"verify_exp": False})
            exp = payload.get("exp")
            if exp:
                # Calculate TTL (time until expiration)
                ttl = exp - datetime.now(timezone.utc).timestamp()
                if ttl > 0:
                    self.redis_client.setex(f"blacklist:{token}", int(ttl), "1")
        except:
            pass  # If we can't decode, we can't blacklist effectively
    
    def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        if not self.redis_client:
            return False
        
        return bool(self.redis_client.get(f"blacklist:{token}"))

class UserManager:
    """User management with secure password handling."""
    
    def __init__(self, redis_client = None):
        self.redis_client = redis_client
        self.password_min_length = 8
        
        # Default admin user (in production, create via CLI)
        self._ensure_admin_user()
    
    def _ensure_admin_user(self):
        """Create default admin user if it doesn't exist."""
        admin_password = os.getenv('ADMIN_PASSWORD', 'change_me_immediately!')
        if admin_password == 'change_me_immediately!':
            print("⚠️  WARNING: Using default admin password. Change immediately!")
        
        admin_user = {
            "user_id": "admin",
            "username": "admin",
            "password_hash": self.hash_password(admin_password),
            "roles": ["admin", "user"],
            "permissions": ["*"],  # All permissions
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active": True
        }
        
        self._save_user(admin_user)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        if len(password) < self.password_min_length:
            raise ValueError(f"Password must be at least {self.password_min_length} characters")
        
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data."""
        user = self._get_user(username)
        if not user:
            return None
        
        if not user.get("active", False):
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            return None
        
        # Remove sensitive data
        safe_user = {k: v for k, v in user.items() if k != "password_hash"}
        return safe_user
    
    def _save_user(self, user: Dict[str, Any]):
        """Save user to storage."""
        if self.redis_client:
            self.redis_client.setex(
                f"user:{user['username']}", 
                86400,  # 24 hours
                json.dumps(user)
            )
    
    def _get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user from storage."""
        if not self.redis_client:
            # Fallback for demo
            return {
                "user_id": username,
                "username": username,
                "password_hash": self.hash_password("demo123"),
                "roles": ["user"],
                "permissions": ["read"],
                "active": True
            }
        
        user_data = self.redis_client.get(f"user:{username}")
        return json.loads(user_data) if user_data else None

# FastAPI dependencies
security = HTTPBearer()
jwt_manager = JWTManager()
user_manager = UserManager()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to verify JWT token."""
    return jwt_manager.verify_token(credentials.credentials)

async def require_permission(permission: str):
    """Create a dependency that requires specific permission."""
    def permission_checker(current_user: Dict = Depends(verify_token)):
        user_permissions = current_user.get("permissions", [])
        if "*" not in user_permissions and permission not in user_permissions:
            raise HTTPException(
                status_code=403, 
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return permission_checker
```

### Step 1.2: API Key Management
```python
# src/auth/api_keys.py
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any
import json

class APIKeyManager:
    """Manage API keys with rotation and rate limiting."""
    
    def __init__(self, redis_client = None):
        self.redis_client = redis_client
        self.key_prefix = "apikey:"
        self.rate_limit_prefix = "ratelimit:"
        self.default_rate_limit = 1000  # requests per hour
    
    def generate_api_key(self, user_id: str, name: str, 
                        permissions: List[str] = None,
                        rate_limit: int = None,
                        expires_days: int = 365) -> Dict[str, Any]:
        """Generate a new API key."""
        # Generate secure random key
        raw_key = secrets.token_urlsafe(32)
        
        # Create key hash for storage
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # Key metadata
        key_data = {
            "key_id": key_hash[:16],  # Short ID for identification
            "user_id": user_id,
            "name": name,
            "permissions": permissions or ["read"],
            "rate_limit": rate_limit or self.default_rate_limit,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=expires_days)).isoformat(),
            "last_used": None,
            "usage_count": 0,
            "active": True
        }
        
        # Store key data
        if self.redis_client:
            self.redis_client.setex(
                f"{self.key_prefix}{key_hash}",
                expires_days * 24 * 3600,  # TTL in seconds
                json.dumps(key_data)
            )
        
        return {
            "api_key": raw_key,
            "key_id": key_data["key_id"],
            "expires_at": key_data["expires_at"],
            "permissions": key_data["permissions"],
            "rate_limit": key_data["rate_limit"]
        }
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key and return key data."""
        if not api_key:
            return None
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Get key data
        key_data = self._get_key_data(key_hash)
        if not key_data:
            return None
        
        # Check if key is active
        if not key_data.get("active", False):
            return None
        
        # Check expiration
        expires_at = datetime.fromisoformat(key_data["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            return None
        
        # Update last used
        self._update_key_usage(key_hash, key_data)
        
        return key_data
    
    def check_rate_limit(self, key_hash: str, key_data: Dict[str, Any]) -> bool:
        """Check if API key has exceeded rate limit."""
        rate_limit = key_data.get("rate_limit", self.default_rate_limit)
        
        # Rate limiting window (1 hour)
        window_key = f"{self.rate_limit_prefix}{key_hash}:{datetime.now(timezone.utc).hour}"
        
        if not self.redis_client:
            return True  # Allow if no Redis
        
        current_count = self.redis_client.get(window_key)
        current_count = int(current_count) if current_count else 0
        
        if current_count >= rate_limit:
            return False
        
        # Increment counter
        pipe = self.redis_client.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, 3600)  # 1 hour TTL
        pipe.execute()
        
        return True
    
    def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """Revoke an API key."""
        # Find key by ID and user
        if not self.redis_client:
            return False
        
        # In production, you'd need a reverse index
        # For demo, we'll mark as inactive
        for key in self.redis_client.scan_iter(f"{self.key_prefix}*"):
            key_data = json.loads(self.redis_client.get(key))
            if (key_data.get("key_id") == key_id and 
                key_data.get("user_id") == user_id):
                
                key_data["active"] = False
                key_data["revoked_at"] = datetime.now(timezone.utc).isoformat()
                
                self.redis_client.set(key, json.dumps(key_data))
                return True
        
        return False
    
    def list_user_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """List all API keys for a user."""
        if not self.redis_client:
            return []
        
        user_keys = []
        for key in self.redis_client.scan_iter(f"{self.key_prefix}*"):
            key_data = json.loads(self.redis_client.get(key))
            if key_data.get("user_id") == user_id:
                # Remove sensitive data
                safe_key_data = {k: v for k, v in key_data.items() 
                               if k not in ["key_hash"]}
                user_keys.append(safe_key_data)
        
        return user_keys
    
    def _get_key_data(self, key_hash: str) -> Optional[Dict[str, Any]]:
        """Get key data from storage."""
        if not self.redis_client:
            return None
        
        key_data = self.redis_client.get(f"{self.key_prefix}{key_hash}")
        return json.loads(key_data) if key_data else None
    
    def _update_key_usage(self, key_hash: str, key_data: Dict[str, Any]):
        """Update key usage statistics."""
        if not self.redis_client:
            return
        
        key_data["last_used"] = datetime.now(timezone.utc).isoformat()
        key_data["usage_count"] = key_data.get("usage_count", 0) + 1
        
        self.redis_client.set(
            f"{self.key_prefix}{key_hash}",
            json.dumps(key_data)
        )

# FastAPI dependencies
api_key_manager = APIKeyManager()

async def verify_api_key(api_key: str = None) -> Dict[str, Any]:
    """FastAPI dependency to verify API key."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    key_data = api_key_manager.verify_api_key(api_key)
    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limit
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    if not api_key_manager.check_rate_limit(key_hash, key_data):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return key_data
```

---

## Part 2: Secure MCP Server Implementation (25 minutes)

### Step 2.1: Secure MCP Server with Authentication
```python
# src/secure_mcp_server.py
from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security.utils import get_authorization_scheme_param
import uvicorn
import ssl
from typing import Optional, Dict, Any, Union
import json
import time
import logging
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP
from src.auth.jwt_auth import verify_token, require_permission, jwt_manager, user_manager
from src.auth.api_keys import verify_api_key, api_key_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s:%(lineno)d'
)
logger = logging.getLogger(__name__)

class SecureMCPServer:
    """Secure MCP server with multiple authentication methods."""
    
    def __init__(self):
        self.app = FastAPI(
            title="Secure MCP Server",
            description="Production-ready MCP server with comprehensive security",
            version="1.0.0"
        )
        self.mcp = FastMCP("Secure MCP Server")
        
        self._setup_middleware()
        self._setup_routes()
        self._setup_mcp_tools()
        
    def _setup_middleware(self):
        """Configure security middleware."""
        
        # CORS with strict settings
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://trusted-domain.com"],  # Specify allowed origins
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type", "X-API-Key"],
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["api.yourdomain.com", "localhost", "127.0.0.1"]
        )
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            
            # Log request
            logger.info(f"Request: {request.method} {request.url} from {request.client.host}")
            
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(f"Response: {response.status_code} in {process_time:.2f}s")
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
    
    def _setup_routes(self):
        """Set up authentication and MCP routes."""
        
        @self.app.post("/auth/login")
        async def login(credentials: Dict[str, str]):
            """Authenticate user and return JWT tokens."""
            username = credentials.get("username")
            password = credentials.get("password")
            
            if not username or not password:
                raise HTTPException(status_code=400, detail="Username and password required")
            
            user = user_manager.authenticate_user(username, password)
            if not user:
                logger.warning(f"Failed login attempt for user: {username}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            tokens = jwt_manager.create_tokens(user)
            logger.info(f"User {username} logged in successfully")
            
            return tokens
        
        @self.app.post("/auth/refresh")
        async def refresh_token(refresh_data: Dict[str, str]):
            """Refresh access token."""
            refresh_token = refresh_data.get("refresh_token")
            if not refresh_token:
                raise HTTPException(status_code=400, detail="Refresh token required")
            
            return jwt_manager.refresh_access_token(refresh_token)
        
        @self.app.post("/auth/logout")
        async def logout(current_user: Dict = Depends(verify_token)):
            """Logout user and blacklist token."""
            # Note: In real implementation, you'd get the token from the request
            logger.info(f"User {current_user['username']} logged out")
            return {"message": "Logged out successfully"}
        
        @self.app.post("/api-keys/generate")
        async def generate_api_key(
            key_request: Dict[str, Any],
            current_user: Dict = Depends(require_permission("admin"))
        ):
            """Generate new API key."""
            return api_key_manager.generate_api_key(
                user_id=current_user["sub"],
                name=key_request.get("name", "Default Key"),
                permissions=key_request.get("permissions", ["read"]),
                rate_limit=key_request.get("rate_limit")
            )
        
        @self.app.get("/api-keys")
        async def list_api_keys(current_user: Dict = Depends(verify_token)):
            """List user's API keys."""
            return api_key_manager.list_user_keys(current_user["sub"])
        
        @self.app.delete("/api-keys/{key_id}")
        async def revoke_api_key(
            key_id: str,
            current_user: Dict = Depends(verify_token)
        ):
            """Revoke an API key."""
            success = api_key_manager.revoke_api_key(key_id, current_user["sub"])
            if not success:
                raise HTTPException(status_code=404, detail="API key not found")
            return {"message": "API key revoked"}
    
    async def _authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate request using JWT or API key."""
        
        # Try API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return await verify_api_key(api_key)
        
        # Try JWT token
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, token = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer":
                return jwt_manager.verify_token(token)
        
        raise HTTPException(status_code=401, detail="Authentication required")
    
    def _setup_mcp_tools(self):
        """Set up MCP tools with security decorators."""
        
        @self.mcp.tool()
        async def secure_data_processor(
            request: Request,
            data: Dict[str, Any],
            operation: str = "process"
        ) -> Dict[str, Any]:
            """
            Process data securely with authentication.
            
            Args:
                data: Input data (validated and sanitized)
                operation: Processing operation
            
            Returns:
                Processed data with audit trail
            """
            # Authenticate request
            auth_data = await self._authenticate_request(request)
            
            # Check permissions
            if "write" not in auth_data.get("permissions", []) and "*" not in auth_data.get("permissions", []):
                raise HTTPException(status_code=403, detail="Write permission required")
            
            # Input validation
            validated_data = self._validate_input(data)
            
            # Process data
            result = {
                "operation": operation,
                "processed_data": validated_data,
                "processed_by": auth_data.get("user_id", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "audit_id": f"audit_{int(time.time())}"
            }
            
            # Audit log
            logger.info(f"Data processed by {auth_data.get('user_id')} - Audit ID: {result['audit_id']}")
            
            return result
        
        @self.mcp.tool()
        async def read_secure_data(
            request: Request,
            resource_id: str
        ) -> Dict[str, Any]:
            """
            Read secure data with authentication and authorization.
            
            Args:
                resource_id: ID of resource to read
            
            Returns:
                Resource data if authorized
            """
            # Authenticate request
            auth_data = await self._authenticate_request(request)
            
            # Check permissions (read is usually default)
            permissions = auth_data.get("permissions", [])
            if "read" not in permissions and "*" not in permissions:
                raise HTTPException(status_code=403, detail="Read permission required")
            
            # Simulate secure data access
            secure_data = {
                "resource_id": resource_id,
                "data": f"Secure data for {resource_id}",
                "accessed_by": auth_data.get("user_id"),
                "access_time": datetime.now(timezone.utc).isoformat(),
                "classification": "restricted"
            }
            
            logger.info(f"Secure data accessed: {resource_id} by {auth_data.get('user_id')}")
            
            return secure_data
    
    def _validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize input data."""
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Data must be a dictionary")
        
        # Size limits
        if len(json.dumps(data)) > 1024 * 1024:  # 1MB limit
            raise HTTPException(status_code=413, detail="Data too large")
        
        # Sanitize strings
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Basic XSS prevention
                sanitized[key] = value.replace("<", "&lt;").replace(">", "&gt;")
            else:
                sanitized[key] = value
        
        return sanitized
    
    def run(self, host: str = "0.0.0.0", port: int = 8443, ssl_cert: str = None, ssl_key: str = None):
        """Run the secure server with optional TLS."""
        
        if ssl_cert and ssl_key:
            # Run with TLS
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(ssl_cert, ssl_key)
            
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                ssl_keyfile=ssl_key,
                ssl_certfile=ssl_cert,
                ssl_version=ssl.PROTOCOL_TLS_SERVER
            )
        else:
            logger.warning("Running without TLS - not recommended for production")
            uvicorn.run(self.app, host=host, port=port)

# Create server instance
secure_server = SecureMCPServer()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Secure MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8443, help="Port to bind to")
    parser.add_argument("--ssl-cert", help="SSL certificate file")
    parser.add_argument("--ssl-key", help="SSL private key file")
    
    args = parser.parse_args()
    
    secure_server.run(
        host=args.host,
        port=args.port,
        ssl_cert=args.ssl_cert,
        ssl_key=args.ssl_key
    )
```

### Step 2.2: Input Validation and Sanitization
```python
# src/security/validators.py
import re
from typing import Any, Dict, List, Union, Optional
from fastapi import HTTPException
import bleach
from marshmallow import Schema, fields, ValidationError, validates_schema

class SecurityValidator:
    """Comprehensive input validation and sanitization."""
    
    def __init__(self):
        self.max_string_length = 10000
        self.max_array_length = 1000
        self.max_nesting_depth = 10
        
        # Dangerous patterns
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
        ]
    
    def validate_and_sanitize(self, data: Any, context: str = "general") -> Any:
        """Main validation and sanitization entry point."""
        
        # Check nesting depth
        if self._get_nesting_depth(data) > self.max_nesting_depth:
            raise HTTPException(status_code=400, detail="Data structure too deeply nested")
        
        # Validate based on type
        if isinstance(data, dict):
            return self._validate_dict(data, context)
        elif isinstance(data, list):
            return self._validate_list(data, context)
        elif isinstance(data, str):
            return self._validate_string(data, context)
        else:
            return data
    
    def _validate_dict(self, data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Validate dictionary data."""
        if len(data) > 100:  # Limit number of keys
            raise HTTPException(status_code=400, detail="Too many keys in object")
        
        validated = {}
        for key, value in data.items():
            # Validate key
            if not isinstance(key, str) or len(key) > 100:
                raise HTTPException(status_code=400, detail=f"Invalid key: {key}")
            
            # Sanitize key
            clean_key = self._sanitize_string(key)
            
            # Recursively validate value
            validated[clean_key] = self.validate_and_sanitize(value, context)
        
        return validated
    
    def _validate_list(self, data: List[Any], context: str) -> List[Any]:
        """Validate list data."""
        if len(data) > self.max_array_length:
            raise HTTPException(status_code=400, detail="Array too long")
        
        return [self.validate_and_sanitize(item, context) for item in data]
    
    def _validate_string(self, data: str, context: str) -> str:
        """Validate and sanitize string data."""
        if len(data) > self.max_string_length:
            raise HTTPException(status_code=400, detail="String too long")
        
        # Check for SQL injection
        if self._contains_sql_injection(data):
            raise HTTPException(status_code=400, detail="Potential SQL injection detected")
        
        # Check for XSS
        if self._contains_xss(data):
            raise HTTPException(status_code=400, detail="Potential XSS detected")
        
        # Sanitize based on context
        if context == "html":
            return bleach.clean(data, tags=['b', 'i', 'u', 'strong', 'em'])
        elif context == "filename":
            return re.sub(r'[<>:"/\\|?*]', '', data)
        else:
            return self._sanitize_string(data)
    
    def _sanitize_string(self, data: str) -> str:
        """Basic string sanitization."""
        # Remove null bytes
        data = data.replace('\x00', '')
        
        # Normalize whitespace
        data = re.sub(r'\s+', ' ', data).strip()
        
        return data
    
    def _contains_sql_injection(self, data: str) -> bool:
        """Check for SQL injection patterns."""
        data_lower = data.lower()
        return any(re.search(pattern, data_lower, re.IGNORECASE) 
                  for pattern in self.sql_injection_patterns)
    
    def _contains_xss(self, data: str) -> bool:
        """Check for XSS patterns."""
        return any(re.search(pattern, data, re.IGNORECASE) 
                  for pattern in self.xss_patterns)
    
    def _get_nesting_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate nesting depth of data structure."""
        if isinstance(data, (dict, list)):
            if not data:
                return current_depth + 1
            
            if isinstance(data, dict):
                return max(self._get_nesting_depth(v, current_depth + 1) 
                          for v in data.values())
            else:
                return max(self._get_nesting_depth(item, current_depth + 1) 
                          for item in data)
        else:
            return current_depth

# Marshmallow schemas for structured validation
class MCPRequestSchema(Schema):
    """Schema for MCP request validation."""
    
    jsonrpc = fields.Str(required=True, validate=lambda x: x == "2.0")
    method = fields.Str(required=True, validate=lambda x: len(x) <= 100)
    params = fields.Dict(missing={})
    id = fields.Raw(required=True)
    
    @validates_schema
    def validate_method(self, data, **kwargs):
        """Validate method name."""
        method = data.get("method", "")
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_/]*$', method):
            raise ValidationError("Invalid method name format")

class ToolCallSchema(Schema):
    """Schema for tool call validation."""
    
    name = fields.Str(required=True, validate=lambda x: len(x) <= 100)
    arguments = fields.Dict(missing={})

# Create validator instance
security_validator = SecurityValidator()
```

---

## Part 3: Audit Logging and Monitoring (15 minutes)

### Step 3.1: Security Audit System
```python
# src/security/audit.py
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import Enum
import hashlib
import os

class AuditEventType(Enum):
    """Types of audit events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SECURITY_VIOLATION = "security_violation"
    SYSTEM_EVENT = "system_event"

class SecurityAuditor:
    """Security audit logging system."""
    
    def __init__(self, log_file: str = "/var/log/mcp/security.log"):
        self.log_file = log_file
        
        # Create security logger
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)
        
        # File handler for audit logs
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # JSON formatter
        formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.propagate = False  # Don't propagate to root logger
    
    def log_event(self, 
                  event_type: AuditEventType,
                  user_id: Optional[str] = None,
                  resource: Optional[str] = None,
                  action: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  success: bool = True,
                  risk_level: str = "low") -> str:
        """Log a security audit event."""
        
        # Create unique event ID
        event_id = self._generate_event_id()
        
        # Build audit record
        audit_record = {
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "success": success,
            "risk_level": risk_level,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
            "hostname": os.uname().nodename if hasattr(os, 'uname') else "unknown"
        }
        
        # Log the event
        self.logger.info(json.dumps(audit_record))
        
        # If high risk, also log to main logger
        if risk_level in ["high", "critical"]:
            main_logger = logging.getLogger(__name__)
            main_logger.warning(f"High-risk security event: {event_id} - {event_type.value}")
        
        return event_id
    
    def log_authentication(self, user_id: str, success: bool, 
                          ip_address: str = None, details: Dict = None):
        """Log authentication attempt."""
        risk_level = "low" if success else "medium"
        action = "login_success" if success else "login_failure"
        
        return self.log_event(
            AuditEventType.AUTHENTICATION,
            user_id=user_id,
            action=action,
            success=success,
            ip_address=ip_address,
            details=details,
            risk_level=risk_level
        )
    
    def log_authorization_failure(self, user_id: str, resource: str, 
                                 required_permission: str, ip_address: str = None):
        """Log authorization failure."""
        return self.log_event(
            AuditEventType.AUTHORIZATION,
            user_id=user_id,
            resource=resource,
            action="access_denied",
            success=False,
            ip_address=ip_address,
            details={"required_permission": required_permission},
            risk_level="medium"
        )
    
    def log_data_access(self, user_id: str, resource: str, 
                       ip_address: str = None, details: Dict = None):
        """Log data access."""
        return self.log_event(
            AuditEventType.DATA_ACCESS,
            user_id=user_id,
            resource=resource,
            action="read",
            ip_address=ip_address,
            details=details
        )
    
    def log_security_violation(self, violation_type: str, user_id: str = None,
                              ip_address: str = None, details: Dict = None):
        """Log security violation."""
        return self.log_event(
            AuditEventType.SECURITY_VIOLATION,
            user_id=user_id,
            action=violation_type,
            success=False,
            ip_address=ip_address,
            details=details,
            risk_level="high"
        )
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = str(int(datetime.now().timestamp() * 1000000))
        return hashlib.sha256(timestamp.encode()).hexdigest()[:16]

# Create global auditor instance
security_auditor = SecurityAuditor()
```

---

## 🧪 Testing Your Understanding

### Quick Check Questions

1. **What is the main advantage of JWT tokens over traditional sessions?**
   - A) Better security
   - B) Stateless authentication
   - C) Smaller size
   - D) Faster processing

2. **How does API key rate limiting prevent abuse?**
   - A) By encrypting requests
   - B) By limiting requests per time window
   - C) By validating input data
   - D) By logging all requests

3. **What is the purpose of token blacklisting?**
   - A) Improve performance
   - B) Enable logout and revocation
   - C) Reduce storage needs
   - D) Simplify authentication

4. **Why is input validation important for security?**
   - A) Better performance
   - B) Prevent injection attacks
   - C) Reduce bandwidth
   - D) Improve user experience

5. **What should be logged in security audit trails?**
   - A) Only successful operations
   - B) Only failed operations
   - C) All security-relevant events
   - D) Only administrative actions

### Practical Exercise

Implement a security middleware that:
1. Detects and blocks suspicious patterns
2. Implements progressive delays for repeated failures
3. Automatically blacklists IPs with too many violations
4. Sends alerts for critical security events

```python
class SecurityMiddleware:
    """Advanced security middleware with threat detection."""
    
    def __init__(self):
        self.violation_tracking = {}
        self.ip_reputation = {}
        # TODO: Implement security logic
        pass
    
    async def process_request(self, request):
        """Process request with security checks."""
        # TODO: Implement security checks
        pass
```

---

## 📝 Session Summary

You've learned to:
- ✅ Implement JWT authentication with refresh tokens
- ✅ Create API key management with rotation
- ✅ Add comprehensive input validation
- ✅ Secure MCP servers with authentication
- ✅ Implement audit logging for security events
- ✅ Configure TLS and security middleware

### Next Session Preview
In Session 6, we'll start with ADK (Agent Development Kit):
- Create first ADK agents
- Connect agents to MCP servers
- Implement agent lifecycle management
- Build conversation agents

### Homework
1. Add OAuth 2.0 integration for third-party authentication
2. Implement RBAC (Role-Based Access Control) system
3. Create security dashboard with real-time monitoring
4. Add automated security testing suite

### Answer Key
1. B) Stateless authentication
2. B) By limiting requests per time window
3. B) Enable logout and revocation
4. B) Prevent injection attacks
5. C) All security-relevant events

---

## Additional Resources
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)