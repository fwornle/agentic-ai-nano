# 📝 Session 3: Multi-Agent Implementation Guide

*Prerequisites: Complete [🎯 Session 3 Hub - Observer Path](Session3_LangGraph_Multi_Agent_Workflows.md)*

**Estimated Time**: 1.5-2 hours
**Focus**: Building working multi-agent systems with proper coordination

## Part 2: Building Specialized Data Processing Teams

Moving from simple workflows to sophisticated data processing teams, we now create specialists who can work together on complex data problems requiring multiple types of processing expertise.

### Agent Node Creation

Creating specialized agent nodes that encapsulate specific data processing capabilities and domain expertise:

**File**: [`src/session3/hierarchical_team.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/hierarchical_team.py) - Multi-agent team setup

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import tool

# Create specialized agents

class DataProfilingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
```

Specialized data agents encapsulate specific capabilities and LLM configurations - like hiring a creative data analyst who excels at generating insights from complex datasets. Higher temperature for exploratory data analysis:

```python
    def profiling_node(self, state: WorkflowState):
        """Specialized data profiling agent"""
        data_batch = state.get("data_batch", "")
        profiling_result = self.llm.invoke(f"Profile this data batch: {data_batch}")

        return {
            **state,
            "profiling_results": profiling_result.content,
            "messages": state["messages"] + [f"Data profiling: {profiling_result.content[:100]}..."]
        }
```

Data quality agents use lower temperature for focused, systematic validation - like having a different specialist who excels at methodical data quality assessment and anomaly detection:

```python
class DataQualityAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    def quality_check_node(self, state: WorkflowState):
        """Specialized data quality assessment agent"""
        data = state.get("profiling_results", "")
        quality_check = self.llm.invoke(f"Assess data quality for: {data}")

        return {
            **state,
            "quality_results": quality_check.content,
            "messages": state["messages"] + [f"Quality check: {quality_check.content[:100]}..."]
        }
```

### Message Passing

Communication between data agents - enabling sophisticated coordination patterns that mirror how high-performing data engineering teams share processing state and results:

**File**: [`src/session3/state_merging.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/state_merging.py) - State management patterns

```python
def pipeline_coordinator_node(state: WorkflowState):
    """Coordinates between different data processing agents"""
    # Collect results from previous agents
    profiling_data = state.get("profiling_results", "")
    quality_data = state.get("quality_results", "")

    # Merge and coordinate
    coordination_result = f"Pipeline coordination: Profiling={len(profiling_data)} chars, Quality={len(quality_data)} chars"

    return {
        **state,
        "coordination_summary": coordination_result,
        "messages": state["messages"] + [coordination_result]
    }
```

The pipeline coordinator aggregates results from multiple data processing agents and provides final synthesis - like a data pipeline orchestrator who brings together insights from different processing stages into a coherent final data product:

```python

# Enhanced workflow with coordination

workflow.add_node("coordinator", pipeline_coordinator_node)
workflow.add_edge("quality_check", "coordinator")
workflow.add_edge("coordinator", END)
```

### Simple Workflow Patterns

Common orchestration patterns that solve real-world data processing collaboration challenges:

**File**: [`src/session3/simple_workflow.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/simple_workflow.py) - Complete workflow example

```python
def create_data_processing_workflow():
    """Create a simple data processing workflow"""
    workflow = StateGraph(WorkflowState)

    # Initialize agents
    profiling_agent = DataProfilingAgent()
    quality_agent = DataQualityAgent()

    # Add agent nodes
    workflow.add_node("profiling", profiling_agent.profiling_node)
    workflow.add_node("quality_check", quality_agent.quality_check_node)
    workflow.add_node("coordinator", pipeline_coordinator_node)
```

Defining the data workflow structure with entry point and edges - creating clear data flow paths that enable effective processing coordination:

```python
    # Define flow
    workflow.set_entry_point("profiling")
    workflow.add_edge("profiling", "quality_check")
    workflow.add_edge("quality_check", "coordinator")
    workflow.add_edge("coordinator", END)

    return workflow.compile()
```

Running the compiled workflow with initial state - launching your AI data processing team to work on a complex data pipeline task:

```python

# Usage

app = create_data_processing_workflow()
result = app.invoke({
    "data_batch": "customer_events_2024_Q1.parquet",
    "messages": [],
    "current_step": "profiling",
    "completed_tasks": []
})
```

### Error Handling

Robust workflow execution that handles the inevitable failures and complications of complex data processing teamwork:

```python
def safe_node_execution(node_func):
    """Wrapper for safe node execution"""
    def wrapper(state: WorkflowState):
        try:
            return node_func(state)
        except Exception as e:
            return {
                **state,
                "error": f"Data processing node failed: {e}",
                "messages": state["messages"] + [f"Error: {e}"]
            }
    return wrapper

# Apply to nodes

workflow.add_node("profiling", safe_node_execution(profiling_agent.profiling_node))
```

## Part 3: State Management & Flow Control - The Intelligence Behind Data Pipeline Orchestration

Moving beyond simple data handoffs to sophisticated coordination patterns that adapt to real-time data characteristics and handle complex decision trees in streaming environments.

### State Schemas

Defining and managing workflow state with the sophistication needed for production data processing applications:

**File**: [`src/session3/advanced_routing.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/advanced_routing.py) - State management examples

```python
from typing import TypedDict, Optional, List, Dict, Any

class AdvancedWorkflowState(TypedDict):
    # Core state
    messages: List[str]
    current_step: str

    # Data flow
    input_data: Optional[Dict[str, Any]]
    profiling_results: Optional[str]
    quality_results: Optional[str]
    final_output: Optional[str]
```

Advanced state includes data flow tracking for robust execution - like maintaining detailed data lineage records that enable sophisticated pipeline management and debugging:

```python
    # Control flow
    completed_tasks: List[str]
    failed_tasks: List[str]
    retry_count: int

    # Metadata
    workflow_id: str
    start_time: str
    last_updated: str
```

Utility function for maintaining state metadata throughout data processing execution - ensuring complete auditability and debugging capability for compliance requirements:

```python
def update_state_metadata(state: AdvancedWorkflowState) -> AdvancedWorkflowState:
    """Update state metadata"""
    from datetime import datetime
    return {
        **state,
        "last_updated": datetime.now().isoformat()
    }
```

### Conditional Routing

Dynamic workflow decisions that mirror how data engineering teams adapt their processing approach based on intermediate data characteristics and quality metrics:

**File**: [`src/session3/decision_logic.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/decision_logic.py) - Decision-making logic

```python
def route_after_profiling(state: AdvancedWorkflowState) -> str:
    """Decide next step after data profiling"""
    profiling_quality = len(state.get("profiling_results", ""))

    if profiling_quality < 100:
        return "retry_profiling"
    elif profiling_quality > 1000:
        return "detailed_quality_check"
    else:
        return "standard_quality_check"
```

Conditional routing enables dynamic workflow decisions based on intermediate data processing results - like having an intelligent pipeline manager who adjusts the data processing approach based on what the profiling discovers about data characteristics:

```python
def route_after_quality_check(state: AdvancedWorkflowState) -> str:
    """Decide if data pipeline processing is complete"""
    quality_results = state.get("quality_results", "")

    if "data quality issues" in quality_results.lower():
        return "additional_cleansing"
    elif "quality approved" in quality_results.lower():
        return END
    else:
        return "manual_review"
```

Implementing conditional routing in the workflow - creating intelligent coordination that adapts to data quality conditions:

```python

# Add conditional routing

from langgraph.graph import Condition

workflow.add_conditional_edges(
    "profiling",
    route_after_profiling,
    {
        "retry_profiling": "profiling",
        "detailed_quality_check": "detailed_quality_check",
        "standard_quality_check": "quality_check"
    }
)
```

### Error Recovery

Handling data processing failures gracefully - the difference between brittle data pipelines that break and resilient systems that adapt to data anomalies:

```python
def error_recovery_node(state: AdvancedWorkflowState):
    """Handle data processing workflow errors"""
    error_count = state.get("retry_count", 0)

    if error_count < 3:
        return {
            **state,
            "retry_count": error_count + 1,
            "current_step": "retry",
            "messages": state["messages"] + [f"Retrying data processing (attempt {error_count + 1})"]
        }
```

Graceful failure handling with maximum retry limits - preventing infinite loops while maximizing the chance of data processing success:

```python
    else:
        return {
            **state,
            "current_step": "failed",
            "final_output": "Data processing workflow failed after maximum retries",
            "messages": state["messages"] + ["Data workflow failed - maximum retries exceeded"]
        }
```

## Part 4: Integration & Testing - Validating Your Intelligent Data Processing Team

Now we verify that our multi-agent data processing systems work correctly in the real world, with comprehensive testing that ensures reliability under various data conditions.

### Workflow Validation

**File**: [`src/session3/test_workflows.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/test_workflows.py) - Complete test suite

```python
def test_simple_data_workflow():
    """Test basic data processing workflow functionality"""
    app = create_data_processing_workflow()

    result = app.invoke({
        "data_batch": "test_dataset.parquet",
        "messages": [],
        "current_step": "test",
        "completed_tasks": []
    })

    assert "profiling_results" in result
    assert "quality_results" in result
    assert len(result["messages"]) > 0
    print("✅ Data processing workflow test passed!")
```

Executing the test to verify data workflow functionality - ensuring your AI data processing team actually works together as designed:

```python

# Run test

test_simple_data_workflow()
```

### Basic Testing Patterns

Comprehensive validation approaches that ensure your multi-agent data processing systems work reliably:

```bash

# Run workflow examples

cd src/session3
python simple_workflow.py
python hierarchical_team.py
python -m pytest test_workflows.py
```

## Validation

### Quick Implementation Exercise

Test your understanding with these complete working examples:

🗂️ **Exercise Files**:

- [`src/session3/simple_workflow.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/simple_workflow.py) - Complete working example
- [`src/session3/test_workflows.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/test_workflows.py) - Test your understanding

```bash
# Try the examples:

cd src/session3
python simple_workflow.py          # Basic data workflow
python hierarchical_team.py        # Multi-agent data coordination
```

---

## 🧭 Navigation

**Previous:** [Session 2 - Implementation →](Session2_*.md)  
**Next:** [Session 4 - Team Orchestration →](Session4_*.md)

---
