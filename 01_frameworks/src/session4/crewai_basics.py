# src/session4/crewai_basics.py
"""
Basic CrewAI implementation showing role-based agents and task orchestration.
"""

from crewai import Agent, Task, Crew, Process
from crewai.tools import SerperDevTool, WebsiteSearchTool, FileReadTool
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
import os

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

def create_research_team():
    """Create a research team with specialized agents."""
    
    # Senior Research Analyst
    researcher = Agent(
        role='Senior Research Analyst',
        goal='Conduct thorough research on assigned topics',
        backstory="""You are a senior research analyst with 15 years of experience 
        in gathering and analyzing information from multiple sources. You excel at 
        finding relevant data, identifying patterns, and extracting key insights.""",
        tools=[SerperDevTool(), WebsiteSearchTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,  # Cannot delegate to others
        max_iter=3  # Maximum iterations for task completion
    )
    
    # Data Analyst
    analyst = Agent(
        role='Data Analyst',
        goal='Analyze research data and identify patterns',
        backstory="""You are a skilled data analyst who specializes in processing 
        research findings, identifying trends, and creating actionable insights 
        from complex information.""",
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Content Writer
    writer = Agent(
        role='Content Writer',
        goal='Create compelling, well-structured content',
        backstory="""You are an experienced content writer who transforms research 
        and analysis into engaging, informative content. You have a talent for 
        making complex topics accessible to a broad audience.""",
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Quality Reviewer
    reviewer = Agent(
        role='Quality Assurance Specialist',
        goal='Review and ensure content quality and accuracy',
        backstory="""You are a meticulous quality reviewer with expertise in 
        fact-checking, editing, and ensuring content meets high standards. You 
        have an eye for detail and never let errors slip through.""",
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=True  # Can delegate back for revisions
    )
    
    return [researcher, analyst, writer, reviewer]

def create_research_tasks(agents: List[Agent], topic: str):
    """Create tasks for the research team."""
    
    researcher, analyst, writer, reviewer = agents
    
    # Task 1: Research
    research_task = Task(
        description=f"""Conduct comprehensive research on: {topic}
        
        Your research should include:
        1. Current state and recent developments
        2. Key players and stakeholders
        3. Challenges and opportunities
        4. Future trends and predictions
        
        Provide detailed findings with sources.""",
        agent=researcher,
        expected_output="Comprehensive research report with citations"
    )
    
    # Task 2: Analysis
    analysis_task = Task(
        description="""Analyze the research findings and identify:
        1. Key patterns and trends
        2. Critical insights and implications
        3. Actionable recommendations
        4. Areas requiring further investigation
        
        Create a structured analysis report.""",
        agent=analyst,
        expected_output="Detailed analysis report with insights",
        context=[research_task]  # Depends on research task
    )
    
    # Task 3: Content Creation
    writing_task = Task(
        description="""Create a comprehensive article based on the research and analysis.
        
        The article should:
        1. Have an engaging introduction
        2. Present key findings clearly
        3. Include data-driven insights
        4. Provide actionable conclusions
        5. Be well-structured and readable""",
        agent=writer,
        expected_output="Well-written article ready for publication",
        context=[research_task, analysis_task]  # Depends on both previous tasks
    )
    
    # Task 4: Quality Review
    review_task = Task(
        description="""Review the article for:
        1. Factual accuracy against research
        2. Clarity and readability
        3. Grammar and style
        4. Completeness and coherence
        
        Provide feedback and request revisions if needed.""",
        agent=reviewer,
        expected_output="Quality review report with final approval or revision requests",
        context=[writing_task]  # Depends on writing task
    )
    
    return [research_task, analysis_task, writing_task, review_task]

def run_research_crew(topic: str):
    """Execute the research crew workflow."""
    
    # Create agents and tasks
    agents = create_research_team()
    tasks = create_research_tasks(agents, topic)
    
    # Create crew with sequential process
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,  # Tasks execute in order
        verbose=2,  # Detailed logging
        memory=True,  # Enable memory between tasks
        cache=True,  # Cache results for efficiency
        max_rpm=10  # Rate limiting for API calls
    )
    
    # Execute the crew
    result = crew.kickoff()
    
    return result

if __name__ == "__main__":
    # Example usage
    topic = "The impact of AI agents on software development"
    result = run_research_crew(topic)
    print(f"\nFinal Result:\n{result}")