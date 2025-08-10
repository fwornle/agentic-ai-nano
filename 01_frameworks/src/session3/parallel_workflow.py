# src/session3/parallel_workflow.py
"""
Parallel execution workflows with LangGraph.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
from datetime import datetime


def research_technical_aspects(state: AgentState) -> AgentState:
    """Research technical aspects in parallel"""
    current_task = state["current_task"]
    
    # Simulate technical research
    technical_data = {
        "architecture": f"Technical architecture for {current_task}",
        "implementation": "Implementation details and considerations",
        "performance": "Performance metrics and benchmarks",
        "scalability": "Scalability analysis"
    }
    
    updated_results = state["results"].copy()
    updated_results["technical_research"] = technical_data
    
    return {
        "results": updated_results,
        "current_task": f"Technical research complete for: {current_task}"
    }


def research_market_aspects(state: AgentState) -> AgentState:
    """Research market aspects in parallel"""
    current_task = state["current_task"]
    
    # Simulate market research
    market_data = {
        "target_audience": f"Target market for {current_task}",
        "competitors": "Competitive landscape analysis",
        "pricing": "Market pricing strategies",
        "trends": "Current market trends and opportunities"
    }
    
    updated_results = state["results"].copy()
    updated_results["market_research"] = market_data
    
    return {
        "results": updated_results,
        "current_task": f"Market research complete for: {current_task}"
    }


def research_competitors(state: AgentState) -> AgentState:
    """Research competitive landscape in parallel"""
    current_task = state["current_task"]
    
    # Simulate competitive research
    competitive_data = {
        "direct_competitors": f"Direct competitors in {current_task} space",
        "indirect_competitors": "Indirect competition analysis",
        "competitive_advantages": "Potential competitive advantages",
        "market_gaps": "Identified market gaps and opportunities"
    }
    
    updated_results = state["results"].copy()
    updated_results["competitive_research"] = competitive_data
    
    return {
        "results": updated_results,
        "current_task": f"Competitive research complete for: {current_task}"
    }


def merge_parallel_results(state: AgentState) -> AgentState:
    """Merge results from parallel execution branches"""
    
    results = state["results"]
    
    # Collect results from different research branches
    technical_data = results.get("technical_research", {})
    market_data = results.get("market_research", {})
    competitive_data = results.get("competitive_research", {})
    
    # Create comprehensive merged result
    merged_research = {
        "technical_insights": technical_data,
        "market_insights": market_data,
        "competitive_insights": competitive_data,
        "merge_timestamp": datetime.now().isoformat(),
        "data_sources": len([d for d in [technical_data, market_data, competitive_data] if d])
    }
    
    # Update state with merged data
    updated_results = results.copy()
    updated_results["comprehensive_research"] = merged_research
    
    return {
        "results": updated_results,
        "current_task": "analysis_phase"
    }


def create_final_analysis(state: AgentState) -> AgentState:
    """Create final analysis from merged research"""
    
    comprehensive_research = state["results"].get("comprehensive_research", {})
    
    # Analyze all the merged research
    final_analysis = {
        "executive_summary": "Comprehensive analysis based on parallel research",
        "technical_recommendations": "Technical implementation recommendations",
        "market_strategy": "Market entry and positioning strategy",
        "competitive_positioning": "Recommended competitive positioning",
        "next_steps": "Recommended next steps based on research",
        "confidence_score": calculate_analysis_confidence(comprehensive_research)
    }
    
    updated_results = state["results"].copy()
    updated_results["final_analysis"] = final_analysis
    
    return {
        "results": updated_results,
        "current_task": "analysis_complete"
    }


def create_parallel_research_workflow():
    """Workflow with parallel research branches"""
    
    workflow = StateGraph(AgentState)
    
    # Add parallel research nodes
    workflow.add_node("technical_research", research_technical_aspects)
    workflow.add_node("market_research", research_market_aspects)
    workflow.add_node("competitive_research", research_competitors)
    workflow.add_node("merge_research", merge_parallel_results)
    workflow.add_node("final_analysis", create_final_analysis)
    
    # All research nodes run in parallel from start
    workflow.set_entry_point("technical_research")
    workflow.set_entry_point("market_research") 
    workflow.set_entry_point("competitive_research")
    
    # All parallel nodes feed into merger
    workflow.add_edge("technical_research", "merge_research")
    workflow.add_edge("market_research", "merge_research")
    workflow.add_edge("competitive_research", "merge_research")
    
    # Final analysis after merge
    workflow.add_edge("merge_research", "final_analysis")
    
    return workflow.compile()


def calculate_analysis_confidence(research_data: dict) -> float:
    """Calculate confidence score for analysis"""
    if not research_data:
        return 0.0
    
    # Base confidence
    confidence = 0.5
    
    # Increase confidence based on data completeness
    data_sources = research_data.get("data_sources", 0)
    confidence += min(data_sources * 0.15, 0.4)  # Max 0.4 boost
    
    # Check for comprehensive insights
    insights = [
        research_data.get("technical_insights", {}),
        research_data.get("market_insights", {}),
        research_data.get("competitive_insights", {})
    ]
    
    complete_insights = sum(1 for insight in insights if insight)
    confidence += complete_insights * 0.1
    
    return min(confidence, 1.0)  # Cap at 1.0