# src/session3/synchronization.py
"""
Synchronization patterns for multi-agent systems with LangGraph.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
import asyncio
from datetime import datetime


def agent_a_task(state: AgentState) -> AgentState:
    """Agent A performs its specialized task"""
    current_task = state["current_task"]
    
    # Simulate Agent A's specialized processing
    result_a = f"Agent A processed: {current_task}"
    
    updated_results = state["results"].copy()
    updated_results["agent_a_result"] = result_a
    updated_results["agent_a_timestamp"] = datetime.now().isoformat()
    
    return {
        "results": updated_results,
        "current_task": "agent_a_complete"
    }


def agent_b_task(state: AgentState) -> AgentState:
    """Agent B performs its specialized task"""
    current_task = state["current_task"]
    
    # Simulate Agent B's specialized processing
    result_b = f"Agent B processed: {current_task}"
    
    updated_results = state["results"].copy()
    updated_results["agent_b_result"] = result_b
    updated_results["agent_b_timestamp"] = datetime.now().isoformat()
    
    return {
        "results": updated_results,
        "current_task": "agent_b_complete"
    }


def wait_for_completion(state: AgentState) -> AgentState:
    """Synchronization point - wait for all agents"""
    results = state["results"]
    
    # Check if all agents have completed
    agent_a_done = "agent_a_result" in results
    agent_b_done = "agent_b_result" in results
    
    if agent_a_done and agent_b_done:
        sync_status = "all_agents_complete"
    else:
        sync_status = "waiting_for_completion"
    
    updated_results = results.copy()
    updated_results["sync_status"] = sync_status
    updated_results["sync_timestamp"] = datetime.now().isoformat()
    
    return {
        "results": updated_results,
        "current_task": sync_status
    }


def combine_results(state: AgentState) -> AgentState:
    """Combine results from synchronized agents"""
    results = state["results"]
    
    agent_a_result = results.get("agent_a_result", "")
    agent_b_result = results.get("agent_b_result", "")
    
    # Combine the results
    combined_result = {
        "agent_a_contribution": agent_a_result,
        "agent_b_contribution": agent_b_result,
        "combined_output": f"Combined: {agent_a_result} + {agent_b_result}",
        "combination_timestamp": datetime.now().isoformat()
    }
    
    updated_results = results.copy()
    updated_results["combined_result"] = combined_result
    
    return {
        "results": updated_results,
        "current_task": "synchronization_complete"
    }


def create_synchronized_workflow():
    """Create workflow with agent synchronization"""
    
    workflow = StateGraph(AgentState)
    
    # Add agent nodes
    workflow.add_node("agent_a", agent_a_task)
    workflow.add_node("agent_b", agent_b_task)
    workflow.add_node("synchronizer", wait_for_completion)
    workflow.add_node("combiner", combine_results)
    
    # Both agents start in parallel
    workflow.set_entry_point("agent_a")
    workflow.set_entry_point("agent_b")
    
    # Both agents feed into synchronizer
    workflow.add_edge("agent_a", "synchronizer")
    workflow.add_edge("agent_b", "synchronizer")
    
    # After synchronization, combine results
    workflow.add_edge("synchronizer", "combiner")
    
    return workflow.compile()


def check_sync_status(state: AgentState) -> str:
    """Decision function for synchronization status"""
    sync_status = state["results"].get("sync_status", "waiting")
    
    if sync_status == "all_agents_complete":
        return "proceed"
    else:
        return "wait"


async def run_synchronized_agents(initial_task: str):
    """Example of running synchronized agents"""
    
    workflow = create_synchronized_workflow()
    
    initial_state = {
        "messages": [],
        "current_task": initial_task,
        "results": {},
        "iteration_count": 0
    }
    
    # Execute the workflow
    result = await workflow.ainvoke(initial_state)
    
    return result["results"]["combined_result"]


# Barrier synchronization pattern
class AgentBarrier:
    """Synchronization barrier for multiple agents"""
    
    def __init__(self, agent_count: int):
        self.agent_count = agent_count
        self.waiting_agents = set()
        self.results = {}
    
    def wait(self, agent_id: str, result: dict) -> bool:
        """Agent waits at barrier with its result"""
        self.waiting_agents.add(agent_id)
        self.results[agent_id] = result
        
        # Return True if all agents have arrived
        return len(self.waiting_agents) == self.agent_count
    
    def get_combined_results(self) -> dict:
        """Get all agent results after barrier is complete"""
        return self.results.copy()
    
    def reset(self):
        """Reset barrier for reuse"""
        self.waiting_agents.clear()
        self.results.clear()