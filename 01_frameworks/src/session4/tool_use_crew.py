# src/session4/tool_use_crew.py
"""
Tool Use pattern implementation using CrewAI teams.
Demonstrates intelligent tool selection and coordinated tool usage.
"""

from crewai import Agent, Task, Crew, Process
from crewai.tools import (
    SerperDevTool, WebsiteSearchTool, FileReadTool,
    DirectoryReadTool, CodeDocsSearchTool
)
from langchain.llms import OpenAI
from typing import Dict, List, Any

def create_tool_specialist_crew(llm=None):
    """Crew with agents specialized in different tool categories"""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Research tool specialist
    research_specialist = Agent(
        role='Research Tool Specialist',
        goal='Execute research tasks using web search and analysis tools effectively',
        backstory="""You are expert at using research tools to gather, analyze, 
        and synthesize information from web sources. You know how to craft effective 
        search queries, evaluate source credibility, and extract key insights.""",
        tools=[SerperDevTool(), WebsiteSearchTool()],
        llm=llm,
        verbose=True,
        max_iter=4
    )
    
    # File system specialist  
    file_specialist = Agent(
        role='File System Specialist',
        goal='Handle file operations, code analysis, and documentation tasks',
        backstory="""You specialize in file system operations, code analysis, 
        and documentation processing. You can read, analyze, and extract 
        insights from various file formats including code, docs, and data files.""",
        tools=[FileReadTool(), DirectoryReadTool(), CodeDocsSearchTool()],
        llm=llm, 
        verbose=True,
        max_iter=3
    )
    
    # Tool coordinator
    coordinator = Agent(
        role='Tool Coordination Manager',
        goal='Plan tool usage strategy and coordinate between specialists',
        backstory="""You understand the capabilities of different tools and 
        coordinate their optimal usage across team members. You plan tool usage 
        strategies, avoid redundant work, and ensure comprehensive coverage.""",
        llm=llm,
        verbose=True,
        allow_delegation=True,
        max_iter=5
    )
    
    # Quality assessor for tool outputs
    quality_assessor = Agent(
        role='Tool Output Quality Assessor',
        goal='Evaluate the quality and completeness of tool-generated outputs',
        backstory="""You assess the quality, accuracy, and completeness of 
        information gathered using various tools. You identify gaps and suggest 
        additional tool usage to improve results.""",
        llm=llm,
        verbose=True
    )
    
    # Planning task
    planning_task = Task(
        description="""Plan the tool usage strategy for comprehensive analysis of 'AI Agent Frameworks 2024'.
        
        Create strategy for:
        1. Web research tools - what to search for and how
        2. File analysis tools - what documentation/code to examine  
        3. Information synthesis approach
        4. Quality assurance processes
        5. Specialist coordination and task division
        
        Consider tool capabilities, limitations, and optimal usage patterns.""",
        agent=coordinator,
        expected_output="Comprehensive tool usage strategy with specialist assignments and quality gates"
    )
    
    # Research execution
    research_task = Task(
        description="""Execute comprehensive research on AI agent frameworks using web tools.
        
        Research focus:
        1. Latest framework releases and updates (2024)
        2. Performance benchmarks and comparisons
        3. Industry adoption patterns and case studies
        4. Technical capabilities and limitations
        5. Developer community feedback and reviews
        
        Use tools strategically:
        - SerperDevTool for broad search and trend analysis
        - WebsiteSearchTool for deep-dive into specific sites/documentation
        
        Verify information from multiple sources and assess credibility.""",
        agent=research_specialist,
        expected_output="Comprehensive research report with web-sourced data, source citations, and credibility assessment",
        context=[planning_task]
    )
    
    # File analysis task
    file_analysis_task = Task(
        description="""Analyze relevant code repositories, documentation, and technical files.
        
        Analysis targets:
        1. Framework documentation and API references
        2. Example code implementations
        3. Configuration files and setup guides
        4. Performance benchmarks and test results
        5. Community contributed resources
        
        Use tools effectively:
        - FileReadTool for specific file content analysis
        - DirectoryReadTool for repository structure understanding
        - CodeDocsSearchTool for targeted documentation searches
        
        Extract patterns, best practices, and technical insights.""",
        agent=file_specialist,
        expected_output="Technical analysis report with code insights, documentation analysis, and implementation patterns",
        context=[planning_task]
    )
    
    # Quality assessment task
    quality_task = Task(
        description="""Assess the quality and completeness of tool-generated research and analysis.
        
        Evaluate:
        1. Information accuracy and source credibility
        2. Coverage completeness - are there gaps?
        3. Data consistency between different sources
        4. Technical depth and practical applicability  
        5. Actionability of insights generated
        
        Identify:
        - Missing information that additional tool usage could provide
        - Inconsistencies that need resolution
        - Opportunities for deeper analysis
        - Quality issues that need addressing""",
        agent=quality_assessor,
        expected_output="Quality assessment report with gap analysis and recommendations for additional tool usage",
        context=[research_task, file_analysis_task]
    )
    
    # Synthesis task
    synthesis_task = Task(
        description="""Synthesize insights from all tool-based analysis into unified findings.
        
        Create comprehensive synthesis:
        1. Unified findings combining web research and file analysis
        2. Tool effectiveness assessment and lessons learned
        3. Methodology recommendations for similar future tasks
        4. Identification of tool limitations and gaps
        5. Best practices for coordinated tool usage
        
        Address quality assessment findings and ensure completeness.""",
        agent=coordinator,
        expected_output="Synthesized analysis report with unified insights, tool usage evaluation, and methodology recommendations",
        context=[research_task, file_analysis_task, quality_task]
    )
    
    return Crew(
        agents=[coordinator, research_specialist, file_specialist, quality_assessor],
        tasks=[planning_task, research_task, file_analysis_task, quality_task, synthesis_task],
        process=Process.sequential,
        verbose=2,
        memory=True
    )


def create_parallel_tool_crew(llm=None):
    """Alternative crew design with parallel tool usage"""
    
    if llm is None:
        llm = OpenAI(temperature=0.7)
    
    # Multiple specialists working in parallel
    web_researcher = Agent(
        role='Web Research Specialist',
        goal='Conduct comprehensive web research on assigned topics',
        tools=[SerperDevTool(), WebsiteSearchTool()],
        llm=llm,
        verbose=True
    )
    
    code_analyst = Agent(
        role='Code Analysis Specialist', 
        goal='Analyze codebases and technical documentation',
        tools=[FileReadTool(), DirectoryReadTool(), CodeDocsSearchTool()],
        llm=llm,
        verbose=True
    )
    
    data_synthesizer = Agent(
        role='Data Synthesis Specialist',
        goal='Combine and synthesize information from multiple tool sources',
        llm=llm,
        verbose=True
    )
    
    # Parallel research tasks
    web_research = Task(
        description="Research AI agent frameworks using web tools",
        agent=web_researcher,
        expected_output="Web research findings with source citations"
    )
    
    code_analysis = Task(
        description="Analyze framework codebases and documentation",
        agent=code_analyst,
        expected_output="Code analysis report with technical insights"
    )
    
    # Synthesis task that depends on both parallel tasks
    synthesis = Task(
        description="Synthesize web research and code analysis into unified report",
        agent=data_synthesizer,
        expected_output="Unified analysis combining all tool-generated insights",
        context=[web_research, code_analysis]
    )
    
    return Crew(
        agents=[web_researcher, code_analyst, data_synthesizer],
        tasks=[web_research, code_analysis, synthesis],
        process=Process.sequential,  # Sequential process with parallel task dependencies
        verbose=2
    )


class ToolUsageTracker:
    """Track tool usage patterns and effectiveness"""
    
    def __init__(self):
        self.tool_usage = {}
        self.success_rates = {}
        self.execution_times = {}
        
    def record_tool_usage(self, tool_name: str, success: bool, execution_time: float):
        """Record tool usage event"""
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
            self.success_rates[tool_name] = []
            self.execution_times[tool_name] = []
            
        self.tool_usage[tool_name] += 1
        self.success_rates[tool_name].append(success)
        self.execution_times[tool_name].append(execution_time)
    
    def get_tool_effectiveness(self, tool_name: str) -> Dict[str, Any]:
        """Get effectiveness metrics for a specific tool"""
        if tool_name not in self.tool_usage:
            return {}
            
        success_rate = sum(self.success_rates[tool_name]) / len(self.success_rates[tool_name])
        avg_execution_time = sum(self.execution_times[tool_name]) / len(self.execution_times[tool_name])
        
        return {
            'usage_count': self.tool_usage[tool_name],
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'effectiveness_score': success_rate * (1 / avg_execution_time) if avg_execution_time > 0 else 0
        }
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of all tool usage"""
        summary = {}
        for tool_name in self.tool_usage.keys():
            summary[tool_name] = self.get_tool_effectiveness(tool_name)
        return summary


def run_tool_use_demo():
    """Demonstrate tool use pattern with CrewAI"""
    
    print("=== CrewAI Tool Use Pattern Demo ===")
    
    # Create and execute specialized tool crew
    crew = create_tool_specialist_crew()
    result = crew.kickoff()
    
    print(f"\n=== TOOL USE WORKFLOW COMPLETE ===")
    print(f"Result:\n{result}")
    
    return result


if __name__ == "__main__":
    run_tool_use_demo()