# Session 5: Secure MCP Servers

## The Digital Fort Knox: Building Impenetrable MCP Servers

Picture this: You've just built the most sophisticated MCP server the world has ever seen. It can manage files, query databases, call APIs, and orchestrate complex workflows with surgical precision. But then, at 3 AM on a Tuesday, your phone buzzes with an urgent alert. Someone has breached your server, stolen sensitive data, and is using your AI agent to wreak havoc across your entire infrastructure.

This nightmare scenario is exactly why security isn't just an afterthought in MCP development—it's the foundation upon which everything else stands. Today, we're going to transform your MCP server from a sitting duck into a digital fortress that would make even the most determined attackers think twice.

*Welcome to the world of enterprise-grade MCP security, where every line of code is a guardian at the gate.*

![MCP Security Architecture](images/mcp-security-architecture.png)

---

## Part 1: The Anatomy of Digital Threats

Before we build our defenses, we need to understand our enemies. In the world of MCP servers, threats don't just knock politely at your front door—they probe every weakness, exploit every vulnerability, and strike when you least expect it.

### The Six Horsemen of the MCP Apocalypse

Imagine your MCP server as a medieval castle. These are the siege engines that attackers will use to breach your walls:

1. **Token Misuse Across Resources**: Like a master key falling into the wrong hands, a stolen token can unlock doors you never intended to open. One compromised token suddenly grants access to your entire digital kingdom.

2. **Authorization Code Interception**: Picture a messenger carrying secret scrolls being ambushed on the road. Without PKCE protection, attackers can intercept authorization codes and masquerade as legitimate users.

3. **Unintended LLM Actions**: Your AI agent receives what looks like an innocent request: "Delete some old files." But those "old files" happen to be your entire database backup. The AI, trusting by nature, complies without question.

4. **Privilege Escalation**: A humble user account somehow gains administrator privileges, like a janitor mysteriously acquiring master keys to every room in a building. Small permissions snowball into system-wide control.

5. **Distributed Rate Limit Bypass**: Attackers coordinate like a swarm of locusts, each request appearing innocent, but together overwhelming your defenses faster than you can count.

6. **Data Exfiltration**: Through carefully crafted queries that look perfectly legitimate, attackers slowly siphon your most sensitive data, one seemingly innocent API call at a time.

### The Security Standards That Stand Guard

Our fortress needs more than just thick walls—it needs a comprehensive defense system:

1. **OAuth 2.1 with PKCE**: The modern standard that treats every authorization request like a secret handshake with cryptographic verification
2. **Resource Indicators (RFC 8707)**: Tokens that can only unlock specific doors, preventing the skeleton key problem
3. **Sandbox Isolation**: Running your MCP servers in protected bubbles, where even a breach can't spread beyond its boundaries

---

## Part 1: The OAuth 2.1 Fortress

### Step 1: Building the Foundation

Let's start by implementing the 2025 MCP security standard. Think of this as laying the cornerstone of our digital fortress:

```python

# src/auth/oauth_mcp.py - 2025 MCP Security Standard

import secrets
import hashlib
import base64
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple
from authlib.integrations.fastapi_oauth2 import AuthorizationServer
from authlib.oauth2.rfc7636 import CodeChallenge
from authlib.oauth2.rfc8707 import ResourceIndicator
import redis
import structlog
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = structlog.get_logger()
```

**Our Arsenal of Security Dependencies:**

- `authlib`: Your OAuth 2.1 Swiss Army knife with PKCE support
- `cryptography`: FIPS-compliant crypto operations that even government agencies trust
- `rfc7636`: PKCE implementation that makes authorization codes useless to eavesdroppers
- `rfc8707`: Resource Indicators that create token-specific access boundaries

### Step 2: The PKCE Guardian

PKCE (Proof Key for Code Exchange) is like having a unique puzzle piece that only you can solve. Even if someone intercepts your authorization code, they can't use it without the matching piece:

```python
class PKCEGenerator:
    """RFC 7636 PKCE implementation for MCP OAuth 2.1."""
    
    @staticmethod
    def generate_code_verifier() -> str:
        """
        Generate cryptographically secure code verifier.
        
        RFC 7636 requires 43-128 character URL-safe string.
        """
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(96)
        ).decode('utf-8').rstrip('=')
        
        logger.info("Generated PKCE code verifier", length=len(code_verifier))
        return code_verifier
    
    @staticmethod 
    def generate_code_challenge(verifier: str) -> Tuple[str, str]:
        """
        Generate code challenge from verifier using SHA256.
        
        Returns: (challenge, method)
        """
        digest = hashes.Hash(hashes.SHA256())
        digest.update(verifier.encode('utf-8'))
        challenge = base64.urlsafe_b64encode(
            digest.finalize()
        ).decode('utf-8').rstrip('=')
        
        return challenge, "S256"
```

### Step 3: The Resource Sentinel

Imagine having magical keys that can only open specific doors. That's exactly what Resource Indicators accomplish—they ensure tokens can't be misused across different resources:

```python
class ResourceIndicatorManager:
    """RFC 8707 Resource Indicators for MCP token scoping."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.valid_resources = {
            'mcp://filesystem-server': {
                'description': 'File system operations',
                'scopes': ['read', 'write', 'list']
            },
            'mcp://database-server': {
                'description': 'Database operations', 
                'scopes': ['select', 'insert', 'update']
            },
            'mcp://api-server': {
                'description': 'External API calls',
                'scopes': ['call', 'webhook']
            }
        }
    
    def validate_resource_request(self, resource: str, scopes: List[str]) -> bool:
        """
        Validate resource indicator and requested scopes.
        
        Prevents tokens from being used on unintended resources.
        """
        if resource not in self.valid_resources:
            logger.warning("Invalid resource requested", resource=resource)
            return False
            
        valid_scopes = self.valid_resources[resource]['scopes']
        invalid_scopes = set(scopes) - set(valid_scopes)
        
        if invalid_scopes:
            logger.warning(
                "Invalid scopes requested", 
                resource=resource, 
                invalid_scopes=list(invalid_scopes)
            )
            return False
            
        return True
    
    def create_scoped_token(self, resource: str, scopes: List[str], 
                           user_context: Dict[str, Any]) -> str:
        """
        Create JWT token scoped to specific resource and permissions.
        
        Token can ONLY be used for the specified resource.
        """
        if not self.validate_resource_request(resource, scopes):
            raise ValueError(f"Invalid resource or scopes: {resource}")
            
        payload = {
            'aud': resource,  # RFC 8707 audience claim
            'scope': ' '.join(scopes),
            'sub': user_context['user_id'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1),
            'resource_indicator': resource,
            'context': user_context
        }
        
        token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')
        logger.info(
            "Created scoped token",
            resource=resource,
            scopes=scopes,
            user_id=user_context['user_id']
        )
        
        return token
```

### Step 4: The JWT Vault

Your JWT manager is like the most sophisticated bank vault ever built. It not only creates and validates tokens but also maintains a blacklist of revoked tokens, ensuring that even legitimate tokens can be instantly invalidated when compromised:

```python
class JWTManager:
    """JWT token management with Redis-based token blacklisting."""
    
    def __init__(self, secret_key: str = None, redis_client = None):
        # Initialize core JWT settings
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', self._generate_secret())
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.redis_client = redis_client
        
        # Validate secret key security
        self._validate_secret_key()
```

The secret key validation is like checking that your vault combination is actually secure:

```python
    def _validate_secret_key(self):
        """Validate that secret key meets security requirements."""
        if len(self.secret_key) < 32:
            raise ValueError("JWT secret key must be at least 32 characters")
        
        if self.secret_key in ['secret', 'password', 'key']:
            raise ValueError("JWT secret key cannot be a common word")
            
        logger.info("JWT Manager initialized with secure secret key")

    def _generate_secret(self) -> str:
        """Generate a secure random secret key."""
        return secrets.token_urlsafe(64)
```  

When creating tokens, we craft them like carefully designed identification cards, containing just enough information to verify identity without revealing sensitive details:

```python
    def create_tokens(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Create access and refresh tokens with proper security claims."""
        now = datetime.now(timezone.utc)
        
        # Access token with comprehensive user permissions
        access_payload = {
            "sub": user_data["user_id"],           # Subject (user ID)
            "username": user_data["username"],     # Human-readable identifier
            "roles": user_data.get("roles", ["user"]),         # User roles
            "permissions": user_data.get("permissions", []),   # Specific permissions
            "iat": now,                            # Issued at time
            "exp": now + timedelta(minutes=self.access_token_expire_minutes),
            "type": "access"                       # Token type for validation
        }

        # Refresh token (minimal claims for security)
        refresh_payload = {
            "sub": user_data["user_id"],          # Only user ID needed
            "iat": now,                           # Issued at time
            "exp": now + timedelta(days=self.refresh_token_expire_days),
            "type": "refresh"                     # Clearly mark as refresh token
        }

        # Generate JWT tokens using secure algorithm
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        # Return tokens in standard OAuth 2.0 format
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60  # Seconds until expiry
        }
```

Token verification is like having a security guard with perfect memory who never lets a fake ID slip by:

```python
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token with comprehensive security checks."""
        try:
            # Step 1: Check blacklist for revoked tokens
            if self._is_token_blacklisted(token):
                raise HTTPException(status_code=401, detail="Token has been revoked")
            
            # Step 2: Cryptographically verify and decode
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Step 3: Validate token type to prevent confusion attacks
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Unexpected token verification error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
```

The blacklist system works like a master "do not admit" list that security guards check before allowing anyone through:

```python
    def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token has been revoked via blacklist."""
        if not self.redis_client:
            return False  # No Redis = no blacklisting capability
        
        try:
            # Hash token to avoid storing sensitive data
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return self.redis_client.exists(f"blacklist:{token_hash}")
        except Exception:
            # Fail securely - log warning but allow access
            logger.warning("Could not check token blacklist")
            return False

    def blacklist_token(self, token: str, ttl_seconds: int = None):
        """Add token to blacklist for secure revocation."""
        if not self.redis_client:
            logger.warning("Cannot blacklist token: Redis not available")
            return
        
        try:
            # Auto-calculate TTL from token expiry if not provided
            if not ttl_seconds:
                ttl_seconds = self._calculate_token_ttl(token)
            
            # Store hashed token in blacklist with expiration
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self.redis_client.setex(f"blacklist:{token_hash}", ttl_seconds, "revoked")
            logger.info(f"Token successfully blacklisted for {ttl_seconds} seconds")
            
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")

    def _calculate_token_ttl(self, token: str) -> int:
        """Calculate remaining TTL for token based on expiry."""
        try:
            # Decode without verifying expiry to get exp claim
            payload = jwt.decode(
                token, self.secret_key, 
                algorithms=[self.algorithm], 
                options={"verify_exp": False}
            )
            exp = payload.get("exp", 0)
            current_time = int(datetime.now(timezone.utc).timestamp())
            return max(0, exp - current_time)  # Ensure non-negative TTL
        except Exception:
            # Default to token expiry time if calculation fails
            return self.access_token_expire_minutes * 60
```

### The Permission Kingdom: Role-Based Access Control (RBAC)

Imagine your MCP server as a vast kingdom with different areas requiring different levels of access. RBAC is like having a sophisticated court system where each person's role determines exactly which doors they can open and which actions they can perform.

```python

# src/auth/permissions.py

from enum import Enum
from typing import List, Set, Dict
from functools import wraps
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class Permission(Enum):
    """Fine-grained permissions for MCP server resources."""
    READ_WEATHER = "weather:read"
    WRITE_WEATHER = "weather:write"
    READ_FILES = "files:read"
    WRITE_FILES = "files:write"
    DELETE_FILES = "files:delete"
    ADMIN_USERS = "admin:users"
    VIEW_METRICS = "metrics:view"
```

The role hierarchy works like a medieval court structure, where each level inherits the privileges of those below:

```python
class Role(Enum):
    """Hierarchical roles from least to most privileged."""
    GUEST = "guest"        # Read-only basic access
    USER = "user"          # Standard user capabilities  
    PREMIUM = "premium"    # Enhanced features
    ADMIN = "admin"        # Full system access

# Progressive permission assignment by role

ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.GUEST: {
        Permission.READ_WEATHER  # Basic read access only
    },
    Role.USER: {
        Permission.READ_WEATHER, 
        Permission.READ_FILES    # Add file reading
    },
    Role.PREMIUM: {
        Permission.READ_WEATHER, Permission.WRITE_WEATHER,
        Permission.READ_FILES, Permission.WRITE_FILES  # Full weather + files
    },
    Role.ADMIN: {
        perm for perm in Permission  # All permissions
    }
}
```

The permission validation system is like having a perfectly organized access control list:

```python
def has_permission(user_permissions: List[str], required_permission: Permission) -> bool:
    """Check if user has specific permission."""
    return required_permission.value in user_permissions

def get_user_permissions(user_roles: List[str]) -> Set[Permission]:
    """Get all permissions for user's roles."""
    permissions = set()
    for role_name in user_roles:
        try:
            role = Role(role_name)
            permissions.update(ROLE_PERMISSIONS.get(role, set()))
        except ValueError:
            logger.warning(f"Unknown role: {role_name}")
    return permissions
```

The permission decorator acts like a security checkpoint that verifies credentials before allowing access to protected resources:

```python
def require_permission(required_permission: Permission):
    """Decorator to enforce permission requirements on MCP tools."""
    def decorator(tool_func):
        @wraps(tool_func)
        async def wrapper(*args, **kwargs):
            # Extract user context from request
            current_user = get_current_user()
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Validate user has required permission
            user_permissions = current_user.get("permissions", [])
            if not has_permission(user_permissions, required_permission):
                logger.warning(
                    f"Permission denied: User {current_user.get('username')} "
                    f"attempted {required_permission.value}"
                )

                raise HTTPException(
                    status_code=403, 
                    detail=f"Permission '{required_permission.value}' required"
                )
            
            return await tool_func(*args, **kwargs)
        return wrapper
    return decorator
```

### The Security Middleware: Your Digital Bouncer

Think of the authentication middleware as the most vigilant bouncer at the most exclusive club. They check every person at the door, verify their credentials, and ensure only authorized individuals gain entry:

```python

# src/auth/middleware.py

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

class MCPAuthMiddleware:
    """Centralized authentication middleware for MCP server security."""
    
    def __init__(self, jwt_manager: JWTManager):
        self.jwt_manager = jwt_manager
        self.security = HTTPBearer(auto_error=False)  # Custom error handling
        self.excluded_paths = {"/health", "/metrics"}  # Skip auth for monitoring
```

The header extraction process is like carefully examining each visitor's identification:

```python
    def _extract_bearer_token(self, request: Request) -> str:
        """Safely extract and validate Bearer token from headers."""
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            raise HTTPException(
                status_code=401, 
                detail="Authorization header required"
            )
        
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401, 
                detail="Bearer token format required"
            )

        # Extract token (handle malformed headers safely)
        parts = auth_header.split(" ")
        if len(parts) != 2:
            raise HTTPException(
                status_code=401, 
                detail="Invalid authorization header format"
            )
        
        return parts[1]
```

The authentication process combines all security checks into one comprehensive verification:

```python
    async def authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Authenticate incoming MCP request with comprehensive validation."""
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            return None
        
        start_time = time.time()
        
        try:
            # Step 1: Extract token from headers
            token = self._extract_bearer_token(request)
            
            # Step 2: Verify token cryptographically
            payload = self.jwt_manager.verify_token(token)

            # Step 3: Log successful authentication
            auth_duration = (time.time() - start_time) * 1000
            logger.info(
                f"Authentication successful: {payload.get('username')} "
                f"(ID: {payload.get('sub')}) in {auth_duration:.2f}ms"
            )
            
            return payload

        except HTTPException:
            # Re-raise HTTP exceptions (already properly formatted)
            raise
        except Exception as e:
            # Log security-relevant errors and fail securely
            logger.error(
                f"Authentication failure from {request.client.host if request.client else 'unknown'}: {e}",
                extra={"request_path": request.url.path, "user_agent": request.headers.get("User-Agent")}
            )
            raise HTTPException(
                status_code=401, 
                detail="Authentication failed"
            )
```

### The Secure MCP Server: Bringing It All Together

Now we combine all our security components into a fortress-like MCP server that can withstand the most determined attacks:

```python

# src/secure_mcp_server.py

from mcp.server.fastmcp import FastMCP
from src.auth.jwt_auth import JWTManager
from src.auth.permissions import require_permission, Permission
from src.auth.middleware import MCPAuthMiddleware
from typing import Dict, List
import re
import os
from pathlib import Path

class SecureMCPServer:
    """Production-ready MCP server with comprehensive security."""
    
    def __init__(self, name: str = "Secure MCP Server"):
        # Core components initialization
        self.mcp = FastMCP(name)
        self.jwt_manager = JWTManager()
        self.auth_middleware = MCPAuthMiddleware(self.jwt_manager)
        
        # Security configuration
        self.allowed_file_patterns = [r'^/tmp/.*\.txt$', r'^/data/.*\.(json|csv)$']
        self.setup_security_tools()
```

Each MCP tool becomes a secured endpoint with appropriate permission checks:

```python
    def setup_security_tools(self):
        """Configure MCP tools with appropriate security controls."""
        
        @self.mcp.tool()
        @require_permission(Permission.READ_WEATHER)
        async def get_weather(city: str) -> Dict:
            """Get weather data - requires weather:read permission."""
            # Input validation
            if not city or len(city) > 100:
                raise HTTPException(status_code=400, detail="Invalid city name")
            
            # Simulated weather API call
            return {
                "city": city, 
                "temperature": 22, 
                "condition": "Sunny",
                "timestamp": datetime.now().isoformat()
            }

        @self.mcp.tool()
        @require_permission(Permission.WRITE_FILES)
        async def write_file(path: str, content: str) -> Dict:
            """Write file with path validation and size limits."""
            # Security validations
            if not self._validate_file_path(path):
                raise HTTPException(status_code=400, detail="File path not allowed")
            
            if len(content) > 1024 * 1024:  # 1MB limit
                raise HTTPException(status_code=400, detail="File too large")
            
            # Secure file writing logic would go here
            return {"success": True, "path": path, "size": len(content)}

        @self.mcp.tool()
        @require_permission(Permission.ADMIN_USERS)
        async def list_users() -> List[Dict]:
            """List system users - admin only."""
            # This would typically query a database
            return [
                {"id": 1, "username": "admin", "role": "admin", "active": True},
                {"id": 2, "username": "user1", "role": "user", "active": True}
            ]
    
    def _validate_file_path(self, path: str) -> bool:
        """Validate file path against security patterns."""
        return any(re.match(pattern, path) for pattern in self.allowed_file_patterns)
```

---

## Part 2: The API Key Arsenal

In the world of machine-to-machine communication, API keys are like diplomatic passports—they need to be secure, verifiable, and easily revocable when compromised. Let's build a system that treats each API key like a precious artifact.

### The API Key Vault

Our API key manager is like having a high-security vault that can generate, store, and validate millions of unique keys while maintaining perfect security:

```python

# src/auth/api_keys.py

import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import uuid
import logging

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Secure API key management with Redis storage and automatic expiration."""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.key_prefix = "api_key:"
        self.default_expiry_days = 90
        self.key_length = 32  # 32 bytes = 256 bits of entropy
```

The key generation process is like minting a new currency—each key must be absolutely unique and impossible to predict:

```python
    def _generate_secure_key(self) -> tuple[str, str]:
        """Generate cryptographically secure API key and ID."""
        key_id = str(uuid.uuid4())
        # Format: mcp_<base64-url-safe-32-bytes>
        api_key = f"mcp_{secrets.token_urlsafe(self.key_length)}"
        return key_id, api_key
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
```

Each API key comes with comprehensive metadata, like a detailed passport with all necessary information:

```python
    def _create_key_metadata(self, key_id: str, user_id: str, name: str, 
                            permissions: List[str], expiry_days: int) -> Dict:
        """Create comprehensive metadata for API key."""
        now = datetime.now()
        return {
            "key_id": key_id,
            "user_id": user_id,
            "name": name[:100],  # Limit name length
            "permissions": permissions,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=expiry_days)).isoformat(),
            "last_used": None,
            "usage_count": 0,
            "active": True,
            "created_by": "system"  # Track creation source
        }
```

The complete key generation process combines security with usability:

```python
    def generate_api_key(self, user_id: str, name: str, permissions: List[str], 
                        expires_in_days: int = None) -> Dict[str, str]:
        """Generate a new API key with full security metadata."""
        # Input validation
        if not user_id or not name:
            raise ValueError("User ID and name are required")
        
        if not permissions:
            raise ValueError("At least one permission must be specified")
        
        # Generate secure key components
        key_id, api_key = self._generate_secure_key()
        key_hash = self._hash_api_key(api_key)

        # Create metadata and store securely
        expiry_days = expires_in_days or self.default_expiry_days
        metadata = self._create_key_metadata(key_id, user_id, name, permissions, expiry_days)
        
        # Store in Redis with automatic expiration
        self._store_key_metadata(key_hash, metadata, expiry_days)
        
        logger.info(f"Generated API key {key_id} for user {user_id}")
        return {
            "api_key": api_key,
            "key_id": key_id,
            "expires_at": metadata["expires_at"]
        }

    def _store_key_metadata(self, key_hash: str, metadata: Dict, expiry_days: int):
        """Securely store key metadata in Redis with TTL."""
        try:
            ttl_seconds = expiry_days * 24 * 60 * 60
            self.redis_client.setex(
                f"{self.key_prefix}{key_hash}",
                ttl_seconds,
                json.dumps(metadata)
            )
        except Exception as e:
            logger.error(f"Failed to store API key metadata: {e}")
            raise RuntimeError("Could not store API key")
```

The validation system works like having a security expert examine each key for authenticity and freshness:

```python
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key with comprehensive security checks."""
        # Step 1: Format validation
        if not self._is_valid_key_format(api_key):
            return None
        
        try:
            # Step 2: Retrieve and validate metadata
            metadata = self._get_key_metadata(api_key)
            if not metadata:
                return None

            # Step 3: Check key status and update usage
            if self._is_key_active(metadata):
                self._update_key_usage(api_key, metadata)
                return metadata
            
            return None
            
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return None

    def _is_valid_key_format(self, api_key: str) -> bool:
        """Validate API key format and structure."""
        if not api_key or not isinstance(api_key, str):
            return False
        
        # Check prefix and length
        if not api_key.startswith("mcp_"):
            logger.warning(f"Invalid API key prefix from request")
            return False
        
        # Expected length: "mcp_" + 32 URL-safe base64 chars = ~47 chars
        if len(api_key) < 40 or len(api_key) > 60:
            logger.warning(f"Invalid API key length: {len(api_key)}")
            return False
        
        return True

    def _get_key_metadata(self, api_key: str) -> Optional[Dict]:
        """Securely retrieve key metadata from storage."""
        key_hash = self._hash_api_key(api_key)
        
        try:
            metadata_json = self.redis_client.get(f"{self.key_prefix}{key_hash}")
            if not metadata_json:
                logger.info(f"API key not found in storage")
                return None
            
            metadata = json.loads(metadata_json)
            return metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted API key metadata: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve API key metadata: {e}")
            return None

    def _is_key_active(self, metadata: Dict) -> bool:
        """Check if API key is still active and valid."""
        # Check active flag
        if not metadata.get("active", False):
            logger.info(f"API key {metadata.get('key_id')} is deactivated")
            return False
        
        # Check expiration (additional safety check)
        expires_at = metadata.get("expires_at")
        if expires_at:
            try:
                expiry = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                if datetime.now() > expiry.replace(tzinfo=None):
                    logger.info(f"API key {metadata.get('key_id')} has expired")
                    return False
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid expiry date format: {e}")
                return False
        
        return True

    def _update_key_usage(self, api_key: str, metadata: Dict):
        """Update key usage statistics atomically."""
        try:
            key_hash = self._hash_api_key(api_key)
            redis_key = f"{self.key_prefix}{key_hash}"
            
            # Update usage statistics
            metadata["last_used"] = datetime.now().isoformat()
            metadata["usage_count"] = metadata.get("usage_count", 0) + 1
            
            # Preserve existing TTL
            ttl = self.redis_client.ttl(redis_key)
            if ttl > 0:
                self.redis_client.setex(redis_key, ttl, json.dumps(metadata))

            else:
                # Fallback: use default expiry
                self.redis_client.setex(
                    redis_key, 
                    self.default_expiry_days * 24 * 60 * 60, 
                    json.dumps(metadata)
                )
                
        except Exception as e:
            # Usage tracking failure shouldn't block authentication
            logger.warning(f"Failed to update key usage statistics: {e}")
```

---

## Part 3: The Rate Limiting Shield

Imagine your MCP server is a popular restaurant during rush hour. Without proper crowd control, you'd be overwhelmed by orders faster than you could process them. Rate limiting is your digital bouncer, ensuring everyone gets served fairly while preventing any single customer from monopolizing the kitchen.

### The Token Bucket: Nature's Perfect Algorithm

The token bucket algorithm mimics how nature handles resource distribution. Think of it as a magical bucket that fills with tokens at a steady rate. Each request needs a token to proceed, and when the bucket empties, requests must wait for new tokens to arrive.

```python

# src/security/rate_limiter.py

import time
import json
import logging
from typing import Optional, Dict
import redis

logger = logging.getLogger(__name__)

class TokenBucketRateLimiter:
    """Token bucket rate limiter with Redis backend for distributed rate limiting."""
    
    def __init__(self, redis_client, default_capacity: int = 100, 
                 default_refill_rate: float = 10):
        self.redis_client = redis_client
        self.default_capacity = default_capacity
        self.default_refill_rate = default_refill_rate  # tokens per second
        self.bucket_prefix = "rate_limit:"
        self.bucket_ttl = 3600  # 1 hour cleanup TTL
```

The bucket state management is like checking how much water is currently in a bucket and when it was last filled:

```python
    def _get_bucket_state(self, bucket_key: str) -> tuple[float, float]:
        """Retrieve current bucket state from Redis."""
        try:
            bucket_data = self.redis_client.get(bucket_key)
            
            if bucket_data:
                bucket = json.loads(bucket_data)
                return bucket["last_refill"], bucket["tokens"]
            else:
                # Initialize new bucket - start with full capacity
                return time.time(), float(self.default_capacity)
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Corrupted bucket data for {bucket_key}: {e}")
            return time.time(), float(self.default_capacity)
```

The token calculation algorithm is the heart of the system—it determines exactly how many tokens should be available at any moment:

```python
    def _calculate_tokens(self, last_refill: float, current_tokens: float, 
                         current_time: float, capacity: int, refill_rate: float) -> float:
        """Calculate current token count using bucket algorithm."""
        # Calculate time elapsed since last refill
        time_elapsed = max(0, current_time - last_refill)
        
        # Calculate tokens to add (rate * time)
        tokens_to_add = time_elapsed * refill_rate
        
        # Add tokens but don't exceed capacity (bucket overflow)
        new_tokens = min(float(capacity), current_tokens + tokens_to_add)
        
        return new_tokens
```

The authorization check is where the magic happens—deciding whether to grant or deny each request:

```python
    async def is_allowed(self, identifier: str, capacity: int = None, 
                        refill_rate: float = None) -> bool:
        """Check if request should be allowed based on rate limit."""
        # Use provided limits or defaults
        capacity = capacity or self.default_capacity
        refill_rate = refill_rate or self.default_refill_rate
        
        bucket_key = f"{self.bucket_prefix}{identifier}"
        current_time = time.time()
        
        try:
            # Step 1: Get current bucket state
            last_refill, current_tokens = self._get_bucket_state(bucket_key)
            
            # Step 2: Calculate available tokens
            available_tokens = self._calculate_tokens(
                last_refill, current_tokens, current_time, capacity, refill_rate
            )

            # Step 3: Check if request can be allowed
            if available_tokens >= 1.0:
                # Allow request and consume token
                remaining_tokens = available_tokens - 1.0
                allowed = True
            else:
                # Deny request, no tokens consumed
                remaining_tokens = available_tokens
                allowed = False
            
            # Step 4: Update bucket state
            self._update_bucket_state(bucket_key, current_time, remaining_tokens)
            
            return allowed

        except Exception as e:
            logger.error(f"Rate limiting error for {identifier}: {e}")
            return True  # Fail open - availability over strict rate limiting

    def _update_bucket_state(self, bucket_key: str, timestamp: float, tokens: float):
        """Update bucket state in Redis with TTL."""
        try:
            new_bucket = {
                "tokens": tokens,
                "last_refill": timestamp
            }
            
            self.redis_client.setex(
                bucket_key, 
                self.bucket_ttl,
                json.dumps(new_bucket)
            )
            
        except Exception as e:
            logger.error(f"Failed to update bucket state for {bucket_key}: {e}")
```

### The Hierarchical Rate Limiting System

Different users deserve different levels of service. Think of it like airline seating—economy, business, and first class all get to the same destination, but with very different experiences along the way:

```python
class RateLimitMiddleware:
    """Role-based rate limiting middleware for MCP servers."""
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter):
        self.rate_limiter = rate_limiter
        
        # Hierarchical rate limits by user role
        self.limits = {
            "guest": {"capacity": 50, "refill_rate": 1},     # Very restrictive
            "user": {"capacity": 200, "refill_rate": 5},     # Standard limits
            "premium": {"capacity": 1000, "refill_rate": 20}, # Enhanced limits
            "admin": {"capacity": 5000, "refill_rate": 100}   # High limits
        }

    def _get_rate_limits(self, user_data: Dict) -> tuple[str, Dict]:
        """Determine user identifier and appropriate rate limits."""
        # Extract primary role (use first role if multiple)
        user_roles = user_data.get("roles", ["guest"])
        primary_role = user_roles[0] if user_roles else "guest"
        
        # Create unique identifier for this user
        user_id = user_data.get("sub", "anonymous")
        identifier = f"user:{user_id}"
        
        # Get limits for this role (fallback to guest if unknown role)
        limits = self.limits.get(primary_role, self.limits["guest"])
        
        return identifier, limits

    async def check_rate_limit(self, request: Request, user_data: Dict) -> bool:
        """Enforce rate limits and block excessive requests."""
        # Determine user limits
        identifier, limits = self._get_rate_limits(user_data)
        
        # Apply rate limiting
        allowed = await self.rate_limiter.is_allowed(
            identifier,
            capacity=limits["capacity"],
            refill_rate=limits["refill_rate"]
        )
        
        if not allowed:
            # Log rate limit violation
            logger.warning(
                f"Rate limit exceeded: {identifier} "
                f"(role: {user_data.get('roles', ['unknown'])[0]})"
            )
            
            # Return standardized rate limit response
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}  # Suggest retry after 60 seconds
            )
        
        return True
```

---

## The Security Arsenal: Summary of Your Digital Fortress

Congratulations! You've just built a comprehensive security system that would make even the most paranoid security expert proud. Let's admire what we've accomplished:

**Your Digital Fortress Now Includes:**

- **OAuth 2.1 with PKCE authentication and Resource Indicators (RFC 8707)**: Like having quantum-encrypted keys that only work for specific doors
- **JWT token system with access/refresh tokens and blacklisting**: A sophisticated ID system with instant revocation capabilities
- **API key management with automatic expiration and usage tracking**: Diplomatic passports for your machines, complete with audit trails
- **Role-based access control (RBAC) with fine-grained permissions**: A royal court system where everyone knows their place and privileges
- **Rate limiting using token bucket algorithm with role-based limits**: Fair resource distribution that prevents any single user from overwhelming the system
- **Input validation and secure error handling**: Careful examination of everything that enters your fortress
- **Comprehensive audit logging and security monitoring**: A security team that never sleeps and remembers everything

---

## Testing Your Security Knowledge

Before we move on, let's make sure you understand the critical concepts that keep your MCP server safe:

### Security Concepts Check

1. **Why use short-lived access tokens (30 minutes)?** - B) Limit exposure if compromised
2. **What's the purpose of token blacklisting?** - B) Enable secure logout and token revocation  
3. **How does the token bucket algorithm work?** - C) Allows bursts but limits average rate
4. **Why hash API keys in storage?** - C) Prevent key theft from database breaches
5. **What is fail-secure design?** - B) Always deny access when systems fail  

### Your Security Challenge

Now it's your turn to add to the fortress. Implement a security audit system that tracks suspicious activity patterns and alerts administrators to potential threats:

```python
@mcp.tool()
@require_permission(Permission.VIEW_METRICS)
async def get_security_audit(time_range: str = "24h") -> Dict:
    """
    Get security audit information for the specified time range.
    
    TODO: Implement audit system that tracks:
    1. Failed authentication attempts
    2. Permission denied events  
    3. Rate limit violations
    4. Unusual access patterns
    
    Args:
        time_range: Time range for audit (1h, 24h, 7d)
        
    Returns:
        Security audit report with metrics and alerts
    """
    # Your implementation here
    pass
```

---

**Next:** [Session 6 - ACP Fundamentals](Session6_ACP_Fundamentals.md)

---

## Test Your Fortress: Multiple Choice Challenge

**Question 1:** What's the best security approach for MCP servers? - C) Defense-in-depth with multiple security layers

**Question 2:** What's the minimum JWT secret key length? - C) 32 characters

**Question 3:** How should refresh tokens be handled? - D) Use Redis with automatic expiration and blacklisting

**Question 4:** What's the best rate limiting algorithm for MCP servers? - D) Token bucket

**Question 5:** What's the main advantage of role-based permissions? - C) Easier management and scalability

**Question 6:** How should MCP tool input validation be implemented? - A) Server-side validation using Pydantic models

**Question 7:** What's the minimum TLS version for production MCP servers? - D) TLS 1.2

**Question 8:** How should API key rotation be handled? - B) Automatic rotation with overlap periods

**Question 9:** What should be logged in security audit trails? - D) Authentication events and permission changes

**Question 10:** What's the best DDoS protection technique? - C) Implementing multiple rate limiting layers

[**🗂️ View Test Solutions →**](Session5_Test_Solutions.md)

---

## Navigation

**Previous:** [Session 4 - Production MCP Deployment](Session4_Production_MCP_Deployment.md)

**Next:** [Session 6 - ACP Fundamentals →](Session6_ACP_Fundamentals.md)

---

## Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)  
- [JWT Security Best Practices](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/)  
- [Redis Security Guidelines](https://redis.io/docs/manual/security/)  
- [Python Cryptography Documentation](https://cryptography.io/en/latest/)  
- [FastAPI Security Patterns](https://fastapi.tiangolo.com/tutorial/security/)
