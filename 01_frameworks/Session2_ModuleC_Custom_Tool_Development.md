# Session 2 - Module C: Custom Tool Development (45 minutes)

**Prerequisites**: [Session 2 Core Section Complete](Session2_LangChain_Foundations.md)  
**Target Audience**: Developers wanting customization  
**Cognitive Load**: 5 specialized concepts

---

## 🎯 Module Overview

This module focuses on building sophisticated custom tools for LangChain agents with advanced patterns including Pydantic validation, API integration, database connectivity, and external system integration with proper error handling and performance optimization.

### Learning Objectives
By the end of this module, you will:
- Create advanced tools using Pydantic models for structured inputs and outputs
- Build tools that integrate with external APIs with authentication and rate limiting
- Implement database and file system tools with proper connection management
- Design tools with comprehensive error recovery and performance monitoring

---

## Part 1: Advanced Tool Creation Patterns (15 minutes)

### Pydantic-Based Tool Architecture

🗂️ **File**: `src/session2/advanced_tool_patterns.py` - Production-ready tool implementations

Modern LangChain tools benefit from structured input/output validation using Pydantic models for type safety and automatic documentation:

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union, Literal
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import logging

class AdvancedToolInput(BaseModel):
    """Base class for advanced tool inputs with validation"""
    
    class Config:
        extra = "forbid"  # Prevent unexpected fields
        validate_assignment = True  # Validate on assignment
        use_enum_values = True  # Use enum values in serialization

class DataAnalysisInput(AdvancedToolInput):
    """Input model for data analysis tool"""
    
    data_source: str = Field(
        description="Data source identifier or file path",
        min_length=1,
        max_length=500
    )
    analysis_type: Literal["descriptive", "diagnostic", "predictive", "prescriptive"] = Field(
        description="Type of analysis to perform"
    )
    columns: Optional[List[str]] = Field(
        default=None,
        description="Specific columns to analyze (if applicable)"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Filters to apply to the data"
    )
    output_format: Literal["json", "csv", "summary"] = Field(
        default="json",
        description="Format for the analysis output"
    )
    
    @validator('columns')
    def validate_columns(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("columns list cannot be empty if provided")
        return v
    
    @validator('filters')
    def validate_filters(cls, v):
        # Ensure filter values are JSON serializable
        try:
            json.dumps(v)
        except (TypeError, ValueError):
            raise ValueError("filters must contain JSON-serializable values")
        return v

class DataAnalysisOutput(BaseModel):
    """Structured output for data analysis results"""
    
    analysis_id: str = Field(description="Unique identifier for this analysis")
    timestamp: datetime = Field(description="When the analysis was performed")
    data_summary: Dict[str, Any] = Field(description="Summary statistics about the data")
    analysis_results: Dict[str, Any] = Field(description="Main analysis results")
    insights: List[str] = Field(description="Key insights discovered")
    recommendations: List[str] = Field(description="Actionable recommendations")
    confidence_level: float = Field(
        ge=0.0, le=1.0,
        description="Confidence level of the analysis (0.0 to 1.0)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the analysis"
    )

class AdvancedDataAnalysisTool(BaseTool):
    """Advanced data analysis tool with structured I/O and comprehensive error handling"""
    
    name = "advanced_data_analysis"
    description = """
    Perform comprehensive data analysis with structured outputs.
    Supports descriptive, diagnostic, predictive, and prescriptive analytics.
    Returns structured results with insights and recommendations.
    """
    
    args_schema = DataAnalysisInput
    return_direct = False
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.config = config or {}
        self.analysis_cache = {}
        self.performance_metrics = {
            "total_analyses": 0,
            "avg_execution_time": 0.0,
            "success_rate": 1.0,
            "cache_hit_rate": 0.0
        }
        self.logger = logging.getLogger(__name__)
    
    def _run(self, data_source: str, analysis_type: str, 
             columns: Optional[List[str]] = None,
             filters: Optional[Dict[str, Any]] = None,
             output_format: str = "json") -> str:
        """Execute data analysis with comprehensive error handling"""
        
        analysis_start_time = datetime.now()
        analysis_id = f"analysis_{analysis_start_time.strftime('%Y%m%d_%H%M%S')}_{hash(data_source) % 10000}"
        
        try:
            # Update performance metrics
            self.performance_metrics["total_analyses"] += 1
            
            # Check cache first
            cache_key = self._generate_cache_key(data_source, analysis_type, columns, filters)
            if cache_key in self.analysis_cache:
                cached_result, cache_time = self.analysis_cache[cache_key]
                if datetime.now() - cache_time < timedelta(hours=1):  # Cache for 1 hour
                    self._update_cache_hit_rate(True)
                    return cached_result.json()
            
            self._update_cache_hit_rate(False)
            
            # Load and validate data
            data = self._load_data(data_source)
            validated_data = self._validate_data(data, columns, filters)
            
            # Perform analysis based on type
            if analysis_type == "descriptive":
                results = self._perform_descriptive_analysis(validated_data)
            elif analysis_type == "diagnostic":
                results = self._perform_diagnostic_analysis(validated_data)
            elif analysis_type == "predictive":
                results = self._perform_predictive_analysis(validated_data)
            elif analysis_type == "prescriptive":
                results = self._perform_prescriptive_analysis(validated_data)
            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")
            
            # Generate insights and recommendations
            insights = self._generate_insights(results, analysis_type)
            recommendations = self._generate_recommendations(results, insights, analysis_type)
            
            # Calculate confidence level
            confidence = self._calculate_confidence(results, validated_data)
            
            # Create structured output
            analysis_output = DataAnalysisOutput(
                analysis_id=analysis_id,
                timestamp=analysis_start_time,
                data_summary=self._create_data_summary(validated_data),
                analysis_results=results,
                insights=insights,
                recommendations=recommendations,
                confidence_level=confidence,
                metadata={
                    "analysis_type": analysis_type,
                    "data_source": data_source,
                    "execution_time": (datetime.now() - analysis_start_time).total_seconds(),
                    "columns_analyzed": columns or "all",
                    "filters_applied": bool(filters)
                }
            )
            
            # Cache the result
            self.analysis_cache[cache_key] = (analysis_output, datetime.now())
            
            # Update performance metrics
            execution_time = (datetime.now() - analysis_start_time).total_seconds()
            self._update_performance_metrics(execution_time, True)
            
            # Return in requested format
            if output_format == "json":
                return analysis_output.json(indent=2)
            elif output_format == "summary":
                return self._create_summary_output(analysis_output)
            else:
                return analysis_output.json()
                
        except Exception as e:
            self.logger.error(f"Analysis failed for {analysis_id}: {str(e)}")
            self._update_performance_metrics(0, False)
            
            # Return structured error response
            error_output = {
                "analysis_id": analysis_id,
                "timestamp": analysis_start_time.isoformat(),
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__
            }
            return json.dumps(error_output, indent=2)
    
    def _load_data(self, data_source: str) -> Dict[str, Any]:
        """Load data from various sources with error handling"""
        
        if data_source.startswith("http"):
            return self._load_from_url(data_source)
        elif data_source.endswith((".csv", ".json", ".xlsx")):
            return self._load_from_file(data_source)
        elif data_source.startswith("db://"):
            return self._load_from_database(data_source)
        else:
            # Assume it's raw JSON data
            try:
                return json.loads(data_source)
            except json.JSONDecodeError:
                raise ValueError(f"Unable to parse data source: {data_source}")
    
    def _perform_descriptive_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform descriptive statistical analysis"""
        
        results = {
            "summary_statistics": {},
            "data_quality": {},
            "distributions": {},
            "correlations": {}
        }
        
        # Implement descriptive analysis logic
        # This is a simplified example - in production, use pandas, numpy, etc.
        
        if isinstance(data, dict) and "records" in data:
            records = data["records"]
            results["summary_statistics"]["total_records"] = len(records)
            results["summary_statistics"]["fields"] = list(records[0].keys()) if records else []
            
            # Calculate basic statistics for numeric fields
            numeric_fields = []
            for field in results["summary_statistics"]["fields"]:
                try:
                    values = [float(record.get(field, 0)) for record in records if record.get(field) is not None]
                    if values:
                        numeric_fields.append(field)
                        results["summary_statistics"][f"{field}_mean"] = sum(values) / len(values)
                        results["summary_statistics"][f"{field}_min"] = min(values)
                        results["summary_statistics"][f"{field}_max"] = max(values)
                except (ValueError, TypeError):
                    continue
            
            results["summary_statistics"]["numeric_fields"] = numeric_fields
        
        return results
    
    def _generate_insights(self, results: Dict[str, Any], analysis_type: str) -> List[str]:
        """Generate meaningful insights from analysis results"""
        
        insights = []
        
        if analysis_type == "descriptive":
            stats = results.get("summary_statistics", {})
            total_records = stats.get("total_records", 0)
            numeric_fields = stats.get("numeric_fields", [])
            
            insights.append(f"Dataset contains {total_records} records with {len(numeric_fields)} numeric fields")
            
            for field in numeric_fields:
                mean_val = stats.get(f"{field}_mean")
                min_val = stats.get(f"{field}_min")
                max_val = stats.get(f"{field}_max")
                
                if mean_val is not None:
                    range_val = max_val - min_val if max_val and min_val else 0
                    insights.append(f"{field}: average {mean_val:.2f}, range {range_val:.2f}")
        
        return insights
    
    def _generate_recommendations(self, results: Dict[str, Any], insights: List[str], 
                                analysis_type: str) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        if analysis_type == "descriptive":
            stats = results.get("summary_statistics", {})
            total_records = stats.get("total_records", 0)
            
            if total_records < 100:
                recommendations.append("Consider collecting more data for more robust analysis")
            
            numeric_fields = stats.get("numeric_fields", [])
            if len(numeric_fields) > 5:
                recommendations.append("Consider dimensionality reduction techniques for better visualization")
            
            recommendations.append("Explore correlations between numeric variables")
            recommendations.append("Consider outlier detection and treatment")
        
        return recommendations
    
    def _calculate_confidence(self, results: Dict[str, Any], data: Dict[str, Any]) -> float:
        """Calculate confidence level based on data quality and analysis completeness"""
        
        confidence_factors = []
        
        # Data size factor
        if isinstance(data, dict) and "records" in data:
            record_count = len(data["records"])
            if record_count >= 1000:
                confidence_factors.append(0.9)
            elif record_count >= 100:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.6)
        
        # Analysis completeness factor
        if results and len(results) > 2:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        # Return average confidence
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
```

---

## Part 2: API Integration Tools (15 minutes)

### Advanced API Integration with Authentication

🗂️ **File**: `src/session2/api_integration_tools.py` - API integration patterns

```python
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import time
import hashlib
import jwt
from datetime import datetime, timedelta

class AuthenticationType(Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    JWT = "jwt"

@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    backoff_factor: float = 1.5

class APIIntegrationInput(AdvancedToolInput):
    """Input model for API integration tool"""
    
    endpoint: str = Field(description="API endpoint URL")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field(default="GET")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    timeout: int = Field(default=30, ge=1, le=300)
    retry_attempts: int = Field(default=3, ge=0, le=10)
    cache_duration: int = Field(default=300, ge=0, le=3600)  # seconds

class AdvancedAPITool(BaseTool):
    """Advanced API integration tool with authentication, rate limiting, and caching"""
    
    name = "advanced_api_integration"
    description = """
    Integrate with external APIs with comprehensive features:
    - Multiple authentication methods
    - Rate limiting and backoff
    - Caching and retry logic
    - Response validation and error handling
    """
    
    args_schema = APIIntegrationInput
    
    def __init__(self, api_config: Dict[str, Any]):
        super().__init__()
        self.api_config = api_config
        self.auth_type = AuthenticationType(api_config.get("auth_type", "none"))
        self.rate_limit_config = RateLimitConfig(**api_config.get("rate_limit", {}))
        
        # Rate limiting state
        self.request_history = []
        self.last_request_time = 0
        
        # Caching
        self.response_cache = {}
        
        # Performance metrics
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0,
            "rate_limit_hits": 0
        }
    
    def _run(self, endpoint: str, method: str = "GET", 
             headers: Optional[Dict[str, str]] = None,
             params: Optional[Dict[str, Any]] = None,
             data: Optional[Dict[str, Any]] = None,
             timeout: int = 30, retry_attempts: int = 3,
             cache_duration: int = 300) -> str:
        """Execute API request with full feature set"""
        
        # Run async method in sync context
        return asyncio.run(
            self._execute_api_request(
                endpoint, method, headers, params, data, 
                timeout, retry_attempts, cache_duration
            )
        )
    
    async def _execute_api_request(self, endpoint: str, method: str,
                                 headers: Optional[Dict[str, str]],
                                 params: Optional[Dict[str, Any]],
                                 data: Optional[Dict[str, Any]],
                                 timeout: int, retry_attempts: int,
                                 cache_duration: int) -> str:
        """Execute API request with comprehensive error handling"""
        
        request_start_time = time.time()
        self.performance_metrics["total_requests"] += 1
        
        try:
            # Check rate limits
            if not await self._check_rate_limit():
                self.performance_metrics["rate_limit_hits"] += 1
                return json.dumps({
                    "error": "Rate limit exceeded",
                    "retry_after": self._get_retry_after_seconds()
                })
            
            # Check cache
            cache_key = self._generate_cache_key(endpoint, method, params, data)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self.performance_metrics["cache_hits"] += 1
                return cached_response
            
            # Prepare headers with authentication
            request_headers = await self._prepare_headers(headers or {})
            
            # Execute request with retries
            for attempt in range(retry_attempts + 1):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.request(
                            method=method,
                            url=endpoint,
                            headers=request_headers,
                            params=params,
                            json=data if method != "GET" else None,
                            timeout=aiohttp.ClientTimeout(total=timeout)
                        ) as response:
                            
                            response_text = await response.text()
                            
                            if response.status == 200:
                                # Success - cache and return
                                self.performance_metrics["successful_requests"] += 1
                                
                                result = {
                                    "status_code": response.status,
                                    "response": response_text,
                                    "headers": dict(response.headers),
                                    "execution_time": time.time() - request_start_time,
                                    "cached": False
                                }
                                
                                # Cache successful responses
                                self._cache_response(cache_key, json.dumps(result), cache_duration)
                                
                                # Update performance metrics
                                self._update_response_time_metric(time.time() - request_start_time)
                                
                                return json.dumps(result, indent=2)
                            
                            elif response.status == 429:  # Rate limited
                                retry_after = int(response.headers.get("Retry-After", 60))
                                if attempt < retry_attempts:
                                    await asyncio.sleep(retry_after)
                                    continue
                                else:
                                    return json.dumps({
                                        "error": "Rate limited by API",
                                        "status_code": response.status,
                                        "retry_after": retry_after
                                    })
                            
                            elif 500 <= response.status < 600:  # Server errors - retry
                                if attempt < retry_attempts:
                                    wait_time = (2 ** attempt) * self.rate_limit_config.backoff_factor
                                    await asyncio.sleep(wait_time)
                                    continue
                                else:
                                    return json.dumps({
                                        "error": f"Server error after {retry_attempts} retries",
                                        "status_code": response.status,
                                        "response": response_text
                                    })
                            
                            else:  # Client errors - don't retry
                                return json.dumps({
                                    "error": "Client error",
                                    "status_code": response.status,
                                    "response": response_text
                                })
                
                except asyncio.TimeoutError:
                    if attempt < retry_attempts:
                        continue
                    else:
                        return json.dumps({
                            "error": f"Request timeout after {retry_attempts} retries",
                            "timeout": timeout
                        })
                
                except aiohttp.ClientError as e:
                    if attempt < retry_attempts:
                        continue
                    else:
                        return json.dumps({
                            "error": f"Network error: {str(e)}"
                        })
        
        except Exception as e:
            self.performance_metrics["failed_requests"] += 1
            return json.dumps({
                "error": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__
            })
    
    async def _prepare_headers(self, base_headers: Dict[str, str]) -> Dict[str, str]:
        """Prepare headers with authentication"""
        
        headers = base_headers.copy()
        headers["User-Agent"] = "LangChain-AdvancedAPITool/1.0"
        
        if self.auth_type == AuthenticationType.API_KEY:
            api_key = self.api_config.get("api_key")
            key_header = self.api_config.get("api_key_header", "X-API-Key")
            if api_key:
                headers[key_header] = api_key
        
        elif self.auth_type == AuthenticationType.BEARER_TOKEN:
            token = self.api_config.get("bearer_token")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        elif self.auth_type == AuthenticationType.BASIC_AUTH:
            username = self.api_config.get("username")
            password = self.api_config.get("password")
            if username and password:
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers["Authorization"] = f"Basic {credentials}"
        
        elif self.auth_type == AuthenticationType.JWT:
            jwt_token = await self._generate_jwt_token()
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
        
        elif self.auth_type == AuthenticationType.OAUTH2:
            oauth_token = await self._get_oauth2_token()
            if oauth_token:
                headers["Authorization"] = f"Bearer {oauth_token}"
        
        return headers
    
    async def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        
        current_time = time.time()
        
        # Clean old requests from history
        cutoff_time = current_time - 60  # Last minute
        self.request_history = [
            req_time for req_time in self.request_history 
            if req_time > cutoff_time
        ]
        
        # Check requests per minute
        if len(self.request_history) >= self.rate_limit_config.requests_per_minute:
            return False
        
        # Check burst limit
        recent_requests = [
            req_time for req_time in self.request_history
            if req_time > current_time - 10  # Last 10 seconds
        ]
        
        if len(recent_requests) >= self.rate_limit_config.burst_limit:
            return False
        
        # Add current request to history
        self.request_history.append(current_time)
        self.last_request_time = current_time
        
        return True
    
    def _generate_cache_key(self, endpoint: str, method: str, 
                          params: Optional[Dict[str, Any]], 
                          data: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for request"""
        
        key_components = [
            endpoint,
            method,
            json.dumps(params or {}, sort_keys=True),
            json.dumps(data or {}, sort_keys=True)
        ]
        
        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if still valid"""
        
        if cache_key in self.response_cache:
            cached_data, cache_time = self.response_cache[cache_key]
            if time.time() - cache_time < 300:  # 5 minute default cache
                return cached_data
            else:
                del self.response_cache[cache_key]
        
        return None
    
    def _cache_response(self, cache_key: str, response: str, duration: int):
        """Cache response for specified duration"""
        
        self.response_cache[cache_key] = (response, time.time())
        
        # Clean old cache entries periodically
        if len(self.response_cache) % 100 == 0:
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Remove expired cache entries"""
        
        current_time = time.time()
        expired_keys = [
            key for key, (_, cache_time) in self.response_cache.items()
            if current_time - cache_time > 3600  # 1 hour max cache
        ]
        
        for key in expired_keys:
            del self.response_cache[key]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        
        total_requests = self.performance_metrics["total_requests"]
        success_rate = (
            self.performance_metrics["successful_requests"] / total_requests * 100
            if total_requests > 0 else 0
        )
        
        cache_hit_rate = (
            self.performance_metrics["cache_hits"] / total_requests * 100
            if total_requests > 0 else 0
        )
        
        return {
            "total_requests": total_requests,
            "success_rate_percentage": round(success_rate, 2),
            "avg_response_time_seconds": round(self.performance_metrics["avg_response_time"], 3),
            "cache_hit_rate_percentage": round(cache_hit_rate, 2),
            "rate_limit_hits": self.performance_metrics["rate_limit_hits"],
            "cached_responses": len(self.response_cache)
        }
```

---

## Part 3: Database & External System Integration (15 minutes)

### Advanced Database Integration

🗂️ **File**: `src/session2/database_integration_tools.py` - Database connectivity patterns

```python
import asyncio
import aiosqlite
import asyncpg
import aiomysql
from typing import Dict, List, Any, Optional, Union, Literal
from dataclasses import dataclass
import json
from datetime import datetime
import logging

class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"

class DatabaseConnectionConfig(BaseModel):
    """Database connection configuration"""
    
    db_type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    connection_pool_size: int = Field(default=10, ge=1, le=100)
    connection_timeout: int = Field(default=30, ge=5, le=300)
    query_timeout: int = Field(default=60, ge=5, le=600)
    ssl_mode: Optional[str] = None

class DatabaseQueryInput(AdvancedToolInput):
    """Input model for database operations"""
    
    query: str = Field(description="SQL query to execute")
    parameters: Optional[List[Any]] = Field(
        default_factory=list,
        description="Query parameters for prepared statements"
    )
    operation_type: Literal["select", "insert", "update", "delete", "transaction"] = Field(
        description="Type of database operation"
    )
    fetch_size: Optional[int] = Field(
        default=None, ge=1, le=10000,
        description="Maximum number of rows to fetch (for SELECT queries)"
    )
    timeout: int = Field(default=60, ge=5, le=600)
    transaction_id: Optional[str] = Field(
        default=None,
        description="Transaction ID for multi-query transactions"
    )
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Basic SQL injection protection
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER']
        query_upper = v.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper and 'WHERE' not in query_upper:
                raise ValueError(f"Potentially dangerous query with {keyword} without WHERE clause")
        
        return v

class AdvancedDatabaseTool(BaseTool):
    """Advanced database integration tool with connection pooling and transaction support"""
    
    name = "advanced_database_tool"
    description = """
    Execute database operations with enterprise features:
    - Connection pooling and management
    - Transaction support
    - Query optimization and caching
    - Comprehensive error handling and monitoring
    """
    
    args_schema = DatabaseQueryInput
    
    def __init__(self, db_config: DatabaseConnectionConfig):
        super().__init__()
        self.db_config = db_config
        self.connection_pool = None
        self.active_transactions = {}
        self.query_cache = {}
        
        # Performance monitoring
        self.performance_metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_query_time": 0.0,
            "cache_hits": 0,
            "active_connections": 0,
            "transaction_count": 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize connection pool
        asyncio.create_task(self._initialize_connection_pool())
    
    async def _initialize_connection_pool(self):
        """Initialize database connection pool"""
        
        try:
            if self.db_config.db_type == DatabaseType.POSTGRESQL:
                self.connection_pool = await asyncpg.create_pool(
                    host=self.db_config.host,
                    port=self.db_config.port or 5432,
                    database=self.db_config.database,
                    user=self.db_config.username,
                    password=self.db_config.password,
                    min_size=1,
                    max_size=self.db_config.connection_pool_size,
                    command_timeout=self.db_config.query_timeout
                )
            
            elif self.db_config.db_type == DatabaseType.MYSQL:
                self.connection_pool = await aiomysql.create_pool(
                    host=self.db_config.host,
                    port=self.db_config.port or 3306,
                    db=self.db_config.database,
                    user=self.db_config.username,
                    password=self.db_config.password,
                    minsize=1,
                    maxsize=self.db_config.connection_pool_size
                )
            
            elif self.db_config.db_type == DatabaseType.SQLITE:
                # SQLite doesn't use traditional connection pooling
                pass
            
            self.logger.info(f"Database connection pool initialized for {self.db_config.db_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise e
    
    def _run(self, query: str, parameters: Optional[List[Any]] = None,
             operation_type: str = "select", fetch_size: Optional[int] = None,
             timeout: int = 60, transaction_id: Optional[str] = None) -> str:
        """Execute database operation"""
        
        return asyncio.run(
            self._execute_database_operation(
                query, parameters, operation_type, fetch_size, timeout, transaction_id
            )
        )
    
    async def _execute_database_operation(self, query: str, parameters: Optional[List[Any]],
                                        operation_type: str, fetch_size: Optional[int],
                                        timeout: int, transaction_id: Optional[str]) -> str:
        """Execute database operation with comprehensive handling"""
        
        query_start_time = datetime.now()
        self.performance_metrics["total_queries"] += 1
        
        try:
            # Check cache for SELECT queries
            if operation_type == "select":
                cache_key = self._generate_query_cache_key(query, parameters)
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    self.performance_metrics["cache_hits"] += 1
                    return cached_result
            
            # Handle transaction operations
            if transaction_id:
                return await self._execute_in_transaction(
                    query, parameters, operation_type, fetch_size, timeout, transaction_id
                )
            
            # Execute single query
            if self.db_config.db_type == DatabaseType.POSTGRESQL:
                result = await self._execute_postgresql_query(
                    query, parameters, operation_type, fetch_size, timeout
                )
            elif self.db_config.db_type == DatabaseType.MYSQL:
                result = await self._execute_mysql_query(
                    query, parameters, operation_type, fetch_size, timeout
                )
            elif self.db_config.db_type == DatabaseType.SQLITE:
                result = await self._execute_sqlite_query(
                    query, parameters, operation_type, fetch_size, timeout
                )
            else:
                raise ValueError(f"Unsupported database type: {self.db_config.db_type}")
            
            # Cache SELECT results
            if operation_type == "select":
                cache_key = self._generate_query_cache_key(query, parameters)
                self._cache_result(cache_key, result)
            
            # Update performance metrics
            execution_time = (datetime.now() - query_start_time).total_seconds()
            self._update_query_metrics(execution_time, True)
            
            self.performance_metrics["successful_queries"] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Database operation failed: {str(e)}")
            self.performance_metrics["failed_queries"] += 1
            
            return json.dumps({
                "error": str(e),
                "error_type": type(e).__name__,
                "query": query[:100] + "..." if len(query) > 100 else query,
                "operation_type": operation_type
            })
    
    async def _execute_postgresql_query(self, query: str, parameters: Optional[List[Any]],
                                      operation_type: str, fetch_size: Optional[int],
                                      timeout: int) -> str:
        """Execute PostgreSQL query"""
        
        async with self.connection_pool.acquire() as connection:
            self.performance_metrics["active_connections"] += 1
            
            try:
                if operation_type == "select":
                    if parameters:
                        rows = await connection.fetch(query, *parameters)
                    else:
                        rows = await connection.fetch(query)
                    
                    # Apply fetch size limit
                    if fetch_size and len(rows) > fetch_size:
                        rows = rows[:fetch_size]
                    
                    # Convert to JSON serializable format
                    result_data = []
                    for row in rows:
                        result_data.append(dict(row))
                    
                    return json.dumps({
                        "status": "success",
                        "operation": operation_type,
                        "rows_returned": len(result_data),
                        "data": result_data,
                        "truncated": fetch_size and len(rows) == fetch_size
                    }, default=str, indent=2)
                
                else:
                    # INSERT, UPDATE, DELETE operations
                    if parameters:
                        result = await connection.execute(query, *parameters)
                    else:
                        result = await connection.execute(query)
                    
                    return json.dumps({
                        "status": "success",
                        "operation": operation_type,
                        "result": result,
                        "rows_affected": self._extract_rows_affected(result)
                    }, indent=2)
            
            finally:
                self.performance_metrics["active_connections"] -= 1
    
    async def _execute_sqlite_query(self, query: str, parameters: Optional[List[Any]],
                                   operation_type: str, fetch_size: Optional[int],
                                   timeout: int) -> str:
        """Execute SQLite query"""
        
        async with aiosqlite.connect(self.db_config.database) as connection:
            self.performance_metrics["active_connections"] += 1
            
            try:
                cursor = await connection.cursor()
                
                if parameters:
                    await cursor.execute(query, parameters)
                else:
                    await cursor.execute(query)
                
                if operation_type == "select":
                    rows = await cursor.fetchall()
                    
                    # Get column names
                    column_names = [description[0] for description in cursor.description]
                    
                    # Apply fetch size limit
                    if fetch_size and len(rows) > fetch_size:
                        rows = rows[:fetch_size]
                    
                    # Convert to JSON format
                    result_data = []
                    for row in rows:
                        result_data.append(dict(zip(column_names, row)))
                    
                    return json.dumps({
                        "status": "success",
                        "operation": operation_type,
                        "rows_returned": len(result_data),
                        "data": result_data,
                        "truncated": fetch_size and len(rows) == fetch_size
                    }, default=str, indent=2)
                
                else:
                    await connection.commit()
                    rows_affected = cursor.rowcount
                    
                    return json.dumps({
                        "status": "success",
                        "operation": operation_type,
                        "rows_affected": rows_affected
                    }, indent=2)
            
            finally:
                self.performance_metrics["active_connections"] -= 1
    
    async def begin_transaction(self, transaction_id: str) -> str:
        """Begin a new database transaction"""
        
        if transaction_id in self.active_transactions:
            return json.dumps({"error": f"Transaction {transaction_id} already exists"})
        
        try:
            if self.db_config.db_type == DatabaseType.POSTGRESQL:
                connection = await self.connection_pool.acquire()
                transaction = connection.transaction()
                await transaction.start()
                
                self.active_transactions[transaction_id] = {
                    "connection": connection,
                    "transaction": transaction,
                    "start_time": datetime.now()
                }
            
            elif self.db_config.db_type == DatabaseType.SQLITE:
                connection = await aiosqlite.connect(self.db_config.database)
                await connection.execute("BEGIN TRANSACTION")
                
                self.active_transactions[transaction_id] = {
                    "connection": connection,
                    "start_time": datetime.now()
                }
            
            self.performance_metrics["transaction_count"] += 1
            
            return json.dumps({
                "status": "success",
                "transaction_id": transaction_id,
                "message": "Transaction started successfully"
            })
            
        except Exception as e:
            return json.dumps({
                "error": f"Failed to start transaction: {str(e)}",
                "transaction_id": transaction_id
            })
    
    async def commit_transaction(self, transaction_id: str) -> str:
        """Commit a database transaction"""
        
        if transaction_id not in self.active_transactions:
            return json.dumps({"error": f"Transaction {transaction_id} not found"})
        
        try:
            transaction_data = self.active_transactions[transaction_id]
            
            if self.db_config.db_type == DatabaseType.POSTGRESQL:
                await transaction_data["transaction"].commit()
                await self.connection_pool.release(transaction_data["connection"])
            
            elif self.db_config.db_type == DatabaseType.SQLITE:
                await transaction_data["connection"].commit()
                await transaction_data["connection"].close()
            
            # Calculate transaction duration
            duration = (datetime.now() - transaction_data["start_time"]).total_seconds()
            
            # Clean up
            del self.active_transactions[transaction_id]
            
            return json.dumps({
                "status": "success",
                "transaction_id": transaction_id,
                "duration_seconds": duration,
                "message": "Transaction committed successfully"
            })
            
        except Exception as e:
            # Attempt rollback on commit failure
            await self.rollback_transaction(transaction_id)
            
            return json.dumps({
                "error": f"Failed to commit transaction: {str(e)}",
                "transaction_id": transaction_id,
                "action": "Transaction rolled back"
            })
    
    async def rollback_transaction(self, transaction_id: str) -> str:
        """Rollback a database transaction"""
        
        if transaction_id not in self.active_transactions:
            return json.dumps({"error": f"Transaction {transaction_id} not found"})
        
        try:
            transaction_data = self.active_transactions[transaction_id]
            
            if self.db_config.db_type == DatabaseType.POSTGRESQL:
                await transaction_data["transaction"].rollback()
                await self.connection_pool.release(transaction_data["connection"])
            
            elif self.db_config.db_type == DatabaseType.SQLITE:
                await transaction_data["connection"].rollback()
                await transaction_data["connection"].close()
            
            # Clean up
            del self.active_transactions[transaction_id]
            
            return json.dumps({
                "status": "success",
                "transaction_id": transaction_id,
                "message": "Transaction rolled back successfully"
            })
            
        except Exception as e:
            return json.dumps({
                "error": f"Failed to rollback transaction: {str(e)}",
                "transaction_id": transaction_id
            })
    
    def get_database_metrics(self) -> Dict[str, Any]:
        """Get comprehensive database performance metrics"""
        
        total_queries = self.performance_metrics["total_queries"]
        success_rate = (
            self.performance_metrics["successful_queries"] / total_queries * 100
            if total_queries > 0 else 0
        )
        
        cache_hit_rate = (
            self.performance_metrics["cache_hits"] / total_queries * 100
            if total_queries > 0 else 0
        )
        
        return {
            "database_type": self.db_config.db_type.value,
            "total_queries": total_queries,
            "success_rate_percentage": round(success_rate, 2),
            "avg_query_time_seconds": round(self.performance_metrics["avg_query_time"], 3),
            "cache_hit_rate_percentage": round(cache_hit_rate, 2),
            "active_connections": self.performance_metrics["active_connections"],
            "active_transactions": len(self.active_transactions),
            "total_transactions": self.performance_metrics["transaction_count"],
            "cached_queries": len(self.query_cache)
        }
```

---

## 🎯 Module Summary

You've now mastered custom tool development for LangChain with enterprise features:

✅ **Advanced Tool Creation Patterns**: Built tools with Pydantic validation and structured I/O  
✅ **API Integration Tools**: Implemented authentication, rate limiting, and caching for external APIs  
✅ **Database & External System Integration**: Created production-ready database tools with connection pooling  
✅ **Performance & Error Handling**: Designed comprehensive monitoring and recovery mechanisms

### Next Steps
- **Continue to Module D**: [Performance & Monitoring](Session2_ModuleD_Performance_Monitoring.md) for optimization strategies
- **Return to Core**: [Session 2 Main](Session2_LangChain_Foundations.md)
- **Advance to Session 3**: [LangGraph Multi-Agent Workflows](Session3_LangGraph_Multi_Agent_Workflows.md)

---

**🗂️ Source Files for Module C:**
- `src/session2/advanced_tool_patterns.py` - Pydantic-based tool architecture
- `src/session2/api_integration_tools.py` - Advanced API integration patterns
- `src/session2/database_integration_tools.py` - Database connectivity and transaction management