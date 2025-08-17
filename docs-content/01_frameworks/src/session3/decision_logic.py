# src/session3/decision_logic.py
"""
Decision functions for conditional routing in LangGraph workflows.
"""

from langgraph_basics import AgentState


def should_continue_analysis(state: AgentState) -> str:
    """Decide whether to continue, retry, or end"""
    
    analysis_result = state["results"].get("analysis", "")
    iteration_count = state.get("iteration_count", 0)
    
    # Check quality of analysis
    if "insufficient data" in analysis_result.lower():
        if iteration_count < 3:  # Max 3 retries
            return "retry"
        else:
            return "end"  # Give up after 3 tries
    
    # Check if analysis is complete
    if len(analysis_result) < 50:  # Too brief
        return "continue"
    
    # Analysis looks good
    return "end"


def route_by_task_type(state: AgentState) -> str:
    """Route to different agents based on task type"""
    current_task = state["current_task"]
    
    if "math" in current_task.lower():
        return "math_specialist"
    elif "research" in current_task.lower():
        return "research_specialist"
    elif "creative" in current_task.lower():
        return "creative_specialist"
    else:
        return "general_agent"


def check_debate_completion(state: AgentState) -> str:
    """Determine if debate should continue"""
    iteration_count = state.get("iteration_count", 0)
    consensus_score = state["results"].get("consensus_score", 0)
    
    if consensus_score >= 0.8:
        return "consensus_reached"
    elif iteration_count >= 5:  # Max 5 debate rounds
        return "impasse"
    else:
        return "continue_debate"


def quality_decision(state: AgentState) -> str:
    """Decide if work needs revision"""
    quality_score = state["results"].get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)
    
    if quality_score >= 0.8:
        return "approved"
    elif iteration_count < 3:
        return "needs_revision"
    else:
        return "max_iterations_reached"


def revision_quality_check(state: AgentState) -> str:
    """Check if revision meets quality standards"""
    revision_score = state["results"].get("revision_score", 0)
    revision_count = state.get("revision_count", 0)
    
    if revision_score >= 0.9:
        return "ready_for_approval"
    elif revision_score >= 0.7:
        return "needs_more_review"
    elif revision_count >= 2:
        return "major_revision_needed"
    else:
        return "needs_more_review"