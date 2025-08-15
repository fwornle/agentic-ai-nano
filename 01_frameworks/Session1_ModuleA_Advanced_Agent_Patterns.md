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

**Response Improvement:**
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

🗂️ **File**: `src/session1/planning_agent.py` - Multi-step planning implementation

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

@dataclass
class PlanStep:
    id: str
    description: str
    dependencies: List[str]
    estimated_time: int
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    
class PlanningAgent(BaseAgent):
    """Agent that breaks down complex tasks into executable plans"""
    
    def __init__(self, name: str, llm_client):
        super().__init__(name, "Multi-step planning agent", llm_client)
        self.current_plan: Optional[List[PlanStep]] = None
        self.execution_history: List[Dict] = []
```

### Plan Generation

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
    
    plan_text = await self._call_llm(planning_prompt)
    
    # Parse the plan into PlanStep objects
    steps = self._parse_plan_text(plan_text)
    self.current_plan = steps
    
    return steps

def _parse_plan_text(self, plan_text: str) -> List[PlanStep]:
    """Parse LLM-generated plan into structured steps"""
    steps = []
    lines = plan_text.strip().split('\n')
    
    for i, line in enumerate(lines):
        if line.strip() and any(line.startswith(str(j)) for j in range(1, 20)):
            # Extract step information
            step_id = f"step_{i+1}"
            description = line.split('.', 1)[1].strip() if '.' in line else line.strip()
            
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

### Plan Execution Engine

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

def _find_next_executable_step(self, completed_steps: set) -> Optional[PlanStep]:
    """Find a step whose dependencies are satisfied"""
    for step in self.current_plan:
        if (step.status == TaskStatus.PENDING and 
            all(dep in completed_steps for dep in step.dependencies)):
            return step
    return None

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

### Collaborative Task Management

```python
async def delegate_complex_task(self, task: str) -> Dict[str, Any]:
    """Delegate complex task to appropriate specialized agents"""
    
    # Step 1: Analyze task to determine which agents are needed
    task_analysis = await self._analyze_task_requirements(task)
    
    # Step 2: Create delegation plan
    delegation_plan = self._create_delegation_plan(task_analysis)
    
    # Step 3: Execute delegation plan
    results = {}
    for agent_name, subtask in delegation_plan.items():
        if agent_name in self.agents:
            result = await self.route_message(subtask, agent_name, "coordinator")
            results[agent_name] = result
    
    # Step 4: Integrate results
    final_result = await self._integrate_agent_results(task, results)
    
    return {
        "original_task": task,
        "delegation_plan": delegation_plan,
        "agent_results": results,
        "integrated_result": final_result
    }

async def _analyze_task_requirements(self, task: str) -> Dict[str, Any]:
    """Analyze what types of agents are needed for this task"""
    analysis_prompt = f"""
    Analyze this task and determine what types of specialized agents would be needed:
    Task: {task}
    
    Available agent types: {list(self.agents.keys())}
    
    For each needed agent type, specify:
    1. What specific subtask they should handle
    2. Why this agent type is appropriate
    
    Return analysis in structured format.
    """
    
    # This would use an LLM to analyze - simplified for example
    return {"required_agents": list(self.agents.keys())[:2]}  # Simplified
```

---

## 🎯 Module Summary

You've now mastered advanced agent patterns including:

✅ **Reflection Agents**: Implemented self-improvement through iterative critique and refinement  
✅ **Multi-Step Planning**: Built systems that decompose complex tasks into executable plans  
✅ **Multi-Agent Orchestration**: Created coordination systems for specialized agent collaboration  
✅ **Self-Improvement Mechanisms**: Designed agents that enhance their performance over time

### Next Steps
- **Continue to Module B**: [Performance Optimization](Session1_ModuleB_Performance_Optimization.md) for speed & efficiency patterns
- **Continue to Module C**: [Complex State Management](Session1_ModuleC_Complex_State_Management.md) for advanced memory systems
- **Return to Core**: [Session 1 Main](Session1_Bare_Metal_Agents.md)
- **Advance to Session 2**: [LangChain Foundations](Session2_LangChain_Foundations.md)

---

**🗂️ Source Files for Module A:**
- `src/session1/reflection_agent.py` - Self-improving reflection agents
- `src/session1/planning_agent.py` - Multi-step planning implementation
- `src/session1/multi_agent_system.py` - Multi-agent coordination system