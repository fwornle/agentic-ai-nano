# Session 4 - Module A: Advanced CrewAI Flows (45 minutes)

**Prerequisites**: [Session 4 Core Section Complete](Session4_CrewAI_Team_Orchestration.md)  
**Target Audience**: Implementers building sophisticated workflow systems  
**Cognitive Load**: 5 advanced concepts

---

## 🎯 Module Overview

This module explores CrewAI's most advanced workflow patterns including deterministic CrewAI Flows, dynamic team formation, sophisticated delegation strategies, and production-ready orchestration patterns. You'll learn to build enterprise-grade agent systems that can handle complex multi-step workflows with guaranteed execution order and state management.

### Learning Objectives
By the end of this module, you will:
- Implement CrewAI Flows for deterministic production workflows
- Design dynamic team formation systems that adapt to task requirements
- Create sophisticated delegation patterns with peer inquiry and workload balancing
- Build enterprise monitoring and performance optimization systems

---

## Part 1: CrewAI Flows - Production Orchestration (25 minutes)

### Deterministic Workflow Patterns

🗂️ **File**: `src/session4/advanced_flows.py` - CrewAI Flow implementations

CrewAI Flows represent a paradigm shift from reactive coordination to deterministic orchestration, essential for enterprise systems:

```python
from crewai.flow import Flow, start, listen, router
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import asyncio

class FlowState(BaseModel):
    """Comprehensive state management for CrewAI Flows"""
    
    # Core workflow data
    project_id: str
    current_phase: str
    completed_phases: List[str]
    
    # Task management
    task_queue: List[Dict[str, Any]]
    active_tasks: Dict[str, Dict[str, Any]]
    completed_tasks: Dict[str, Dict[str, Any]]
    
    # Team coordination
    team_assignments: Dict[str, List[str]]
    resource_allocation: Dict[str, float]
    performance_metrics: Dict[str, Any]
    
    # Flow control
    flow_status: str
    error_history: List[Dict[str, Any]]
    checkpoint_data: Dict[str, Any]

class EnterpriseResearchFlow(Flow):
    """Advanced research workflow with deterministic execution and state management"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.state_history = []
        self.performance_tracker = {}
        
    @start()
    def initiate_research_project(self, topic: str, complexity: str = "standard") -> FlowState:
        """Initialize comprehensive research project with full state tracking"""
        
        project_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Analyze project requirements
        task_analysis = self._analyze_project_requirements(topic, complexity)
        
        # Initialize comprehensive state
        initial_state = FlowState(
            project_id=project_id,
            current_phase="initiation",
            completed_phases=[],
            task_queue=task_analysis["tasks"],
            active_tasks={},
            completed_tasks={},
            team_assignments=task_analysis["team_assignments"],
            resource_allocation=task_analysis["resource_allocation"],
            performance_metrics={
                "start_time": datetime.now().timestamp(),
                "estimated_duration": task_analysis["estimated_duration"],
                "complexity_score": task_analysis["complexity_score"]
            },
            flow_status="active",
            error_history=[],
            checkpoint_data={"last_checkpoint": datetime.now().timestamp()}
        )
        
        self.logger.info(f"Research project initiated: {project_id}")
        self._save_state_checkpoint(initial_state)
        
        return initial_state
    
    @listen(initiate_research_project)
    def orchestrate_research_teams(self, state: FlowState) -> FlowState:
        """Coordinate multiple research teams with sophisticated load balancing"""
        
        # Dynamic team formation based on task requirements
        optimal_teams = self._form_optimal_research_teams(state.task_queue)
        
        # Assign tasks to teams with workload balancing
        team_assignments = {}
        for team_id, team_config in optimal_teams.items():
            assigned_tasks = self._assign_tasks_to_team(
                team_config, 
                state.task_queue,
                state.resource_allocation
            )
            team_assignments[team_id] = assigned_tasks
        
        # Update state with team coordination
        updated_state = state.copy()
        updated_state.current_phase = "team_orchestration"
        updated_state.team_assignments = team_assignments
        updated_state.active_tasks = self._convert_assignments_to_active_tasks(team_assignments)
        
        # Track orchestration metrics
        updated_state.performance_metrics.update({
            "teams_formed": len(optimal_teams),
            "tasks_assigned": len(updated_state.active_tasks),
            "orchestration_time": datetime.now().timestamp()
        })
        
        self.logger.info(f"Teams orchestrated: {len(optimal_teams)} teams, {len(updated_state.active_tasks)} tasks")
        self._save_state_checkpoint(updated_state)
        
        return updated_state
    
    @listen(orchestrate_research_teams)
    def execute_parallel_research(self, state: FlowState) -> FlowState:
        """Execute research tasks in parallel with comprehensive monitoring"""
        
        # Simulate parallel research execution with sophisticated coordination
        research_results = {}
        execution_metrics = {}
        
        for task_id, task_data in state.active_tasks.items():
            try:
                # Execute research task with monitoring
                start_time = datetime.now().timestamp()
                
                result = self._execute_research_task(
                    task_data,
                    state.team_assignments,
                    state.resource_allocation
                )
                
                execution_time = datetime.now().timestamp() - start_time
                
                research_results[task_id] = {
                    "result": result,
                    "execution_time": execution_time,
                    "quality_score": self._assess_result_quality(result),
                    "status": "completed"
                }
                
                execution_metrics[task_id] = {
                    "execution_time": execution_time,
                    "resource_usage": task_data.get("resource_usage", 0.0),
                    "team_efficiency": self._calculate_team_efficiency(task_data)
                }
                
            except Exception as e:
                research_results[task_id] = {
                    "error": str(e),
                    "status": "failed"
                }
                
                # Log error for analysis
                updated_state.error_history.append({
                    "task_id": task_id,
                    "error": str(e),
                    "timestamp": datetime.now().timestamp()
                })
        
        # Update state with research results
        updated_state = state.copy()
        updated_state.current_phase = "research_execution"
        updated_state.completed_tasks = research_results
        updated_state.active_tasks = {}  # Tasks completed
        
        # Update performance metrics
        total_execution_time = sum(
            metrics["execution_time"] for metrics in execution_metrics.values()
        )
        average_quality = sum(
            result.get("quality_score", 0) for result in research_results.values()
            if "quality_score" in result
        ) / len(research_results)
        
        updated_state.performance_metrics.update({
            "research_execution_time": total_execution_time,
            "average_quality_score": average_quality,
            "successful_tasks": len([r for r in research_results.values() if r.get("status") == "completed"]),
            "failed_tasks": len([r for r in research_results.values() if r.get("status") == "failed"])
        })
        
        self.logger.info(f"Research execution completed: {len(research_results)} tasks processed")
        self._save_state_checkpoint(updated_state)
        
        return updated_state
    
    @listen(execute_parallel_research)
    def synthesize_research_findings(self, state: FlowState) -> FlowState:
        """Intelligent synthesis of research findings with quality assessment"""
        
        # Collect all successful research results
        successful_results = {
            task_id: result for task_id, result in state.completed_tasks.items()
            if result.get("status") == "completed"
        }
        
        if not successful_results:
            # Handle case where no research was successful
            updated_state = state.copy()
            updated_state.flow_status = "failed"
            updated_state.error_history.append({
                "phase": "synthesis",
                "error": "No successful research results to synthesize",
                "timestamp": datetime.now().timestamp()
            })
            return updated_state
        
        # Perform intelligent synthesis with quality weighting
        synthesis_result = self._perform_weighted_synthesis(
            successful_results,
            state.performance_metrics
        )
        
        # Quality validation of synthesis
        synthesis_quality = self._validate_synthesis_quality(synthesis_result)
        
        # Update state with synthesis results
        updated_state = state.copy()
        updated_state.current_phase = "synthesis"
        updated_state.completed_phases = state.completed_phases + ["research_execution"]
        
        # Add synthesis to completed tasks
        updated_state.completed_tasks["synthesis"] = {
            "result": synthesis_result,
            "quality_score": synthesis_quality,
            "sources_count": len(successful_results),
            "synthesis_timestamp": datetime.now().timestamp(),
            "status": "completed"
        }
        
        # Final performance metrics
        total_flow_time = datetime.now().timestamp() - state.performance_metrics["start_time"]
        updated_state.performance_metrics.update({
            "total_flow_time": total_flow_time,
            "synthesis_quality": synthesis_quality,
            "overall_efficiency": self._calculate_overall_efficiency(updated_state),
            "completion_timestamp": datetime.now().timestamp()
        })
        
        updated_state.flow_status = "completed"
        
        self.logger.info(f"Research synthesis completed with quality score: {synthesis_quality}")
        self._save_state_checkpoint(updated_state)
        
        return updated_state
    
    @router(execute_parallel_research)
    def route_based_on_quality(self, state: FlowState) -> str:
        """Intelligent routing based on research quality and completeness"""
        
        successful_tasks = [
            task for task in state.completed_tasks.values()
            if task.get("status") == "completed"
        ]
        
        if not successful_tasks:
            return "handle_research_failure"
        
        # Calculate average quality score
        average_quality = sum(
            task.get("quality_score", 0) for task in successful_tasks
        ) / len(successful_tasks)
        
        # Determine routing based on quality thresholds
        if average_quality >= 0.8:
            return "synthesize_research_findings"  # High quality - proceed to synthesis
        elif average_quality >= 0.6:
            return "enhance_research_quality"     # Medium quality - enhancement needed
        else:
            return "retry_research_phase"         # Low quality - retry needed
    
    def _analyze_project_requirements(self, topic: str, complexity: str) -> Dict[str, Any]:
        """Analyze project requirements and create execution plan"""
        
        complexity_mapping = {
            "simple": {"tasks": 3, "duration": 1800, "score": 0.3},
            "standard": {"tasks": 6, "duration": 3600, "score": 0.6},
            "complex": {"tasks": 10, "duration": 7200, "score": 0.9}
        }
        
        config = complexity_mapping.get(complexity, complexity_mapping["standard"])
        
        # Generate task structure based on topic and complexity
        tasks = []
        for i in range(config["tasks"]):
            tasks.append({
                "task_id": f"research_task_{i+1}",
                "type": "research",
                "focus": f"aspect_{i+1}_of_{topic}",
                "priority": "high" if i < 2 else "standard",
                "estimated_duration": config["duration"] // config["tasks"]
            })
        
        # Team assignment strategy
        team_assignments = {
            "primary_research": tasks[:config["tasks"]//2],
            "secondary_research": tasks[config["tasks"]//2:],
            "quality_assurance": ["validation", "cross_check"]
        }
        
        # Resource allocation
        resource_allocation = {
            "primary_research": 0.5,
            "secondary_research": 0.3,
            "quality_assurance": 0.2
        }
        
        return {
            "tasks": tasks,
            "team_assignments": team_assignments,
            "resource_allocation": resource_allocation,
            "estimated_duration": config["duration"],
            "complexity_score": config["score"]
        }
    
    def _form_optimal_research_teams(self, task_queue: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Form optimal research teams based on task requirements"""
        
        # Analyze task requirements for team formation
        high_priority_tasks = [task for task in task_queue if task.get("priority") == "high"]
        standard_tasks = [task for task in task_queue if task.get("priority") != "high"]
        
        teams = {}
        
        if high_priority_tasks:
            teams["priority_team"] = {
                "specialization": "high_priority_research",
                "capacity": len(high_priority_tasks),
                "skills": ["deep_analysis", "rapid_research", "quality_validation"],
                "resource_weight": 0.6
            }
        
        if standard_tasks:
            teams["standard_team"] = {
                "specialization": "standard_research",
                "capacity": len(standard_tasks),
                "skills": ["general_research", "data_gathering", "fact_checking"],
                "resource_weight": 0.4
            }
        
        return teams
    
    def _execute_research_task(self, task_data: Dict[str, Any], 
                             team_assignments: Dict[str, Any],
                             resource_allocation: Dict[str, float]) -> Dict[str, Any]:
        """Execute individual research task with comprehensive result tracking"""
        
        # Simulate sophisticated research execution
        focus_area = task_data.get("focus", "general")
        task_type = task_data.get("type", "research")
        
        # Generate research result based on focus and type
        research_result = {
            "findings": f"Comprehensive research on {focus_area}",
            "data_points": ["point_1", "point_2", "point_3"],
            "sources": ["source_1", "source_2", "source_3"],
            "analysis": f"Detailed analysis of {focus_area} reveals key insights",
            "confidence_score": 0.85,
            "completeness": 0.90
        }
        
        return research_result
    
    def _save_state_checkpoint(self, state: FlowState):
        """Save state checkpoint for recovery and monitoring"""
        self.state_history.append({
            "timestamp": datetime.now().timestamp(),
            "phase": state.current_phase,
            "state_snapshot": state.dict()
        })
        
        # Keep only last 10 checkpoints for memory efficiency
        if len(self.state_history) > 10:
            self.state_history = self.state_history[-10:]
```

---

## Part 2: Dynamic Team Formation and Delegation (20 minutes)

### Adaptive Team Assembly

🗂️ **File**: `src/session4/dynamic_teams.py` - Dynamic team formation systems

```python
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

class SkillLevel(Enum):
    """Skill proficiency levels for capability assessment"""
    NOVICE = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5

@dataclass
class AgentCapability:
    """Comprehensive agent capability profile"""
    agent_id: str
    primary_skills: Dict[str, SkillLevel]
    secondary_skills: Dict[str, SkillLevel]
    performance_history: Dict[str, float] = field(default_factory=dict)
    availability_score: float = 1.0
    collaboration_rating: float = 0.8
    learning_rate: float = 0.1

@dataclass
class TaskRequirement:
    """Detailed task requirement specification"""
    task_id: str
    required_skills: Dict[str, SkillLevel]
    estimated_duration: int
    complexity_score: float
    collaboration_needs: List[str]
    deadline: Optional[datetime] = None

class DynamicTeamFormation:
    """Advanced team formation system with AI-driven optimization"""
    
    def __init__(self):
        self.agent_capabilities: Dict[str, AgentCapability] = {}
        self.team_configurations: Dict[str, Dict[str, Any]] = {}
        self.performance_history: Dict[str, List[float]] = {}
        self.collaboration_matrix: Dict[Tuple[str, str], float] = {}
        
    def register_agent_capabilities(self, agent_id: str, capabilities: AgentCapability):
        """Register agent with comprehensive capability profile"""
        self.agent_capabilities[agent_id] = capabilities
        
        # Initialize performance tracking
        if agent_id not in self.performance_history:
            self.performance_history[agent_id] = []
    
    def analyze_task_requirements(self, task_description: str, 
                                context: Dict[str, Any]) -> TaskRequirement:
        """AI-powered task analysis for optimal team formation"""
        
        # Extract skills from task description using NLP-like analysis
        required_skills = self._extract_required_skills(task_description)
        
        # Assess task complexity
        complexity_score = self._assess_task_complexity(task_description, context)
        
        # Determine collaboration requirements
        collaboration_needs = self._identify_collaboration_patterns(task_description)
        
        # Estimate duration based on complexity and requirements
        estimated_duration = self._estimate_task_duration(complexity_score, required_skills)
        
        return TaskRequirement(
            task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            required_skills=required_skills,
            estimated_duration=estimated_duration,
            complexity_score=complexity_score,
            collaboration_needs=collaboration_needs,
            deadline=context.get("deadline")
        )
    
    def form_optimal_team(self, task_requirement: TaskRequirement,
                         available_agents: List[str]) -> Dict[str, Any]:
        """Form optimal team using multi-criteria optimization"""
        
        # Filter available agents by capability
        candidate_agents = self._filter_capable_agents(task_requirement, available_agents)
        
        if not candidate_agents:
            raise ValueError("No agents available with required capabilities")
        
        # Generate team combinations
        team_combinations = self._generate_team_combinations(
            candidate_agents, 
            task_requirement
        )
        
        # Evaluate each team combination
        best_team = None
        best_score = -1
        
        for team_combination in team_combinations:
            team_score = self._evaluate_team_effectiveness(
                team_combination, 
                task_requirement
            )
            
            if team_score > best_score:
                best_score = team_score
                best_team = team_combination
        
        # Generate team configuration
        team_config = self._create_team_configuration(best_team, task_requirement)
        
        return {
            "team_members": best_team,
            "team_score": best_score,
            "configuration": team_config,
            "formation_metadata": {
                "formation_time": datetime.now(),
                "alternatives_considered": len(team_combinations),
                "optimization_criteria": "multi_criteria"
            }
        }
    
    def _extract_required_skills(self, task_description: str) -> Dict[str, SkillLevel]:
        """Extract required skills from task description"""
        
        # Skill keyword mapping for analysis
        skill_keywords = {
            "research": {"keywords": ["research", "investigate", "analyze"], "level": SkillLevel.ADVANCED},
            "writing": {"keywords": ["write", "document", "report"], "level": SkillLevel.INTERMEDIATE},
            "analysis": {"keywords": ["analyze", "evaluate", "assess"], "level": SkillLevel.ADVANCED},
            "coding": {"keywords": ["code", "implement", "develop"], "level": SkillLevel.EXPERT},
            "design": {"keywords": ["design", "create", "architect"], "level": SkillLevel.ADVANCED},
            "review": {"keywords": ["review", "validate", "check"], "level": SkillLevel.INTERMEDIATE}
        }
        
        required_skills = {}
        task_lower = task_description.lower()
        
        for skill, config in skill_keywords.items():
            for keyword in config["keywords"]:
                if keyword in task_lower:
                    # Adjust skill level based on task complexity indicators
                    base_level = config["level"]
                    if any(indicator in task_lower for indicator in ["complex", "advanced", "expert"]):
                        required_skills[skill] = SkillLevel.EXPERT
                    elif any(indicator in task_lower for indicator in ["simple", "basic", "quick"]):
                        required_skills[skill] = SkillLevel.INTERMEDIATE
                    else:
                        required_skills[skill] = base_level
                    break
        
        return required_skills
    
    def _evaluate_team_effectiveness(self, team_members: List[str],
                                   task_requirement: TaskRequirement) -> float:
        """Comprehensive team effectiveness evaluation"""
        
        if not team_members:
            return 0.0
        
        # Skill coverage score
        skill_coverage = self._calculate_skill_coverage(team_members, task_requirement)
        
        # Performance history score
        performance_score = self._calculate_team_performance_score(team_members)
        
        # Collaboration compatibility
        collaboration_score = self._calculate_collaboration_compatibility(team_members)
        
        # Availability and workload balance
        availability_score = self._calculate_team_availability(team_members)
        
        # Size efficiency (prefer smaller effective teams)
        size_efficiency = max(0.5, 1.0 - (len(team_members) - 2) * 0.1)
        
        # Weighted composite score
        effectiveness_score = (
            skill_coverage * 0.35 +
            performance_score * 0.25 +
            collaboration_score * 0.20 +
            availability_score * 0.15 +
            size_efficiency * 0.05
        )
        
        return min(effectiveness_score, 1.0)
    
    def _calculate_skill_coverage(self, team_members: List[str],
                                task_requirement: TaskRequirement) -> float:
        """Calculate how well team covers required skills"""
        
        total_coverage = 0.0
        total_requirements = len(task_requirement.required_skills)
        
        if total_requirements == 0:
            return 1.0
        
        for skill, required_level in task_requirement.required_skills.items():
            best_team_level = SkillLevel.NOVICE
            
            # Find highest skill level in team for this skill
            for agent_id in team_members:
                agent_capability = self.agent_capabilities.get(agent_id)
                if agent_capability:
                    # Check primary skills first
                    if skill in agent_capability.primary_skills:
                        agent_level = agent_capability.primary_skills[skill]
                        if agent_level.value > best_team_level.value:
                            best_team_level = agent_level
                    # Check secondary skills
                    elif skill in agent_capability.secondary_skills:
                        agent_level = agent_capability.secondary_skills[skill]
                        if agent_level.value > best_team_level.value:
                            best_team_level = agent_level
            
            # Calculate coverage for this skill
            if best_team_level.value >= required_level.value:
                skill_coverage = 1.0  # Fully covered
            else:
                skill_coverage = best_team_level.value / required_level.value
            
            total_coverage += skill_coverage
        
        return total_coverage / total_requirements
    
    def _calculate_collaboration_compatibility(self, team_members: List[str]) -> float:
        """Calculate team collaboration compatibility score"""
        
        if len(team_members) < 2:
            return 1.0  # Single member teams have perfect compatibility
        
        total_compatibility = 0.0
        pair_count = 0
        
        # Evaluate all agent pairs
        for i, agent1 in enumerate(team_members):
            for agent2 in team_members[i+1:]:
                pair_key = (agent1, agent2)
                reverse_key = (agent2, agent1)
                
                # Get collaboration score from matrix
                if pair_key in self.collaboration_matrix:
                    compatibility = self.collaboration_matrix[pair_key]
                elif reverse_key in self.collaboration_matrix:
                    compatibility = self.collaboration_matrix[reverse_key]
                else:
                    # Default compatibility based on agent collaboration ratings
                    agent1_capability = self.agent_capabilities.get(agent1)
                    agent2_capability = self.agent_capabilities.get(agent2)
                    
                    if agent1_capability and agent2_capability:
                        compatibility = (
                            agent1_capability.collaboration_rating +
                            agent2_capability.collaboration_rating
                        ) / 2
                    else:
                        compatibility = 0.7  # Default moderate compatibility
                
                total_compatibility += compatibility
                pair_count += 1
        
        return total_compatibility / pair_count if pair_count > 0 else 1.0
```

---

## 🎯 Module Summary

You've now mastered advanced CrewAI flow patterns and dynamic team coordination:

✅ **CrewAI Flows**: Implemented deterministic workflows with state management and guaranteed execution order  
✅ **Dynamic Team Formation**: Created adaptive team assembly systems with AI-driven optimization  
✅ **Sophisticated Delegation**: Built advanced delegation patterns with peer inquiry and workload balancing  
✅ **Production Orchestration**: Designed enterprise-grade monitoring and performance optimization systems

### Next Steps
- **Continue to Module B**: [Enterprise Team Patterns](Session4_ModuleB_Enterprise_Team_Patterns.md) for production architectures
- **Return to Core**: [Session 4 Main](Session4_CrewAI_Team_Orchestration.md)
- **Advance to Session 6**: [Agent Communication Protocols](Session6_Agent_Communication_Protocols.md)

---

**🗂️ Source Files for Module A:**
- `src/session4/advanced_flows.py` - CrewAI Flow implementations
- `src/session4/dynamic_teams.py` - Dynamic team formation systems
- `src/session4/delegation_patterns.py` - Sophisticated delegation strategies