# Session 2: LangChain Foundations & Tool Integration

## 🎯 Learning Navigation Hub
**Total Time Investment**: 85 minutes (Core) + 30-225 minutes (Optional)
**Your Learning Path**: Choose your engagement level

### Quick Start Guide
- **👀 Observer (45 min)**: Read core concepts + watch demonstrations  
- **🙋‍♂️ Participant (85 min)**: Follow guided exercises + implement examples
- **🛠️ Implementer (120 min)**: Build custom solutions + explore optional modules

---

## 📋 SESSION OVERVIEW DASHBOARD

### Core Learning Track (85 minutes) - REQUIRED
| Section | Concept Load | Time | Skills |
|---------|--------------|------|--------|
| 🏗️ Architecture Overview | 3 concepts | 20 min | Understanding |
| 🛠️ Essential Chain Patterns | 4 concepts | 25 min | Implementation |
| 🤖 Agent Creation & Tools | 4 concepts | 25 min | Application |
| 💾 Memory & State | 3 concepts | 15 min | Integration |

### Optional Deep Dive Modules (Choose Your Adventure)
- 🔬 **Module A: Advanced LangChain Patterns** (60 min) - Complex workflows & optimization
- 🏭 **Module B: Production Deployment Strategies** (70 min) - Enterprise deployment & monitoring  
- 🔧 **Module C: Custom Tool Development** (45 min) - Building specialized tools
- 📊 **Module D: Performance & Monitoring** (50 min) - Optimization & observability

**🗂️ Code Files**: All examples use files in `src/session2/`
**🚀 Quick Start**: Run `cd src/session2 && python langchain_basics.py` to see LangChain in action

---

## 🧭 CORE SECTION (Required - 85 minutes)

### Part 1: LangChain Architecture Overview (20 minutes)
**Cognitive Load**: 3 new concepts  
**Learning Mode**: Conceptual Understanding

#### Core Components (7 minutes)
LangChain has four essential building blocks that work together:

![LangChain Overview](images/langchain-overview.svg)

🗂️ **File**: `src/session2/langchain_basics.py` - Core setup and imports

```python
# Essential LangChain imports
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent  
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StdOutCallbackHandler
```

**The Four Pillars:**
1. **LLMs**: The "brain" that makes decisions
2. **Tools**: The "hands" that interact with the world  
3. **Memory**: The "context" that maintains state
4. **Agents**: The "orchestrator" that coordinates everything

#### LLM Setup Patterns (8 minutes)
Quick LLM initialization for different providers:

🗂️ **File**: `src/session2/llm_setup.py` - LLM factory pattern implementation

```python
# Simple LLM factory pattern
def create_llm(provider="openai"):
    if provider == "openai":
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
    elif provider == "anthropic":
        return ChatAnthropic(model="claude-3-sonnet")
    
# Usage
llm = create_llm("openai")
```

#### Component Relationships (5 minutes)
How components work together in the LangChain ecosystem:

```text
Input → Agent → Tool Selection → LLM Reasoning → Output
         ↑              ↓              ↑
      Memory ←→ Context Management ←→ State
```

---

### Part 2: Essential Chain Patterns (25 minutes)
**Cognitive Load**: 4 new concepts
**Learning Mode**: Hands-on Implementation

#### Simple Chain Creation (8 minutes)
Basic chain for sequential processing:

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Create a simple chain
template = "Analyze this text and provide insights: {text}"
prompt = PromptTemplate(template=template, input_variables=["text"])
chain = LLMChain(llm=llm, prompt=prompt)

# Use the chain
result = chain.run("AI agents are becoming more capable")
```

#### Sequential Chains (7 minutes)
Connecting multiple chains for complex workflows:

```python
from langchain.chains import SequentialChain

# Chain 1: Summarize
summary_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        template="Summarize: {text}",
        input_variables=["text"]
    ),
    output_key="summary"
)

# Chain 2: Analyze sentiment  
sentiment_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        template="Analyze sentiment of: {summary}",
        input_variables=["summary"]
    ),
    output_key="sentiment"
)

# Combine chains
full_chain = SequentialChain(
    chains=[summary_chain, sentiment_chain],
    input_variables=["text"],
    output_variables=["summary", "sentiment"]
)
```

#### Prompt Templates (5 minutes)
Dynamic prompt creation with variables:

```python
# Template with multiple variables
template = """
Role: {role}
Task: {task} 
Context: {context}
Format your response as: {format}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["role", "task", "context", "format"]
)

# Use with chain
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(
    role="Data Analyst",
    task="Analyze trends",
    context="Sales data from Q4",
    format="Bullet points"
)
```

#### Error Handling Patterns (5 minutes)
Basic error handling and retry logic:

```python
from langchain.callbacks import StdOutCallbackHandler
import time

def run_with_retry(chain, inputs, max_retries=3):
    for attempt in range(max_retries):
        try:
            return chain.run(inputs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
    
# Usage
try:
    result = run_with_retry(chain, {"text": "example input"})
except Exception as e:
    print(f"Chain failed after retries: {e}")
```

---

### Part 3: Agent Creation & Tool Integration (25 minutes)
**Cognitive Load**: 4 new concepts
**Learning Mode**: Application & Synthesis

#### Basic Tool Creation (8 minutes)
Three methods for creating tools:

🗂️ **File**: `src/session2/langchain_tools.py` - Complete tool implementations

```python
from langchain.agents import Tool
from langchain.tools import tool
import requests

# Method 1: Tool class
def get_weather(location: str) -> str:
    """Get current weather for a location"""
    # Simplified weather API call
    return f"Weather in {location}: Sunny, 72°F"

weather_tool = Tool(
    name="Weather",
    description="Get current weather for any location",
    func=get_weather
)

# Method 2: @tool decorator
@tool
def calculate_math(expression: str) -> str:
    """Calculate mathematical expressions safely"""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except:
        return "Invalid mathematical expression"

# Method 3: Quick function tool
def search_web(query: str) -> str:
    """Search the web for information"""
    return f"Search results for '{query}': Found 5 relevant articles"

search_tool = Tool(
    name="WebSearch", 
    description="Search web for information",
    func=search_web
)
```

#### Agent Initialization (7 minutes)
Creating agents with tools and memory:

```python
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

# Set up memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create tools list
tools = [weather_tool, calculate_math, search_tool]

# Initialize agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)
```

#### Tool Calling Patterns (5 minutes)
How agents decide when and how to use tools:

```python
# Agent automatically chooses tools based on input
response = agent.run("What's the weather in New York and calculate 15 * 24?")

# The agent will:
# 1. Analyze the request  
# 2. Identify need for weather_tool and calculate_math
# 3. Call tools in appropriate order
# 4. Synthesize results into coherent response
```

#### Basic Error Recovery (5 minutes)
Handling tool failures gracefully:

```python
def robust_tool_execution(agent, query, fallback_response=None):
    """Execute agent with fallback handling"""
    try:
        return agent.run(query)
    except Exception as e:
        print(f"Tool execution failed: {e}")
        if fallback_response:
            return fallback_response
        return "I encountered an error and couldn't complete the request."

# Usage with fallback
result = robust_tool_execution(
    agent, 
    "Complex query that might fail",
    fallback_response="Let me try a different approach..."
)
```

---

### Part 4: Memory & State Management (15 minutes)
**Cognitive Load**: 3 new concepts
**Learning Mode**: Integration & Application

#### Memory Types (5 minutes)
Different memory strategies for various use cases:

```python
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory
)

# Buffer memory - keeps all messages
buffer_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Summary memory - summarizes old conversations  
summary_memory = ConversationSummaryMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True
)

# Window memory - keeps last N messages
window_memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,  # Keep last 5 exchanges
    return_messages=True
)
```

#### State Persistence (5 minutes)
Saving and loading agent state:

```python
import json

def save_memory(memory, filename):
    """Save memory to file"""
    with open(filename, 'w') as f:
        json.dump(memory.chat_memory.messages, f, default=str)

def load_memory(memory, filename):
    """Load memory from file"""
    try:
        with open(filename, 'r') as f:
            messages = json.load(f)
            # Restore messages to memory
            for msg in messages:
                memory.chat_memory.add_message(msg)
    except FileNotFoundError:
        print("No previous memory file found")

# Usage
save_memory(memory, "agent_memory.json")
load_memory(memory, "agent_memory.json")
```

#### Context Management (5 minutes)
Managing context for better responses:

```python
# Context-aware agent setup
def create_context_aware_agent(context_info):
    """Create agent with specific context"""
    system_message = f"""
    You are a helpful assistant with the following context:
    {context_info}
    
    Always consider this context when responding.
    """
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        agent_kwargs={"system_message": system_message}
    )

# Create specialized agent
research_agent = create_context_aware_agent(
    "You are helping with academic research on AI agents"
)
```

---

## ✅ Core Section Validation (5 minutes)

### Quick Implementation Exercise
Build a simple LangChain agent to verify your understanding:

🗂️ **Exercise Files**: 
- `src/session2/langchain_basics.py` - Complete working examples
- `src/session2/langchain_tool_use.py` - Agent with tools implementation

```bash
# Try the examples:
cd src/session2
python langchain_basics.py        # Basic LangChain setup
python langchain_tool_use.py      # Agent with tools
```

```python
# Challenge: Create a basic agent with 2 tools
def create_simple_agent():
    # 1. Define your tools
    # 2. Set up memory
    # 3. Initialize agent
    # 4. Test with a query
    pass

# Test your implementation
agent = create_simple_agent()
result = agent.run("Help me with a simple task")
```

### Self-Assessment Checklist
- [ ] I understand the 4 core LangChain components
- [ ] I can create basic chains and prompt templates  
- [ ] I can build simple tools and agents
- [ ] I understand memory and state management
- [ ] I'm ready to explore optional modules or move to next session

**Next Session Prerequisites**: ✅ Core Section Complete
**Recommended**: Explore at least one Optional Module for deeper understanding

---

# 🎛️ OPTIONAL MODULES (Choose Your Adventure)

## 🔬 Module A: Advanced LangChain Patterns (60 minutes)
**Prerequisites**: Core Section Complete  
**Target Audience**: Implementers seeking deeper understanding
**Cognitive Load**: 6 advanced concepts

### A1: Complex Multi-Agent Workflows (20 minutes)
Advanced orchestration patterns with multiple specialized agents working together in sophisticated coordination patterns.

### A2: Custom Chain Development (20 minutes)  
Building custom chain classes, implementing advanced chain logic, and creating reusable chain components for enterprise applications.

### A3: Advanced Tool Patterns (20 minutes)
Creating sophisticated tools with state management, async operations, and error recovery mechanisms for production environments.

[Detailed content would be moved here from original session]

---

## 🏭 Module B: Production Deployment Strategies (70 minutes)
**Prerequisites**: Core Section Complete
**Target Audience**: Those building real systems
**Cognitive Load**: 7 production concepts

### B1: LangGraph Integration & Production Patterns (25 minutes)
Deep dive into LangGraph integration, production workflow patterns, and enterprise-scale orchestration strategies.

### B2: Performance Optimization & Monitoring (25 minutes)
Advanced performance tuning, caching strategies, monitoring setup, and observability for production LangChain applications.

### B3: Enterprise Deployment Architecture (20 minutes)
Container deployment, scaling patterns, load balancing, and production infrastructure for LangChain systems.

[Detailed content would be moved here from original session]

---

## 🔧 Module C: Custom Tool Development (45 minutes)
**Prerequisites**: Core Section Complete
**Target Audience**: Developers wanting customization
**Cognitive Load**: 5 specialized concepts

### C1: Advanced Tool Creation Patterns (15 minutes)
Sophisticated tool development using Pydantic models, structured inputs/outputs, and validation patterns.

### C2: API Integration Tools (15 minutes)
Building tools that integrate with external APIs, handling authentication, rate limiting, and error recovery.

### C3: Database & External System Integration (15 minutes)
Creating tools that interact with databases, file systems, and other external services with proper connection management.

[Detailed content would be moved here from original session]

---

## 📊 Module D: Performance & Monitoring (50 minutes)
**Prerequisites**: Core Section Complete  
**Target Audience**: Production-focused developers
**Cognitive Load**: 6 optimization concepts

### D1: Performance Benchmarking & Optimization (20 minutes)
Measuring LangChain performance, identifying bottlenecks, and implementing optimization strategies.

### D2: Advanced Monitoring & Observability (20 minutes)
Setting up comprehensive monitoring, logging, and observability for production LangChain applications.

### D3: Cost Optimization & Resource Management (10 minutes)
Managing API costs, token usage optimization, and resource allocation strategies.

[Detailed content would be moved here from original session]

---

## 🔄 LEARNING REINFORCEMENT

### Spaced Repetition Schedule
- **Day 1**: Complete core concepts ✅
- **Day 3**: Review key patterns (10 min quick review)  
- **Week 1**: Apply concepts in different context (15 min practice)
- **Week 2**: Teach-back exercise (20 min explanation to others)

### Cross-Session Integration  
**Connections to Other Sessions:**
- **Session 1**: Compare with bare-metal implementations
- **Session 3**: LangGraph patterns expand on concepts here
- **Session 5**: Type safety patterns complement LangChain usage

### Knowledge Application Projects
1. **Simple**: Build a basic QA agent with 2 tools
2. **Intermediate**: Create a multi-step research agent  
3. **Advanced**: Implement a customer service agent with memory

---

## 📊 Progress Tracking

### Completion Status
- [ ] Core Section (85 min) - Essential for next session
- [ ] Module A: Advanced Patterns (60 min)  
- [ ] Module B: Production Deployment (70 min)
- [ ] Module C: Custom Tools (45 min)
- [ ] Module D: Performance (50 min)

### Time Investment Tracking
- **Minimum Path**: 85 minutes (Core only)
- **Recommended Path**: 145 minutes (Core + 1 optional module)
- **Comprehensive Path**: 310 minutes (Core + all modules)

### Next Steps
- **To Session 3**: Complete Core Section
- **For Production Use**: Add Module B  
- **For Advanced Development**: Add Module A
- **For Custom Tools**: Add Module C

---

## 📝 Multiple Choice Test - Session 2 (15 minutes)

Test your understanding of LangChain foundations and agent patterns.

### Question 1
**What is the primary benefit of LangChain's unified LLM interface?**

A) Better performance  
B) Consistent API across different LLM providers  
C) Lower cost  
D) Faster response times  

### Question 2
**Which LangChain component is responsible for managing conversation context?**

A) Tools  
B) Agents  
C) Memory  
D) Chains  

### Question 3
**How many ways can you create tools in LangChain?**

A) One - inheriting from BaseTool  
B) Two - BaseTool and @tool decorator  
C) Three - BaseTool, @tool decorator, and StructuredTool  
D) Four - including custom implementations  

### Question 4
**What is the purpose of the `handle_parsing_errors` parameter in LangChain agents?**

A) To improve performance  
B) To gracefully handle malformed LLM responses  
C) To reduce costs  
D) To enable debugging  

### Question 5
**Which LangChain agent type is specifically designed for the ReAct pattern?**

A) STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION  
B) REACT_DOCSTORE  
C) ZERO_SHOT_REACT_DESCRIPTION  
D) All of the above  

### Question 6
**In the LangChain reflection implementation, what determines when the reflection loop stops?**

A) Fixed number of iterations  
B) When critique contains "SATISFACTORY"  
C) When response quality score exceeds threshold  
D) When no changes are detected  

### Question 7
**How does LangChain's built-in ReAct agent differ from the custom implementation?**

A) Built-in agent is faster  
B) Built-in agent has more abstraction, custom has more control  
C) Built-in agent is more accurate  
D) No significant difference  

### Question 8
**What is the main advantage of LangChain's Plan-and-Execute framework?**

A) Faster execution  
B) Better tool integration  
C) Separation of planning and execution phases  
D) Lower computational cost  

### Question 9
**In the multi-agent system, how do agents share context between workflow steps?**

A) Shared memory objects  
B) Previous step results are included in subsequent instructions  
C) Global state variables  
D) Database storage  

### Question 10
**What makes the conversation memory BufferWindowMemory different from ConversationBufferMemory?**

A) It's faster  
B) It only keeps the last K interactions  
C) It has better accuracy  
D) It works with more LLM providers  

---

### Practical Validation
Build a working agent that can:
- Use at least 2 tools
- Maintain conversation memory  
- Handle basic error scenarios
- Provide helpful responses

**🗂️ View Test Solutions**: Complete answers and explanations available in `Session2_Test_Solutions.md`

**Success Criteria**: Score 8+ out of 10 to demonstrate mastery of LangChain foundations.

---

[← Back to Session 1](Session1_Bare_Metal_Agents.md) | [Next: Session 3 →](Session3_LangGraph_Multi_Agent_Workflows.md)