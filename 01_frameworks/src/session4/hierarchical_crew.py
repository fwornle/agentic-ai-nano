# src/session4/hierarchical_crew.py
"""
Hierarchical CrewAI implementation with manager-led delegation.
"""

from crewai import Agent, Task, Crew, Process
from crewai.tools import Tool
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class HierarchicalTeamManager:
    """Manages hierarchical teams with delegation and oversight."""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4", temperature=0.7)
        self.teams = {}
        self.performance_metrics = {}
    
    def create_software_development_team(self):
        """Create a hierarchical software development team."""
        
        # Project Manager (Top of hierarchy)
        project_manager = Agent(
            role='Project Manager',
            goal='Oversee project execution and coordinate team efforts',
            backstory="""You are an experienced project manager with expertise in 
            agile methodologies. You excel at breaking down complex projects, 
            delegating tasks, and ensuring timely delivery.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True,  # Can delegate to team members
            max_iter=5
        )
        
        # Tech Lead (Reports to PM)
        tech_lead = Agent(
            role='Technical Lead',
            goal='Make technical decisions and guide development',
            backstory="""You are a senior technical leader with deep expertise in 
            software architecture. You make critical technical decisions and mentor 
            the development team.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True,  # Can delegate to developers
            max_iter=4
        )
        
        # Senior Developer (Reports to Tech Lead)
        senior_developer = Agent(
            role='Senior Software Developer',
            goal='Implement complex features and solve technical challenges',
            backstory="""You are a skilled senior developer with expertise in 
            multiple programming languages and frameworks. You handle the most 
            challenging implementation tasks.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        # QA Engineer (Reports to Tech Lead)
        qa_engineer = Agent(
            role='Quality Assurance Engineer',
            goal='Ensure software quality through comprehensive testing',
            backstory="""You are a detail-oriented QA engineer who specializes in 
            finding bugs, writing test cases, and ensuring software meets quality 
            standards.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        # Documentation Specialist (Reports to PM)
        doc_specialist = Agent(
            role='Documentation Specialist',
            goal='Create comprehensive technical documentation',
            backstory="""You are a technical writer who excels at creating clear, 
            comprehensive documentation for both technical and non-technical 
            audiences.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        return {
            'manager': project_manager,
            'tech_lead': tech_lead,
            'senior_dev': senior_developer,
            'qa': qa_engineer,
            'docs': doc_specialist
        }
    
    def create_project_tasks(self, project_description: str, team: Dict[str, Agent]):
        """Create hierarchical tasks for a software project."""
        
        # High-level planning task (Manager)
        planning_task = Task(
            description=f"""Create a comprehensive project plan for: {project_description}
            
            Include:
            1. Project scope and objectives
            2. Technical requirements
            3. Resource allocation
            4. Timeline and milestones
            5. Risk assessment
            
            Delegate specific planning aspects to team members as needed.""",
            agent=team['manager'],
            expected_output="Detailed project plan with task breakdown"
        )
        
        # Technical architecture task (Tech Lead)
        architecture_task = Task(
            description="""Design the technical architecture based on project requirements.
            
            Include:
            1. System architecture diagram
            2. Technology stack selection
            3. Database design
            4. API specifications
            5. Security considerations""",
            agent=team['tech_lead'],
            expected_output="Complete technical architecture document",
            context=[planning_task]
        )
        
        # Implementation task (Senior Developer)
        implementation_task = Task(
            description="""Implement core features based on architecture design.
            
            Focus on:
            1. Core business logic
            2. API endpoints
            3. Database integration
            4. Error handling
            5. Performance optimization""",
            agent=team['senior_dev'],
            expected_output="Implemented code with documentation",
            context=[architecture_task]
        )
        
        # Testing task (QA Engineer)
        testing_task = Task(
            description="""Create and execute comprehensive test plan.
            
            Include:
            1. Unit test cases
            2. Integration tests
            3. Performance testing
            4. Security testing
            5. Bug reports and tracking""",
            agent=team['qa'],
            expected_output="Test report with coverage metrics",
            context=[implementation_task]
        )
        
        # Documentation task (Documentation Specialist)
        documentation_task = Task(
            description="""Create complete project documentation.
            
            Include:
            1. User documentation
            2. API documentation
            3. Deployment guide
            4. Troubleshooting guide
            5. Release notes""",
            agent=team['docs'],
            expected_output="Complete documentation package",
            context=[implementation_task, testing_task]
        )
        
        return [planning_task, architecture_task, implementation_task, 
                testing_task, documentation_task]
    
    def create_hierarchical_crew(self, project_description: str):
        """Create a hierarchical crew for project execution."""
        
        team = self.create_software_development_team()
        tasks = self.create_project_tasks(project_description, team)
        
        # Create hierarchical crew with manager
        crew = Crew(
            agents=list(team.values()),
            tasks=tasks,
            process=Process.hierarchical,  # Hierarchical process with delegation
            manager_llm=self.llm,  # Manager uses this LLM for coordination
            verbose=2,
            memory=True,
            cache=True,
            max_rpm=10,
            share_crew=True  # Agents can share context
        )
        
        return crew
    
    def track_performance(self, agent_name: str, task: str, success: bool, duration: float):
        """Track agent performance metrics."""
        
        if agent_name not in self.performance_metrics:
            self.performance_metrics[agent_name] = {
                'tasks_completed': 0,
                'tasks_failed': 0,
                'total_duration': 0,
                'average_duration': 0
            }
        
        metrics = self.performance_metrics[agent_name]
        if success:
            metrics['tasks_completed'] += 1
        else:
            metrics['tasks_failed'] += 1
        
        metrics['total_duration'] += duration
        total_tasks = metrics['tasks_completed'] + metrics['tasks_failed']
        metrics['average_duration'] = metrics['total_duration'] / total_tasks
        
        # Log performance
        print(f"\nPerformance Update for {agent_name}:")
        print(f"  Task: {task}")
        print(f"  Success: {success}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Success Rate: {metrics['tasks_completed']/total_tasks*100:.1f}%")
    
    def generate_team_report(self):
        """Generate performance report for the entire team."""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'team_metrics': self.performance_metrics,
            'summary': {
                'total_agents': len(self.performance_metrics),
                'total_tasks': sum(m['tasks_completed'] + m['tasks_failed'] 
                                 for m in self.performance_metrics.values()),
                'overall_success_rate': self._calculate_overall_success_rate()
            }
        }
        
        return json.dumps(report, indent=2)
    
    def _calculate_overall_success_rate(self):
        """Calculate overall team success rate."""
        
        total_completed = sum(m['tasks_completed'] for m in self.performance_metrics.values())
        total_failed = sum(m['tasks_failed'] for m in self.performance_metrics.values())
        
        if total_completed + total_failed == 0:
            return 0
        
        return (total_completed / (total_completed + total_failed)) * 100

# Example usage
if __name__ == "__main__":
    # Create manager
    manager = HierarchicalTeamManager()
    
    # Define project
    project = "Build a REST API for a task management system with authentication"
    
    # Create and run crew
    crew = manager.create_hierarchical_crew(project)
    result = crew.kickoff()
    
    print(f"\nProject Result:\n{result}")
    
    # Generate performance report
    report = manager.generate_team_report()
    print(f"\nTeam Performance Report:\n{report}")