# Session 2: LangChain Foundations - Mastering Production-Ready AI Application Development

## Learning Outcomes

By the end of this session, you will be able to:
- **Implement** LangChain's modular component system for production AI applications
- **Build** sophisticated chain orchestration patterns with tool integration
- **Apply** state management strategies for complex workflows
- **Evaluate** when LangChain excels versus when enterprise teams need alternatives
- **Deploy** LangChain applications with proper monitoring and performance optimization

## Chapter Overview: LangChain's 2025 Market Position

### Industry Context & Market Leadership

LangChain dominates the AI application framework space in 2025, powering 130K+ applications with 28 million monthly downloads and $25M Series A funding from Sequoia Capital. As the backbone of 60% of AI agent development workflows, LangChain processes millions of production requests across financial services, healthcare, and enterprise technology sectors.

### Enterprise Adoption & Production Challenges

99K GitHub stars and 250K+ LangSmith users demonstrate LangChain's market leadership, yet enterprise deployments reveal critical production challenges: 45.8% of teams cite performance quality concerns, while scalability limitations emerge in real-time and mission-critical workloads. Understanding these trade-offs enables strategic technology decisions.

### What Students Will Master & Business Impact

You'll master LangChain's production-proven architecture: modular component systems, chain orchestration patterns, intelligent tool integration, and state management strategies. More critically, you'll understand when LangChain excels (rapid prototyping, MVP development, educational systems) versus when enterprise teams migrate to specialized alternatives.

### Competitive Positioning vs 2025 Alternatives

LangChain pioneered modular AI development, establishing industry-standard concepts (chains, agents, memory) adopted across competing frameworks. While AutoGen provides structured multi-agent communication and CrewAI offers lean role-based workflows, LangChain's 600+ integrations and mature production tooling (LangServe, LangSmith) maintain its leadership for comprehensive AI application development.

### Production Applications & Strategic Considerations

Enterprise customers including Microsoft, Boston Consulting Group, and Morningstar leverage LangChain for customer support (35-45% resolution rate improvements), financial analysis, and document processing. However, teams targeting enterprise-scale, real-time systems often transition to specialized solutions after prototype validation.

## Learning Navigation Hub

**Total Time Investment**: 85 minutes (Core) + 225 minutes (Optional Advanced)

### Professional Learning Paths

- **Observer (45 min)**: Executive understanding - architecture analysis, market position, strategic decisions
- **Participant (85 min)**: Developer implementation - hands-on coding, production patterns, best practices  
- **Implementer (120 min)**: Technical leadership - advanced patterns, enterprise architecture, performance optimization

---

## Session Overview Dashboard

### Core Learning Track (85 minutes) - REQUIRED

| Section | Business Value | Time | Competency Level |
|---------|----------------|------|------------------|
| Architecture Foundation | Enterprise design patterns | 20 min | Strategic Understanding |
| Chain Implementation | Production workflow automation | 25 min | Technical Implementation |
| Agent & Tool Systems | Intelligent automation capabilities | 25 min | Applied Engineering |
| State & Memory Management | Scalable conversation systems | 15 min | System Integration |

### Optional Advanced Modules

**Enterprise Warning**: Advanced modules contain production deployment challenges and competitive framework analysis

- **[Module A: Advanced LangChain Patterns](Session2_ModuleA_Advanced_LangChain_Patterns.md)** (60 min) - Complex workflows & production limitations
- **[Module B: Production Deployment Strategies](Session2_ModuleB_Production_Deployment_Strategies.md)** (70 min) - Enterprise challenges & framework alternatives  
- **[Module C: Custom Tool Development](Session2_ModuleC_Custom_Tool_Development.md)** (45 min) - Production-grade specialized tools
- **[Module D: Performance & Monitoring](Session2_ModuleD_Performance_Monitoring.md)** (50 min) - Performance bottlenecks & optimization strategies

**Code Repository**: [`src/session2/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session2)
**Quick Validation**: `cd src/session2 && python langchain_basics.py`

---

## Core Section (Required - 85 minutes)

### Part 1: LangChain Architecture Overview (20 minutes)

**Cognitive Load**: 3 new concepts  
**Learning Mode**: Conceptual Understanding

#### Core Components (7 minutes)

LangChain has four essential building blocks that work together:

![LangChain Overview](images/langchain-overview.svg)

**Reference Implementation**: [`src/session2/langchain_basics.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session2/langchain_basics.py)

### LangChain Architecture Foundation - Production Setup

Installation and environment configuration for production-ready development:

```bash

# Production-grade installation with version pinning

pip install langchain==0.1.0 openai==1.0.0
export OPENAI_API_KEY="your-production-key"
```

### Essential Imports - Modular Component System

### Essential Import Structure

```python

# Core LangChain foundation imports

from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StdOutCallbackHandler
```

**Observer Path**: These four imports represent LangChain's core architecture - LLM interface, agent orchestration, memory management, and observability. Each serves a distinct purpose in the modular system design.

**Participant Path**: You'll use these imports to build production-ready AI applications. ChatOpenAI provides the reasoning engine, agents orchestrate complex workflows, memory maintains context, and callbacks enable monitoring.

**Implementer Path**: Understanding these abstractions enables architectural decisions about when to use LangChain's built-in components versus building custom implementations for enterprise requirements.

### LangChain's Four-Pillar Architecture

This modular design separates concerns for maintainable production systems:

1. **LLMs (Large Language Models)**: The reasoning engine that processes natural language and makes decisions
2. **Tools**: External interfaces that extend agent capabilities beyond text generation  
3. **Memory**: State management systems that maintain conversation context and learning
4. **Agents**: Orchestration layer that coordinates LLM reasoning with tool execution

**Production Considerations**: This separation enables independent scaling, testing, and replacement of components. However, the abstraction layers can introduce performance overhead and debugging complexity in enterprise environments.

#### LLM Setup Patterns (8 minutes)

Quick LLM initialization for different providers:

**Reference Implementation**: [`src/session2/llm_setup.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session2/llm_setup.py)

### LLM Factory Pattern - Production Configuration

```python
def create_llm(provider="openai"):
    if provider == "openai":
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
```

**Observer Path**: The factory pattern provides provider abstraction - one interface for multiple LLM services (OpenAI, Anthropic, local models). Temperature controls output randomness: 0=deterministic, 1=creative.

**Participant Path**: Environment variable configuration enables secure API key management. The factory pattern supports easy provider switching for cost optimization or feature requirements.

```python

# Usage with error handling

try:
    llm = create_llm("openai")
except Exception as e:
    print(f"LLM initialization failed: {e}")
    llm = create_llm("fallback_provider")
```

**Implementer Path**: Enterprise deployments extend this pattern with connection pooling, rate limiting, and failover mechanisms for production reliability.

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

### LLMChain - Fundamental Building Block

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Template with variable substitution

template = "Analyze this text and provide insights: {text}"
prompt = PromptTemplate(template=template, input_variables=["text"])
```

**Observer Path**: LLMChain combines LLM + prompt template for reusable workflows. Variables in `{brackets}` enable dynamic content substitution.

**Participant Path**: Build the chain and execute with real data:

```python

# Chain construction and execution

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("AI agents are becoming more capable")
print(f"Analysis: {result}")
```

**Implementer Path**: Production chains require error handling, input validation, and output parsing for reliable automation systems.

#### Sequential Chains (7 minutes)

Connecting multiple chains for complex workflows:

### Sequential Chain - Pipeline Processing

```python
from langchain.chains import SequentialChain

# Step 1: Content summarization

summary_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        template="Summarize: {text}",
        input_variables=["text"]
    ),
    output_key="summary"
)
```

**Observer Path**: Sequential chains enable multi-step processing where each step's output feeds the next step's input - ideal for complex analysis pipelines.

```python

# Step 2: Sentiment analysis

sentiment_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        template="Analyze sentiment of: {summary}",
        input_variables=["summary"]
    ),
    output_key="sentiment"
)
```

**Participant Path**: Chain composition creates sophisticated workflows:

```python

# Pipeline assembly

analysis_pipeline = SequentialChain(
    chains=[summary_chain, sentiment_chain],
    input_variables=["text"],
    output_variables=["summary", "sentiment"]
)

# Execute complete pipeline

results = analysis_pipeline.run({"text": "Long document content..."})
```

**Implementer Path**: Production pipelines require intermediate result validation, error recovery, and performance monitoring between chain steps.

#### Prompt Templates (5 minutes)

Dynamic prompt creation with variables:

Prompt templates allow you to create reusable, parameterized prompts. This is especially useful when you need consistent formatting across different inputs. Variables are filled in at runtime, enabling dynamic prompt generation.

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
```

Now we can use this template with a chain to generate dynamic responses:

```python

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

Robust error handling is crucial for production LangChain applications. Common failure reasons include API rate limits, network timeouts, and temporary service unavailability. This pattern implements retry logic with exponential backoff (wait times: 1s, 2s, 4s, etc.).

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

**Reference Implementation**: [`src/session2/langchain_tools.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session2/langchain_tools.py)

### Observer Path - What Are Tools?

Tools give AI agents "superpowers" beyond just text:
- Calculator tool: AI can do math
- Weather tool: AI can check current conditions
- Database tool: AI can look up information
- Web search tool: AI can find recent information

### Three Ways to Create Tools
1. **Tool class**: Most control, more code
2. **@tool decorator**: Clean and simple
3. **Function wrapper**: Quickest for testing

**Security Advisory**: Never use `eval()` in production - use secure math parsers like `sympy`.

### Participant Path - Create Simple Tools

```python
from langchain.agents import Tool
from langchain.tools import tool

# Method 1: Explicit tool creation

def get_weather(location: str) -> str:
    """Get weather for any city"""
    # In reality, call weather API
    return f"Weather in {location}: Sunny, 72°F"

weather_tool = Tool(
    name="Weather",
    description="Get current weather for any location",
    func=get_weather
)
```

**Observer Path**: The function does the work, Tool class wraps it for the agent to use.

Method 2 - Cleaner syntax:

```python

# Method 2: Decorator approach (cleaner)

@tool
def simple_calculator(math_problem: str) -> str:
    """Solve basic math like '2 + 2' or '10 * 5'"""
    try:
        # DEMO ONLY - use sympy in production!
        result = eval(math_problem.replace(' ', ''))
        return f"Answer: {result}"
    except:
        return "Cannot solve that math problem"
```

**Observer Path**: The @tool decorator automatically converts your function into an agent tool.

Method 3 - Quick testing:

```python

# Method 3: Simple wrapper for testing

def web_search_demo(query: str) -> str:
    """Pretend to search the web"""
    return f"Found 3 articles about '{query}'"

search_tool = Tool(
    name="WebSearch",
    description="Search for information online", 
    func=web_search_demo
)
```

#### Agent Initialization (7 minutes)

### Observer Path - How Agents Work

Agents follow the **ReAct pattern** (Reasoning + Acting):
1. **Think**: "User wants weather AND math - I need 2 tools"
2. **Act**: Use weather tool for "New York" 
3. **Think**: "Got weather, now need to calculate 15 * 24"
4. **Act**: Use calculator tool for "15 * 24"
5. **Think**: "Now I'll combine both results into a nice response"

### Participant Path - Agent Types

`CHAT_CONVERSATIONAL_REACT_DESCRIPTION` = Long name for:
- Uses chat models (like GPT-4)
- Remembers conversation history
- Follows ReAct thinking pattern
- Can use multiple tools intelligently

### Build Your First Agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

# Memory = conversation history

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True  # Keep message format
)
```

**Observer Path**: Memory stores what was said before, like a conversation transcript.

```python

# Give agent access to tools

tools = [weather_tool, simple_calculator, search_tool]

# Create the agent

agent = initialize_agent(
    tools=tools,           # What it can do
    llm=llm,              # How it thinks
    agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,         # What it remembers
    verbose=True          # Show thinking process
)
```

**Observer Path**: The agent now has a brain (LLM), tools (capabilities), and memory (context).

#### Tool Calling Patterns (5 minutes)

### See Your Agent Think and Act

```python

# Complex request that needs multiple tools

response = agent.run(
    "What's the weather in New York and what's 15 times 24?"
)
```

**Observer Path**: Watch the agent's thought process (if verbose=True):
```
Thought: I need to get weather for New York AND do math
Action: Weather tool with "New York" 
Observation: Weather in New York: Sunny, 72°F
Thought: Now I need to calculate 15 * 24
Action: Calculator tool with "15 * 24"
Observation: Answer: 360
Thought: I have both answers, time to respond
Final Answer: The weather in New York is sunny and 72°F. 15 times 24 equals 360.
```

**Participant Path**: The agent automatically:
1. Breaks down complex requests
2. Chooses appropriate tools
3. Executes actions in logical order
4. Combines results into coherent responses

**Implementer Path**: Production agents add tool timeout limits, result validation, error recovery, and fallback responses when tools fail.

#### Basic Error Recovery (5 minutes)

### Observer Path - Why Things Fail

Tools fail for common reasons:
- Weather API is down
- Calculator gets invalid input like "banana + 5"
- Network timeout
- Rate limits exceeded

### Participant Path - Graceful Error Handling

```python
def safe_agent_run(agent, user_question, backup_message=None):
    """Try to run agent, handle failures gracefully"""
    try:
        return agent.run(user_question)
    except Exception as error:
        print(f"Something went wrong: {error}")
        
        # Provide helpful fallback
        if backup_message:
            return backup_message
        else:
            return "I'm having technical difficulties. Please try again later."

# Usage example

result = safe_agent_run(
    agent,
    "What's the weather in Mars?",  # This might fail!
    backup_message="I can't check Mars weather, but I can help with Earth locations!"
)
```

**Observer Path**: Instead of crashing, the agent provides a helpful error message and suggests alternatives.

**Implementer Path**: Production systems add retry logic, circuit breakers, detailed error logging, and intelligent fallback routing.

---

### Part 4: Memory & State Management (15 minutes)

**Cognitive Load**: 3 new concepts
**Learning Mode**: Integration & Application

#### Memory Types (5 minutes)

### Observer Path - Memory Types Explained

**Buffer Memory** = Keep everything (like a complete transcript)
**Summary Memory** = Summarize old parts (like meeting minutes)
**Window Memory** = Keep only recent messages (like short-term memory)

### When to use which?
- **Buffer**: Short conversations, need exact history
- **Summary**: Long conversations, want context but not details  
- **Window**: Fixed memory size, only care about recent context

### Participant Path - Configure Memory Types

```python
from langchain.memory import (
    ConversationBufferMemory,      # Everything
    ConversationSummaryMemory,     # Summarized
    ConversationBufferWindowMemory # Recent only
)

# Option 1: Remember everything

full_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Option 2: Summarize old conversations

smart_memory = ConversationSummaryMemory(
    llm=llm,  # Needs LLM to create summaries
    memory_key="chat_history", 
    return_messages=True
)

# Option 3: Keep last 5 exchanges only

recent_memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,  # Last 5 question-answer pairs
    return_messages=True
)
```

#### State Persistence (5 minutes)

### Observer Path - Why Save Memory?

Imagine talking to a customer service agent who forgets everything each time you call. Saving memory lets your agent remember previous conversations.

### Participant Path - Simple Persistence

```python
import json

def save_conversation(memory, filename):
    """Save chat history to file"""
    with open(filename, 'w') as f:
        # Convert messages to saveable format
        messages = memory.chat_memory.messages
        json.dump([str(msg) for msg in messages], f)
    print(f"Conversation saved to {filename}")

def load_conversation(memory, filename):
    """Load previous chat history"""
    try:
        with open(filename, 'r') as f:
            old_messages = json.load(f)
            print(f"Loaded {len(old_messages)} previous messages")
            # Note: Simplified - full implementation needs message reconstruction
    except FileNotFoundError:
        print("No previous conversation found - starting fresh")
```

Usage example:

```python

# At end of session

save_conversation(memory, "customer_chat.json")

# At start of new session

load_conversation(memory, "customer_chat.json")
```

**Implementer Path**: Production systems use databases, handle message serialization properly, implement encryption for sensitive conversations, and manage memory lifecycle.

#### Context Management (5 minutes)

### Observer Path - Context = Personality + Knowledge

Context gives your agent:
- **Role**: "You're a medical assistant" vs "You're a coding tutor"
- **Knowledge**: "You know about our company's products"
- **Style**: "Be friendly and casual" vs "Be formal and professional"

### Participant Path - Create Specialized Agents

```python
def create_specialized_agent(role_description, tools_list):
    """Build agent with specific role and knowledge"""
    
    # Give the agent personality and context
    system_prompt = f"""
    You are {role_description}.
    
    Always stay in character and use your specialized knowledge.
    Be helpful but stick to your expertise area.
    """
```

Build the complete agent:

```python
    # Standard memory setup
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create agent with personality
    return initialize_agent(
        tools=tools_list,
        llm=llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        agent_kwargs={"system_message": system_prompt}
    )
```

Create different expert agents:

```python

# Medical assistant

med_agent = create_specialized_agent(
    "a medical research assistant helping doctors find information",
    [medical_database_tool, drug_interaction_tool]
)

# Coding tutor

code_agent = create_specialized_agent(
    "a programming tutor helping students learn Python",
    [code_runner_tool, documentation_tool]
)
```

---

## Core Section Validation (5 minutes)

### Professional Implementation Exercise

### Exercise Files

- [`src/session2/langchain_basics.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session2/langchain_basics.py) - Foundation patterns
- [`src/session2/langchain_tool_use.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session2/langchain_tool_use.py) - Agent implementation

### Validation Commands
```bash
cd src/session2
python langchain_basics.py        # Architecture validation
python langchain_tool_use.py      # Agent workflow testing
```

**Observer Path**: Run the example files to see LangChain in action. Notice how components work together and how agents make decisions.

**Participant Path**: Build a practical business assistant:
```python
def create_business_agent():
    # 1. Define tools: calculator, email, calendar
    # 2. Set up conversation memory
    # 3. Add error handling for tool failures
    # 4. Test with: "Schedule meeting and calculate budget"
    pass
```

**Implementer Path**: Add custom authentication, database connections, monitoring dashboards, and multi-agent coordination for enterprise deployment.

### Self-Assessment Checklist

- [ ] I can explain LangChain's 4 building blocks (LLM, Tools, Memory, Agent)
- [ ] I can create chains that process text through templates
- [ ] I can build tools that give agents new capabilities  
- [ ] I can set up agents that remember conversations
- [ ] I understand when to use LangChain vs alternatives for production

**Next Session Prerequisites**: ✅ Core Section Complete
**Recommended**: Explore at least one Optional Module for deeper understanding

---

### Choose Your Advanced Path:

- **[Module A: Advanced LangChain Patterns →](Session2_ModuleA_Advanced_LangChain_Patterns.md)** - Complex workflows & optimization
- **[Module B: Production Deployment Strategies →](Session2_ModuleB_Production_Deployment_Strategies.md)** - Enterprise deployment & monitoring
- **[Module C: Custom Tool Development →](Session2_ModuleC_Custom_Tool_Development.md)** - Building specialized tools
- **[Module D: Performance & Monitoring →](Session2_ModuleD_Performance_Monitoring.md)** - Optimization & observability
- **[Next Session: LangGraph Multi-Agent Workflows →](Session3_LangGraph_Multi_Agent_Workflows.md)** - Graph-based workflows

### Professional Learning Paths

**Executive Track**: Core → Module B (production strategy understanding)
**Engineering Track**: Core → Module A → Module C (technical implementation mastery)
**Architecture Track**: Core → Module B → Module D (enterprise deployment expertise)
**Complete Mastery**: All modules in sequence

---

## Multiple Choice Test - Session 2

Test your understanding of LangChain foundations and agent patterns:

**Question 1:** What is the primary benefit of LangChain's unified LLM interface?  
A) Lower cost  
B) Consistent API across different LLM providers  
C) Faster response times  
D) Better performance  

**Question 2:** Which LangChain component is responsible for managing conversation context?  
A) Chains  
B) Tools  
C) Memory  
D) Agents  

**Question 3:** How many ways can you create tools in LangChain?  
A) Four - including custom implementations  
B) Two - BaseTool and @tool decorator  
C) Three - BaseTool, @tool decorator, and StructuredTool  
D) One - inheriting from BaseTool  

**Question 4:** What is the purpose of the `handle_parsing_errors` parameter in LangChain agents?  
A) To gracefully handle malformed LLM responses  
B) To reduce costs  
C) To enable debugging  
D) To improve performance  

**Question 5:** Which LangChain agent type is specifically designed for the ReAct pattern?  
A) All of the above  
B) ZERO_SHOT_REACT_DESCRIPTION  
C) STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION  
D) REACT_DOCSTORE  

**[**View Test Solutions →**](Session2_Test_Solutions.md)**

## Navigation

**Previous:** [Session 1 - Bare Metal Agents](Session1_Bare_Metal_Agents.md)

### Advanced Modules:
- **[Module A: Advanced LangChain Patterns](Session2_ModuleA_Advanced_LangChain_Patterns.md)** - Complex workflows & optimization
- **[Module B: Production Deployment Strategies](Session2_ModuleB_Production_Deployment_Strategies.md)** - Enterprise deployment & monitoring
- **[Module C: Custom Tool Development](Session2_ModuleC_Custom_Tool_Development.md)** - Building specialized tools
- **[Module D: Performance & Monitoring](Session2_ModuleD_Performance_Monitoring.md)** - Optimization & observability

**Next:** [Session 3 - LangGraph Multi-Agent Workflows →](Session3_LangGraph_Multi_Agent_Workflows.md)

---

