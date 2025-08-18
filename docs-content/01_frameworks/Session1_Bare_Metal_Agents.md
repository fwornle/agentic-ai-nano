# Session 1: Bare Metal Agents (Pure Python Implementation)

## 🎯 Learning Navigation Hub

**Total Time Investment**: 75 minutes (Core) + 30-105 minutes (Optional)  
**Your Learning Path**: Choose your engagement level

### Quick Start Guide

- **👀 Observer (40 min)**: Read concepts + examine code structure  
- **🙋‍♂️ Participant (75 min)**: Follow exercises + implement basic agents  
- **🛠️ Implementer (120 min)**: Build custom agents + explore advanced patterns

---

## 📋 SESSION OVERVIEW DASHBOARD

### Core Learning Track (75 minutes) - REQUIRED

| Section | Concept Load | Time | Skills |
|---------|--------------|------|--------|
| 🏗️ Agent Architecture | 3 concepts | 20 min | Understanding |
| 🤖 Building First Agent | 4 concepts | 25 min | Implementation |
| 🛠️ Tool Integration | 4 concepts | 20 min | Application |
| ✅ Testing & Validation | 3 concepts | 10 min | Verification |

### Optional Deep Dive Modules (Choose Your Adventure)

- 🔬 **[Module A: Advanced Agent Patterns](Session1_ModuleA_Advanced_Agent_Patterns.md)** (40 min) - Sophisticated reasoning loops  
- ⚡ **[Module B: Performance Optimization](Session1_ModuleB_Performance_Optimization.md)** (35 min) - Speed & efficiency patterns  
- 🔄 **[Module C: Complex State Management](Session1_ModuleC_Complex_State_Management.md)** (30 min) - Advanced memory systems

**🗂️ Code Files**: All examples use files in [`src/session1/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session1)

---

## 🧭 CORE SECTION (Required - 75 minutes)

### Part 1: Agent Architecture Fundamentals (20 minutes)

**Cognitive Load**: 3 new concepts
**Learning Mode**: Conceptual Understanding

#### Basic Agent Structure (8 minutes)

Every agent needs these core components:

![Agent Pattern Control](images/agent-core-components.png)

🗂️ **File**: [`src/session1/base_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session1/base_agent.py)

This is the foundation class for all agents. Think of it as the blueprint that defines what capabilities every agent should have. The memory list stores past interactions, while the tools dictionary holds functions the agent can call.

```python
class BaseAgent:
    def __init__(self, model_name="gpt-4"):
        self.model_name = model_name
        self.memory = []  # Simple conversation memory
        self.tools = {}   # Available tools
        
    def run(self, user_input: str) -> str:
        """Main agent execution loop"""
        # 1. Process input
        # 2. Decide on action  
        # 3. Execute action
        # 4. Return response
        pass
```

The `run` method is where the magic happens. The actual implementation (available in the source file) involves parsing user input, determining if tools are needed, executing actions, and formatting the response.

**Key Concepts:**

1. **Model Interface**: How agents talk to LLMs  
2. **Memory Management**: Keeping track of context  
3. **Tool Registry**: Available actions the agent can take

#### Input/Output Handling (7 minutes)

Clean interfaces for agent interaction:

These methods belong to the BaseAgent class and handle data transformation between raw user input and structured agent processing. They ensure consistent formatting across all agent interactions.

```python
def process_input(self, user_input: str) -> dict:
    """Convert user input to structured format"""
    return {
        "message": user_input,
        "timestamp": datetime.now(),
        "session_id": self.session_id
    }

def format_output(self, agent_response: str) -> str:
    """Format agent response for display"""
    return f"🤖 Agent: {agent_response}"
```

#### State Management Basics (5 minutes)

Simple but effective state tracking:

The AgentState class tracks everything the agent needs to remember during conversations. This is crucial for maintaining context and making informed decisions throughout multi-turn interactions.

```python
class AgentState:
    def __init__(self):
        self.current_task = None
        self.conversation_history = []
        self.available_tools = []
        self.confidence_level = 0.0
        
    def update_state(self, action: str, result: str):
        """Update agent state after each action"""
        self.conversation_history.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now()
        })
```

---

### Part 2: Building Your First Agent (25 minutes)

**Cognitive Load**: 4 new concepts
**Learning Mode**: Hands-on Implementation

#### Simple Agent Implementation (10 minutes)

Let's build a working agent from scratch:

🗂️ **File**: [`src/session1/base_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session1/base_agent.py) - See the `SimpleAgent` class

```python
class SimpleAgent:
    def __init__(self):
        self.memory = []
```

The SimpleAgent class starts with basic initialization, creating an empty memory list to store conversation history.

Now let's add the core thinking logic that processes user input:

```python
    def think(self, input_text: str) -> str:
        """Basic reasoning step"""
        # Add to memory
        self.memory.append(f"User: {input_text}")
        
        # Simple response logic
        if "?" in input_text:
            response = f"I understand you're asking: {input_text}"
        else:
            response = f"I acknowledge: {input_text}"
            
        self.memory.append(f"Agent: {response}")
        return response
```

Finally, we add the main execution method and test the agent:

```python
    def run(self, input_text: str) -> str:
        """Main execution method"""
        return self.think(input_text)

# Test it out!
agent = SimpleAgent()
response = agent.run("What is machine learning?")
print(response)
```

#### Basic Reasoning Loop (8 minutes)

Implementing the core agent thinking process:

🗂️ **File**: [`src/session1/react_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session1/react_agent.py) - See the reasoning loop implementation

This method implements the ReAct (Reasoning + Acting) pattern, a fundamental pattern where agents think, act, and observe in a loop. Each iteration involves analyzing the situation, deciding on an action, executing it, and observing the results.

```python
def reasoning_loop(self, task: str) -> str:
    """Simple ReAct-style reasoning"""
    max_steps = 5
    
    for step in range(max_steps):
        # Think: Analyze current situation
        thought = self.generate_thought(task, step)
        print(f"Step {step + 1} - Thought: {thought}")
```

The reasoning loop begins by setting up the thinking phase - the agent analyzes the current situation and generates thoughts about how to proceed.

Next comes the action decision phase:

```python
        # Act: Decide what to do
        if self.is_task_complete(thought):
            return self.generate_final_answer(thought)
            
        action = self.decide_action(thought)
        print(f"Step {step + 1} - Action: {action}")
```

Finally, the agent observes the results and updates its memory for the next iteration:

```python
        # Observe: See results
        observation = self.execute_action(action)
        print(f"Step {step + 1} - Observation: {observation}")
        
        # Update state for next iteration
        self.update_memory(thought, action, observation)
    
    return "Task completed after maximum steps"
```

#### Error Handling Patterns (4 minutes)

Making agents robust:

This wrapper method ensures agents handle errors gracefully, preventing crashes and providing user-friendly error messages when something goes wrong.

```python
def safe_agent_execution(self, user_input: str) -> str:
    """Execute agent with proper error handling"""
    try:
        return self.run(user_input)
    except Exception as e:
        error_msg = f"Agent encountered an error: {e}"
        self.memory.append(f"Error: {error_msg}")
        return "I apologize, but I encountered an issue. Could you try rephrasing your request?"
```

#### Testing Your Agent (3 minutes)

🗂️ **File**: [`src/session1/test_agents.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session1/test_agents.py) - Complete test suite

```python
def test_simple_agent():
    """Test basic agent functionality"""
    agent = SimpleAgent()
    
    # Test question handling
    response = agent.run("What is AI?")
    assert "asking" in response.lower()
    
    # Test statement handling  
    response = agent.run("I like programming")
    assert "acknowledge" in response.lower()
    
    # Test memory
    assert len(agent.memory) == 4  # 2 user inputs + 2 agent responses
    
    print("✅ All tests passed!")

# Run the test
test_simple_agent()
```

---

### Part 3: Tool Integration Basics (20 minutes)

**Cognitive Load**: 4 new concepts
**Learning Mode**: Application & Integration

#### Simple Tool Creation (8 minutes)

Building tools that agents can use:

![Agent Pattern Tool Integration](images/agent-pattern-tool-integration.png)

🗂️ **File**: [`src/session1/tools.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session1/tools.py) - Complete tool implementations

The SimpleTool base class provides a consistent interface for all tools. The name is used by the agent to identify the tool, while the description helps the agent decide when to use it.

**⚠️ Security Warning**: The calculator example uses `eval()` which is dangerous! This implementation includes basic safety checks, but in production you should use a proper math expression parser like sympy or numexpr instead.

```python
class SimpleTool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, input_data: str) -> str:
        """Override this method in specific tools"""
        raise NotImplementedError
```

This base class defines the interface that all tools must follow. Each tool needs a name and description, plus an execute method.

Now let's implement a specific calculator tool with safety checks:

```python
class CalculatorTool(SimpleTool):
    def __init__(self):
        super().__init__("calculator", "Performs basic math calculations")
    
    def execute(self, expression: str) -> str:
        """Safely evaluate math expressions"""
        try:
            # Basic safety check
            if any(char in expression for char in ['import', 'exec', 'eval', '__']):
                return "Invalid expression for security reasons"
            
            result = eval(expression)
            return f"Calculation result: {result}"
        except Exception as e:
            return f"Math error: {e}"
```

Here's how to use the calculator tool:

```python
# Usage example
calc = CalculatorTool()
result = calc.execute("2 + 3 * 4")
print(result)  # "Calculation result: 14"
```

#### Tool Calling Mechanisms (6 minutes)

How agents decide when and how to use tools:

🗂️ **File**: [`src/session1/tool_use_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session1/tool_use_agent.py) - See the `ToolUseAgent` class

```python
class ToolUseAgent:
    def __init__(self):
        self.tools = {}
        self.memory = []
        
    def register_tool(self, tool: SimpleTool):
        """Add a tool to the agent's toolkit"""
        self.tools[tool.name] = tool
```

The ToolUseAgent starts with basic setup, maintaining a registry of available tools and conversation memory.

Now let's add the decision logic for when to use tools:

```python
    def should_use_tool(self, user_input: str) -> tuple[bool, str]:
        """Decide if we need a tool for this input"""
        # Simple keyword-based tool selection
        if any(word in user_input.lower() for word in ['calculate', 'math', '+', '-', '*', '/']):
            return True, 'calculator'
        return False, None
```

Finally, the main execution method that ties everything together:

```python
    def run(self, user_input: str) -> str:
        """Execute with tool usage"""
        needs_tool, tool_name = self.should_use_tool(user_input)
        
        if needs_tool and tool_name in self.tools:
            # Extract the calculation from the input
            # (In real implementation, use better parsing)
            tool_result = self.tools[tool_name].execute(user_input)
            return f"Using {tool_name}: {tool_result}"
        else:
            return f"I understand your request: {user_input}"
```

#### Basic Validation (3 minutes)

Ensuring tool outputs are useful:

This validation method helps agents determine if a tool executed successfully. It's part of the agent's quality control system, checking for common failure indicators like error messages or empty responses.

```python
def validate_tool_output(self, tool_name: str, output: str) -> bool:
    """Check if tool output looks reasonable"""
    if "error" in output.lower():
        return False
    if output.strip() == "":
        return False
    return True
```

#### Integration Testing (3 minutes)

Testing agents with tools:

This integration test verifies that agents and tools work together correctly, testing the complete flow from user input through tool execution to final response.

```python
def test_tool_integration():
    """Test agent + tool integration"""
    agent = ToolUseAgent()
    calc_tool = CalculatorTool()
    agent.register_tool(calc_tool)
    
    # Test tool usage
    response = agent.run("Calculate 15 + 27")
    assert "42" in response
    
    # Test non-tool usage
    response = agent.run("Hello there")
    assert "understand" in response
    
    print("✅ Tool integration tests passed!")
```

---

### Part 4: Testing & Validation (10 minutes)

**Cognitive Load**: 3 new concepts
**Learning Mode**: Production Readiness

#### Unit Testing Approaches (4 minutes)

🗂️ **File**: [`src/session1/test_agents.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session1/test_agents.py) - Complete test suite

```python
import unittest

class TestAgentFunctionality(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.agent = SimpleAgent()
        self.tool_agent = ToolUseAgent()
        self.tool_agent.register_tool(CalculatorTool())
```

The test class starts with setup, creating agent instances and registering tools for consistent testing.

Now let's add the individual test methods:

```python
    def test_basic_responses(self):
        """Test basic agent responses"""
        response = self.agent.run("Hello")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_tool_integration(self):
        """Test tool usage"""
        response = self.tool_agent.run("What is 5 * 6?")
        self.assertIn("30", response)
```

Finally, the test runner:

```python
# Run tests
if __name__ == "__main__":
    unittest.main()
```

#### Common Troubleshooting (3 minutes)

Typical issues and solutions:

```python
def debug_agent_issues(agent, user_input):
    """Helper function to debug agent problems"""
    print(f"Input: {user_input}")
    print(f"Memory state: {len(agent.memory)} items")
    print(f"Available tools: {list(agent.tools.keys())}")
    
    try:
        response = agent.run(user_input)
        print(f"Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Check input format and agent state")
```

#### Running Everything (3 minutes)

🗂️ **File**: [`src/session1/demo_runner.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session1/demo_runner.py) - Complete demonstration

```python
def run_agent_demo():
    """Demonstrate all agent capabilities"""
    print("=== Bare Metal Agent Demo ===")
    
    # 1. Simple agent
    simple_agent = SimpleAgent()
    print("Simple Agent Response:", simple_agent.run("What is AI?"))
```

The demo starts by testing our basic SimpleAgent with a question to see how it responds.

Next, we test tool integration capabilities:

```python
    # 2. Tool-enabled agent
    tool_agent = ToolUseAgent()
    tool_agent.register_tool(CalculatorTool())
    print("Tool Agent Response:", tool_agent.run("Calculate 12 * 8"))
```

Finally, we demonstrate the advanced ReAct reasoning pattern:

```python
    # 3. ReAct agent
    react_agent = ReActAgent()  # From react_agent.py
    print("ReAct Agent working on complex task...")
    response = react_agent.run("Plan a simple Python project")
    print("ReAct Response:", response)

if __name__ == "__main__":
    run_agent_demo()
```

---

## ✅ Core Section Validation (5 minutes)

### Quick Implementation Exercise

🗂️ **Files to Run**: [`src/session1/demo_runner.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session1/demo_runner.py)

```bash
cd src/session1
python demo_runner.py
python test_agents.py
```

### Self-Assessment Checklist

- [ ] I understand basic agent architecture (input/output, memory, tools)
- [ ] I can implement a simple reasoning loop
- [ ] I can create and integrate basic tools
- [ ] I can test agent functionality
- [ ] I'm ready to explore framework implementations

**Next Session Prerequisites**: ✅ Core Section Complete
**Ready for**: Session 2: LangChain Foundations (framework implementation)

---

## 📝 Multiple Choice Test - Session 1

Test your understanding of bare metal agent implementation and core patterns:

**Question 1:** What is the primary benefit of implementing agents from scratch before using frameworks?  
A) Lower resource usage  
B) Easier deployment  
C) Better performance  
D) Deeper understanding of agent mechanics  

 Deeper understanding of agent mechanics  


**Question 2:** In the BaseAgent class, what is the purpose of the conversation_history attribute?  
A) Maintaining context across interactions  
B) Error tracking  
C) Performance monitoring  
D) Tool execution logs  

 Tool execution logs  


**Question 3:** Which method must be implemented by all subclasses of BaseAgent?  
A) get_available_tools()  
B) process_message()  
C) add_tool()  
D) _generate_response()  

 _generate_response()  


**Question 4:** How does the Tool abstract base class ensure consistency across different tool implementations?  
A) By handling errors automatically  
B) By providing default implementations  
C) By requiring execute() and _get_parameters() methods  
D) By managing tool state  

 By managing tool state  


**Question 5:** What design pattern is demonstrated by the BaseAgent and its subclasses?  
A) Strategy Pattern  
B) Factory Pattern  
C) Template Method Pattern  
D) Observer Pattern  

 Observer Pattern  


[**🗂️ View Test Solutions →**](Session1_Test_Solutions.md)

## 🧭 Navigation

**Previous:** [Session 0 - Introduction to Agent Frameworks & Patterns](Session0_Introduction_to_Agent_Frameworks_Patterns.md)

**Optional Deep Dive Modules:**

- 🔬 **[Module A: Advanced Agent Patterns](Session1_ModuleA_Advanced_Agent_Patterns.md)** - Sophisticated reasoning loops  
- ⚡ **[Module B: Performance Optimization](Session1_ModuleB_Performance_Optimization.md)** - Speed & efficiency patterns  
- 🔄 **[Module C: Complex State Management](Session1_ModuleC_Complex_State_Management.md)** - Advanced memory systems

**Next:** [Session 2 - LangChain Foundations](Session2_LangChain_Foundations.md) →

---
