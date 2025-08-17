# src/session3/workflow_nodes.py
"""
Node implementations for LangGraph workflows.
"""

from langgraph_basics import AgentState
from langchain.schema import HumanMessage, AIMessage


def research_node(state: AgentState) -> AgentState:
    """Research node - gathers information"""
    current_task = state["current_task"]
    
    # Simulate research (in practice, call LLM or tools)
    research_result = f"Researched information about: {current_task}"
    
    # Update state
    updated_results = state["results"].copy()
    updated_results["research"] = research_result
    
    return {
        "results": updated_results,
        "messages": state["messages"] + [HumanMessage(content=research_result)]
    }


def analyze_node(state: AgentState) -> AgentState:
    """Analysis node - processes research data"""
    research_data = state["results"].get("research", "")
    
    # Simulate analysis
    analysis_result = f"Analysis of: {research_data}"
    
    # Update state
    updated_results = state["results"].copy()
    updated_results["analysis"] = analysis_result
    
    return {
        "results": updated_results,
        "messages": state["messages"] + [AIMessage(content=analysis_result)]
    }


def report_node(state: AgentState) -> AgentState:
    """Report node - creates final output"""
    analysis_data = state["results"].get("analysis", "")
    
    # Create report
    report_result = f"Final report based on: {analysis_data}"
    
    # Update state
    updated_results = state["results"].copy()
    updated_results["final_report"] = report_result
    
    return {
        "results": updated_results,
        "messages": state["messages"] + [AIMessage(content=report_result)]
    }