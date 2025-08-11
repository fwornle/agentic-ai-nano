# src/session4/reflection_crew.py
"""
Reflection pattern implementation using CrewAI teams.
Demonstrates self-improvement through iterative review and refinement.
"""

from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI
from typing import Dict, Any

def create_reflection_crew(llm=None):
    """Crew that implements reflection pattern for continuous improvement"""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Primary worker agent
    worker = Agent(
        role='Content Creator',
        goal='Create high-quality content through iterative improvement',
        backstory="""You create content and continuously improve it through 
        self-reflection and feedback incorporation. You take pride in producing 
        excellent work and are always willing to refine your outputs.""",
        llm=llm,
        verbose=True,
        max_iter=3
    )
    
    # Reflection agent - provides self-critique  
    reflector = Agent(
        role='Self-Reflection Specialist', 
        goal='Provide honest self-critique and improvement suggestions',
        backstory="""You are the critical inner voice that evaluates work objectively 
        and suggests specific improvements. You focus on quality, clarity, and impact.
        You are constructive but demanding in your standards.""",
        llm=llm,
        verbose=True
    )
    
    # Quality gate agent
    quality_judge = Agent(
        role='Quality Judge',
        goal='Determine if work meets quality standards or needs more iteration',
        backstory="""You are an impartial judge of quality who decides whether 
        work is ready for publication or needs further refinement. You have high 
        standards but are fair in your assessments.""",
        llm=llm,
        verbose=True
    )
    
    # Initial creation task
    create_task = Task(
        description="""Create initial content on: 'The Future of AI Agents in Enterprise'.
        
        Requirements:
        - 800-1000 words
        - Include current state, trends, and predictions
        - Focus on business value and practical applications
        - Use clear, engaging writing style""",
        agent=worker,
        expected_output="First draft of enterprise AI agents article"
    )
    
    # Reflection task
    reflect_task = Task(
        description="""Reflect on the created content and provide detailed critique.
        
        Evaluate:
        1. Content quality and depth of analysis
        2. Clarity and logical structure  
        3. Engagement and readability
        4. Completeness and missing elements
        5. Accuracy and credibility
        
        Provide specific, actionable improvement suggestions.
        Be constructively critical and detailed in your feedback.""",
        agent=reflector,
        expected_output="Detailed self-critique with specific improvement suggestions",
        context=[create_task]
    )
    
    # Improvement task
    improve_task = Task(
        description="""Improve the content based on reflection feedback.
        
        Actions:
        - Address all feedback points systematically
        - Enhance weak areas identified in reflection
        - Maintain strengths while fixing weaknesses
        - Ensure improvements align with original goals
        
        Document what changes you made and why.""",
        agent=worker,
        expected_output="Improved version of content with change documentation",
        context=[create_task, reflect_task]
    )
    
    # Quality evaluation task  
    evaluate_task = Task(
        description="""Evaluate if the improved content meets quality standards.
        
        Assessment criteria:
        - Content depth and insight quality (1-10)
        - Writing clarity and flow (1-10) 
        - Engagement and readability (1-10)
        - Completeness and coverage (1-10)
        - Overall professional standard (1-10)
        
        Decision rules:
        - APPROVED: Average score >= 8.0
        - NEEDS_WORK: Average score < 8.0
        
        Provide specific reasoning for the decision and scores.""",
        agent=quality_judge,
        expected_output="Quality evaluation with APPROVED/NEEDS_WORK decision and detailed scoring",
        context=[improve_task]
    )
    
    # Second reflection cycle if needed
    second_reflect_task = Task(
        description="""If content was not approved, conduct second reflection cycle.
        
        Focus on:
        - Why previous improvements were insufficient
        - What additional changes are needed
        - How to achieve the required quality level
        - Alternative approaches to consider""",
        agent=reflector,
        expected_output="Second reflection with deeper analysis and suggestions",
        context=[evaluate_task]
    )
    
    # Final improvement task
    final_improve_task = Task(
        description="""Make final improvements to achieve approval standard.
        
        This is your final opportunity to meet quality requirements.
        - Implement all critical feedback
        - Ensure professional publication quality
        - Verify all requirements are met""",
        agent=worker,
        expected_output="Final improved content meeting quality standards",
        context=[second_reflect_task]
    )
    
    return Crew(
        agents=[worker, reflector, quality_judge],
        tasks=[create_task, reflect_task, improve_task, evaluate_task, 
               second_reflect_task, final_improve_task],
        process=Process.sequential,
        verbose=2,
        memory=True
    )


def run_reflection_workflow():
    """Execute the reflection pattern workflow"""
    
    print("=== CrewAI Reflection Pattern Demo ===")
    
    # Create and execute crew
    crew = create_reflection_crew()
    result = crew.kickoff()
    
    print(f"\n=== REFLECTION WORKFLOW COMPLETE ===")
    print(f"Final Result:\n{result}")
    
    return result


class ReflectionMetrics:
    """Track reflection pattern effectiveness"""
    
    def __init__(self):
        self.iterations = 0
        self.quality_scores = []
        self.improvements_made = []
        
    def record_iteration(self, quality_score: float, improvements: list):
        """Record reflection iteration metrics"""
        self.iterations += 1
        self.quality_scores.append(quality_score)
        self.improvements_made.extend(improvements)
        
    def get_improvement_rate(self) -> float:
        """Calculate quality improvement rate"""
        if len(self.quality_scores) < 2:
            return 0.0
        return (self.quality_scores[-1] - self.quality_scores[0]) / self.iterations
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get reflection metrics summary"""
        return {
            'total_iterations': self.iterations,
            'final_quality_score': self.quality_scores[-1] if self.quality_scores else 0,
            'improvement_rate': self.get_improvement_rate(),
            'total_improvements': len(self.improvements_made),
            'quality_progression': self.quality_scores
        }


if __name__ == "__main__":
    run_reflection_workflow()