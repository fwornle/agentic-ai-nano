# Session 5: PydanticAI Type-Safe Agents - Building Reliable Data Processing Systems

Imagine your ML training pipeline silently consuming corrupted data because an AI agent returned malformed feature vectors. Or discovering that your real-time recommendation system has been serving inconsistent user profiles for weeks, causing a 15% drop in click-through rates. These are the silent killers of data engineering systems - unpredictable AI responses that cascade through your entire data processing infrastructure.

PydanticAI eliminates these risks entirely by bringing production-grade type safety and validation to data processing agent development. Unlike traditional frameworks that work with unpredictable text responses, PydanticAI guarantees your agents return exactly the data schemas you define, with automatic validation and clear error messages - or they fail fast with detailed diagnostics.

In this session, you'll learn to build AI agents that are as reliable and predictable as the rest of your distributed data processing infrastructure, ensuring data quality and consistency across petabyte-scale systems.

## Overview

PydanticAI brings production-grade type safety and validation to AI agent development, solving one of the biggest challenges in deploying AI systems within data processing pipelines. Unlike traditional frameworks that work with unstructured text, PydanticAI guarantees your agents return exactly the data structures you define, with automatic validation and clear error messages.

### Key Benefits for Data Engineers

- **Schema Enforcement**: Guaranteed response structure prevents downstream data corruption - catch schema violations during development, not in production ETL pipelines
- **Data Validation**: Automatic field validation with detailed error messages for data quality assurance - know exactly what went wrong and where in your data flow
- **Type Safety**: Leverages familiar Python patterns and type hints - integrate seamlessly with existing data processing frameworks like Pandas, Spark, and Kafka
- **Infrastructure Agnostic**: Works with OpenAI, Anthropic, Gemini, and other providers - not locked into any single vendor for your data processing needs

You'll build type-safe agents with structured data outputs, validated tools with guaranteed schemas for data pipeline integration, production-ready error handling for distributed systems, and deployable FastAPI applications for microservice architectures.

---

## Type Safety Architecture - The Foundation of Reliable Data Processing

PydanticAI brings compile-time type safety to AI development through structured data models and automatic validation, solving the fundamental problem of unpredictable AI responses that can corrupt data processing workflows across distributed systems.

![PydanticAI](images/pydantic-ai.png)

Let's start with the essential imports - the building blocks for type-safe data processing systems:

```python
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
```

### Three Pillars of Data Pipeline Safety

These principles transform chaotic AI responses into reliable, predictable data outputs that maintain integrity across distributed processing systems:

1. **Structured Schema Models**: Define exact data shapes - like database schemas that enforce consistency across petabyte-scale processing
2. **Field-Level Validation**: Ensure data integrity at the field level - catch data quality issues before they propagate through your data pipelines
3. **Type Contracts**: Compile-time error prevention - fail fast during development, not when your streaming pipeline is processing millions of events

### Data Schema Definition

Pydantic models act as data contracts that specify exactly what your data should look like. This prevents bugs from schema mismatches, wrong types, or invalid values - the kinds of subtle errors that cause production outages in distributed data systems.

First, we define enums for controlled values - eliminating the possibility of invalid categorical data:

```python
class DataQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"
```

Next, we create structured models with validation - defining exactly what valid data looks like for ML feature processing:

```python
class FeatureExtractionRequest(BaseModel):
    dataset_id: str = Field(..., min_length=1, max_length=100)
    feature_description: str = Field(..., min_length=5)
    quality_threshold: DataQuality = Field(default=DataQuality.MEDIUM)
    completion_date: Optional[str] = Field(None, regex=r'\d{4}-\d{2}-\d{2}')
```

Now we can create validated instances - data that's guaranteed to be correct or the system fails fast:

```python
feature_request = FeatureExtractionRequest(
    dataset_id="user_behavior_events_2024",
    feature_description="Extract click-through features for recommendation model",
    quality_threshold=DataQuality.HIGH,
    completion_date="2025-01-01"
)
```

### Validation Benefits in Data Processing

Type safety prevents common data corruption issues by catching schema violations early - the difference between debugging during development versus firefighting production data pipeline failures. Compare these approaches:

Without validation - prone to silent data corruption and runtime errors:

```python
def process_features_unsafe(data):
    if data.get('quality_threshold') == 'critical':  # Typo! Should be 'high'
        apply_strict_validation(data)
    return data
```

With type safety - prevents schema violations and guarantees data structure:

```python
def process_features_safe(request: FeatureExtractionRequest):
    if request.quality_threshold == DataQuality.HIGH:  # Type-safe, no schema violations possible
        apply_strict_validation(request)
    return request
```

Validation catches data quality issues immediately - no more mysterious pipeline failures:

```python
try:
    bad_request = FeatureExtractionRequest(
        dataset_id="",  # Empty dataset ID
        feature_description="Short",  # Too short
        quality_threshold="critical"  # Invalid enum value
    )
except ValidationError as e:
    print(f"Schema validation failed: {e}")
```

---

## Agent Creation & Structure - Guaranteed Data Outputs Every Time

Moving from unpredictable text responses to structured, validated data outputs that integrate seamlessly with your existing data processing infrastructure and ML pipelines.

### Basic Agent Setup for Data Processing

PydanticAI agents guarantee response structure, solving the fundamental challenge of AI unpredictability in data engineering workflows. When you specify a `result_type`, the agent always returns data in that exact format or raises a validation error - no more parsing inconsistent responses in your data pipelines.

First, define the response structure - your data contract for ML feature engineering results:

```python
class FeatureExtractionResponse(BaseModel):
    extraction_id: str
    status: str
    estimated_completion: str
    feature_pipeline_steps: List[str]
```

Create the type-safe agent - guaranteed to return structured data or fail with clear diagnostics:

```python
feature_extraction_agent = Agent(
    'openai:gpt-4',
    result_type=FeatureExtractionResponse,
    system_prompt='You are a data pipeline feature extraction assistant.'
)
```

Use the agent with guaranteed structure - no more parsing text or handling malformed responses in your ETL jobs:

```python
async def plan_feature_extraction(description: str) -> FeatureExtractionResponse:
    result = await feature_extraction_agent.run(f"Plan this feature extraction task: {description}")
    # Result is guaranteed to be FeatureExtractionResponse type
    return result
```

### Agent with Data Service Dependencies

Real data processing applications need access to data warehouses, cloud storage, streaming systems, and ML feature stores. PydanticAI provides dependency injection for clean, testable architecture that scales to production data processing needs.

Define your data service dependencies - encapsulating external data infrastructure access:

```python
class DataWarehouseDep:
    def __init__(self, warehouse_url: str):
        self.warehouse_url = warehouse_url
    
    def save_feature_job(self, job_data: dict) -> str:
        # Integration with Snowflake, BigQuery, Redshift, etc.
        return f"job_{hash(str(job_data)) % 100000}"
```

Create agent with dependency injection - clean separation of concerns for data processing:

```python
data_agent_with_warehouse = Agent(
    'openai:gpt-4',
    result_type=FeatureExtractionResponse,
    deps_type=DataWarehouseDep
)

@data_agent_with_warehouse.system_prompt
def system_prompt(ctx: RunContext[DataWarehouseDep]) -> str:
    return f"You are a data processing assistant. Warehouse: {ctx.deps.warehouse_url}"
```

Use with dependencies - accessing data services cleanly and testably:

```python
warehouse = DataWarehouseDep("snowflake://data-warehouse.company.com")
result = await data_agent_with_warehouse.run(
    "Create an ETL pipeline for customer segmentation features",
    deps=warehouse
)
```

### Custom Data Validation

Beyond basic types, you can add data processing validation - ensuring outputs meet your specific data quality requirements. Pydantic validators implement complex rules that reflect real-world data constraints and ML pipeline requirements.

```python
from pydantic import validator, root_validator

class ValidatedFeatureExtractionResponse(BaseModel):
    extraction_id: str
    status: str = Field(..., regex=r'^(queued|processing|completed|failed)$')
    estimated_hours: int = Field(..., ge=1, le=168)  # 1 hour to 1 week
    complexity: str = Field(..., regex=r'^(simple|moderate|complex)$')
```

Add custom validation logic - data processing rules that ensure data quality:

```python
    @validator('extraction_id')
    def validate_extraction_id(cls, v):
        if not v.startswith('feat_'):
            raise ValueError('Feature extraction ID must start with "feat_"')
        return v
```

Add cross-field validation - ensuring relationships between fields make data processing sense:

```python
    @root_validator
    def validate_complexity_hours(cls, values):
        complexity = values.get('complexity')
        hours = values.get('estimated_hours')
        
        if complexity == 'simple' and hours > 24:
            raise ValueError('Simple feature extraction should not exceed 24 hours')
        elif complexity == 'complex' and hours < 48:
            raise ValueError('Complex feature extraction should require at least 48 hours')
        
        return values
```

Create agent with enhanced validation - data processing logic baked into the data structures:

```python
validated_feature_agent = Agent(
    'openai:gpt-4',
    result_type=ValidatedFeatureExtractionResponse
)
```

### Error Handling Patterns for Data Pipelines

Production data systems need robust error handling that distinguishes between validation failures and system errors - essential for debugging and monitoring distributed data processing.

```python
from pydantic import ValidationError

async def safe_data_agent_execution(agent, query: str):
    """Execute data agent with comprehensive error handling"""
    try:
        result = await agent.run(query)
        return {"success": True, "data": result}
    
    except ValidationError as e:
        return {
            "success": False,
            "error": "data_validation_failed",
            "details": e.errors()
        }
```

Handle other error types - comprehensive error classification for better monitoring:

```python
    except Exception as e:
        return {
            "success": False,
            "error": "execution_failed", 
            "details": str(e)
        }
```

Use with proper error checking - reliable error handling that enables debugging:

```python
result = await safe_data_agent_execution(
    validated_feature_agent, 
    "Plan a complex real-time streaming feature pipeline"
)

if result["success"]:
    job_data = result["data"]
    print(f"Feature extraction job created: {job_data.extraction_id}")
else:
    print(f"Error: {result['error']}")
```

---

## Tool Integration & Validation - Reliable Data System Interactions

Moving beyond unreliable tool calls to guaranteed, validated interactions with external data systems, cloud services, and ML platforms.

### Type-Safe Tool Creation for Data Services

Type-safe tools define exact input and output schemas, eliminating bugs from malformed data and enabling reliable integrations with data processing systems.

Define tool schemas - contracts for data system interactions:

```python
from pydantic_ai import Tool

class DataQueryInput(BaseModel):
    sql_query: str = Field(..., min_length=10)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    format: str = Field(default="json", regex=r'^(json|csv|parquet)$')

class DataQueryOutput(BaseModel):
    row_count: int
    columns: List[str]
    execution_time: float
    result_preview: str
```

Create the type-safe tool - guaranteed input validation and output structure:

```python
def create_data_query_tool() -> Tool:
    async def execute_query(input_data: DataQueryInput) -> DataQueryOutput:
        try:
            # Integration with data warehouse (Snowflake, BigQuery, Redshift)
            import time
            start_time = time.time()
            
            # Mock execution - in production, use actual database drivers
            time.sleep(0.1)  # Simulate query execution time
            execution_time = time.time() - start_time
            
            return DataQueryOutput(
                row_count=1000000,  # Typical data scale
                columns=["user_id", "event_type", "timestamp", "feature_value"],
                execution_time=execution_time,
                result_preview="user_id,event_type,timestamp,feature_value\n123,click,2024-01-01,0.85"
            )
        except Exception as e:
            raise ValueError(f"Data warehouse query failed: {e}")
    
    return Tool(execute_query, takes=DataQueryInput, returns=DataQueryOutput)
```

Register with agent - type-safe tool integration:

```python
query_tool = create_data_query_tool()
data_analyst_agent = Agent(
    'openai:gpt-4',
    tools=[query_tool]
)
```

### Data Pipeline Integration Tools

Type-safe tools validate both API inputs and responses, catching mismatches immediately and preventing silent failures in production data systems.

Define API tool schemas - contracts for external data service integration:

```python
import httpx
from typing import Optional

class DataPipelineStatusInput(BaseModel):
    pipeline_id: str = Field(..., min_length=1)
    include_metrics: bool = Field(default=True)

class DataPipelineStatusOutput(BaseModel):
    pipeline_id: str
    status: str
    records_processed: int
    throughput_per_second: Optional[float] = None
    error_rate: Optional[float] = None
```

Create the pipeline status API tool - validated external service interaction:

```python
async def create_pipeline_status_tool() -> Tool:
    async def get_pipeline_status(input_data: DataPipelineStatusInput) -> DataPipelineStatusOutput:
        async with httpx.AsyncClient() as client:
            # Integration with Kafka, Argo Workflows, or similar data orchestration systems
            return DataPipelineStatusOutput(
                pipeline_id=input_data.pipeline_id,
                status="running",
                records_processed=15000000,  # Typical data volume
                throughput_per_second=2500.5,
                error_rate=0.001
            )
    
    return Tool(get_pipeline_status, takes=DataPipelineStatusInput, returns=DataPipelineStatusOutput)
```

Use in an agent - reliable external data service integration:

```python
pipeline_tool = await create_pipeline_status_tool()
pipeline_agent = Agent(
    'openai:gpt-4', 
    tools=[pipeline_tool],
    result_type=str
)

result = await pipeline_agent.run("What's the status of pipeline customer-events-etl?")
```

### Tool Composition for Data Analysis

Combine multiple tools for complex data queries with structured responses - building sophisticated data processing capabilities from validated components.

Define multi-tool response - comprehensive output structure for data analysis:

```python
class DataAnalysisResponse(BaseModel):
    summary: str
    queries_executed: List[str] = Field(default_factory=list)
    pipeline_status: Optional[DataPipelineStatusOutput] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    data_quality_score: float = Field(..., ge=0.0, le=1.0)
```

Create multi-tool agent - coordinated tool usage with structured outputs:

```python
data_analysis_agent = Agent(
    'openai:gpt-4',
    tools=[query_tool, pipeline_tool],
    result_type=DataAnalysisResponse,
    system_prompt="""
    You are a data analysis assistant with query execution and pipeline monitoring tools.
    Structure responses with required fields and confidence levels based on data quality.
    """
)
```

Use multiple tools - complex data analysis with validated results:

```python
result = await data_analysis_agent.run(
    "Analyze customer behavior trends and check the ETL pipeline status."
)
```

### Tool Error Recovery for Data Systems

Production data tools need graceful failure handling with retry logic and structured error responses - essential for reliable system operation in distributed data environments.

```python
import asyncio

class RobustDataTool:
    def __init__(self, tool_func, max_retries=3):
        self.tool_func = tool_func
        self.max_retries = max_retries
    
    async def execute(self, input_data, retry_count=0):
        try:
            return await self.tool_func(input_data)
        except Exception as e:
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.execute(input_data, retry_count + 1)
```

Handle final failure gracefully - structured error responses for data processing:

```python
            else:
                return {
                    "error": True,
                    "message": f"Data tool failed after {self.max_retries} retries: {e}",
                    "fallback_available": True,
                    "data_source": "cache"
                }
```

Wrap tools for reliability - production-ready error handling:

```python
robust_query_tool = RobustDataTool(query_tool)
```

---

## Testing & Deployment - Production-Ready Data Processing Systems

Moving from prototype to production with comprehensive testing and deployment strategies that ensure reliability at scale for data processing environments.

### Testing Patterns for Data Agents

Type-safe agents are easier to test because inputs and outputs are predictable - enabling comprehensive test coverage that catches regressions in data processing logic.

Test model validation - ensuring data contracts work correctly:

```python
import pytest
from unittest.mock import AsyncMock

def test_feature_extraction_request_validation():
    valid_request = FeatureExtractionRequest(
        dataset_id="user_behavior_analytics",
        feature_description="Process user click events for ML feature engineering",
        quality_threshold=DataQuality.HIGH
    )
    assert valid_request.dataset_id == "user_behavior_analytics"
```

Test validation failures - ensuring error handling works correctly:

```python
    with pytest.raises(ValidationError):
        FeatureExtractionRequest(
            dataset_id="",  # Too short
            feature_description="Short"  # Too short
        )
```

Test agent behavior with mocks - reliable testing without external data dependencies:

```python
@pytest.mark.asyncio
async def test_data_agent_response():
    mock_agent = AsyncMock()
    mock_agent.run.return_value = FeatureExtractionResponse(
        extraction_id="feat_123",
        status="queued",
        estimated_completion="4 hours",
        feature_pipeline_steps=["Ingestion", "Transformation", "Validation"]
    )
    
    result = await mock_agent.run("Test query")
    assert result.extraction_id == "feat_123"
    assert len(result.feature_pipeline_steps) == 3
```

### Configuration Management for Data Environments

Pydantic's BaseSettings manages different environments with automatic environment variable loading - essential for production deployment of data processing systems.

```python
from pydantic import BaseSettings

class DataAgentConfig(BaseSettings):
    model_name: str = "openai:gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.3  # Lower temperature for data processing consistency
    api_key: Optional[str] = None
    data_warehouse_url: str = "snowflake://localhost"
    
    class Config:
        env_prefix = "DATA_AGENT_"
        env_file = ".env"
```

Load configuration - environment-aware settings:

```python
config = DataAgentConfig()
```

Create agent with config - production-ready configuration management:

```python
production_data_agent = Agent(
    config.model_name,
    result_type=FeatureExtractionResponse,
    system_prompt="Production data processing assistant"
)
```

### Deployment with FastAPI for Data Services

FastAPI automatically handles request/response validation using Pydantic models - seamless integration that eliminates boilerplate and ensures consistency for data processing APIs.

```python
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

app = FastAPI()

@app.post("/extract-features", response_model=FeatureExtractionResponse)
async def extract_features(request: FeatureExtractionRequest):
    try:
        result = await feature_extraction_agent.run(
            f"Extract features from dataset: {request.dataset_id} - {request.feature_description}"
        )
        return result
```

Handle errors with proper HTTP status codes - production-ready error handling:

```python
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Add health check - monitoring and observability for data systems:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "data_services": "connected"}
```

---

## Quick Implementation Exercise

Build a data quality assessment agent to verify your understanding - applying all the concepts you've learned:

```python
class DataQualityRequest(BaseModel):
    dataset_name: str
    max_rows: int = Field(..., ge=1000, le=10000000)
    
class DataQualityReport(BaseModel):
    dataset_name: str
    total_rows: int
    missing_values_pct: float
    duplicate_rows_pct: float
    quality_score: float
    recommendations: List[str]

def create_data_quality_agent():
    # 1. Define your models (done above)
    # 2. Create agent with result_type
    # 3. Add system prompt for data quality analysis
    # 4. Test with data quality query
    pass
```

Test your implementation - ensuring everything works correctly:

```python
agent = create_data_quality_agent()
result = await agent.run("Assess quality of customer_events dataset with 5M rows")
```

### Self-Assessment

- [ ] I understand PydanticAI's type safety benefits for data processing
- [ ] I can create structured models with validation for data schemas
- [ ] I can build type-safe agents with data processing tools
- [ ] I understand testing and deployment basics for data systems

---

## Optional Deep Dive Modules

- **[Module A: Advanced Type Systems](Session5_ModuleA_Advanced_Type_Systems.md)** - Complex validation & streaming data
- **[Module B: Enterprise PydanticAI](Session5_ModuleB_Enterprise_PydanticAI.md)** - Production deployment & monitoring  
- **[Module C: Custom Validation Systems](Session5_ModuleC_Custom_Validation_Systems.md)** - Specialized validators & data quality middleware
- **[Module D: Testing & Benchmarking](Session5_ModuleD_Testing_Benchmarking.md)** - Comprehensive testing strategies for data systems

---

## 📝 Multiple Choice Test - Session 5

Test your understanding of PydanticAI type-safe agent development:

**Question 1:** What is the primary advantage of PydanticAI over traditional agent frameworks?  
A) Faster execution speed  
B) Lower computational cost  
C) Better user interface  
D) Automatic validation and structured outputs with compile-time type checking  

**Question 2:** Which validation constraint ensures a field value falls within a specific numeric range?  
A) Field(range=(0, 100))  
B) Field(between=0:100)  
C) Field(min=0, max=100)  
D) Field(ge=0, le=100)  

**Question 3:** What happens when PydanticAI model validation fails?  
A) Application crashes immediately  
B) Silent failure with default values  
C) Warning message is logged  
D) ValidationError is raised with detailed field information  

**Question 4:** How do you define a tool function for a PydanticAI agent?  
A) Using @tool decorator  
B) Using def tool() syntax  
C) Using @function decorator  
D) Using Tool class with takes and returns parameters  

**Question 5:** What is the purpose of RunContext in PydanticAI?  
A) Handles error messages  
B) Provides runtime configuration and dependencies  
C) Manages conversation history  
D) Controls execution speed  

[**🗂️ View Test Solutions →**](Session5_Test_Solutions.md)

## 🧭 Navigation

**Previous:** [Session 4 - CrewAI Team Orchestration](Session4_CrewAI_Team_Orchestration.md)

**Optional Deep Dive Modules:**

- 🔬 **[Module A: Advanced Type Systems](Session5_ModuleA_Advanced_Type_Systems.md)** - Complex validation & streaming data
- 🏭 **[Module B: Enterprise PydanticAI](Session5_ModuleB_Enterprise_PydanticAI.md)** - Production deployment & monitoring
- 🔧 **[Module C: Custom Validation Systems](Session5_ModuleC_Custom_Validation_Systems.md)** - Specialized validators & data quality middleware
- 🧪 **[Module D: Testing & Benchmarking](Session5_ModuleD_Testing_Benchmarking.md)** - Comprehensive testing strategies for data systems

**Next:** [Session 6 - Atomic Agents Modular Architecture →](Session6_Atomic_Agents_Modular_Architecture.md)

---
