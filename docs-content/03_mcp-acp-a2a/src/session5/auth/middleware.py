"""Authentication middleware for MCP servers."""

import logging
from typing import Dict, Any, Optional
from contextvars import ContextVar
from fastapi import Request, HTTPException
from .jwt_auth import JWTManager

logger = logging.getLogger(__name__)

# Context variable to store current user across request
_current_user: ContextVar[Optional[Dict[str, Any]]] = ContextVar('current_user', default=None)


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current user from request context."""
    return _current_user.get()


def set_current_user(user_data: Dict[str, Any]):
    """Set current user in request context."""
    _current_user.set(user_data)


class MCPAuthMiddleware:
    """Authentication middleware for MCP servers."""
    
    def __init__(self, jwt_manager: JWTManager):
        self.jwt_manager = jwt_manager
    
    async def authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate incoming MCP request."""
        try:
            # Extract Bearer token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=401, 
                    detail="Missing or invalid authorization header"
                )
            
            token = auth_header.split(" ")[1]
            
            # Verify and decode token
            payload = self.jwt_manager.verify_token(token)
            
            # Set user in context
            set_current_user(payload)
            
            # Log successful authentication
            logger.info(
                f"Authenticated user: {payload.get('username')} "
                f"(ID: {payload.get('sub')})"
            )
            
            return payload
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    async def authenticate_api_key(self, request: Request, api_key_manager) -> Dict[str, Any]:
        """Authenticate request using API key."""
        try:
            # Extract API key from X-API-Key header
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                raise HTTPException(status_code=401, detail="API key required")
            
            # Validate API key
            metadata = api_key_manager.validate_api_key(api_key)
            if not metadata:
                raise HTTPException(status_code=401, detail="Invalid API key")
            
            # Create user context from API key metadata
            user_data = {
                "sub": metadata["user_id"],
                "username": f"api_key_{metadata['name']}",
                "roles": ["user"],  # Default role for API keys
                "permissions": metadata.get("permissions", []),
                "auth_method": "api_key"
            }
            
            # Set user in context
            set_current_user(user_data)
            
            logger.info(f"API key authenticated: {metadata['name']}")
            return user_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"API key authentication error: {e}")
            raise HTTPException(status_code=401, detail="API key authentication failed")
    
    def clear_current_user(self):
        """Clear current user context."""
        set_current_user(None)