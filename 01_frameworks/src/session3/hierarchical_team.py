# src/session3/hierarchical_team.py
"""
Hierarchical team management patterns with LangGraph.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
from typing import List, Dict


def manager_planning(state: AgentState) -> AgentState:
    """Manager plans and delegates tasks"""
    current_task = state["current_task"]
    
    # Manager analyzes task and creates plan
    task_plan = {
        "main_task": current_task,
        "subtasks": [
            {"id": "subtask_1", "description": f"Research phase for {current_task}", "assigned_to": "researcher"},
            {"id": "subtask_2", "description": f"Analysis phase for {current_task}", "assigned_to": "analyst"},
            {"id": "subtask_3", "description": f"Implementation phase for {current_task}", "assigned_to": "implementer"}
        ],
        "timeline": "3 phases, sequential execution",
        "success_criteria": "All subtasks completed successfully"
    }
    
    updated_results = state["results"].copy()
    updated_results["task_plan"] = task_plan
    updated_results["current_phase"] = "planning_complete"
    updated_results["manager_status"] = "delegated"
    
    return {
        "results": updated_results,
        "current_task": "delegation_phase"
    }


def researcher_work(state: AgentState) -> AgentState:
    """Researcher executes research subtask"""
    task_plan = state["results"].get("task_plan", {})
    research_subtask = next((task for task in task_plan.get("subtasks", []) 
                           if task["assigned_to"] == "researcher"), {})
    
    # Execute research
    research_output = {
        "subtask_id": research_subtask.get("id", "unknown"),
        "findings": f"Research findings for: {research_subtask.get('description', 'unknown task')}",
        "data_sources": ["Academic papers", "Industry reports", "Expert interviews"],
        "confidence_level": 0.8,
        "completion_status": "completed"
    }
    
    updated_results = state["results"].copy()
    updated_results["research_output"] = research_output
    
    return {
        "results": updated_results,
        "current_task": "research_complete"
    }


def analyst_work(state: AgentState) -> AgentState:
    """Analyst processes research and provides analysis"""
    research_output = state["results"].get("research_output", {})
    task_plan = state["results"].get("task_plan", {})
    analysis_subtask = next((task for task in task_plan.get("subtasks", []) 
                           if task["assigned_to"] == "analyst"), {})
    
    # Perform analysis based on research
    analysis_output = {
        "subtask_id": analysis_subtask.get("id", "unknown"),
        "analysis": f"Analysis of research: {research_output.get('findings', 'no research')}",
        "insights": ["Key insight 1", "Key insight 2", "Key insight 3"],
        "recommendations": ["Recommendation A", "Recommendation B"],
        "risk_assessment": "Medium risk identified",
        "completion_status": "completed"
    }
    
    updated_results = state["results"].copy()
    updated_results["analysis_output"] = analysis_output
    
    return {
        "results": updated_results,
        "current_task": "analysis_complete"
    }


def implementer_work(state: AgentState) -> AgentState:
    """Implementer creates final deliverable"""
    research_output = state["results"].get("research_output", {})
    analysis_output = state["results"].get("analysis_output", {})
    task_plan = state["results"].get("task_plan", {})
    impl_subtask = next((task for task in task_plan.get("subtasks", []) 
                       if task["assigned_to"] == "implementer"), {})
    
    # Create implementation based on research and analysis
    implementation_output = {
        "subtask_id": impl_subtask.get("id", "unknown"),
        "deliverable": f"Implementation based on: {analysis_output.get('analysis', 'no analysis')}",
        "components": ["Component A", "Component B", "Component C"],
        "integration_points": ["System integration", "API endpoints", "User interface"],
        "testing_status": "Unit tests passed",
        "completion_status": "completed"
    }
    
    updated_results = state["results"].copy()
    updated_results["implementation_output"] = implementation_output
    
    return {
        "results": updated_results,
        "current_task": "implementation_complete"
    }


def manager_review(state: AgentState) -> AgentState:
    """Manager reviews all team outputs"""
    research_output = state["results"].get("research_output", {})
    analysis_output = state["results"].get("analysis_output", {})
    implementation_output = state["results"].get("implementation_output", {})
    
    # Manager evaluates team performance
    team_review = {
        "research_quality": evaluate_output(research_output),
        "analysis_quality": evaluate_output(analysis_output),
        "implementation_quality": evaluate_output(implementation_output),
        "overall_assessment": "Team performance evaluation",
        "success_rate": calculate_success_rate([research_output, analysis_output, implementation_output]),
        "team_feedback": generate_team_feedback([research_output, analysis_output, implementation_output])
    }
    
    updated_results = state["results"].copy()
    updated_results["team_review"] = team_review
    updated_results["project_status"] = "completed" if team_review["success_rate"] > 0.8 else "needs_revision"
    
    return {
        "results": updated_results,
        "current_task": "project_reviewed"
    }


def create_hierarchical_team_workflow():
    """Create hierarchical team workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add team member nodes
    workflow.add_node("manager", manager_planning)
    workflow.add_node("researcher", researcher_work)
    workflow.add_node("analyst", analyst_work)
    workflow.add_node("implementer", implementer_work)
    workflow.add_node("review", manager_review)
    
    # Start with manager planning
    workflow.set_entry_point("manager")
    
    # Sequential delegation pattern
    workflow.add_edge("manager", "researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "implementer")
    workflow.add_edge("implementer", "review")
    
    return workflow.compile()


def create_parallel_team_workflow():
    """Create workflow where some team members work in parallel"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("manager", manager_planning)
    workflow.add_node("researcher", researcher_work)
    workflow.add_node("analyst", analyst_work)
    workflow.add_node("implementer", implementer_work)
    workflow.add_node("review", manager_review)
    
    # Start with manager
    workflow.set_entry_point("manager")
    
    # Manager delegates to researcher and analyst in parallel
    workflow.add_edge("manager", "researcher")
    workflow.add_edge("manager", "analyst")
    
    # Both feed into implementer
    workflow.add_edge("researcher", "implementer")
    workflow.add_edge("analyst", "implementer")
    
    # Final review
    workflow.add_edge("implementer", "review")
    
    return workflow.compile()


# Helper functions
def evaluate_output(output: Dict) -> float:
    """Evaluate quality of team member output"""
    if not output or output.get("completion_status") != "completed":
        return 0.0
    
    # Simple evaluation based on output completeness
    quality = 0.5  # Base quality
    
    if "findings" in output or "analysis" in output or "deliverable" in output:
        quality += 0.3
    
    confidence = output.get("confidence_level", 0.5)
    quality += confidence * 0.2
    
    return min(quality, 1.0)


def calculate_success_rate(outputs: List[Dict]) -> float:
    """Calculate overall team success rate"""
    if not outputs:
        return 0.0
    
    completed_count = sum(1 for output in outputs 
                         if output and output.get("completion_status") == "completed")
    
    return completed_count / len(outputs)


def generate_team_feedback(outputs: List[Dict]) -> Dict:
    """Generate feedback for team performance"""
    completed_outputs = [output for output in outputs 
                        if output and output.get("completion_status") == "completed"]
    
    return {
        "total_tasks": len(outputs),
        "completed_tasks": len(completed_outputs),
        "completion_rate": len(completed_outputs) / len(outputs) if outputs else 0,
        "strengths": ["Good task completion", "Clear communication"],
        "areas_for_improvement": ["Timeline management", "Quality consistency"],
        "overall_rating": "Satisfactory" if len(completed_outputs) >= len(outputs) * 0.8 else "Needs Improvement"
    }


# Team coordination utilities
class TeamCoordinator:
    """Utility class for team coordination"""
    
    def __init__(self):
        self.team_members = {}
        self.task_assignments = {}
        self.completion_status = {}
    
    def assign_task(self, member: str, task: Dict):
        """Assign task to team member"""
        self.task_assignments[member] = task
        self.completion_status[member] = "assigned"
    
    def mark_complete(self, member: str, result: Dict):
        """Mark member's task as complete"""
        self.completion_status[member] = "completed"
        self.team_members[member] = result
    
    def all_tasks_complete(self) -> bool:
        """Check if all tasks are complete"""
        return all(status == "completed" for status in self.completion_status.values())
    
    def get_team_results(self) -> Dict:
        """Get consolidated team results"""
        return self.team_members.copy()