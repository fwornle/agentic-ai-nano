# Session 1 - Module A: Advanced Agent Patterns (40 minutes)

**Prerequisites**: [Session 1 Core Section Complete](Session1_Bare_Metal_Agents.md)  
**Target Audience**: Implementers seeking sophisticated patterns  
**Cognitive Load**: 6 advanced concepts

---

## 🎯 Module Overview

This module explores sophisticated agent patterns including reflection-based self-improvement, multi-step planning systems, and collaborative multi-agent architectures. You'll implement advanced reasoning loops that form the foundation of professional agent frameworks.

### Learning Objectives

By the end of this module, you will:

- Build reflection agents that improve their own outputs through self-critique
- Implement multi-step planning systems for complex task decomposition
- Create multi-agent orchestration systems with specialized roles
- Design self-improvement mechanisms that enhance agent performance over time

---

## Part 1: Sophisticated Reasoning Loops (15 minutes)

### The Reflection Pattern Implementation

🗂️ **File**: `src/session1/reflection_agent.py` - Advanced ReAct implementation

The reflection pattern enables agents to iteratively improve their responses through self-critique and refinement:

**Traditional Approach:**

```text
Question → Generate Answer → Return Answer
```

**Reflection Approach:**

```text
Question → Initial Answer → Critique → Improve → Critique → Improve → Final Answer
```

### Reflection Agent Structure

Understanding Bare Metal Self-Improvement: This reflection agent demonstrates the foundational pattern of iterative self-improvement. It inherits from BaseAgent and adds the ability to critique and enhance its own responses through multiple iterations.

```python
# From src/session1/reflection_agent.py
from base_agent import BaseAgent
from typing import Dict

class ReflectionAgent(BaseAgent):
    """Agent that reflects on and improves its own outputs"""
    
    def __init__(self, name: str, llm_client, max_iterations: int = 3):
        super().__init__(name, "Agent with reflection capabilities", llm_client)
        self.max_iterations = max_iterations  # Prevent infinite loops
        self.reflection_history = []          # Track improvement process
```

**Why Limit Iterations?** Without a maximum, the agent could get stuck in endless self-improvement loops.

### The Core Reflection Loop

The core reflection loop orchestrates the iterative improvement process:

```python
# From src/session1/reflection_agent.py (continued)
async def _generate_response(self, message: str, context: Dict = None) -> str:
    """Generate response with reflection and improvement"""
    current_response = await self._initial_response(message, context)
    
    for iteration in range(self.max_iterations):
        # Step 1: Reflect on current response
        critique = await self._reflect_on_response(message, current_response)
        
        # Step 2: If response is good enough, return it
        if self._is_response_satisfactory(critique):
            self.logger.info(f"Response satisfactory after {iteration + 1} iterations")
            break
```

The loop continues with improvement and tracking phases:

```python
        # Step 3: Improve response based on critique
        improved_response = await self._improve_response(
            message, current_response, critique
        )
        
        # Step 4: Track the improvement process
        self._track_reflection(iteration, current_response, critique, improved_response)
        
        current_response = improved_response
    
    return current_response
```

### Reflection Methods Implementation

**Initial Response Generation:**

```python
async def _initial_response(self, message: str, context: Dict = None) -> str:
    """Generate initial response without reflection"""
    system_prompt = f"""
    You are {self.name}, {self.description}.
    Provide a helpful response to the user's message.
    This is your initial response - focus on being accurate and comprehensive.
    """
    
    prompt = f"{system_prompt}\n\nUser message: {message}"
    response = await self._call_llm(prompt)
    return response
```

**Self-Critique Implementation:**

The reflection method analyzes the agent's own response using structured evaluation criteria. This systematic approach ensures consistent, high-quality feedback:

```python
async def _reflect_on_response(self, original_message: str, response: str) -> str:
    """Generate critique of the current response"""
    critique_prompt = f"""
    Analyze this response to the user's message and provide constructive criticism.
    
    User's message: {original_message}
    Response to critique: {response}
    
    Evaluate:
    1. Accuracy of information
    2. Completeness of answer
    3. Clarity and organization
    4. Helpfulness to the user
    
    Provide specific suggestions for improvement.
    If the response is already excellent, say "SATISFACTORY".
    """
    
    critique = await self._call_llm(critique_prompt)
    return critique
```

The "SATISFACTORY" keyword provides a clear stopping condition, preventing endless improvement cycles when the response is already good enough.

**Response Improvement:**

The improvement process takes the critique and generates an enhanced response that specifically addresses the identified issues:

```python
async def _improve_response(self, message: str, current_response: str, critique: str) -> str:
    """Improve response based on critique"""
    improvement_prompt = f"""
    Improve the following response based on the critique provided.
    
    Original user message: {message}
    Current response: {current_response}
    Critique: {critique}
    
    Generate an improved version that addresses the critique while maintaining accuracy.
    """
    
    improved = await self._call_llm(improvement_prompt)
    return improved
```

---

## Part 2: Multi-Step Planning (15 minutes)

### Planning Agent Architecture

🗂️ **File**: `src/session1/react_agent.py` - Multi-step planning implementation

Complex tasks require breaking down into manageable steps with proper execution order and dependency handling:

```python
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
```

The `TaskStatus` enum provides clear tracking of each step's execution state, enabling proper workflow management and error handling throughout the planning process.

```python
@dataclass
class PlanStep:
    id: str
    description: str
    dependencies: List[str]
    estimated_time: int
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
```

The `PlanStep` dataclass captures all essential information for step execution: what to do (description), when to do it (dependencies), how long it might take (estimated_time), and what happened (status and result).

```python
class PlanningAgent(BaseAgent):
    """Agent that breaks down complex tasks into executable plans"""
    
    def __init__(self, name: str, llm_client):
        super().__init__(name, "Multi-step planning agent", llm_client)
        self.current_plan: Optional[List[PlanStep]] = None
        self.execution_history: List[Dict] = []
```

### Plan Generation

The planning system breaks complex tasks into manageable, executable steps with clear dependencies:

The planning system breaks complex tasks into manageable, executable steps with clear dependencies:

```python
async def create_plan(self, complex_task: str) -> List[PlanStep]:
    """Break down complex task into executable steps"""
    
    planning_prompt = f"""
    Break down this complex task into specific, executable steps:
    Task: {complex_task}
    
    For each step, provide:
    1. Clear description of what to do
    2. Dependencies (which steps must complete first)
    3. Estimated time in minutes
    
    Format as a numbered list with dependencies noted.
    Be specific and actionable.
    """
```

After generating the plan text, it's parsed into structured objects:

```python
    plan_text = await self._call_llm(planning_prompt)
    
    # Parse the plan into PlanStep objects
    steps = self._parse_plan_text(plan_text)
    self.current_plan = steps
    
    return steps
```

The LLM generates a text-based plan which is then parsed into structured objects for programmatic execution.

```python
def _parse_plan_text(self, plan_text: str) -> List[PlanStep]:
    """Parse LLM-generated plan into structured steps"""
    steps = []
    lines = plan_text.strip().split('\n')
    
    for i, line in enumerate(lines):
        if line.strip() and any(line.startswith(str(j)) for j in range(1, 20)):
            # Extract step information
            step_id = f"step_{i+1}"
            description = line.split('.', 1)[1].strip() if '.' in line else line.strip()
```

The parser identifies numbered steps and extracts their descriptions. This approach handles various formatting styles from different LLM responses.

```python
            # Simple dependency detection (look for "after step X" patterns)
            dependencies = self._extract_dependencies(description)
            
            steps.append(PlanStep(
                id=step_id,
                description=description,
                dependencies=dependencies,
                estimated_time=5  # Default estimate
            ))
    
    return steps
```

Dependency extraction looks for phrases like "after step 2" to understand task ordering. Each step becomes a structured object that can be executed systematically.

### Plan Execution Engine

The execution engine manages the sequential execution of plan steps while respecting dependencies:

```python
async def execute_plan(self) -> Dict[str, any]:
    """Execute the current plan with dependency management"""
    if not self.current_plan:
        return {"error": "No plan to execute"}
    
    execution_log = []
    completed_steps = set()
    
    while len(completed_steps) < len(self.current_plan):
        # Find next executable step (dependencies satisfied)
        next_step = self._find_next_executable_step(completed_steps)
        
        if not next_step:
            return {"error": "No executable steps found - circular dependencies?"}
```

The main loop continues until all steps are completed, finding the next executable step at each iteration. The circular dependency check prevents infinite loops.

```python
        # Execute the step
        self.logger.info(f"Executing step: {next_step.description}")
        next_step.status = TaskStatus.IN_PROGRESS
        
        try:
            result = await self._execute_step(next_step)
            next_step.result = result
            next_step.status = TaskStatus.COMPLETED
            completed_steps.add(next_step.id)
            
            execution_log.append({
                "step": next_step.description,
                "result": result,
                "status": "completed"
            })
```

Each step execution is wrapped in a try-catch block with proper status tracking. Successful completions are logged and the step ID is added to the completed set.

```python
        except Exception as e:
            next_step.status = TaskStatus.FAILED
            execution_log.append({
                "step": next_step.description,
                "error": str(e),
                "status": "failed"
            })
            break
    
    return {
        "execution_log": execution_log,
        "completed_steps": len(completed_steps),
        "total_steps": len(self.current_plan),
        "success": len(completed_steps) == len(self.current_plan)
    }
```

Failure handling stops the execution and logs the error. The return structure provides complete visibility into the execution process and outcomes.

```python
def _find_next_executable_step(self, completed_steps: set) -> Optional[PlanStep]:
    """Find a step whose dependencies are satisfied"""
    for step in self.current_plan:
        if (step.status == TaskStatus.PENDING and 
            all(dep in completed_steps for dep in step.dependencies)):
            return step
    return None
```

The dependency resolver ensures steps only execute when their prerequisites are complete, maintaining proper execution order.

```python
async def _execute_step(self, step: PlanStep) -> str:
    """Execute an individual plan step"""
    execution_prompt = f"""
    Execute this specific task step:
    {step.description}
    
    Provide a clear result of what was accomplished.
    Be specific about what was done and any outputs produced.
    """
    
    result = await self._call_llm(execution_prompt)
    return result
```

Individual step execution uses focused prompts that clearly specify what needs to be accomplished and what kind of output is expected.

---

## Part 3: Multi-Agent Orchestration (10 minutes)

### Agent Coordinator Architecture

🗂️ **File**: `src/session1/multi_agent_system.py` - Multi-agent coordination

Understanding Bare Metal Multi-Agent Coordination: This coordinator class manages multiple specialized agents working together on complex tasks. It handles agent registration, message routing, and communication tracking.

```python
from typing import Dict, List, Any
from base_agent import BaseAgent, AgentMessage
from datetime import datetime

class AgentCoordinator:
    """Coordinates multiple specialized agents in a system"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}  # Registered agents
        self.message_history = []               # All inter-agent messages
        self.communication_patterns = {}       # Track who talks to whom
    
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent with the coordinator"""
        self.agents[agent.name] = agent
        self.communication_patterns[agent.name] = []
        print(f"✓ Registered agent: {agent.name} ({agent.description})")
```

### Message Routing System

The routing system manages communication between agents while maintaining detailed logs for analysis:

```python
async def route_message(self, message: str, to_agent: str, from_agent: str = "user") -> str:
    """Route message to specific agent and track communication"""
    if to_agent not in self.agents:
        return f"Error: Agent '{to_agent}' not found"
    
    # Log communication pattern
    self.communication_patterns[to_agent].append({
        "from": from_agent,
        "message": message[:50] + "..." if len(message) > 50 else message,
        "timestamp": datetime.now()
    })
```

Communication patterns are tracked separately from full message history, allowing analysis of agent interaction frequency and patterns while keeping logs manageable.

```python
    # Process message with target agent
    agent = self.agents[to_agent]
    response = await agent.process_message(message)
    
    # Store complete conversation
    self.message_history.append({
        "from": from_agent,
        "to": to_agent,
        "message": message,
        "response": response,
        "timestamp": datetime.now()
    })
    
    return response
```

The complete message history stores full conversations for debugging and audit purposes, while the response is returned immediately to maintain system responsiveness.

### Collaborative Task Management

Complex tasks are broken down and delegated to the most appropriate specialized agents:

```python
async def delegate_complex_task(self, task: str) -> Dict[str, Any]:
    """Delegate complex task to appropriate specialized agents"""
    
    # Step 1: Analyze task to determine which agents are needed
    task_analysis = await self._analyze_task_requirements(task)
    
    # Step 2: Create delegation plan
    delegation_plan = self._create_delegation_plan(task_analysis)
    
    # Step 3: Execute delegation plan
```

The three-phase approach ensures systematic task decomposition: first understanding what skills are needed, then planning how to use available agents, and finally executing the coordinated effort.

```python
    results = {}
    for agent_name, subtask in delegation_plan.items():
        if agent_name in self.agents:
            result = await self.route_message(subtask, agent_name, "coordinator")
            results[agent_name] = result
```

The execution phase iterates through the delegation plan, routing each subtask to the appropriate specialized agent and collecting their results.

```python
    # Step 4: Integrate results
    final_result = await self._integrate_agent_results(task, results)
    
    return {
        "original_task": task,
        "delegation_plan": delegation_plan,
        "agent_results": results,
        "integrated_result": final_result
    }
```

The final integration step combines individual agent results into a cohesive response that addresses the original complex task comprehensively.

Task analysis uses the LLM to understand which specialized agents are needed:

Task analysis uses the LLM to understand which specialized agents are needed:

```python
async def _analyze_task_requirements(self, task: str) -> Dict[str, Any]:
    """Analyze what types of agents are needed for this task"""
    analysis_prompt = f"""
    Analyze this task and determine what types of specialized agents would be needed:
    Task: {task}
    
    Available agent types: {list(self.agents.keys())}
```

The analysis provides context about available agents and requests specific justifications:

```python
    For each needed agent type, specify:
    1. What specific subtask they should handle
    2. Why this agent type is appropriate
    
    Return analysis in structured format.
    """
    
    # This would use an LLM to analyze - simplified for example
    return {"required_agents": list(self.agents.keys())[:2]}  # Simplified
```

The analysis provides context about available agents and requests specific justifications for agent selection, ensuring intelligent task distribution rather than random assignment.

---

## 📝 Multiple Choice Test - Module A

Test your understanding of advanced agent patterns:

**Question 1:** What is the key mechanism that prevents infinite loops in reflection agents?  
A) Memory limitations  
B) Maximum iteration limits with satisfactory conditions  
C) Network timeouts  
D) User intervention  

**Question 2:** In multi-step planning, what is the primary purpose of dependency management?  
A) Reducing memory usage  
B) Ensuring steps execute in the correct order  
C) Speeding up execution  
D) Simplifying code structure  

**Question 3:** What does the planning agent's `_parse_plan_text` method accomplish?  
A) Generates new plans from scratch  
B) Converts LLM-generated text into structured PlanStep objects  
C) Executes individual plan steps  
D) Validates plan correctness  

**Question 4:** In multi-agent orchestration, what information is stored in communication patterns?  
A) Complete message history with full content  
B) Summarized message data with sender, recipient, and timestamp  
C) Only error messages  
D) Agent performance metrics  

**Question 5:** What is the three-phase approach used in collaborative task management?  
A) Planning, execution, validation  
B) Analysis, delegation, integration  
C) Task analysis, delegation plan creation, plan execution  
D) Registration, routing, completion

**🗂️ View Test Solutions →** Complete answers and explanations available in `Session1_ModuleA_Test_Solutions.md`

---

## 🎯 Module Summary

You've now mastered advanced agent patterns including:

✅ **Reflection Agents**: Implemented self-improvement through iterative critique and refinement  
✅ **Multi-Step Planning**: Built systems that decompose complex tasks into executable plans  
✅ **Multi-Agent Orchestration**: Created coordination systems for specialized agent collaboration  
✅ **Self-Improvement Mechanisms**: Designed agents that enhance their performance over time

---

## 🧭 Navigation & Quick Start

**Related Modules:**

- **Core Session:** [Session 1 - Bare Metal Agents](Session1_Bare_Metal_Agents.md)
- **Module B:** [Performance Optimization](Session1_ModuleB_Performance_Optimization.md)
- **Module C:** [Complex State Management](Session1_ModuleC_Complex_State_Management.md)

**🗂️ Code Files:** All examples use files in `src/session1/`

- `reflection_agent.py` - Self-improving reflection agents
- `react_agent.py` - Multi-step planning implementation (includes planning patterns)
- `multi_agent_system.py` - Multi-agent coordination system

**🚀 Quick Start:** Run `cd src/session1 && python demo_runner.py` to see implementations

**Next:** [Session 2 - LangChain Foundations](Session2_LangChain_Foundations.md) →
