"""
Configuration Management - Session 8
Configuration settings for advanced workflow systems.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Environment types for configuration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    database: str = "workflow_db"
    username: str = "workflow_user"
    password: str = "workflow_password"
    pool_size: int = 10
    max_overflow: int = 20
    ssl_mode: str = "prefer"
    connection_timeout: int = 30


@dataclass
class RedisConfig:
    """Redis configuration settings."""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    connection_pool_size: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True


@dataclass
class WorkflowConfig:
    """Workflow engine configuration."""
    max_concurrent_workflows: int = 100
    max_concurrent_steps: int = 500
    default_workflow_timeout: int = 3600  # 1 hour
    default_step_timeout: int = 300       # 5 minutes
    retry_attempts: int = 3
    retry_delay: int = 5
    enable_checkpointing: bool = True
    checkpoint_interval: int = 300        # 5 minutes
    failure_strategy: str = "fail_fast"   # fail_fast, continue, retry


@dataclass
class ParallelProcessingConfig:
    """Parallel processing configuration."""
    default_strategy: str = "async_tasks"  # async_tasks, thread_pool, process_pool, hybrid
    max_workers: int = 10
    batch_size: int = 5
    timeout_per_task: int = 300
    enable_load_balancing: bool = True
    retry_failed_tasks: bool = True
    max_retries: int = 3


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration."""
    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_system_monitoring: bool = True
    system_monitor_interval: int = 5      # seconds
    enable_performance_tracking: bool = True
    enable_alerts: bool = True
    alert_check_interval: int = 30        # seconds
    retention_days: int = 30


@dataclass
class StateManagementConfig:
    """State management configuration."""
    storage_type: str = "sqlite"          # memory, sqlite, redis, file
    sqlite_db_path: str = "workflow_state.db"
    redis_key_prefix: str = "workflow:"
    auto_checkpoint_interval: int = 300   # 5 minutes
    auto_cleanup_interval: int = 3600     # 1 hour
    default_ttl: int = 86400              # 24 hours
    max_states_per_workflow: int = 1000


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    enable_authentication: bool = True
    enable_authorization: bool = True
    jwt_secret_key: str = "your-secret-key-here"
    jwt_expiration_hours: int = 24
    api_rate_limit: int = 1000            # requests per hour
    enable_api_keys: bool = True
    require_https: bool = False           # Set to True in production
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = True
    log_file_path: str = "logs/workflow.log"
    max_file_size_mb: int = 100
    backup_count: int = 5
    enable_json_logging: bool = False
    enable_structured_logging: bool = True


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    enable_cors: bool = True
    enable_swagger: bool = True
    request_timeout: int = 30
    max_request_size_mb: int = 100
    enable_compression: bool = True


class ConfigurationManager:
    """Manages application configuration from multiple sources."""
    
    def __init__(self, config_dir: str = "config", environment: Optional[str] = None):
        self.config_dir = Path(config_dir)
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.config_data: Dict[str, Any] = {}
        
        # Load configuration
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from files and environment variables."""
        # Load base configuration
        base_config_file = self.config_dir / "base.json"
        if base_config_file.exists():
            with open(base_config_file, 'r') as f:
                self.config_data.update(json.load(f))
        
        # Load environment-specific configuration
        env_config_file = self.config_dir / f"{self.environment}.json"
        if env_config_file.exists():
            with open(env_config_file, 'r') as f:
                env_config = json.load(f)
                self._deep_update(self.config_data, env_config)
        
        # Override with environment variables
        self._load_from_environment()
        
        logger.info(f"Configuration loaded for environment: {self.environment}")
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Deep update of nested dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def _load_from_environment(self):
        """Load configuration values from environment variables."""
        env_mappings = {
            # Database
            "DATABASE_HOST": ["database", "host"],
            "DATABASE_PORT": ["database", "port"],
            "DATABASE_NAME": ["database", "database"],
            "DATABASE_USER": ["database", "username"],
            "DATABASE_PASSWORD": ["database", "password"],
            
            # Redis
            "REDIS_HOST": ["redis", "host"],
            "REDIS_PORT": ["redis", "port"],
            "REDIS_PASSWORD": ["redis", "password"],
            
            # Workflow
            "MAX_CONCURRENT_WORKFLOWS": ["workflow", "max_concurrent_workflows"],
            "DEFAULT_TIMEOUT": ["workflow", "default_workflow_timeout"],
            
            # Security
            "JWT_SECRET": ["security", "jwt_secret_key"],
            "ENABLE_HTTPS": ["security", "require_https"],
            
            # API
            "API_HOST": ["api", "host"],
            "API_PORT": ["api", "port"],
            "DEBUG": ["api", "debug"]
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(self.config_data, config_path, env_value)
    
    def _set_nested_value(self, data: Dict[str, Any], path: List[str], value: Any):
        """Set a nested dictionary value using a path."""
        current = data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        final_key = path[-1]
        if isinstance(value, str):
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
        
        current[final_key] = value
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        db_config = self.config_data.get("database", {})
        return DatabaseConfig(
            host=db_config.get("host", "localhost"),
            port=db_config.get("port", 5432),
            database=db_config.get("database", "workflow_db"),
            username=db_config.get("username", "workflow_user"),
            password=db_config.get("password", "workflow_password"),
            pool_size=db_config.get("pool_size", 10),
            max_overflow=db_config.get("max_overflow", 20),
            ssl_mode=db_config.get("ssl_mode", "prefer"),
            connection_timeout=db_config.get("connection_timeout", 30)
        )
    
    def get_redis_config(self) -> RedisConfig:
        """Get Redis configuration."""
        redis_config = self.config_data.get("redis", {})
        return RedisConfig(
            host=redis_config.get("host", "localhost"),
            port=redis_config.get("port", 6379),
            database=redis_config.get("database", 0),
            password=redis_config.get("password"),
            connection_pool_size=redis_config.get("connection_pool_size", 10),
            socket_timeout=redis_config.get("socket_timeout", 5),
            socket_connect_timeout=redis_config.get("socket_connect_timeout", 5),
            retry_on_timeout=redis_config.get("retry_on_timeout", True)
        )
    
    def get_workflow_config(self) -> WorkflowConfig:
        """Get workflow configuration."""
        workflow_config = self.config_data.get("workflow", {})
        return WorkflowConfig(
            max_concurrent_workflows=workflow_config.get("max_concurrent_workflows", 100),
            max_concurrent_steps=workflow_config.get("max_concurrent_steps", 500),
            default_workflow_timeout=workflow_config.get("default_workflow_timeout", 3600),
            default_step_timeout=workflow_config.get("default_step_timeout", 300),
            retry_attempts=workflow_config.get("retry_attempts", 3),
            retry_delay=workflow_config.get("retry_delay", 5),
            enable_checkpointing=workflow_config.get("enable_checkpointing", True),
            checkpoint_interval=workflow_config.get("checkpoint_interval", 300),
            failure_strategy=workflow_config.get("failure_strategy", "fail_fast")
        )
    
    def get_parallel_processing_config(self) -> ParallelProcessingConfig:
        """Get parallel processing configuration."""
        parallel_config = self.config_data.get("parallel_processing", {})
        return ParallelProcessingConfig(
            default_strategy=parallel_config.get("default_strategy", "async_tasks"),
            max_workers=parallel_config.get("max_workers", 10),
            batch_size=parallel_config.get("batch_size", 5),
            timeout_per_task=parallel_config.get("timeout_per_task", 300),
            enable_load_balancing=parallel_config.get("enable_load_balancing", True),
            retry_failed_tasks=parallel_config.get("retry_failed_tasks", True),
            max_retries=parallel_config.get("max_retries", 3)
        )
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        monitoring_config = self.config_data.get("monitoring", {})
        return MonitoringConfig(
            enable_metrics=monitoring_config.get("enable_metrics", True),
            metrics_port=monitoring_config.get("metrics_port", 9090),
            enable_system_monitoring=monitoring_config.get("enable_system_monitoring", True),
            system_monitor_interval=monitoring_config.get("system_monitor_interval", 5),
            enable_performance_tracking=monitoring_config.get("enable_performance_tracking", True),
            enable_alerts=monitoring_config.get("enable_alerts", True),
            alert_check_interval=monitoring_config.get("alert_check_interval", 30),
            retention_days=monitoring_config.get("retention_days", 30)
        )
    
    def get_state_management_config(self) -> StateManagementConfig:
        """Get state management configuration."""
        state_config = self.config_data.get("state_management", {})
        return StateManagementConfig(
            storage_type=state_config.get("storage_type", "sqlite"),
            sqlite_db_path=state_config.get("sqlite_db_path", "workflow_state.db"),
            redis_key_prefix=state_config.get("redis_key_prefix", "workflow:"),
            auto_checkpoint_interval=state_config.get("auto_checkpoint_interval", 300),
            auto_cleanup_interval=state_config.get("auto_cleanup_interval", 3600),
            default_ttl=state_config.get("default_ttl", 86400),
            max_states_per_workflow=state_config.get("max_states_per_workflow", 1000)
        )
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        security_config = self.config_data.get("security", {})
        return SecurityConfig(
            enable_authentication=security_config.get("enable_authentication", True),
            enable_authorization=security_config.get("enable_authorization", True),
            jwt_secret_key=security_config.get("jwt_secret_key", "your-secret-key-here"),
            jwt_expiration_hours=security_config.get("jwt_expiration_hours", 24),
            api_rate_limit=security_config.get("api_rate_limit", 1000),
            enable_api_keys=security_config.get("enable_api_keys", True),
            require_https=security_config.get("require_https", False),
            allowed_origins=security_config.get("allowed_origins", ["*"])
        )
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        logging_config = self.config_data.get("logging", {})
        return LoggingConfig(
            level=logging_config.get("level", "INFO"),
            format=logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            enable_file_logging=logging_config.get("enable_file_logging", True),
            log_file_path=logging_config.get("log_file_path", "logs/workflow.log"),
            max_file_size_mb=logging_config.get("max_file_size_mb", 100),
            backup_count=logging_config.get("backup_count", 5),
            enable_json_logging=logging_config.get("enable_json_logging", False),
            enable_structured_logging=logging_config.get("enable_structured_logging", True)
        )
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration."""
        api_config = self.config_data.get("api", {})
        return APIConfig(
            host=api_config.get("host", "0.0.0.0"),
            port=api_config.get("port", 8080),
            debug=api_config.get("debug", False),
            enable_cors=api_config.get("enable_cors", True),
            enable_swagger=api_config.get("enable_swagger", True),
            request_timeout=api_config.get("request_timeout", 30),
            max_request_size_mb=api_config.get("max_request_size_mb", 100),
            enable_compression=api_config.get("enable_compression", True)
        )
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key_path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set_config_value(self, key_path: str, value: Any):
        """Set a configuration value using dot notation."""
        keys = key_path.split('.')
        self._set_nested_value(self.config_data, keys, value)
    
    def reload_configuration(self):
        """Reload configuration from files."""
        self.config_data.clear()
        self._load_configuration()
        logger.info("Configuration reloaded")
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return any errors."""
        errors = []
        
        # Validate required configurations
        required_configs = [
            "database.host",
            "database.database",
            "security.jwt_secret_key"
        ]
        
        for config_key in required_configs:
            if self.get_config_value(config_key) is None:
                errors.append(f"Missing required configuration: {config_key}")
        
        # Validate value ranges
        if self.get_config_value("workflow.max_concurrent_workflows", 0) <= 0:
            errors.append("workflow.max_concurrent_workflows must be greater than 0")
        
        if self.get_config_value("api.port", 0) <= 0 or self.get_config_value("api.port", 0) > 65535:
            errors.append("api.port must be between 1 and 65535")
        
        # Validate security settings for production
        if self.environment == EnvironmentType.PRODUCTION.value:
            if not self.get_config_value("security.require_https", False):
                errors.append("HTTPS should be required in production")
            
            if self.get_config_value("security.jwt_secret_key") == "your-secret-key-here":
                errors.append("Default JWT secret key should not be used in production")
        
        return errors
    
    def export_configuration(self, file_path: str):
        """Export current configuration to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.config_data, f, indent=2, default=str)
        logger.info(f"Configuration exported to {file_path}")
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information."""
        return {
            "environment": self.environment,
            "config_dir": str(self.config_dir),
            "loaded_files": [
                str(self.config_dir / "base.json"),
                str(self.config_dir / f"{self.environment}.json")
            ],
            "config_keys": list(self.config_data.keys())
        }


# Global configuration instance
config_manager: Optional[ConfigurationManager] = None


def get_config() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global config_manager
    if config_manager is None:
        config_manager = ConfigurationManager()
    return config_manager


def initialize_config(config_dir: str = "config", environment: Optional[str] = None) -> ConfigurationManager:
    """Initialize the global configuration manager."""
    global config_manager
    config_manager = ConfigurationManager(config_dir, environment)
    return config_manager