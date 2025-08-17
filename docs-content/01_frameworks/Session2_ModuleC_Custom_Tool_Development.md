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

Modern LangChain tools benefit from structured input/output validation using Pydantic models for type safety and automatic documentation. The foundation starts with imports and base classes:

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
```

The `AdvancedToolInput` base class establishes strict validation rules that prevent unexpected fields and ensure data integrity throughout tool execution.

```python
class DataAnalysisInput(AdvancedToolInput):
    """Input model for data analysis tool"""
```

Specialized input models inherit from the base class, gaining automatic validation while defining specific field requirements for their domain.

```python
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
```
    
Custom validators ensure data quality and prevent common errors:

```python
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
```

Validators prevent empty column lists and ensure filters are JSON-serializable, catching data issues before they cause runtime errors.

```python
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
```

The output model provides comprehensive structure including unique identifiers, timestamps, analysis results, insights, recommendations, and confidence levels with proper constraints.

The advanced tool implementation combines structured I/O with performance tracking:

```python
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
```

The tool class specifies its schema, enabling automatic validation and documentation generation for agent interactions.

```python
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
```

Initialization sets up caching, performance tracking, and logging infrastructure essential for production tool deployment.

The tool execution method handles the complete analysis workflow. Let's break this down into logical phases:

```python
    def _run(self, data_source: str, analysis_type: str, 
             columns: Optional[List[str]] = None,
             filters: Optional[Dict[str, Any]] = None,
             output_format: str = "json") -> str:
        """Execute data analysis with comprehensive error handling"""
        
        analysis_start_time = datetime.now()
        analysis_id = f"analysis_{analysis_start_time.strftime('%Y%m%d_%H%M%S')}_{hash(data_source) % 10000}"
```

Analysis execution begins with timing and unique ID generation. Analysis ID enables tracking and debugging while timestamp supports performance monitoring and audit trails.

Phase 1: Cache checking and performance tracking

```python        
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
```

Cache optimization checks for previously computed results before expensive analysis operations. One-hour cache TTL balances result freshness with performance gains.

Phase 2: Data loading and validation

```python            
            # Load and validate data
            data = self._load_data(data_source)
            validated_data = self._validate_data(data, columns, filters)
```

Data loading and validation ensure analysis operates on clean, structured data. Validation prevents errors and ensures analysis reliability across different data sources.

Phase 3: Analysis execution based on type

```python            
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
```

Analysis type routing enables specialized processing for different analytical approaches. Each analysis type implements domain-specific algorithms and statistical methods.

Phase 4: Results enhancement with insights and recommendations

```python            
            # Generate insights and recommendations
            insights = self._generate_insights(results, analysis_type)
            recommendations = self._generate_recommendations(results, insights, analysis_type)
            
            # Calculate confidence level
            confidence = self._calculate_confidence(results, validated_data)
```

Insight generation and confidence calculation transform raw analysis results into actionable intelligence. Confidence scoring helps users understand result reliability.

Phase 5: Structured output creation

```python            
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
```

Structured output packaging includes comprehensive metadata for audit trails and debugging. Execution time and configuration tracking enable performance optimization.

Phase 6: Caching and metrics update

```python            
            # Cache the result
            self.analysis_cache[cache_key] = (analysis_output, datetime.now())
            
            # Update performance metrics
            execution_time = (datetime.now() - analysis_start_time).total_seconds()
            self._update_performance_metrics(execution_time, True)
```

Result caching and performance tracking enable optimization and monitoring. Successful analysis results are cached for reuse while metrics support performance analysis.

Phase 7: Output formatting and return

```python            
            # Return in requested format
            if output_format == "json":
                return analysis_output.json(indent=2)
            elif output_format == "summary":
                return self._create_summary_output(analysis_output)
            else:
                return analysis_output.json()
```

Output formatting provides flexible response types for different client needs. JSON format enables programmatic processing while summary format provides human-readable insights.

Error handling and recovery:

```python                
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
```

Error handling provides structured error responses with comprehensive debugging information. Logging and metrics updates ensure failures are tracked for operational monitoring.

```python    
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
```

Data loading supports multiple source types with intelligent type detection. URL, file, database, and raw JSON handling provides comprehensive data integration capabilities.

```python    
    def _perform_descriptive_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform descriptive statistical analysis"""
        
        results = {
            "summary_statistics": {},
            "data_quality": {},
            "distributions": {},
            "correlations": {}
        }
```

Descriptive analysis framework establishes comprehensive statistical analysis structure. Results dictionary organizes statistics, quality metrics, distributions, and correlations.

```python        
        # Implement descriptive analysis logic
        # This is a simplified example - in production, use pandas, numpy, etc.
        
        if isinstance(data, dict) and "records" in data:
            records = data["records"]
            results["summary_statistics"]["total_records"] = len(records)
            results["summary_statistics"]["fields"] = list(records[0].keys()) if records else []
```

Record processing extracts basic dataset characteristics including record count and field structure. Field identification enables subsequent statistical computation.

```python            
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
```

Numeric field processing calculates essential statistical measures including mean, minimum, and maximum values. Error handling ensures robust processing across different data types.

```python    
    def _generate_insights(self, results: Dict[str, Any], analysis_type: str) -> List[str]:
        """Generate meaningful insights from analysis results"""
        
        insights = []
        
        if analysis_type == "descriptive":
            stats = results.get("summary_statistics", {})
            total_records = stats.get("total_records", 0)
            numeric_fields = stats.get("numeric_fields", [])
            
            insights.append(f"Dataset contains {total_records} records with {len(numeric_fields)} numeric fields")
```

Insight generation transforms statistical results into human-readable observations. Dataset overview provides context for subsequent detailed insights.

```python            
            for field in numeric_fields:
                mean_val = stats.get(f"{field}_mean")
                min_val = stats.get(f"{field}_min")
                max_val = stats.get(f"{field}_max")
                
                if mean_val is not None:
                    range_val = max_val - min_val if max_val and min_val else 0
                    insights.append(f"{field}: average {mean_val:.2f}, range {range_val:.2f}")
        
        return insights
```

Field-specific insights provide detailed statistical summaries with formatted numerical values. Range calculations help identify data distribution characteristics.

```python    
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
```

Recommendation generation provides actionable guidance based on analysis results. Data size and dimensionality assessments guide appropriate analytical next steps.

```python    
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
```

Confidence calculation considers data size as a primary reliability factor. Larger datasets generally provide more statistically significant results.

```python        
        # Analysis completeness factor
        if results and len(results) > 2:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        # Return average confidence
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
```

Analysis completeness and composite confidence scoring provide comprehensive result reliability assessment. Multiple factors ensure confidence accurately reflects analysis quality.

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
```

API integration imports provide comprehensive async HTTP capabilities, authentication libraries, and utility functions for enterprise API integration patterns.

```python
class AuthenticationType(Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    JWT = "jwt"
```

Authentication type enumeration supports all major API authentication patterns. Comprehensive coverage enables integration with diverse enterprise and public APIs.

```python
@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    backoff_factor: float = 1.5

```

Rate limiting configuration provides production-ready API throttling. Burst limits and backoff factors prevent API abuse while ensuring responsive operation.

```python
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

```

API input validation ensures comprehensive parameter checking with appropriate constraints. Timeout and retry limits prevent resource exhaustion while enabling robust operation.

```python
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
```

Advanced API tool provides enterprise-grade API integration capabilities. Comprehensive feature set supports production requirements including authentication, rate limiting, and caching.

```python    
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
```

Tool initialization establishes authentication, rate limiting state, caching infrastructure, and performance tracking. Comprehensive metrics enable operational monitoring and optimization.

```python    
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
```

Synchronous wrapper enables async API execution within synchronous LangChain tool interface. Asyncio.run provides proper event loop management for async HTTP operations.

```python    
    async def _execute_api_request(self, endpoint: str, method: str,
                                 headers: Optional[Dict[str, str]],
                                 params: Optional[Dict[str, Any]],
                                 data: Optional[Dict[str, Any]],
                                 timeout: int, retry_attempts: int,
                                 cache_duration: int) -> str:
        """Execute API request with comprehensive error handling"""
        
        request_start_time = time.time()
        self.performance_metrics["total_requests"] += 1
```

Async request execution begins with performance tracking and request counting. Timing starts immediately to capture complete request lifecycle including rate limiting and caching.

```python        
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
```

Rate limiting and cache checking optimize API usage before expensive network operations. Cache hits dramatically improve response times while rate limiting prevents API abuse.

```python            
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
```

HTTP request execution uses aiohttp for async performance with proper authentication headers. Session management and timeout configuration ensure robust network operations.

```python                            
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
```

Successful response processing captures comprehensive response metadata including timing and headers. Structured result format enables consistent response handling.

```python                                
                                # Cache successful responses
                                self._cache_response(cache_key, json.dumps(result), cache_duration)
                                
                                # Update performance metrics
                                self._update_response_time_metric(time.time() - request_start_time)
                                
                                return json.dumps(result, indent=2)
```

Response caching and metrics updates complete successful request processing. Cache storage enables future request optimization while metrics support performance monitoring.

```python                            
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
```

Rate limit handling respects API-provided retry-after headers with automatic backoff. Retry logic ensures graceful handling of temporary API capacity limitations.

```python                            
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
```

Server error handling implements exponential backoff with configurable retry attempts. Persistent server errors are reported with comprehensive error context.

```python                            
                            else:  # Client errors - don't retry
                                return json.dumps({
                                    "error": "Client error",
                                    "status_code": response.status,
                                    "response": response_text
                                })
```

Client error handling avoids unnecessary retries for 4xx responses. Clear error reporting helps diagnose request formatting and authentication issues.

```python                
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
```

Network exception handling provides retry logic for transient connectivity issues. Timeout and client errors are retried with appropriate backoff strategies.

```python        
        except Exception as e:
            self.performance_metrics["failed_requests"] += 1
            return json.dumps({
                "error": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__
            })
```

Global exception handling captures unexpected errors with comprehensive error reporting. Failed request tracking enables monitoring and debugging of tool reliability.

```python    
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
```

Authentication header preparation supports multiple authentication types with flexible configuration. API key, bearer token, basic auth, JWT, and OAuth2 patterns enable comprehensive API integration.

```python        
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
```

Comprehensive authentication methods handle enterprise authentication patterns. Basic auth encoding, JWT generation, and OAuth2 token management support diverse API requirements.

```python    
    async def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        
        current_time = time.time()
        
        # Clean old requests from history
        cutoff_time = current_time - 60  # Last minute
        self.request_history = [
            req_time for req_time in self.request_history 
            if req_time > cutoff_time
        ]
```

Rate limit checking maintains sliding window of request history. Historical request cleanup ensures accurate rate limiting without memory bloat.

```python        
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
```

Multi-level rate limiting prevents both sustained and burst API abuse. Per-minute and burst limits provide comprehensive API protection with proper request history tracking.

```python    
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
```

Cache key generation creates unique identifiers from request parameters. Deterministic key creation enables effective caching while MD5 hashing provides consistent key formatting.

```python    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if still valid"""
        
        if cache_key in self.response_cache:
            cached_data, cache_time = self.response_cache[cache_key]
            if time.time() - cache_time < 300:  # 5 minute default cache
                return cached_data
            else:
                del self.response_cache[cache_key]
        
        return None
```

Cache retrieval validates entry freshness before returning cached responses. Expired entries are automatically removed to maintain cache accuracy and prevent stale data issues.

```python    
    def _cache_response(self, cache_key: str, response: str, duration: int):
        """Cache response for specified duration"""
        
        self.response_cache[cache_key] = (response, time.time())
        
        # Clean old cache entries periodically
        if len(self.response_cache) % 100 == 0:
            self._cleanup_cache()
```

Response caching with periodic cleanup prevents memory bloat. Modulo-based cleanup triggering balances cache maintenance with performance overhead.

```python    
    def _cleanup_cache(self):
        """Remove expired cache entries"""
        
        current_time = time.time()
        expired_keys = [
            key for key, (_, cache_time) in self.response_cache.items()
            if current_time - cache_time > 3600  # 1 hour max cache
        ]
        
        for key in expired_keys:
            del self.response_cache[key]
```

Cache cleanup removes entries older than one hour to prevent indefinite memory growth. Batch cleanup operation maintains cache efficiency while preserving recent entries.

```python    
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

Performance metrics provide comprehensive API tool analytics including success rates, response times, cache effectiveness, and rate limiting statistics for operational monitoring and optimization.

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
```

Database integration imports provide async drivers for multiple database systems. Comprehensive type hints and logging support enterprise database connectivity patterns.

```python
class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
```

Database type enumeration supports major database systems. SQLite, PostgreSQL, MySQL, and MongoDB coverage enables comprehensive enterprise database integration.

```python
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

```

Database configuration provides comprehensive connection parameters with validation constraints. Pool sizing, timeouts, and SSL configuration support enterprise database requirements.

```python
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
```

Database query input model provides comprehensive query specification with safety validation. Operation type classification and parameter support enable secure database interactions.

```python    
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
```

Query validation includes basic SQL injection protection by detecting dangerous operations without WHERE clauses. Security-first validation prevents accidental data loss or unauthorized access.

```python
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
```

Advanced database tool provides enterprise-grade database integration with comprehensive feature set. Connection pooling, transactions, caching, and monitoring support production requirements.

```python    
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
```

Tool initialization establishes connection pool, transaction tracking, query caching, and performance monitoring infrastructure. Async connection pool initialization ensures readiness for database operations.

```python    
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
```

PostgreSQL connection pool configuration includes comprehensive parameters for host, port, credentials, pool sizing, and timeout settings. Default port handling simplifies configuration.

```python            
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
```

Multi-database support includes MySQL and SQLite configurations. SQLite bypasses connection pooling due to its file-based nature while maintaining consistent interface.

```python            
            self.logger.info(f"Database connection pool initialized for {self.db_config.db_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise e
```

Connection pool initialization provides error handling and logging for debugging connection issues. Exception propagation ensures initialization failures are properly handled.

```python    
    def _run(self, query: str, parameters: Optional[List[Any]] = None,
             operation_type: str = "select", fetch_size: Optional[int] = None,
             timeout: int = 60, transaction_id: Optional[str] = None) -> str:
        """Execute database operation"""
        
        return asyncio.run(
            self._execute_database_operation(
                query, parameters, operation_type, fetch_size, timeout, transaction_id
            )
        )
```

Synchronous database operation wrapper enables async execution within LangChain tool interface. Asyncio.run provides proper event loop management for database operations.

```python    
    async def _execute_database_operation(self, query: str, parameters: Optional[List[Any]],
                                        operation_type: str, fetch_size: Optional[int],
                                        timeout: int, transaction_id: Optional[str]) -> str:
        """Execute database operation with comprehensive handling"""
        
        query_start_time = datetime.now()
        self.performance_metrics["total_queries"] += 1
```

Database operation execution begins with performance tracking and timing. Query start time and counter enable comprehensive performance monitoring and analysis.

```python        
        try:
            # Check cache for SELECT queries
            if operation_type == "select":
                cache_key = self._generate_query_cache_key(query, parameters)
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    self.performance_metrics["cache_hits"] += 1
                    return cached_result
```

Query caching optimizes SELECT operations by avoiding redundant database queries. Cache hits dramatically improve response times for repeated queries.

```python            
            # Handle transaction operations
            if transaction_id:
                return await self._execute_in_transaction(
                    query, parameters, operation_type, fetch_size, timeout, transaction_id
                )
```

Transaction routing enables multi-query operations with ACID compliance. Transaction ID identifies related queries for proper state management and rollback capabilities.

```python            
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
```

Database-specific execution routing enables optimized drivers for PostgreSQL, MySQL, and SQLite. Each database type utilizes specialized connection and query patterns.

```python            
            # Cache SELECT results
            if operation_type == "select":
                cache_key = self._generate_query_cache_key(query, parameters)
                self._cache_result(cache_key, result)
            
            # Update performance metrics
            execution_time = (datetime.now() - query_start_time).total_seconds()
            self._update_query_metrics(execution_time, True)
            
            self.performance_metrics["successful_queries"] += 1
            
            return result
```

Query result caching and performance tracking complete successful operations. Cache storage improves subsequent query performance while metrics enable operational monitoring.

```python            
        except Exception as e:
            self.logger.error(f"Database operation failed: {str(e)}")
            self.performance_metrics["failed_queries"] += 1
            
            return json.dumps({
                "error": str(e),
                "error_type": type(e).__name__,
                "query": query[:100] + "..." if len(query) > 100 else query,
                "operation_type": operation_type
            })
```

Error handling provides comprehensive failure information including error type, truncated query, and operation context. Logging and metrics updates enable failure analysis and monitoring.

```python    
    async def _execute_postgresql_query(self, query: str, parameters: Optional[List[Any]],
                                      operation_type: str, fetch_size: Optional[int],
                                      timeout: int) -> str:
        """Execute PostgreSQL query"""
        
        async with self.connection_pool.acquire() as connection:
            self.performance_metrics["active_connections"] += 1
```

PostgreSQL query execution utilizes connection pool for resource management. Active connection tracking enables pool monitoring and resource optimization.

```python            
            try:
                if operation_type == "select":
                    if parameters:
                        rows = await connection.fetch(query, *parameters)
                    else:
                        rows = await connection.fetch(query)
                    
                    # Apply fetch size limit
                    if fetch_size and len(rows) > fetch_size:
                        rows = rows[:fetch_size]
```

SELECT operation handling supports parameterized queries for security. Fetch size limiting prevents memory exhaustion from large result sets.

```python                    
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
```

Result formatting converts PostgreSQL records to JSON-serializable dictionaries. Structured response includes metadata about rows returned and truncation status.

```python                
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
```

Modification operations (INSERT, UPDATE, DELETE) use execute for proper transaction handling. Result extraction provides affected row counts for operation verification.

```python
            finally:
                self.performance_metrics["active_connections"] -= 1
```

Connection cleanup ensures proper resource management. Connection counter tracking enables pool monitoring and prevents resource leaks.

### SQLite Query Execution

SQLite query execution provides lightweight database operations with automatic connection management and comprehensive result formatting.

```python
    async def _execute_sqlite_query(self, query: str, parameters: Optional[List[Any]],
                                   operation_type: str, fetch_size: Optional[int],
                                   timeout: int) -> str:
        """Execute SQLite query with connection management and result formatting"""
        
        async with aiosqlite.connect(self.db_config.database) as connection:
            self.performance_metrics["active_connections"] += 1
```

SQLite connection establishment uses aiosqlite for async operations. Connection tracking provides performance visibility into database resource usage.

```python
            try:
                cursor = await connection.cursor()
                
                if parameters:
                    await cursor.execute(query, parameters)
                else:
                    await cursor.execute(query)
```

Query execution supports parameterized queries for SQL injection prevention. Cursor creation enables result processing and metadata extraction.

```python
                if operation_type == "select":
                    rows = await cursor.fetchall()
                    
                    # Get column names for structured results
                    column_names = [description[0] for description in cursor.description]
                    
                    # Apply fetch size limit for memory management
                    if fetch_size and len(rows) > fetch_size:
                        rows = rows[:fetch_size]
```

SELECT operations retrieve complete result sets with column metadata. Fetch size limiting prevents memory exhaustion from large datasets while preserving column structure.

```python
                    # Convert to JSON format with column mapping
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
```

Result formatting creates structured JSON responses with column names mapped to values. Truncation indicators help identify when results exceed fetch limits.

```python
                else:
                    # Handle modification operations (INSERT, UPDATE, DELETE)
                    await connection.commit()
                    rows_affected = cursor.rowcount
                    
                    return json.dumps({
                        "status": "success",
                        "operation": operation_type,
                        "rows_affected": rows_affected
                    }, indent=2)
```

Modification operations include automatic commit for data persistence. Row count tracking provides feedback on operation impact and success verification.

```python
            finally:
                self.performance_metrics["active_connections"] -= 1
```

Resource cleanup maintains accurate connection tracking. Finally blocks ensure counter updates regardless of execution success or failure.

### Transaction Management System

Database transaction management provides ACID compliance with support for multi-query operations, rollback capabilities, and comprehensive transaction lifecycle tracking.

```python
    async def begin_transaction(self, transaction_id: str) -> str:
        """Begin a new database transaction with lifecycle management"""
        
        if transaction_id in self.active_transactions:
            return json.dumps({"error": f"Transaction {transaction_id} already exists"})
```

Transaction uniqueness validation prevents duplicate transaction IDs. Active transaction tracking enables proper resource management and state consistency.

```python
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
```

PostgreSQL transaction initialization uses connection pooling for resource efficiency. Transaction object creation enables proper rollback and commit operations with timing tracking.

```python
            elif self.db_config.db_type == DatabaseType.SQLITE:
                connection = await aiosqlite.connect(self.db_config.database)
                await connection.execute("BEGIN TRANSACTION")
                
                self.active_transactions[transaction_id] = {
                    "connection": connection,
                    "start_time": datetime.now()
                }
```

SQLite transaction management uses direct SQL commands for transaction control. Connection storage enables query execution within transaction scope.

```python
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
```

Transaction creation includes metric tracking and comprehensive error handling. Success responses provide confirmation while error responses include diagnostic information.

### Transaction Commit Operations

Transaction commit operations finalize database changes with proper resource cleanup and comprehensive duration tracking for performance analysis.

```python
    async def commit_transaction(self, transaction_id: str) -> str:
        """Commit a database transaction with resource cleanup"""
        
        if transaction_id not in self.active_transactions:
            return json.dumps({"error": f"Transaction {transaction_id} not found"})
```

Transaction existence validation ensures commit operations only proceed for active transactions. Error responses provide clear feedback for invalid transaction IDs.

```python
        try:
            transaction_data = self.active_transactions[transaction_id]
            
            if self.db_config.db_type == DatabaseType.POSTGRESQL:
                await transaction_data["transaction"].commit()
                await self.connection_pool.release(transaction_data["connection"])
```

PostgreSQL commit operations use transaction objects for proper ACID compliance. Connection pool release ensures resource availability for subsequent operations.

```python
            elif self.db_config.db_type == DatabaseType.SQLITE:
                await transaction_data["connection"].commit()
                await transaction_data["connection"].close()
```

SQLite commit operations apply changes directly to the database file. Connection closure prevents resource leaks and ensures proper cleanup.

```python
            # Calculate transaction duration for performance monitoring
            duration = (datetime.now() - transaction_data["start_time"]).total_seconds()
            
            # Clean up transaction tracking
            del self.active_transactions[transaction_id]
            
            return json.dumps({
                "status": "success",
                "transaction_id": transaction_id,
                "duration_seconds": duration,
                "message": "Transaction committed successfully"
            })
```

Duration calculation provides performance insights for transaction optimization. Transaction cleanup removes tracking data and returns comprehensive success information.

```python
        except Exception as e:
            # Attempt rollback on commit failure for data integrity
            await self.rollback_transaction(transaction_id)
            
            return json.dumps({
                "error": f"Failed to commit transaction: {str(e)}",
                "transaction_id": transaction_id,
                "action": "Transaction rolled back"
            })
```

Commit failure handling includes automatic rollback to prevent partial commits. Error responses indicate both the failure and the corrective action taken.

### Transaction Rollback Operations

Transaction rollback operations provide comprehensive cleanup and resource management for failed transactions or explicit rollback requests.

```python
    async def rollback_transaction(self, transaction_id: str) -> str:
        """Rollback a database transaction with comprehensive cleanup"""
        
        if transaction_id not in self.active_transactions:
            return json.dumps({"error": f"Transaction {transaction_id} not found"})
```

Rollback validation ensures only active transactions can be rolled back. Clear error messages help diagnose transaction state issues.

```python
        try:
            transaction_data = self.active_transactions[transaction_id]
            
            if self.db_config.db_type == DatabaseType.POSTGRESQL:
                await transaction_data["transaction"].rollback()
                await self.connection_pool.release(transaction_data["connection"])
```

PostgreSQL rollback uses transaction objects for proper state restoration. Connection pool release ensures resources are returned for reuse.

```python
            elif self.db_config.db_type == DatabaseType.SQLITE:
                await transaction_data["connection"].rollback()
                await transaction_data["connection"].close()
```

SQLite rollback operations restore database to pre-transaction state. Connection closure completes transaction cleanup and resource management.

```python
            # Clean up transaction tracking
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
```

Rollback completion includes transaction cleanup and success confirmation. Exception handling provides diagnostic information for rollback failures.

### Database Performance Metrics

Comprehensive database performance metrics provide operational insights for monitoring, optimization, and capacity planning.

```python
    def get_database_metrics(self) -> Dict[str, Any]:
        """Get comprehensive database performance metrics"""
        
        total_queries = self.performance_metrics["total_queries"]
        success_rate = (
            self.performance_metrics["successful_queries"] / total_queries * 100
            if total_queries > 0 else 0
        )
```

Basic metrics calculation provides success rate analysis. Division by zero protection ensures reliable metrics regardless of query volume.

```python
        cache_hit_rate = (
            self.performance_metrics["cache_hits"] / total_queries * 100
            if total_queries > 0 else 0
        )
```

Cache performance metrics measure caching effectiveness. Hit rate calculation helps optimize cache policies and identify performance improvements.

```python
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

Comprehensive metrics dictionary provides complete operational visibility. Rounded percentages and timing values enhance readability while preserving precision.

---

## 📝 Multiple Choice Test - Module C

Test your understanding of custom tool development:

**Question 1:** What benefits do Pydantic models provide for LangChain tool development?

A) Faster execution only  
B) Type safety, automatic validation, and documentation generation  
C) Reduced memory usage  
D) Simplified deployment  

**Question 2:** What configuration options are set in the `AdvancedToolInput` Config class?

A) Only field validation  
B) Extra fields forbidden, validate on assignment, use enum values  
C) Just type checking  
D) Only serialization settings  

**Question 3:** What does the `@validator('filters')` decorator ensure?

A) Filters are not empty  
B) Filters contain JSON-serializable values  
C) Filters are unique  
D) Filters are properly formatted  

**Question 4:** What performance metrics are tracked in the `AdvancedDataAnalysisTool`?

A) Only execution time  
B) Total analyses, average execution time, success rate, and cache hit rate  
C) Just error counts  
D) Only cache statistics  

**Question 5:** What is the purpose of the `args_schema` attribute in the tool class?

A) Define tool name only  
B) Enable automatic validation and documentation generation  
C) Set execution timeout  
D) Configure caching behavior  

[**View Test Solutions →**](Session2_ModuleC_Test_Solutions.md)

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