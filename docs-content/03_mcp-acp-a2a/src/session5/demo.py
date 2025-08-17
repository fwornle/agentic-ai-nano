"""Demo script showing secure MCP server usage."""

import asyncio
import logging
from secure_mcp_server import SecureMCPServer
from config import SecurityConfig
from auth.permissions import Permission, Role, get_user_permissions

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_secure_mcp_server():
    """Demonstrate secure MCP server functionality."""
    
    # Create configuration
    config = SecurityConfig()
    config.validate()
    
    # Initialize secure server
    server = SecureMCPServer(config)
    
    # Demo user data
    demo_user = {
        "user_id": "demo_user_123",
        "username": "demo_user",
        "roles": ["user"],
        "permissions": get_user_permissions(["user"])
    }
    
    # Create JWT tokens
    tokens = server.jwt_manager.create_tokens(demo_user)
    logger.info(f"Created tokens for user: {demo_user['username']}")
    logger.info(f"Access token expires in: {tokens['expires_in']} seconds")
    
    # Verify token
    try:
        payload = server.jwt_manager.verify_token(tokens["access_token"])
        logger.info(f"Token verified for user: {payload['username']}")
        logger.info(f"User permissions: {payload['permissions']}")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
    
    # Demo security status
    status = server.get_security_status()
    logger.info("Security status:")
    for feature, enabled in status["security_features"].items():
        logger.info(f"  {feature}: {'✓' if enabled else '✗'}")
    
    # Demo audit logging
    server.audit_system.log_security_event(
        server.audit_system.SecurityEventType.LOGIN_SUCCESS,
        user_id=demo_user["user_id"],
        details={"demo": True, "username": demo_user["username"]}
    )
    
    logger.info("Secure MCP server demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(demo_secure_mcp_server())