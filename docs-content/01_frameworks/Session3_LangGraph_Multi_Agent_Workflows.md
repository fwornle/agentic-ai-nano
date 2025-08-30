# Session 3: LangGraph Multi-Agent Workflows - Orchestrating Distributed Data Processing

When your petabyte-scale data lake spans multiple clouds and processing terabytes of streaming data requires coordinated work from validation agents, transformation engines, and quality monitors - rigid sequential pipelines become the bottleneck that kills performance. A single delayed data validation step can cascade through your entire pipeline, blocking critical downstream analytics and causing SLA violations that impact business decisions.

LangGraph transforms your data processing agents from sequential bottlenecks into intelligent orchestration networks where data validation, transformation, aggregation, and quality assurance work in parallel based on data characteristics, resource availability, and processing priorities in real-time.

In this session, you'll build sophisticated multi-agent data processing systems that mirror modern distributed streaming architectures - with parallel execution, conditional routing, and adaptive resource allocation optimized for large-scale data workflows.

## Learning Outcomes

By the end of this session, you will be able to:
- **Design** and implement graph-based data pipeline orchestration using LangGraph
- **Build** complex multi-agent systems with stateful coordination for data processing workflows
- **Apply** state management patterns for distributed data streaming coordination
- **Implement** production-grade tracing and observability for multi-agent data pipelines
- **Evaluate** when to choose graph-based architectures over simple chain-based data flows

## The Graph Revolution: Beyond Linear Data Pipelines

Unlike sequential data pipelines where validation always precedes transformation which always precedes aggregation, LangGraph uses directed graphs with nodes (specialized processors) connected by conditional edges (intelligent routing). This architecture provides stateful coordination, dynamic decision-making, and production-grade observability for complex data processing workflows.

Think of it as the difference between traditional ETL pipelines and modern stream processing architectures - sometimes data quality validation needs direct input from schema inference, sometimes ML feature engineering requires simultaneous input from multiple data sources, and sometimes you need to route back to data ingestion when quality thresholds aren't met.

## Quick Start

Run `cd src/session3 && python simple_workflow.py` to see LangGraph orchestrating multiple data processing agents like a conductor leading a data orchestra.

Code files are located in [`src/session3/`](https://github.com/fwornle/agentic-ai-nano/tree/main/docs-content/01_frameworks/src/session3).

## Part 1: Graph Architecture Overview

### Graph-Based Workflow Foundation

Building on our LangChain foundations, LangGraph transforms multi-agent data systems from linear pipelines into sophisticated graph structures that mirror real-world distributed data processing:

**File**: [`src/session3/langgraph_basics.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/langgraph_basics.py) - Core workflow setup

### Production-Grade State Management

LangGraph's StateGraph provides the foundation for distributed data processing coordination, solving the critical challenge of how multiple processing agents can work together while maintaining data lineage and pipeline observability:

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, List, Optional

# Data processing workflow state with comprehensive tracking

class WorkflowState(TypedDict):
    messages: List[str]           # Processing status updates
    current_step: str            # Active processing stage  
    completed_tasks: List[str]   # Processing audit trail
    data_context: dict          # Shared processing metadata
    error_state: Optional[str]  # Processing failure handling
    batch_id: str               # Current data batch identifier
    resource_usage: dict        # Cluster resource tracking
```

This state structure provides the observability and error handling required for production data processing - think of it as the shared processing context that all data agents can access and update. Each field serves a specific purpose in maintaining pipeline integrity and enabling debugging when data processing issues occur in your distributed system.

```python

# Initialize the data processing workflow graph

workflow = StateGraph(WorkflowState)
```

### Core Architecture Principles:

Understanding these principles is like grasping the fundamental laws that govern distributed data processing systems:

1. **Directed Graph Structure**: Nodes (specialized processors) connected by conditional edges (intelligent routing) - like having clear data flow paths between ingestion, validation, transformation, and storage layers
2. **Immutable State Flow**: State evolves through nodes without mutation, ensuring data lineage traceability - every processing step is recorded and auditable for compliance and debugging
3. **Conditional Decision Points**: Dynamic routing based on data characteristics and resource availability - like having intelligent load balancers that route data batches to optimal processing clusters

### Nodes and Edges

Building blocks of LangGraph workflows - the data processing agents (nodes) and their coordination patterns (edges):

**File**: [`src/session3/workflow_nodes.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session3/workflow_nodes.py) - Node implementations

```python
def data_validation_node(state: WorkflowState):
    """Data quality validation phase of the processing workflow"""
    print(f"🔍 Validating: {state['current_step']} for batch {state['batch_id']}")
    # Add data validation logic here
    return {
        **state,
        "messages": state["messages"] + ["Data validation completed"],
        "completed_tasks": state["completed_tasks"] + ["validation"]
    }
```

Each node function receives the current processing state and returns an updated state - like a specialized data processing service receiving a data batch, performing its transformation, and updating the pipeline status. The `**state` syntax preserves existing processing context while updating specific fields, ensuring data lineage is never lost in the handoff.

```python
def transformation_node(state: WorkflowState):
    """Data transformation phase of the workflow"""
    print(f"📊 Transforming: Processing validated data batch")
    return {
        **state,
        "messages": state["messages"] + ["Data transformation completed"],
        "completed_tasks": state["completed_tasks"] + ["transformation"]
    }
```

Now we connect these nodes to create our data processing structure - establishing the coordination patterns that enable effective data pipeline orchestration:

```python

# Add nodes to workflow

workflow.add_node("validation", data_validation_node)
workflow.add_node("transformation", transformation_node)
workflow.add_edge("validation", "transformation")
```

### Basic Graph Creation

Putting it all together into a functioning multi-agent data processing system:

```python

# Set entry point and compile

workflow.set_entry_point("validation")
workflow.add_edge("transformation", END)

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

## Part 2: Multi-Agent Orchestration - Building Specialized Data Processing Teams

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

---

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

---

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

---

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

## 📝 Multiple Choice Test - Session 3

Test your understanding of LangGraph workflows and multi-agent coordination:

**Question 1:** What is the primary advantage of LangGraph over sequential data pipeline agents?  
A) Better performance  
B) Lower cost  
C) Graph-based workflows with conditional routing and parallel execution  
D) Simpler implementation  

**Question 2:** In LangGraph, what component defines the data that flows between nodes?  
A) State (TypedDict)  
B) Edges  
C) Memory  
D) Tools  

**Question 3:** What determines the flow between nodes in a LangGraph workflow?  
A) Random selection  
B) User input  
C) Sequential execution only  
D) Conditional edges and decision functions  

**Question 4:** How does LangGraph handle parallel agent execution?  
A) Through parallel nodes with state merging  
B) It doesn't support parallel execution  
C) Through external orchestration  
D) Using threading only  

**Question 5:** What happens when a LangGraph node updates state?  
A) State is reset to default  
B) The entire state is replaced  
C) Previous state is archived  
D) Only specified fields are updated/merged  

[**🗂️ View Test Solutions →**](Session3_Test_Solutions.md)

---

## 🧭 Navigation

**Previous:** [Session 2 - LangChain Foundations](Session2_LangChain_Foundations.md)

**Optional Deep Dive Modules:**

- 🔬 **[Module A: Advanced Orchestration Patterns](Session3_ModuleA_Advanced_Orchestration_Patterns.md)** - Complex workflow coordination & dynamic agent generation for large-scale data processing
- 🏭 **[Module B: Enterprise State Management](Session3_ModuleB_Enterprise_State_Management.md)** - Production state handling & sophisticated routing for enterprise data pipelines

**Next:** [Session 4 - CrewAI Team Orchestration →](Session4_CrewAI_Team_Orchestration.md)

---