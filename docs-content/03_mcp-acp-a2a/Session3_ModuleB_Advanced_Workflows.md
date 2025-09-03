# Session 3 - Module B: Advanced Workflow Orchestration

> **⚠️ ADVANCED OPTIONAL MODULE**
> Prerequisites: Complete Session 3 core content first.

Advanced workflow orchestration patterns enable parallel processing, conditional routing, state management, and error recovery for complex enterprise agent systems.

## Advanced Orchestration Patterns

### Pattern 1: Parallel Processing with Result Aggregation

When multiple independent operations can run simultaneously, parallel processing dramatically improves performance.

```python
# workflows/parallel_processor.py - Core imports and state definition
import asyncio
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
import time
import logging
```

These imports establish the foundation for our parallel processing workflow system. We use `asyncio` for concurrent execution across multiple data sources, `dataclasses` for clean state management, and `langgraph` for building the sophisticated workflow orchestration. This combination enables enterprise-scale parallel processing with proper error handling and result aggregation.

```python
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
```

The `ParallelWorkflowState` captures results from three independent data sources that can be processed simultaneously. Each result field stores the outcome from weather APIs, file systems, and database queries. This parallel architecture dramatically improves performance by eliminating sequential waiting - instead of processing data sources one-by-one, the system processes all three concurrently.

```python
    # Processing status tracking
    completed_tasks: Set[str] = field(default_factory=set)
    failed_tasks: Set[str] = field(default_factory=set)
    start_time: Optional[float] = None

    # Final aggregated result
    aggregated_result: Optional[Dict] = None
    processing_time: Optional[float] = None
```

Status tracking enables sophisticated parallel coordination. The `completed_tasks` and `failed_tasks` sets track which operations finish successfully or encounter errors. The `start_time` enables precise performance measurement, while `aggregated_result` combines all parallel results into a unified response. This design ensures that partial failures don't prevent successful results from being returned.

```python
class ParallelWorkflowOrchestrator:
    """Advanced parallel workflow with intelligent task coordination."""

    def __init__(self, mcp_manager):
        self.mcp_manager = mcp_manager
        self.workflow = None
```

The orchestrator manages the entire parallel workflow lifecycle. The MCP manager provides access to various data adapters (weather, filesystem, database), while the workflow graph coordinates parallel execution. This separation of concerns enables the orchestrator to focus on coordination logic while adapters handle domain-specific operations.

```python
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
```

The workflow architecture separates initialization, parallel processing, result aggregation, and error handling into distinct nodes. The initializer sets up tracking state, the three processor nodes execute concurrently, and the aggregator combines results. This modular design enables independent scaling and optimization of each processing domain.

```python
        # Define parallel execution flow
        workflow.set_entry_point("initializer")

        # Fan out to parallel processors
        workflow.add_edge("initializer", "weather_processor")
        workflow.add_edge("initializer", "file_processor")
        workflow.add_edge("initializer", "database_processor")
```

The fan-out pattern creates three parallel execution paths from the initializer. Unlike sequential processing, these edges enable simultaneous execution of weather, file, and database operations. This parallel fan-out is the key to achieving significant performance improvements in data-intensive workflows.

```python
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
```

Conditional aggregation implements intelligent coordination logic. Each processor checks whether all parallel tasks are complete before proceeding to aggregation. The "wait" option allows other processors to continue running, while "aggregate" triggers result combination, and "error" handles failures gracefully. This coordination ensures optimal resource utilization and proper error handling.

```python
        workflow.add_edge("aggregator", END)
        workflow.add_edge("error_handler", END)

        self.workflow = workflow.compile()
        return self.workflow
```

Workflow compilation creates the executable state machine that orchestrates parallel processing. The compiled workflow optimizes the execution graph and validates the routing logic, ensuring reliable parallel coordination in production environments.

```python
    async def _initialize_processing(self, state: ParallelWorkflowState) -> ParallelWorkflowState:
        """Initialize parallel processing state."""
        state.start_time = time.time()
        state.completed_tasks = set()
        state.failed_tasks = set()
        logger.info(f"Starting parallel processing for query: {state.query}")
        return state
```

Initialization establishes the coordination infrastructure needed for parallel processing. The timestamp enables precise performance measurement, while the task sets track completion status across concurrent operations. This setup phase is crucial for monitoring parallel execution and ensuring reliable result aggregation.

```python
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
```

The weather processor demonstrates nested parallelization - processing multiple cities concurrently within the larger parallel workflow. The `asyncio.gather()` function executes all city weather requests simultaneously, with `return_exceptions=True` ensuring that failures in one city don't prevent processing of others. This approach maximizes throughput while maintaining resilience.

```python
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
```

Result aggregation and status tracking ensure that successful city weather data is preserved even when some cities fail. The completion tracking enables the coordination logic to determine when all parallel tasks are finished. This robust error handling prevents partial failures from blocking the entire workflow.

```python
        except Exception as e:
            state.failed_tasks.add("weather")
            state.weather_result = {"error": str(e)}
            logger.error(f"Weather processing failed: {e}")

        return state
```

Comprehensive error handling ensures that weather processing failures are captured and reported without crashing the entire parallel workflow. The failed task tracking enables intelligent decision-making about whether to proceed with partial results or trigger error handling workflows.

```python
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
```

Timeout handling prevents slow weather API calls from blocking the entire parallel workflow. The 5-second timeout provides reasonable response time expectations while ensuring that unresponsive services don't degrade overall system performance. This pattern is essential in production systems where external service reliability varies.

```python
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
```

File processing demonstrates another level of parallelization - searching for multiple terms simultaneously across the filesystem. This approach dramatically improves search performance by leveraging concurrent I/O operations. The parallel search pattern is particularly effective for large codebases or document repositories.

```python
                file_data = {}
                for term, result in zip(search_terms, results):
                    if not isinstance(result, Exception):
                        file_data[f"files_for_{term}"] = result

                state.file_result = file_data
            else:
                state.file_result = {"error": "File service unavailable"}

            state.completed_tasks.add("files")
            logger.info("File processing completed")
```

Result organization creates structured output where each search term's results are clearly identified. This organization enables downstream processing to understand which files relate to specific search criteria, improving the utility of aggregated results.

```python
        except Exception as e:
            state.failed_tasks.add("files")
            state.file_result = {"error": str(e)}
            logger.error(f"File processing failed: {e}")

        return state
```

File processing error handling ensures that filesystem failures don't prevent weather and database processing from completing successfully. This resilience is crucial in distributed systems where different data sources have varying reliability characteristics.

```python
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
```

File search timeout handling uses a longer 10-second limit to account for filesystem I/O latency. The pattern matching enables flexible filename searches, while the timeout prevents hanging on unresponsive filesystem operations. This balance between thoroughness and responsiveness is essential for user-facing applications.

```python
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
```

Database processing executes multiple queries in parallel across different data tables or schemas. This approach is particularly effective when queries target different database partitions or when using connection pooling. The parallel query execution can significantly reduce overall database interaction time.

```python
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
```

Database result organization maintains clear relationships between query types and their results. This structure enables downstream processing to understand the context and relevance of different data sets, improving the quality of aggregated insights.

```python
        except Exception as e:
            state.failed_tasks.add("database")
            state.database_result = {"error": str(e)}
            logger.error(f"Database processing failed: {e}")

        return state
```

Database error handling ensures that query failures are contained and don't impact other parallel processing streams. This isolation is crucial in enterprise environments where database availability may vary independently from other services.

```python
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
```

Database query timeout uses a longer 15-second limit to accommodate complex analytical queries while preventing indefinite blocking. This timeout strategy recognizes that database operations often require more processing time than API calls or file operations, but still need bounded execution time for system reliability.

```python
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
```

Completion status checking implements the coordination logic that determines when all parallel processing is finished. The set operation `all_tasks >= expected_tasks` efficiently checks whether all three processing streams have completed (either successfully or with failures). This logic enables intelligent workflow routing based on actual execution state.

```python
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
```

Result aggregation combines outcomes from all parallel processing streams into a unified response structure. The processing time measurement demonstrates the performance benefits of parallel execution - the total time reflects the longest individual operation rather than the sum of all operations. This aggregation provides comprehensive visibility into both successful results and processing metadata.

```python
        if state.weather_result:
            aggregated["results"]["weather"] = state.weather_result

        if state.file_result:
            aggregated["results"]["files"] = state.file_result

        if state.database_result:
            aggregated["results"]["database"] = state.database_result
```

Selective result inclusion ensures that only available results are included in the final response. This approach handles partial success scenarios gracefully, providing value even when some parallel operations fail. The conditional inclusion prevents null or undefined values from cluttering the response.

```python
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
```

Summary generation provides human-readable insights into parallel processing outcomes. The summary creation logic intelligently describes what was accomplished, helping users understand the scope and success of their query. The comprehensive logging enables performance monitoring and troubleshooting in production environments.

```python
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
```

Error handling creates structured output that separates successful partial results from specific error details. This organization enables client applications to extract value from partial success while understanding exactly what failed and why. The separation of concerns improves error reporting and debugging capabilities.

```python
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
```

Error categorization enables intelligent handling of partial success scenarios. By separating successful results from error details, the system can provide maximum value even when some operations fail. This approach is essential in distributed systems where component failures are expected and must be handled gracefully.

```python
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
```

Helper methods demonstrate intelligent query parsing that extracts meaningful parameters for parallel processing. The city extraction enables geographic weather queries, while search term extraction creates focused file searches. These parsing functions convert natural language queries into structured parameters for parallel execution.

```python
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

The workflow execution method provides the main interface for running parallel processing workflows. The lazy workflow compilation optimizes startup time, while the comprehensive error handling ensures graceful failure modes. The structured return format enables client applications to easily distinguish between successful and failed executions while accessing all available results and metadata.

### Pattern 2: Conditional Workflow Routing

Dynamic workflows adapt their execution path based on runtime conditions and intermediate results. This pattern implements intelligent content analysis and routing to ensure queries reach the most appropriate processing pipeline.

```python
# workflows/conditional_router.py - Imports and classification enums
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re
import logging
```

These imports establish the foundation for intelligent workflow routing. The `re` module enables sophisticated pattern matching for content analysis, while the typing imports ensure robust type checking for complex routing logic. This approach enables enterprise-grade content classification and routing decisions.

```python
logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    CUSTOMER_SERVICE = "customer_service"
    TECHNICAL_SUPPORT = "technical_support"
    SALES_INQUIRY = "sales_inquiry"
    DATA_ANALYSIS = "data_analysis"
    GENERAL_QUERY = "general_query"
```

The `WorkflowType` enum defines the major business domains that require different processing approaches. Each workflow type corresponds to specialized handling logic, routing requests to appropriate teams or systems. This classification enables organizations to automate initial query routing, reducing response times and improving customer experience.

```python
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
```

Priority levels create a numerical hierarchy enabling automated SLA management and resource allocation. Higher priority requests receive expedited processing and may trigger escalation workflows. This systematic approach ensures critical issues receive immediate attention while maintaining efficient resource utilization.

```python
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
```

The workflow state captures comprehensive classification metadata extracted from the incoming query. `workflow_type` determines the processing pipeline, `priority` influences resource allocation, and `customer_tier` enables personalized service levels. The `urgency_keywords` provide audit trails for classification decisions, supporting continuous improvement of routing accuracy.

```python
    # Processing results
    primary_result: Optional[Dict] = None
    escalation_result: Optional[Dict] = None

    # Routing decisions
    routing_path: List[str] = None
    escalated: bool = False
```

The state design separates classification results from processing outcomes, enabling clear audit trails and debugging capabilities. The `routing_path` tracks the complete workflow journey, while the `escalated` flag triggers specialized handling for high-priority or sensitive issues.

```python
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
```

The router initialization establishes pattern-based classification rules using regular expressions. Customer service patterns capture common account management, order management, and access-related queries. This rule-based approach enables precise routing while remaining maintainable and auditable.

```python
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
```

Technical support patterns identify system issues, API problems, and performance concerns, routing them to specialized technical teams. Sales inquiry patterns detect commercial interest, triggering sales-optimized workflows. Data analysis patterns route analytical requests to appropriate data processing pipelines. This comprehensive pattern library enables accurate domain classification.

```python
        self.urgency_patterns = [
            (r"urgent|emergency|critical|asap|immediately", Priority.CRITICAL),
            (r"important|priority|soon|quickly", Priority.HIGH),
            (r"please|when possible|sometime", Priority.MEDIUM)
        ]
```

Urgency pattern detection enables automatic priority classification based on customer language. Critical keywords trigger immediate escalation, high priority patterns ensure faster response times, and polite language patterns indicate standard priority levels. This linguistic analysis automates triage decisions that traditionally required human judgment.

```python
        self.escalation_triggers = [
            r"complaint|frustrated|angry|disappointed",
            r"manager|supervisor|escalate",
            r"unacceptable|terrible|worst"
        ]
```

Escalation triggers detect emotionally charged language and explicit escalation requests, automatically routing these queries to senior staff or specialized escalation workflows. This proactive approach prevents customer dissatisfaction from escalating while ensuring appropriate resources handle sensitive situations.

```python
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
```

The workflow architecture separates classification from specialized processing, creating a modular design that's easy to maintain and extend. Each handler node specializes in processing specific query types, while the classifier acts as an intelligent routing gateway. This separation of concerns enables teams to independently optimize their domain-specific processing logic.

```python
        # Set entry point
        workflow.set_entry_point("classifier")
```

The classifier serves as the single entry point, ensuring all queries undergo consistent analysis and routing. This centralized approach enables comprehensive logging, metrics collection, and routing rule management across the entire system.

```python
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
```

Conditional routing creates dynamic execution paths based on classification results. The `_route_workflow` function determines the appropriate handler based on query analysis, enabling sophisticated decision-making about processing approaches. This flexibility allows the system to adapt to different query types while maintaining consistent handling patterns.

```python
        # Priority processing after main handling
        workflow.add_edge("customer_service_handler", "priority_processor")
        workflow.add_edge("technical_support_handler", "priority_processor")
        workflow.add_edge("sales_handler", "priority_processor")
        workflow.add_edge("data_analysis_handler", "priority_processor")
        workflow.add_edge("general_handler", "priority_processor")
```

Priority processing creates a common post-processing stage where priority-specific handling occurs. This design ensures consistent priority-based resource allocation and SLA management across all query types, while allowing domain-specific handlers to focus on their specialized processing logic.

```python
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
```

Escalation handling provides a safety net for high-priority or sensitive queries that require specialized attention. The conditional logic determines whether escalation is needed based on priority levels, customer tiers, or explicit escalation triggers, ensuring appropriate resource allocation for critical issues.

```python
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
```

Query classification uses scoring-based pattern matching to determine the most appropriate workflow type. Each pattern match increases the score for that workflow category, enabling accurate classification even when queries contain mixed content. This approach handles ambiguous queries gracefully while maintaining high classification accuracy.

```python
        # Select highest scoring workflow type
        if max(workflow_scores.values()) > 0:
            state.workflow_type = max(workflow_scores, key=workflow_scores.get)
        else:
            state.workflow_type = WorkflowType.GENERAL_QUERY
```

The scoring mechanism handles edge cases gracefully, defaulting to general query processing when no specific patterns match. This ensures that the system can process any input, even queries that don't fit established categories, maintaining robustness and preventing system failures.

```python
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
```

Priority determination uses hierarchical matching, selecting the highest priority level found in the query. The urgency keywords extraction provides transparency into classification decisions, enabling audit trails and continuous improvement of pattern recognition accuracy.

```python
        # Check for escalation triggers
        for pattern in self.escalation_triggers:
            if re.search(pattern, query_lower):
                state.escalated = True
                break

        # Routing path tracking
        state.routing_path = ["classifier"]

        logger.info(f"Classified query as {state.workflow_type.value} with priority {state.priority.value}")

        return state
```

Escalation trigger detection and routing path tracking complete the classification process. The comprehensive logging provides visibility into classification decisions, enabling monitoring and optimization of routing accuracy over time.

```python
    def _route_workflow(self, state: ConditionalWorkflowState) -> str:
        """Route workflow based on classification."""
        if state.escalated:
            return "escalation"

        return state.workflow_type.value
```

The routing decision prioritizes escalation over normal workflow routing, ensuring that sensitive or high-priority queries receive immediate attention. This simple but effective logic prevents escalation-worthy queries from getting lost in standard processing pipelines.

```python
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
```

Customer service handling demonstrates personalized processing based on customer data. The customer tier determination enables differentiated service levels, ensuring premium customers receive enhanced support while maintaining efficient service for all customers. This approach balances resource allocation with customer satisfaction objectives.

```python
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
```

Customer service processing includes comprehensive error handling with fallback responses, ensuring that system failures don't leave customers without support. The personalized recommendations based on customer tier and query content demonstrate how AI can enhance traditional customer service operations.

```python
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
```

Technical support handling integrates with system monitoring capabilities, automatically checking logs and system status to provide context-aware support. This approach enables proactive issue identification and more accurate problem diagnosis, reducing resolution times and improving customer experience.

```python
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
```

Technical support combines automated analysis with severity assessment, enabling intelligent triage and resource allocation. The technical recommendations provide actionable next steps, helping both support agents and customers resolve issues efficiently.

```python
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
```

Sales inquiry handling integrates with product databases to provide accurate, up-to-date pricing and feature information. This automated approach ensures consistent sales messaging while enabling rapid response to customer inquiries.

```python
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
```

Sales processing includes lead quality assessment, enabling prioritization of high-value prospects and appropriate resource allocation. The automated recommendations help sales teams focus their efforts on the most promising opportunities while ensuring all inquiries receive appropriate attention.

```python
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
```

Data analysis handling connects to analytical databases and systems to provide data-driven insights. This automated approach enables rapid response to analytical requests while ensuring data accuracy and consistency across different analysis scenarios.

```python
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
```

Data analysis processing generates actionable insights and visualizations, transforming raw analytical requests into meaningful business intelligence. The automated insight generation helps users understand complex data patterns without requiring deep analytical expertise.

```python
    async def _handle_general_query(self, state: ConditionalWorkflowState) -> ConditionalWorkflowState:
        """Handle general query workflow."""
        state.routing_path.append("general")

        state.primary_result = {
            "type": "general_query",
            "action": "General information provided",
            "response": "Comprehensive general response based on available data"
        }

        return state
```

General query handling provides a catch-all processor for queries that don't fit specific categories. This ensures system robustness and prevents query rejection, while maintaining consistent response patterns across all query types.

```python
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
```

Priority processing applies consistent SLA management across all query types, ensuring high-priority queries receive expedited handling regardless of their domain classification. The priority flags enable downstream systems to appropriately allocate resources and track SLA compliance.

```python
    def _check_escalation_needed(self, state: ConditionalWorkflowState) -> str:
        """Check if escalation is needed."""
        if (state.escalated or
            state.priority == Priority.CRITICAL or
            (state.customer_tier == "premium" and state.priority == Priority.HIGH)):
            return "escalate"

        return "complete"
```

Escalation logic combines multiple factors including explicit escalation flags, critical priority levels, and customer tier considerations. This multi-dimensional approach ensures that escalation decisions account for both technical priority and business importance.

```python
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
```

Escalation handling preserves the original processing results while adding escalation metadata, enabling senior staff to understand both the customer's issue and the initial processing attempts. This comprehensive context improves escalation efficiency and customer satisfaction.

```python
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
```

Helper methods implement business logic for customer tier determination and severity assessment. These functions encapsulate domain expertise, enabling consistent evaluation criteria across different processing scenarios while maintaining flexibility for business rule evolution.

```python
    def _assess_lead_quality(self, state: ConditionalWorkflowState) -> str:
        """Assess sales lead quality."""
        if any(word in state.query.lower() for word in ["demo", "trial", "purchase", "buy"]):
            return "hot"
        elif any(word in state.query.lower() for word in ["price", "cost", "quote"]):
            return "warm"
        else:
            return "cold"
```

Lead quality assessment provides automated sales qualification, helping prioritize follow-up efforts and resource allocation. The scoring system identifies prospects likely to convert, enabling sales teams to focus on high-value opportunities.

```python
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
```

Domain-specific recommendations provide actionable next steps tailored to each workflow type. Customer service recommendations focus on account verification and documentation, while technical recommendations emphasize diagnostic procedures. This specialization ensures appropriate guidance for different issue types.

```python
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
```

Sales and analytics recommendations provide specific, actionable guidance tailored to each domain's needs. Sales recommendations focus on conversion activities, while analytics recommendations emphasize insight delivery and visualization. This specialization ensures appropriate outcomes for different query types.

```python
    async def run_conditional_workflow(self, query: str) -> Dict[str, Any]:
        """Execute conditional workflow."""
        if not self.workflow:
            await self.build_workflow()

        initial_state = ConditionalWorkflowState(
            query=query,
            messages=[HumanMessage(content=query)]
        )
```

The workflow execution method provides the primary interface for conditional routing. State initialization creates a clean processing context, while the workflow compilation ensures all routing logic is properly configured before execution begins.

```python
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

Advanced workflows implement compensation patterns to handle failures and maintain data consistency. The Saga pattern ensures that when complex multi-step transactions fail, all completed steps are properly rolled back to maintain system integrity.

```python
# workflows/compensation_handler.py - Core imports and data structures
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import logging
```

These imports establish the foundation for our compensation workflow system. We use `asyncio` for handling concurrent operations during rollback, `dataclasses` for clean state management, and `Enum` for type-safe transaction status tracking. The compensation pattern is crucial in distributed systems where partial failures must not leave the system in an inconsistent state.

```python
logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"
```

The `TransactionStatus` enum defines the lifecycle states of our distributed transaction. This follows the Saga pattern where transactions can either complete successfully, fail and require compensation, or be fully compensated back to the original state. This enum provides type safety and clear status tracking throughout the complex workflow.

```python
@dataclass
class CompensationAction:
    """Represents a compensation action for failed operations."""
    step_name: str
    compensation_function: str
    compensation_args: Dict[str, Any]
    executed: bool = False
    execution_time: Optional[float] = None
```

The `CompensationAction` dataclass encapsulates everything needed to undo a completed operation. Each successful workflow step registers its corresponding undo action. The `step_name` links to the original operation, `compensation_function` specifies the rollback method, and `compensation_args` contains the data needed for rollback. This design enables precise, trackable compensation of any failed transaction.

```python
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
```

The workflow state tracks the complete transaction lifecycle. `executed_steps` and `failed_steps` provide audit trails for debugging and compliance. `compensation_actions` accumulates the undo operations as each step completes, creating a complete rollback plan. This comprehensive state tracking enables sophisticated error recovery and system reliability.

```python
    # Results tracking
    step_results: Dict[str, Any] = field(default_factory=dict)
    final_status: TransactionStatus = TransactionStatus.PENDING

    # Recovery information
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3
```

The results tracking captures outcomes from each workflow step, enabling partial success reporting and detailed failure analysis. `checkpoint_data` stores intermediate state for recovery scenarios, while `recovery_attempts` implements exponential backoff and circuit breaker patterns. This design supports both immediate retry logic and long-term system resilience.

```python
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
```

The `CompensationWorkflowHandler` implements the Saga orchestrator pattern. The `compensation_map` creates a registry of undo operations for each workflow step. This mapping enables the system to automatically determine and execute the correct rollback sequence when failures occur. The pattern ensures that complex business processes can be safely reversed, maintaining data consistency across distributed systems.

This establishes the core compensation workflow infrastructure. Let's examine how the workflow graph is constructed with sophisticated error handling:

```python
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
```

This workflow architecture implements a sophisticated e-commerce transaction pipeline with built-in compensation capabilities. Each node represents a critical business step: user account creation, payment processing, notification sending, inventory management, and shipping label generation. The compensation and recovery handlers ensure that any failure triggers appropriate rollback procedures, maintaining system consistency.

```python
        # Define execution flow
        workflow.set_entry_point("initialize_transaction")
        workflow.add_edge("initialize_transaction", "step_1_user_account")
```

The execution flow starts with transaction initialization and proceeds through each business step. Now let's examine the sophisticated conditional routing that handles failures:

```python
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
```

These conditional edges implement sophisticated error handling at each workflow step. When a step completes, `_check_step_status` determines the next action: continue to the next step on success, attempt recovery on transient failures, or execute compensation on permanent failures. This pattern ensures that the system gracefully handles various failure modes while maintaining transaction integrity.

```python
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
```

The conditional routing pattern ensures consistent error handling across all workflow steps. This design enables automated decision-making about whether to proceed, retry, or compensate based on the specific failure characteristics.

```python
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
```

The recovery handler implements intelligent retry routing, directing flow back to the specific failed step rather than restarting the entire workflow. This optimization reduces processing time and resource usage while maintaining transaction safety. When retry limits are exceeded, the system automatically triggers compensation to ensure data consistency.

```python
        workflow.add_edge("compensation_handler", END)
        workflow.add_edge("finalize_transaction", END)

        self.workflow = workflow.compile()
        return self.workflow
```

These final edges complete the workflow graph by defining termination points and compiling the state machine. The compiled workflow becomes an executable graph that can handle complex transaction flows with sophisticated error recovery.

```python
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
```

Transaction initialization establishes the tracking infrastructure needed for compensation. The unique transaction ID enables correlation across distributed systems, while the checkpoint data provides recovery points. This setup phase is critical for maintaining transaction integrity throughout the workflow execution.

```python
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
```

The user account creation step demonstrates the compensation pattern's core principle: every operation that modifies system state must be paired with an undo operation. The checkpoint data captures the execution state, enabling recovery if the step partially completes. This approach ensures atomicity in distributed transactions.

```python
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
```

Each successful step registers its corresponding compensation action, building a complete rollback plan. The compensation action captures all necessary data for undo operations, including the user ID needed for account deletion. This pattern ensures that failures at any point can trigger appropriate cleanup.

```python
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
```

Payment processing represents the most critical step in e-commerce workflows. The checkpoint ensures we can track partial payment states, while the result captures essential payment metadata. In production systems, this would integrate with payment processors like Stripe or PayPal, handling complex payment states and potential authorization vs. capture scenarios.

```python
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
```

Payment processing exemplifies the critical nature of compensation patterns. The refund compensation action captures the exact payment details needed for reversal. This ensures that failed transactions don't leave customers charged for incomplete orders, maintaining both data integrity and customer trust.

```python
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
```

Notification sending demonstrates compensation for communication operations. While you can't "unsend" an email, you can send corrective communications. The compensation action would send a cancellation notice, informing the customer that their order was cancelled due to processing issues. This maintains customer communication integrity throughout the transaction lifecycle.

```python
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
```

Notification compensation ensures customers receive appropriate communication about transaction failures. This pattern maintains transparency and trust by keeping customers informed about order status changes, even when technical failures occur.

```python
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
```

Inventory management requires precise compensation to prevent overselling and stock discrepancies. The inventory decrement operation must be exactly reversible to maintain accurate stock levels. This is crucial in e-commerce systems where inventory consistency directly impacts customer satisfaction and business operations.

```python
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
```

Inventory compensation demonstrates the importance of exact reversal operations. The compensation action restores the exact quantity that was decremented, ensuring inventory accuracy. This pattern prevents stock discrepancies that could lead to overselling or customer disappointment.

```python
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
```

Shipping label creation represents the final fulfillment step in the e-commerce workflow. The compensation action ensures that cancelled orders don't generate shipping costs or create confusion in the fulfillment process. This step demonstrates how compensation patterns extend beyond data consistency to include external service interactions.

```python
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
```

Shipping label compensation prevents unnecessary shipping costs and logistics confusion when transactions fail. The label cancellation ensures clean rollback of the entire fulfillment process, maintaining operational efficiency.

```python
    def _check_step_status(self, state: CompensationWorkflowState) -> str:
        """Check status of last executed step."""
        if state.failed_steps:
            last_failed = state.failed_steps[-1]

            if state.recovery_attempts < state.max_recovery_attempts:
                return "retry"
            else:
                return "compensate"

        return "continue"
```

The status checking logic implements a circuit breaker pattern, determining whether to retry failed operations or trigger compensation. This decision logic balances system resilience with performance, avoiding infinite retry loops while providing reasonable recovery opportunities for transient failures.

```python
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
```

The recovery handler implements exponential backoff and retry logic, providing transient failure resilience while avoiding system overload. The delay between retries helps systems recover from temporary resource constraints.

```python
    def _check_recovery_status(self, state: CompensationWorkflowState) -> str:
        """Determine recovery action."""
        if state.failed_steps:
            failed_step = state.failed_steps[-1]

            if state.recovery_attempts >= state.max_recovery_attempts:
                return "compensate"

            # Route to specific retry based on failed step
            return f"retry_{failed_step}"

        return "abort"
```

Recovery status checking enables intelligent retry routing, directing workflow execution back to the specific failed step rather than restarting the entire process. This optimization saves processing time and resources while maintaining transaction integrity.

```python
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
```

Compensation execution implements the Saga pattern's rollback mechanism, executing undo operations in reverse order of the original execution. This ensures that dependencies between operations are properly handled during rollback, maintaining system consistency even during failure scenarios.

```python
    async def _execute_single_compensation(self, compensation: CompensationAction):
        """Execute a single compensation action."""
        func_name = compensation.compensation_function

        if func_name in self.compensation_map:
            compensation_func = self.compensation_map[func_name]
            await compensation_func(compensation.compensation_args)
        else:
            logger.warning(f"No compensation function found for {func_name}")
```

Single compensation execution demonstrates the registry pattern, using the compensation map to dynamically invoke the appropriate undo function. This design enables flexible, maintainable compensation logic that can easily accommodate new workflow steps.

```python
    async def _finalize_transaction(self, state: CompensationWorkflowState) -> CompensationWorkflowState:
        """Finalize successful transaction."""
        state.final_status = TransactionStatus.COMPLETED

        logger.info(f"Transaction {state.transaction_id} completed successfully")
        logger.info(f"Executed steps: {state.executed_steps}")

        return state
```

Transaction finalization marks the successful completion of the entire workflow. The comprehensive logging provides audit trails and debugging information, essential for enterprise transaction systems that require detailed tracking and compliance reporting.

```python
    # Compensation functions
    async def _compensate_create_user(self, args: Dict[str, Any]):
        """Compensate user account creation."""
        adapter = await self.mcp_manager.get_adapter("database")
        if adapter:
            await adapter.call_tool("delete", {
                "table": "users",
                "id": args["user_id"]
            })
```

User account compensation performs the exact inverse of the original operation, deleting the created user account to maintain data consistency. This ensures that failed transactions don't leave orphaned user accounts in the system, preventing data pollution and security concerns.

```python
    async def _compensate_payment(self, args: Dict[str, Any]):
        """Compensate payment charge."""
        # Simulate refund processing
        logger.info(f"Refunding payment {args['payment_id']} amount {args['amount']}")

    async def _compensate_notification(self, args: Dict[str, Any]):
        """Compensate notification sending."""
        # Send cancellation notification
        logger.info(f"Sending cancellation notification to {args['recipient']}")
```

Payment and notification compensation functions demonstrate different types of undo operations. Payment compensation involves actual refund processing through payment gateways, while notification compensation sends corrective communications. These examples show how compensation adapts to the nature of each operation type.

```python
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
```

Inventory and shipping compensation complete the rollback of physical fulfillment operations. These functions ensure that failed transactions don't result in inventory discrepancies or unnecessary shipping costs, maintaining operational accuracy across the entire business process.

```python
    async def run_compensation_workflow(self, query: str) -> Dict[str, Any]:
        """Execute workflow with compensation handling."""
        if not self.workflow:
            await self.build_workflow()

        initial_state = CompensationWorkflowState(
            query=query,
            messages=[HumanMessage(content=query)],
            transaction_id=""
        )
```

The workflow execution method provides the entry point for running compensation-enabled transactions. The initial state setup creates a clean transaction context, while the workflow compilation ensures all routing logic is properly configured before execution begins.

```python
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

## 🧭 Navigation

**Previous:** [Session 2 - Implementation →](Session2_*.md)  
**Next:** [Session 4 - Team Orchestration →](Session4_*.md)

---
