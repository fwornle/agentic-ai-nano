# Session 3: LangGraph Multi-Agent Workflows

## 🎯 Learning Navigation Hub
**Total Time Investment**: 70 minutes (Core) + 30-75 minutes (Optional)
**Your Learning Path**: Choose your engagement level

### Quick Start Guide
- **👀 Observer (40 min)**: Read concepts + examine workflow patterns
- **🙋‍♂️ Participant (70 min)**: Follow exercises + implement workflows
- **🛠️ Implementer (100 min)**: Build custom systems + explore advanced patterns

---

## 📋 SESSION OVERVIEW DASHBOARD

### Core Learning Track (70 minutes) - REQUIRED
| Section | Concept Load | Time | Skills |
|---------|--------------|------|--------|
| 🏗️ LangGraph Fundamentals | 3 concepts | 20 min | Understanding |
| 🤖 Multi-Agent Orchestration | 4 concepts | 25 min | Implementation |
| 🔄 State Management & Flow | 3 concepts | 20 min | Application |
| ✅ Integration & Testing | 2 concepts | 5 min | Verification |

### Optional Deep Dive Modules (Choose Your Adventure)
- 🔬 **[Module A: Advanced Orchestration Patterns](Session3_ModuleA_Advanced_Orchestration_Patterns.md)** (40 min) - Complex workflow coordination & dynamic agent generation
- 🏭 **[Module B: Enterprise State Management](Session3_ModuleB_Enterprise_State_Management.md)** (35 min) - Production state handling & sophisticated routing

**🗂️ Code Files**: All examples use files in [`src/session3/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session3)
**🚀 Quick Start**: Run `cd src/session3 && python simple_workflow.py` to see LangGraph in action

---

## 🧭 CORE SECTION (Required - 70 minutes)

### Part 1: LangGraph Fundamentals (20 minutes)
**Cognitive Load**: 3 new concepts
**Learning Mode**: Conceptual Understanding

#### Graph-Based Workflows (8 minutes)
LangGraph enables sophisticated agent workflows through graph structures:

🗂️ **File**: [`src/session3/langgraph_basics.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/langgraph_basics.py) - Core workflow setup

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, List

# Define workflow state
class WorkflowState(TypedDict):
    messages: List[str]
    current_step: str
    completed_tasks: List[str]

# Create the workflow graph
workflow = StateGraph(WorkflowState)
```

**Key Concepts:**
1. **Graph Structure**: Nodes (agents/functions) connected by edges (flow control)
2. **State Management**: Shared state that flows through the entire workflow
3. **Conditional Routing**: Dynamic decision-making about next steps

#### Nodes and Edges (7 minutes)
Building blocks of LangGraph workflows:

🗂️ **File**: [`src/session3/workflow_nodes.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/workflow_nodes.py) - Node implementations

```python
def research_node(state: WorkflowState):
    """Research phase of the workflow"""
    print(f"🔍 Research: {state['current_step']}")
    # Add research logic here
    return {
        **state,
        "messages": state["messages"] + ["Research completed"],
        "completed_tasks": state["completed_tasks"] + ["research"]
    }

def analysis_node(state: WorkflowState):
    """Analysis phase of the workflow"""
    print(f"📊 Analysis: Processing research results")
    return {
        **state,
        "messages": state["messages"] + ["Analysis completed"],
        "completed_tasks": state["completed_tasks"] + ["analysis"]
    }

# Add nodes to workflow
workflow.add_node("research", research_node)
workflow.add_node("analysis", analysis_node)
workflow.add_edge("research", "analysis")
```

#### Basic Graph Creation (5 minutes)
Putting it all together:

```python
# Set entry point and compile
workflow.set_entry_point("research")
workflow.add_edge("analysis", END)

# Compile the workflow
app = workflow.compile()

# Run the workflow
result = app.invoke({
    "messages": [],
    "current_step": "start",
    "completed_tasks": []
})
```

---

### Part 2: Multi-Agent Orchestration (25 minutes)
**Cognitive Load**: 4 new concepts
**Learning Mode**: Implementation & Coordination

#### Agent Node Creation (8 minutes)
Creating specialized agent nodes:

🗂️ **File**: [`src/session3/hierarchical_team.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/hierarchical_team.py) - Multi-agent team setup

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import tool

# Create specialized agents
class ResearchAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        
    def research_node(self, state: WorkflowState):
        """Specialized research agent"""
        query = state.get("query", "")
        research_result = self.llm.invoke(f"Research this topic: {query}")
        
        return {
            **state,
            "research_results": research_result.content,
            "messages": state["messages"] + [f"Research: {research_result.content[:100]}..."]
        }

class AnalysisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        
    def analysis_node(self, state: WorkflowState):
        """Specialized analysis agent"""
        data = state.get("research_results", "")
        analysis = self.llm.invoke(f"Analyze this data: {data}")
        
        return {
            **state,
            "analysis_results": analysis.content,
            "messages": state["messages"] + [f"Analysis: {analysis.content[:100]}..."]
        }
```

#### Message Passing (7 minutes)
Communication between agents:

🗂️ **File**: [`src/session3/state_merging.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/state_merging.py) - State management patterns

```python
def coordinator_node(state: WorkflowState):
    """Coordinates between different agents"""
    # Collect results from previous agents
    research_data = state.get("research_results", "")
    analysis_data = state.get("analysis_results", "")
    
    # Merge and coordinate
    coordination_result = f"Coordination: Research={len(research_data)} chars, Analysis={len(analysis_data)} chars"
    
    return {
        **state,
        "coordination_summary": coordination_result,
        "messages": state["messages"] + [coordination_result]
    }

# Enhanced workflow with coordination
workflow.add_node("coordinator", coordinator_node)
workflow.add_edge("analysis", "coordinator")
workflow.add_edge("coordinator", END)
```

#### Simple Workflow Patterns (6 minutes)
Common orchestration patterns:

🗂️ **File**: [`src/session3/simple_workflow.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/simple_workflow.py) - Complete workflow example

```python
def create_research_workflow():
    """Create a simple research workflow"""
    workflow = StateGraph(WorkflowState)
    
    # Initialize agents
    research_agent = ResearchAgent()
    analysis_agent = AnalysisAgent()
    
    # Add agent nodes
    workflow.add_node("research", research_agent.research_node)
    workflow.add_node("analysis", analysis_agent.analysis_node)
    workflow.add_node("coordinator", coordinator_node)
    
    # Define flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", "coordinator")
    workflow.add_edge("coordinator", END)
    
    return workflow.compile()

# Usage
app = create_research_workflow()
result = app.invoke({
    "query": "Benefits of renewable energy",
    "messages": [],
    "current_step": "research",
    "completed_tasks": []
})
```

#### Error Handling (4 minutes)
Robust workflow execution:

```python
def safe_node_execution(node_func):
    """Wrapper for safe node execution"""
    def wrapper(state: WorkflowState):
        try:
            return node_func(state)
        except Exception as e:
            return {
                **state,
                "error": f"Node failed: {e}",
                "messages": state["messages"] + [f"Error: {e}"]
            }
    return wrapper

# Apply to nodes
workflow.add_node("research", safe_node_execution(research_agent.research_node))
```

---

### Part 3: State Management & Flow Control (20 minutes)
**Cognitive Load**: 3 new concepts
**Learning Mode**: Application & Control

#### State Schemas (8 minutes)
Defining and managing workflow state:

🗂️ **File**: [`src/session3/advanced_routing.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/advanced_routing.py) - State management examples

```python
from typing import TypedDict, Optional, List, Dict, Any

class AdvancedWorkflowState(TypedDict):
    # Core state
    messages: List[str]
    current_step: str
    
    # Data flow
    input_data: Optional[Dict[str, Any]]
    research_results: Optional[str]
    analysis_results: Optional[str]
    final_output: Optional[str]
    
    # Control flow
    completed_tasks: List[str]
    failed_tasks: List[str]
    retry_count: int
    
    # Metadata
    workflow_id: str
    start_time: str
    last_updated: str

def update_state_metadata(state: AdvancedWorkflowState) -> AdvancedWorkflowState:
    """Update state metadata"""
    from datetime import datetime
    return {
        **state,
        "last_updated": datetime.now().isoformat()
    }
```

#### Conditional Routing (7 minutes)
Dynamic workflow decisions:

🗂️ **File**: [`src/session3/decision_logic.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/decision_logic.py) - Decision-making logic

```python
def route_after_research(state: AdvancedWorkflowState) -> str:
    """Decide next step after research"""
    research_quality = len(state.get("research_results", ""))
    
    if research_quality < 100:
        return "retry_research"
    elif research_quality > 1000:
        return "detailed_analysis"
    else:
        return "standard_analysis"

def route_after_analysis(state: AdvancedWorkflowState) -> str:
    """Decide if workflow is complete"""
    analysis_results = state.get("analysis_results", "")
    
    if "insufficient data" in analysis_results.lower():
        return "additional_research"
    elif "complete" in analysis_results.lower():
        return END
    else:
        return "review"

# Add conditional routing
from langgraph.graph import Condition

workflow.add_conditional_edges(
    "research",
    route_after_research,
    {
        "retry_research": "research",
        "detailed_analysis": "detailed_analysis", 
        "standard_analysis": "analysis"
    }
)
```

#### Error Recovery (5 minutes)
Handling failures gracefully:

```python
def error_recovery_node(state: AdvancedWorkflowState):
    """Handle workflow errors"""
    error_count = state.get("retry_count", 0)
    
    if error_count < 3:
        return {
            **state,
            "retry_count": error_count + 1,
            "current_step": "retry",
            "messages": state["messages"] + [f"Retrying (attempt {error_count + 1})"]
        }
    else:
        return {
            **state,
            "current_step": "failed",
            "final_output": "Workflow failed after maximum retries",
            "messages": state["messages"] + ["Workflow failed - maximum retries exceeded"]
        }
```

---

### Part 4: Integration & Testing (5 minutes)
**Cognitive Load**: 2 new concepts
**Learning Mode**: Verification

#### Workflow Validation (3 minutes)
🗂️ **File**: [`src/session3/test_workflows.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/test_workflows.py) - Complete test suite

```python
def test_simple_workflow():
    """Test basic workflow functionality"""
    app = create_research_workflow()
    
    result = app.invoke({
        "query": "Test query",
        "messages": [],
        "current_step": "test",
        "completed_tasks": []
    })
    
    assert "research_results" in result
    assert "analysis_results" in result
    assert len(result["messages"]) > 0
    print("✅ Workflow test passed!")

# Run test
test_simple_workflow()
```

#### Basic Testing Patterns (2 minutes)
```bash
# Run workflow examples
cd src/session3
python simple_workflow.py
python hierarchical_team.py
python -m pytest test_workflows.py
```

---

## ✅ Core Section Validation (5 minutes)

### Quick Implementation Exercise
🗂️ **Exercise Files**: 
- [`src/session3/simple_workflow.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/simple_workflow.py) - Complete working example
- [`src/session3/test_workflows.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/test_workflows.py) - Test your understanding

```bash
# Try the examples:
cd src/session3
python simple_workflow.py          # Basic workflow
python hierarchical_team.py        # Multi-agent coordination
```

### Self-Assessment Checklist
- [ ] I understand LangGraph's graph-based approach
- [ ] I can create nodes and connect them with edges
- [ ] I can implement multi-agent coordination
- [ ] I understand state management and conditional routing
- [ ] I'm ready to explore optional modules or move to next session

**Next Session Prerequisites**: ✅ Core Section Complete
**Ready for**: Session 4: CrewAI Team Orchestration (team-based agents)

---

### 🧭 **Choose Your Next Path:**
- **[🔬 Module A: Advanced Orchestration Patterns →](Session3_ModuleA_Advanced_Orchestration_Patterns.md)** - Complex workflow coordination & dynamic agent generation
- **[🏭 Module B: Enterprise State Management →](Session3_ModuleB_Enterprise_State_Management.md)** - Production state handling & sophisticated routing
- **[📝 Test Your Knowledge →](Session3_Test_Solutions.md)** - Comprehensive quiz
- **[📖 Next Session: CrewAI Team Orchestration →](Session4_CrewAI_Team_Orchestration.md)** - Team-based agent frameworks

### 🎆 Complete Learning Path Options
**Sequential Learning**: Core → Module A → Module B  
**Production Focus**: Core → Module B  
**Advanced Patterns**: Core → Module A

---

## 📊 Progress Tracking

### Completion Status
- [ ] Core Section (70 min) - Essential for next session
- [ ] Module A: Advanced Orchestration (40 min)
- [ ] Module B: Enterprise State Management (35 min)

**🗂️ All Code Examples**: Available in [`src/session3/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session3) - 15 Python files with complete implementations!

---

## 📝 Multiple Choice Test - Session 3 (15 minutes)

Test your understanding of LangGraph workflows and multi-agent coordination.

### Question 1
**What is the primary advantage of LangGraph over sequential LangChain agents?**

A) Better performance  
B) Graph-based workflows with conditional routing and parallel execution  
C) Lower cost  
D) Simpler implementation  

### Question 2
**In LangGraph, what component defines the data that flows between nodes?**

A) Edges  
B) State (TypedDict)  
C) Tools  
D) Memory  

### Question 3
**What determines the flow between nodes in a LangGraph workflow?**

A) Sequential execution only  
B) Conditional edges and decision functions  
C) Random selection  
D) User input  

### Question 4
**How does LangGraph handle parallel agent execution?**

A) It doesn't support parallel execution  
B) Through parallel nodes with state merging  
C) Using threading only  
D) Through external orchestration  

### Question 5
**What happens when a LangGraph node updates state?**

A) The entire state is replaced  
B) Only specified fields are updated/merged  
C) State is reset to default  
D) Previous state is archived  

### Question 6
**In the debate pattern, what determines when the debate ends?**

A) Fixed number of rounds  
B) Consensus score and maximum iterations  
C) User intervention  
D) Random timing  

### Question 7
**What is the purpose of a decision function in conditional edges?**

A) To process user input  
B) To determine the next node based on current state  
C) To validate node outputs  
D) To handle errors  

### Question 8
**How does LangGraph's state merging work in parallel execution?**

A) Last node wins  
B) First node wins  
C) States are automatically merged based on field types  
D) Manual merging required  

### Question 9
**What makes LangGraph suitable for complex multi-agent workflows?**

A) Built-in LLM integration  
B) Graph architecture with conditional routing and state management  
C) Better error handling  
D) Faster execution speed  

### Question 10
**In the hierarchical team pattern, what role does the manager node play?**

A) Executes all tasks  
B) Coordinates worker agents and manages workflow state  
C) Stores all data  
D) Handles user interface  

---

**🗂️ View Test Solutions**: Complete answers and explanations available in `Session3_Test_Solutions.md`

**Success Criteria**: Score 8+ out of 10 to demonstrate mastery of LangGraph workflows.

---

## 🧭 Navigation

**Previous: [Session 2 - LangChain Foundations](Session2_LangChain_Foundations.md)**

**Optional Deep Dive Modules:**
- **[🔬 Module A: Advanced Orchestration Patterns](Session3_ModuleA_Advanced_Orchestration_Patterns.md)**
- **[🏭 Module B: Enterprise State Management](Session3_ModuleB_Enterprise_State_Management.md)**

**[📝 Test Your Knowledge: Session 3 Solutions](Session3_Test_Solutions.md)**

**[Next: Session 4 - CrewAI Team Orchestration →](Session4_CrewAI_Team_Orchestration.md)**