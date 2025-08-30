# Session 2 - Module C: Custom Tool Development

> **⚠️ ADVANCED OPTIONAL MODULE**  
> Prerequisites: Complete Session 2 core content first.

At 11:23 PM on a Friday in January 2024, Palantir's data fusion platform processed 847 billion data points across 23 different data sources simultaneously, with each data stream requiring specialized processing logic that no standard tool could handle. The secret wasn't general-purpose solutions - it was 312 custom-built data processing tools that understood financial market feeds, satellite imagery, social media streams, IoT sensor networks, and government databases with precision that transformed raw information streams into actionable intelligence within milliseconds.

This is the reality of modern data engineering at scale: off-the-shelf tools get you started, but custom tools get you to market leadership. When Bloomberg processes financial data streams from 40,000+ sources, when Tesla analyzes automotive sensor data from millions of vehicles, or when Google manages search index updates across petabytes of web content, they win because their data processing tools are precisely engineered for their specific data challenges.

The companies dominating data-intensive industries understand a crucial truth: generic tools solve generic problems, but competitive advantages come from tools that understand your exact data patterns, processing requirements, and business logic better than anyone else's systems possibly could.

---

## Part 1: Advanced Tool Architecture

### Tool Development Foundations for Data Processing

🗂️ **File**: `src/session2/tool_foundations.py` - Core tool development patterns for data systems

Custom data processing tools require sophisticated architecture that handles the complexity of enterprise data workflows while maintaining performance and reliability:

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union, Type, Callable
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import asyncio
import logging
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from dataclasses import dataclass, field

@dataclass
class DataToolContext:
    """Execution context for data processing tools with comprehensive metadata"""
    execution_id: str
    user_id: Optional[str]
    session_id: Optional[str] 
    request_timestamp: datetime
    dataset_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_options: Dict[str, Any] = field(default_factory=dict)
    quality_requirements: Dict[str, Any] = field(default_factory=dict)
    performance_targets: Dict[str, Any] = field(default_factory=dict)
```

DataToolContext provides comprehensive execution metadata for data processing operations. Dataset metadata, quality requirements, and performance targets ensure tools operate with full context about data processing expectations and constraints.

```python
class DataProcessingResult:
    """Structured result container for data processing operations"""
    
    def __init__(self, success: bool = True):
        self.success = success
        self.data: Any = None
        self.metadata: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.performance_metrics: Dict[str, Any] = {}
        self.quality_metrics: Dict[str, Any] = {}
        self.execution_time: Optional[float] = None
        self.processed_records: int = 0
        
    def add_error(self, error: str):
        """Add error message to result"""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str):
        """Add warning message to result"""
        self.warnings.append(warning)
    
    def set_performance_metric(self, metric_name: str, value: Any):
        """Set performance metric for monitoring"""
        self.performance_metrics[metric_name] = value
    
    def set_quality_metric(self, metric_name: str, value: Any):
        """Set data quality metric"""
        self.quality_metrics[metric_name] = value
```

DataProcessingResult provides structured output for data tool operations with comprehensive error tracking, performance metrics, and quality assessment. This standardized result format enables consistent tool integration and monitoring across data processing workflows.

```python    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization"""
        return {
            "success": self.success,
            "data": self.data,
            "metadata": self.metadata,
            "errors": self.errors,
            "warnings": self.warnings,
            "performance_metrics": self.performance_metrics,
            "quality_metrics": self.quality_metrics,
            "execution_time": self.execution_time,
            "processed_records": self.processed_records
        }
```

### Base Data Processing Tool Architecture

Advanced base class provides comprehensive infrastructure for enterprise-grade data processing tools:

```python
class AdvancedDataProcessingTool(BaseTool, ABC):
    """Advanced base class for enterprise data processing tools with comprehensive features"""
    
    # Tool configuration
    max_execution_time: int = 300  # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds
    enable_async: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.performance_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self._lock = threading.Lock()
        
        # Initialize tool-specific configuration
        self._initialize_tool_config()
    
    @abstractmethod
    def _initialize_tool_config(self):
        """Initialize tool-specific configuration - implement in subclasses"""
        pass
    
    @abstractmethod
    async def _execute_data_processing(self, context: DataToolContext, 
                                     **kwargs) -> DataProcessingResult:
        """Execute core data processing logic - implement in subclasses"""
        pass
```

AdvancedDataProcessingTool establishes enterprise tool infrastructure with caching, retry logic, performance tracking, and async execution. Abstract methods ensure consistent implementation patterns while providing comprehensive operational features.

```python    
    def _run(self, **kwargs) -> str:
        """Synchronous tool execution with comprehensive error handling"""
        
        # Create execution context for data processing
        context = DataToolContext(
            execution_id=f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            user_id=kwargs.get("user_id"),
            session_id=kwargs.get("session_id"),
            request_timestamp=datetime.now(),
            dataset_metadata=kwargs.get("dataset_metadata", {}),
            processing_options=kwargs.get("processing_options", {}),
            quality_requirements=kwargs.get("quality_requirements", {}),
            performance_targets=kwargs.get("performance_targets", {})
        )
        
        try:
            # Execute with performance tracking for data processing
            start_time = datetime.now()
            
            if self.enable_async:
                result = asyncio.run(self._execute_with_retry(context, **kwargs))
            else:
                result = self._execute_sync_with_retry(context, **kwargs)
            
            # Record performance metrics for monitoring
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self._record_performance_metrics(context, result, execution_time)
            
            return self._format_tool_output(result)
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            error_result = DataProcessingResult(success=False)
            error_result.add_error(f"Tool execution failed: {str(e)}")
            
            return self._format_tool_output(error_result)
```

Synchronous execution wrapper provides comprehensive context creation, performance tracking, and error handling for data processing tools. Context creation captures execution metadata while performance recording enables monitoring and optimization.

### Retry Logic and Caching Implementation

Robust retry logic and intelligent caching optimize data processing tool reliability and performance:

```python
async def _execute_with_retry(self, context: DataToolContext, 
                            **kwargs) -> DataProcessingResult:
    """Execute data processing with intelligent retry logic and caching"""
    
    # Check cache for recent results
    if self.enable_caching:
        cached_result = self._check_cache(context, kwargs)
        if cached_result:
            self.logger.debug(f"Cache hit for execution: {context.execution_id}")
            return cached_result
    
    last_error = None
    
    for attempt in range(self.retry_attempts):
        try:
            self.logger.info(f"Executing data processing attempt {attempt + 1}/{self.retry_attempts}")
            
            # Execute core data processing logic
            result = await asyncio.wait_for(
                self._execute_data_processing(context, **kwargs),
                timeout=self.max_execution_time
            )
            
            # Cache successful results for future use
            if self.enable_caching and result.success:
                self._cache_result(context, kwargs, result)
            
            return result
```

Retry execution with timeout protection and caching optimization reduces redundant data processing while ensuring reliable operation. Cache checking and result caching improve performance for repeated data processing operations.

```python            
        except asyncio.TimeoutError:
            last_error = f"Data processing timeout after {self.max_execution_time} seconds"
            self.logger.warning(f"Attempt {attempt + 1} timed out")
            
        except Exception as e:
            last_error = str(e)
            self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
        
        # Wait before retry with exponential backoff
        if attempt < self.retry_attempts - 1:
            delay = self.retry_delay * (2 ** attempt)
            self.logger.info(f"Waiting {delay} seconds before retry")
            await asyncio.sleep(delay)
    
    # All retries failed - return error result
    error_result = DataProcessingResult(success=False)
    error_result.add_error(f"All retry attempts failed. Last error: {last_error}")
    
    return error_result
```

Retry failure handling with exponential backoff prevents overwhelming failed services while providing comprehensive error reporting. Final error result includes detailed failure information for troubleshooting data processing issues.

```python
def _check_cache(self, context: DataToolContext, kwargs: Dict[str, Any]) -> Optional[DataProcessingResult]:
    """Check for cached results with TTL validation"""
    
    cache_key = self._generate_cache_key(context, kwargs)
    
    with self._lock:
        if cache_key in self.cache:
            cached_time = self.cache_timestamps.get(cache_key)
            if cached_time and (datetime.now() - cached_time).total_seconds() < self.cache_ttl:
                return self.cache[cache_key]
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
                if cache_key in self.cache_timestamps:
                    del self.cache_timestamps[cache_key]
    
    return None

def _cache_result(self, context: DataToolContext, kwargs: Dict[str, Any], 
                 result: DataProcessingResult):
    """Cache successful result with timestamp"""
    
    cache_key = self._generate_cache_key(context, kwargs)
    
    with self._lock:
        self.cache[cache_key] = result
        self.cache_timestamps[cache_key] = datetime.now()
        
        # Limit cache size to prevent memory issues
        if len(self.cache) > 1000:
            oldest_key = min(self.cache_timestamps.keys(), 
                           key=lambda k: self.cache_timestamps[k])
            del self.cache[oldest_key]
            del self.cache_timestamps[oldest_key]
```

Cache management with TTL validation and size limits ensures optimal memory usage while providing performance benefits. Thread-safe cache operations prevent race conditions in concurrent data processing environments.

---

## Part 2: Specialized Data Processing Tools

### Enterprise Data Warehouse Integration Tool

🗂️ **File**: `src/session2/data_warehouse_tools.py` - Enterprise data warehouse integration

```python
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import asyncpg
import aiodns
from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime
import logging

class EnterpriseDataWarehouseTool(AdvancedDataProcessingTool):
    """Advanced tool for enterprise data warehouse operations with connection pooling and optimization"""
    
    name = "enterprise_data_warehouse_tool"
    description = "Execute optimized queries against enterprise data warehouses with connection pooling and result caching"
    
    def __init__(self, warehouse_config: Dict[str, Any], **kwargs):
        self.warehouse_config = warehouse_config
        self.connection_pools: Dict[str, Any] = {}
        self.query_optimizer = QueryOptimizer()
        self.result_serializer = DataWarehouseResultSerializer()
        
        super().__init__(**kwargs)
    
    def _initialize_tool_config(self):
        """Initialize data warehouse connection pools and optimization settings"""
        
        self.max_execution_time = self.warehouse_config.get("max_query_time", 600)  # 10 minutes
        self.connection_timeout = self.warehouse_config.get("connection_timeout", 30)
        self.query_timeout = self.warehouse_config.get("query_timeout", 300)
        self.max_result_size = self.warehouse_config.get("max_result_size", 1000000)  # 1M rows
        
        # Initialize connection pools for each warehouse
        self._initialize_connection_pools()
```

EnterpriseDataWarehouseTool provides sophisticated data warehouse integration with connection pooling, query optimization, and result serialization. Configuration-driven setup enables multi-warehouse support with performance optimization.

```python    
    class ToolInput(BaseModel):
        sql_query: str = Field(description="SQL query to execute against data warehouse")
        warehouse_name: str = Field(default="default", description="Target data warehouse identifier")
        query_parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters for prepared statements")
        result_format: str = Field(default="json", description="Result format: json, parquet, csv")
        enable_optimization: bool = Field(default=True, description="Enable query optimization")
        cache_results: bool = Field(default=True, description="Cache query results")
        
        @validator('sql_query')
        def validate_sql_query(cls, v):
            """Validate SQL query for security and syntax"""
            if not v or not v.strip():
                raise ValueError("SQL query cannot be empty")
            
            # Basic SQL injection prevention
            dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
            query_upper = v.upper()
            
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    raise ValueError(f"Potentially dangerous SQL keyword detected: {keyword}")
            
            return v.strip()
    
    args_schema: Type[BaseModel] = ToolInput
```

Input validation ensures secure SQL execution with injection prevention and syntax validation. Result format options and optimization controls provide flexible data warehouse query execution with security safeguards.

```python
async def _execute_data_processing(self, context: DataToolContext, 
                                 **kwargs) -> DataProcessingResult:
    """Execute optimized data warehouse query with comprehensive monitoring"""
    
    sql_query = kwargs.get("sql_query")
    warehouse_name = kwargs.get("warehouse_name", "default")
    query_parameters = kwargs.get("query_parameters", {})
    result_format = kwargs.get("result_format", "json")
    enable_optimization = kwargs.get("enable_optimization", True)
    
    result = DataProcessingResult()
    
    try:
        # Optimize query if enabled
        if enable_optimization:
            optimized_query = self.query_optimizer.optimize_query(sql_query, context)
            self.logger.info(f"Query optimized: {len(sql_query)} -> {len(optimized_query)} chars")
        else:
            optimized_query = sql_query
        
        # Get connection pool for warehouse
        pool = await self._get_connection_pool(warehouse_name)
        
        # Execute query with performance monitoring
        start_time = datetime.now()
        
        async with pool.acquire() as connection:
            query_result = await self._execute_optimized_query(
                connection, optimized_query, query_parameters, context
            )
        
        execution_time = (datetime.now() - start_time).total_seconds()
```

Query execution with optimization and connection pooling ensures efficient data warehouse access. Performance monitoring and connection management provide enterprise-grade data processing capabilities.

```python        
        # Process and format results
        formatted_result = await self._format_query_result(query_result, result_format)
        
        # Set result data and metadata
        result.data = formatted_result
        result.processed_records = len(query_result) if isinstance(query_result, list) else 1
        result.metadata = {
            "warehouse_name": warehouse_name,
            "query_execution_time": execution_time,
            "result_format": result_format,
            "optimized": enable_optimization,
            "query_hash": self._hash_query(optimized_query)
        }
        
        # Set performance metrics
        result.set_performance_metric("query_execution_time", execution_time)
        result.set_performance_metric("rows_processed", result.processed_records)
        result.set_performance_metric("data_transfer_size", len(json.dumps(formatted_result)))
        
        return result
        
    except Exception as e:
        result.add_error(f"Data warehouse query execution failed: {str(e)}")
        self.logger.error(f"Query execution error: {str(e)}")
        return result
```

Result processing and formatting with comprehensive metadata and performance metrics provide detailed execution information. Error handling ensures graceful failure with detailed diagnostic information for troubleshooting data warehouse issues.

### Real-time Streaming Data Processing Tool

🗂️ **File**: `src/session2/streaming_data_tools.py` - Real-time data stream processing

```python
import asyncio
import aiohttp
import websockets
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta
import logging

class StreamingDataProcessingTool(AdvancedDataProcessingTool):
    """Advanced tool for real-time streaming data processing with multiple stream sources"""
    
    name = "streaming_data_processing_tool"
    description = "Process real-time data streams from multiple sources including Kafka, WebSockets, and HTTP streams"
    
    def __init__(self, streaming_config: Dict[str, Any], **kwargs):
        self.streaming_config = streaming_config
        self.active_streams: Dict[str, Any] = {}
        self.stream_processors: Dict[str, Callable] = {}
        self.stream_metrics: Dict[str, Dict[str, Any]] = {}
        
        super().__init__(**kwargs)
    
    def _initialize_tool_config(self):
        """Initialize streaming data processing configuration"""
        
        self.max_execution_time = self.streaming_config.get("max_processing_time", 1800)  # 30 minutes
        self.batch_size = self.streaming_config.get("batch_size", 1000)
        self.processing_timeout = self.streaming_config.get("processing_timeout", 60)
        self.enable_backpressure = self.streaming_config.get("enable_backpressure", True)
        
        # Initialize stream source connections
        self._initialize_stream_sources()
```

StreamingDataProcessingTool provides comprehensive real-time data processing capabilities with support for multiple streaming platforms. Configuration-driven setup enables flexible stream source integration with performance optimization.

```python    
    class ToolInput(BaseModel):
        stream_source: str = Field(description="Stream source type: kafka, websocket, http_stream")
        source_config: Dict[str, Any] = Field(description="Source-specific configuration parameters")
        processing_function: str = Field(description="Data processing function to apply")
        output_destination: Optional[str] = Field(default=None, description="Optional output destination")
        processing_mode: str = Field(default="batch", description="Processing mode: batch, streaming, micro_batch")
        window_size_seconds: int = Field(default=60, description="Processing window size in seconds")
        
        @validator('stream_source')
        def validate_stream_source(cls, v):
            valid_sources = ['kafka', 'websocket', 'http_stream', 'pubsub', 'kinesis']
            if v not in valid_sources:
                raise ValueError(f"Invalid stream source. Must be one of: {valid_sources}")
            return v
    
    args_schema: Type[BaseModel] = ToolInput
```

Input validation ensures supported streaming sources and processing modes. Window size configuration and processing mode options provide flexible real-time data processing capabilities.

```python
async def _execute_data_processing(self, context: DataToolContext, 
                                 **kwargs) -> DataProcessingResult:
    """Execute real-time streaming data processing with comprehensive monitoring"""
    
    stream_source = kwargs.get("stream_source")
    source_config = kwargs.get("source_config", {})
    processing_function = kwargs.get("processing_function")
    processing_mode = kwargs.get("processing_mode", "batch")
    window_size = kwargs.get("window_size_seconds", 60)
    
    result = DataProcessingResult()
    
    try:
        # Initialize stream connection
        stream_connection = await self._connect_to_stream(stream_source, source_config)
        
        # Create processing pipeline based on mode
        if processing_mode == "streaming":
            processed_data = await self._process_streaming_data(
                stream_connection, processing_function, context
            )
        elif processing_mode == "micro_batch":
            processed_data = await self._process_micro_batches(
                stream_connection, processing_function, window_size, context
            )
        else:  # batch mode
            processed_data = await self._process_batch_data(
                stream_connection, processing_function, context
            )
        
        # Collect processing results and metrics
        result.data = processed_data
        result.processed_records = len(processed_data) if isinstance(processed_data, list) else 1
        
        # Add streaming-specific metadata
        result.metadata = {
            "stream_source": stream_source,
            "processing_mode": processing_mode,
            "window_size_seconds": window_size,
            "stream_metrics": self.stream_metrics.get(context.execution_id, {})
        }
        
        return result
        
    except Exception as e:
        result.add_error(f"Streaming data processing failed: {str(e)}")
        self.logger.error(f"Streaming processing error: {str(e)}")
        return result
```

Streaming data execution supports multiple processing modes with comprehensive monitoring and metrics collection. Connection management and processing pipeline creation provide flexible real-time data processing capabilities.

### Machine Learning Pipeline Integration Tool

🗂️ **File**: `src/session2/ml_pipeline_tools.py` - ML pipeline integration and model operations

```python
import mlflow
import mlflow.sklearn
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime
import logging

class MLPipelineIntegrationTool(AdvancedDataProcessingTool):
    """Advanced tool for machine learning pipeline integration with model lifecycle management"""
    
    name = "ml_pipeline_integration_tool"
    description = "Integrate with ML pipelines for model training, evaluation, deployment, and inference"
    
    def __init__(self, ml_config: Dict[str, Any], **kwargs):
        self.ml_config = ml_config
        self.mlflow_client = MlflowClient(ml_config.get("mlflow_tracking_uri"))
        self.model_registry = {}
        self.feature_store_client = None
        self.deployment_targets = ml_config.get("deployment_targets", {})
        
        super().__init__(**kwargs)
    
    def _initialize_tool_config(self):
        """Initialize ML pipeline configuration and model registry"""
        
        self.max_execution_time = self.ml_config.get("max_training_time", 3600)  # 1 hour
        self.model_validation_threshold = self.ml_config.get("validation_threshold", 0.85)
        self.auto_deployment_enabled = self.ml_config.get("auto_deployment", False)
        
        # Initialize MLflow and model registry
        mlflow.set_tracking_uri(self.ml_config.get("mlflow_tracking_uri"))
        
        # Initialize feature store connection if configured
        if "feature_store_config" in self.ml_config:
            self._initialize_feature_store()
```

MLPipelineIntegrationTool provides comprehensive machine learning pipeline integration with model lifecycle management, feature store integration, and automated deployment capabilities.

```python    
    class ToolInput(BaseModel):
        operation: str = Field(description="ML operation: train, evaluate, predict, deploy, monitor")
        model_name: str = Field(description="Model name for operation")
        experiment_name: str = Field(default="default", description="MLflow experiment name")
        model_version: Optional[str] = Field(default=None, description="Specific model version")
        training_data: Optional[Dict[str, Any]] = Field(default=None, description="Training dataset configuration")
        evaluation_metrics: List[str] = Field(default=["accuracy", "precision", "recall", "f1"], description="Evaluation metrics to compute")
        deployment_target: Optional[str] = Field(default=None, description="Deployment target environment")
        
        @validator('operation')
        def validate_operation(cls, v):
            valid_operations = ['train', 'evaluate', 'predict', 'deploy', 'monitor', 'feature_engineering']
            if v not in valid_operations:
                raise ValueError(f"Invalid operation. Must be one of: {valid_operations}")
            return v
    
    args_schema: Type[BaseModel] = ToolInput
```

Input validation ensures supported ML operations and provides comprehensive parameter configuration for different machine learning pipeline tasks.

```python
async def _execute_data_processing(self, context: DataToolContext, 
                                 **kwargs) -> DataProcessingResult:
    """Execute ML pipeline operation with comprehensive lifecycle management"""
    
    operation = kwargs.get("operation")
    model_name = kwargs.get("model_name")
    experiment_name = kwargs.get("experiment_name", "default")
    training_data = kwargs.get("training_data")
    evaluation_metrics = kwargs.get("evaluation_metrics", ["accuracy"])
    
    result = DataProcessingResult()
    
    try:
        # Set MLflow experiment
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run(run_name=f"{operation}_{model_name}_{context.execution_id}"):
            
            if operation == "train":
                ml_result = await self._train_model(model_name, training_data, context)
            elif operation == "evaluate":
                ml_result = await self._evaluate_model(model_name, evaluation_metrics, context)
            elif operation == "predict":
                ml_result = await self._run_model_inference(model_name, kwargs, context)
            elif operation == "deploy":
                ml_result = await self._deploy_model(model_name, kwargs.get("deployment_target"), context)
            elif operation == "monitor":
                ml_result = await self._monitor_model_performance(model_name, context)
            elif operation == "feature_engineering":
                ml_result = await self._execute_feature_engineering(kwargs, context)
            else:
                raise ValueError(f"Unsupported ML operation: {operation}")
            
            # Log operation results to MLflow
            mlflow.log_params({
                "operation": operation,
                "model_name": model_name,
                "execution_id": context.execution_id
            })
            
            mlflow.log_metrics(ml_result.performance_metrics)
            
            result.data = ml_result.data
            result.metadata = ml_result.metadata
            result.performance_metrics = ml_result.performance_metrics
            result.quality_metrics = ml_result.quality_metrics
            
            return result
            
    except Exception as e:
        result.add_error(f"ML pipeline operation failed: {str(e)}")
        self.logger.error(f"ML operation error: {str(e)}")
        return result
```

ML pipeline execution with comprehensive MLflow integration provides model lifecycle management with experiment tracking, metrics logging, and operation-specific processing capabilities.

---

## Part 3: Tool Integration & Orchestration

### Tool Chain Orchestration System

🗂️ **File**: `src/session2/tool_orchestration.py` - Advanced tool coordination and workflow management

```python
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import networkx as nx

class ToolExecutionMode(Enum):
    """Execution modes for tool orchestration in data processing workflows"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel" 
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"
    DAG = "dag"  # Directed Acyclic Graph

@dataclass
class ToolExecutionNode:
    """Represents a single tool execution node in data processing workflow"""
    tool_name: str
    tool_instance: Any
    input_parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    conditions: Optional[Dict[str, Any]] = None
    retry_policy: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 300
    execution_context: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowExecutionResult:
    """Comprehensive result from tool workflow execution"""
    workflow_id: str
    success: bool
    execution_time: float
    executed_tools: List[str]
    tool_results: Dict[str, DataProcessingResult]
    failed_tools: List[str] = field(default_factory=list)
    skipped_tools: List[str] = field(default_factory=list)
    workflow_metadata: Dict[str, Any] = field(default_factory=dict)
```

Tool orchestration data structures provide comprehensive workflow management for complex data processing pipelines. Execution modes, node definitions, and result tracking enable sophisticated tool coordination.

```python
class DataProcessingWorkflowOrchestrator:
    """Advanced orchestrator for complex data processing tool workflows"""
    
    def __init__(self, orchestrator_config: Dict[str, Any]):
        self.config = orchestrator_config
        self.registered_tools: Dict[str, Any] = {}
        self.workflow_definitions: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[WorkflowExecutionResult] = []
        
        # Workflow execution engine
        self.execution_engine = WorkflowExecutionEngine()
        self.dependency_resolver = DependencyResolver()
        self.condition_evaluator = ConditionEvaluator()
        
        self.logger = logging.getLogger(__name__)
    
    def register_tool(self, tool_name: str, tool_instance: Any, tool_config: Dict[str, Any] = None):
        """Register data processing tool with orchestrator"""
        
        self.registered_tools[tool_name] = {
            "instance": tool_instance,
            "config": tool_config or {},
            "registration_time": datetime.now(),
            "usage_count": 0,
            "success_rate": 0.0
        }
        
        self.logger.info(f"Registered data processing tool: {tool_name}")
```

Workflow orchestrator provides comprehensive tool registration and workflow management. Tool registration includes configuration, usage tracking, and success rate monitoring for data processing optimization.

```python    
    async def execute_workflow(self, workflow_definition: Dict[str, Any], 
                             global_context: Dict[str, Any] = None) -> WorkflowExecutionResult:
        """Execute complex data processing workflow with comprehensive monitoring"""
        
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = datetime.now()
        
        workflow_result = WorkflowExecutionResult(
            workflow_id=workflow_id,
            success=True,
            execution_time=0.0,
            executed_tools=[],
            tool_results={}
        )
        
        try:
            # Parse workflow definition into execution graph
            execution_graph = self._build_execution_graph(workflow_definition)
            
            # Validate workflow dependencies and detect cycles
            validation_result = self._validate_workflow(execution_graph)
            if not validation_result["valid"]:
                workflow_result.success = False
                workflow_result.workflow_metadata["validation_errors"] = validation_result["errors"]
                return workflow_result
            
            # Execute workflow based on execution mode
            execution_mode = ToolExecutionMode(workflow_definition.get("execution_mode", "sequential"))
            
            if execution_mode == ToolExecutionMode.SEQUENTIAL:
                await self._execute_sequential_workflow(execution_graph, workflow_result, global_context)
            elif execution_mode == ToolExecutionMode.PARALLEL:
                await self._execute_parallel_workflow(execution_graph, workflow_result, global_context)
            elif execution_mode == ToolExecutionMode.DAG:
                await self._execute_dag_workflow(execution_graph, workflow_result, global_context)
            elif execution_mode == ToolExecutionMode.CONDITIONAL:
                await self._execute_conditional_workflow(execution_graph, workflow_result, global_context)
            else:
                raise ValueError(f"Unsupported execution mode: {execution_mode}")
```

Workflow execution supports multiple execution modes with comprehensive validation and monitoring. Graph building, dependency validation, and mode-specific execution provide flexible data processing workflow capabilities.

```python            
            # Calculate final execution metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            workflow_result.execution_time = execution_time
            
            # Determine overall workflow success
            workflow_result.success = len(workflow_result.failed_tools) == 0
            
            # Add workflow metadata
            workflow_result.workflow_metadata.update({
                "execution_mode": execution_mode.value,
                "total_tools": len(execution_graph.nodes),
                "success_rate": len(workflow_result.executed_tools) / len(execution_graph.nodes) if execution_graph.nodes else 0
            })
            
            # Store execution history for analysis
            self.execution_history.append(workflow_result)
            
            return workflow_result
            
        except Exception as e:
            workflow_result.success = False
            workflow_result.execution_time = (datetime.now() - start_time).total_seconds()
            workflow_result.workflow_metadata["execution_error"] = str(e)
            
            self.logger.error(f"Workflow execution failed: {str(e)}")
            return workflow_result
```

Workflow completion includes comprehensive metrics calculation, success determination, and execution history storage. Error handling ensures graceful failure with detailed diagnostic information.

### DAG-based Workflow Execution

Directed Acyclic Graph execution enables complex data processing workflows with sophisticated dependency management:

```python
async def _execute_dag_workflow(self, execution_graph: nx.DiGraph, 
                               workflow_result: WorkflowExecutionResult,
                               global_context: Dict[str, Any]) -> None:
    """Execute workflow as Directed Acyclic Graph with dependency resolution"""
    
    # Perform topological sort for execution order
    try:
        execution_order = list(nx.topological_sort(execution_graph))
    except nx.NetworkXError as e:
        raise ValueError(f"Workflow contains cycles - not a valid DAG: {str(e)}")
    
    # Track completed tools and their outputs for dependency resolution
    completed_tools: Dict[str, DataProcessingResult] = {}
    execution_context = global_context.copy() if global_context else {}
    
    # Execute tools in topological order with dependency checking
    for tool_name in execution_order:
        tool_node = execution_graph.nodes[tool_name]['node_data']
        
        try:
            # Check if all dependencies are satisfied
            dependencies_satisfied = await self._check_dependencies_satisfied(
                tool_node.dependencies, completed_tools
            )
            
            if not dependencies_satisfied["satisfied"]:
                self.logger.warning(f"Tool {tool_name} dependencies not satisfied: {dependencies_satisfied['missing']}")
                workflow_result.skipped_tools.append(tool_name)
                continue
            
            # Prepare tool input with dependency outputs
            tool_input = self._prepare_tool_input_with_dependencies(
                tool_node.input_parameters, 
                tool_node.dependencies, 
                completed_tools,
                execution_context
            )
```

DAG execution with topological sorting ensures proper dependency resolution for data processing workflows. Dependency checking and input preparation enable complex data flow between tools.

```python            
            # Execute tool with timeout and retry logic
            tool_result = await self._execute_single_tool_with_monitoring(
                tool_node, tool_input, workflow_result.workflow_id
            )
            
            # Record tool execution results
            completed_tools[tool_name] = tool_result
            workflow_result.tool_results[tool_name] = tool_result
            
            if tool_result.success:
                workflow_result.executed_tools.append(tool_name)
                
                # Update global execution context with tool outputs
                execution_context[f"{tool_name}_output"] = tool_result.data
                execution_context[f"{tool_name}_metadata"] = tool_result.metadata
                
            else:
                workflow_result.failed_tools.append(tool_name)
                
                # Check if this tool failure should stop workflow
                if tool_node.conditions and tool_node.conditions.get("stop_on_failure", False):
                    self.logger.error(f"Critical tool {tool_name} failed - stopping workflow")
                    break
            
        except Exception as e:
            self.logger.error(f"Tool {tool_name} execution failed with exception: {str(e)}")
            workflow_result.failed_tools.append(tool_name)
            
            # Create error result for tracking
            error_result = DataProcessingResult(success=False)
            error_result.add_error(str(e))
            workflow_result.tool_results[tool_name] = error_result
```

Tool execution within DAG workflow includes comprehensive error handling, result tracking, and context management. Success/failure tracking and conditional stopping enable robust workflow execution.

---

## 📝 Multiple Choice Test - Module C

Test your understanding of custom tool development for data engineering systems:

**Question 1:** What components are included in the `DataToolContext` class for comprehensive execution metadata?  
A) Only execution_id and timestamp  
B) execution_id, user_id, session_id, request_timestamp, dataset_metadata, processing_options, quality_requirements, and performance_targets  
C) Just user context and session data  
D) Only dataset metadata and processing options  

**Question 2:** What is the primary purpose of the `DataProcessingResult` class?  
A) Store only successful results  
B) Provide structured result container with errors, warnings, performance metrics, and quality metrics  
C) Handle database connections  
D) Manage tool registration  

**Question 3:** Which execution modes are supported by the `ToolExecutionMode` enum for workflow orchestration?  
A) Only SEQUENTIAL and PARALLEL  
B) SEQUENTIAL, PARALLEL, CONDITIONAL, PIPELINE, and DAG  
C) Just DAG and PIPELINE  
D) Only CONDITIONAL execution  

**Question 4:** What does the DAG-based workflow execution provide for data processing workflows?  
A) Simple sequential execution  
B) Complex dependency management with topological sorting and dependency resolution  
C) Only parallel processing  
D) Basic error handling  

**Question 5:** What features does the `EnterpriseDataWarehouseTool` provide for data warehouse operations?  
A) Only basic SQL execution  
B) Connection pooling, query optimization, result caching, and security validation  
C) Just connection management  
D) Only result formatting  

[**View Test Solutions →**](Session2_ModuleC_Test_Solutions.md)

---

## Module Summary

You've now mastered custom tool development for enterprise data processing systems:

✅ **Advanced Tool Architecture**: Built sophisticated tool foundations with comprehensive execution context and result management  
✅ **Specialized Data Processing Tools**: Developed enterprise-grade tools for data warehouses, streaming data, and ML pipelines  
✅ **Tool Integration & Orchestration**: Created advanced workflow orchestration with DAG-based execution and dependency management  
✅ **Production-Ready Patterns**: Implemented robust error handling, caching, retry logic, and performance monitoring

### Next Steps
- **Continue to Module D**: [Performance Monitoring](Session2_ModuleD_Performance_Monitoring.md) for data system optimization and observability
- **Return to Core**: [Session 2 Main](Session2_LangChain_Foundations.md)
- **Advance to Session 3**: [LangGraph Multi-Agent Workflows](Session3_LangGraph_Multi_Agent_Workflows.md)

---

**🗂️ Source Files for Module C:**
- `src/session2/tool_foundations.py` - Core tool development patterns and architecture
- `src/session2/data_warehouse_tools.py` - Enterprise data warehouse integration tools
- `src/session2/streaming_data_tools.py` - Real-time streaming data processing tools
- `src/session2/ml_pipeline_tools.py` - Machine learning pipeline integration tools
- `src/session2/tool_orchestration.py` - Advanced tool workflow orchestration systems