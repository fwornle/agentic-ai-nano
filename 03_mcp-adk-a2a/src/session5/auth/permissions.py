"""Role-based access control (RBAC) permission system."""

from enum import Enum
from typing import Set, Dict, Any
from functools import wraps
from fastapi import HTTPException


class Permission(Enum):
    """Enumeration of available permissions."""
    READ_WEATHER = "weather:read"
    WRITE_WEATHER = "weather:write"
    READ_FILES = "files:read"
    WRITE_FILES = "files:write"
    DELETE_FILES = "files:delete"
    ADMIN_USERS = "admin:users"
    VIEW_METRICS = "metrics:view"


class Role(Enum):
    """Predefined roles with permission sets."""
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.GUEST: {Permission.READ_WEATHER},
    Role.USER: {Permission.READ_WEATHER, Permission.READ_FILES},
    Role.PREMIUM: {
        Permission.READ_WEATHER, Permission.WRITE_WEATHER,
        Permission.READ_FILES, Permission.WRITE_FILES
    },
    Role.ADMIN: {perm for perm in Permission}  # All permissions
}


def get_permissions_for_roles(roles: list[str]) -> Set[str]:
    """Get all permissions for a list of roles."""
    permissions = set()
    for role_str in roles:
        try:
            role = Role(role_str)
            role_perms = ROLE_PERMISSIONS.get(role, set())
            permissions.update(perm.value for perm in role_perms)
        except ValueError:
            # Unknown role, skip
            pass
    return permissions


def require_permission(required_permission: Permission):
    """Decorator to require specific permission for MCP tool access."""
    def decorator(tool_func):
        @wraps(tool_func)
        async def wrapper(*args, **kwargs):
            # Get current user from request context (injected by middleware)
            from .middleware import get_current_user
            current_user = get_current_user()
            
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Check if user has required permission
            user_permissions = set(current_user.get("permissions", []))
            if required_permission.value not in user_permissions:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Permission '{required_permission.value}' required"
                )
            
            return await tool_func(*args, **kwargs)
        return wrapper
    return decorator


def has_permission(user_data: Dict[str, Any], permission: Permission) -> bool:
    """Check if user has specific permission."""
    user_permissions = set(user_data.get("permissions", []))
    return permission.value in user_permissions


def get_user_permissions(roles: list[str]) -> list[str]:
    """Get all permissions for user roles."""
    permissions = get_permissions_for_roles(roles)
    return list(permissions)