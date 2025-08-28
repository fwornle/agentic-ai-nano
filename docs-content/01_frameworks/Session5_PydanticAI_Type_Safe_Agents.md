# Session 5: PydanticAI Type-Safe Agents - Building Bulletproof AI Systems

Imagine deploying an AI agent to production, only to discover it sometimes returns malformed data that crashes your billing system. Or worse, it occasionally returns the wrong data structure, causing silent failures that corrupt customer records. These are the kinds of production nightmares that keep CTOs awake at night.

PydanticAI eliminates these risks entirely by bringing production-grade type safety and validation to AI agent development. Unlike traditional frameworks that work with unpredictable text responses, PydanticAI guarantees your agents return exactly the data structures you define, with automatic validation and clear error messages - or they fail fast with detailed diagnostics.

In this session, you'll learn to build AI agents that are as reliable and predictable as the rest of your production infrastructure.

## Overview

PydanticAI brings production-grade type safety and validation to AI agent development, solving one of the biggest challenges in deploying AI systems at scale. Unlike traditional frameworks that work with unstructured text, PydanticAI guarantees your agents return exactly the data structures you define, with automatic validation and clear error messages.

### Key Benefits

- **Type Safety**: Guaranteed response structure with compile-time error prevention - catch bugs during development, not production
- **Validation**: Automatic data validation with detailed error messages - know exactly what went wrong and where
- **Python-First**: Leverages familiar Python patterns and standard library - no new paradigms to learn
- **Model Agnostic**: Works with OpenAI, Anthropic, Gemini, and other providers - not locked into any single vendor

You'll build type-safe agents with structured responses, validated tools with guaranteed schemas, production-ready error handling, and deployable FastAPI applications.

---

## Type Safety Architecture - The Foundation of Reliable AI

PydanticAI brings compile-time type safety to AI development through structured data models and automatic validation, solving the fundamental problem of unpredictable AI responses.

![PydanticAI](images/pydantic-ai.png)

Let's start with the essential imports - the building blocks for type-safe AI systems:

```python
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
```

### Three Pillars of Type Safety

These principles transform chaotic AI responses into reliable, predictable outputs:

1. **Structured Models**: Define exact data shapes - like blueprints that enforce consistency
2. **Validation Rules**: Ensure data integrity - catch problems before they propagate
3. **Type Hints**: Compile-time error prevention - fail fast during development, not production

### Basic Model Definition

Pydantic models act as contracts that specify exactly what your data should look like. This prevents bugs from typos, wrong types, or invalid values - the kinds of subtle errors that cause production outages.

First, we define enums for controlled values - eliminating the possibility of typos or invalid options:

```python
class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"
```

Next, we create structured models with validation - defining exactly what valid data looks like:

```python
class TaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=5)
    priority: Priority = Field(default=Priority.MEDIUM)
    due_date: Optional[str] = Field(None, regex=r'\d{4}-\d{2}-\d{2}')
```

Now we can create validated instances - data that's guaranteed to be correct or the system fails fast:

```python
task = TaskRequest(
    title="Learn PydanticAI",
    description="Complete the type-safe agent tutorial",
    priority=Priority.HIGH,
    due_date="2025-01-01"
)
```

### Validation Benefits

Type safety prevents common bugs by catching errors early - the difference between debugging in development versus firefighting in production. Compare these approaches:

Without validation - prone to silent failures and runtime errors:

```python
def process_task_unsafe(data):
    if data.get('priority') == 'urgent':  # Typo! Should be 'high'
        handle_urgent(data)
    return data
```

With type safety - prevents typos and guarantees structure:

```python
def process_task_safe(task: TaskRequest):
    if task.priority == Priority.HIGH:  # Type-safe, no typos possible
        handle_urgent(task)
    return task
```

Validation catches issues immediately - no more mysterious production failures:

```python
try:
    bad_task = TaskRequest(
        title="",  # Too short
        description="Short",  # Too short
        priority="urgent"  # Invalid enum value
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

---

## Agent Creation & Structure - Guaranteed Outputs Every Time

Moving from unpredictable text responses to structured, validated outputs that integrate seamlessly with your existing systems.

### Basic Agent Setup

PydanticAI agents guarantee response structure, solving the fundamental challenge of AI unpredictability. When you specify a `result_type`, the agent always returns data in that exact format or raises a validation error - no more guessing games.

First, define the response structure - your contract with the AI system:

```python
class TaskResponse(BaseModel):
    task_id: str
    status: str
    estimated_completion: str
    next_steps: List[str]
```

Create the type-safe agent - guaranteed to return structured data or fail with clear diagnostics:

```python
task_agent = Agent(
    'openai:gpt-4',
    result_type=TaskResponse,
    system_prompt='You are a task planning assistant.'
)
```

Use the agent with guaranteed structure - no more parsing text or handling malformed responses:

```python
async def plan_task(description: str) -> TaskResponse:
    result = await task_agent.run(f"Plan this task: {description}")
    # Result is guaranteed to be TaskResponse type
    return result
```

### Agent with Dependencies

Real applications need access to external services - databases, APIs, file systems. PydanticAI provides dependency injection for clean, testable architecture that scales to enterprise needs.

Define your dependencies - encapsulating external service access:

```python
class DatabaseDep:
    def __init__(self, db_url: str):
        self.db_url = db_url
    
    def save_task(self, task_data: dict) -> str:
        # Simplified database save
        return f"task_{hash(str(task_data)) % 100000}"
```

Create agent with dependency injection - clean separation of concerns:

```python
task_agent_with_db = Agent(
    'openai:gpt-4',
    result_type=TaskResponse,
    deps_type=DatabaseDep
)

@task_agent_with_db.system_prompt
def system_prompt(ctx: RunContext[DatabaseDep]) -> str:
    return f"You are a task assistant. Database: {ctx.deps.db_url}"
```

Use with dependencies - accessing external services cleanly and testably:

```python
db = DatabaseDep("postgresql://localhost:5432/tasks")
result = await task_agent_with_db.run(
    "Create a project plan",
    deps=db
)
```

### Custom Result Validation

Beyond basic types, you can add business logic validation - ensuring outputs meet your specific business requirements. Pydantic validators implement complex rules that reflect real-world constraints.

```python
from pydantic import validator, root_validator

class ValidatedTaskResponse(BaseModel):
    task_id: str
    status: str = Field(..., regex=r'^(pending|in_progress|completed)$')
    estimated_hours: int = Field(..., ge=1, le=100)
    complexity: str = Field(..., regex=r'^(simple|moderate|complex)$')
```

Add custom validation logic - business rules that ensure data quality:

```python
    @validator('task_id')
    def validate_task_id(cls, v):
        if not v.startswith('task_'):
            raise ValueError('Task ID must start with "task_"')
        return v
```

Add cross-field validation - ensuring relationships between fields make business sense:

```python
    @root_validator
    def validate_complexity_hours(cls, values):
        complexity = values.get('complexity')
        hours = values.get('estimated_hours')
        
        if complexity == 'simple' and hours > 8:
            raise ValueError('Simple tasks should not exceed 8 hours')
        elif complexity == 'complex' and hours < 16:
            raise ValueError('Complex tasks should require at least 16 hours')
        
        return values
```

Create agent with enhanced validation - business logic baked into the data structures:

```python
validated_agent = Agent(
    'openai:gpt-4',
    result_type=ValidatedTaskResponse
)
```

### Error Handling Patterns

Production systems need robust error handling that distinguishes between validation failures and system errors - essential for debugging and monitoring.

```python
from pydantic import ValidationError

async def safe_agent_execution(agent, query: str):
    """Execute agent with comprehensive error handling"""
    try:
        result = await agent.run(query)
        return {"success": True, "data": result}
    
    except ValidationError as e:
        return {
            "success": False,
            "error": "validation_failed",
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
result = await safe_agent_execution(
    validated_agent, 
    "Plan a complex software project"
)

if result["success"]:
    task_data = result["data"]
    print(f"Task created: {task_data.task_id}")
else:
    print(f"Error: {result['error']}")
```

---

## Tool Integration & Validation - Reliable External Interactions

Moving beyond unreliable tool calls to guaranteed, validated interactions with external systems.

### Type-Safe Tool Creation

Type-safe tools define exact input and output schemas, eliminating bugs from malformed data and enabling reliable integrations with external systems.

Define tool schemas - contracts for external system interactions:

```python
from pydantic_ai import Tool

class CalculateInput(BaseModel):
    expression: str = Field(..., regex=r'^[0-9+\-*/().\s]+$')
    precision: int = Field(default=2, ge=0, le=10)

class CalculateOutput(BaseModel):
    result: float
    expression: str
    formatted_result: str
```

Create the type-safe tool - guaranteed input validation and output structure:

```python
def create_calculator_tool() -> Tool:
    async def calculate(input_data: CalculateInput) -> CalculateOutput:
        try:
            # WARNING: eval() requires caution in production
            # Consider using ast.literal_eval() or a math library
            result = eval(input_data.expression)
            formatted = f"{result:.{input_data.precision}f}"
            
            return CalculateOutput(
                result=result,
                expression=input_data.expression,
                formatted_result=formatted
            )
        except Exception as e:
            raise ValueError(f"Invalid calculation: {e}")
    
    return Tool(calculate, takes=CalculateInput, returns=CalculateOutput)
```

Register with agent - type-safe tool integration:

```python
calc_tool = create_calculator_tool()
math_agent = Agent(
    'openai:gpt-4',
    tools=[calc_tool]
)
```

### API Integration Tools

Type-safe tools validate both API inputs and responses, catching mismatches immediately and preventing silent failures in production systems.

Define API tool schemas - contracts for external service integration:

```python
import httpx
from typing import Optional

class WeatherInput(BaseModel):
    location: str = Field(..., min_length=2)
    units: str = Field(default="celsius", regex=r'^(celsius|fahrenheit)$')

class WeatherOutput(BaseModel):
    location: str
    temperature: float
    condition: str
    humidity: Optional[int] = None
```

Create the weather API tool - validated external service interaction:

```python
async def create_weather_tool() -> Tool:
    async def get_weather(input_data: WeatherInput) -> WeatherOutput:
        async with httpx.AsyncClient() as client:
            # Mock API response for demo
            return WeatherOutput(
                location=input_data.location,
                temperature=22.5 if input_data.units == "celsius" else 72.5,
                condition="Sunny",
                humidity=65
            )
    
    return Tool(get_weather, takes=WeatherInput, returns=WeatherOutput)
```

Use in an agent - reliable external service integration:

```python
weather_tool = await create_weather_tool()
weather_agent = Agent(
    'openai:gpt-4', 
    tools=[weather_tool],
    result_type=str
)

result = await weather_agent.run("What's the weather in London?")
```

### Tool Composition

Combine multiple tools for complex queries with structured responses - building sophisticated capabilities from validated components.

Define multi-tool response - comprehensive output structure:

```python
class AgentResponse(BaseModel):
    answer: str
    calculations_used: List[str] = Field(default_factory=list)
    weather_data: Optional[WeatherOutput] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
```

Create multi-tool agent - coordinated tool usage with structured outputs:

```python
multi_tool_agent = Agent(
    'openai:gpt-4',
    tools=[calc_tool, weather_tool],
    result_type=AgentResponse,
    system_prompt="""
    You are a helpful assistant with calculation and weather tools.
    Structure responses with required fields and confidence levels.
    """
)
```

Use multiple tools - complex problem solving with validated results:

```python
result = await multi_tool_agent.run(
    "If it's 72°F in New York, what's that in Celsius? Also get weather."
)
```

### Tool Error Recovery

Production tools need graceful failure handling with retry logic and structured error responses - essential for reliable system operation.

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
```

Handle final failure gracefully - structured error responses:

```python
            else:
                return {
                    "error": True,
                    "message": f"Tool failed after {self.max_retries} retries: {e}",
                    "fallback_available": True
                }
```

Wrap tools for reliability - production-ready error handling:

```python
robust_calc = RobustTool(calc_tool)
```

---

## Testing & Deployment - Production-Ready AI Systems

Moving from prototype to production with comprehensive testing and deployment strategies that ensure reliability at scale.

### Testing Patterns

Type-safe agents are easier to test because inputs and outputs are predictable - enabling comprehensive test coverage that catches regressions.

Test model validation - ensuring data contracts work correctly:

```python
import pytest
from unittest.mock import AsyncMock

def test_task_request_validation():
    valid_task = TaskRequest(
        title="Test Task",
        description="This is a test task",
        priority=Priority.HIGH
    )
    assert valid_task.title == "Test Task"
```

Test validation failures - ensuring error handling works correctly:

```python
    with pytest.raises(ValidationError):
        TaskRequest(
            title="",  # Too short
            description="Short"  # Too short
        )
```

Test agent behavior with mocks - reliable testing without external dependencies:

```python
@pytest.mark.asyncio
async def test_agent_response():
    mock_agent = AsyncMock()
    mock_agent.run.return_value = TaskResponse(
        task_id="task_123",
        status="pending",
        estimated_completion="2 hours",
        next_steps=["Step 1", "Step 2"]
    )
    
    result = await mock_agent.run("Test query")
    assert result.task_id == "task_123"
    assert len(result.next_steps) == 2
```

### Configuration Management

Pydantic's BaseSettings manages different environments with automatic environment variable loading - essential for production deployment.

```python
from pydantic import BaseSettings

class AgentConfig(BaseSettings):
    model_name: str = "openai:gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.7
    api_key: Optional[str] = None
    
    class Config:
        env_prefix = "AGENT_"
        env_file = ".env"
```

Load configuration - environment-aware settings:

```python
config = AgentConfig()
```

Create agent with config - production-ready configuration management:

```python
production_agent = Agent(
    config.model_name,
    result_type=TaskResponse,
    system_prompt="Production task assistant"
)
```

### Deployment with FastAPI

FastAPI automatically handles request/response validation using Pydantic models - seamless integration that eliminates boilerplate and ensures consistency.

```python
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

app = FastAPI()

@app.post("/task", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    try:
        result = await task_agent.run(
            f"Create a task: {request.title} - {request.description}"
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

Add health check - monitoring and observability:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

---

## Quick Implementation Exercise

Build a book recommendation agent to verify your understanding - applying all the concepts you've learned:

```python
class BookRequest(BaseModel):
    genre: str
    max_pages: int = Field(..., ge=50, le=1000)
    
class BookRecommendation(BaseModel):
    title: str
    author: str
    pages: int
    summary: str

def create_book_agent():
    # 1. Define your models (done above)
    # 2. Create agent with result_type
    # 3. Add system prompt
    # 4. Test with query
    pass
```

Test your implementation - ensuring everything works correctly:

```python
agent = create_book_agent()
result = await agent.run("Recommend a sci-fi book under 300 pages")
```

### Self-Assessment

- [ ] I understand PydanticAI's type safety benefits
- [ ] I can create structured models with validation
- [ ] I can build type-safe agents with tools
- [ ] I understand testing and deployment basics

---

## Optional Deep Dive Modules

- **[Module A: Advanced Type Systems](Session5_ModuleA_Advanced_Type_Systems.md)** - Complex validation & streaming
- **[Module B: Enterprise PydanticAI](Session5_ModuleB_Enterprise_PydanticAI.md)** - Production deployment & monitoring  
- **[Module C: Custom Validation Systems](Session5_ModuleC_Custom_Validation_Systems.md)** - Specialized validators & middleware
- **[Module D: Testing & Benchmarking](Session5_ModuleD_Testing_Benchmarking.md)** - Comprehensive testing strategies

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

- 🔬 **[Module A: Advanced Type Systems](Session5_ModuleA_Advanced_Type_Systems.md)** - Complex validation & streaming
- 🏭 **[Module B: Enterprise PydanticAI](Session5_ModuleB_Enterprise_PydanticAI.md)** - Production deployment & monitoring
- 🔧 **[Module C: Custom Validation Systems](Session5_ModuleC_Custom_Validation_Systems.md)** - Specialized validators & middleware
- 🧪 **[Module D: Testing & Benchmarking](Session5_ModuleD_Testing_Benchmarking.md)** - Comprehensive testing strategies

**Next:** [Session 6 - Atomic Agents Modular Architecture →](Session6_Atomic_Agents_Modular_Architecture.md)

---
