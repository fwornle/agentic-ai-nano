# src/session3/state_merging.py
"""
Advanced state merging patterns for complex multi-agent workflows.
"""

from langgraph_basics import AgentState
from typing import Dict, List, Any, Callable, Union
from datetime import datetime
import json


class StateMerger:
    """Advanced state merging utility for complex workflows"""
    
    def __init__(self):
        self.merge_strategies = {}
        self.conflict_resolution = {}
    
    def register_merge_strategy(self, key: str, strategy: Callable):
        """Register merge strategy for specific state key"""
        self.merge_strategies[key] = strategy
    
    def register_conflict_resolution(self, key: str, resolver: Callable):
        """Register conflict resolution for specific state key"""
        self.conflict_resolution[key] = resolver
    
    def merge_states(self, states: List[AgentState]) -> AgentState:
        """Merge multiple agent states"""
        if not states:
            return {
                "messages": [],
                "current_task": "",
                "results": {},
                "iteration_count": 0
            }
        
        if len(states) == 1:
            return states[0]
        
        # Initialize merged state with first state
        merged_state = states[0].copy()
        
        # Merge with remaining states
        for state in states[1:]:
            merged_state = self._merge_two_states(merged_state, state)
        
        return merged_state
    
    def _merge_two_states(self, state1: AgentState, state2: AgentState) -> AgentState:
        """Merge two agent states"""
        merged = {}
        
        # Get all keys from both states
        all_keys = set(state1.keys()) | set(state2.keys())
        
        for key in all_keys:
            if key in self.merge_strategies:
                # Use custom merge strategy
                merged[key] = self.merge_strategies[key](
                    state1.get(key), state2.get(key)
                )
            else:
                # Use default merge strategy
                merged[key] = self._default_merge(
                    key, state1.get(key), state2.get(key)
                )
        
        return merged
    
    def _default_merge(self, key: str, value1: Any, value2: Any) -> Any:
        """Default merge strategy"""
        if value1 is None:
            return value2
        if value2 is None:
            return value1
        
        # Handle different data types
        if isinstance(value1, list) and isinstance(value2, list):
            return value1 + value2
        elif isinstance(value1, dict) and isinstance(value2, dict):
            return {**value1, **value2}
        elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            return max(value1, value2)  # Take maximum for numeric values
        else:
            # For other types, prefer the second value (more recent)
            return value2


def merge_parallel_research_results(state: AgentState) -> AgentState:
    """Merge results from parallel research agents"""
    results = state["results"]
    
    # Collect research results from different agents
    research_data = {}
    for key, value in results.items():
        if "research" in key.lower():
            research_data[key] = value
    
    # Create comprehensive research summary
    merged_research = {
        "total_research_sources": len(research_data),
        "research_components": list(research_data.keys()),
        "detailed_findings": research_data,
        "synthesis": create_research_synthesis(research_data),
        "merge_timestamp": datetime.now().isoformat()
    }
    
    updated_results = results.copy()
    updated_results["merged_research"] = merged_research
    
    return {
        "results": updated_results,
        "current_task": "research_merged"
    }


def merge_analysis_streams(state: AgentState) -> AgentState:
    """Merge multiple analysis streams into unified insights"""
    results = state["results"]
    
    # Collect different types of analysis
    analysis_streams = {}
    for key, value in results.items():
        if "analysis" in key.lower() or "insight" in key.lower():
            analysis_streams[key] = value
    
    # Create unified analysis
    unified_analysis = {
        "stream_count": len(analysis_streams),
        "analysis_types": list(analysis_streams.keys()),
        "individual_analyses": analysis_streams,
        "cross_stream_insights": generate_cross_insights(analysis_streams),
        "confidence_matrix": calculate_confidence_matrix(analysis_streams),
        "unified_recommendations": synthesize_recommendations(analysis_streams)
    }
    
    updated_results = results.copy()
    updated_results["unified_analysis"] = unified_analysis
    
    return {
        "results": updated_results,
        "current_task": "analysis_unified"
    }


def merge_decision_inputs(state: AgentState) -> AgentState:
    """Merge inputs from multiple decision-making agents"""
    results = state["results"]
    
    # Collect decision inputs
    decision_inputs = {}
    votes = {}
    confidence_scores = {}
    
    for key, value in results.items():
        if "decision" in key.lower() or "vote" in key.lower():
            decision_inputs[key] = value
            
            # Extract votes and confidence if available
            if isinstance(value, dict):
                if "vote" in value:
                    votes[key] = value["vote"]
                if "confidence" in value:
                    confidence_scores[key] = value["confidence"]
    
    # Aggregate decision data
    merged_decisions = {
        "input_count": len(decision_inputs),
        "individual_inputs": decision_inputs,
        "vote_summary": aggregate_votes(votes),
        "confidence_analysis": analyze_confidence(confidence_scores),
        "decision_matrix": create_decision_matrix(decision_inputs),
        "recommended_action": determine_recommended_action(votes, confidence_scores)
    }
    
    updated_results = results.copy()
    updated_results["merged_decisions"] = merged_decisions
    
    return {
        "results": updated_results,
        "current_task": "decisions_merged"
    }


def smart_state_merge(states: List[AgentState], merge_config: Dict[str, str]) -> AgentState:
    """Smart state merging with configurable strategies"""
    
    # Initialize merger with custom strategies
    merger = StateMerger()
    
    # Configure merge strategies based on config
    if "messages" in merge_config:
        if merge_config["messages"] == "concat":
            merger.register_merge_strategy("messages", lambda v1, v2: (v1 or []) + (v2 or []))
        elif merge_config["messages"] == "latest":
            merger.register_merge_strategy("messages", lambda v1, v2: v2 if v2 else v1)
    
    if "results" in merge_config:
        if merge_config["results"] == "deep_merge":
            merger.register_merge_strategy("results", deep_merge_dicts)
        elif merge_config["results"] == "union":
            merger.register_merge_strategy("results", lambda v1, v2: {**(v1 or {}), **(v2 or {})})
    
    if "iteration_count" in merge_config:
        if merge_config["iteration_count"] == "sum":
            merger.register_merge_strategy("iteration_count", lambda v1, v2: (v1 or 0) + (v2 or 0))
        elif merge_config["iteration_count"] == "max":
            merger.register_merge_strategy("iteration_count", lambda v1, v2: max(v1 or 0, v2 or 0))
    
    return merger.merge_states(states)


def create_state_merge_workflow():
    """Create workflow that demonstrates various state merging patterns"""
    from langgraph.graph import StateGraph, END
    
    workflow = StateGraph(AgentState)
    
    # Add merging nodes
    workflow.add_node("merge_research", merge_parallel_research_results)
    workflow.add_node("merge_analysis", merge_analysis_streams)
    workflow.add_node("merge_decisions", merge_decision_inputs)
    
    # Sequential merging
    workflow.set_entry_point("merge_research")
    workflow.add_edge("merge_research", "merge_analysis")
    workflow.add_edge("merge_analysis", "merge_decisions")
    workflow.add_edge("merge_decisions", END)
    
    return workflow.compile()


# Helper functions for merging
def create_research_synthesis(research_data: Dict[str, Any]) -> str:
    """Create synthesis from multiple research sources"""
    if not research_data:
        return "No research data available for synthesis"
    
    synthesis_points = []
    for source, data in research_data.items():
        if isinstance(data, dict) and "findings" in data:
            synthesis_points.append(f"From {source}: {data['findings']}")
        elif isinstance(data, str):
            synthesis_points.append(f"From {source}: {data[:100]}...")
    
    return "Research synthesis: " + " | ".join(synthesis_points)


def generate_cross_insights(analysis_streams: Dict[str, Any]) -> List[str]:
    """Generate insights across multiple analysis streams"""
    insights = []
    
    if len(analysis_streams) >= 2:
        insights.append("Multiple analysis perspectives provide comprehensive view")
    
    # Look for common themes
    common_terms = find_common_terms(analysis_streams)
    if common_terms:
        insights.append(f"Common themes identified: {', '.join(common_terms[:3])}")
    
    return insights


def calculate_confidence_matrix(analysis_streams: Dict[str, Any]) -> Dict[str, float]:
    """Calculate confidence matrix for analysis streams"""
    confidence_matrix = {}
    
    for stream_name, stream_data in analysis_streams.items():
        if isinstance(stream_data, dict) and "confidence" in stream_data:
            confidence_matrix[stream_name] = stream_data["confidence"]
        else:
            # Assign default confidence based on data completeness
            confidence_matrix[stream_name] = 0.7 if stream_data else 0.3
    
    return confidence_matrix


def synthesize_recommendations(analysis_streams: Dict[str, Any]) -> List[str]:
    """Synthesize recommendations from multiple analysis streams"""
    all_recommendations = []
    
    for stream_data in analysis_streams.values():
        if isinstance(stream_data, dict):
            if "recommendations" in stream_data:
                if isinstance(stream_data["recommendations"], list):
                    all_recommendations.extend(stream_data["recommendations"])
                else:
                    all_recommendations.append(str(stream_data["recommendations"]))
    
    # Remove duplicates and return top recommendations
    unique_recommendations = list(set(all_recommendations))
    return unique_recommendations[:5]  # Top 5 recommendations


def aggregate_votes(votes: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate votes from multiple decision agents"""
    vote_counts = {}
    total_votes = len(votes)
    
    for vote in votes.values():
        vote_str = str(vote)
        vote_counts[vote_str] = vote_counts.get(vote_str, 0) + 1
    
    # Find majority vote
    majority_vote = max(vote_counts.items(), key=lambda x: x[1]) if vote_counts else ("no_vote", 0)
    
    return {
        "vote_counts": vote_counts,
        "total_votes": total_votes,
        "majority_vote": majority_vote[0],
        "majority_count": majority_vote[1],
        "consensus_strength": majority_vote[1] / total_votes if total_votes > 0 else 0
    }


def analyze_confidence(confidence_scores: Dict[str, float]) -> Dict[str, Any]:
    """Analyze confidence scores across agents"""
    if not confidence_scores:
        return {"average_confidence": 0, "confidence_variance": 0}
    
    scores = list(confidence_scores.values())
    average = sum(scores) / len(scores)
    variance = sum((score - average) ** 2 for score in scores) / len(scores)
    
    return {
        "average_confidence": average,
        "confidence_variance": variance,
        "confidence_range": (min(scores), max(scores)),
        "high_confidence_agents": [k for k, v in confidence_scores.items() if v >= 0.8],
        "low_confidence_agents": [k for k, v in confidence_scores.items() if v <= 0.5]
    }


def create_decision_matrix(decision_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Create decision matrix from multiple inputs"""
    matrix = {
        "total_inputs": len(decision_inputs),
        "input_types": list(decision_inputs.keys()),
        "decision_complexity": "high" if len(decision_inputs) > 3 else "medium",
        "consensus_indicators": []
    }
    
    # Analyze consensus indicators
    if len(decision_inputs) >= 2:
        matrix["consensus_indicators"].append("Multiple agent inputs available")
    
    return matrix


def determine_recommended_action(votes: Dict[str, Any], confidence_scores: Dict[str, float]) -> str:
    """Determine recommended action based on votes and confidence"""
    if not votes:
        return "insufficient_data"
    
    # Get vote aggregation
    vote_summary = aggregate_votes(votes)
    majority_vote = vote_summary["majority_vote"]
    consensus_strength = vote_summary["consensus_strength"]
    
    # Factor in confidence
    avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5
    
    if consensus_strength >= 0.7 and avg_confidence >= 0.7:
        return f"proceed_with_{majority_vote}"
    elif consensus_strength >= 0.5:
        return f"cautiously_proceed_with_{majority_vote}"
    else:
        return "seek_additional_input"


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    if dict1 is None:
        return dict2 or {}
    if dict2 is None:
        return dict1 or {}
    
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge_dicts(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                result[key] = result[key] + value
            else:
                result[key] = value  # Overwrite with new value
        else:
            result[key] = value
    
    return result


def find_common_terms(analysis_streams: Dict[str, Any]) -> List[str]:
    """Find common terms across analysis streams"""
    all_terms = []
    
    for stream_data in analysis_streams.values():
        if isinstance(stream_data, str):
            all_terms.extend(stream_data.lower().split())
        elif isinstance(stream_data, dict):
            # Extract text from dict values
            for value in stream_data.values():
                if isinstance(value, str):
                    all_terms.extend(value.lower().split())
    
    # Count term frequency
    term_counts = {}
    for term in all_terms:
        if len(term) > 3:  # Only consider meaningful terms
            term_counts[term] = term_counts.get(term, 0) + 1
    
    # Return terms that appear multiple times
    common_terms = [term for term, count in term_counts.items() if count >= 2]
    return sorted(common_terms, key=lambda x: term_counts[x], reverse=True)