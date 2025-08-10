# src/session3/review_chain.py
"""
Review chain pattern for quality assurance and iterative improvement.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
from decision_logic import quality_decision, revision_quality_check


def create_initial_work(state: AgentState) -> AgentState:
    """Create initial work product"""
    current_task = state["current_task"]
    
    # Simulate initial work creation
    initial_work = f"Initial work product for: {current_task}"
    
    updated_results = state["results"].copy()
    updated_results["initial_work"] = initial_work
    updated_results["work_version"] = 1
    updated_results["creation_timestamp"] = "2024-01-01T10:00:00"
    
    return {
        "results": updated_results,
        "current_task": "initial_work_created"
    }


def review_work(state: AgentState) -> AgentState:
    """Review the work and provide feedback"""
    current_work = state["results"].get("initial_work", "")
    version = state["results"].get("work_version", 1)
    
    # Simulate review process
    review_feedback = {
        "version_reviewed": version,
        "quality_score": calculate_work_quality(current_work),
        "strengths": ["Clear structure", "Good analysis"],
        "weaknesses": ["Needs more detail", "Missing examples"],
        "recommendations": ["Add specific examples", "Expand conclusion"],
        "reviewer_confidence": 0.8
    }
    
    updated_results = state["results"].copy()
    updated_results["review_feedback"] = review_feedback
    updated_results["quality_score"] = review_feedback["quality_score"]
    
    return {
        "results": updated_results,
        "current_task": "work_reviewed"
    }


def revise_work(state: AgentState) -> AgentState:
    """Revise work based on feedback"""
    review_feedback = state["results"].get("review_feedback", {})
    current_version = state["results"].get("work_version", 1)
    
    # Simulate revision process
    revised_work = f"Revised work (v{current_version + 1}) incorporating feedback"
    
    # Calculate improvement from revision
    original_quality = review_feedback.get("quality_score", 0.5)
    revision_improvement = 0.2  # Assume 20% improvement
    new_quality = min(original_quality + revision_improvement, 1.0)
    
    updated_results = state["results"].copy()
    updated_results["revised_work"] = revised_work
    updated_results["work_version"] = current_version + 1
    updated_results["revision_score"] = new_quality
    updated_results["revision_count"] = state["results"].get("revision_count", 0) + 1
    
    return {
        "results": updated_results,
        "current_task": "work_revised"
    }


def final_approval(state: AgentState) -> AgentState:
    """Final approval of the work"""
    final_version = state["results"].get("work_version", 1)
    final_quality = state["results"].get("revision_score", 0.5)
    revision_count = state["results"].get("revision_count", 0)
    
    approval_decision = {
        "approved": final_quality >= 0.8,
        "final_version": final_version,
        "final_quality_score": final_quality,
        "total_revisions": revision_count,
        "approval_timestamp": "2024-01-01T15:00:00",
        "approval_notes": get_approval_notes(final_quality, revision_count)
    }
    
    updated_results = state["results"].copy()
    updated_results["final_approval"] = approval_decision
    
    return {
        "results": updated_results,
        "current_task": "approval_complete"
    }


def escalate_for_review(state: AgentState) -> AgentState:
    """Escalate work for higher-level review"""
    current_quality = state["results"].get("revision_score", 0.5)
    revision_count = state["results"].get("revision_count", 0)
    
    escalation_info = {
        "reason": "Quality standards not met after multiple revisions",
        "current_quality": current_quality,
        "revisions_attempted": revision_count,
        "escalation_timestamp": "2024-01-01T16:00:00",
        "recommended_action": "Senior review required"
    }
    
    updated_results = state["results"].copy()
    updated_results["escalation"] = escalation_info
    
    return {
        "results": updated_results,
        "current_task": "escalated_for_review"
    }


def create_review_chain_workflow():
    """Create review chain workflow with quality gates"""
    
    workflow = StateGraph(AgentState)
    
    # Add workflow nodes
    workflow.add_node("creator", create_initial_work)
    workflow.add_node("reviewer", review_work)
    workflow.add_node("reviser", revise_work)
    workflow.add_node("approver", final_approval)
    workflow.add_node("escalation", escalate_for_review)
    
    # Start with work creation
    workflow.set_entry_point("creator")
    
    # Linear flow to review
    workflow.add_edge("creator", "reviewer")
    
    # Conditional routing after review
    workflow.add_conditional_edges(
        "reviewer",
        quality_decision,
        {
            "approved": "approver",
            "needs_revision": "reviser",
            "max_iterations_reached": "escalation"
        }
    )
    
    # After revision, check quality again
    workflow.add_conditional_edges(
        "reviser",
        revision_quality_check,
        {
            "ready_for_approval": "approver",
            "needs_more_review": "reviewer",
            "major_revision_needed": "escalation"
        }
    )
    
    return workflow.compile()


# Helper functions
def calculate_work_quality(work: str) -> float:
    """Calculate quality score for work"""
    if not work:
        return 0.0
    
    # Simple quality metrics
    quality = 0.3  # Base quality
    
    if len(work) > 50:
        quality += 0.2
    if "analysis" in work.lower():
        quality += 0.2
    if "initial" in work.lower():
        quality += 0.1  # Bonus for being initial work
    if len(work.split()) > 10:
        quality += 0.2
    
    return min(quality, 1.0)


def get_approval_notes(quality_score: float, revision_count: int) -> str:
    """Generate approval notes"""
    if quality_score >= 0.9:
        return f"Excellent work quality achieved after {revision_count} revisions"
    elif quality_score >= 0.8:
        return f"Good work quality achieved after {revision_count} revisions"
    else:
        return f"Work approved with reservations after {revision_count} revisions"


# Quality gate decorator
def quality_gate(min_quality: float):
    """Decorator for quality gates"""
    def decorator(func):
        def wrapper(state: AgentState):
            result = func(state)
            current_quality = result["results"].get("quality_score", 0)
            
            if current_quality < min_quality:
                result["results"]["quality_gate_failed"] = True
                result["results"]["required_quality"] = min_quality
                result["results"]["actual_quality"] = current_quality
            
            return result
        return wrapper
    return decorator