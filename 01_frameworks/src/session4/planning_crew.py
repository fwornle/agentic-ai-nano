# src/session4/planning_crew.py
"""
Planning pattern implementation using CrewAI teams.
Demonstrates strategic planning and coordinated execution with specialized planning roles.
"""

from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI
from typing import Dict, List, Any
from datetime import datetime, timedelta

def create_planning_crew(llm=None):
    """Crew implementing comprehensive planning pattern with specialized roles"""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Strategic planner - high-level planning
    planner = Agent(
        role='Strategic Project Planner',
        goal='Create comprehensive project plans with clear phases, dependencies, and realistic timelines',
        backstory="""You are an experienced project planner with 15+ years in complex 
        technology projects. You excel at breaking down complex projects into manageable 
        phases, identifying dependencies, creating realistic timelines, and anticipating 
        potential challenges before they become problems.""",
        llm=llm,
        verbose=True,
        allow_delegation=True,
        max_iter=5
    )
    
    # Resource analyst - capacity and resource planning
    resource_analyst = Agent(
        role='Resource Planning Analyst',
        goal='Analyze resource requirements, constraints, and optimization opportunities',
        backstory="""You specialize in resource analysis, capacity planning, 
        and identifying potential bottlenecks or resource conflicts. You have deep 
        expertise in human resource planning, infrastructure requirements, and 
        budget optimization for technology projects.""",
        llm=llm,
        verbose=True,
        max_iter=3
    )
    
    # Risk assessor - risk identification and mitigation
    risk_assessor = Agent(
        role='Risk Assessment Specialist',
        goal='Identify potential risks systematically and develop comprehensive mitigation strategies',
        backstory="""You are expert at identifying project risks across technical, 
        business, and operational dimensions. You assess impact and probability, 
        develop effective mitigation strategies, and create contingency plans. 
        You think several steps ahead to anticipate problems.""",
        llm=llm,
        verbose=True,
        max_iter=4
    )
    
    # Execution coordinator - implementation planning
    coordinator = Agent(
        role='Execution Coordinator',
        goal='Coordinate plan execution, monitor progress, and adapt plans to changing circumstances',
        backstory="""You coordinate project execution, track progress against milestones, 
        and ensure plans are followed while remaining flexible to adapt to changing 
        circumstances. You excel at keeping teams aligned and projects on track.""",
        llm=llm,
        verbose=True,
        allow_delegation=True,
        max_iter=4
    )
    
    # Quality assurance for plans
    plan_reviewer = Agent(
        role='Plan Quality Reviewer',
        goal='Review plans for completeness, feasibility, and quality before finalization',
        backstory="""You review project plans with a critical eye for completeness, 
        feasibility, and quality. You identify gaps, inconsistencies, and potential 
        improvements before plans are finalized and executed.""",
        llm=llm,
        verbose=True,
        max_iter=2
    )
    
    # Initial strategic planning task
    initial_planning = Task(
        description="""Create a comprehensive project plan for 'Building an Enterprise AI Agent Platform'.
        
        Project scope:
        - Multi-tenant SaaS platform for AI agent deployment
        - Support for multiple agent frameworks (CrewAI, LangGraph, etc.)
        - Enterprise security, compliance, and governance features
        - Scalable architecture supporting 10,000+ concurrent agents
        - Integration with existing enterprise systems
        
        Plan requirements:
        1. Project scope definition and clear objectives
        2. Major phases and key milestones with timelines
        3. Detailed task breakdown structure
        4. Dependencies and critical path analysis
        5. Success criteria and measurable outcomes
        6. Stakeholder identification and communication plan
        
        Create realistic 12-month development timeline.""",
        agent=planner,
        expected_output="Comprehensive strategic project plan with phases, tasks, dependencies, and 12-month timeline"
    )
    
    # Resource planning task
    resource_planning = Task(
        description="""Analyze comprehensive resource requirements for the AI platform project.
        
        Resource analysis areas:
        1. Human resources:
           - Development team composition (frontend, backend, DevOps, AI/ML)
           - Required skills and experience levels
           - Team growth timeline and hiring plan
           - Training and onboarding requirements
        
        2. Technical infrastructure:
           - Development and staging environments
           - Production infrastructure (cloud, on-premise, hybrid)
           - AI/ML compute requirements (GPUs, specialized hardware)
           - Data storage and processing capabilities
        
        3. Budget considerations:
           - Personnel costs and salary expectations
           - Infrastructure and cloud service costs
           - Third-party licenses and service subscriptions
           - Contingency budget for unforeseen expenses
        
        4. External dependencies:
           - Vendor relationships and procurement needs
           - Partner integrations and API access
           - Compliance and security audit requirements
           
        Provide detailed resource allocation timeline aligned with project phases.""",
        agent=resource_analyst,
        expected_output="Detailed resource plan with requirements, costs, allocation timeline, and procurement strategy",
        context=[initial_planning]
    )
    
    # Risk assessment task
    risk_assessment = Task(
        description="""Conduct thorough risk assessment for the AI platform project across all dimensions.
        
        Risk categories to assess:
        
        1. Technical risks:
           - AI model performance and reliability challenges
           - Scalability and performance bottlenecks
           - Integration complexity with existing systems
           - Security vulnerabilities and data protection
           - Technology obsolescence and vendor lock-in
        
        2. Resource and organizational risks:
           - Key person dependencies and knowledge retention
           - Skill availability and team scaling challenges
           - Budget overruns and cost escalation
           - Timeline delays and milestone slippage
        
        3. Business and market risks:
           - Changing market requirements and competition
           - Regulatory changes and compliance requirements
           - Customer adoption and user acceptance
           - ROI achievement and business case validation
        
        4. Operational risks:
           - Service reliability and uptime requirements
           - Disaster recovery and business continuity
           - Support and maintenance complexity
           - Change management and user training
        
        For each risk:
        - Assess probability (1-5) and impact (1-5)
        - Develop specific mitigation strategies
        - Create contingency plans for high-impact risks
        - Assign risk owners and monitoring processes""",
        agent=risk_assessor,
        expected_output="Comprehensive risk register with probability/impact scores, mitigation strategies, contingency plans, and monitoring procedures",
        context=[initial_planning, resource_planning]
    )
    
    # Plan integration task
    plan_integration = Task(
        description="""Integrate all planning components into a unified, executable master plan.
        
        Integration requirements:
        1. Master project schedule integrating all workstreams
        2. Resource allocation schedule aligned with project phases
        3. Risk mitigation activities integrated into timeline
        4. Budget timeline with cash flow projections
        5. Communication and governance processes
        6. Quality gates and decision points
        7. Change management and scope control procedures
        8. Progress monitoring and reporting framework
        
        Ensure all components are consistent and mutually supportive.
        Resolve any conflicts or inconsistencies between different planning inputs.
        Create executive dashboard view for stakeholder communication.""",
        agent=coordinator,
        expected_output="Integrated master plan with unified timeline, resources, risks, and governance framework ready for execution",
        context=[initial_planning, resource_planning, risk_assessment]
    )
    
    # Plan validation and quality review
    plan_validation = Task(
        description="""Conduct comprehensive validation of the integrated master plan.
        
        Validation criteria:
        1. Logic and dependencies:
           - Are task dependencies logical and complete?
           - Is the critical path realistic and achievable?
           - Are there any circular dependencies or conflicts?
        
        2. Resource allocation realism:
           - Are resource requirements realistic and achievable?
           - Is the hiring timeline feasible for required skills?
           - Are infrastructure scaling plans adequate?
        
        3. Risk mitigation adequacy:
           - Are high-impact risks properly addressed?
           - Are mitigation strategies specific and actionable?
           - Are contingency plans realistic and well-defined?
        
        4. Timeline achievability:
           - Are milestone dates realistic given scope and resources?
           - Is there adequate buffer for unforeseen issues?
           - Are external dependencies properly accounted for?
        
        5. Success criteria measurability:
           - Are success criteria specific and measurable?
           - Are there clear metrics and measurement processes?
           - Are quality gates well-defined and achievable?
        
        Provide specific recommendations for any issues identified.
        Assign overall plan quality score and approval recommendation.""",
        agent=plan_reviewer,
        expected_output="Plan validation report with quality assessment, specific recommendations, and final approval status",
        context=[plan_integration]
    )
    
    # Final plan optimization
    final_optimization = Task(
        description="""Based on validation feedback, optimize the plan for maximum effectiveness.
        
        Optimization focus:
        1. Address any validation issues identified
        2. Optimize resource utilization and cost effectiveness
        3. Streamline processes and eliminate redundancies
        4. Enhance risk mitigation without over-engineering
        5. Improve timeline efficiency while maintaining quality
        6. Strengthen success measurement and monitoring
        
        Create final optimized plan ready for stakeholder approval and execution.
        Include implementation guide and success metrics dashboard.""",
        agent=planner,
        expected_output="Final optimized project plan with implementation guide, success metrics, and stakeholder presentation materials",
        context=[plan_validation]
    )
    
    return Crew(
        agents=[planner, resource_analyst, risk_assessor, coordinator, plan_reviewer],
        tasks=[initial_planning, resource_planning, risk_assessment, plan_integration, 
               plan_validation, final_optimization],
        process=Process.sequential,
        verbose=2,
        memory=True
    )


def create_agile_planning_crew(llm=None):
    """Alternative planning crew using agile/iterative planning approach"""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Agile planning specialists
    product_owner = Agent(
        role='Product Owner',
        goal='Define and prioritize product requirements and user stories',
        backstory="""You represent stakeholder interests and define what needs 
        to be built. You create user stories, prioritize features, and make 
        product decisions.""",
        llm=llm,
        verbose=True
    )
    
    scrum_master = Agent(
        role='Scrum Master',
        goal='Facilitate agile processes and remove impediments',
        backstory="""You facilitate agile ceremonies, help teams self-organize, 
        and remove impediments to team productivity.""",
        llm=llm,
        verbose=True,
        allow_delegation=True
    )
    
    technical_lead = Agent(
        role='Technical Lead',
        goal='Provide technical planning and architecture guidance',
        backstory="""You provide technical leadership, architecture decisions, 
        and help estimate technical complexity of features.""",
        llm=llm,
        verbose=True
    )
    
    # Agile planning tasks
    backlog_creation = Task(
        description="Create product backlog with prioritized user stories",
        agent=product_owner,
        expected_output="Prioritized product backlog with user stories and acceptance criteria"
    )
    
    sprint_planning = Task(
        description="Plan first sprint with capacity and velocity estimation",
        agent=scrum_master,
        expected_output="Sprint plan with committed stories and capacity allocation",
        context=[backlog_creation]
    )
    
    technical_planning = Task(
        description="Create technical architecture and implementation approach",
        agent=technical_lead,
        expected_output="Technical architecture plan and implementation strategy",
        context=[backlog_creation]
    )
    
    release_planning = Task(
        description="Create release plan with major milestones and dependencies",
        agent=scrum_master,
        expected_output="Release plan with quarterly milestones and feature delivery schedule",
        context=[sprint_planning, technical_planning]
    )
    
    return Crew(
        agents=[product_owner, scrum_master, technical_lead],
        tasks=[backlog_creation, sprint_planning, technical_planning, release_planning],
        process=Process.sequential,
        verbose=2
    )


class PlanningMetrics:
    """Track planning effectiveness and outcomes"""
    
    def __init__(self):
        self.planning_phases = []
        self.resource_estimates = []
        self.risk_assessments = []
        self.timeline_accuracy = []
        
    def record_planning_phase(self, phase: str, duration: float, quality_score: float):
        """Record planning phase completion"""
        self.planning_phases.append({
            'phase': phase,
            'duration': duration,
            'quality_score': quality_score,
            'timestamp': datetime.now()
        })
    
    def record_resource_estimate(self, resource_type: str, estimated: float, actual: float):
        """Record resource estimation accuracy"""
        accuracy = 1 - abs(estimated - actual) / max(estimated, actual)
        self.resource_estimates.append({
            'resource_type': resource_type,
            'estimated': estimated,
            'actual': actual,
            'accuracy': accuracy
        })
    
    def record_timeline_milestone(self, milestone: str, planned_date: datetime, 
                                 actual_date: datetime):
        """Record timeline accuracy for milestones"""
        variance_days = (actual_date - planned_date).days
        self.timeline_accuracy.append({
            'milestone': milestone,
            'planned_date': planned_date,
            'actual_date': actual_date,
            'variance_days': variance_days
        })
    
    def get_planning_effectiveness(self) -> Dict[str, Any]:
        """Calculate overall planning effectiveness metrics"""
        if not self.planning_phases:
            return {'insufficient_data': True}
        
        avg_quality = sum(phase['quality_score'] for phase in self.planning_phases) / len(self.planning_phases)
        total_planning_time = sum(phase['duration'] for phase in self.planning_phases)
        
        resource_accuracy = (sum(est['accuracy'] for est in self.resource_estimates) / 
                           len(self.resource_estimates)) if self.resource_estimates else 0
        
        timeline_accuracy = (sum(1 for t in self.timeline_accuracy if abs(t['variance_days']) <= 7) /
                           len(self.timeline_accuracy)) if self.timeline_accuracy else 0
        
        return {
            'planning_phases_completed': len(self.planning_phases),
            'average_planning_quality': avg_quality,
            'total_planning_duration': total_planning_time,
            'resource_estimation_accuracy': resource_accuracy,
            'timeline_accuracy_rate': timeline_accuracy,
            'overall_planning_score': (avg_quality + resource_accuracy + timeline_accuracy) / 3
        }


def run_planning_demo():
    """Demonstrate planning pattern with CrewAI"""
    
    print("=== CrewAI Planning Pattern Demo ===")
    
    # Create and execute planning crew
    crew = create_planning_crew()
    result = crew.kickoff()
    
    print(f"\n=== PLANNING WORKFLOW COMPLETE ===")
    print(f"Result:\n{result}")
    
    return result


if __name__ == "__main__":
    run_planning_demo()