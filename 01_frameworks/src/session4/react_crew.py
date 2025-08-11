# src/session4/react_crew.py
"""
ReAct pattern implementation using CrewAI teams.
Demonstrates Reasoning and Acting in iterative cycles with team coordination.
"""

from crewai import Agent, Task, Crew, Process
from crewai.tools import SerperDevTool, WebsiteSearchTool
from langchain.llms import OpenAI
from typing import Dict, List, Any

def create_react_crew(llm=None):
    """Crew implementing ReAct pattern: Reason -> Act -> Observe -> Reason..."""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Strategic reasoner - thinks through problems
    reasoner = Agent(
        role='Strategic Reasoner',
        goal='Analyze situations logically and develop reasoning-based action plans',
        backstory="""You excel at logical reasoning, problem analysis, and 
        strategic planning. You think through problems step-by-step, consider 
        multiple approaches, and develop clear action plans based on sound reasoning.""",
        llm=llm,
        verbose=True,
        max_iter=4
    )
    
    # Action executor - implements plans
    actor = Agent(
        role='Action Executor', 
        goal='Execute planned actions efficiently and gather comprehensive results',
        backstory="""You specialize in taking concrete actions based on 
        reasoned plans. You execute tasks efficiently, use tools effectively,
        and gather comprehensive feedback about results and outcomes.""",
        tools=[SerperDevTool(), WebsiteSearchTool()],
        llm=llm,
        verbose=True,
        max_iter=3
    )
    
    # Observer and evaluator - assesses outcomes
    observer = Agent(
        role='Result Observer',
        goal='Observe action results critically and evaluate progress toward goals',
        backstory="""You carefully observe action results, evaluate their 
        effectiveness against intended goals, and provide insights for the next 
        reasoning cycle. You identify what worked, what didn't, and why.""",
        llm=llm,
        verbose=True,
        max_iter=2
    )
    
    # Learning synthesizer - captures lessons learned
    synthesizer = Agent(
        role='Learning Synthesizer',
        goal='Synthesize lessons learned across reasoning-action cycles',
        backstory="""You capture insights and lessons learned from multiple 
        reasoning-action cycles, identifying patterns and developing improved 
        approaches for future similar challenges.""",
        llm=llm,
        verbose=True
    )
    
    # Initial reasoning task
    reason_task = Task(
        description="""Reason about how to research 'Best AI Agent Development Practices for Production Systems'.
        
        Think through systematically:
        1. What specific information is needed for production AI agents?
        2. What sources would provide the most valuable insights?
        3. What research approach would be most effective?
        4. What success criteria should guide the research?
        5. What potential challenges or obstacles might arise?
        
        Develop a clear reasoning framework and specific action plan.""",
        agent=reasoner,
        expected_output="Detailed reasoning analysis with logical framework and specific actionable research plan"
    )
    
    # Action execution task
    act_task = Task(
        description="""Execute the reasoned research plan from the Strategic Reasoner.
        
        Take specific actions:
        1. Implement the research strategy as planned
        2. Use tools strategically to gather targeted information
        3. Document detailed findings and sources
        4. Note any unexpected results, challenges, or opportunities
        5. Gather evidence to evaluate plan effectiveness
        
        Be thorough and systematic in execution.""",
        agent=actor,
        expected_output="Comprehensive action results with detailed findings, evidence, and execution notes",
        context=[reason_task]
    )
    
    # Observation and evaluation task
    observe_task = Task(
        description="""Observe and critically evaluate the results of executed actions.
        
        Systematic evaluation:
        1. How well did actions achieve the intended research goals?
        2. What aspects of the approach worked effectively vs. what didn't?
        3. What unexpected insights or challenges emerged during execution?
        4. How could the approach be improved in the next iteration?
        5. What new information changes our understanding of the problem?
        
        Provide detailed evaluation and specific guidance for next reasoning cycle.""",
        agent=observer,
        expected_output="Critical evaluation of action results with specific insights and recommendations for next iteration",
        context=[act_task]
    )
    
    # Re-reasoning task based on observations
    re_reason_task = Task(
        description="""Based on observations and evaluation, refine reasoning and plan next actions.
        
        Updated reasoning process:
        1. Integrate lessons learned from observation feedback
        2. Identify gaps or areas needing deeper investigation
        3. Refine the approach based on what was learned
        4. Plan next actions that address identified issues
        5. Update success criteria based on new insights
        
        Build upon previous work while addressing identified shortcomings.""",
        agent=reasoner,
        expected_output="Refined reasoning with updated approach and improved action plan based on learned insights",
        context=[observe_task]
    )
    
    # Second action cycle
    second_act_task = Task(
        description="""Execute the refined action plan incorporating lessons learned.
        
        Improved execution:
        1. Apply lessons learned from previous cycle
        2. Focus on areas identified as needing more attention
        3. Use refined strategies and approaches
        4. Continue building comprehensive information base
        5. Document improvements in approach and results
        
        Show how learning improved execution effectiveness.""",
        agent=actor,
        expected_output="Second cycle execution results showing improved approach and enhanced findings",
        context=[re_reason_task]
    )
    
    # Final observation and synthesis
    final_observe_task = Task(
        description="""Final observation and synthesis of the complete ReAct process.
        
        Comprehensive analysis:
        1. Compare results between first and second reasoning-action cycles
        2. Evaluate the effectiveness of the ReAct approach overall
        3. Identify key insights discovered through the iterative process
        4. Assess the quality and completeness of final information gathered
        5. Document lessons learned about ReAct pattern implementation
        
        Provide final evaluation of both content results and process effectiveness.""",
        agent=observer,
        expected_output="Final observation report comparing cycles and evaluating overall ReAct process effectiveness",
        context=[second_act_task]
    )
    
    # Learning synthesis task
    synthesis_task = Task(
        description="""Synthesize lessons learned across the entire ReAct process.
        
        Create comprehensive synthesis:
        1. Key insights about production AI agent development (the research topic)
        2. Lessons learned about the ReAct pattern implementation
        3. Process improvements and best practices identified
        4. Effectiveness comparison of different reasoning-action approaches
        5. Recommendations for future ReAct pattern applications
        
        Provide both substantive findings and methodological insights.""",
        agent=synthesizer,
        expected_output="Comprehensive synthesis combining research findings with ReAct methodology insights",
        context=[final_observe_task]
    )
    
    return Crew(
        agents=[reasoner, actor, observer, synthesizer],
        tasks=[reason_task, act_task, observe_task, re_reason_task, 
               second_act_task, final_observe_task, synthesis_task],
        process=Process.sequential,
        verbose=2,
        memory=True
    )


def create_parallel_react_crew(llm=None):
    """Alternative ReAct crew with parallel reasoning streams"""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Multiple reasoners for different perspectives
    technical_reasoner = Agent(
        role='Technical Reasoner',
        goal='Reason about technical aspects and implementation details',
        backstory="""You focus on technical reasoning, architecture decisions, 
        and implementation considerations.""",
        llm=llm,
        verbose=True
    )
    
    business_reasoner = Agent(
        role='Business Reasoner',
        goal='Reason about business value, ROI, and strategic implications',
        backstory="""You focus on business reasoning, value propositions, 
        and strategic considerations.""",
        llm=llm,
        verbose=True
    )
    
    # Shared action executor
    executor = Agent(
        role='Multi-Perspective Executor',
        goal='Execute actions based on multiple reasoning perspectives',
        backstory="""You execute actions that address both technical and 
        business reasoning perspectives.""",
        tools=[SerperDevTool(), WebsiteSearchTool()],
        llm=llm,
        verbose=True
    )
    
    # Shared observer
    observer = Agent(
        role='Multi-Perspective Observer',
        goal='Observe results from multiple reasoning perspectives',
        backstory="""You evaluate results considering both technical and 
        business perspectives.""",
        llm=llm,
        verbose=True
    )
    
    # Parallel reasoning tasks
    tech_reasoning = Task(
        description="Develop technical reasoning approach for AI agent production practices",
        agent=technical_reasoner,
        expected_output="Technical reasoning framework and action plan"
    )
    
    business_reasoning = Task(
        description="Develop business reasoning approach for AI agent production practices",
        agent=business_reasoner,
        expected_output="Business reasoning framework and action plan"
    )
    
    # Combined execution
    combined_execution = Task(
        description="Execute research addressing both technical and business reasoning perspectives",
        agent=executor,
        expected_output="Research results addressing multi-perspective requirements",
        context=[tech_reasoning, business_reasoning]
    )
    
    # Multi-perspective observation
    observation = Task(
        description="Observe results from both technical and business perspectives",
        agent=observer,
        expected_output="Multi-perspective evaluation of research results",
        context=[combined_execution]
    )
    
    return Crew(
        agents=[technical_reasoner, business_reasoner, executor, observer],
        tasks=[tech_reasoning, business_reasoning, combined_execution, observation],
        process=Process.sequential,
        verbose=2
    )


class ReactCycleTracker:
    """Track ReAct cycles and their effectiveness"""
    
    def __init__(self):
        self.cycles = []
        self.reasoning_quality = []
        self.action_effectiveness = []
        self.observation_insights = []
        
    def record_cycle(self, cycle_num: int, reasoning_score: float, 
                    action_score: float, observation_insights: List[str]):
        """Record a complete ReAct cycle"""
        self.cycles.append(cycle_num)
        self.reasoning_quality.append(reasoning_score)
        self.action_effectiveness.append(action_score)
        self.observation_insights.append(observation_insights)
    
    def get_improvement_trend(self) -> Dict[str, Any]:
        """Calculate improvement trends across cycles"""
        if len(self.cycles) < 2:
            return {'insufficient_data': True}
            
        reasoning_trend = self.reasoning_quality[-1] - self.reasoning_quality[0]
        action_trend = self.action_effectiveness[-1] - self.action_effectiveness[0]
        
        return {
            'total_cycles': len(self.cycles),
            'reasoning_improvement': reasoning_trend,
            'action_improvement': action_trend,
            'average_reasoning_quality': sum(self.reasoning_quality) / len(self.reasoning_quality),
            'average_action_effectiveness': sum(self.action_effectiveness) / len(self.action_effectiveness),
            'total_insights_generated': sum(len(insights) for insights in self.observation_insights)
        }
    
    def get_cycle_summary(self) -> Dict[str, Any]:
        """Get summary of all ReAct cycles"""
        return {
            'cycles_completed': len(self.cycles),
            'quality_progression': self.reasoning_quality,
            'effectiveness_progression': self.action_effectiveness,
            'insights_per_cycle': [len(insights) for insights in self.observation_insights],
            'improvement_trends': self.get_improvement_trend()
        }


def run_react_demo():
    """Demonstrate ReAct pattern with CrewAI"""
    
    print("=== CrewAI ReAct Pattern Demo ===")
    
    # Create and execute ReAct crew
    crew = create_react_crew()
    result = crew.kickoff()
    
    print(f"\n=== REACT WORKFLOW COMPLETE ===")
    print(f"Result:\n{result}")
    
    return result


if __name__ == "__main__":
    run_react_demo()