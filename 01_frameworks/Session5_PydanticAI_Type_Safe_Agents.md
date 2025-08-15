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
- 🔬 **Module A: Advanced Type Systems** (60 min) - Complex validation & streaming
- 🏭 **Module B: Enterprise PydanticAI** (70 min) - Production deployment & monitoring
- 🔧 **Module C: Custom Validation Systems** (50 min) - Specialized validators & middleware
- 🧪 **Module D: Testing & Benchmarking** (40 min) - Comprehensive testing strategies

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

```python
from pydantic import BaseModel, Field
from enum import Enum

# Define enums for controlled values
class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"

# Create structured models
class TaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=5)
    priority: Priority = Field(default=Priority.MEDIUM)
    due_date: Optional[str] = Field(None, regex=r'\d{4}-\d{2}-\d{2}')

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

```python
# Without validation (prone to errors)
def process_task_unsafe(data):
    if data.get('priority') == 'urgent':  # Typo! Should be 'high'
        handle_urgent(data)
    return data

# With PydanticAI validation (catches errors early)
def process_task_safe(task: TaskRequest):
    if task.priority == Priority.HIGH:  # Type-safe, no typos possible
        handle_urgent(task)
    return task

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

```python
from pydantic_ai import Agent
from pydantic import BaseModel

# Define the response structure
class TaskResponse(BaseModel):
    task_id: str
    status: str
    estimated_completion: str
    next_steps: List[str]

# Create a type-safe agent
task_agent = Agent(
    'openai:gpt-4',
    result_type=TaskResponse,
    system_prompt='You are a task planning assistant.'
)

# Use the agent with guaranteed structure
async def plan_task(description: str) -> TaskResponse:
    result = await task_agent.run(f"Plan this task: {description}")
    # Result is guaranteed to be TaskResponse type
    return result
```

#### Agent with Dependencies (6 minutes)
Adding external services and context:

```python
# Define dependencies for the agent
class DatabaseDep:
    def __init__(self, db_url: str):
        self.db_url = db_url
    
    def save_task(self, task_data: dict) -> str:
        # Simplified database save
        return f"task_{''.join(str(hash(str(task_data)))[:8])}"

# Agent with dependency injection
task_agent_with_db = Agent(
    'openai:gpt-4',
    result_type=TaskResponse,
    deps_type=DatabaseDep
)

@task_agent_with_db.system_prompt
def system_prompt(ctx: RunContext[DatabaseDep]) -> str:
    return f"You are a task assistant. Database: {ctx.deps.db_url}"

# Usage with dependencies
db = DatabaseDep("postgresql://localhost:5432/tasks")
result = await task_agent_with_db.run(
    "Create a project plan",
    deps=db
)
```

#### Custom Result Validation (6 minutes)
Adding business logic validation:

```python
from pydantic import validator, root_validator

class ValidatedTaskResponse(BaseModel):
    task_id: str
    status: str = Field(..., regex=r'^(pending|in_progress|completed)$')
    estimated_hours: int = Field(..., ge=1, le=100)
    complexity: str = Field(..., regex=r'^(simple|moderate|complex)$')
    
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

# Agent with enhanced validation
validated_agent = Agent(
    'openai:gpt-4',
    result_type=ValidatedTaskResponse
)
```

#### Error Handling Patterns (5 minutes)
Managing validation failures gracefully:

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
    
    except Exception as e:
        # Handle other errors
        return {
            "success": False,
            "error": "execution_failed", 
            "details": str(e)
        }

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

# Create type-safe tool
def create_calculator_tool() -> Tool:
    async def calculate(input_data: CalculateInput) -> CalculateOutput:
        try:
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

# Register tool with agent
calc_tool = create_calculator_tool()
math_agent = Agent(
    'openai:gpt-4',
    tools=[calc_tool]
)
```

#### API Integration Tools (7 minutes)
Connecting to external services:

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

```python
# Create a multi-tool agent
class AgentResponse(BaseModel):
    answer: str
    calculations_used: List[str] = Field(default_factory=list)
    weather_data: Optional[WeatherOutput] = None
    confidence: float = Field(..., ge=0.0, le=1.0)

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

# Example query that might use multiple tools
result = await multi_tool_agent.run(
    "If it's 72°F in New York, what's that in Celsius? Also get current weather."
)
```

#### Tool Error Recovery (5 minutes)
Handling tool failures gracefully:

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
            else:
                # Return error response instead of raising
                return {
                    "error": True,
                    "message": f"Tool failed after {self.max_retries} retries: {e}",
                    "fallback_available": True
                }

# Wrap existing tools for reliability
robust_calc = RobustTool(calc_tool)
```

---

### Part 4: Testing & Deployment (15 minutes)
**Cognitive Load**: 3 new concepts
**Learning Mode**: Production Readiness

#### Basic Testing Patterns (6 minutes)
Testing type-safe agents:

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
    
    # Invalid request
    with pytest.raises(ValidationError):
        TaskRequest(
            title="",  # Too short
            description="Short"  # Too short
        )

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

# Load configuration
config = AgentConfig()

# Create agent with config
production_agent = Agent(
    config.model_name,
    result_type=TaskResponse,
    system_prompt="Production task assistant"
)
```

#### Basic Deployment (4 minutes)
Simple deployment patterns:

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
    
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
**Recommended**: Explore Module A or B for production usage

---

# 🎛️ OPTIONAL MODULES (Choose Your Adventure)

## 🔬 Module A: Advanced Type Systems (60 minutes)
**Prerequisites**: Core Section Complete
**Target Audience**: Developers seeking sophisticated validation
**Cognitive Load**: 6 advanced concepts

### A1: Complex Validation Patterns (25 minutes)
Advanced validators, custom field types, and sophisticated validation logic including cross-field validation and business rule enforcement.

### A2: Streaming Response Validation (20 minutes)
Real-time validation of streaming responses, partial result validation, and progressive data validation patterns.

### A3: Custom Validators & Middleware (15 minutes)
Building custom validation functions, middleware patterns for preprocessing/postprocessing, and validation optimization techniques.

[Detailed content moved from original Part 2: Advanced Validation]

---

## 🏭 Module B: Enterprise PydanticAI (70 minutes)
**Prerequisites**: Core Section Complete
**Target Audience**: Production system builders
**Cognitive Load**: 7 production concepts

### B1: Production Architecture Patterns (25 minutes)
Enterprise deployment patterns, multi-environment configuration, and production monitoring setup.

### B2: Scalability & Performance (25 minutes)
Performance optimization, caching strategies, connection pooling, and load balancing for PydanticAI applications.

### B3: Security & Compliance (20 minutes)
Security patterns, data privacy compliance, audit logging, and enterprise integration security.

[Detailed content moved from original Part 3: Production Patterns]

---

## 🔧 Module C: Custom Validation Systems (50 minutes)
**Prerequisites**: Core Section Complete
**Target Audience**: Developers building specialized systems
**Cognitive Load**: 5 specialized concepts

### C1: Domain-Specific Validators (20 minutes)
Creating validators for specific business domains, industry-specific validation rules, and regulatory compliance patterns.

### C2: Integration Testing Patterns (15 minutes)
Advanced testing strategies, mock management, integration test patterns, and validation testing frameworks.

### C3: Error Recovery Systems (15 minutes)
Sophisticated error handling, fallback patterns, partial result recovery, and resilient system design.

[Detailed content moved from original Part 4: Integration & Error Handling]

---

## 🧪 Module D: Testing & Benchmarking (40 minutes)
**Prerequisites**: Core Section Complete
**Target Audience**: Quality-focused developers
**Cognitive Load**: 4 testing concepts

### D1: Comprehensive Testing Strategies (20 minutes)
Advanced testing patterns, property-based testing, fuzzing, and validation testing methodologies.

### D2: Performance Benchmarking (15 minutes)
Performance measurement, benchmarking strategies, optimization identification, and performance regression testing.

### D3: Production Monitoring (5 minutes)
Monitoring setup, metrics collection, alerting patterns, and observability for PydanticAI systems.

[Detailed content moved from original Part 5: Performance Optimization]

---

## 🔄 LEARNING REINFORCEMENT

### Spaced Repetition Schedule
- **Day 1**: Complete core concepts ✅
- **Day 3**: Review validation patterns (15 min)
- **Week 1**: Build a small type-safe agent (30 min)
- **Week 2**: Implement production patterns (45 min)

### Cross-Session Integration
**Connections to Other Sessions:**
- **Session 2**: Compare with LangChain's approach to validation
- **Session 4**: CrewAI + PydanticAI for type-safe teams
- **Session 8**: Production deployment patterns

### Knowledge Application Projects
1. **Simple**: Build a validated data processing agent
2. **Intermediate**: Create a multi-tool agent with error handling
3. **Advanced**: Implement an enterprise agent with full monitoring

---

## 📊 Progress Tracking

### Completion Status
- [ ] Core Section (90 min) - Essential for next session
- [ ] Module A: Advanced Type Systems (60 min)
- [ ] Module B: Enterprise PydanticAI (70 min)  
- [ ] Module C: Custom Validation (50 min)
- [ ] Module D: Testing & Benchmarking (40 min)

### Time Investment Tracking
- **Minimum Path**: 90 minutes (Core only)
- **Recommended Path**: 160 minutes (Core + Module A)
- **Production Path**: 160 minutes (Core + Module B)
- **Comprehensive Path**: 310 minutes (Core + all modules)

### Next Steps
- **To Session 6**: Complete Core Section
- **For Production Use**: Add Module B
- **For Advanced Validation**: Add Module A
- **For Testing Excellence**: Add Module D

---

## 📝 Multiple Choice Test - Session 5 (15 minutes)

Test your understanding of PydanticAI type-safe agent development.

### Question 1
**What is the primary advantage of PydanticAI over traditional agent frameworks?**

A) Lower computational cost  
B) Automatic validation and structured outputs with compile-time type checking  
C) Better user interface  
D) Faster execution speed  

### Question 2
**Which validation constraint ensures a field value falls within a specific numeric range?**

A) Field(min=0, max=100)  
B) Field(ge=0, le=100)  
C) Field(range=(0, 100))  
D) Field(between=0:100)  

### Question 3
**What happens when PydanticAI model validation fails?**

A) Silent failure with default values  
B) ValidationError is raised with detailed field information  
C) Application crashes immediately  
D) Warning message is logged  

### Question 4
**How do you define a tool function for a PydanticAI agent?**

A) Using @tool decorator  
B) Using @agent.tool decorator  
C) Using @function decorator  
D) Using def tool() syntax  

### Question 5
**What is the purpose of RunContext in PydanticAI?**

A) Provides runtime configuration and dependencies  
B) Handles error messages  
C) Manages conversation history  
D) Controls execution speed  

### Question 6
**Which decorator enables cross-field validation in Pydantic models?**

A) @field_validator  
B) @root_validator  
C) @cross_validator  
D) @model_validator  

### Question 7
**How do you implement custom validation logic for complex business rules?**

A) Built-in validators only  
B) Custom validator methods with @field_validator or @root_validator  
C) External validation libraries  
D) Manual checks in application code  

### Question 8
**What is the main benefit of using structured outputs in PydanticAI?**

A) Better performance  
B) Guaranteed data format with automatic parsing and validation  
C) Lower resource usage  
D) Simpler code structure  

### Question 9
**How does PydanticAI handle type conversion and coercion?**

A) Manual conversion required  
B) Automatic type coercion with validation  
C) No type conversion supported  
D) Runtime type checking only  

### Question 10
**What makes PydanticAI particularly suitable for production applications?**

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

**🗂️ View Test Solutions**: Complete answers and explanations available in `Session5_Test_Solutions.md`

**Success Criteria**: Score 8+ out of 10 to demonstrate mastery of PydanticAI type safety.

---

[← Back to Session 4](Session4_CrewAI_Team_Orchestration.md) | [Next: Session 6 →](Session6_Atomic_Agents_Modular_Architecture.md)