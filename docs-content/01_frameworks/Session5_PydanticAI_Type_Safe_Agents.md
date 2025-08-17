# Session 5: PydanticAI Type-Safe Agents

## 🎯 Learning Navigation Hub
**Total Time Investment**: 90 minutes (Core) + 30-320 minutes (Optional)
**Your Learning Path**: Choose your engagement level

### Quick Start Guide

- **👀 Observer (50 min)**: Read core concepts + examine type safety examples
- **🙋‍♂️ Participant (90 min)**: Follow guided exercises + implement type-safe agents
- **🛠️ Implementer (150 min)**: Build production solutions + explore advanced patterns

---

## 📋 SESSION OVERVIEW DASHBOARD

### Core Learning Track (90 minutes) - REQUIRED
| Section | Concept Load | Time | Skills |
|---------|--------------|------|--------|
| 🏗️ Type Safety Fundamentals | 3 concepts | 25 min | Understanding |
| 🤖 Agent Creation & Structure | 4 concepts | 25 min | Implementation |
| 🛠️ Tool Integration & Validation | 4 concepts | 25 min | Application |
| 🚀 Testing & Deployment | 3 concepts | 15 min | Production |

### Optional Deep Dive Modules (Choose Your Adventure)

- 🔬 **[Module A: Advanced Type Systems](Session5_ModuleA_Advanced_Type_Systems.md)** (60 min) - Complex validation & streaming
- 🏭 **[Module B: Enterprise PydanticAI](Session5_ModuleB_Enterprise_PydanticAI.md)** (70 min) - Production deployment & monitoring
- 🔧 **[Module C: Custom Validation Systems](Session5_ModuleC_Custom_Validation_Systems.md)** (50 min) - Specialized validators & middleware
- 🧪 **[Module D: Testing & Benchmarking](Session5_ModuleD_Testing_Benchmarking.md)** (40 min) - Comprehensive testing strategies

**🗂️ Code Files**: All examples use files in `src/session5/`
**🚀 Quick Start**: Run `cd src/session5 && python pydantic_agents.py` to see PydanticAI in action

---

## 🧭 CORE SECTION (Required - 90 minutes)

### Part 1: Type Safety Fundamentals (25 minutes)
**Cognitive Load**: 3 new concepts
**Learning Mode**: Conceptual Understanding

#### Core PydanticAI Concepts (10 minutes)
PydanticAI brings type safety to AI agent development through structured validation:

![PydanticAI](images/pydantic-ai.png)

🗂️ **File**: `src/session5/pydantic_agents.py` - Core agent implementations and examples

```python
# Essential PydanticAI imports
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
```

**The Three Pillars of Type Safety:**

1. **Structured Models**: Define exact data shapes
2. **Validation Rules**: Ensure data integrity 
3. **Type Hints**: Compile-time error prevention

#### Basic Model Definition (8 minutes)
Create type-safe data structures:

Before we can build type-safe agents, we need to define the data structures they'll work with. Think of Pydantic models as contracts that specify exactly what data looks like and what values are acceptable. This prevents common bugs like typos in field names, wrong data types, or invalid values.

Enums are particularly powerful because they create a closed set of valid options - instead of remembering that priority can be "high", "medium", or "low", the IDE can autocomplete and the validator ensures only these values are accepted.

```python
from pydantic import BaseModel, Field
from enum import Enum

# Define enums for controlled values
class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"
```

Now we create structured models with field validation rules:

```python
# Create structured models
class TaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=5)
    priority: Priority = Field(default=Priority.MEDIUM)
    due_date: Optional[str] = Field(None, regex=r'\d{4}-\d{2}-\d{2}')
```

Finally, we demonstrate usage with automatic validation:

```python
# Usage - automatic validation
task = TaskRequest(
    title="Learn PydanticAI",
    description="Complete the type-safe agent tutorial",
    priority=Priority.HIGH,
    due_date="2025-01-01"
)
```

#### Validation Benefits (7 minutes)
Understanding why type safety matters:

The real power of type safety becomes apparent when you compare traditional "stringly-typed" code with validated approaches. Without validation, typos and incorrect values can cause silent failures that are hard to debug. With Pydantic validation, errors are caught immediately with clear messages about what went wrong.

Notice how the unsafe version uses string comparisons that can have typos, while the safe version uses enum values that are checked at runtime and provide IDE autocompletion.

```python
# Without validation (prone to errors)
def process_task_unsafe(data):
    if data.get('priority') == 'urgent':  # Typo! Should be 'high'
        handle_urgent(data)
    return data
```

Compare this with the type-safe approach that prevents typos:

```python
# With PydanticAI validation (catches errors early)
def process_task_safe(task: TaskRequest):
    if task.priority == Priority.HIGH:  # Type-safe, no typos possible
        handle_urgent(task)
    return task
```

Validation catches issues immediately with clear error messages:

```python
# Validation catches issues immediately
try:
    bad_task = TaskRequest(
        title="",  # Too short - will raise validation error
        description="Short",  # Too short - will raise validation error
        priority="urgent"  # Invalid - will suggest correct values
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

---

### Part 2: Agent Creation & Structure (25 minutes)
**Cognitive Load**: 4 new concepts
**Learning Mode**: Implementation & Practice

#### Basic Agent Setup (8 minutes)
Creating your first type-safe agent:

PydanticAI agents are different from other frameworks because they guarantee the structure of their responses. When you specify a `result_type`, the agent will always return data in that exact format, or raise a validation error if the LLM produces invalid output.

This is revolutionary for building reliable systems - instead of parsing free-form text responses and hoping they contain the right fields, you get strongly-typed objects that you can immediately use in your code with full confidence.

```python
from pydantic_ai import Agent
from pydantic import BaseModel

# Define the response structure
class TaskResponse(BaseModel):
    task_id: str
    status: str
    estimated_completion: str
    next_steps: List[str]
```

Next, we create the type-safe agent with guaranteed response structure:

```python
# Create a type-safe agent
task_agent = Agent(
    'openai:gpt-4',
    result_type=TaskResponse,
    system_prompt='You are a task planning assistant.'
)
```

Finally, we use the agent with guaranteed structured output:

```python
# Use the agent with guaranteed structure
async def plan_task(description: str) -> TaskResponse:
    result = await task_agent.run(f"Plan this task: {description}")
    # Result is guaranteed to be TaskResponse type
    return result
```

#### Agent with Dependencies (6 minutes)
Adding external services and context:

Real applications need access to external services like databases, APIs, or file systems. PydanticAI's dependency injection system lets you provide these services to agents in a clean, testable way. The agent can access dependencies through the `RunContext`, and you can easily swap implementations for testing.

The `@system_prompt` decorator allows dynamic prompt generation based on the available dependencies, making prompts context-aware and more effective.

```python
# Define dependencies for the agent
class DatabaseDep:
    def __init__(self, db_url: str):
        self.db_url = db_url
    
    def save_task(self, task_data: dict) -> str:
        # Simplified database save
        return f"task_{''.join(str(hash(str(task_data)))[:8])}"
```

Now we create an agent that uses dependency injection:

```python
# Agent with dependency injection
task_agent_with_db = Agent(
    'openai:gpt-4',
    result_type=TaskResponse,
    deps_type=DatabaseDep
)

@task_agent_with_db.system_prompt
def system_prompt(ctx: RunContext[DatabaseDep]) -> str:
    return f"You are a task assistant. Database: {ctx.deps.db_url}"
```

Finally, we demonstrate usage with dependencies:

```python
# Usage with dependencies
db = DatabaseDep("postgresql://localhost:5432/tasks")
result = await task_agent_with_db.run(
    "Create a project plan",
    deps=db
)
```

#### Custom Result Validation (6 minutes)
Adding business logic validation:

Beyond basic type checking, you often need business logic validation. Pydantic validators let you implement complex rules that reflect real-world constraints. Field validators check individual values, while root validators can examine relationships between multiple fields.

This example shows how to enforce business rules like "complex tasks must take at least 16 hours" - rules that prevent unrealistic planning and ensure data quality.

```python
from pydantic import validator, root_validator

class ValidatedTaskResponse(BaseModel):
    task_id: str
    status: str = Field(..., regex=r'^(pending|in_progress|completed)$')
    estimated_hours: int = Field(..., ge=1, le=100)
    complexity: str = Field(..., regex=r'^(simple|moderate|complex)$')
```

Now we add custom validation logic for business rules:

```python
    @validator('task_id')
    def validate_task_id(cls, v):
        if not v.startswith('task_'):
            raise ValueError('Task ID must start with "task_"')
        return v
    
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

Finally, we create an agent that uses this enhanced validation:

```python
# Agent with enhanced validation
validated_agent = Agent(
    'openai:gpt-4',
    result_type=ValidatedTaskResponse
)
```

#### Error Handling Patterns (5 minutes)
Managing validation failures gracefully:

In production systems, you need robust error handling that distinguishes between different failure types. Validation errors indicate the LLM produced invalid output (usually fixable with prompt improvements), while execution errors suggest system issues.

This pattern returns structured error information that helps with debugging and allows graceful degradation in user interfaces.

```python
from pydantic import ValidationError

async def safe_agent_execution(agent, query: str):
    """Execute agent with comprehensive error handling"""
    try:
        result = await agent.run(query)
        return {"success": True, "data": result}
    
    except ValidationError as e:
        # Handle validation errors
        return {
            "success": False,
            "error": "validation_failed",
            "details": e.errors()
        }
```

Handle other types of errors with fallback responses:

```python
    except Exception as e:
        # Handle other errors
        return {
            "success": False,
            "error": "execution_failed", 
            "details": str(e)
        }
```

Finally, demonstrate usage with proper error checking:

```python
# Usage
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

### Part 3: Tool Integration & Validation (25 minutes)
**Cognitive Load**: 4 new concepts
**Learning Mode**: Application & Integration

#### Type-Safe Tool Creation (8 minutes)
Building validated tools:

Type-safe tools are where PydanticAI really shines. Instead of tools that accept and return arbitrary data, you define exact input and output schemas. This eliminates entire classes of bugs - the tool can't receive malformed input, and it must return properly structured output.

The regex validation on the calculator input provides basic protection against code injection attacks, though in production you should use a proper math expression parser instead of `eval()`.

```python
from pydantic_ai import Tool
from pydantic import BaseModel, Field

# Define tool input/output schemas
class CalculateInput(BaseModel):
    expression: str = Field(..., regex=r'^[0-9+\-*/().\s]+$')
    precision: int = Field(default=2, ge=0, le=10)

class CalculateOutput(BaseModel):
    result: float
    expression: str
    formatted_result: str
```

Now we create the type-safe tool with validation:

```python
# Create type-safe tool
def create_calculator_tool() -> Tool:
    async def calculate(input_data: CalculateInput) -> CalculateOutput:
        try:
            # WARNING: Using eval() in production requires extreme caution
            # The regex validation above provides basic protection, but consider
            # using a proper math expression parser like ast.literal_eval()
            # or a dedicated math library for production use
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

Finally, register the tool with an agent:

```python
# Register tool with agent
calc_tool = create_calculator_tool()
math_agent = Agent(
    'openai:gpt-4',
    tools=[calc_tool]
)
```

#### API Integration Tools (7 minutes)
Connecting to external services:

Real applications need to integrate with external APIs. Type-safe tools make these integrations more reliable by validating both the input parameters and the API responses. Even if the external API changes its response format, your validation will catch the mismatch immediately rather than causing silent failures downstream.

This weather tool example shows how to structure API calls with proper input validation and response mapping.

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

Now we create the weather API integration tool:

```python
async def create_weather_tool() -> Tool:
    async def get_weather(input_data: WeatherInput) -> WeatherOutput:
        # Simplified weather API call
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

Finally, we use the tool in an agent:

```python
# Usage in agent
weather_tool = await create_weather_tool()
weather_agent = Agent(
    'openai:gpt-4', 
    tools=[weather_tool],
    result_type=str
)

result = await weather_agent.run("What's the weather in London?")
```

#### Tool Composition (5 minutes)
Combining multiple tools effectively:

The power of type-safe agents becomes apparent when combining multiple tools. The agent can use different tools as needed and return structured responses that combine information from multiple sources. The response model ensures all required fields are present and properly formatted.

Notice how the agent might use both calculation and weather tools to answer a complex query, returning structured data that includes confidence levels and metadata about which tools were used.

```python
# Create a multi-tool agent
class AgentResponse(BaseModel):
    answer: str
    calculations_used: List[str] = Field(default_factory=list)
    weather_data: Optional[WeatherOutput] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
```

Now we create an agent that can use multiple tools:

```python
multi_tool_agent = Agent(
    'openai:gpt-4',
    tools=[calc_tool, weather_tool],
    result_type=AgentResponse,
    system_prompt="""
    You are a helpful assistant with access to calculation and weather tools.
    Always structure your response with the required fields.
    Include confidence level based on tool reliability.
    """
)
```

Finally, we demonstrate a query that uses multiple tools:

```python
# Example query that might use multiple tools
result = await multi_tool_agent.run(
    "If it's 72°F in New York, what's that in Celsius? Also get current weather."
)
```

#### Tool Error Recovery (5 minutes)
Handling tool failures gracefully:

Production tools must handle failures gracefully. Network timeouts, API rate limits, and service outages are inevitable. This robust tool wrapper implements retry logic with exponential backoff and provides structured error responses instead of crashing.

By returning error objects instead of raising exceptions, the agent can continue processing and potentially use alternative tools or provide partial results.

```python
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

Handle final failure with structured error response:

```python
            else:
                # Return error response instead of raising
                return {
                    "error": True,
                    "message": f"Tool failed after {self.max_retries} retries: {e}",
                    "fallback_available": True
                }
```

Finally, wrap existing tools for reliability:

```python
# Wrap existing tools for reliability
robust_calc = RobustTool(calc_tool)
```

---

### Part 4: Testing & Deployment (15 minutes)
**Cognitive Load**: 3 new concepts
**Learning Mode**: Production Readiness

#### Basic Testing Patterns (6 minutes)
Testing type-safe agents:

Type-safe agents are easier to test because their inputs and outputs are predictable. You can test model validation separately from agent behavior, and use mocks to simulate agent responses without calling expensive LLM APIs.

The validation tests ensure your models reject invalid data, while the agent tests verify the overall behavior using mocked responses.

```python
import pytest
from unittest.mock import AsyncMock

# Test model validation
def test_task_request_validation():
    # Valid request
    valid_task = TaskRequest(
        title="Test Task",
        description="This is a test task",
        priority=Priority.HIGH
    )
    assert valid_task.title == "Test Task"
```

Test validation failures to ensure models reject invalid data:

```python
    # Invalid request
    with pytest.raises(ValidationError):
        TaskRequest(
            title="",  # Too short
            description="Short"  # Too short
        )
```

Test agent behavior using mocks to avoid LLM API calls:

```python
# Test agent behavior
@pytest.mark.asyncio
async def test_agent_response():
    # Mock the agent for testing
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

#### Configuration Management (5 minutes)
Managing different environments:

Pydantic's BaseSettings class provides powerful configuration management that automatically loads values from environment variables or configuration files. This makes it easy to deploy the same code across different environments (development, staging, production) with different settings.

The `env_prefix` feature helps organize environment variables, and the `env_file` support allows local development configuration.

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

Load configuration from environment variables or config files:

```python
# Load configuration
config = AgentConfig()
```

Finally, create an agent using the configuration:

```python
# Create agent with config
production_agent = Agent(
    config.model_name,
    result_type=TaskResponse,
    system_prompt="Production task assistant"
)
```

#### Basic Deployment (4 minutes)
Simple deployment patterns:

Deploying PydanticAI agents as web APIs is straightforward with FastAPI, which automatically handles request/response validation using your Pydantic models. The framework generates OpenAPI documentation automatically, and validation errors are handled gracefully with proper HTTP status codes.

This pattern provides a production-ready foundation that can be extended with authentication, rate limiting, and monitoring.

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

Handle validation and execution errors with proper HTTP status codes:

```python
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Add a health check endpoint for monitoring:

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

---

## ✅ Core Section Validation (5 minutes)

### Quick Implementation Exercise
Build a simple PydanticAI agent to verify understanding:

```python
# Challenge: Create a book recommendation agent
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

# Test your implementation
agent = create_book_agent()
result = await agent.run("Recommend a sci-fi book under 300 pages")
```

### Self-Assessment Checklist

- [ ] I understand PydanticAI's type safety benefits
- [ ] I can create structured models with validation
- [ ] I can build type-safe agents with tools
- [ ] I understand testing and deployment basics
- [ ] I'm ready to explore optional modules or move to next session

**Next Session Prerequisites**: ✅ Core Section Complete
**Recommended**: Explore optional modules for specialized knowledge


---

## 🎛️ OPTIONAL MODULES (Choose Your Adventure)

## 🔬 Module A: Advanced Type Systems (60 minutes)
**Prerequisites**: Core Section Complete  
**Target Audience**: Developers seeking sophisticated validation  
**Cognitive Load**: 6 advanced concepts

### Learning Objectives

- Build complex validation patterns with cross-field dependencies
- Implement custom field types and validators  
- Create middleware systems for validation optimization
- Handle streaming validation and real-time data validation
- Design enterprise-grade error handling systems

**[📖 Start Module A: Advanced Type Systems →](Session5_ModuleA_Advanced_Type_Systems.md)**

---

## 🏭 Module B: Enterprise PydanticAI (70 minutes)
**Prerequisites**: Core Section Complete  
**Target Audience**: Production system builders  
**Cognitive Load**: 7 production concepts

### Learning Objectives

- Implement dependency injection for clean architecture
- Build scalable agent systems with proper monitoring
- Deploy production-ready PydanticAI applications
- Create enterprise integration patterns
- Monitor and optimize agent performance

**[📖 Start Module B: Enterprise PydanticAI →](Session5_ModuleB_Enterprise_PydanticAI.md)**

---

## 🔧 Module C: Custom Validation Systems (50 minutes)
**Prerequisites**: Core Section Complete  
**Target Audience**: Developers building specialized systems  
**Cognitive Load**: 5 specialized concepts

### Learning Objectives

- Build sophisticated error management systems
- Implement intelligent retry strategies with circuit breakers
- Create domain-specific validation patterns
- Design resilient external service integrations
- Test error handling comprehensively

**[📖 Start Module C: Custom Validation Systems →](Session5_ModuleC_Custom_Validation_Systems.md)**

---

## 🧪 Module D: Testing & Benchmarking (40 minutes)
**Prerequisites**: Core Section Complete  
**Target Audience**: Quality assurance engineers and performance analysts  
**Cognitive Load**: 4 testing concepts

### Learning Objectives

- Build comprehensive testing frameworks for PydanticAI agents
- Implement performance monitoring and benchmarking systems
- Create enterprise-grade observability with distributed tracing
- Design intelligent caching and optimization patterns
- Monitor production systems with metrics and alerting

**[📖 Start Module D: Testing & Benchmarking →](Session5_ModuleD_Testing_Benchmarking.md)**



## 📝 Multiple Choice Test - Session 5 (15 minutes)

Test your understanding of PydanticAI type-safe agent development.

**Question 1:** What is the primary advantage of PydanticAI over traditional agent frameworks?  

A) Lower computational cost  
B) Automatic validation and structured outputs with compile-time type checking  
C) Better user interface  
D) Faster execution speed  

**Question 2:** Which validation constraint ensures a field value falls within a specific numeric range?  

A) Field(min=0, max=100)  
B) Field(ge=0, le=100)  
C) Field(range=(0, 100))  
D) Field(between=0:100)  

**Question 3:** What happens when PydanticAI model validation fails?  

A) Silent failure with default values  
B) ValidationError is raised with detailed field information  
C) Application crashes immediately  
D) Warning message is logged  

**Question 4:** How do you define a tool function for a PydanticAI agent?  

A) Using @tool decorator  
B) Using @agent.tool decorator  
C) Using @function decorator  
D) Using def tool() syntax  

**Question 5:** What is the purpose of RunContext in PydanticAI?  

A) Provides runtime configuration and dependencies  
B) Handles error messages  
C) Manages conversation history  
D) Controls execution speed  

**Question 6:** Which decorator enables cross-field validation in Pydantic models?  

A) @field_validator  
B) @root_validator  
C) @cross_validator  
D) @model_validator  

**Question 7:** How do you implement custom validation logic for complex business rules?  

A) Built-in validators only  
B) Custom validator methods with @field_validator or @root_validator  
C) External validation libraries  
D) Manual checks in application code  

**Question 8:** What is the main benefit of using structured outputs in PydanticAI?  

A) Better performance  
B) Guaranteed data format with automatic parsing and validation  
C) Lower resource usage  
D) Simpler code structure  

**Question 9:** How does PydanticAI handle type conversion and coercion?  

A) Manual conversion required  
B) Automatic type coercion with validation  
C) No type conversion supported  
D) Runtime type checking only  

**Question 10:** What makes PydanticAI particularly suitable for production applications?  

A) Built-in GUI components  
B) Strong type safety, validation, and error handling  
C) Automatic deployment features  
D) Built-in monitoring dashboards  

---

### Practical Validation

Build a working type-safe agent that:

- Uses structured input and output models
- Includes at least one tool with validation
- Handles validation errors gracefully
- Can be deployed with FastAPI

[**🗂️ View Test Solutions →**](Session5_Test_Solutions.md)

---

## 🧭 Navigation

**Previous:** [Session 4 - CrewAI Team Orchestration](Session4_CrewAI_Team_Orchestration.md)

**Optional Deep Dive Modules:**

- 🔬 **[Module A: Advanced Type Systems](Session5_ModuleA_Advanced_Type_Systems.md)** - Complex validation & streaming
- 🏭 **[Module B: Enterprise PydanticAI](Session5_ModuleB_Enterprise_PydanticAI.md)** - Production deployment & monitoring
- 🔧 **[Module C: Custom Validation Systems](Session5_ModuleC_Custom_Validation_Systems.md)** - Specialized validators & middleware
- 🧪 **[Module D: Testing & Benchmarking](Session5_ModuleD_Testing_Benchmarking.md)** - Comprehensive testing strategies

**Next:** [Session 6 - Atomic Agents Modular Architecture →](Session6_Atomic_Agents_Modular_Architecture.md)