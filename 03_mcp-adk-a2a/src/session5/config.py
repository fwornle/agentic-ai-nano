"""Configuration management for secure MCP server."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class SecurityConfig:
    """Security configuration for MCP server."""
    
    # JWT Configuration
    jwt_secret_key: str = None
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # Rate Limiting
    default_rate_limit_capacity: int = 100
    default_rate_limit_refill_rate: float = 10.0
    
    # File Security
    max_file_size: int = 1024 * 1024  # 1MB
    allowed_file_extensions: set = None
    
    # Audit System
    audit_retention_days: int = 7
    enable_audit_logging: bool = True
    
    # API Keys
    api_key_expiry_days: int = 90
    enable_api_key_rotation: bool = True
    
    def __post_init__(self):
        """Initialize configuration from environment variables."""
        # Load from environment
        self.jwt_secret_key = self.jwt_secret_key or os.getenv("JWT_SECRET_KEY")
        self.redis_host = os.getenv("REDIS_HOST", self.redis_host)
        self.redis_port = int(os.getenv("REDIS_PORT", str(self.redis_port)))
        self.redis_password = os.getenv("REDIS_PASSWORD", self.redis_password)
        
        # File security defaults
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = {".txt", ".json", ".csv", ".md", ".log"}
        
        # Validate critical settings
        if not self.jwt_secret_key:
            import secrets
            self.jwt_secret_key = secrets.token_urlsafe(64)
            print("WARNING: Using auto-generated JWT secret. Set JWT_SECRET_KEY for production.")
    
    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Create configuration from environment variables."""
        return cls()
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if len(self.jwt_secret_key) < 32:
            raise ValueError("JWT secret key must be at least 32 characters")
        
        if self.jwt_access_token_expire_minutes < 5:
            raise ValueError("Access token expiry must be at least 5 minutes")
        
        if self.max_file_size > 10 * 1024 * 1024:  # 10MB
            raise ValueError("Max file size should not exceed 10MB")
        
        return True


# Default configuration instance
default_config = SecurityConfig()