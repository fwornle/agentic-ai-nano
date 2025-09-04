# ⚙️ Session 5 Advanced: OAuth 2.1 Implementation

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths
> Time Investment: 3-4 hours
> Outcome: Master advanced OAuth 2.1 with PKCE and Resource Indicators

## Advanced Learning Outcomes

After completing this module, you will master:

- Complete OAuth 2.1 authorization server implementation  
- Advanced Resource Indicators (RFC 8707) for token scoping  
- Production-grade security with Redis-backed token management  
- Advanced JWT features including blacklisting and rotation  

## Complete OAuth 2.1 Authorization Server

Let's build a full-featured OAuth 2.1 authorization server with all the advanced security features needed for production MCP deployments.

### Foundation Setup with Security Dependencies

First, we establish our comprehensive security foundation:

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
```

This arsenal provides everything needed for enterprise-grade OAuth security:

- `authlib`: Your OAuth 2.1 Swiss Army knife with PKCE support
- `cryptography`: FIPS-compliant crypto operations
- `rfc7636`: PKCE implementation that makes authorization codes useless to eavesdroppers
- `rfc8707`: Resource Indicators that create token-specific access boundaries

### Advanced Resource Indicator System

Resource Indicators (RFC 8707) are like having magical keys that can only open specific doors. This ensures tokens can't be misused across different resources:

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
```

The `mcp://` URI scheme clearly identifies these as MCP-specific resources, preventing confusion with other OAuth resources.

Now we implement comprehensive resource validation:

```python
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
```

The validation uses set operations to efficiently check for invalid scopes, preventing tokens from gaining unintended privileges.

Creating RFC 8707 compliant tokens with proper audience restrictions:

```python
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

The `aud` (audience) claim is the key RFC 8707 feature—it ensures tokens are only valid for the specified resource.

### Enterprise JWT Management with Advanced Features

Your production JWT manager handles the complete token lifecycle with sophisticated security features:

```python
class AdvancedJWTManager:
    """Enterprise JWT management with Redis-based blacklisting and rotation."""

    def __init__(self, secret_key: str = None, redis_client = None):
        # Initialize core JWT settings
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', self._generate_secret())
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.redis_client = redis_client

        # Validate secret key security
        self._validate_secret_key()

    def _validate_secret_key(self):
        """Validate that secret key meets security requirements."""
        if len(self.secret_key) < 32:
            raise ValueError("JWT secret key must be at least 32 characters")

        if self.secret_key in ['secret', 'password', 'key']:
            raise ValueError("JWT secret key cannot be a common word")

        logger.info("JWT Manager initialized with secure secret key")
```

The validation prevents the most common JWT security mistakes: weak secrets and predictable keys.

#### Advanced Token Creation with Comprehensive Claims

When creating tokens, we craft them like carefully designed identification cards:

```python
    def create_tokens(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Create access and refresh tokens with comprehensive security claims."""
        now = datetime.now(timezone.utc)

        # Access token with comprehensive user permissions
        access_payload = {
            "sub": user_data["user_id"],           # Subject (user ID)
            "username": user_data["username"],     # Human-readable identifier
            "roles": user_data.get("roles", ["user"]),         # User roles
            "permissions": user_data.get("permissions", []),   # Specific permissions
            "iat": now,                            # Issued at time
            "exp": now + timedelta(minutes=self.access_token_expire_minutes),
            "type": "access",                      # Token type for validation
            "jti": str(uuid.uuid4())              # Unique token identifier
        }

        # Refresh token (minimal claims for security)
        refresh_payload = {
            "sub": user_data["user_id"],          # Only user ID needed
            "iat": now,                           # Issued at time
            "exp": now + timedelta(days=self.refresh_token_expire_days),
            "type": "refresh",                    # Clearly mark as refresh token
            "jti": str(uuid.uuid4())             # Unique identifier for blacklisting
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

The `jti` (JWT ID) claim enables precise token tracking and revocation—essential for production security.

#### Advanced Token Verification with Multi-Layer Security

Token verification implements comprehensive security checks:

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

            # Step 4: Additional security validations
            if not payload.get("jti"):
                raise HTTPException(status_code=401, detail="Invalid token format")

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Unexpected token verification error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
```

The four-step verification process ensures maximum security while providing clear error handling.

#### Production Token Blacklisting System

The blacklist system provides instant token revocation across distributed deployments:

```python
    def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token has been revoked via blacklist."""
        if not self.redis_client:
            return False  # No Redis = no blacklisting capability

        try:
            # Extract JTI from token for blacklist lookup
            payload = jwt.decode(
                token, self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )

            jti = payload.get("jti")
            if not jti:
                return False  # Can't blacklist tokens without JTI

            return self.redis_client.exists(f"blacklist:{jti}")

        except Exception:
            # Fail securely - log warning but allow verification to continue
            logger.warning("Could not check token blacklist")
            return False

    def blacklist_token(self, token: str, ttl_seconds: int = None):
        """Add token to blacklist for secure revocation."""
        if not self.redis_client:
            logger.warning("Cannot blacklist token: Redis not available")
            return

        try:
            # Extract JTI and expiry for efficient blacklisting
            payload = jwt.decode(
                token, self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )

            jti = payload.get("jti")
            if not jti:
                logger.warning("Cannot blacklist token without JTI")
                return

            # Auto-calculate TTL from token expiry if not provided
            if not ttl_seconds:
                ttl_seconds = self._calculate_token_ttl(payload)

            # Store JTI in blacklist with expiration
            self.redis_client.setex(f"blacklist:{jti}", ttl_seconds, "revoked")
            logger.info(f"Token successfully blacklisted for {ttl_seconds} seconds")

        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
```

Using JTI for blacklisting is more efficient than hashing the entire token and provides precise control over individual tokens.

### Complete OAuth 2.1 Authorization Flow

Now we implement the complete authorization flow with PKCE and Resource Indicators:

```python
class OAuth21AuthorizationServer:
    """Complete OAuth 2.1 authorization server with PKCE and Resource Indicators."""

    def __init__(self, jwt_manager: AdvancedJWTManager,
                 resource_manager: ResourceIndicatorManager):
        self.jwt_manager = jwt_manager
        self.resource_manager = resource_manager
        self.pkce_generator = PKCEGenerator()
        self.auth_codes = {}  # In production: use Redis

    def create_authorization_url(self, client_id: str, redirect_uri: str,
                                scope: str, resource: str = None) -> Dict[str, str]:
        """
        Create authorization URL with PKCE challenge.

        Returns URL and code verifier for client storage.
        """
        # Generate PKCE components
        code_verifier = self.pkce_generator.generate_code_verifier()
        code_challenge, challenge_method = self.pkce_generator.generate_code_challenge(code_verifier)

        # Generate authorization code
        auth_code = secrets.token_urlsafe(32)
        state = secrets.token_urlsafe(16)

        # Store authorization request details
        self.auth_codes[auth_code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "resource": resource,
            "code_challenge": code_challenge,
            "challenge_method": challenge_method,
            "expires_at": datetime.now() + timedelta(minutes=10),  # Short-lived auth codes
            "state": state
        }

        # Build authorization URL
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": challenge_method
        }

        if resource:
            params["resource"] = resource

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"/oauth/authorize?{query_string}"

        return {
            "authorization_url": auth_url,
            "code_verifier": code_verifier,  # Client must store this securely
            "state": state
        }
```

The authorization URL includes all necessary PKCE parameters and optional Resource Indicators.

#### Token Exchange with Complete Validation

The token exchange implements full PKCE verification:

```python
    def exchange_code_for_tokens(self, auth_code: str, code_verifier: str,
                                client_id: str, redirect_uri: str) -> Dict[str, str]:
        """
        Exchange authorization code for tokens with PKCE verification.

        Implements complete OAuth 2.1 with PKCE validation.
        """
        # Step 1: Validate authorization code exists and not expired
        auth_request = self.auth_codes.get(auth_code)
        if not auth_request:
            raise HTTPException(status_code=400, detail="Invalid authorization code")

        if datetime.now() > auth_request["expires_at"]:
            del self.auth_codes[auth_code]  # Clean up expired code
            raise HTTPException(status_code=400, detail="Authorization code expired")

        # Step 2: Validate client and redirect URI
        if auth_request["client_id"] != client_id:
            raise HTTPException(status_code=400, detail="Invalid client")

        if auth_request["redirect_uri"] != redirect_uri:
            raise HTTPException(status_code=400, detail="Invalid redirect URI")

        # Step 3: PKCE verification - critical security check
        stored_challenge = auth_request["code_challenge"]
        challenge_method = auth_request["challenge_method"]

        # Generate challenge from provided verifier
        calculated_challenge, _ = self.pkce_generator.generate_code_challenge(code_verifier)

        if calculated_challenge != stored_challenge:
            logger.warning(f"PKCE verification failed for client {client_id}")
            raise HTTPException(status_code=400, detail="Invalid code verifier")

        # Step 4: Create tokens with proper scoping
        user_data = {
            "user_id": f"user_{secrets.token_hex(8)}",  # In production: get from user session
            "username": "demo_user",
            "roles": ["user"],
            "permissions": auth_request["scope"].split()
        }

        # Use Resource Indicators if specified
        if auth_request.get("resource"):
            tokens = self.resource_manager.create_scoped_token(
                auth_request["resource"],
                auth_request["scope"].split(),
                user_data
            )
        else:
            tokens = self.jwt_manager.create_tokens(user_data)

        # Clean up used authorization code
        del self.auth_codes[auth_code]

        logger.info(f"Successfully exchanged code for tokens: client {client_id}")
        return tokens
```

This comprehensive implementation validates every aspect of the OAuth 2.1 flow while maintaining security throughout.

## Advanced Security Features

### Token Rotation Strategy

Implement automatic token rotation for enhanced security:

```python
    def rotate_refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Rotate refresh token for enhanced security.

        Old refresh token becomes invalid, new tokens issued.
        """
        try:
            # Verify current refresh token
            payload = jwt.decode(refresh_token, self.jwt_manager.secret_key, algorithms=["HS256"])

            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")

            # Blacklist old refresh token
            self.jwt_manager.blacklist_token(refresh_token)

            # Create new token pair
            user_data = {
                "user_id": payload["sub"],
                "username": "refreshed_user",  # In production: fetch from database
                "roles": ["user"],
                "permissions": ["read", "write"]
            }

            new_tokens = self.jwt_manager.create_tokens(user_data)
            logger.info(f"Refresh token rotated for user {payload['sub']}")

            return new_tokens

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
```

Token rotation ensures that even if refresh tokens are compromised, the exposure window is minimized.

### Security Monitoring Integration

Add comprehensive security monitoring:

```python
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-relevant events for monitoring and analysis."""
        logger.info(
            "Security event",
            event_type=event_type,
            timestamp=datetime.utcnow().isoformat(),
            **details
        )

        # In production: send to SIEM, security dashboard, etc.
        if event_type in ["failed_login", "pkce_failure", "token_misuse"]:
            # Alert on critical security events
            self._send_security_alert(event_type, details)

    def _send_security_alert(self, event_type: str, details: Dict[str, Any]):
        """Send real-time security alerts for critical events."""
        # Implementation would integrate with your alerting system
        logger.warning(f"SECURITY ALERT: {event_type}", **details)
```

Security monitoring provides visibility into potential attacks and system health.

---

## 🧭 Navigation

**Previous:** [Session 4 - Team Orchestration →](Session4_Production_MCP_Deployment.md)  
**Next:** [Session 6 - Modular Architecture →](Session6_ACP_Fundamentals.md)

---
