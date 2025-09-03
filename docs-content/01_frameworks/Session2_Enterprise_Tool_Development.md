# ⚙️ Session 2: Enterprise Tool Development

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete [🎯 Observer Path](Session2_LangChain_Foundations.md) and [📝 Participant Path](Session2_Practical_Implementation.md)
> Time Investment: 2-3 hours
> Outcome: Master custom tool development, enterprise integrations, and advanced tool orchestration patterns

## Advanced Learning Outcomes

After completing this enterprise tool development module, you will master:

- Advanced tool development patterns for enterprise data systems integration  
- Custom tool orchestration and composition strategies  
- Enterprise authentication and security patterns for tool access  
- Performance optimization techniques for high-throughput tool operations  
- Monitoring and observability frameworks for tool ecosystem management  

## Enterprise Tool Architecture Patterns

Production agent systems require sophisticated tool architectures that integrate seamlessly with existing enterprise infrastructure while providing robust error handling, monitoring, and security controls.

### Advanced Tool Development Framework

Create a comprehensive framework for enterprise tool development with standardized patterns:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
import logging
from contextlib import asynccontextmanager

class ToolCategory(Enum):
    DATA_ACCESS = "data_access"
    DATA_PROCESSING = "data_processing"
    MONITORING = "monitoring"
    INTEGRATION = "integration"
    COMMUNICATION = "communication"
    SECURITY = "security"

class ToolPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass
class ToolMetrics:
    """Comprehensive tool performance metrics"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    last_call_timestamp: Optional[str] = None
    last_error: Optional[str] = None
    last_success_timestamp: Optional[str] = None

@dataclass
class ToolConfiguration:
    """Enterprise tool configuration with validation"""
    name: str
    description: str
    category: ToolCategory
    priority: ToolPriority
    max_retries: int = 3
    timeout_seconds: int = 30
    rate_limit_calls_per_minute: int = 60
    auth_required: bool = True
    audit_enabled: bool = True
    caching_enabled: bool = False
    cache_ttl_seconds: int = 300
    dependencies: List[str] = field(default_factory=list)
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 60

class EnterpriseToolBase(ABC):
    """Base class for all enterprise tools with comprehensive framework support"""

    def __init__(self, config: ToolConfiguration):
        self.config = config
        self.metrics = ToolMetrics()
        self.logger = logging.getLogger(f"tool.{config.name}")
        self.rate_limiter = RateLimiter(config.rate_limit_calls_per_minute)
        self.cache = ToolCache() if config.caching_enabled else None
        self.health_status = "unknown"
        self.last_health_check = None

        # Initialize monitoring
        self._setup_monitoring()

    def _setup_monitoring(self):
        """Initialize comprehensive monitoring for the tool"""

        # Setup performance monitoring
        self.performance_monitor = ToolPerformanceMonitor(self.config.name)

        # Setup health monitoring if enabled
        if self.config.health_check_enabled:
            self.health_monitor = ToolHealthMonitor(
                self.config.name,
                self.config.health_check_interval_seconds,
                self._perform_health_check
            )

    @abstractmethod
    async def _execute_core_functionality(self, **kwargs) -> Any:
        """Core tool functionality - implemented by subclasses"""
        pass

    @abstractmethod
    def _perform_health_check(self) -> Dict[str, Any]:
        """Perform tool-specific health check"""
        pass

    async def execute(self, auth_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute tool with comprehensive enterprise controls"""

        execution_start = time.time()
        call_id = str(uuid.uuid4())

        try:
            # Pre-execution validations
            await self._validate_execution_preconditions(auth_context, kwargs)

            # Rate limiting
            await self.rate_limiter.acquire()

            # Check cache if enabled
            if self.cache:
                cache_key = self._generate_cache_key(kwargs)
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    self.metrics.successful_calls += 1
                    return self._format_success_response(cached_result, from_cache=True)

            # Execute with timeout and retries
            result = await self._execute_with_retries(auth_context, **kwargs)

            # Cache result if caching enabled
            if self.cache and result:
                cache_key = self._generate_cache_key(kwargs)
                await self.cache.set(cache_key, result, self.config.cache_ttl_seconds)

            # Update metrics
            execution_time = time.time() - execution_start
            self._update_success_metrics(execution_time)

            # Audit logging
            if self.config.audit_enabled:
                await self._log_audit_event("tool_execution_success", {
                    "call_id": call_id,
                    "execution_time": execution_time,
                    "auth_context": auth_context.get("user_id", "unknown"),
                    "input_params": list(kwargs.keys())
                })

            return self._format_success_response(result)

        except Exception as e:
            # Update failure metrics
            execution_time = time.time() - execution_start
            self._update_failure_metrics(execution_time, str(e))

            # Audit logging for failures
            if self.config.audit_enabled:
                await self._log_audit_event("tool_execution_failure", {
                    "call_id": call_id,
                    "execution_time": execution_time,
                    "error": str(e),
                    "auth_context": auth_context.get("user_id", "unknown")
                })

            return self._format_error_response(str(e), call_id)

    async def _validate_execution_preconditions(self, auth_context: Dict[str, Any], params: Dict[str, Any]):
        """Validate all preconditions before tool execution"""

        # Authentication validation
        if self.config.auth_required and not auth_context.get("authenticated", False):
            raise PermissionError("Authentication required for tool execution")

        # Authorization validation
        required_permissions = self._get_required_permissions()
        user_permissions = auth_context.get("permissions", [])

        if required_permissions and not any(perm in user_permissions for perm in required_permissions):
            raise PermissionError(f"Insufficient permissions. Required: {required_permissions}")

        # Parameter validation
        required_params = self._get_required_parameters()
        missing_params = [param for param in required_params if param not in params]

        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")

        # Dependency health check
        await self._validate_dependencies()

    async def _execute_with_retries(self, auth_context: Dict[str, Any], **kwargs) -> Any:
        """Execute tool with retry logic and timeout"""

        for attempt in range(self.config.max_retries + 1):
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._execute_core_functionality(**kwargs),
                    timeout=self.config.timeout_seconds
                )

                return result

            except asyncio.TimeoutError:
                if attempt == self.config.max_retries:
                    raise TimeoutError(f"Tool execution timeout after {self.config.timeout_seconds} seconds")

                self.logger.warning(f"Attempt {attempt + 1} timed out, retrying...")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                if attempt == self.config.max_retries:
                    raise e

                # Check if error is retryable
                if not self._is_retryable_error(e):
                    raise e

                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}, retrying...")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable"""

        retryable_error_types = [
            ConnectionError,
            TimeoutError,
            # Add more retryable error types as needed
        ]

        return any(isinstance(error, error_type) for error_type in retryable_error_types)

    @abstractmethod
    def _get_required_permissions(self) -> List[str]:
        """Get list of required permissions for tool execution"""
        pass

    @abstractmethod
    def _get_required_parameters(self) -> List[str]:
        """Get list of required parameters for tool execution"""
        pass

    def _update_success_metrics(self, execution_time: float):
        """Update metrics for successful execution"""

        self.metrics.total_calls += 1
        self.metrics.successful_calls += 1
        self.metrics.total_execution_time += execution_time
        self.metrics.average_execution_time = self.metrics.total_execution_time / self.metrics.total_calls
        self.metrics.last_call_timestamp = datetime.now().isoformat()
        self.metrics.last_success_timestamp = datetime.now().isoformat()

    def _update_failure_metrics(self, execution_time: float, error: str):
        """Update metrics for failed execution"""

        self.metrics.total_calls += 1
        self.metrics.failed_calls += 1
        self.metrics.total_execution_time += execution_time
        self.metrics.average_execution_time = self.metrics.total_execution_time / self.metrics.total_calls
        self.metrics.last_call_timestamp = datetime.now().isoformat()
        self.metrics.last_error = error

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""

        return {
            "tool_name": self.config.name,
            "health_status": self.health_status,
            "last_health_check": self.last_health_check,
            "metrics": {
                "total_calls": self.metrics.total_calls,
                "success_rate": self.metrics.successful_calls / max(1, self.metrics.total_calls),
                "average_execution_time": self.metrics.average_execution_time,
                "last_success": self.metrics.last_success_timestamp,
                "last_error": self.metrics.last_error
            },
            "configuration": {
                "category": self.config.category.value,
                "priority": self.config.priority.value,
                "timeout": self.config.timeout_seconds,
                "max_retries": self.config.max_retries
            }
        }

class RateLimiter:
    """Token bucket rate limiter for tool execution"""

    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.tokens = calls_per_minute
        self.last_refill = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to execute (blocks if rate limited)"""

        async with self.lock:
            now = time.time()

            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            tokens_to_add = elapsed * (self.calls_per_minute / 60.0)
            self.tokens = min(self.calls_per_minute, self.tokens + tokens_to_add)
            self.last_refill = now

            # If no tokens available, wait
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) * (60.0 / self.calls_per_minute)
                await asyncio.sleep(sleep_time)
                self.tokens = 1

            # Consume token
            self.tokens -= 1

class ToolCache:
    """Simple in-memory cache for tool results"""

    def __init__(self):
        self.cache = {}
        self.expiry = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""

        if key not in self.cache:
            return None

        if key in self.expiry and time.time() > self.expiry[key]:
            del self.cache[key]
            del self.expiry[key]
            return None

        return self.cache[key]

    async def set(self, key: str, value: Any, ttl_seconds: int):
        """Set cached value with TTL"""

        self.cache[key] = value
        self.expiry[key] = time.time() + ttl_seconds
```

## Enterprise Data Integration Tools

Create sophisticated tools for integrating with enterprise data systems including data warehouses, streaming platforms, and ML pipelines.

### Advanced Data Warehouse Integration Tool

Implement a production-ready data warehouse tool with connection pooling, query optimization, and comprehensive error handling:

```python
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import pandas as pd
from typing import Union, List, Dict

class EnterpriseDataWarehouseTool(EnterpriseToolBase):
    """Production-ready data warehouse integration tool"""

    def __init__(self, config: ToolConfiguration, connection_config: Dict[str, Any]):
        super().__init__(config)

        self.connection_config = connection_config
        self.engine = self._create_database_engine()
        self.query_cache = {}
        self.query_optimizer = QueryOptimizer()

        # Query templates for common operations
        self.query_templates = {
            "table_info": "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = :table_name",
            "table_stats": "SELECT COUNT(*) as row_count, COUNT(DISTINCT :column) as unique_values FROM :table_name",
            "data_quality": """
                SELECT
                    COUNT(*) as total_rows,
                    COUNT(*) - COUNT(:column) as null_count,
                    COUNT(DISTINCT :column) as unique_count
                FROM :table_name
            """
        }

    def _create_database_engine(self) -> sqlalchemy.Engine:
        """Create optimized database engine with connection pooling"""

        connection_string = self._build_connection_string()

        engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Validate connections before use
            pool_recycle=3600,   # Recycle connections every hour
            echo=False  # Set to True for SQL debugging
        )

        return engine

    def _build_connection_string(self) -> str:
        """Build secure connection string from configuration"""

        db_type = self.connection_config["type"]  # postgres, snowflake, bigquery, etc.
        host = self.connection_config["host"]
        port = self.connection_config["port"]
        database = self.connection_config["database"]
        username = self.connection_config["username"]
        password = self.connection_config["password"]

        if db_type == "postgresql":
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == "snowflake":
            account = self.connection_config["account"]
            warehouse = self.connection_config["warehouse"]
            return f"snowflake://{username}:{password}@{account}/{database}/{warehouse}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    async def _execute_core_functionality(self, query: str = None, operation: str = None, **kwargs) -> Dict[str, Any]:
        """Execute data warehouse operations"""

        if operation:
            return await self._execute_predefined_operation(operation, **kwargs)
        elif query:
            return await self._execute_custom_query(query, **kwargs)
        else:
            raise ValueError("Either 'query' or 'operation' must be provided")

    async def _execute_custom_query(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute custom SQL query with optimization and safety checks"""

        # Validate query safety
        self._validate_query_safety(query)

        # Optimize query if possible
        optimized_query = self.query_optimizer.optimize(query)

        try:
            with self.engine.connect() as connection:
                # Execute query with parameters
                result = connection.execute(text(optimized_query), params or {})

                if result.returns_rows:
                    # Convert to DataFrame for easier manipulation
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())

                    return {
                        "status": "success",
                        "row_count": len(df),
                        "columns": list(df.columns),
                        "data": df.to_dict(orient="records"),
                        "metadata": {
                            "query": optimized_query,
                            "execution_time": "calculated_separately",  # Would be tracked in metrics
                            "optimization_applied": optimized_query != query
                        }
                    }
                else:
                    # Query didn't return rows (INSERT, UPDATE, DELETE, etc.)
                    return {
                        "status": "success",
                        "rows_affected": result.rowcount,
                        "metadata": {
                            "query": optimized_query,
                            "query_type": "modification"
                        }
                    }

        except Exception as e:
            self.logger.error(f"Database query failed: {str(e)}")
            raise e

    async def _execute_predefined_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute predefined data warehouse operations"""

        if operation == "describe_table":
            return await self._describe_table(kwargs.get("table_name"))

        elif operation == "table_statistics":
            return await self._get_table_statistics(kwargs.get("table_name"))

        elif operation == "data_quality_report":
            return await self._generate_data_quality_report(kwargs.get("table_name"), kwargs.get("columns"))

        elif operation == "query_performance_analysis":
            return await self._analyze_query_performance(kwargs.get("query"))

        else:
            raise ValueError(f"Unknown operation: {operation}")

    async def _describe_table(self, table_name: str) -> Dict[str, Any]:
        """Get comprehensive table structure information"""

        try:
            with self.engine.connect() as connection:
                # Get column information
                columns_result = connection.execute(
                    text(self.query_templates["table_info"]),
                    {"table_name": table_name}
                )

                columns_info = []
                for row in columns_result:
                    columns_info.append({
                        "column_name": row.column_name,
                        "data_type": row.data_type,
                        "nullable": row.is_nullable == "YES"
                    })

                # Get table statistics
                table_stats = connection.execute(
                    text(f"SELECT COUNT(*) as row_count FROM {table_name}")
                ).fetchone()

                return {
                    "table_name": table_name,
                    "columns": columns_info,
                    "row_count": table_stats.row_count,
                    "column_count": len(columns_info)
                }

        except Exception as e:
            raise Exception(f"Failed to describe table {table_name}: {str(e)}")

    def _validate_query_safety(self, query: str):
        """Validate query for safety (prevent destructive operations)"""

        query_upper = query.upper().strip()

        # Block dangerous operations
        dangerous_operations = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE"]

        for operation in dangerous_operations:
            if query_upper.startswith(operation):
                raise PermissionError(f"Operation '{operation}' is not allowed through this tool")

        # Check for suspicious patterns
        if "--" in query or "/*" in query:
            self.logger.warning("Query contains comment patterns - reviewing for safety")

    def _get_required_permissions(self) -> List[str]:
        return ["data_warehouse_read", "sql_query_execute"]

    def _get_required_parameters(self) -> List[str]:
        return []  # Parameters depend on the specific operation

    def _perform_health_check(self) -> Dict[str, Any]:
        """Perform health check by testing database connection"""

        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()

                return {
                    "status": "healthy",
                    "connection_pool_size": self.engine.pool.size(),
                    "checked_at": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }

class QueryOptimizer:
    """SQL query optimizer for common patterns"""

    def optimize(self, query: str) -> str:
        """Apply common query optimizations"""

        optimized_query = query

        # Add LIMIT if none specified for SELECT queries
        if query.upper().strip().startswith("SELECT") and "LIMIT" not in query.upper():
            optimized_query += " LIMIT 1000"  # Default limit for safety

        # Add basic optimizations
        optimized_query = self._optimize_joins(optimized_query)
        optimized_query = self._optimize_where_clauses(optimized_query)

        return optimized_query

    def _optimize_joins(self, query: str) -> str:
        """Optimize JOIN operations"""
        # Simplified optimization - in production, use more sophisticated query analysis
        return query

    def _optimize_where_clauses(self, query: str) -> str:
        """Optimize WHERE clauses"""
        # Simplified optimization - in production, analyze and optimize WHERE conditions
        return query
```

### Advanced Streaming Data Integration Tool

Create sophisticated tools for real-time streaming data integration:

```python
import kafka
from kafka import KafkaConsumer, KafkaProducer
import json
from typing import AsyncGenerator

class EnterpriseStreamingTool(EnterpriseToolBase):
    """Production-ready streaming data integration tool"""

    def __init__(self, config: ToolConfiguration, streaming_config: Dict[str, Any]):
        super().__init__(config)

        self.streaming_config = streaming_config
        self.kafka_config = streaming_config.get("kafka", {})
        self.consumers = {}
        self.producers = {}

        # Initialize connections
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize streaming platform connections"""

        if self.kafka_config:
            self._initialize_kafka_connections()

    def _initialize_kafka_connections(self):
        """Initialize Kafka connections with proper configuration"""

        bootstrap_servers = self.kafka_config["bootstrap_servers"]
        security_config = self.kafka_config.get("security", {})

        # Consumer configuration
        consumer_config = {
            "bootstrap_servers": bootstrap_servers,
            "value_deserializer": lambda m: json.loads(m.decode('utf-8')),
            "auto_offset_reset": "latest",
            "enable_auto_commit": True,
            "group_id": f"langchain_agent_{uuid.uuid4().hex[:8]}"
        }

        # Producer configuration
        producer_config = {
            "bootstrap_servers": bootstrap_servers,
            "value_serializer": lambda v: json.dumps(v).encode('utf-8'),
            "acks": "all",  # Wait for all replicas
            "retries": 3,
            "batch_size": 16384,
            "linger_ms": 10
        }

        # Add security configuration if provided
        if security_config:
            consumer_config.update(security_config)
            producer_config.update(security_config)

        self.default_consumer_config = consumer_config
        self.default_producer_config = producer_config

    async def _execute_core_functionality(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute streaming operations"""

        if operation == "consume_messages":
            return await self._consume_messages(**kwargs)

        elif operation == "produce_message":
            return await self._produce_message(**kwargs)

        elif operation == "get_topic_info":
            return await self._get_topic_info(**kwargs)

        elif operation == "monitor_stream":
            return await self._monitor_stream(**kwargs)

        else:
            raise ValueError(f"Unknown streaming operation: {operation}")

    async def _consume_messages(self, topic: str, max_messages: int = 100, timeout_ms: int = 10000) -> Dict[str, Any]:
        """Consume messages from streaming topic"""

        try:
            consumer = KafkaConsumer(
                topic,
                **self.default_consumer_config,
                consumer_timeout_ms=timeout_ms
            )

            messages = []
            message_count = 0

            for message in consumer:
                if message_count >= max_messages:
                    break

                message_data = {
                    "topic": message.topic,
                    "partition": message.partition,
                    "offset": message.offset,
                    "timestamp": message.timestamp,
                    "value": message.value,
                    "headers": dict(message.headers) if message.headers else {}
                }

                messages.append(message_data)
                message_count += 1

            consumer.close()

            return {
                "topic": topic,
                "messages_consumed": len(messages),
                "messages": messages,
                "metadata": {
                    "timeout_ms": timeout_ms,
                    "max_messages_requested": max_messages
                }
            }

        except Exception as e:
            raise Exception(f"Failed to consume messages from topic {topic}: {str(e)}")

    async def _produce_message(self, topic: str, message: Dict[str, Any], key: str = None) -> Dict[str, Any]:
        """Produce message to streaming topic"""

        try:
            producer = KafkaProducer(**self.default_producer_config)

            # Send message
            future = producer.send(
                topic,
                value=message,
                key=key.encode('utf-8') if key else None
            )

            # Wait for confirmation
            record_metadata = future.get(timeout=10)

            producer.close()

            return {
                "status": "success",
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset,
                "timestamp": record_metadata.timestamp
            }

        except Exception as e:
            raise Exception(f"Failed to produce message to topic {topic}: {str(e)}")

    async def _monitor_stream(self, topic: str, duration_seconds: int = 60) -> Dict[str, Any]:
        """Monitor streaming topic for specified duration"""

        try:
            consumer = KafkaConsumer(
                topic,
                **self.default_consumer_config,
                consumer_timeout_ms=1000  # 1 second timeout for monitoring
            )

            monitoring_start = time.time()
            message_count = 0
            total_bytes = 0
            partition_counts = {}

            while time.time() - monitoring_start < duration_seconds:
                try:
                    message = next(consumer)

                    message_count += 1
                    total_bytes += len(json.dumps(message.value).encode('utf-8'))

                    partition = message.partition
                    partition_counts[partition] = partition_counts.get(partition, 0) + 1

                except StopIteration:
                    # No messages in timeout window
                    continue

            consumer.close()

            actual_duration = time.time() - monitoring_start

            return {
                "topic": topic,
                "monitoring_duration": actual_duration,
                "total_messages": message_count,
                "messages_per_second": message_count / actual_duration if actual_duration > 0 else 0,
                "total_bytes": total_bytes,
                "bytes_per_second": total_bytes / actual_duration if actual_duration > 0 else 0,
                "partition_distribution": partition_counts,
                "active_partitions": len(partition_counts)
            }

        except Exception as e:
            raise Exception(f"Failed to monitor topic {topic}: {str(e)}")

    def _get_required_permissions(self) -> List[str]:
        return ["streaming_data_access", "kafka_topic_access"]

    def _get_required_parameters(self) -> List[str]:
        return ["operation"]

    def _perform_health_check(self) -> Dict[str, Any]:
        """Perform health check by testing Kafka connection"""

        try:
            from kafka import KafkaClient

            client = KafkaClient(bootstrap_servers=self.kafka_config["bootstrap_servers"])

            # Get cluster metadata to test connection
            metadata = client.cluster

            client.close()

            return {
                "status": "healthy",
                "brokers": len(metadata.brokers),
                "topics": len(metadata.topics),
                "checked_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
```

## Tool Orchestration and Composition

Advanced enterprise systems require sophisticated tool orchestration patterns that enable complex workflows involving multiple tools and conditional logic.

### Advanced Tool Orchestration Framework

Create a comprehensive framework for orchestrating multiple tools in complex workflows:

```python
from typing import Callable, Any, Union, List
from dataclasses import dataclass
from enum import Enum
import asyncio

class WorkflowStepType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"

@dataclass
class WorkflowStep:
    step_id: str
    step_type: WorkflowStepType
    tool_name: str
    operation: str
    parameters: Dict[str, Any]
    condition: Optional[Callable[[Any], bool]] = None
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    retry_count: int = 0

@dataclass
class WorkflowResult:
    workflow_id: str
    status: str
    steps_completed: List[str]
    steps_failed: List[str]
    results: Dict[str, Any]
    execution_time: float
    error_details: Optional[str] = None

class EnterpriseToolOrchestrator:
    """Advanced tool orchestration framework for complex enterprise workflows"""

    def __init__(self):
        self.registered_tools = {}
        self.workflow_templates = {}
        self.execution_history = []
        self.active_workflows = {}

    def register_tool(self, tool_name: str, tool_instance: EnterpriseToolBase):
        """Register a tool for use in workflows"""

        self.registered_tools[tool_name] = tool_instance
        self.logger.info(f"Registered tool: {tool_name}")

    def create_workflow_template(self, template_name: str, steps: List[WorkflowStep]) -> str:
        """Create reusable workflow template"""

        # Validate workflow steps
        self._validate_workflow_steps(steps)

        template_id = f"{template_name}_{uuid.uuid4().hex[:8]}"

        self.workflow_templates[template_id] = {
            "template_name": template_name,
            "steps": steps,
            "created_at": datetime.now().isoformat()
        }

        return template_id

    async def execute_workflow(self, template_id: str, auth_context: Dict[str, Any],
                              input_parameters: Dict[str, Any] = None) -> WorkflowResult:
        """Execute workflow from template with comprehensive orchestration"""

        if template_id not in self.workflow_templates:
            raise ValueError(f"Workflow template not found: {template_id}")

        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        execution_start = time.time()

        # Initialize workflow state
        workflow_state = {
            "workflow_id": workflow_id,
            "template_id": template_id,
            "status": "running",
            "steps_completed": [],
            "steps_failed": [],
            "step_results": {},
            "global_context": input_parameters or {}
        }

        self.active_workflows[workflow_id] = workflow_state

        try:
            template = self.workflow_templates[template_id]
            steps = template["steps"]

            # Execute workflow steps based on orchestration strategy
            await self._execute_workflow_steps(steps, workflow_state, auth_context)

            execution_time = time.time() - execution_start

            # Finalize workflow result
            result = WorkflowResult(
                workflow_id=workflow_id,
                status="completed" if not workflow_state["steps_failed"] else "partial_failure",
                steps_completed=workflow_state["steps_completed"],
                steps_failed=workflow_state["steps_failed"],
                results=workflow_state["step_results"],
                execution_time=execution_time
            )

            # Archive workflow
            self.execution_history.append(result)
            del self.active_workflows[workflow_id]

            return result

        except Exception as e:
            execution_time = time.time() - execution_start

            # Handle workflow failure
            result = WorkflowResult(
                workflow_id=workflow_id,
                status="failed",
                steps_completed=workflow_state.get("steps_completed", []),
                steps_failed=workflow_state.get("steps_failed", []),
                results=workflow_state.get("step_results", {}),
                execution_time=execution_time,
                error_details=str(e)
            )

            self.execution_history.append(result)
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

            return result

    async def _execute_workflow_steps(self, steps: List[WorkflowStep],
                                    workflow_state: Dict[str, Any],
                                    auth_context: Dict[str, Any]):
        """Execute workflow steps with proper orchestration"""

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(steps)

        # Execute steps in dependency order
        executed_steps = set()

        while len(executed_steps) < len(steps):
            # Find steps ready for execution (dependencies satisfied)
            ready_steps = []

            for step in steps:
                if (step.step_id not in executed_steps and
                    all(dep in executed_steps for dep in step.dependencies)):
                    ready_steps.append(step)

            if not ready_steps:
                # Check for circular dependencies or other issues
                remaining_steps = [s.step_id for s in steps if s.step_id not in executed_steps]
                raise Exception(f"Workflow deadlock: remaining steps {remaining_steps} cannot be executed")

            # Group ready steps by execution type
            sequential_steps = [s for s in ready_steps if s.step_type == WorkflowStepType.SEQUENTIAL]
            parallel_steps = [s for s in ready_steps if s.step_type == WorkflowStepType.PARALLEL]
            conditional_steps = [s for s in ready_steps if s.step_type == WorkflowStepType.CONDITIONAL]

            # Execute sequential steps first (one by one)
            for step in sequential_steps:
                await self._execute_single_step(step, workflow_state, auth_context)
                executed_steps.add(step.step_id)

            # Execute parallel steps concurrently
            if parallel_steps:
                parallel_tasks = [
                    self._execute_single_step(step, workflow_state, auth_context)
                    for step in parallel_steps
                ]

                await asyncio.gather(*parallel_tasks, return_exceptions=True)

                for step in parallel_steps:
                    executed_steps.add(step.step_id)

            # Execute conditional steps
            for step in conditional_steps:
                if self._evaluate_step_condition(step, workflow_state):
                    await self._execute_single_step(step, workflow_state, auth_context)
                else:
                    # Mark as completed but skipped
                    workflow_state["step_results"][step.step_id] = {"status": "skipped", "reason": "condition_not_met"}

                executed_steps.add(step.step_id)

    async def _execute_single_step(self, step: WorkflowStep,
                                 workflow_state: Dict[str, Any],
                                 auth_context: Dict[str, Any]):
        """Execute individual workflow step"""

        try:
            # Get tool instance
            if step.tool_name not in self.registered_tools:
                raise ValueError(f"Tool not registered: {step.tool_name}")

            tool = self.registered_tools[step.tool_name]

            # Prepare parameters with context substitution
            resolved_parameters = self._resolve_step_parameters(step.parameters, workflow_state)

            # Execute tool
            step_start = time.time()
            result = await asyncio.wait_for(
                tool.execute(auth_context, operation=step.operation, **resolved_parameters),
                timeout=step.timeout_seconds
            )
            step_time = time.time() - step_start

            # Store result in workflow state
            workflow_state["step_results"][step.step_id] = {
                "status": "completed",
                "result": result,
                "execution_time": step_time
            }

            workflow_state["steps_completed"].append(step.step_id)

            # Update global context with step results
            if isinstance(result, dict) and "data" in result:
                workflow_state["global_context"][f"step_{step.step_id}_result"] = result["data"]

        except Exception as e:
            # Handle step failure
            workflow_state["step_results"][step.step_id] = {
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - step_start if 'step_start' in locals() else 0
            }

            workflow_state["steps_failed"].append(step.step_id)

            # Decide whether to continue workflow or fail completely
            if step.retry_count > 0:
                # Implement retry logic here
                pass
            else:
                # For now, continue with other steps unless this step is critical
                pass

    def _resolve_step_parameters(self, parameters: Dict[str, Any],
                               workflow_state: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter references to workflow context"""

        resolved = {}

        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Parameter reference - resolve from workflow context
                reference = value[2:-1]  # Remove ${ }

                if reference in workflow_state["global_context"]:
                    resolved[key] = workflow_state["global_context"][reference]
                elif reference.startswith("step_") and reference in workflow_state["global_context"]:
                    resolved[key] = workflow_state["global_context"][reference]
                else:
                    # Reference not found - use original value
                    resolved[key] = value
            else:
                resolved[key] = value

        return resolved

    def _build_dependency_graph(self, steps: List[WorkflowStep]) -> Dict[str, List[str]]:
        """Build step dependency graph for orchestration"""

        graph = {}

        for step in steps:
            graph[step.step_id] = step.dependencies.copy()

        return graph

    def _validate_workflow_steps(self, steps: List[WorkflowStep]):
        """Validate workflow steps for consistency and feasibility"""

        step_ids = {step.step_id for step in steps}

        # Check for duplicate step IDs
        if len(step_ids) != len(steps):
            raise ValueError("Duplicate step IDs found in workflow")

        # Validate dependencies exist
        for step in steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise ValueError(f"Step {step.step_id} depends on non-existent step {dep}")

        # Check for circular dependencies (simplified check)
        # In production, implement full cycle detection algorithm

        # Validate tools exist
        for step in steps:
            if step.tool_name not in self.registered_tools:
                raise ValueError(f"Tool {step.tool_name} not registered for step {step.step_id}")

    def _evaluate_step_condition(self, step: WorkflowStep, workflow_state: Dict[str, Any]) -> bool:
        """Evaluate step condition for conditional execution"""

        if not step.condition:
            return True

        try:
            # Pass workflow state to condition function
            return step.condition(workflow_state)
        except Exception as e:
            # If condition evaluation fails, default to not executing the step
            return False

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of active workflow"""

        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id].copy()

        # Check execution history
        for result in self.execution_history:
            if result.workflow_id == workflow_id:
                return {
                    "workflow_id": result.workflow_id,
                    "status": result.status,
                    "steps_completed": result.steps_completed,
                    "steps_failed": result.steps_failed,
                    "execution_time": result.execution_time
                }

        return None

    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive orchestration metrics"""

        total_workflows = len(self.execution_history)
        completed_workflows = sum(1 for r in self.execution_history if r.status == "completed")
        failed_workflows = sum(1 for r in self.execution_history if r.status == "failed")

        if total_workflows == 0:
            return {
                "total_workflows": 0,
                "success_rate": 0,
                "average_execution_time": 0,
                "active_workflows": len(self.active_workflows)
            }

        average_execution_time = sum(r.execution_time for r in self.execution_history) / total_workflows

        return {
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "failed_workflows": failed_workflows,
            "success_rate": completed_workflows / total_workflows,
            "average_execution_time": average_execution_time,
            "active_workflows": len(self.active_workflows),
            "registered_tools": len(self.registered_tools),
            "workflow_templates": len(self.workflow_templates)
        }
```

## 🎯📝 Prerequisites Review

Before implementing enterprise tool development, ensure mastery of foundational concepts:

**Essential Prerequisites:**  
- [🎯 LangChain Tool Basics](Session2_LangChain_Foundations.md) - Core tool creation and usage patterns  
- [📝 Production Tool Implementation](Session2_Practical_Implementation.md) - Practical tool development with error handling  

## ⚙️ Continue Advanced Learning

Complete your advanced LangChain mastery:

**Complementary Advanced Modules:**  
- [⚙️ Advanced Agent Architecture](Session2_Advanced_Agent_Architecture.md) - Sophisticated orchestration patterns  
- [⚙️ Production Memory Systems](Session2_Production_Memory_Systems.md) - Enterprise state management and persistence  

**Legacy Advanced Modules:**  
- [Custom Tool Development](Session2_ModuleC_Custom_Tool_Development.md) - Specialized tool creation patterns  
- [Production Deployment Strategies](Session2_ModuleB_Production_Deployment_Strategies.md) - Enterprise deployment & monitoring  
- [Performance Monitoring](Session2_ModuleD_Performance_Monitoring.md) - System optimization & observability  
---

**Next:** [Session 3 - LangGraph Multi-Agent Workflows →](Session3_LangGraph_Multi_Agent_Workflows.md)

---
