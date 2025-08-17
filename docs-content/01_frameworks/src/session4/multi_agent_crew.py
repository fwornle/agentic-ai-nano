# src/session4/multi_agent_crew.py
"""
Multi-agent collaboration pattern implementation using CrewAI teams.
Demonstrates complex team coordination, consensus building, and collaborative decision-making.
"""

from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI
from typing import Dict, List, Any, Optional
import json

def create_collaborative_crew(llm=None):
    """Multi-agent crew with complex collaboration patterns and consensus building"""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Domain experts with different perspectives
    tech_expert = Agent(
        role='Technical Architecture Expert',
        goal='Provide technical expertise, architectural guidance, and implementation insights',
        backstory="""You are a senior technical architect with 20+ years of experience 
        in system design, scalability, and technical implementation. You focus on 
        technical feasibility, performance, security, and maintainability. You think 
        deeply about technical trade-offs and long-term implications.""",
        llm=llm,
        verbose=True,
        max_iter=4
    )
    
    business_expert = Agent(
        role='Business Strategy Expert',
        goal='Provide business perspective, strategic guidance, and market insights',
        backstory="""You are a business strategist with expertise in market analysis, 
        business models, and strategic planning. You focus on ROI, market opportunity, 
        competitive advantage, and business value creation. You understand how 
        technology decisions impact business outcomes.""",
        llm=llm,
        verbose=True,
        max_iter=4
    )
    
    user_expert = Agent(
        role='User Experience Expert',
        goal='Provide user-centric perspective, usability guidance, and adoption insights',
        backstory="""You are a UX expert focused on user needs, usability, and 
        human-centered design principles. You understand user behavior, adoption 
        patterns, and how to create technology that people actually want to use. 
        You advocate for the end-user perspective in all decisions.""",
        llm=llm,
        verbose=True,
        max_iter=4
    )
    
    operations_expert = Agent(
        role='Operations Expert',
        goal='Provide operational perspective on deployment, maintenance, and support',
        backstory="""You are an operations expert with deep experience in system 
        deployment, monitoring, maintenance, and support. You understand what it 
        takes to run systems reliably in production and support them long-term.""",
        llm=llm,
        verbose=True,
        max_iter=3
    )
    
    # Collaboration facilitator
    facilitator = Agent(
        role='Collaboration Facilitator',
        goal='Facilitate expert collaboration, build consensus, and resolve conflicts',
        backstory="""You excel at facilitating discussions between diverse experts, 
        identifying common ground, building consensus on complex decisions, and 
        helping teams work through disagreements constructively. You have strong 
        emotional intelligence and conflict resolution skills.""",
        llm=llm,
        verbose=True,
        allow_delegation=True,
        max_iter=5
    )
    
    # Decision synthesizer
    synthesizer = Agent(
        role='Decision Synthesizer',
        goal='Synthesize expert inputs into unified decisions and balanced recommendations',
        backstory="""You specialize in synthesizing diverse expert opinions into 
        coherent decisions and actionable recommendations. You can find creative 
        solutions that address multiple stakeholder needs and create win-win outcomes.""",
        llm=llm,
        verbose=True,
        max_iter=4
    )
    
    # Expert input tasks (can run in parallel)
    tech_input_task = Task(
        description="""Provide comprehensive technical perspective on 'Building a Customer Service AI Agent Platform'.
        
        Technical analysis focus:
        1. Architecture requirements and design patterns
        2. Scalability needs for handling 10,000+ concurrent conversations
        3. Integration challenges with existing customer service systems
        4. Technology stack recommendations (frameworks, databases, infrastructure)
        5. Performance requirements and optimization strategies
        6. Security considerations for customer data and privacy
        7. Monitoring, logging, and observability requirements
        8. Technical risk factors and mitigation strategies
        9. Development and deployment complexity assessment
        10. Long-term technical maintainability and evolution
        
        Provide specific, actionable technical recommendations with rationale.""",
        agent=tech_expert,
        expected_output="Comprehensive technical analysis with architecture recommendations, risk assessment, and implementation guidance"
    )
    
    business_input_task = Task(
        description="""Provide comprehensive business perspective on 'Building a Customer Service AI Agent Platform'.
        
        Business analysis focus:
        1. Market opportunity and competitive landscape analysis
        2. Business value proposition and ROI calculations
        3. Revenue model and pricing strategy considerations
        4. Cost-benefit analysis including development and operational costs
        5. Market timing and competitive positioning
        6. Customer acquisition and retention strategies
        7. Partnership and integration opportunities
        8. Regulatory and compliance considerations
        9. Business risk factors and mitigation strategies
        10. Strategic alignment with company goals and objectives
        
        Provide specific business recommendations with quantitative analysis where possible.""",
        agent=business_expert,
        expected_output="Comprehensive business analysis with ROI projections, market strategy, and business risk assessment"
    )
    
    user_input_task = Task(
        description="""Provide comprehensive user experience perspective on 'Building a Customer Service AI Agent Platform'.
        
        UX analysis focus:
        1. User journey mapping for customers seeking support
        2. Interaction design requirements for natural conversations
        3. Accessibility requirements for diverse user populations
        4. Usability considerations for both customers and support agents
        5. User adoption factors and change management needs
        6. Experience quality metrics and measurement approaches
        7. User feedback integration and continuous improvement
        8. Multi-channel experience consistency (web, mobile, voice)
        9. User trust and confidence building mechanisms
        10. Cultural and language considerations for global deployment
        
        Provide specific UX recommendations with user research insights and design principles.""",
        agent=user_expert,
        expected_output="Comprehensive UX analysis with user journey maps, design requirements, and adoption strategy"
    )
    
    operations_input_task = Task(
        description="""Provide comprehensive operations perspective on 'Building a Customer Service AI Agent Platform'.
        
        Operations analysis focus:
        1. Deployment strategy and infrastructure requirements
        2. Monitoring and alerting system design
        3. Incident response and problem resolution procedures
        4. Capacity planning and auto-scaling requirements
        5. Backup, disaster recovery, and business continuity
        6. Security operations and threat response
        7. Performance monitoring and optimization
        8. Support and maintenance procedures
        9. Change management and release processes
        10. Compliance auditing and reporting requirements
        
        Provide specific operational recommendations with procedures and metrics.""",
        agent=operations_expert,
        expected_output="Comprehensive operations analysis with deployment strategy, monitoring plan, and maintenance procedures"
    )
    
    # Collaboration facilitation task
    facilitation_task = Task(
        description="""Facilitate collaboration between all domain experts to identify synergies, conflicts, and opportunities.
        
        Facilitation objectives:
        1. Identify areas of strong agreement and alignment between experts
        2. Surface points of disagreement, tension, or conflicting priorities
        3. Find opportunities for creative synthesis and win-win solutions
        4. Highlight trade-offs that require explicit decision-making
        5. Identify shared priorities and common values across perspectives
        6. Map dependencies and interactions between different expert domains
        7. Facilitate constructive discussion of conflicting viewpoints
        8. Build foundation for consensus building in next phase
        
        Create framework for productive collaboration and decision-making.""",
        agent=facilitator,
        expected_output="Collaboration analysis with consensus opportunities, conflict areas, and framework for resolution",
        context=[tech_input_task, business_input_task, user_input_task, operations_input_task]
    )
    
    # Consensus building task
    consensus_task = Task(
        description="""Build consensus on key decisions for the AI agent platform project.
        
        Consensus building focus:
        1. Resolve disagreements between expert perspectives constructively
        2. Find creative solutions that address multiple stakeholder needs
        3. Prioritize conflicting requirements using agreed-upon criteria
        4. Create shared understanding of trade-offs and their implications
        5. Establish decision-making frameworks for ongoing choices
        6. Build commitment to agreed-upon approaches across all experts
        7. Document areas where consensus was achieved and methods used
        8. Identify decisions that require escalation or additional input
        
        Use collaborative problem-solving techniques to build genuine consensus.""",
        agent=facilitator,
        expected_output="Consensus framework with agreed-upon decisions, trade-off criteria, and commitment from all experts",
        context=[facilitation_task]
    )
    
    # Conflict resolution task (if needed)
    conflict_resolution_task = Task(
        description="""Address any remaining conflicts or disagreements that couldn't be resolved through consensus building.
        
        Conflict resolution approach:
        1. Identify root causes of persistent disagreements
        2. Explore alternative solutions not yet considered
        3. Use structured decision-making frameworks (cost-benefit, risk analysis)
        4. Seek expert input on creative compromise solutions
        5. Document trade-offs and rationale for difficult decisions
        6. Ensure all perspectives are heard and understood
        7. Build acceptance even when perfect agreement isn't possible
        8. Create mechanisms for revisiting decisions based on new information
        
        Focus on constructive resolution that maintains team cohesion.""",
        agent=facilitator,
        expected_output="Conflict resolution outcomes with rationale, compromise solutions, and team alignment",
        context=[consensus_task]
    )
    
    # Final synthesis task
    synthesis_task = Task(
        description="""Synthesize all expert inputs and consensus into comprehensive, unified recommendations.
        
        Synthesis objectives:
        1. Create unified project recommendations addressing all expert perspectives
        2. Develop multi-perspective implementation plan with clear phases
        3. Document balanced trade-off decisions with rationale
        4. Integrate risk mitigation strategies from all domains
        5. Establish success metrics across technical, business, UX, and operational dimensions
        6. Create governance framework for ongoing multi-perspective decision-making
        7. Provide implementation roadmap that addresses all stakeholder needs
        8. Document lessons learned from the collaborative decision-making process
        
        Ensure final recommendations are comprehensive, balanced, and actionable.""",
        agent=synthesizer,
        expected_output="Comprehensive synthesis with unified recommendations, multi-perspective implementation plan, and balanced trade-off decisions",
        context=[consensus_task, conflict_resolution_task]
    )
    
    return Crew(
        agents=[tech_expert, business_expert, user_expert, operations_expert, facilitator, synthesizer],
        tasks=[tech_input_task, business_input_task, user_input_task, operations_input_task, 
               facilitation_task, consensus_task, conflict_resolution_task, synthesis_task],
        process=Process.sequential,  # Could also use hierarchical with facilitator as manager
        verbose=2,
        memory=True
    )


def create_debate_crew(llm=None):
    """Alternative multi-agent crew focused on structured debate and argumentation"""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Debate participants
    advocate = Agent(
        role='Solution Advocate',
        goal='Present strongest possible arguments for the proposed solution',
        backstory="""You are skilled at building compelling cases and presenting 
        strong arguments in favor of proposed solutions.""",
        llm=llm,
        verbose=True
    )
    
    skeptic = Agent(
        role='Critical Skeptic',
        goal='Challenge assumptions and present counter-arguments',
        backstory="""You are skilled at finding flaws, challenging assumptions, 
        and presenting strong counter-arguments to test ideas thoroughly.""",
        llm=llm,
        verbose=True
    )
    
    moderator = Agent(
        role='Debate Moderator',
        goal='Facilitate fair debate and synthesize insights from both sides',
        backstory="""You facilitate structured debates, ensure fair representation 
        of all viewpoints, and synthesize insights from different perspectives.""",
        llm=llm,
        verbose=True,
        allow_delegation=True
    )
    
    # Debate structure
    opening_arguments = Task(
        description="Present opening arguments for building the AI agent platform",
        agent=advocate,
        expected_output="Compelling case with evidence and reasoning"
    )
    
    counter_arguments = Task(
        description="Present counter-arguments and challenges to the proposal",
        agent=skeptic,
        expected_output="Critical analysis highlighting risks and alternatives",
        context=[opening_arguments]
    )
    
    rebuttal = Task(
        description="Respond to counter-arguments with additional evidence",
        agent=advocate,
        expected_output="Rebuttal addressing skeptic's concerns",
        context=[counter_arguments]
    )
    
    synthesis = Task(
        description="Synthesize insights from the debate into balanced recommendations",
        agent=moderator,
        expected_output="Balanced synthesis incorporating insights from both sides",
        context=[opening_arguments, counter_arguments, rebuttal]
    )
    
    return Crew(
        agents=[advocate, skeptic, moderator],
        tasks=[opening_arguments, counter_arguments, rebuttal, synthesis],
        process=Process.sequential,
        verbose=2
    )


class CollaborationMetrics:
    """Track multi-agent collaboration effectiveness"""
    
    def __init__(self):
        self.consensus_scores = []
        self.conflict_resolutions = []
        self.participation_rates = {}
        self.decision_quality_scores = []
        
    def record_consensus_attempt(self, topic: str, initial_agreement: float, 
                                final_agreement: float, rounds: int):
        """Record consensus building attempt"""
        self.consensus_scores.append({
            'topic': topic,
            'initial_agreement': initial_agreement,
            'final_agreement': final_agreement,
            'improvement': final_agreement - initial_agreement,
            'rounds_needed': rounds
        })
    
    def record_conflict_resolution(self, conflict_type: str, resolution_method: str, 
                                 success: bool, time_taken: float):
        """Record conflict resolution attempt"""
        self.conflict_resolutions.append({
            'conflict_type': conflict_type,
            'resolution_method': resolution_method,
            'success': success,
            'time_taken': time_taken
        })
    
    def record_participation(self, agent_role: str, contributions: int, quality_score: float):
        """Record agent participation in collaboration"""
        if agent_role not in self.participation_rates:
            self.participation_rates[agent_role] = []
        
        self.participation_rates[agent_role].append({
            'contributions': contributions,
            'quality_score': quality_score
        })
    
    def record_decision_quality(self, decision: str, quality_score: float, 
                               stakeholder_satisfaction: float):
        """Record quality of collaborative decisions"""
        self.decision_quality_scores.append({
            'decision': decision,
            'quality_score': quality_score,
            'stakeholder_satisfaction': stakeholder_satisfaction
        })
    
    def get_collaboration_effectiveness(self) -> Dict[str, Any]:
        """Calculate overall collaboration effectiveness"""
        if not self.consensus_scores:
            return {'insufficient_data': True}
        
        avg_consensus_improvement = sum(score['improvement'] for score in self.consensus_scores) / len(self.consensus_scores)
        avg_consensus_rounds = sum(score['rounds_needed'] for score in self.consensus_scores) / len(self.consensus_scores)
        
        conflict_success_rate = (sum(1 for res in self.conflict_resolutions if res['success']) / 
                               len(self.conflict_resolutions)) if self.conflict_resolutions else 0
        
        avg_decision_quality = (sum(decision['quality_score'] for decision in self.decision_quality_scores) /
                              len(self.decision_quality_scores)) if self.decision_quality_scores else 0
        
        return {
            'consensus_building_effectiveness': avg_consensus_improvement,
            'average_rounds_to_consensus': avg_consensus_rounds,
            'conflict_resolution_success_rate': conflict_success_rate,
            'average_decision_quality': avg_decision_quality,
            'total_consensus_attempts': len(self.consensus_scores),
            'total_conflicts_resolved': len(self.conflict_resolutions),
            'overall_collaboration_score': (avg_consensus_improvement + conflict_success_rate + avg_decision_quality) / 3
        }


def create_hierarchical_collaboration_crew(llm=None):
    """Hierarchical multi-agent crew with manager coordination"""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Manager coordinates collaboration
    manager = Agent(
        role='Collaboration Manager',
        goal='Coordinate multi-expert collaboration and drive decisions',
        backstory="""You coordinate collaboration between diverse experts, 
        facilitate decision-making, and ensure productive outcomes.""",
        llm=llm,
        verbose=True,
        allow_delegation=True
    )
    
    # Expert team members
    experts = [
        Agent(
            role=f'Expert {i}',
            goal=f'Provide specialized expertise in domain {i}',
            backstory=f"""You are a domain expert specializing in area {i}.""",
            llm=llm,
            verbose=True
        ) for i in range(3)
    ]
    
    # Manager-driven tasks
    coordination_task = Task(
        description="Coordinate expert collaboration on AI platform decision",
        agent=manager,
        expected_output="Coordination plan and expert assignments"
    )
    
    expert_tasks = [
        Task(
            description=f"Provide expert analysis from perspective {i}",
            agent=expert,
            expected_output=f"Expert analysis {i}",
            context=[coordination_task]
        ) for i, expert in enumerate(experts)
    ]
    
    final_decision = Task(
        description="Make final decision based on expert inputs",
        agent=manager,
        expected_output="Final collaborative decision with rationale",
        context=expert_tasks
    )
    
    return Crew(
        agents=[manager] + experts,
        tasks=[coordination_task] + expert_tasks + [final_decision],
        process=Process.hierarchical,
        manager_llm=llm,
        verbose=2
    )


def run_collaboration_demo():
    """Demonstrate multi-agent collaboration pattern with CrewAI"""
    
    print("=== CrewAI Multi-Agent Collaboration Pattern Demo ===")
    
    # Create and execute collaborative crew
    crew = create_collaborative_crew()
    result = crew.kickoff()
    
    print(f"\n=== COLLABORATION WORKFLOW COMPLETE ===")
    print(f"Result:\n{result}")
    
    return result


if __name__ == "__main__":
    run_collaboration_demo()