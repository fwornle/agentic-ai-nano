# Session 4 - Module B: Enterprise Team Patterns (40 minutes)

**Prerequisites**: [Session 4 Core Section Complete](Session4_CrewAI_Team_Orchestration.md)  
**Target Audience**: Enterprise system architects  
**Cognitive Load**: 4 enterprise concepts

---

## 🎯 Module Overview

This module explores production-ready CrewAI team architectures including custom tool development, hierarchical delegation strategies, enterprise monitoring systems, and performance optimization patterns. You'll learn to build scalable agent teams that can handle enterprise workloads with sophisticated coordination and monitoring.

### Learning Objectives
By the end of this module, you will:
- Create custom tools that enable specialized agent capabilities
- Implement hierarchical delegation with autonomous peer inquiry
- Build enterprise monitoring and performance tracking systems
- Design production-ready team architectures with scaling strategies

---

## Part 1: Custom Tools and Agent Capabilities (20 minutes)

### Advanced Tool Architecture

🗂️ **File**: `src/session4/enterprise_tools.py` - Production tool implementations

Custom tools transform agents from conversational interfaces into powerful automation systems:

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, List, Any, Optional
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass

class ToolExecutionContext(BaseModel):
    """Context information for tool execution"""
    agent_id: str
    task_id: str
    execution_timestamp: datetime
    resource_limits: Dict[str, Any]
    security_context: Dict[str, str]

class SearchInput(BaseModel):
    """Comprehensive input schema for enterprise search tool"""
    query: str = Field(..., description="Search query with keywords")
    max_results: int = Field(default=10, description="Maximum results to return")
    source_types: List[str] = Field(default=["web", "knowledge_base"], description="Types of sources to search")
    quality_threshold: float = Field(default=0.7, description="Minimum quality score for results")
    time_range: Optional[str] = Field(default=None, description="Time range filter (e.g., 'last_week')")

class DataAnalysisInput(BaseModel):
    """Input schema for data analysis tool"""
    dataset_path: str = Field(..., description="Path to dataset")
    analysis_type: str = Field(..., description="Type of analysis (statistical, trend, correlation)")
    output_format: str = Field(default="json", description="Output format preference")
    visualization: bool = Field(default=False, description="Generate visualizations")

class EnterpriseSearchTool(BaseTool):
    """Production-grade search tool with multi-source aggregation"""
    
    name: str = "enterprise_search"
    description: str = "Advanced search across multiple enterprise data sources with quality filtering"
    args_schema: Type[BaseModel] = SearchInput
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.search_cache = {}
        self.source_adapters = {
            "web": self._search_web,
            "knowledge_base": self._search_knowledge_base,
            "documents": self._search_documents,
            "databases": self._search_databases
        }
        
    def _run(self, query: str, max_results: int = 10, 
             source_types: List[str] = None, quality_threshold: float = 0.7,
             time_range: Optional[str] = None) -> str:
        """Execute comprehensive enterprise search"""
        
        if source_types is None:
            source_types = ["web", "knowledge_base"]
        
        # Check cache first
        cache_key = self._generate_cache_key(query, source_types, time_range)
        if cache_key in self.search_cache:
            cached_result = self.search_cache[cache_key]
            if self._is_cache_valid(cached_result):
                self.logger.info(f"Returning cached results for query: {query}")
                return json.dumps(cached_result["results"], indent=2)
        
        # Execute search across all specified sources
        search_results = {}
        total_results = 0
        
        for source_type in source_types:
            if source_type in self.source_adapters:
                try:
                    source_results = self.source_adapters[source_type](
                        query, max_results, time_range
                    )
                    
                    # Filter by quality threshold
                    filtered_results = [
                        result for result in source_results
                        if result.get("quality_score", 0) >= quality_threshold
                    ]
                    
                    search_results[source_type] = filtered_results
                    total_results += len(filtered_results)
                    
                except Exception as e:
                    self.logger.error(f"Search failed for source {source_type}: {str(e)}")
                    search_results[source_type] = []
        
        # Aggregate and rank results
        aggregated_results = self._aggregate_search_results(search_results, max_results)
        
        # Cache results for future use
        cache_entry = {
            "results": aggregated_results,
            "timestamp": datetime.now(),
            "query": query,
            "source_types": source_types
        }
        self.search_cache[cache_key] = cache_entry
        
        # Prepare response with metadata
        response = {
            "query": query,
            "total_sources_searched": len(source_types),
            "total_results_found": total_results,
            "results_returned": len(aggregated_results["ranked_results"]),
            "search_timestamp": datetime.now().isoformat(),
            "results": aggregated_results
        }
        
        self.logger.info(f"Search completed: {total_results} results from {len(source_types)} sources")
        return json.dumps(response, indent=2)
    
    def _search_web(self, query: str, max_results: int, time_range: Optional[str]) -> List[Dict[str, Any]]:
        """Search web sources with enterprise-grade filtering"""
        
        # Simulate web search with quality scoring
        web_results = []
        
        # Generate realistic web search results
        for i in range(min(max_results, 8)):
            result = {
                "title": f"Web Result {i+1}: {query}",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"Comprehensive information about {query} with detailed analysis...",
                "source": "web",
                "quality_score": 0.6 + (i * 0.05),  # Varying quality scores
                "relevance_score": 0.8 - (i * 0.03),
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "metadata": {
                    "domain_authority": 85 - (i * 2),
                    "content_type": "article",
                    "word_count": 1200 + (i * 100)
                }
            }
            web_results.append(result)
        
        return web_results
    
    def _search_knowledge_base(self, query: str, max_results: int, time_range: Optional[str]) -> List[Dict[str, Any]]:
        """Search internal knowledge base with contextual relevance"""
        
        knowledge_results = []
        
        # Generate knowledge base results
        for i in range(min(max_results, 5)):
            result = {
                "title": f"Knowledge Base: {query} - Entry {i+1}",
                "content": f"Internal documentation about {query} with enterprise context...",
                "source": "knowledge_base",
                "quality_score": 0.85 + (i * 0.02),  # Generally higher quality
                "relevance_score": 0.9 - (i * 0.02),
                "timestamp": (datetime.now() - timedelta(hours=i*6)).isoformat(),
                "metadata": {
                    "document_type": "policy" if i % 2 == 0 else "procedure",
                    "department": "engineering" if i % 3 == 0 else "operations",
                    "version": f"1.{i+1}",
                    "approval_status": "approved"
                }
            }
            knowledge_results.append(result)
        
        return knowledge_results
    
    def _aggregate_search_results(self, search_results: Dict[str, List[Dict[str, Any]]],
                                max_results: int) -> Dict[str, Any]:
        """Aggregate and rank results from multiple sources"""
        
        all_results = []
        
        # Collect all results with source weighting
        source_weights = {
            "knowledge_base": 1.2,  # Higher weight for internal sources
            "web": 1.0,
            "documents": 1.1,
            "databases": 1.3
        }
        
        for source, results in search_results.items():
            weight = source_weights.get(source, 1.0)
            for result in results:
                # Calculate composite score
                composite_score = (
                    result.get("quality_score", 0) * 0.6 +
                    result.get("relevance_score", 0) * 0.4
                ) * weight
                
                result["composite_score"] = composite_score
                all_results.append(result)
        
        # Sort by composite score
        ranked_results = sorted(all_results, key=lambda x: x["composite_score"], reverse=True)
        
        # Limit results
        top_results = ranked_results[:max_results]
        
        # Generate aggregation metadata
        source_distribution = {}
        for result in top_results:
            source = result["source"]
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        return {
            "ranked_results": top_results,
            "aggregation_metadata": {
                "total_results_considered": len(all_results),
                "source_distribution": source_distribution,
                "ranking_algorithm": "composite_quality_relevance",
                "weighting_applied": True
            }
        }

class DataAnalysisTool(BaseTool):
    """Advanced data analysis tool for enterprise datasets"""
    
    name: str = "enterprise_data_analysis"
    description: str = "Perform statistical analysis and generate insights from enterprise datasets"
    args_schema: Type[BaseModel] = DataAnalysisInput
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.analysis_cache = {}
        
    def _run(self, dataset_path: str, analysis_type: str,
             output_format: str = "json", visualization: bool = False) -> str:
        """Execute comprehensive data analysis"""
        
        try:
            # Validate inputs
            if not self._validate_dataset_path(dataset_path):
                raise ValueError(f"Invalid dataset path: {dataset_path}")
            
            if analysis_type not in ["statistical", "trend", "correlation", "clustering"]:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")
            
            # Execute analysis based on type
            analysis_results = self._perform_analysis(dataset_path, analysis_type)
            
            # Generate visualizations if requested
            if visualization:
                visualization_data = self._generate_visualizations(analysis_results, analysis_type)
                analysis_results["visualizations"] = visualization_data
            
            # Format output
            if output_format == "json":
                return json.dumps(analysis_results, indent=2, default=str)
            elif output_format == "summary":
                return self._generate_analysis_summary(analysis_results)
            else:
                return json.dumps(analysis_results, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Data analysis failed: {str(e)}")
            return json.dumps({"error": str(e), "analysis_type": analysis_type}, indent=2)
    
    def _perform_analysis(self, dataset_path: str, analysis_type: str) -> Dict[str, Any]:
        """Perform the requested analysis on the dataset"""
        
        # Simulate dataset loading and analysis
        dataset_info = {
            "path": dataset_path,
            "size": 10000,  # Simulated dataset size
            "columns": ["timestamp", "value", "category", "status"],
            "loaded_at": datetime.now().isoformat()
        }
        
        if analysis_type == "statistical":
            return self._statistical_analysis(dataset_info)
        elif analysis_type == "trend":
            return self._trend_analysis(dataset_info)
        elif analysis_type == "correlation":
            return self._correlation_analysis(dataset_info)
        elif analysis_type == "clustering":
            return self._clustering_analysis(dataset_info)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    def _statistical_analysis(self, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis"""
        
        return {
            "analysis_type": "statistical",
            "dataset_info": dataset_info,
            "statistics": {
                "mean": 45.7,
                "median": 42.3,
                "std_deviation": 12.8,
                "min_value": 12.1,
                "max_value": 89.4,
                "quartiles": [32.5, 42.3, 58.9],
                "skewness": 0.23,
                "kurtosis": -0.45
            },
            "distribution": {
                "type": "normal",
                "parameters": {"mu": 45.7, "sigma": 12.8},
                "goodness_of_fit": 0.92
            },
            "insights": [
                "Data follows approximately normal distribution",
                "Low skewness indicates balanced distribution",
                "No significant outliers detected"
            ],
            "confidence_level": 0.95,
            "sample_size": dataset_info["size"],
            "analysis_timestamp": datetime.now().isoformat()
        }

class WorkflowOrchestrationTool(BaseTool):
    """Tool for orchestrating complex multi-agent workflows"""
    
    name: str = "workflow_orchestrator"
    description: str = "Coordinate and monitor complex multi-agent workflows"
    args_schema: Type[BaseModel] = BaseModel
    
    def __init__(self):
        super().__init__()
        self.active_workflows = {}
        self.workflow_history = {}
        self.logger = logging.getLogger(__name__)
        
    def _run(self, action: str, workflow_id: str = None, **kwargs) -> str:
        """Execute workflow orchestration commands"""
        
        if action == "create":
            return self._create_workflow(kwargs)
        elif action == "status":
            return self._get_workflow_status(workflow_id)
        elif action == "monitor":
            return self._monitor_all_workflows()
        elif action == "optimize":
            return self._optimize_workflow_performance()
        else:
            return json.dumps({"error": f"Unknown action: {action}"}, indent=2)
    
    def _create_workflow(self, config: Dict[str, Any]) -> str:
        """Create new workflow with advanced configuration"""
        
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow_config = {
            "id": workflow_id,
            "name": config.get("name", "Unnamed Workflow"),
            "description": config.get("description", ""),
            "agents": config.get("agents", []),
            "tasks": config.get("tasks", []),
            "dependencies": config.get("dependencies", {}),
            "resources": config.get("resources", {}),
            "monitoring": {
                "enabled": True,
                "metrics": ["performance", "quality", "resource_usage"],
                "alerts": ["task_failure", "resource_exhaustion", "deadline_risk"]
            },
            "created_at": datetime.now(),
            "status": "created",
            "execution_history": []
        }
        
        self.active_workflows[workflow_id] = workflow_config
        
        return json.dumps({
            "workflow_id": workflow_id,
            "status": "created",
            "configuration": workflow_config
        }, indent=2, default=str)
```

---

## Part 2: Hierarchical Delegation and Performance Optimization (20 minutes)

### Enterprise Delegation Patterns

🗂️ **File**: `src/session4/enterprise_delegation.py` - Production delegation systems

```python
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
import queue
import logging

class DelegationAuthority(Enum):
    """Levels of delegation authority in enterprise hierarchies"""
    EXECUTE_ONLY = 1          # Can only execute assigned tasks
    PEER_COLLABORATE = 2      # Can request help from peers
    TEAM_COORDINATE = 3       # Can coordinate team members
    DEPARTMENT_MANAGE = 4     # Can manage department resources
    ENTERPRISE_LEAD = 5       # Can make enterprise-level decisions

class TaskPriority(Enum):
    """Task priority levels for enterprise workload management"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class DelegationRule:
    """Comprehensive delegation rule specification"""
    from_authority: DelegationAuthority
    to_authority: DelegationAuthority
    task_types: List[str]
    conditions: Dict[str, Any]
    resource_limits: Dict[str, float]
    approval_required: bool = False
    escalation_path: Optional[List[str]] = None

@dataclass
class WorkloadMetrics:
    """Comprehensive workload tracking for agents"""
    agent_id: str
    current_tasks: int = 0
    total_capacity: int = 10
    complexity_score: float = 0.0
    performance_rating: float = 0.8
    last_updated: datetime = field(default_factory=datetime.now)
    specialization_bonus: Dict[str, float] = field(default_factory=dict)

class EnterpriseHierarchicalDelegation:
    """Production-grade hierarchical delegation with enterprise features"""
    
    def __init__(self):
        self.delegation_rules: List[DelegationRule] = []
        self.authority_matrix: Dict[str, DelegationAuthority] = {}
        self.workload_tracker: Dict[str, WorkloadMetrics] = {}
        self.delegation_history: List[Dict[str, Any]] = []
        self.peer_networks: Dict[str, List[str]] = {}
        self.performance_monitor = threading.Thread(target=self._monitor_performance, daemon=True)
        self.alert_queue = queue.Queue()
        self.logger = logging.getLogger(__name__)
        
        # Initialize enterprise delegation rules
        self._initialize_enterprise_rules()
        
        # Start performance monitoring
        self.performance_monitor.start()
    
    def _initialize_enterprise_rules(self):
        """Initialize comprehensive enterprise delegation rules"""
        
        # Executive level delegation rules
        self.delegation_rules.extend([
            DelegationRule(
                from_authority=DelegationAuthority.ENTERPRISE_LEAD,
                to_authority=DelegationAuthority.DEPARTMENT_MANAGE,
                task_types=["strategic_planning", "resource_allocation", "policy_creation"],
                conditions={"complexity": ">= 0.8", "impact": "enterprise"},
                resource_limits={"budget": 1000000, "personnel": 50},
                approval_required=False,
                escalation_path=["board_approval"]
            ),
            DelegationRule(
                from_authority=DelegationAuthority.DEPARTMENT_MANAGE,
                to_authority=DelegationAuthority.TEAM_COORDINATE,
                task_types=["project_management", "team_coordination", "quality_assurance"],
                conditions={"department_scope": True, "deadline": "<= 30_days"},
                resource_limits={"budget": 100000, "personnel": 10},
                approval_required=True,
                escalation_path=["department_head", "enterprise_lead"]
            ),
            DelegationRule(
                from_authority=DelegationAuthority.TEAM_COORDINATE,
                to_authority=DelegationAuthority.PEER_COLLABORATE,
                task_types=["implementation", "research", "analysis", "testing"],
                conditions={"team_scope": True, "skill_match": ">= 0.7"},
                resource_limits={"budget": 10000, "time": "7_days"},
                approval_required=False,
                escalation_path=["team_lead", "department_manager"]
            )
        ])
        
        # Peer collaboration rules
        self.delegation_rules.append(
            DelegationRule(
                from_authority=DelegationAuthority.PEER_COLLABORATE,
                to_authority=DelegationAuthority.PEER_COLLABORATE,
                task_types=["consultation", "code_review", "knowledge_sharing"],
                conditions={"peer_level": True, "workload": "<= 0.8"},
                resource_limits={"time": "2_hours"},
                approval_required=False,
                escalation_path=["team_coordinator"]
            )
        )
    
    def register_agent_authority(self, agent_id: str, authority: DelegationAuthority,
                               specializations: Dict[str, float] = None):
        """Register agent with delegation authority and specializations"""
        
        self.authority_matrix[agent_id] = authority
        
        # Initialize workload tracking
        self.workload_tracker[agent_id] = WorkloadMetrics(
            agent_id=agent_id,
            specialization_bonus=specializations or {}
        )
        
        self.logger.info(f"Agent {agent_id} registered with authority: {authority.name}")
    
    def can_delegate_task(self, from_agent: str, to_agent: str, 
                         task_type: str, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive delegation validation with enterprise rules"""
        
        # Get agent authorities
        from_authority = self.authority_matrix.get(from_agent)
        to_authority = self.authority_matrix.get(to_agent)
        
        if not from_authority or not to_authority:
            return {
                "can_delegate": False,
                "reason": "Agent authority not found",
                "requires_escalation": True
            }
        
        # Check delegation rules
        applicable_rules = self._find_applicable_rules(
            from_authority, to_authority, task_type, task_context
        )
        
        if not applicable_rules:
            return {
                "can_delegate": False,
                "reason": "No applicable delegation rules",
                "requires_escalation": True,
                "escalation_path": ["team_coordinator", "department_manager"]
            }
        
        # Validate workload capacity
        workload_check = self._validate_workload_capacity(to_agent, task_context)
        
        if not workload_check["has_capacity"]:
            return {
                "can_delegate": False,
                "reason": f"Target agent overloaded: {workload_check['reason']}",
                "alternative_agents": workload_check.get("alternatives", []),
                "requires_escalation": False
            }
        
        # Check resource limits
        resource_check = self._validate_resource_limits(applicable_rules[0], task_context)
        
        if not resource_check["within_limits"]:
            return {
                "can_delegate": False,
                "reason": f"Resource limits exceeded: {resource_check['violations']}",
                "requires_escalation": True,
                "escalation_path": applicable_rules[0].escalation_path
            }
        
        # All checks passed
        return {
            "can_delegate": True,
            "rule_applied": applicable_rules[0].__dict__,
            "workload_impact": workload_check,
            "approval_required": applicable_rules[0].approval_required,
            "monitoring_required": True
        }
    
    def execute_delegation(self, from_agent: str, to_agent: str,
                          task_description: str, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute delegation with comprehensive tracking and monitoring"""
        
        # Validate delegation
        validation_result = self.can_delegate_task(from_agent, to_agent, 
                                                 task_context.get("type", "general"), 
                                                 task_context)
        
        if not validation_result["can_delegate"]:
            return {
                "success": False,
                "delegation_id": None,
                "validation_result": validation_result
            }
        
        # Create delegation record
        delegation_id = f"del_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{from_agent}_{to_agent}"
        
        delegation_record = {
            "delegation_id": delegation_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task_description": task_description,
            "task_context": task_context,
            "validation_result": validation_result,
            "status": "active",
            "created_at": datetime.now(),
            "estimated_completion": datetime.now() + timedelta(
                hours=task_context.get("estimated_hours", 4)
            ),
            "priority": TaskPriority(task_context.get("priority", 2)),
            "monitoring": {
                "enabled": True,
                "check_interval": 3600,  # 1 hour
                "alerts_enabled": True
            }
        }
        
        # Update workload tracking
        self._update_workload(to_agent, task_context)
        
        # Log delegation
        self.delegation_history.append(delegation_record)
        
        # Set up monitoring if required
        if validation_result.get("monitoring_required", False):
            self._setup_delegation_monitoring(delegation_record)
        
        self.logger.info(f"Delegation executed: {delegation_id}")
        
        return {
            "success": True,
            "delegation_id": delegation_id,
            "delegation_record": delegation_record,
            "monitoring_setup": validation_result.get("monitoring_required", False)
        }
    
    def optimize_workload_distribution(self, available_agents: List[str],
                                     pending_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """AI-powered workload optimization across agent teams"""
        
        # Analyze current workload distribution
        workload_analysis = self._analyze_current_workloads(available_agents)
        
        # Generate optimal task assignments
        optimization_result = self._generate_optimal_assignments(
            pending_tasks, 
            workload_analysis
        )
        
        # Calculate performance improvements
        performance_impact = self._calculate_optimization_impact(
            optimization_result,
            workload_analysis
        )
        
        return {
            "optimization_id": f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "current_workload_analysis": workload_analysis,
            "recommended_assignments": optimization_result["assignments"],
            "performance_improvements": {
                "efficiency_gain": performance_impact["efficiency_gain"],
                "load_balance_improvement": performance_impact["balance_improvement"],
                "estimated_completion_speedup": performance_impact["speedup"],
                "resource_utilization_improvement": performance_impact["resource_optimization"]
            },
            "implementation_steps": optimization_result["implementation_steps"],
            "risk_assessment": optimization_result["risks"],
            "monitoring_recommendations": optimization_result["monitoring"]
        }
    
    def _find_applicable_rules(self, from_authority: DelegationAuthority,
                              to_authority: DelegationAuthority,
                              task_type: str, task_context: Dict[str, Any]) -> List[DelegationRule]:
        """Find delegation rules applicable to the given context"""
        
        applicable_rules = []
        
        for rule in self.delegation_rules:
            # Check authority levels
            if (rule.from_authority == from_authority and 
                rule.to_authority == to_authority):
                
                # Check task type
                if task_type in rule.task_types or "any" in rule.task_types:
                    
                    # Check conditions
                    if self._evaluate_rule_conditions(rule.conditions, task_context):
                        applicable_rules.append(rule)
        
        return applicable_rules
    
    def _evaluate_rule_conditions(self, conditions: Dict[str, Any],
                                 task_context: Dict[str, Any]) -> bool:
        """Evaluate whether task context meets rule conditions"""
        
        for condition, requirement in conditions.items():
            if condition not in task_context:
                continue
                
            context_value = task_context[condition]
            
            if isinstance(requirement, str):
                # Handle comparison operators
                if requirement.startswith(">="):
                    if not (context_value >= float(requirement[2:].strip())):
                        return False
                elif requirement.startswith("<="):
                    if not (context_value <= float(requirement[2:].strip())):
                        return False
                elif requirement.startswith(">"):
                    if not (context_value > float(requirement[1:].strip())):
                        return False
                elif requirement.startswith("<"):
                    if not (context_value < float(requirement[1:].strip())):
                        return False
                else:
                    if context_value != requirement:
                        return False
            else:
                if context_value != requirement:
                    return False
        
        return True
    
    def _monitor_performance(self):
        """Background performance monitoring for delegated tasks"""
        
        while True:
            try:
                # Check active delegations
                active_delegations = [
                    record for record in self.delegation_history
                    if record["status"] == "active"
                ]
                
                for delegation in active_delegations:
                    # Check for deadline risks
                    if self._is_deadline_at_risk(delegation):
                        self.alert_queue.put({
                            "type": "deadline_risk",
                            "delegation_id": delegation["delegation_id"],
                            "message": "Task may miss deadline",
                            "severity": "warning"
                        })
                    
                    # Check for workload issues
                    workload_issues = self._check_workload_health(delegation["to_agent"])
                    if workload_issues:
                        self.alert_queue.put({
                            "type": "workload_issue",
                            "agent_id": delegation["to_agent"],
                            "issues": workload_issues,
                            "severity": "warning"
                        })
                
                # Sleep for monitoring interval
                threading.Event().wait(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {str(e)}")
                threading.Event().wait(60)  # Retry after 1 minute
```

---

## 🎯 Module Summary

You've now mastered enterprise CrewAI team patterns and production architectures:

✅ **Custom Tool Development**: Created sophisticated tools that enable specialized agent capabilities  
✅ **Hierarchical Delegation**: Implemented enterprise delegation patterns with authority matrices and peer inquiry  
✅ **Performance Optimization**: Built workload balancing and optimization systems for team efficiency  
✅ **Enterprise Monitoring**: Designed comprehensive monitoring and alerting systems for production teams

### Next Steps
- **Return to Core**: [Session 4 Main](Session4_CrewAI_Team_Orchestration.md)
- **Advance to Session 6**: [Agent Communication Protocols](Session6_Agent_Communication_Protocols.md)
- **Compare with Module A**: [Advanced CrewAI Flows](Session4_ModuleA_Advanced_CrewAI_Flows.md)

---

**🗂️ Source Files for Module B:**
- `src/session4/enterprise_tools.py` - Production tool implementations
- `src/session4/enterprise_delegation.py` - Hierarchical delegation systems
- `src/session4/performance_optimization.py` - Team performance monitoring