"""
Configuration Management for A2A Communication

This module provides centralized configuration management for the A2A
communication system, including agent settings, registry configuration,
and system parameters.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RedisConfig:
    """Redis configuration for agent registry."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    health_check_interval: int = 30


@dataclass
class RegistryConfig:
    """Agent registry configuration."""
    use_redis: bool = True
    redis_config: RedisConfig = field(default_factory=RedisConfig)
    heartbeat_interval: int = 30  # seconds
    heartbeat_timeout: int = 90   # seconds
    cleanup_interval: int = 60    # seconds
    max_agents: int = 1000


@dataclass
class RouterConfig:
    """Message router configuration."""
    default_timeout: int = 30     # seconds
    max_retries: int = 3
    retry_delay: float = 1.0      # seconds
    max_queue_size: int = 10000
    use_http_transport: bool = True
    http_timeout: int = 30        # seconds


@dataclass
class ChoreographyConfig:
    """Choreography engine configuration."""
    max_event_history: int = 1000
    cleanup_interval: int = 300   # seconds
    pattern_timeout: int = 30     # seconds
    event_ttl: int = 3600        # seconds


@dataclass
class AgentConfig:
    """Base agent configuration."""
    max_concurrent_tasks: int = 10
    health_check_interval: int = 60  # seconds
    metrics_update_interval: int = 30  # seconds
    default_timeout: int = 30       # seconds
    max_retries: int = 3


@dataclass
class CustomerServiceConfig:
    """Customer service agent configuration."""
    base_config: AgentConfig = field(default_factory=AgentConfig)
    max_tickets: int = 20
    escalation_threshold: int = 3    # failed attempts before escalation
    response_time_sla: int = 300    # seconds
    satisfaction_threshold: float = 3.0  # out of 5.0


@dataclass
class TechnicalSupportConfig:
    """Technical support agent configuration."""
    base_config: AgentConfig = field(default_factory=AgentConfig)
    max_issues: int = 10
    diagnostic_timeout: int = 300   # seconds
    solution_timeout: int = 1800    # seconds
    escalation_severity: str = "high"  # minimum severity for auto-escalation
    specializations: List[str] = field(default_factory=lambda: ["general_technical"])


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_encryption: bool = False
    encryption_key: Optional[str] = None
    enable_authentication: bool = True
    api_key_header: str = "X-API-Key"
    rate_limit_requests: int = 1000  # per hour
    rate_limit_window: int = 3600    # seconds
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = True
    log_file: str = "a2a_system.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_structured_logging: bool = False


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_port: int = 8080
    enable_tracing: bool = False
    jaeger_endpoint: Optional[str] = None
    prometheus_endpoint: Optional[str] = None


@dataclass
class A2ASystemConfig:
    """Complete A2A system configuration."""
    registry: RegistryConfig = field(default_factory=RegistryConfig)
    router: RouterConfig = field(default_factory=RouterConfig)
    choreography: ChoreographyConfig = field(default_factory=ChoreographyConfig)
    customer_service: CustomerServiceConfig = field(default_factory=CustomerServiceConfig)
    technical_support: TechnicalSupportConfig = field(default_factory=TechnicalSupportConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Environment settings
    environment: str = "development"  # development, staging, production
    debug: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2ASystemConfig':
        """Create configuration from dictionary."""
        
        def create_dataclass_from_dict(dataclass_type, data_dict):
            """Recursively create dataclass instances from dictionaries."""
            if not isinstance(data_dict, dict):
                return data_dict
            
            field_types = {field.name: field.type for field in dataclass_type.__dataclass_fields__.values()}
            kwargs = {}
            
            for key, value in data_dict.items():
                if key in field_types:
                    field_type = field_types[key]
                    
                    # Handle nested dataclasses
                    if hasattr(field_type, '__dataclass_fields__'):
                        kwargs[key] = create_dataclass_from_dict(field_type, value)
                    else:
                        kwargs[key] = value
            
            return dataclass_type(**kwargs)
        
        # Handle nested configurations
        config_data = data.copy()
        
        for field_name, field_info in cls.__dataclass_fields__.items():
            if field_name in config_data and hasattr(field_info.type, '__dataclass_fields__'):
                config_data[field_name] = create_dataclass_from_dict(
                    field_info.type, 
                    config_data[field_name]
                )
        
        return cls(**config_data)
    
    def save_to_file(self, filepath: str):
        """Save configuration to a JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Configuration saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {filepath}: {e}")
            raise
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'A2ASystemConfig':
        """Load configuration from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"Configuration loaded from {filepath}")
            return cls.from_dict(data)
        except FileNotFoundError:
            logger.warning(f"Configuration file {filepath} not found, using defaults")
            return cls()
        except Exception as e:
            logger.error(f"Failed to load configuration from {filepath}: {e}")
            raise
    
    def update_from_env(self):
        """Update configuration from environment variables."""
        
        # Registry configuration
        if os.getenv("REDIS_HOST"):
            self.registry.redis_config.host = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT"):
            self.registry.redis_config.port = int(os.getenv("REDIS_PORT"))
        if os.getenv("REDIS_PASSWORD"):
            self.registry.redis_config.password = os.getenv("REDIS_PASSWORD")
        
        # Router configuration
        if os.getenv("ROUTER_TIMEOUT"):
            self.router.default_timeout = int(os.getenv("ROUTER_TIMEOUT"))
        if os.getenv("ROUTER_MAX_RETRIES"):
            self.router.max_retries = int(os.getenv("ROUTER_MAX_RETRIES"))
        
        # Security configuration
        if os.getenv("ENABLE_ENCRYPTION"):
            self.security.enable_encryption = os.getenv("ENABLE_ENCRYPTION").lower() == "true"
        if os.getenv("ENCRYPTION_KEY"):
            self.security.encryption_key = os.getenv("ENCRYPTION_KEY")
        if os.getenv("API_KEY_HEADER"):
            self.security.api_key_header = os.getenv("API_KEY_HEADER")
        
        # Environment settings
        if os.getenv("A2A_ENVIRONMENT"):
            self.environment = os.getenv("A2A_ENVIRONMENT")
        if os.getenv("DEBUG"):
            self.debug = os.getenv("DEBUG").lower() == "true"
        
        # Logging configuration
        if os.getenv("LOG_LEVEL"):
            self.logging.level = os.getenv("LOG_LEVEL").upper()
        if os.getenv("LOG_FILE"):
            self.logging.log_file = os.getenv("LOG_FILE")
        
        logger.info("Configuration updated from environment variables")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Validate registry configuration
        if self.registry.heartbeat_timeout <= self.registry.heartbeat_interval:
            issues.append("Registry heartbeat_timeout must be greater than heartbeat_interval")
        
        if self.registry.redis_config.port < 1 or self.registry.redis_config.port > 65535:
            issues.append("Redis port must be between 1 and 65535")
        
        # Validate router configuration
        if self.router.default_timeout <= 0:
            issues.append("Router default_timeout must be positive")
        
        if self.router.max_retries < 0:
            issues.append("Router max_retries cannot be negative")
        
        # Validate choreography configuration
        if self.choreography.max_event_history <= 0:
            issues.append("Choreography max_event_history must be positive")
        
        if self.choreography.event_ttl <= 0:
            issues.append("Choreography event_ttl must be positive")
        
        # Validate agent configurations
        if self.customer_service.max_tickets <= 0:
            issues.append("Customer service max_tickets must be positive")
        
        if self.technical_support.max_issues <= 0:
            issues.append("Technical support max_issues must be positive")
        
        # Validate security configuration
        if self.security.enable_encryption and not self.security.encryption_key:
            issues.append("Encryption key required when encryption is enabled")
        
        if self.security.rate_limit_requests <= 0:
            issues.append("Rate limit requests must be positive")
        
        # Validate logging configuration
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging.level not in valid_log_levels:
            issues.append(f"Log level must be one of: {', '.join(valid_log_levels)}")
        
        # Validate monitoring configuration
        if self.monitoring.metrics_port < 1024 or self.monitoring.metrics_port > 65535:
            issues.append("Metrics port should be between 1024 and 65535")
        
        if self.monitoring.health_check_port == self.monitoring.metrics_port:
            issues.append("Health check port must be different from metrics port")
        
        return issues
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration overrides."""
        
        if self.environment == "production":
            return {
                "debug": False,
                "logging": {"level": "WARNING"},
                "security": {
                    "enable_encryption": True,
                    "enable_authentication": True,
                    "rate_limit_requests": 100
                },
                "registry": {"heartbeat_interval": 15},
                "router": {"max_retries": 5}
            }
        elif self.environment == "staging":
            return {
                "debug": False,
                "logging": {"level": "INFO"},
                "security": {
                    "enable_encryption": False,
                    "enable_authentication": True
                }
            }
        else:  # development
            return {
                "debug": True,
                "logging": {"level": "DEBUG"},
                "security": {
                    "enable_encryption": False,
                    "enable_authentication": False
                }
            }
    
    def apply_environment_config(self):
        """Apply environment-specific configuration overrides."""
        
        env_config = self.get_environment_config()
        
        def update_nested_dict(target, updates):
            """Recursively update nested dictionary."""
            for key, value in updates.items():
                if key in target.__dict__:
                    if isinstance(value, dict) and hasattr(target.__dict__[key], '__dict__'):
                        update_nested_dict(target.__dict__[key], value)
                    else:
                        setattr(target, key, value)
        
        update_nested_dict(self, env_config)
        logger.info(f"Applied {self.environment} environment configuration")


class ConfigurationManager:
    """Configuration manager for the A2A system."""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._get_default_config_file()
        self._config: Optional[A2ASystemConfig] = None
    
    def _get_default_config_file(self) -> str:
        """Get default configuration file path."""
        
        # Check environment variable first
        if os.getenv("A2A_CONFIG_FILE"):
            return os.getenv("A2A_CONFIG_FILE")
        
        # Check common locations
        possible_paths = [
            "a2a_config.json",
            "./config/a2a_config.json",
            str(Path.home() / ".a2a" / "config.json"),
            "/etc/a2a/config.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return "a2a_config.json"  # Default
    
    def load_config(self) -> A2ASystemConfig:
        """Load configuration from file and environment."""
        
        if self._config is None:
            # Load from file
            self._config = A2ASystemConfig.load_from_file(self.config_file)
            
            # Update from environment
            self._config.update_from_env()
            
            # Apply environment-specific settings
            self._config.apply_environment_config()
            
            # Validate configuration
            issues = self._config.validate()
            if issues:
                error_msg = "Configuration validation failed:\n" + "\n".join(f"- {issue}" for issue in issues)
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Configuration loaded successfully for {self._config.environment} environment")
        
        return self._config
    
    def save_config(self, config: A2ASystemConfig = None):
        """Save configuration to file."""
        
        config_to_save = config or self._config
        if config_to_save is None:
            raise ValueError("No configuration to save")
        
        config_to_save.save_to_file(self.config_file)
    
    def reload_config(self) -> A2ASystemConfig:
        """Reload configuration from file."""
        
        self._config = None
        return self.load_config()
    
    def get_config(self) -> A2ASystemConfig:
        """Get current configuration, loading if necessary."""
        
        if self._config is None:
            return self.load_config()
        
        return self._config
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values."""
        
        if self._config is None:
            self.load_config()
        
        # Apply updates (simplified - in production you might want more sophisticated merging)
        config_dict = self._config.to_dict()
        config_dict.update(updates)
        self._config = A2ASystemConfig.from_dict(config_dict)
        
        logger.info("Configuration updated")


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager(config_file: str = None) -> ConfigurationManager:
    """Get the global configuration manager instance."""
    
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_file)
    
    return _config_manager


def get_config() -> A2ASystemConfig:
    """Get the current system configuration."""
    
    return get_config_manager().get_config()


def create_sample_config() -> A2ASystemConfig:
    """Create a sample configuration for testing/development."""
    
    config = A2ASystemConfig()
    
    # Development environment settings
    config.environment = "development"
    config.debug = True
    
    # Use in-memory storage for development
    config.registry.use_redis = False
    
    # Relaxed security for development
    config.security.enable_encryption = False
    config.security.enable_authentication = False
    
    # Verbose logging for development
    config.logging.level = "DEBUG"
    
    return config


def save_sample_config(filepath: str = "sample_config.json"):
    """Save a sample configuration file."""
    
    config = create_sample_config()
    config.save_to_file(filepath)
    logger.info(f"Sample configuration saved to {filepath}")


# Configuration validation utilities
def validate_redis_connection(redis_config: RedisConfig) -> bool:
    """Validate Redis connection configuration."""
    
    try:
        import redis
        
        client = redis.Redis(
            host=redis_config.host,
            port=redis_config.port,
            db=redis_config.db,
            password=redis_config.password,
            decode_responses=redis_config.decode_responses,
            socket_timeout=redis_config.socket_timeout,
            socket_connect_timeout=redis_config.socket_connect_timeout
        )
        
        client.ping()
        return True
        
    except ImportError:
        logger.warning("Redis not available - using in-memory storage")
        return False
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False


def setup_logging(logging_config: LoggingConfig):
    """Setup logging based on configuration."""
    
    import logging.handlers
    
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, logging_config.level))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(logging_config.format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if enabled
    if logging_config.enable_file_logging:
        file_handler = logging.handlers.RotatingFileHandler(
            logging_config.log_file,
            maxBytes=logging_config.max_file_size,
            backupCount=logging_config.backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    logger.info(f"Logging configured - level: {logging_config.level}")


# Example usage
if __name__ == "__main__":
    # Create and save sample configuration
    save_sample_config()
    
    # Load and validate configuration
    config_manager = ConfigurationManager("sample_config.json")
    config = config_manager.load_config()
    
    print("Configuration loaded successfully!")
    print(f"Environment: {config.environment}")
    print(f"Debug mode: {config.debug}")
    print(f"Registry uses Redis: {config.registry.use_redis}")