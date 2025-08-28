# Session 3 - Module B: Advanced Workflow Orchestration

> **⚠️ ADVANCED OPTIONAL MODULE**  
> Prerequisites: Complete Session 3 core content first.

Advanced workflow orchestration patterns enable parallel processing, conditional routing, state management, and error recovery for complex enterprise agent systems.

## Advanced Orchestration Patterns

### Pattern 1: Parallel Processing with Result Aggregation

When multiple independent operations can run simultaneously, parallel processing dramatically improves performance.

```python
# workflows/parallel_processor.py
import asyncio
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParallelWorkflowState:
    """State for parallel processing workflow."""
    query: str
    messages: List[Any]
    
    # Parallel processing results
    weather_result: Optional[Dict] = None
    file_result: Optional[Dict] = None
    database_result: Optional[Dict] = None
    
    # Processing status tracking
    completed_tasks: Set[str] = field(default_factory=set)
    failed_tasks: Set[str] = field(default_factory=set)
    start_time: Optional[float] = None
    
    # Final aggregated result
    aggregated_result: Optional[Dict] = None
    processing_time: Optional[float] = None

class ParallelWorkflowOrchestrator:
    """Advanced parallel workflow with intelligent task coordination."""
    
    def __init__(self, mcp_manager):
        self.mcp_manager = mcp_manager
        self.workflow = None
        
    async def build_workflow(self) -> StateGraph:
        """Build parallel processing workflow graph."""
        workflow = StateGraph(ParallelWorkflowState)
        
        # Add processing nodes
        workflow.add_node("initializer", self._initialize_processing)
        workflow.add_node("weather_processor", self._process_weather)
        workflow.add_node("file_processor", self._process_files)
        workflow.add_node("database_processor", self._process_database)
        workflow.add_node("aggregator", self._aggregate_results)
        workflow.add_node("error_handler", self._handle_errors)
        
        # Define parallel execution flow
        workflow.set_entry_point("initializer")
        
        # Fan out to parallel processors
        workflow.add_edge("initializer", "weather_processor")
        workflow.add_edge("initializer", "file_processor")  
        workflow.add_edge("initializer", "database_processor")
        
        # Conditional aggregation based on completion
        workflow.add_conditional_edges(
            "weather_processor",
            self._check_completion_status,
            {
                "aggregate": "aggregator",
                "wait": END,  # Continue processing
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "file_processor",
            self._check_completion_status,
            {
                "aggregate": "aggregator",
                "wait": END,
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "database_processor",
            self._check_completion_status,
            {
                "aggregate": "aggregator", 
                "wait": END,
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("aggregator", END)
        workflow.add_edge("error_handler", END)
        
        self.workflow = workflow.compile()
        return self.workflow
    
    async def _initialize_processing(self, state: ParallelWorkflowState) -> ParallelWorkflowState:
        """Initialize parallel processing state."""
        state.start_time = time.time()
        state.completed_tasks = set()
        state.failed_tasks = set()
        logger.info(f"Starting parallel processing for query: {state.query}")
        return state
    
    async def _process_weather(self, state: ParallelWorkflowState) -> ParallelWorkflowState:
        """Process weather data in parallel."""
        try:
            if "weather" in state.query.lower():
                adapter = await self.mcp_manager.get_adapter("weather")
                if adapter:
                    cities = self._extract_cities(state.query)
                    weather_data = {}
                    
                    # Process multiple cities in parallel
                    tasks = [
                        self._get_weather_for_city(adapter, city) 
                        for city in cities
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for city, result in zip(cities, results):
                        if not isinstance(result, Exception):
                            weather_data[city] = result
                    
                    state.weather_result = weather_data
                else:
                    state.weather_result = {"error": "Weather service unavailable"}
            else:
                state.weather_result = {"skipped": "No weather query detected"}
            
            state.completed_tasks.add("weather")
            logger.info("Weather processing completed")
            
        except Exception as e:
            state.failed_tasks.add("weather")
            state.weather_result = {"error": str(e)}
            logger.error(f"Weather processing failed: {e}")
        
        return state
    
    async def _get_weather_for_city(self, adapter, city: str) -> Dict:
        """Get weather for a single city with timeout."""
        try:
            return await asyncio.wait_for(
                adapter.call_tool("get_current_weather", {"city": city}),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            return {"error": f"Timeout getting weather for {city}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _process_files(self, state: ParallelWorkflowState) -> ParallelWorkflowState:
        """Process file operations in parallel."""
        try:
            adapter = await self.mcp_manager.get_adapter("filesystem")
            if adapter:
                search_terms = self._extract_search_terms(state.query)
                
                # Search for multiple terms in parallel
                search_tasks = [
                    self._search_files_for_term(adapter, term)
                    for term in search_terms
                ]
                
                results = await asyncio.gather(*search_tasks, return_exceptions=True)
                
                file_data = {}
                for term, result in zip(search_terms, results):
                    if not isinstance(result, Exception):
                        file_data[f"files_for_{term}"] = result
                
                state.file_result = file_data
            else:
                state.file_result = {"error": "File service unavailable"}
            
            state.completed_tasks.add("files")
            logger.info("File processing completed")
            
        except Exception as e:
            state.failed_tasks.add("files")
            state.file_result = {"error": str(e)}
            logger.error(f"File processing failed: {e}")
        
        return state
    
    async def _search_files_for_term(self, adapter, term: str) -> Dict:
        """Search files for a specific term with timeout."""
        try:
            return await asyncio.wait_for(
                adapter.call_tool("search_files", {
                    "pattern": f"*{term}*",
                    "search_type": "name"
                }),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            return {"error": f"Timeout searching files for {term}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _process_database(self, state: ParallelWorkflowState) -> ParallelWorkflowState:
        """Process database operations in parallel."""
        try:
            adapter = await self.mcp_manager.get_adapter("database")
            if adapter:
                # Simulate parallel database queries
                query_tasks = [
                    self._execute_database_query(adapter, "user_data", state.query),
                    self._execute_database_query(adapter, "historical_data", state.query),
                    self._execute_database_query(adapter, "metadata", state.query)
                ]
                
                results = await asyncio.gather(*query_tasks, return_exceptions=True)
                
                database_data = {}
                query_types = ["user_data", "historical_data", "metadata"]
                for query_type, result in zip(query_types, results):
                    if not isinstance(result, Exception):
                        database_data[query_type] = result
                
                state.database_result = database_data
            else:
                state.database_result = {"error": "Database service unavailable"}
            
            state.completed_tasks.add("database")
            logger.info("Database processing completed")
            
        except Exception as e:
            state.failed_tasks.add("database")
            state.database_result = {"error": str(e)}
            logger.error(f"Database processing failed: {e}")
        
        return state
    
    async def _execute_database_query(self, adapter, query_type: str, query: str) -> Dict:
        """Execute a database query with timeout."""
        try:
            return await asyncio.wait_for(
                adapter.call_tool("query", {
                    "table": query_type,
                    "query": query
                }),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            return {"error": f"Timeout executing {query_type} query"}
        except Exception as e:
            return {"error": str(e)}
    
    def _check_completion_status(self, state: ParallelWorkflowState) -> str:
        """Check if all parallel tasks are complete."""
        expected_tasks = {"weather", "files", "database"}
        all_tasks = state.completed_tasks | state.failed_tasks
        
        if all_tasks >= expected_tasks:
            if state.failed_tasks:
                return "error"
            else:
                return "aggregate"
        
        return "wait"
    
    async def _aggregate_results(self, state: ParallelWorkflowState) -> ParallelWorkflowState:
        """Aggregate results from all parallel processors."""
        processing_time = time.time() - state.start_time if state.start_time else 0
        state.processing_time = processing_time
        
        # Aggregate all results
        aggregated = {
            "query": state.query,
            "processing_time_seconds": processing_time,
            "completed_tasks": list(state.completed_tasks),
            "failed_tasks": list(state.failed_tasks),
            "results": {}
        }
        
        if state.weather_result:
            aggregated["results"]["weather"] = state.weather_result
        
        if state.file_result:
            aggregated["results"]["files"] = state.file_result
        
        if state.database_result:
            aggregated["results"]["database"] = state.database_result
        
        # Generate summary
        summary_parts = []
        if state.weather_result and "error" not in state.weather_result:
            summary_parts.append("Weather data retrieved successfully")
        
        if state.file_result and "error" not in state.file_result:
            summary_parts.append("File search completed")
        
        if state.database_result and "error" not in state.database_result:
            summary_parts.append("Database queries executed")
        
        aggregated["summary"] = "; ".join(summary_parts) if summary_parts else "Partial results available"
        
        state.aggregated_result = aggregated
        
        logger.info(f"Parallel processing completed in {processing_time:.2f} seconds")
        logger.info(f"Completed: {state.completed_tasks}, Failed: {state.failed_tasks}")
        
        return state
    
    async def _handle_errors(self, state: ParallelWorkflowState) -> ParallelWorkflowState:
        """Handle errors in parallel processing."""
        processing_time = time.time() - state.start_time if state.start_time else 0
        
        error_summary = {
            "query": state.query,
            "processing_time_seconds": processing_time,
            "completed_tasks": list(state.completed_tasks),
            "failed_tasks": list(state.failed_tasks),
            "partial_results": {},
            "errors": {}
        }
        
        # Collect partial results and errors
        if state.weather_result:
            if "error" in state.weather_result:
                error_summary["errors"]["weather"] = state.weather_result["error"]
            else:
                error_summary["partial_results"]["weather"] = state.weather_result
        
        if state.file_result:
            if "error" in state.file_result:
                error_summary["errors"]["files"] = state.file_result["error"]
            else:
                error_summary["partial_results"]["files"] = state.file_result
        
        if state.database_result:
            if "error" in state.database_result:
                error_summary["errors"]["database"] = state.database_result["error"]
            else:
                error_summary["partial_results"]["database"] = state.database_result
        
        state.aggregated_result = error_summary
        
        logger.warning(f"Parallel processing completed with errors after {processing_time:.2f} seconds")
        
        return state
    
    def _extract_cities(self, query: str) -> List[str]:
        """Extract city names from query."""
        cities = ["London", "New York", "Tokyo", "Sydney", "Paris"]
        found = [city for city in cities if city.lower() in query.lower()]
        return found or ["London"]
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query."""
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        words = [word for word in query.lower().split() if len(word) > 3 and word not in stop_words]
        return words[:3]
    
    async def run_parallel_workflow(self, query: str) -> Dict[str, Any]:
        """Execute parallel workflow."""
        if not self.workflow:
            await self.build_workflow()
        
        initial_state = ParallelWorkflowState(
            query=query,
            messages=[HumanMessage(content=query)]
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            return {
                "success": True,
                "result": final_state.aggregated_result,
                "processing_time": final_state.processing_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
```

### Pattern 2: Conditional Workflow Routing

Dynamic workflows adapt their execution path based on runtime conditions and intermediate results.

```python
# workflows/conditional_router.py
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    CUSTOMER_SERVICE = "customer_service"
    TECHNICAL_SUPPORT = "technical_support"
    SALES_INQUIRY = "sales_inquiry"
    DATA_ANALYSIS = "data_analysis"
    GENERAL_QUERY = "general_query"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ConditionalWorkflowState:
    """State for conditional workflow routing."""
    query: str
    messages: List[Any]
    
    # Classification results
    workflow_type: Optional[WorkflowType] = None
    priority: Optional[Priority] = None
    customer_tier: Optional[str] = None
    urgency_keywords: List[str] = None
    
    # Processing results
    primary_result: Optional[Dict] = None
    escalation_result: Optional[Dict] = None
    
    # Routing decisions
    routing_path: List[str] = None
    escalated: bool = False

class ConditionalWorkflowRouter:
    """Intelligent workflow routing based on content analysis."""
    
    def __init__(self, mcp_manager):
        self.mcp_manager = mcp_manager
        self.workflow = None
        
        # Define routing rules
        self.workflow_patterns = {
            WorkflowType.CUSTOMER_SERVICE: [
                r"account|billing|payment|refund|cancel|subscription",
                r"order|shipping|delivery|tracking|return",
                r"login|password|access|locked"
            ],
            WorkflowType.TECHNICAL_SUPPORT: [
                r"error|bug|crash|broken|not working|issue",
                r"api|integration|connection|timeout",
                r"performance|slow|loading|response"
            ],
            WorkflowType.SALES_INQUIRY: [
                r"price|cost|quote|demo|trial|purchase",
                r"features|comparison|upgrade|plan",
                r"contact sales|sales team|pricing"
            ],
            WorkflowType.DATA_ANALYSIS: [
                r"report|analytics|data|statistics|metrics",
                r"trend|analysis|forecast|prediction",
                r"dashboard|visualization|chart"
            ]
        }
        
        self.urgency_patterns = [
            (r"urgent|emergency|critical|asap|immediately", Priority.CRITICAL),
            (r"important|priority|soon|quickly", Priority.HIGH),
            (r"please|when possible|sometime", Priority.MEDIUM)
        ]
        
        self.escalation_triggers = [
            r"complaint|frustrated|angry|disappointed",
            r"manager|supervisor|escalate",
            r"unacceptable|terrible|worst"
        ]
    
    async def build_workflow(self) -> StateGraph:
        """Build conditional routing workflow."""
        workflow = StateGraph(ConditionalWorkflowState)
        
        # Add processing nodes
        workflow.add_node("classifier", self._classify_query)
        workflow.add_node("customer_service_handler", self._handle_customer_service)
        workflow.add_node("technical_support_handler", self._handle_technical_support)
        workflow.add_node("sales_handler", self._handle_sales_inquiry)
        workflow.add_node("data_analysis_handler", self._handle_data_analysis)
        workflow.add_node("general_handler", self._handle_general_query)
        workflow.add_node("escalation_handler", self._handle_escalation)
        workflow.add_node("priority_processor", self._process_priority)
        
        # Set entry point
        workflow.set_entry_point("classifier")
        
        # Conditional routing based on classification
        workflow.add_conditional_edges(
            "classifier",
            self._route_workflow,
            {
                "customer_service": "customer_service_handler",
                "technical_support": "technical_support_handler", 
                "sales_inquiry": "sales_handler",
                "data_analysis": "data_analysis_handler",
                "general_query": "general_handler",
                "escalation": "escalation_handler"
            }
        )
        
        # Priority processing after main handling
        workflow.add_edge("customer_service_handler", "priority_processor")
        workflow.add_edge("technical_support_handler", "priority_processor")
        workflow.add_edge("sales_handler", "priority_processor")
        workflow.add_edge("data_analysis_handler", "priority_processor")
        workflow.add_edge("general_handler", "priority_processor")
        
        # Escalation handling
        workflow.add_conditional_edges(
            "priority_processor",
            self._check_escalation_needed,
            {
                "escalate": "escalation_handler",
                "complete": END
            }
        )
        
        workflow.add_edge("escalation_handler", END)
        
        self.workflow = workflow.compile()
        return self.workflow
    
    async def _classify_query(self, state: ConditionalWorkflowState) -> ConditionalWorkflowState:
        """Classify query type and extract metadata."""
        query_lower = state.query.lower()
        
        # Classify workflow type
        workflow_scores = {}
        for workflow_type, patterns in self.workflow_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            workflow_scores[workflow_type] = score
        
        # Select highest scoring workflow type
        if max(workflow_scores.values()) > 0:
            state.workflow_type = max(workflow_scores, key=workflow_scores.get)
        else:
            state.workflow_type = WorkflowType.GENERAL_QUERY
        
        # Determine priority
        state.priority = Priority.LOW  # Default
        for pattern, priority in self.urgency_patterns:
            if re.search(pattern, query_lower):
                if priority.value > state.priority.value:
                    state.priority = priority
        
        # Extract urgency keywords
        state.urgency_keywords = []
        for pattern, _ in self.urgency_patterns:
            state.urgency_keywords.extend(re.findall(pattern, query_lower))
        
        # Check for escalation triggers
        for pattern in self.escalation_triggers:
            if re.search(pattern, query_lower):
                state.escalated = True
                break
        
        # Routing path tracking
        state.routing_path = ["classifier"]
        
        logger.info(f"Classified query as {state.workflow_type.value} with priority {state.priority.value}")
        
        return state
    
    def _route_workflow(self, state: ConditionalWorkflowState) -> str:
        """Route workflow based on classification."""
        if state.escalated:
            return "escalation"
        
        return state.workflow_type.value
    
    async def _handle_customer_service(self, state: ConditionalWorkflowState) -> ConditionalWorkflowState:
        """Handle customer service workflow."""
        state.routing_path.append("customer_service")
        
        try:
            # Simulate customer service processing
            adapter = await self.mcp_manager.get_adapter("database")
            if adapter:
                # Look up customer information
                customer_data = await adapter.call_tool("query", {
                    "table": "customers",
                    "query": state.query
                })
                
                # Check account status
                if customer_data:
                    state.customer_tier = self._determine_customer_tier(customer_data)
            
            state.primary_result = {
                "type": "customer_service",
                "action": "Account inquiry processed",
                "customer_tier": state.customer_tier,
                "recommendations": self._get_customer_service_recommendations(state)
            }
            
        except Exception as e:
            state.primary_result = {
                "type": "customer_service",
                "error": str(e),
                "fallback": "Standard customer service response"
            }
        
        return state
    
    async def _handle_technical_support(self, state: ConditionalWorkflowState) -> ConditionalWorkflowState:
        """Handle technical support workflow."""
        state.routing_path.append("technical_support")
        
        try:
            # Check system status and logs
            adapter = await self.mcp_manager.get_adapter("filesystem")
            if adapter:
                log_data = await adapter.call_tool("search_files", {
                    "pattern": "*.log",
                    "search_type": "name"
                })
            
            state.primary_result = {
                "type": "technical_support",
                "action": "Technical analysis completed",
                "severity": self._assess_technical_severity(state),
                "next_steps": self._get_technical_recommendations(state)
            }
            
        except Exception as e:
            state.primary_result = {
                "type": "technical_support",
                "error": str(e),
                "fallback": "Standard technical support response"
            }
        
        return state
    
    async def _handle_sales_inquiry(self, state: ConditionalWorkflowState) -> ConditionalWorkflowState:
        """Handle sales inquiry workflow."""
        state.routing_path.append("sales")
        
        try:
            # Get pricing and product information
            adapter = await self.mcp_manager.get_adapter("database")
            if adapter:
                product_data = await adapter.call_tool("query", {
                    "table": "products",
                    "query": state.query
                })
            
            state.primary_result = {
                "type": "sales_inquiry",
                "action": "Sales information provided",
                "lead_quality": self._assess_lead_quality(state),
                "recommendations": self._get_sales_recommendations(state)
            }
            
        except Exception as e:
            state.primary_result = {
                "type": "sales_inquiry", 
                "error": str(e),
                "fallback": "Standard sales response"
            }
        
        return state
    
    async def _handle_data_analysis(self, state: ConditionalWorkflowState) -> ConditionalWorkflowState:
        """Handle data analysis workflow."""
        state.routing_path.append("data_analysis")
        
        try:
            # Perform data analysis
            adapter = await self.mcp_manager.get_adapter("database")
            if adapter:
                analytics_data = await adapter.call_tool("query", {
                    "table": "analytics",
                    "query": state.query
                })
            
            state.primary_result = {
                "type": "data_analysis",
                "action": "Data analysis completed",
                "insights": self._generate_insights(state),
                "visualizations": "Charts and graphs generated"
            }
            
        except Exception as e:
            state.primary_result = {
                "type": "data_analysis",
                "error": str(e),
                "fallback": "Standard analytics response"
            }
        
        return state
    
    async def _handle_general_query(self, state: ConditionalWorkflowState) -> ConditionalWorkflowState:
        """Handle general query workflow."""
        state.routing_path.append("general")
        
        state.primary_result = {
            "type": "general_query",
            "action": "General information provided",
            "response": "Comprehensive general response based on available data"
        }
        
        return state
    
    async def _process_priority(self, state: ConditionalWorkflowState) -> ConditionalWorkflowState:
        """Process based on priority level."""
        state.routing_path.append("priority_processor")
        
        if state.priority in [Priority.HIGH, Priority.CRITICAL]:
            # Add priority flags to result
            if state.primary_result:
                state.primary_result["priority_processing"] = {
                    "level": state.priority.name,
                    "expedited": True,
                    "sla": "4 hours" if state.priority == Priority.HIGH else "1 hour"
                }
        
        return state
    
    def _check_escalation_needed(self, state: ConditionalWorkflowState) -> str:
        """Check if escalation is needed."""
        if (state.escalated or 
            state.priority == Priority.CRITICAL or 
            (state.customer_tier == "premium" and state.priority == Priority.HIGH)):
            return "escalate"
        
        return "complete"
    
    async def _handle_escalation(self, state: ConditionalWorkflowState) -> ConditionalWorkflowState:
        """Handle escalation workflow."""
        state.routing_path.append("escalation")
        
        state.escalation_result = {
            "escalated": True,
            "reason": "Priority level or customer tier requires escalation",
            "assigned_to": "Senior support team",
            "escalation_time": time.time(),
            "original_result": state.primary_result
        }
        
        logger.warning(f"Query escalated: {state.query[:50]}...")
        
        return state
    
    # Helper methods for assessment and recommendations
    def _determine_customer_tier(self, customer_data: Dict) -> str:
        """Determine customer tier from data."""
        # Simplified tier determination
        return customer_data.get("tier", "standard")
    
    def _assess_technical_severity(self, state: ConditionalWorkflowState) -> str:
        """Assess technical issue severity."""
        if state.priority == Priority.CRITICAL:
            return "critical"
        elif "error" in state.query.lower() or "crash" in state.query.lower():
            return "high"
        else:
            return "medium"
    
    def _assess_lead_quality(self, state: ConditionalWorkflowState) -> str:
        """Assess sales lead quality."""
        if any(word in state.query.lower() for word in ["demo", "trial", "purchase", "buy"]):
            return "hot"
        elif any(word in state.query.lower() for word in ["price", "cost", "quote"]):
            return "warm"
        else:
            return "cold"
    
    def _get_customer_service_recommendations(self, state: ConditionalWorkflowState) -> List[str]:
        """Get customer service recommendations."""
        return [
            "Verify account information",
            "Check recent transaction history",
            "Provide relevant documentation"
        ]
    
    def _get_technical_recommendations(self, state: ConditionalWorkflowState) -> List[str]:
        """Get technical support recommendations."""
        return [
            "Check system logs",
            "Verify configuration settings",
            "Test connectivity"
        ]
    
    def _get_sales_recommendations(self, state: ConditionalWorkflowState) -> List[str]:
        """Get sales recommendations."""
        return [
            "Provide product comparison",
            "Schedule demo if interested",
            "Send pricing information"
        ]
    
    def _generate_insights(self, state: ConditionalWorkflowState) -> List[str]:
        """Generate data insights."""
        return [
            "Trend analysis completed",
            "Key metrics identified",
            "Recommendations generated"
        ]
    
    async def run_conditional_workflow(self, query: str) -> Dict[str, Any]:
        """Execute conditional workflow."""
        if not self.workflow:
            await self.build_workflow()
        
        initial_state = ConditionalWorkflowState(
            query=query,
            messages=[HumanMessage(content=query)]
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            result = {
                "success": True,
                "workflow_type": final_state.workflow_type.value,
                "priority": final_state.priority.name,
                "routing_path": final_state.routing_path,
                "primary_result": final_state.primary_result
            }
            
            if final_state.escalation_result:
                result["escalation"] = final_state.escalation_result
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
```

### Pattern 3: State Recovery and Compensation

Advanced workflows implement compensation patterns to handle failures and maintain data consistency.

```python
# workflows/compensation_handler.py
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import logging

logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"

@dataclass
class CompensationAction:
    """Represents a compensation action for failed operations."""
    step_name: str
    compensation_function: str
    compensation_args: Dict[str, Any]
    executed: bool = False
    execution_time: Optional[float] = None

@dataclass
class CompensationWorkflowState:
    """State for workflow with compensation handling."""
    query: str
    messages: List[Any]
    
    # Transaction tracking
    transaction_id: str
    executed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    compensation_actions: List[CompensationAction] = field(default_factory=list)
    
    # Results tracking
    step_results: Dict[str, Any] = field(default_factory=dict)
    final_status: TransactionStatus = TransactionStatus.PENDING
    
    # Recovery information
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3

class CompensationWorkflowHandler:
    """Workflow handler with advanced compensation and recovery patterns."""
    
    def __init__(self, mcp_manager):
        self.mcp_manager = mcp_manager
        self.workflow = None
        
        # Define compensation mappings
        self.compensation_map = {
            "create_user_account": self._compensate_create_user,
            "charge_payment": self._compensate_payment,
            "send_notification": self._compensate_notification,
            "update_inventory": self._compensate_inventory,
            "create_shipping_label": self._compensate_shipping
        }
    
    async def build_workflow(self) -> StateGraph:
        """Build workflow with compensation handling."""
        workflow = StateGraph(CompensationWorkflowState)
        
        # Add processing nodes with compensation
        workflow.add_node("initialize_transaction", self._initialize_transaction)
        workflow.add_node("step_1_user_account", self._create_user_account)
        workflow.add_node("step_2_payment", self._charge_payment)
        workflow.add_node("step_3_notification", self._send_notification)
        workflow.add_node("step_4_inventory", self._update_inventory)
        workflow.add_node("step_5_shipping", self._create_shipping_label)
        workflow.add_node("finalize_transaction", self._finalize_transaction)
        workflow.add_node("compensation_handler", self._execute_compensation)
        workflow.add_node("recovery_handler", self._handle_recovery)
        
        # Define execution flow
        workflow.set_entry_point("initialize_transaction")
        workflow.add_edge("initialize_transaction", "step_1_user_account")
        
        # Conditional flows with error handling
        workflow.add_conditional_edges(
            "step_1_user_account",
            self._check_step_status,
            {
                "continue": "step_2_payment",
                "retry": "recovery_handler",
                "compensate": "compensation_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "step_2_payment",
            self._check_step_status,
            {
                "continue": "step_3_notification",
                "retry": "recovery_handler", 
                "compensate": "compensation_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "step_3_notification",
            self._check_step_status,
            {
                "continue": "step_4_inventory",
                "retry": "recovery_handler",
                "compensate": "compensation_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "step_4_inventory",
            self._check_step_status,
            {
                "continue": "step_5_shipping",
                "retry": "recovery_handler",
                "compensate": "compensation_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "step_5_shipping",
            self._check_step_status,
            {
                "continue": "finalize_transaction",
                "retry": "recovery_handler",
                "compensate": "compensation_handler"
            }
        )
        
        # Recovery and compensation flows
        workflow.add_conditional_edges(
            "recovery_handler",
            self._check_recovery_status,
            {
                "retry_step_1": "step_1_user_account",
                "retry_step_2": "step_2_payment",
                "retry_step_3": "step_3_notification",
                "retry_step_4": "step_4_inventory",
                "retry_step_5": "step_5_shipping",
                "compensate": "compensation_handler",
                "abort": END
            }
        )
        
        workflow.add_edge("compensation_handler", END)
        workflow.add_edge("finalize_transaction", END)
        
        self.workflow = workflow.compile()
        return self.workflow
    
    async def _initialize_transaction(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Initialize transaction with compensation tracking."""
        state.transaction_id = f"txn_{int(time.time())}"
        state.executed_steps = []
        state.failed_steps = []
        state.compensation_actions = []
        state.step_results = {}
        state.checkpoint_data = {"initialized": True, "start_time": time.time()}
        
        logger.info(f"Initialized transaction {state.transaction_id}")
        return state
    
    async def _create_user_account(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Step 1: Create user account with compensation tracking."""
        step_name = "create_user_account"
        
        try:
            # Save checkpoint before execution
            state.checkpoint_data[step_name] = {"status": "executing", "timestamp": time.time()}
            
            # Simulate user account creation
            adapter = await self.mcp_manager.get_adapter("database")
            if adapter:
                result = await adapter.call_tool("insert", {
                    "table": "users",
                    "data": {"query": state.query, "transaction_id": state.transaction_id}
                })
                
                state.step_results[step_name] = result
                state.executed_steps.append(step_name)
                
                # Register compensation action
                compensation = CompensationAction(
                    step_name=step_name,
                    compensation_function="delete_user_account",
                    compensation_args={"user_id": result.get("user_id"), "transaction_id": state.transaction_id}
                )
                state.compensation_actions.append(compensation)
                
                logger.info(f"Successfully executed {step_name}")
            else:
                raise Exception("Database adapter not available")
            
        except Exception as e:
            state.failed_steps.append(step_name)
            state.step_results[step_name] = {"error": str(e)}
            logger.error(f"Failed to execute {step_name}: {e}")
        
        return state
    
    async def _charge_payment(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Step 2: Charge payment with compensation tracking."""
        step_name = "charge_payment"
        
        try:
            state.checkpoint_data[step_name] = {"status": "executing", "timestamp": time.time()}
            
            # Simulate payment processing
            # In real implementation, this would call payment processor
            result = {
                "payment_id": f"pay_{int(time.time())}",
                "amount": 99.99,
                "status": "charged",
                "transaction_id": state.transaction_id
            }
            
            state.step_results[step_name] = result
            state.executed_steps.append(step_name)
            
            # Register compensation action
            compensation = CompensationAction(
                step_name=step_name,
                compensation_function="refund_payment",
                compensation_args={"payment_id": result["payment_id"], "amount": result["amount"]}
            )
            state.compensation_actions.append(compensation)
            
            logger.info(f"Successfully executed {step_name}")
            
        except Exception as e:
            state.failed_steps.append(step_name)
            state.step_results[step_name] = {"error": str(e)}
            logger.error(f"Failed to execute {step_name}: {e}")
        
        return state
    
    async def _send_notification(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Step 3: Send notification with compensation tracking."""
        step_name = "send_notification"
        
        try:
            state.checkpoint_data[step_name] = {"status": "executing", "timestamp": time.time()}
            
            # Simulate notification sending
            result = {
                "notification_id": f"notif_{int(time.time())}",
                "recipient": "user@example.com",
                "status": "sent",
                "transaction_id": state.transaction_id
            }
            
            state.step_results[step_name] = result
            state.executed_steps.append(step_name)
            
            # Register compensation action
            compensation = CompensationAction(
                step_name=step_name,
                compensation_function="send_cancellation_notification",
                compensation_args={"notification_id": result["notification_id"], "recipient": result["recipient"]}
            )
            state.compensation_actions.append(compensation)
            
            logger.info(f"Successfully executed {step_name}")
            
        except Exception as e:
            state.failed_steps.append(step_name)
            state.step_results[step_name] = {"error": str(e)}
            logger.error(f"Failed to execute {step_name}: {e}")
        
        return state
    
    async def _update_inventory(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Step 4: Update inventory with compensation tracking."""
        step_name = "update_inventory"
        
        try:
            state.checkpoint_data[step_name] = {"status": "executing", "timestamp": time.time()}
            
            # Simulate inventory update
            adapter = await self.mcp_manager.get_adapter("database")
            if adapter:
                result = await adapter.call_tool("update", {
                    "table": "inventory",
                    "data": {"quantity": -1, "transaction_id": state.transaction_id}
                })
                
                state.step_results[step_name] = result
                state.executed_steps.append(step_name)
                
                # Register compensation action
                compensation = CompensationAction(
                    step_name=step_name,
                    compensation_function="restore_inventory",
                    compensation_args={"item_id": "item_123", "quantity": 1}
                )
                state.compensation_actions.append(compensation)
                
                logger.info(f"Successfully executed {step_name}")
            else:
                raise Exception("Database adapter not available")
            
        except Exception as e:
            state.failed_steps.append(step_name)
            state.step_results[step_name] = {"error": str(e)}
            logger.error(f"Failed to execute {step_name}: {e}")
        
        return state
    
    async def _create_shipping_label(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Step 5: Create shipping label with compensation tracking."""
        step_name = "create_shipping_label"
        
        try:
            state.checkpoint_data[step_name] = {"status": "executing", "timestamp": time.time()}
            
            # Simulate shipping label creation
            result = {
                "label_id": f"label_{int(time.time())}",
                "tracking_number": f"TRK{int(time.time())}",
                "status": "created",
                "transaction_id": state.transaction_id
            }
            
            state.step_results[step_name] = result
            state.executed_steps.append(step_name)
            
            # Register compensation action
            compensation = CompensationAction(
                step_name=step_name,
                compensation_function="cancel_shipping_label",
                compensation_args={"label_id": result["label_id"], "tracking_number": result["tracking_number"]}
            )
            state.compensation_actions.append(compensation)
            
            logger.info(f"Successfully executed {step_name}")
            
        except Exception as e:
            state.failed_steps.append(step_name)
            state.step_results[step_name] = {"error": str(e)}
            logger.error(f"Failed to execute {step_name}: {e}")
        
        return state
    
    def _check_step_status(self, state: CompensationWorkflowState) -> str:
        """Check status of last executed step."""
        if state.failed_steps:
            last_failed = state.failed_steps[-1]
            
            if state.recovery_attempts < state.max_recovery_attempts:
                return "retry"
            else:
                return "compensate"
        
        return "continue"
    
    async def _handle_recovery(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Handle recovery attempts."""
        state.recovery_attempts += 1
        
        if state.failed_steps:
            failed_step = state.failed_steps[-1]
            logger.info(f"Attempting recovery for {failed_step} (attempt {state.recovery_attempts})")
            
            # Clear the failed step to retry
            state.failed_steps.remove(failed_step)
            
            # Add some delay before retry
            await asyncio.sleep(1.0)
        
        return state
    
    def _check_recovery_status(self, state: CompensationWorkflowState) -> str:
        """Determine recovery action."""
        if state.failed_steps:
            failed_step = state.failed_steps[-1]
            
            if state.recovery_attempts >= state.max_recovery_attempts:
                return "compensate"
            
            # Route to specific retry based on failed step
            return f"retry_{failed_step}"
        
        return "abort"
    
    async def _execute_compensation(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Execute compensation actions for failed transaction."""
        state.final_status = TransactionStatus.FAILED
        
        logger.warning(f"Executing compensation for transaction {state.transaction_id}")
        
        # Execute compensation actions in reverse order
        for compensation in reversed(state.compensation_actions):
            if not compensation.executed:
                try:
                    await self._execute_single_compensation(compensation)
                    compensation.executed = True
                    compensation.execution_time = time.time()
                    logger.info(f"Executed compensation: {compensation.compensation_function}")
                    
                except Exception as e:
                    logger.error(f"Compensation failed: {compensation.compensation_function} - {e}")
        
        state.final_status = TransactionStatus.COMPENSATED
        return state
    
    async def _execute_single_compensation(self, compensation: CompensationAction):
        """Execute a single compensation action."""
        func_name = compensation.compensation_function
        
        if func_name in self.compensation_map:
            compensation_func = self.compensation_map[func_name]
            await compensation_func(compensation.compensation_args)
        else:
            logger.warning(f"No compensation function found for {func_name}")
    
    async def _finalize_transaction(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Finalize successful transaction."""
        state.final_status = TransactionStatus.COMPLETED
        
        logger.info(f"Transaction {state.transaction_id} completed successfully")
        logger.info(f"Executed steps: {state.executed_steps}")
        
        return state
    
    # Compensation functions
    async def _compensate_create_user(self, args: Dict[str, Any]):
        """Compensate user account creation."""
        adapter = await self.mcp_manager.get_adapter("database")
        if adapter:
            await adapter.call_tool("delete", {
                "table": "users",
                "id": args["user_id"]
            })
    
    async def _compensate_payment(self, args: Dict[str, Any]):
        """Compensate payment charge."""
        # Simulate refund processing
        logger.info(f"Refunding payment {args['payment_id']} amount {args['amount']}")
    
    async def _compensate_notification(self, args: Dict[str, Any]):
        """Compensate notification sending."""
        # Send cancellation notification
        logger.info(f"Sending cancellation notification to {args['recipient']}")
    
    async def _compensate_inventory(self, args: Dict[str, Any]):
        """Compensate inventory update."""
        adapter = await self.mcp_manager.get_adapter("database")
        if adapter:
            await adapter.call_tool("update", {
                "table": "inventory",
                "data": {"quantity": args["quantity"]}
            })
    
    async def _compensate_shipping(self, args: Dict[str, Any]):
        """Compensate shipping label creation."""
        # Cancel shipping label
        logger.info(f"Cancelling shipping label {args['label_id']}")
    
    async def run_compensation_workflow(self, query: str) -> Dict[str, Any]:
        """Execute workflow with compensation handling."""
        if not self.workflow:
            await self.build_workflow()
        
        initial_state = CompensationWorkflowState(
            query=query,
            messages=[HumanMessage(content=query)],
            transaction_id=""
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": final_state.final_status == TransactionStatus.COMPLETED,
                "transaction_id": final_state.transaction_id,
                "final_status": final_state.final_status.value,
                "executed_steps": final_state.executed_steps,
                "failed_steps": final_state.failed_steps,
                "recovery_attempts": final_state.recovery_attempts,
                "compensation_actions": len([c for c in final_state.compensation_actions if c.executed]),
                "step_results": final_state.step_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
```

## Module Assessment

**Question 1:** What is the primary advantage of parallel processing in workflows?  
A) Simplified code structure
B) Reduced resource usage
C) Faster overall execution time
D) Better error handling

**Question 2:** In conditional workflow routing, what determines the execution path?  
A) Random selection
B) Runtime conditions and content analysis
C) User preferences
D) System load

**Question 3:** What is the purpose of compensation actions in workflow patterns?  
A) Improve performance
B) Undo completed steps when later steps fail
C) Reduce memory usage
D) Simplify configuration

**Question 4:** How does the parallel workflow handle partial failures?  
A) Stops all processing immediately
B) Continues with successful results and reports failures
C) Retries all operations
D) Ignores failed operations

**Question 5:** What triggers escalation in the conditional workflow router?  
A) High system load
B) Customer tier, priority level, or escalation keywords
C) Time of day
D) Random intervals

**Question 6:** In the compensation pattern, in what order are compensation actions executed?  
A) Random order
B) Same order as original execution
C) Reverse order of original execution
D) Priority-based order

**Question 7:** What is the benefit of checkpoint data in advanced workflows?  
A) Performance optimization
B) State recovery and resumption after failures
C) User experience improvement
D) Reduced memory usage

[**View Module B Test Solutions →**](Session3_ModuleB_Test_Solutions.md)

---

[← Back to Session 3](Session3_LangChain_MCP_Integration.md) | [Previous: Module A](Session3_ModuleA_Enterprise_Patterns.md)
