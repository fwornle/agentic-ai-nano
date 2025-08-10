# src/session3/advanced_routing.py
"""
Advanced routing patterns for LangGraph workflows.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
from decision_logic import route_by_task_type


def analyze_task_requirements(state: AgentState) -> AgentState:
    """Analyze task to determine requirements"""
    current_task = state["current_task"]
    
    # Analyze task complexity and requirements
    task_analysis = {
        "complexity": "medium" if len(current_task) > 100 else "simple",
        "domain": determine_domain(current_task),
        "estimated_time": estimate_time(current_task),
        "required_tools": identify_required_tools(current_task)
    }
    
    updated_results = state["results"].copy()
    updated_results["task_analysis"] = task_analysis
    
    return {
        "results": updated_results,
        "current_task": current_task
    }


def handle_math_tasks(state: AgentState) -> AgentState:
    """Handle mathematical calculations and analysis"""
    current_task = state["current_task"]
    
    # Simulate math processing
    math_result = f"Mathematical analysis of: {current_task}"
    
    updated_results = state["results"].copy()
    updated_results["math_result"] = math_result
    updated_results["specialist_used"] = "math_specialist"
    
    return {
        "results": updated_results,
        "current_task": "math_processing_complete"
    }


def handle_research_tasks(state: AgentState) -> AgentState:
    """Handle research and information gathering"""
    current_task = state["current_task"]
    
    # Simulate research processing
    research_result = f"Research findings for: {current_task}"
    
    updated_results = state["results"].copy()
    updated_results["research_result"] = research_result
    updated_results["specialist_used"] = "research_specialist"
    
    return {
        "results": updated_results,
        "current_task": "research_processing_complete"
    }


def handle_creative_tasks(state: AgentState) -> AgentState:
    """Handle creative and artistic tasks"""
    current_task = state["current_task"]
    
    # Simulate creative processing
    creative_result = f"Creative interpretation of: {current_task}"
    
    updated_results = state["results"].copy()
    updated_results["creative_result"] = creative_result
    updated_results["specialist_used"] = "creative_specialist"
    
    return {
        "results": updated_results,
        "current_task": "creative_processing_complete"
    }


def check_output_quality(state: AgentState) -> AgentState:
    """Quality control node with feedback loop"""
    
    # Get the latest result
    results = state["results"]
    latest_result = list(results.values())[-1] if results else ""
    
    # Simple quality metrics
    quality_score = calculate_quality_score(latest_result)
    
    # Update state with quality assessment
    updated_results = results.copy()
    updated_results["quality_score"] = quality_score
    updated_results["needs_revision"] = quality_score < 0.7
    
    return {
        "results": updated_results,
        "iteration_count": state.get("iteration_count", 0) + 1
    }


def create_intelligent_routing_workflow():
    """Workflow with intelligent task routing"""
    
    workflow = StateGraph(AgentState)
    
    # Add specialized agent nodes
    workflow.add_node("task_analyzer", analyze_task_requirements)
    workflow.add_node("math_specialist", handle_math_tasks)
    workflow.add_node("research_specialist", handle_research_tasks)
    workflow.add_node("creative_specialist", handle_creative_tasks)
    workflow.add_node("quality_checker", check_output_quality)
    
    # Start with task analysis
    workflow.set_entry_point("task_analyzer")
    
    # Route based on task type
    workflow.add_conditional_edges(
        "task_analyzer",
        route_by_task_type,
        {
            "math_specialist": "math_specialist",
            "research_specialist": "research_specialist", 
            "creative_specialist": "creative_specialist"
        }
    )
    
    # All specialists go to quality check
    workflow.add_edge("math_specialist", "quality_checker")
    workflow.add_edge("research_specialist", "quality_checker")
    workflow.add_edge("creative_specialist", "quality_checker")
    
    return workflow.compile()


# Helper functions
def determine_domain(task: str) -> str:
    """Determine the domain of a task"""
    task_lower = task.lower()
    if any(word in task_lower for word in ["calculate", "equation", "number", "math"]):
        return "mathematics"
    elif any(word in task_lower for word in ["research", "find", "information", "data"]):
        return "research"
    elif any(word in task_lower for word in ["create", "design", "write", "artistic"]):
        return "creative"
    else:
        return "general"


def estimate_time(task: str) -> str:
    """Estimate time required for task"""
    if len(task) < 50:
        return "short"
    elif len(task) < 200:
        return "medium"
    else:
        return "long"


def identify_required_tools(task: str) -> list:
    """Identify tools needed for task"""
    tools = []
    task_lower = task.lower()
    
    if "calculate" in task_lower:
        tools.append("calculator")
    if "research" in task_lower:
        tools.append("search_engine")
    if "write" in task_lower:
        tools.append("text_generator")
    
    return tools


def calculate_quality_score(result: str) -> float:
    """Calculate quality score for a result"""
    if not result:
        return 0.0
    
    # Simple quality metrics
    score = 0.5  # Base score
    
    if len(result) > 100:
        score += 0.2  # Good length
    if "analysis" in result.lower():
        score += 0.2  # Contains analysis
    if result.count(".") > 2:
        score += 0.1  # Well structured
    
    return min(score, 1.0)  # Cap at 1.0