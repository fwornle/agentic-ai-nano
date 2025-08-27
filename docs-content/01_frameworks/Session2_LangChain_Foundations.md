# Session 2: LangChain Foundations

LangChain is a modular framework for building AI applications with language models. This session covers LangChain's core architecture, chain patterns, tool integration, and memory management.

**Code Repository**: [`src/session2/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session2)
**Quick Start**: `cd src/session2 && python langchain_basics.py`

---

## LangChain Architecture Overview


### Core Components

LangChain has four essential building blocks:

![LangChain Overview](images/langchain-overview.svg)

1. **LLMs**: Language models that power reasoning and text generation
2. **Tools**: External functions that extend agent capabilities
3. **Memory**: Context storage for conversation continuity  
4. **Agents**: Orchestration layer that coordinates components

### Installation and Setup

First, install LangChain and configure your environment:

```bash
pip install langchain==0.1.0 openai==1.0.0
export OPENAI_API_KEY="your-api-key"
```

### Essential Imports

These imports provide access to LangChain's core functionality:

```python
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StdOutCallbackHandler
```

### LLM Initialization

Create an LLM instance with proper configuration:

```python
def create_llm(provider="openai"):
    if provider == "openai":
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
```

The temperature parameter controls output randomness: 0 for deterministic responses, 1 for creative responses.

### Usage with Error Handling

Always include error handling when initializing LLMs:

```python
try:
    llm = create_llm("openai")
except Exception as e:
    print(f"LLM initialization failed: {e}")
    # Implement fallback logic here
```

### Component Flow

Here's how LangChain components work together:

```text
Input → Agent → Tool Selection → LLM Reasoning → Output
         ↑              ↓              ↑
      Memory ←→ Context Management ←→ State
```

---

## Chain Patterns

### Simple Chain Creation

Chains combine LLMs with prompt templates for reusable workflows:

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
```

Create a template with variable substitution:

```python
template = "Analyze this text and provide insights: {text}"
prompt = PromptTemplate(template=template, input_variables=["text"])
```

Variables in `{brackets}` enable dynamic content substitution.

### Chain Construction and Execution

Build the chain and execute it with data:

```python
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("AI agents are becoming more capable")
print(f"Analysis: {result}")
```

### Sequential Chains

Sequential chains connect multiple steps for complex workflows:

```python
from langchain.chains import SequentialChain
```

Create the first step - content summarization:

```python
summary_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        template="Summarize: {text}",
        input_variables=["text"]
    ),
    output_key="summary"
)
```

Create the second step - sentiment analysis:

```python
sentiment_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        template="Analyze sentiment of: {summary}",
        input_variables=["summary"]
    ),
    output_key="sentiment"
)
```

Each step's output feeds into the next step's input, creating a processing pipeline.

### Pipeline Assembly and Execution

Combine the chains into a complete pipeline:

```python
analysis_pipeline = SequentialChain(
    chains=[summary_chain, sentiment_chain],
    input_variables=["text"],
    output_variables=["summary", "sentiment"]
)
```

Execute the complete pipeline:

```python
results = analysis_pipeline.run({"text": "Long document content..."})
```

### Prompt Templates

Prompt templates create reusable, parameterized prompts with variables:

```python
template = """
Role: {role}
Task: {task} 
Context: {context}
Format your response as: {format}
"""
```

Define the template with input variables:

```python
prompt = PromptTemplate(
    template=template,
    input_variables=["role", "task", "context", "format"]
)
```

Variables are filled in at runtime, enabling dynamic prompt generation.

### Using Templates with Chains

Combine the template with a chain for dynamic responses:

```python
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(
    role="Data Analyst",
    task="Analyze trends",
    context="Sales data from Q4",
    format="Bullet points"
)
```

### Error Handling and Retry Logic

Robust error handling is crucial for production applications. Common failures include API rate limits, network timeouts, and service unavailability:

```python
from langchain.callbacks import StdOutCallbackHandler
import time
```

Implement retry logic with exponential backoff:

```python
def run_with_retry(chain, inputs, max_retries=3):
    for attempt in range(max_retries):
        try:
            return chain.run(inputs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Wait: 1s, 2s, 4s
```

### Usage Example

Use the retry function with proper error handling:

```python
try:
    result = run_with_retry(chain, {"text": "example input"})
except Exception as e:
    print(f"Chain failed after retries: {e}")
```

---

## Agent Creation & Tool Integration

### Understanding Tools

Tools extend agent capabilities beyond text generation:

- Calculator: Mathematical computations
- Weather: Current conditions lookup
- Database: Information retrieval
- Web search: Recent information access

### Tool Creation Methods

There are three ways to create tools in LangChain:

```python
from langchain.agents import Tool
from langchain.tools import tool
```

#### Method 1: Explicit Tool Creation

Define a function and wrap it in a Tool class:

```python
def get_weather(location: str) -> str:
    """Get weather for any city"""
    # In reality, call weather API
    return f"Weather in {location}: Sunny, 72°F"
```

Wrap the function in a Tool:

```python
weather_tool = Tool(
    name="Weather",
    description="Get current weather for any location",
    func=get_weather
)
```

#### Method 2: Decorator Approach

Use the @tool decorator for cleaner syntax:

```python
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

**Security Note**: Never use `eval()` in production - use secure parsers like `sympy`.

#### Method 3: Simple Wrapper

Quick wrapper for testing purposes:

```python
def web_search_demo(query: str) -> str:
    """Pretend to search the web"""
    return f"Found 3 articles about '{query}'"
```

Create the tool wrapper:

```python
search_tool = Tool(
    name="WebSearch",
    description="Search for information online", 
    func=web_search_demo
)
```

### Agent Initialization

Agents follow the **ReAct pattern** (Reasoning + Acting):

1. **Think**: Analyze the user's request
2. **Act**: Use appropriate tools
3. **Think**: Process the results
4. **Act**: Use more tools if needed
5. **Think**: Formulate final response

### Setting Up Memory

First, configure conversation memory:

```python
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
```

Memory stores conversation history:

```python
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
```

### Creating the Agent

Combine tools, LLM, and memory into an agent:

```python
tools = [weather_tool, simple_calculator, search_tool]
```

Initialize the agent with all components:

```python
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True  # Show thinking process
)
```

The agent now has reasoning (LLM), capabilities (tools), and context (memory).

### Tool Calling in Action

Run the agent with a complex request that needs multiple tools:

```python
response = agent.run(
    "What's the weather in New York and what's 15 times 24?"
)
```

### Agent Thought Process

With verbose=True, you can see the agent's reasoning:

```text
Thought: I need to get weather for New York AND do math
Action: Weather tool with "New York" 
Observation: Weather in New York: Sunny, 72°F
Thought: Now I need to calculate 15 * 24
Action: Calculator tool with "15 * 24"
Observation: Answer: 360
Thought: I have both answers, time to respond
Final Answer: The weather in New York is sunny and 72°F. 15 times 24 equals 360.
```

The agent automatically:

1. Breaks down complex requests
2. Chooses appropriate tools
3. Executes actions in logical order
4. Combines results into coherent responses

### Error Recovery

Tools can fail for various reasons:

- API downtime
- Invalid input
- Network timeouts
- Rate limits

### Graceful Error Handling

Implement error handling to prevent crashes:

```python
def safe_agent_run(agent, user_question, backup_message=None):
    """Try to run agent, handle failures gracefully"""
    try:
        return agent.run(user_question)
    except Exception as error:
        print(f"Something went wrong: {error}")
        
        if backup_message:
            return backup_message
        else:
            return "I'm having technical difficulties. Please try again later."
```

### Usage Example

Use the wrapper function with fallback messaging:

```python
result = safe_agent_run(
    agent,
    "What's the weather in Mars?",
    backup_message="I can't check Mars weather, but I can help with Earth locations!"
)
```

Instead of crashing, the agent provides helpful error messages and suggests alternatives.

---

## Memory & State Management

### Memory Types

LangChain offers three main memory types:

- **Buffer Memory**: Stores complete conversation history
- **Summary Memory**: Summarizes older conversations
- **Window Memory**: Keeps only recent messages

### When to Use Each Type

- **Buffer**: Short conversations requiring exact history
- **Summary**: Long conversations where context matters but details don't
- **Window**: Fixed memory size, focus on recent context

### Memory Configuration

Import the memory types:

```python
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory
)
```

#### Buffer Memory: Remember Everything

```python
full_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
```

#### Summary Memory: Intelligent Summarization

```python
smart_memory = ConversationSummaryMemory(
    llm=llm,  # Needs LLM to create summaries
    memory_key="chat_history", 
    return_messages=True
)
```

#### Window Memory: Recent Context Only

```python
recent_memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,  # Last 5 question-answer pairs
    return_messages=True
)
```

### State Persistence

Saving memory allows agents to remember previous conversations across sessions.

### Basic Persistence Functions

Implement simple file-based persistence:

```python
import json

def save_conversation(memory, filename):
    """Save chat history to file"""
    with open(filename, 'w') as f:
        messages = memory.chat_memory.messages
        json.dump([str(msg) for msg in messages], f)
    print(f"Conversation saved to {filename}")
```

Load previous conversations:

```python
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

### Usage Example

Save and load conversations:

```python
# At end of session
save_conversation(memory, "customer_chat.json")

# At start of new session
load_conversation(memory, "customer_chat.json")
```

### Context Management

Context gives agents personality and specialized knowledge:

- **Role**: Medical assistant vs coding tutor
- **Knowledge**: Domain-specific information
- **Style**: Communication preferences

### Creating Specialized Agents

Define a function to build specialized agents:

```python
def create_specialized_agent(role_description, tools_list):
    """Build agent with specific role and knowledge"""
    
    system_prompt = f"""
    You are {role_description}.
    
    Always stay in character and use your specialized knowledge.
    Be helpful but stick to your expertise area.
    """
```

Set up memory and create the agent:

```python
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    return initialize_agent(
        tools=tools_list,
        llm=llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        agent_kwargs={"system_message": system_prompt}
    )
```

### Creating Expert Agents

Build different specialized agents:

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

## Practical Implementation

### Exercise Files

Practice with these implementation examples:

- [`src/session2/langchain_basics.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session2/langchain_basics.py) - Foundation patterns
- [`src/session2/langchain_tool_use.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session2/langchain_tool_use.py) - Agent implementation

### Validation Commands

Test your understanding with these commands:

```bash
cd src/session2
python langchain_basics.py        # Architecture validation
python langchain_tool_use.py      # Agent workflow testing
```

### Build Your Own Business Agent

Create a practical assistant following this structure:

```python
def create_business_agent():
    # 1. Define tools: calculator, email, calendar
    # 2. Set up conversation memory
    # 3. Add error handling for tool failures
    # 4. Test with: "Schedule meeting and calculate budget"
    pass
```

### Self-Assessment Checklist

- [ ] I can explain LangChain's 4 building blocks (LLM, Tools, Memory, Agent)
- [ ] I can create chains that process text through templates
- [ ] I can build tools that give agents new capabilities  
- [ ] I can set up agents that remember conversations
- [ ] I understand when to use LangChain vs alternatives for production

---

---

## 📝 Multiple Choice Test - Session 2

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

**Question 4:** What is the primary purpose of Sequential Chains in LangChain?  
A) To run multiple agents simultaneously  
B) To connect multiple processing steps where each step's output feeds the next  
C) To handle errors in parallel  
D) To reduce computational costs  

**Question 5:** Which memory type would be best for a long conversation where you need context but not all details?  
A) ConversationBufferMemory  
B) ConversationSummaryMemory  
C) ConversationBufferWindowMemory  
D) ConversationEntityMemory  

[**🗂️ View Test Solutions →**](Session2_Test_Solutions.md)

## 🧭 Navigation

**Previous:** [Session 1 - Bare Metal Agents](Session1_Bare_Metal_Agents.md)

**Optional Deep Dive Modules:**

- 🔬 **[Module A: Advanced LangChain Patterns](Session2_ModuleA_Advanced_LangChain_Patterns.md)** - Complex workflows & optimization
- 🏭 **[Module B: Production Deployment Strategies](Session2_ModuleB_Production_Deployment_Strategies.md)** - Enterprise deployment & monitoring
- 🛠️ **[Module C: Custom Tool Development](Session2_ModuleC_Custom_Tool_Development.md)** - Building specialized tools
- 📊 **[Module D: Performance & Monitoring](Session2_ModuleD_Performance_Monitoring.md)** - Optimization & observability

**Next:** [Session 3 - LangGraph Multi-Agent Workflows →](Session3_LangGraph_Multi_Agent_Workflows.md)

---

