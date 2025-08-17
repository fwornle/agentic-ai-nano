"""JWT Authentication system for secure MCP servers."""

import jwt
import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class JWTManager:
    """JWT token management with Redis-based token blacklisting."""
    
    def __init__(self, secret_key: str = None, redis_client=None):
        self.secret_key = secret_key or self._generate_secret()
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
        """Create access and refresh tokens with proper security claims."""
        now = datetime.now(timezone.utc)
        
        # Access token with user permissions
        access_payload = {
            "sub": user_data["user_id"],
            "username": user_data["username"],
            "roles": user_data.get("roles", ["user"]),
            "permissions": user_data.get("permissions", []),
            "iat": now,
            "exp": now + timedelta(minutes=self.access_token_expire_minutes),
            "type": "access"
        }
        
        # Refresh token (minimal claims for security)
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
        """Verify and decode JWT token with blacklist checking."""
        try:
            # Check if token is blacklisted
            if self._is_token_blacklisted(token):
                raise HTTPException(status_code=401, detail="Token has been revoked")
            
            # Decode and verify token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is in the blacklist."""
        if not self.redis_client:
            return False
        
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return self.redis_client.exists(f"blacklist:{token_hash}")
        except Exception:
            logger.warning("Could not check token blacklist")
            return False
    
    def blacklist_token(self, token: str, ttl_seconds: int = None):
        """Blacklist a token (for logout/revocation)."""
        if not self.redis_client:
            return
        
        try:
            if not ttl_seconds:
                payload = jwt.decode(
                    token, self.secret_key, algorithms=[self.algorithm], 
                    options={"verify_exp": False}
                )
                exp = payload.get("exp", 0)
                ttl_seconds = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
            
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self.redis_client.setex(f"blacklist:{token_hash}", ttl_seconds, "revoked")
            
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")