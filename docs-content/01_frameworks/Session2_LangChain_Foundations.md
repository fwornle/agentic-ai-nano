# Session 2: LangChain Foundations - Building Intelligent Application Architectures

Imagine you're an architect designing a smart city where different AI components work together seamlessly - traffic lights coordinate with navigation systems, weather sensors influence energy grids, and citizen services adapt to real-time needs. This is exactly what LangChain enables in the AI world: a sophisticated framework that transforms isolated language model calls into orchestrated, intelligent applications that can reason, remember, and act purposefully.

In this session, you'll build your first LangChain applications and discover why this framework has become the backbone of modern AI systems.

**Code Repository**: [`src/session2/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session2)
**Quick Start**: `cd src/session2 && python langchain_basics.py`

---

## LangChain Architecture Overview: The Master Conductor's Framework

Building on the bare metal foundations from Session 1, LangChain operates like a master conductor leading a symphony orchestra. Each component - models, prompts, chains, and memory - plays its specific part, but the magic happens when they're orchestrated together to create something far more powerful than the sum of their parts.

### Core Components

LangChain has four essential building blocks that work together like departments in a well-run organization:

![LangChain Overview](images/langchain-overview.svg)

1. **LLMs**: These are your brilliant consultants who provide insights and generate responses - the reasoning engines that power intelligent behavior
2. **Tools**: External functions that extend agent capabilities beyond text generation - like giving your AI hands to interact with the digital world
3. **Memory**: Context storage for conversation continuity - the agent's ability to remember what happened before, just like human working memory
4. **Agents**: Orchestration layer that coordinates components - the intelligent dispatcher that decides what to do when

### Installation and Setup

First, we'll set up the foundation that transforms individual API calls into sophisticated AI systems:

```bash
pip install langchain==0.1.0 openai==1.0.0
export OPENAI_API_KEY="your-api-key"
```

### Essential Imports

These imports provide access to LangChain's core functionality, giving you the building blocks for intelligent applications:

```python
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StdOutCallbackHandler
```

### LLM Initialization

Create an LLM instance with proper configuration - this is where raw computational power becomes accessible intelligence:

```python
def create_llm(provider="openai"):
    if provider == "openai":
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
```

The temperature parameter controls output randomness: 0 for deterministic responses (like a precise calculator), 1 for creative responses (like a brainstorming partner).

### Usage with Error Handling

Always include error handling when initializing LLMs - production systems need graceful failure handling:

```python
try:
    llm = create_llm("openai")
except Exception as e:
    print(f"LLM initialization failed: {e}")
    # Implement fallback logic here
```

### Component Flow

Here's how LangChain components work together in an intelligent dance of coordination:

```text
Input → Agent → Tool Selection → LLM Reasoning → Output
         ↑              ↓              ↑
      Memory ←→ Context Management ←→ State
```

This flow mirrors how human experts solve problems - they listen, remember context, choose appropriate methods, apply reasoning, and respond with informed answers.

---

## Chain Patterns: Building Processing Pipelines

Chains are where LangChain truly shines, transforming simple interactions into sophisticated processing workflows. Think of chains as assembly lines where each station adds value to the final product.

### Simple Chain Creation

Chains combine LLMs with prompt templates for reusable workflows, solving the problem of how to make AI responses consistent and purposeful:

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
```

Create a template with variable substitution - this is like creating a conversation blueprint that adapts to different situations:

```python
template = "Analyze this text and provide insights: {text}"
prompt = PromptTemplate(template=template, input_variables=["text"])
```

Variables in `{brackets}` enable dynamic content substitution - the same template works for analyzing news articles, customer feedback, or research papers.

### Chain Construction and Execution

Build the chain and execute it with data - this is where templates become living, responsive systems:

```python
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("AI agents are becoming more capable")
print(f"Analysis: {result}")
```

### Sequential Chains

Sequential chains connect multiple steps for complex workflows, like having multiple experts review the same document in sequence:

```python
from langchain.chains import SequentialChain
```

Create the first step - content summarization (like having a research assistant extract key points):

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

Create the second step - sentiment analysis (like having an emotional intelligence expert interpret the tone):

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

Each step's output feeds into the next step's input, creating a processing pipeline that mirrors how human experts collaborate on complex analysis.

### Pipeline Assembly and Execution

Combine the chains into a complete pipeline - this creates a system where the whole is greater than the sum of its parts:

```python
analysis_pipeline = SequentialChain(
    chains=[summary_chain, sentiment_chain],
    input_variables=["text"],
    output_variables=["summary", "sentiment"]
)
```

Execute the complete pipeline - watch as your raw text transforms into structured insights:

```python
results = analysis_pipeline.run({"text": "Long document content..."})
```

### Prompt Templates

Prompt templates create reusable, parameterized prompts with variables, solving the challenge of how to maintain consistency while adapting to different contexts:

```python
template = """
Role: {role}
Task: {task} 
Context: {context}
Format your response as: {format}
"""
```

Define the template with input variables - this creates a flexible framework that can handle countless scenarios:

```python
prompt = PromptTemplate(
    template=template,
    input_variables=["role", "task", "context", "format"]
)
```

Variables are filled in at runtime, enabling dynamic prompt generation that adapts to specific needs while maintaining professional structure.

### Using Templates with Chains

Combine the template with a chain for dynamic responses - this is where templates become powerful, adaptive interfaces:

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

Robust error handling is crucial for production applications, transforming brittle demos into resilient systems. Common failures include API rate limits, network timeouts, and service unavailability:

```python
from langchain.callbacks import StdOutCallbackHandler
import time
```

Implement retry logic with exponential backoff - this pattern handles temporary failures gracefully:

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

Use the retry function with proper error handling - this ensures your applications degrade gracefully:

```python
try:
    result = run_with_retry(chain, {"text": "example input"})
except Exception as e:
    print(f"Chain failed after retries: {e}")
```

---

## Agent Creation & Tool Integration: Giving AI Hands to Act

Moving beyond text generation, we now give our agents the ability to take action in the digital world. This is where AI transforms from passive responders to active problem-solvers.

### Understanding Tools

Tools extend agent capabilities beyond text generation, like giving a brilliant mind the ability to interact with the physical world:

- Calculator: Mathematical computations with perfect accuracy
- Weather: Current conditions lookup from live data sources
- Database: Information retrieval from structured knowledge
- Web search: Recent information access from the entire internet

### Tool Creation Methods

There are three ways to create tools in LangChain, each optimized for different use cases:

```python
from langchain.agents import Tool
from langchain.tools import tool
```

#### Method 1: Explicit Tool Creation

Define a function and wrap it in a Tool class - this approach gives you maximum control and clarity:

```python
def get_weather(location: str) -> str:
    """Get weather for any city"""
    # In reality, call weather API
    return f"Weather in {location}: Sunny, 72°F"
```

Wrap the function in a Tool - this creates a standardized interface that agents can understand and use:

```python
weather_tool = Tool(
    name="Weather",
    description="Get current weather for any location",
    func=get_weather
)
```

#### Method 2: Decorator Approach

Use the @tool decorator for cleaner syntax - this is like adding superpowers to regular functions:

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

**Security Note**: Never use `eval()` in production - use secure parsers like `sympy` to prevent code injection attacks.

#### Method 3: Simple Wrapper

Quick wrapper for testing purposes - perfect for prototyping and demos:

```python
def web_search_demo(query: str) -> str:
    """Pretend to search the web"""
    return f"Found 3 articles about '{query}'"
```

Create the tool wrapper - this makes any function available to your agents:

```python
search_tool = Tool(
    name="WebSearch",
    description="Search for information online", 
    func=web_search_demo
)
```

### Agent Initialization

Agents follow the **ReAct pattern** (Reasoning + Acting) - a cycle that mirrors how human experts approach complex problems:

1. **Think**: Analyze the user's request and understand what's needed
2. **Act**: Use appropriate tools to gather information or take action
3. **Think**: Process the results and determine if more action is needed
4. **Act**: Use more tools if the problem isn't fully solved
5. **Think**: Formulate final response based on all gathered information

### Setting Up Memory

First, configure conversation memory - this gives agents the ability to maintain context across multiple interactions:

```python
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
```

Memory stores conversation history like a human's working memory during extended discussions:

```python
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
```

### Creating the Agent

Combine tools, LLM, and memory into an agent - this creates an intelligent system that can reason, remember, and act:

```python
tools = [weather_tool, simple_calculator, search_tool]
```

Initialize the agent with all components - this is where individual pieces become an intelligent, coordinated system:

```python
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True  # Show thinking process
)
```

The agent now has reasoning (LLM), capabilities (tools), and context (memory) - everything needed for intelligent problem-solving.

### Tool Calling in Action

Run the agent with a complex request that needs multiple tools - watch as it breaks down problems like a human expert:

```python
response = agent.run(
    "What's the weather in New York and what's 15 times 24?"
)
```

### Agent Thought Process

With verbose=True, you can see the agent's reasoning - this reveals the sophisticated decision-making happening behind the scenes:

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

The agent automatically handles complex coordination tasks that would require explicit programming in traditional systems:

1. Breaks down complex requests into manageable subtasks
2. Chooses appropriate tools for each subtask
3. Executes actions in logical order for efficiency
4. Combines results into coherent, comprehensive responses

### Error Recovery

Tools can fail for various reasons in real-world applications - network issues, service outages, and data problems are inevitable:

- API downtime when services are unavailable
- Invalid input when users provide malformed data
- Network timeouts during slow connections
- Rate limits when services restrict usage

### Graceful Error Handling

Implement error handling to prevent crashes and maintain user experience:

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

Use the wrapper function with fallback messaging - this ensures users always get helpful responses:

```python
result = safe_agent_run(
    agent,
    "What's the weather in Mars?",
    backup_message="I can't check Mars weather, but I can help with Earth locations!"
)
```

Instead of crashing, the agent provides helpful error messages and suggests alternatives - the difference between a brittle demo and a user-friendly application.

---

## Memory & State Management: Building Persistent Intelligence

Memory transforms stateless interactions into coherent, context-aware conversations. Just as humans maintain working memory during discussions, agents need memory systems to provide intelligent, contextual responses.

### Memory Types

LangChain offers three main memory types, each optimized for different scenarios like different types of human memory:

- **Buffer Memory**: Stores complete conversation history (like a detailed meeting transcript)
- **Summary Memory**: Summarizes older conversations (like executive briefings that capture key points)
- **Window Memory**: Keeps only recent messages (like short-term memory focused on immediate context)

### When to Use Each Type

Choose memory types based on your application's needs and constraints:

- **Buffer**: Short conversations requiring exact history - perfect for technical support or detailed consultations
- **Summary**: Long conversations where context matters but details don't - ideal for ongoing coaching or therapy sessions
- **Window**: Fixed memory size, focus on recent context - best for chatbots with resource constraints

### Memory Configuration

Import the memory types that will give your agents different cognitive capabilities:

```python
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory
)
```

#### Buffer Memory: Remember Everything

Perfect for situations where every detail matters - like a court stenographer capturing every word:

```python
full_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
```

#### Summary Memory: Intelligent Summarization

Uses the LLM to compress old conversations while preserving important context - like having a personal assistant who keeps you briefed:

```python
smart_memory = ConversationSummaryMemory(
    llm=llm,  # Needs LLM to create summaries
    memory_key="chat_history", 
    return_messages=True
)
```

#### Window Memory: Recent Context Only

Maintains focus on the most recent interactions - like having a conversation where you naturally forget older topics:

```python
recent_memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,  # Last 5 question-answer pairs
    return_messages=True
)
```

### State Persistence

Saving memory allows agents to remember previous conversations across sessions, creating continuity like human relationships that build over time.

### Basic Persistence Functions

Implement simple file-based persistence - this transforms temporary interactions into lasting relationships:

```python
import json

def save_conversation(memory, filename):
    """Save chat history to file"""
    with open(filename, 'w') as f:
        messages = memory.chat_memory.messages
        json.dump([str(msg) for msg in messages], f)
    print(f"Conversation saved to {filename}")
```

Load previous conversations to maintain continuity across sessions:

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

Save and load conversations to create persistent agent relationships:

```python
# At end of session
save_conversation(memory, "customer_chat.json")

# At start of new session
load_conversation(memory, "customer_chat.json")
```

### Context Management

Context gives agents personality and specialized knowledge, transforming generic AI into domain experts:

- **Role**: Medical assistant vs coding tutor - different expertise and communication styles
- **Knowledge**: Domain-specific information that shapes responses
- **Style**: Communication preferences that match user expectations

### Creating Specialized Agents

Define a function to build specialized agents - this is like hiring different experts for different tasks:

```python
def create_specialized_agent(role_description, tools_list):
    """Build agent with specific role and knowledge"""
    
    system_prompt = f"""
    You are {role_description}.
    
    Always stay in character and use your specialized knowledge.
    Be helpful but stick to your expertise area.
    """
```

Set up memory and create the agent - this builds a consistent personality that users can rely on:

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

Build different specialized agents - each with their own expertise and personality:

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

## Practical Implementation: Building Real-World Systems

Now we move from concepts to practice, creating agents that solve actual business problems and provide real value to users.

### Exercise Files

Practice with these implementation examples that demonstrate LangChain patterns in action:

- [`src/session2/langchain_basics.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session2/langchain_basics.py) - Foundation patterns and core concepts
- [`src/session2/langchain_tool_use.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session2/langchain_tool_use.py) - Complete agent implementation with tools

### Validation Commands

Test your understanding with these commands that verify your implementations work correctly:

```bash
cd src/session2
python langchain_basics.py        # Architecture validation
python langchain_tool_use.py      # Agent workflow testing
```

### Build Your Own Business Agent

Create a practical assistant following this structure - this exercise brings together everything you've learned:

```python
def create_business_agent():
    # 1. Define tools: calculator, email, calendar
    # 2. Set up conversation memory
    # 3. Add error handling for tool failures
    # 4. Test with: "Schedule meeting and calculate budget"
    pass
```

### Self-Assessment Checklist

Verify your understanding before moving forward:

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