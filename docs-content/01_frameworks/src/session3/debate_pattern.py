# src/session3/debate_pattern.py
"""
Debate pattern implementation for multi-agent decision making.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
from decision_logic import check_debate_completion


def advocate_position(state: AgentState) -> AgentState:
    """Advocate presents their position"""
    current_task = state["current_task"]
    iteration_count = state.get("iteration_count", 0)
    
    # Generate advocate's argument
    advocate_argument = f"Advocate argues FOR: {current_task} (Round {iteration_count + 1})"
    
    updated_results = state["results"].copy()
    if "debate_history" not in updated_results:
        updated_results["debate_history"] = []
    
    updated_results["debate_history"].append({
        "role": "advocate",
        "argument": advocate_argument,
        "round": iteration_count + 1
    })
    
    updated_results["last_position"] = "advocate"
    
    return {
        "results": updated_results,
        "current_task": current_task,
        "iteration_count": iteration_count + 1
    }


def critic_position(state: AgentState) -> AgentState:
    """Critic presents counter-arguments"""
    current_task = state["current_task"]
    iteration_count = state.get("iteration_count", 0)
    
    # Generate critic's counter-argument
    critic_argument = f"Critic argues AGAINST: {current_task} (Round {iteration_count})"
    
    updated_results = state["results"].copy()
    if "debate_history" not in updated_results:
        updated_results["debate_history"] = []
    
    updated_results["debate_history"].append({
        "role": "critic",
        "argument": critic_argument,
        "round": iteration_count
    })
    
    updated_results["last_position"] = "critic"
    
    return {
        "results": updated_results,
        "current_task": current_task
    }


def judge_debate(state: AgentState) -> AgentState:
    """Judge evaluates the debate and calculates consensus"""
    debate_history = state["results"].get("debate_history", [])
    iteration_count = state.get("iteration_count", 0)
    
    # Simple consensus calculation
    advocate_args = len([arg for arg in debate_history if arg["role"] == "advocate"])
    critic_args = len([arg for arg in debate_history if arg["role"] == "critic"])
    
    # Calculate consensus score (simplified)
    if advocate_args == 0 and critic_args == 0:
        consensus_score = 0
    else:
        balance = abs(advocate_args - critic_args) / max(advocate_args + critic_args, 1)
        consensus_score = 1 - balance  # More balanced = higher consensus
    
    judge_evaluation = {
        "advocate_arguments": advocate_args,
        "critic_arguments": critic_args,
        "consensus_score": consensus_score,
        "debate_rounds": iteration_count,
        "judgment": determine_judgment(consensus_score, iteration_count)
    }
    
    updated_results = state["results"].copy()
    updated_results["judge_evaluation"] = judge_evaluation
    updated_results["consensus_score"] = consensus_score
    
    return {
        "results": updated_results,
        "current_task": state["current_task"]
    }


def resolve_debate(state: AgentState) -> AgentState:
    """Final resolution of the debate"""
    judge_evaluation = state["results"].get("judge_evaluation", {})
    consensus_score = judge_evaluation.get("consensus_score", 0)
    
    if consensus_score >= 0.8:
        resolution = "Strong consensus reached"
    elif consensus_score >= 0.6:
        resolution = "Moderate consensus reached"
    else:
        resolution = "No clear consensus - decision needed"
    
    final_decision = {
        "resolution": resolution,
        "final_consensus_score": consensus_score,
        "recommended_action": get_recommended_action(consensus_score),
        "debate_summary": summarize_debate(state["results"].get("debate_history", []))
    }
    
    updated_results = state["results"].copy()
    updated_results["final_decision"] = final_decision
    
    return {
        "results": updated_results,
        "current_task": "debate_resolved"
    }


def create_debate_workflow():
    """Create multi-agent debate workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add debate participants
    workflow.add_node("advocate", advocate_position)
    workflow.add_node("critic", critic_position)
    workflow.add_node("judge", judge_debate)
    workflow.add_node("resolver", resolve_debate)
    
    # Start with advocate
    workflow.set_entry_point("advocate")
    
    # Debate flow
    workflow.add_edge("advocate", "critic")
    workflow.add_edge("critic", "judge")
    
    # Conditional routing based on debate status
    workflow.add_conditional_edges(
        "judge",
        check_debate_completion,
        {
            "continue_debate": "advocate",  # Continue debate
            "consensus_reached": "resolver",  # End with consensus
            "impasse": "resolver"  # End at impasse
        }
    )
    
    return workflow.compile()


# Helper functions
def determine_judgment(consensus_score: float, rounds: int) -> str:
    """Determine judge's overall judgment"""
    if consensus_score >= 0.8:
        return "Strong agreement achieved"
    elif consensus_score >= 0.6:
        return "Reasonable consensus found"
    elif rounds >= 5:
        return "Maximum rounds reached - impasse"
    else:
        return "Debate should continue"


def get_recommended_action(consensus_score: float) -> str:
    """Get recommended action based on consensus"""
    if consensus_score >= 0.8:
        return "Proceed with confidence"
    elif consensus_score >= 0.6:
        return "Proceed with caution"
    else:
        return "Seek additional input or expert opinion"


def summarize_debate(debate_history: list) -> dict:
    """Summarize the entire debate"""
    if not debate_history:
        return {"summary": "No debate occurred"}
    
    advocate_rounds = [arg for arg in debate_history if arg["role"] == "advocate"]
    critic_rounds = [arg for arg in debate_history if arg["role"] == "critic"]
    
    return {
        "total_rounds": len(debate_history),
        "advocate_arguments": len(advocate_rounds),
        "critic_arguments": len(critic_rounds),
        "final_round": max([arg["round"] for arg in debate_history]) if debate_history else 0,
        "debate_balanced": abs(len(advocate_rounds) - len(critic_rounds)) <= 1
    }