# src/session3/simple_workflow.py
"""
Simple workflow creation and configuration with LangGraph.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
from workflow_nodes import research_node, analyze_node, report_node
from decision_logic import should_continue_analysis


def create_basic_workflow():
    """Create a simple three-node workflow"""
    
    # Create the graph with our state schema
    workflow = StateGraph(AgentState)
    
    # Add nodes (the work units)
    workflow.add_node("researcher", research_node)
    workflow.add_node("analyzer", analyze_node)
    workflow.add_node("reporter", report_node)
    
    return workflow


def configure_workflow_edges(workflow):
    """Configure how nodes connect to each other"""
    
    # Simple sequential edge
    workflow.add_edge("researcher", "analyzer")
    
    # Conditional edge with decision logic
    workflow.add_conditional_edges(
        "analyzer",                    # From this node
        should_continue_analysis,      # Decision function
        {
            "continue": "reporter",    # If continue, go to reporter
            "retry": "researcher",     # If retry, go back to researcher
            "end": END                 # If done, end workflow
        }
    )
    
    # Set starting point
    workflow.set_entry_point("researcher")
    
    return workflow


def create_complete_basic_workflow():
    """Create and configure a complete basic workflow"""
    workflow = create_basic_workflow()
    workflow = configure_workflow_edges(workflow)
    return workflow.compile()