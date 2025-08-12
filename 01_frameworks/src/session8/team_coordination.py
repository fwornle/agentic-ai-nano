# Multi-Agent Team Coordination and Orchestration
# Production-ready team workflows and specialized agent coordination

from agno import Team, Workflow
from agno.agents import SpecializedAgent
from agno.coordination import TaskRouter, LoadBalancer, PriorityQueue
from agno.workflows import SequentialFlow, ParallelFlow, ConditionalFlow
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class WorkflowRequest:
    """Request for workflow execution"""
    task_description: str
    priority: TaskPriority
    max_execution_time: timedelta
    requirements: Dict[str, Any]
    context: Dict[str, Any] = None


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    workflow_id: str
    team_used: Optional[str] = None
    execution_time: float = 0
    result: Any = None
    success: bool = False
    error: Optional[str] = None


class WorkflowMonitor:
    """Monitoring and logging for workflow execution"""
    
    def __init__(self, workflow_id: str, team_name: str):
        self.workflow_id = workflow_id
        self.team_name = team_name
        self.start_time = datetime.now()
        self.events = []
    
    def log_success(self, result: Any):
        """Log successful workflow completion"""
        self.events.append({
            "type": "success",
            "timestamp": datetime.now(),
            "result": str(result)[:100]  # Truncate for logging
        })
    
    def log_timeout(self):
        """Log workflow timeout"""
        self.events.append({
            "type": "timeout", 
            "timestamp": datetime.now(),
            "duration": (datetime.now() - self.start_time).total_seconds()
        })
    
    def log_error(self, error: Exception):
        """Log workflow error"""
        self.events.append({
            "type": "error",
            "timestamp": datetime.now(),
            "error": str(error)
        })
    
    async def finalize(self):
        """Complete monitoring and store results"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        print(f"Workflow {self.workflow_id} completed in {total_time:.2f}s")
        # In production, this would write to monitoring system


class WorkflowTimeoutError(Exception):
    """Raised when workflow exceeds time limits"""
    pass


class ProductionTeamOrchestrator:
    """Enterprise-grade multi-agent team management"""
    
    def __init__(self):
        # Core coordination infrastructure
        self.task_router = TaskRouter()        # Routes tasks to appropriate agents
        self.load_balancer = LoadBalancer()    # Distributes load across agent instances
        self.priority_queue = PriorityQueue()  # Manages task priorities and scheduling
        
        # Performance tracking
        self.team_metrics = {
            "tasks_completed": 0,
            "average_completion_time": 0,
            "agent_utilization": {},
            "workflow_success_rate": 0
        }
        
        # Initialize specialized agents and teams
        self.agents = self._initialize_specialized_agents()
        self.teams = self._create_specialized_teams()
        
        print(f"Team orchestrator initialized with {len(self.agents)} agents")
    
    def _initialize_specialized_agents(self) -> Dict[str, SpecializedAgent]:
        """Initialize agents optimized for specific capabilities"""
        
        agents = {
            # Fast, high-throughput agent for data collection
            "data_collector": SpecializedAgent(
                name="data_collector",
                model="gpt-4o-mini",              # Fast model for throughput
                tools=["web_search", "database_query", "api_client"],
                instructions="""
                Collect comprehensive data efficiently from multiple sources.
                Focus on accuracy and completeness over analysis.
                """,
                max_concurrent_tasks=5,           # High concurrency for I/O bound tasks
                timeout=30,                       # Quick timeout for responsiveness
                resource_limits={"cpu": "low", "memory": "medium"}
            ),
            
            # Powerful agent for deep analysis work
            "data_analyzer": SpecializedAgent(
                name="data_analyzer", 
                model="gpt-4o",                   # Powerful model for complex reasoning
                tools=["statistical_analysis", "trend_detection", "visualization"],
                instructions="""
                Perform thorough analysis on provided data.
                Identify patterns, trends, and actionable insights.
                Provide statistical confidence levels for findings.
                """,
                max_concurrent_tasks=3,           # Lower concurrency for compute-intensive tasks
                timeout=120,                      # Longer timeout for complex analysis
                resource_limits={"cpu": "high", "memory": "high"}
            ),
            
            # Specialized writer for content generation
            "report_writer": SpecializedAgent(
                name="report_writer",
                model="gpt-4o",
                tools=["document_formatter", "template_engine"],
                instructions="""
                Generate high-quality written content from analysis results.
                Focus on clarity, structure, and actionable recommendations.
                Follow enterprise writing standards and formatting.
                """,
                max_concurrent_tasks=2,
                timeout=90,
                resource_limits={"cpu": "medium", "memory": "medium"}
            ),
            
            # Quality assurance agent
            "quality_reviewer": SpecializedAgent(
                name="quality_reviewer",
                model="gpt-4o",
                tools=["quality_checker", "compliance_validator"],
                instructions="""
                Review content for accuracy, completeness, and compliance.
                Verify all claims are supported by data.
                Ensure outputs meet enterprise quality standards.
                """,
                max_concurrent_tasks=2,
                timeout=60,
                resource_limits={"cpu": "medium", "memory": "low"}
            )
        }
        
        # Track agent initialization success
        self.team_metrics["agent_utilization"] = {
            name: {"active_tasks": 0, "completed_tasks": 0, "error_rate": 0.0}
            for name in agents.keys()
        }
        
        return agents
    
    def _create_specialized_teams(self) -> Dict[str, Team]:
        """Create teams optimized for different workflow patterns"""
        
        teams = {}
        
        # Research team: Parallel data collection + sequential analysis
        teams["research"] = Team(
            name="research_team",
            agents=[self.agents["data_collector"], self.agents["data_analyzer"]],
            workflow=self._create_research_workflow(),
            coordination_pattern="producer_consumer",  # Data collector feeds analyzer
            max_execution_time=300,                    # 5 minute timeout
            retry_failed_tasks=True,
            quality_gates_enabled=True
        )
        
        # Content team: Sequential analysis -> writing -> review
        teams["content"] = Team(
            name="content_team",
            agents=[
                self.agents["data_analyzer"],
                self.agents["report_writer"],
                self.agents["quality_reviewer"]
            ],
            workflow=self._create_content_workflow(),
            coordination_pattern="pipeline",           # Sequential pipeline
            max_execution_time=600,                    # 10 minute timeout
            retry_failed_tasks=True,
            quality_gates_enabled=True
        )
        
        return teams
    
    def _create_research_workflow(self) -> ParallelFlow:
        """Create optimized research workflow with proper dependencies"""
        
        return ParallelFlow([
            # Phase 1: Parallel data collection from multiple sources
            {
                "name": "data_collection_phase",
                "agent": "data_collector",
                "tasks": [
                    {"type": "web_research", "priority": "high", "timeout": 30},
                    {"type": "database_search", "priority": "medium", "timeout": 60},
                    {"type": "api_queries", "priority": "medium", "timeout": 45}
                ],
                "execution_mode": "parallel",         # Execute all collection tasks simultaneously
                "success_threshold": 0.67,           # 2 of 3 sources must succeed
                "aggregate_results": True
            },
            
            # Phase 2: Sequential analysis of collected data
            {
                "name": "data_analysis_phase", 
                "agent": "data_analyzer",
                "depends_on": ["data_collection_phase"],  # Wait for collection to complete
                "tasks": [
                    {"type": "trend_analysis", "input_from": "data_collection_phase"},
                    {"type": "statistical_summary", "input_from": "data_collection_phase"}
                ],
                "execution_mode": "sequential",      # Analysis tasks have dependencies
                "quality_check": {
                    "confidence_threshold": 0.8,    # Require high confidence in results
                    "completeness_check": True       # Ensure all data was analyzed
                }
            }
        ])
    
    def _create_content_workflow(self) -> SequentialFlow:
        """Create content generation workflow"""
        
        return SequentialFlow([
            {
                "agent": "data_analyzer",
                "task": "analysis_for_content",
                "output_format": "structured_insights"
            },
            {
                "agent": "report_writer", 
                "task": "generate_content",
                "input_from": "data_analyzer"
            },
            {
                "agent": "quality_reviewer",
                "task": "review_and_approve",
                "input_from": "report_writer"
            }
        ])
    
    async def orchestrate_complex_workflow(self, 
                                         workflow_request: WorkflowRequest) -> WorkflowResult:
        """Coordinate complex multi-team workflow with fault tolerance"""
        
        workflow_id = f"workflow_{int(datetime.now().timestamp())}"
        start_time = datetime.now()
        
        try:
            # Route task to appropriate team based on requirements
            selected_team = await self.task_router.select_team(
                request=workflow_request,
                available_teams=self.teams,
                selection_criteria={
                    "capability_match": 0.8,        # Team must have 80% capability match
                    "current_load": "prefer_low",   # Prefer less busy teams
                    "historical_performance": True  # Consider past performance
                }
            )
            
            # Add to priority queue with SLA requirements
            await self.priority_queue.enqueue(
                workflow_id=workflow_id,
                team=selected_team,
                request=workflow_request,
                priority=workflow_request.priority,
                sla_deadline=start_time + workflow_request.max_execution_time
            )
            
            # Execute workflow with monitoring
            result = await self._execute_with_monitoring(
                workflow_id=workflow_id,
                team=selected_team,
                request=workflow_request
            )
            
            # Update performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_team_metrics(selected_team.name, execution_time, success=True)
            
            return WorkflowResult(
                workflow_id=workflow_id,
                team_used=selected_team.name,
                execution_time=execution_time,
                result=result,
                success=True
            )
            
        except Exception as e:
            # Handle workflow failures gracefully
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_team_metrics("unknown", execution_time, success=False)
            
            return WorkflowResult(
                workflow_id=workflow_id,
                execution_time=execution_time,
                error=str(e),
                success=False
            )
    
    async def _execute_with_monitoring(self, 
                                     workflow_id: str, 
                                     team: Team, 
                                     request: WorkflowRequest) -> Any:
        """Execute workflow with comprehensive monitoring"""
        
        # Create monitoring context
        monitor = WorkflowMonitor(workflow_id, team.name)
        
        try:
            # Execute with timeout protection
            result = await asyncio.wait_for(
                team.execute(request),
                timeout=request.max_execution_time.total_seconds()
            )
            
            monitor.log_success(result)
            return result
            
        except asyncio.TimeoutError:
            monitor.log_timeout()
            raise WorkflowTimeoutError(f"Workflow {workflow_id} timed out")
            
        except Exception as e:
            monitor.log_error(e)
            raise
        
        finally:
            # Always complete monitoring
            await monitor.finalize()
    
    def _update_team_metrics(self, team_name: str, execution_time: float, success: bool):
        """Update team performance metrics"""
        self.team_metrics["tasks_completed"] += 1
        
        # Update average completion time
        total_tasks = self.team_metrics["tasks_completed"]
        current_avg = self.team_metrics["average_completion_time"]
        self.team_metrics["average_completion_time"] = (
            (current_avg * (total_tasks - 1) + execution_time) / total_tasks
        )
        
        # Update success rate
        if success:
            current_rate = self.team_metrics["workflow_success_rate"]
            self.team_metrics["workflow_success_rate"] = (
                (current_rate * (total_tasks - 1) + 1.0) / total_tasks
            )
    
    def get_team_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive team performance report"""
        return {
            "overview": {
                "total_tasks": self.team_metrics["tasks_completed"],
                "average_completion_time": self.team_metrics["average_completion_time"],
                "success_rate": self.team_metrics["workflow_success_rate"]
            },
            "agent_utilization": self.team_metrics["agent_utilization"],
            "team_status": {
                name: {
                    "agents": len(team.agents),
                    "active": team.is_active(),
                    "current_load": team.get_current_load()
                }
                for name, team in self.teams.items()
            }
        }


# Dynamic Agent Scaling System
class DynamicAgentScaler:
    """Automatically scale agent resources based on demand"""
    
    def __init__(self, orchestrator: ProductionTeamOrchestrator):
        self.orchestrator = orchestrator
        self.scaling_rules = {
            "cpu_threshold": 80,       # Scale up when CPU > 80%
            "queue_length": 10,        # Scale up when queue > 10 items
            "response_time": 30,       # Scale up when avg response > 30s
            "min_agents": 1,           # Minimum agents per type
            "max_agents": 10           # Maximum agents per type
        }
        
    async def monitor_and_scale(self):
        """Continuously monitor and adjust agent scaling"""
        while True:
            try:
                # Check current system metrics
                metrics = await self._collect_system_metrics()
                
                # Determine if scaling is needed
                scaling_decision = self._evaluate_scaling_needs(metrics)
                
                if scaling_decision["action"] == "scale_up":
                    await self._scale_up_agents(scaling_decision["agent_types"])
                elif scaling_decision["action"] == "scale_down":
                    await self._scale_down_agents(scaling_decision["agent_types"])
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Scaling monitor error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        return {
            "queue_lengths": await self._get_queue_lengths(),
            "agent_utilization": await self._get_agent_utilization(),
            "response_times": await self._get_response_times(),
            "error_rates": await self._get_error_rates()
        }
    
    def _evaluate_scaling_needs(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if scaling up or down is needed"""
        
        # Check if scale up is needed
        if (metrics["queue_lengths"]["max"] > self.scaling_rules["queue_length"] or
            metrics["response_times"]["average"] > self.scaling_rules["response_time"]):
            
            # Identify which agent types need scaling
            bottleneck_agents = self._identify_bottlenecks(metrics)
            
            return {
                "action": "scale_up",
                "agent_types": bottleneck_agents,
                "reason": "High load detected"
            }
        
        # Check if scale down is possible
        elif (metrics["queue_lengths"]["max"] < 2 and
              metrics["agent_utilization"]["average"] < 30):
            
            underutilized_agents = self._identify_underutilized(metrics)
            
            return {
                "action": "scale_down", 
                "agent_types": underutilized_agents,
                "reason": "Low utilization detected"
            }
        
        return {"action": "no_change"}
    
    async def _scale_up_agents(self, agent_types: List[str]):
        """Add more agent instances of specified types"""
        for agent_type in agent_types:
            current_count = len(self.orchestrator.agents.get(agent_type, []))
            if current_count < self.scaling_rules["max_agents"]:
                new_agent = self._create_agent_instance(agent_type)
                self.orchestrator.agents[agent_type].append(new_agent)
                print(f"Scaled up {agent_type}: {current_count + 1} instances")
    
    async def _scale_down_agents(self, agent_types: List[str]):
        """Remove agent instances of specified types"""
        for agent_type in agent_types:
            current_agents = self.orchestrator.agents.get(agent_type, [])
            if len(current_agents) > self.scaling_rules["min_agents"]:
                # Remove least utilized agent
                agent_to_remove = min(current_agents, key=lambda a: a.get_utilization())
                current_agents.remove(agent_to_remove)
                print(f"Scaled down {agent_type}: {len(current_agents)} instances")


# Example usage and demonstration
if __name__ == "__main__":
    async def main():
        # Create team orchestrator
        orchestrator = ProductionTeamOrchestrator()
        
        # Create sample workflow request
        research_request = WorkflowRequest(
            task_description="Research AI trends in healthcare for Q4 2024",
            priority=TaskPriority.HIGH,
            max_execution_time=timedelta(minutes=5),
            requirements={
                "data_sources": ["web", "academic", "industry_reports"],
                "analysis_depth": "comprehensive",
                "output_format": "executive_summary"
            }
        )
        
        # Execute workflow
        print("=== Executing Research Workflow ===")
        result = await orchestrator.orchestrate_complex_workflow(research_request)
        
        if result.success:
            print(f"Workflow completed successfully in {result.execution_time:.2f}s")
            print(f"Team used: {result.team_used}")
        else:
            print(f"Workflow failed: {result.error}")
        
        # Generate performance report
        print("\n=== Team Performance Report ===")
        performance_report = orchestrator.get_team_performance_report()
        
        for section, data in performance_report.items():
            print(f"{section.upper()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
            print()
        
        # Demonstrate dynamic scaling
        print("=== Starting Dynamic Scaling Monitor ===")
        scaler = DynamicAgentScaler(orchestrator)
        # In production, this would run continuously
        # await scaler.monitor_and_scale()
        
    # Run demonstration
    asyncio.run(main())