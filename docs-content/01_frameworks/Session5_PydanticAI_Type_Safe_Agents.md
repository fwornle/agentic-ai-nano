# 🎯📝⚙️ Session 5: PydanticAI Type-Safe Agents Hub

## 🎯📝⚙️ Learning Path Overview

This session offers three distinct learning paths designed to match your goals and time investment:

=== "🎯 Observer (1-2 hours)"

    **Focus**: Understanding concepts and architecture
    
    **Activities**: Core type safety principles and basic PydanticAI usage
    
    **Ideal for**: Decision makers, architects, overview learners

=== "📝 Participant (3-4 hours)"

    **Focus**: Guided implementation and analysis
    
    **Activities**: Build production-ready type-safe agents with tools and validation
    
    **Ideal for**: Developers, technical leads, hands-on learners

=== "⚙️ Implementer (8-10 hours)"

    **Focus**: Complete implementation and customization
    
    **Activities**: Advanced type systems, enterprise patterns, custom validation systems
    
    **Ideal for**: Senior engineers, architects, specialists

# 🎯 Observer Path: Essential Type Safety Concepts

Imagine your ML training pipeline silently consuming corrupted data because an AI agent returned malformed feature vectors. PydanticAI eliminates these risks by bringing production-grade type safety to AI agent development.

## What is PydanticAI?

PydanticAI brings production-grade type safety and validation to AI agent development. Unlike traditional frameworks that work with unpredictable text responses, PydanticAI guarantees your agents return exactly the data schemas you define.

### Key Benefits

- **Schema Enforcement**: Guaranteed response structure prevents data corruption  
- **Data Validation**: Automatic field validation with clear error messages  
- **Type Safety**: Leverages familiar Python patterns and type hints  
- **Infrastructure Agnostic**: Works with OpenAI, Anthropic, Gemini, and other providers  

This Observer path covers essential concepts for understanding type-safe agent development fundamentals.

## Type Safety Architecture Fundamentals

PydanticAI brings compile-time type safety to AI development through structured data models and automatic validation.

![PydanticAI](images/pydantic-ai.png)

Essential imports for type-safe agents:

```python
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
```

### Three Core Principles

These principles transform unpredictable AI responses into reliable data:

1. **Structured Schema Models**: Define exact data shapes  
2. **Field-Level Validation**: Ensure data integrity at field level  
3. **Type Contracts**: Prevent errors during development  

### Basic Schema Definition

Pydantic models act as data contracts that specify exactly what your data should look like.

First, define enums for controlled values:

```python
class DataQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

Then create structured models with validation:

```python
class FeatureExtractionRequest(BaseModel):
    dataset_id: str = Field(..., min_length=1, max_length=100)
    feature_description: str = Field(..., min_length=5)
    quality_threshold: DataQuality = Field(default=DataQuality.MEDIUM)
    completion_date: Optional[str] = Field(None, regex=r'\d{4}-\d{2}-\d{2}')
```

Create validated instances:

```python
request = FeatureExtractionRequest(
    dataset_id="user_behavior_2024",
    feature_description="Extract features for ML model",
    quality_threshold=DataQuality.HIGH,
    completion_date="2025-01-01"
)
```

### Validation Benefits

Type safety prevents common data issues by catching schema violations early.

Without validation - prone to errors:

```python
def process_unsafe(data):
    if data.get('quality_threshold') == 'critical':  # Typo!
        apply_validation(data)
    return data
```

With type safety - prevents violations:

```python
def process_safe(request: FeatureExtractionRequest):
    if request.quality_threshold == DataQuality.HIGH:
        apply_validation(request)
    return request
```

Validation catches issues immediately:

```python
try:
    bad_request = FeatureExtractionRequest(
        dataset_id="",  # Too short
        feature_description="Short",  # Too short
        quality_threshold="invalid"  # Invalid enum
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Basic Agent Creation

PydanticAI agents guarantee response structure, eliminating unpredictable text responses.

Define the response structure:

```python
class FeatureExtractionResponse(BaseModel):
    extraction_id: str
    status: str
    estimated_completion: str
    feature_pipeline_steps: List[str]
```

Create the type-safe agent:

```python
feature_agent = Agent(
    'openai:gpt-4',
    result_type=FeatureExtractionResponse,
    system_prompt='You are a feature extraction assistant.'
)
```

Use the agent with guaranteed structure:

```python
async def plan_extraction(description: str) -> FeatureExtractionResponse:
    result = await feature_agent.run(
        f"Plan extraction task: {description}"
    )
    # Result is guaranteed to be FeatureExtractionResponse
    return result
```

### Agents with Dependencies

Real applications need external services. PydanticAI provides dependency injection for clean architecture.

Define service dependencies:

```python
class DataWarehouseDep:
    def __init__(self, warehouse_url: str):
        self.warehouse_url = warehouse_url

    def save_job(self, job_data: dict) -> str:
        # Integration with data warehouses
        return f"job_{hash(str(job_data)) % 100000}"
```

Create agent with dependencies:

```python
data_agent = Agent(
    'openai:gpt-4',
    result_type=FeatureExtractionResponse,
    deps_type=DataWarehouseDep
)

@data_agent.system_prompt
def system_prompt(ctx: RunContext[DataWarehouseDep]) -> str:
    return f"Data assistant. Warehouse: {ctx.deps.warehouse_url}"
```

Use with dependencies:

```python
warehouse = DataWarehouseDep("snowflake://company.com")
result = await data_agent.run(
    "Create ETL pipeline for customer features",
    deps=warehouse
)
```

### Custom Validation

Add custom validation rules for specific data quality requirements.

First, import validators and define the base model:

```python
from pydantic import validator, root_validator

class ValidatedResponse(BaseModel):
    extraction_id: str
    status: str = Field(..., regex=r'^(queued|processing|completed|failed)$')
    estimated_hours: int = Field(..., ge=1, le=168)
    complexity: str = Field(..., regex=r'^(simple|moderate|complex)$')
```

Add field-level validation for extraction IDs:

```python
    @validator('extraction_id')
    def validate_id(cls, v):
        if not v.startswith('feat_'):
            raise ValueError('ID must start with "feat_"')
        return v
```

Add cross-field validation to ensure logical consistency:

```python
    @root_validator
    def validate_complexity_hours(cls, values):
        complexity = values.get('complexity')
        hours = values.get('estimated_hours')

        if complexity == 'simple' and hours > 24:
            raise ValueError('Simple tasks should not exceed 24 hours')
        elif complexity == 'complex' and hours < 48:
            raise ValueError('Complex tasks need at least 48 hours')

        return values
```

Use enhanced validation:

```python
validated_agent = Agent(
    'openai:gpt-4',
    result_type=ValidatedResponse
)
```

### Error Handling

Handle validation errors gracefully in production systems.

Start with imports and basic structure:

```python
from pydantic import ValidationError

async def safe_agent_execution(agent, query: str):
    """Execute agent with error handling"""
    try:
        result = await agent.run(query)
        return {"success": True, "data": result}
```

Handle specific validation errors with detailed information:

```python
    except ValidationError as e:
        return {
            "success": False,
            "error": "validation_failed",
            "details": e.errors()
        }
```

Handle general errors with fallback response:

```python
    except Exception as e:
        return {
            "success": False,
            "error": "execution_failed",
            "details": str(e)
        }
```

Use with error checking:

```python
result = await safe_agent_execution(
    validated_agent,
    "Plan a complex feature pipeline"
)

if result["success"]:
    job_data = result["data"]
    print(f"Job created: {job_data.extraction_id}")
else:
    print(f"Error: {result['error']}")
```

## Basic Tool Integration

Type-safe tools define exact input and output schemas for reliable system interactions.

Define tool schemas:

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

Create the type-safe tool with proper structure:

```python
def create_query_tool() -> Tool:
    async def execute_query(input_data: DataQueryInput) -> DataQueryOutput:
        import time
        start_time = time.time()

        # Mock execution - use actual drivers in production
        time.sleep(0.1)
        execution_time = time.time() - start_time
```

This creates the basic tool structure and timing measurement.

```python
        return DataQueryOutput(
            row_count=1000000,
            columns=["user_id", "event_type", "timestamp"],
            execution_time=execution_time,
            result_preview="user_id,event_type,timestamp\n123,click,2024-01-01"
        )

    return Tool(execute_query, takes=DataQueryInput, returns=DataQueryOutput)
```

The return statement creates the validated output with proper schema compliance.

Register with agent:

```python
query_tool = create_query_tool()
analyst_agent = Agent(
    'openai:gpt-4',
    tools=[query_tool]
)
```

### API Integration Tools

Type-safe tools validate API inputs and responses, preventing silent failures.

Define API tool schemas:

```python
import httpx
from typing import Optional

class PipelineStatusInput(BaseModel):
    pipeline_id: str = Field(..., min_length=1)
    include_metrics: bool = Field(default=True)

class PipelineStatusOutput(BaseModel):
    pipeline_id: str
    status: str
    records_processed: int
    throughput_per_second: Optional[float] = None
    error_rate: Optional[float] = None
```

Create the API tool:

```python
async def create_status_tool() -> Tool:
    async def get_status(input_data: PipelineStatusInput) -> PipelineStatusOutput:
        # Mock API call - use actual API clients in production
        return PipelineStatusOutput(
            pipeline_id=input_data.pipeline_id,
            status="running",
            records_processed=15000000,
            throughput_per_second=2500.5,
            error_rate=0.001
        )

    return Tool(get_status, takes=PipelineStatusInput, returns=PipelineStatusOutput)
```

Use in agent:

```python
status_tool = await create_status_tool()
pipeline_agent = Agent(
    'openai:gpt-4',
    tools=[status_tool],
    result_type=str
)

result = await pipeline_agent.run("Status of pipeline customer-events?")
```

### Multi-Tool Composition

Combine multiple tools for complex queries with structured responses.

Define multi-tool response:

```python
class AnalysisResponse(BaseModel):
    summary: str
    queries_executed: List[str] = Field(default_factory=list)
    pipeline_status: Optional[PipelineStatusOutput] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    data_quality_score: float = Field(..., ge=0.0, le=1.0)
```

Create multi-tool agent:

```python
analysis_agent = Agent(
    'openai:gpt-4',
    tools=[query_tool, status_tool],
    result_type=AnalysisResponse,
    system_prompt="""
    Data analysis assistant with query and monitoring tools.
    Structure responses with confidence levels.
    """
)
```

Use multiple tools:

```python
result = await analysis_agent.run(
    "Analyze customer trends and check ETL status."
)
```

### Tool Error Recovery

Production tools need graceful failure handling with retry logic.

```python
import asyncio

class RobustTool:
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
            else:
                return {
                    "error": True,
                    "message": f"Tool failed after {self.max_retries} retries: {e}",
                    "fallback_available": True
                }
```

Wrap tools for reliability:

```python
robust_tool = RobustTool(query_tool)
```

## Testing Type-Safe Agents

Type-safe agents are easier to test because inputs and outputs are predictable.

Test model validation:

```python
import pytest
from unittest.mock import AsyncMock

def test_request_validation():
    valid_request = FeatureExtractionRequest(
        dataset_id="user_behavior",
        feature_description="Process user events for ML",
        quality_threshold=DataQuality.HIGH
    )
    assert valid_request.dataset_id == "user_behavior"

    with pytest.raises(ValidationError):
        FeatureExtractionRequest(
            dataset_id="",  # Too short
            feature_description="Short"  # Too short
        )
```

Test agent behavior with mocks:

```python
@pytest.mark.asyncio
async def test_agent_response():
    mock_agent = AsyncMock()
    mock_agent.run.return_value = FeatureExtractionResponse(
        extraction_id="feat_123",
        status="queued",
        estimated_completion="4 hours",
        feature_pipeline_steps=["Ingestion", "Transformation"]
    )

    result = await mock_agent.run("Test query")
    assert result.extraction_id == "feat_123"
    assert len(result.feature_pipeline_steps) == 2
```

## Configuration Management

Pydantic's BaseSettings manages environments with automatic variable loading.

```python
from pydantic import BaseSettings

class AgentConfig(BaseSettings):
    model_name: str = "openai:gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.3
    api_key: Optional[str] = None
    warehouse_url: str = "snowflake://localhost"

    class Config:
        env_prefix = "AGENT_"
        env_file = ".env"

config = AgentConfig()

production_agent = Agent(
    config.model_name,
    result_type=FeatureExtractionResponse,
    system_prompt="Production assistant"
)
```

## FastAPI Deployment

FastAPI automatically handles validation using Pydantic models.

Start with FastAPI setup and imports:

```python
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

app = FastAPI()
```

Create the main feature extraction endpoint:

```python
@app.post("/extract-features", response_model=FeatureExtractionResponse)
async def extract_features(request: FeatureExtractionRequest):
    try:
        result = await feature_agent.run(
            f"Extract from: {request.dataset_id} - {request.feature_description}"
        )
        return result
```

Handle errors with appropriate HTTP status codes:

```python
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Add health check endpoint:

```python
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}
```

## 🎯 Observer Path Practice

Build a simple data quality agent to verify your understanding:

Define the data quality models:

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
```

Create the quality assessment agent:

```python
def create_quality_agent():
    return Agent(
        'openai:gpt-4',
        result_type=DataQualityReport,
        system_prompt="You are a data quality assistant."
    )
```

Test the implementation:

```python
agent = create_quality_agent()
result = await agent.run("Assess customer_events dataset with 5M rows")
```

### 🎯 Observer Path Self-Assessment

- [ ] I understand PydanticAI's type safety benefits  
- [ ] I can create structured models with validation  
- [ ] I can build basic type-safe agents  
- [ ] I understand error handling basics  

## 📝 Continue Your Learning Journey

### 📝 Ready for hands-on implementation? Continue with:  
- 📝 [Practical Implementation](Session5_Practical_Implementation.md)  
- 📝 [Production Deployment](Session5_Production_Deployment.md)  

### ⚙️ Advanced: Implementer Path - Complete Mastery
For deep expertise, explore:  
- ⚙️ [Advanced Type Systems](Session5_ModuleA_Advanced_Type_Systems.md)  
- ⚙️ [Enterprise PydanticAI](Session5_ModuleB_Enterprise_PydanticAI.md)  
- ⚙️ [Custom Validation Systems](Session5_ModuleC_Custom_Validation_Systems.md)  
- ⚙️ [Testing & Benchmarking](Session5_ModuleD_Testing_Benchmarking.md)  

## 📝 Multiple Choice Test - Session 5

**Question 1:** What is the primary advantage of PydanticAI?  
A) Faster execution  
B) Lower cost  
C) Better UI  
D) Automatic validation and structured outputs  

**Question 2:** Which constraint ensures numeric range validation?  
A) Field(range=(0, 100))  
B) Field(between=0:100)  
C) Field(min=0, max=100)  
D) Field(ge=0, le=100)  

**Question 3:** What happens when validation fails?  
A) Application crashes  
B) Silent failure  
C) Warning logged  
D) ValidationError raised  

**Question 4:** How do you define tools?  
A) @tool decorator  
B) def tool() syntax  
C) @function decorator  
D) Tool class with takes/returns  

**Question 5:** What is RunContext for?  
A) Error handling  
B) Runtime configuration and dependencies  
C) Conversation history  
D) Speed control  

[View Solutions →](Session5_Test_Solutions.md)

---

## 🧭 Navigation

**Previous:** [Session 4 - Team Orchestration →](Session4_*.md)  
**Next:** [Session 6 - Modular Architecture →](Session6_*.md)

---
