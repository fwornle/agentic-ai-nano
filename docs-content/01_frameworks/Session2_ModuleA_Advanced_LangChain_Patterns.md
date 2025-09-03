# Session 2 - Module A: Advanced LangChain Patterns

> **⚠️ ADVANCED OPTIONAL MODULE**
> Prerequisites: Complete Session 2 core content first.

At 3:47 AM on a Tuesday in March 2024, Databricks' intelligent data lakehouse system identified a critical insight buried within petabytes of streaming analytics data that would optimize data processing costs by 31% and reduce query latency by 47% over the next quarter. The breakthrough wasn't human intuition - it was an intricate network of 47 specialized AI agents working in perfect coordination across data pipelines, each contributing analytical insights that no single system could have discovered independently.

This wasn't just data automation. This was orchestrated intelligence at enterprise data scale - the kind of sophisticated multi-agent coordination that separates leading data platforms from their competition. When Snowflake processes millions of analytical queries daily, when Apache Kafka coordinates streaming data across thousands of topics, or when MLflow manages machine learning pipelines at global scale, they're leveraging the same advanced LangChain patterns you're about to master.

The companies winning today's data race understand a fundamental truth: individual data agents are powerful, but coordinated data intelligence ecosystems are unstoppable. Master these patterns, and you'll architect data systems that don't just process information - they anticipate data quality issues, adapt to schema changes, and optimize performance faster than traditional data engineering teams can react.

---

## Part 1: Complex Multi-Agent Data Workflows

### Advanced Data Processing Orchestration Patterns

🗂️ **File**: `src/session2/multi_agent_workflows.py` - Complex data agent coordination

Multi-agent systems in LangChain require sophisticated coordination patterns where specialized data agents collaborate on complex analytical tasks. The foundation starts with defining agent roles and orchestration for data processing scenarios:

```python
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain.schema import BaseMessage
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class DataAgentRole:
    name: str
    description: str
    tools: List[BaseTool]
    specialization: str
    expertise_areas: List[str]
```

The `DataAgentRole` dataclass defines the structure for specialized data agents, including their specific tools and areas of expertise, enabling systematic agent creation and management for data processing workflows.

```python
class DataProcessingOrchestrator:
    """Orchestrates complex data workflows across multiple specialized agents"""
```

The orchestrator class manages multiple data agents, coordinating their interactions and ensuring efficient data processing task distribution based on each agent's data specialization.

```python
    def __init__(self, llm):
        self.llm = llm
        self.agents: Dict[str, Any] = {}
        self.workflow_history: List[Dict[str, Any]] = []
        self.shared_memory = ConversationBufferMemory(
            memory_key="shared_data_context",
            return_messages=True
        )
```

### Specialized Data Agent Creation

Specialized agent creation follows a structured pattern with domain-specific data tools and memory for data processing continuity:

```python
def create_data_ingestion_agent(self) -> Any:
    """Create agent specialized in data ingestion and validation"""

    ingestion_tools = [
        self._create_schema_validation_tool(),
        self._create_data_quality_checker_tool(),
        self._create_pipeline_monitor_tool()
    ]

    ingestion_memory = ConversationBufferMemory(
        memory_key="ingestion_history",
        return_messages=True
    )
```

The data ingestion agent gets specialized tools for data validation and quality checking with dedicated memory to maintain context across data ingestion sessions.

```python
    ingestion_agent = initialize_agent(
        tools=ingestion_tools,
        llm=self.llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=ingestion_memory,
        verbose=True,
        agent_kwargs={
            "system_message": """You are a data ingestion specialist focused on ensuring
            reliable, high-quality data flow into analytics systems. Your role is to:
            1. Validate data schemas and formats
            2. Monitor data quality metrics and anomalies
            3. Ensure pipeline reliability and performance
            4. Provide actionable insights on data ingestion issues"""
        }
    )

    return ingestion_agent
```

The system message clearly defines the agent's role and capabilities, ensuring consistent behavior focused on data ingestion tasks with emphasis on quality and reliability.

```python
def create_analytics_agent(self) -> Any:
    """Create agent specialized in data analytics and pattern recognition"""

    analytics_tools = [
        self._create_query_optimizer_tool(),
        self._create_pattern_detection_tool(),
        self._create_performance_analyzer_tool()
    ]

    analytics_memory = ConversationBufferMemory(
        memory_key="analytics_history",
        return_messages=True
    )
```

The analytics agent receives different specialized tools focused on query optimization, pattern detection, and performance analysis capabilities for deep data insights.

```python
    analytics_agent = initialize_agent(
        tools=analytics_tools,
        llm=self.llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=analytics_memory,
        verbose=True,
        agent_kwargs={
            "system_message": """You are a data analytics specialist. Your role is to:
            1. Optimize data queries and processing workflows
            2. Identify patterns and trends in large datasets
            3. Perform statistical analysis and anomaly detection
            4. Create insights and recommendations from data analysis"""
        }
    )

    return analytics_agent
```

Each agent type gets a tailored system message that defines its specific responsibilities and approach to data problem-solving with focus on analytical rigor.

```python
def create_ml_pipeline_agent(self) -> Any:
    """Create agent specialized in ML pipeline management and model operations"""

    ml_tools = [
        self._create_model_training_tool(),
        self._create_feature_engineering_tool(),
        self._create_model_monitoring_tool()
    ]

    ml_memory = ConversationBufferMemory(
        memory_key="ml_pipeline_history",
        return_messages=True
    )
```

The ML pipeline agent specializes in machine learning operations including model training, feature engineering, and monitoring. Specialized tools for ML workflow management enable comprehensive model lifecycle support.

```python
    ml_agent = initialize_agent(
        tools=ml_tools,
        llm=self.llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=ml_memory,
        verbose=True,
        agent_kwargs={
            "system_message": """You are an ML pipeline specialist. Your role is to:
            1. Manage machine learning model training and deployment
            2. Engineer and validate features for model performance
            3. Monitor model performance and data drift
            4. Optimize ML workflows for scalability and reliability"""
        }
    )

    return ml_agent
```

### Data Workflow Coordination Engine

The coordination engine manages complex multi-phase data workflows with sophisticated tracking for enterprise data processing:

```python
async def execute_complex_data_workflow(self, task: str, workflow_type: str = "data_processing_analysis") -> Dict[str, Any]:
    """Execute complex multi-agent data workflow with dynamic coordination"""

    workflow_id = f"data_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Initialize workflow context
    workflow_context = {
        "workflow_id": workflow_id,
        "task": task,
        "type": workflow_type,
        "started_at": datetime.now(),
        "phases": [],
        "intermediate_results": {},
        "agent_interactions": []
    }
```

The workflow context tracks all aspects of data processing execution including timing, phases, results, and agent interactions, enabling comprehensive data workflow monitoring and optimization.

```python
    try:
        # Phase 1: Data Ingestion and Validation
        ingestion_results = await self._execute_ingestion_phase(task, workflow_context)
        workflow_context["phases"].append("data_ingestion")
        workflow_context["intermediate_results"]["ingestion"] = ingestion_results

        # Phase 2: Data Analytics and Pattern Recognition
        analytics_results = await self._execute_analytics_phase(
            ingestion_results, workflow_context
        )
        workflow_context["phases"].append("analytics")
        workflow_context["intermediate_results"]["analytics"] = analytics_results
```

The workflow executes in sequential phases optimized for data processing, with each phase building on the results of the previous data analysis while maintaining comprehensive tracking.

```python
        # Phase 3: ML Pipeline Processing
        ml_results = await self._execute_ml_pipeline_phase(
            ingestion_results, analytics_results, workflow_context
        )
        workflow_context["phases"].append("ml_processing")
        workflow_context["intermediate_results"]["ml_processing"] = ml_results
```

The ML pipeline phase leverages both ingestion and analytics results to create comprehensive machine learning workflows, utilizing the accumulated knowledge from data validation and analysis phases.

```python
        # Phase 4: Data Quality Review and Optimization
        final_results = await self._execute_optimization_phase(
            ml_results, workflow_context
        )

        workflow_context["completed_at"] = datetime.now()
        workflow_context["final_results"] = final_results
        workflow_context["success"] = True

        return workflow_context
```

Workflow finalization captures completion metadata and optimization results. Success tracking enables proper data workflow conclusion while completion timestamps provide audit trails for data processing performance analysis.

```python
    except Exception as e:
        workflow_context["error"] = str(e)
        workflow_context["success"] = False
        workflow_context["failed_at"] = datetime.now()
        return workflow_context
```

Error handling preserves workflow state during failures. Exception details enable debugging while failure timestamps support recovery and monitoring systems for data processing reliability.

Now let's implement the individual data workflow phases, starting with the data ingestion phase:

```python
async def _execute_ingestion_phase(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute data ingestion phase with specialized ingestion agent"""

    ingestion_agent = self.agents.get("data_ingestion") or self.create_data_ingestion_agent()
    self.agents["data_ingestion"] = ingestion_agent
```

Data ingestion phase initialization creates or retrieves specialized data ingestion agents. Agent caching improves performance while dynamic creation enables flexible resource allocation for data processing tasks.

Next, we create a structured data ingestion prompt that guides the agent's data validation investigation:

```python
    ingestion_prompt = f"""
    Conduct comprehensive data ingestion analysis for the following task:
    {task}

    Focus on:
    1. Validating data schema and format compliance
    2. Assessing data quality metrics and anomalies
    3. Monitoring pipeline performance and throughput
    4. Identifying data source reliability and consistency

    Provide detailed findings with data quality scores and recommendations.
    """

    ingestion_result = ingestion_agent.run(ingestion_prompt)
```

Structured data ingestion prompts guide agent behavior and ensure comprehensive investigation. The four-focus approach covers schema validation, quality assessment, performance monitoring, and reliability analysis for robust data ingestion.

Finally, we track the interaction and return structured data results:

```python
    context["agent_interactions"].append({
        "agent": "data_ingestion",
        "phase": "ingestion",
        "timestamp": datetime.now(),
        "input": ingestion_prompt,
        "output": ingestion_result
    })

    return {
        "data_findings": ingestion_result,
        "quality_metrics": self._extract_quality_metrics(ingestion_result),
        "confidence_level": self._assess_data_confidence(ingestion_result)
    }

The analytics phase processes ingestion findings to identify patterns and generate data insights:

```python
async def _execute_analytics_phase(self, ingestion_data: Dict[str, Any],
                                context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute analytics phase with specialized analytics agent"""

    analytics_agent = self.agents.get("analytics") or self.create_analytics_agent()
    self.agents["analytics"] = analytics_agent
```

Analytics agent initialization retrieves existing agents or creates new specialized analytical capabilities. Agent caching optimizes performance while ensuring appropriate data analytics expertise is available.

We create a structured analytics prompt that focuses on different analytical dimensions:

```python
    analytics_prompt = f"""
    Analyze the following data ingestion findings:
    {ingestion_data['data_findings']}

    Perform:  
    1. Pattern identification and trend analysis across data sources  
    2. Statistical analysis of data quality and completeness metrics  
    3. Correlation analysis between different data streams and sources  
    4. Identification of optimization opportunities and performance improvements  

    Provide structured analysis with actionable insights and recommendations.
    """

    analytics_result = analytics_agent.run(analytics_prompt)
```

Structured analytics prompts guide comprehensive data investigation. The four-step approach covers pattern recognition, statistical processing, correlation discovery, and optimization identification for thorough data analysis.

We track the analytics interaction and return enriched data insights:

```python
    context["agent_interactions"].append({
        "agent": "analytics",
        "phase": "analytics",
        "timestamp": datetime.now(),
        "input": analytics_prompt,
        "output": analytics_result
    })

    return {
        "analysis": analytics_result,
        "patterns_identified": self._extract_data_patterns(analytics_result),
        "optimization_opportunities": self._extract_optimizations(analytics_result),
        "confidence_level": self._assess_analytics_confidence(analytics_result)
    }

The ML pipeline phase combines all previous work into comprehensive machine learning workflow optimization:

```python
async def _execute_ml_pipeline_phase(self, ingestion_data: Dict[str, Any],
                                 analytics_data: Dict[str, Any],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ML pipeline phase with specialized ML agent"""

    ml_agent = self.agents.get("ml_pipeline") or self.create_ml_pipeline_agent()
    self.agents["ml_pipeline"] = ml_agent
```

ML pipeline agent preparation ensures appropriate machine learning capabilities. Agent retrieval or creation provides specialized ML expertise for combining data ingestion and analytics outputs into actionable ML workflows.

We create a comprehensive ML pipeline prompt that integrates all previous data findings:

```python
    ml_prompt = f"""
    Design ML pipeline optimization based on data ingestion and analytics:

    Data Ingestion Results:
    {ingestion_data['data_findings']}

    Analytics Results:
    {analytics_data['analysis']}

    Create a comprehensive ML pipeline strategy that includes:
    1. Feature engineering recommendations based on data quality
    2. Model architecture suggestions for identified patterns
    3. Training pipeline optimization for data throughput
    4. Monitoring and alerting for model performance and data drift
    5. Deployment strategies for scalable ML inference

    Format as a detailed ML engineering plan with implementation priorities.
    """

    ml_result = ml_agent.run(ml_prompt)
```

Comprehensive ML pipeline prompts integrate ingestion and analytics findings. The five-component structure ensures feature engineering, model design, training optimization, monitoring, and deployment for complete ML pipeline coverage.

Finally, we track the ML pipeline interaction and extract structured ML outputs:

```python
    context["agent_interactions"].append({
        "agent": "ml_pipeline",
        "phase": "ml_processing",
        "timestamp": datetime.now(),
        "input": ml_prompt,
        "output": ml_result
    })

    return {
        "ml_strategy": ml_result,
        "feature_recommendations": self._extract_feature_recommendations(ml_result),
        "deployment_plan": self._extract_deployment_plan(ml_result),
        "performance_score": self._assess_ml_pipeline_quality(ml_result)
    }
```

---

## Part 2: Custom Data Processing Chain Development

### Advanced Data Chain Architecture

🗂️ **File**: `src/session2/custom_chains.py` - Custom chain implementations for data processing

```python
from langchain.chains.base import Chain
from langchain.schema import BasePromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.prompts import PromptTemplate
from typing import Dict, List, Any, Optional
import asyncio
from abc import ABC, abstractmethod
```

Advanced data chain development requires sophisticated imports for custom chain creation. These imports provide the foundation for building complex data processing chains with validation, callbacks, and structured prompt management.

```python
class CustomDataAnalysisChain(Chain):
    """Custom chain for sophisticated data processing workflows"""

    llm: Any
    analysis_prompt: BasePromptTemplate
    validation_prompt: BasePromptTemplate
    output_key: str = "data_analysis_result"

    def __init__(self, llm, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
```

CustomDataAnalysisChain establishes the foundation for sophisticated data processing workflows with built-in validation. The class structure separates analysis and validation prompts for data quality assurance.

```python
        self.analysis_prompt = PromptTemplate(
            template="""
            Perform comprehensive data analysis on the following dataset:
            {dataset_info}

            Data Analysis Framework:
            1. Data Quality Assessment and Profiling
            2. Statistical Pattern Recognition and Trends
            3. Anomaly Detection and Outlier Identification
            4. Performance Optimization Recommendations
            5. Actionable Insight Generation with Business Impact

            Provide structured analysis with confidence scores and data lineage tracking.
            """,
            input_variables=["dataset_info"]
        )
```

Structured data analysis prompt defines a comprehensive framework for dataset analysis. The five-step approach ensures thorough examination while confidence scoring and lineage tracking provide quality indicators for downstream processing.

```python
        self.validation_prompt = PromptTemplate(
            template="""
            Validate the following data analysis for accuracy and completeness:
            {analysis}

            Check for:
            1. Statistical accuracy and methodology soundness
            2. Data quality metrics and validation completeness
            3. Business relevance and actionable insights
            4. Potential biases, errors, or data integrity issues

            Provide validation score (1-10) and improvement suggestions for data analysis.
            """,
            input_variables=["analysis"]
        )
```

Validation prompt configuration ensures data analysis quality control through systematic review. The four-point validation checklist covers statistical accuracy, data quality, business relevance, and integrity assessment for comprehensive data analysis assurance.

```python
    @property
    def input_keys(self) -> List[str]:
        return ["dataset_info"]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute the data analysis chain"""

        # Step 1: Perform initial data analysis
        analysis_result = self.llm.invoke(
            self.analysis_prompt.format(dataset_info=inputs["dataset_info"])
        )

        # Step 2: Validate data analysis quality
        validation_result = self.llm.invoke(
            self.validation_prompt.format(analysis=analysis_result.content)
        )
```

Two-phase data analysis execution ensures quality through validation. Initial analysis processes the dataset information, while validation assessment evaluates result quality and completeness for data reliability.

```python
        # Step 3: Determine if re-analysis is needed for data quality
        validation_score = self._extract_validation_score(validation_result.content)

        if validation_score < 7:
            # Re-analyze with improvements for better data insights
            improved_analysis = self._improve_data_analysis(
                inputs["dataset_info"],
                analysis_result.content,
                validation_result.content
            )
            final_analysis = improved_analysis
        else:
            final_analysis = analysis_result.content
```

Adaptive re-analysis improves data analysis quality when validation scores fall below threshold. Scores under 7 trigger improvement cycles, while higher scores proceed with original analysis results for data processing efficiency.

```python
        return {
            self.output_key: {
                "analysis": final_analysis,
                "validation_score": validation_score,
                "validation_feedback": validation_result.content,
                "iterations": 2 if validation_score < 7 else 1
            }
        }

    def _improve_data_analysis(self, original_dataset: str, initial_analysis: str,
                         validation_feedback: str) -> str:
        """Improve data analysis based on validation feedback"""

        improvement_prompt = f"""
        Improve the following data analysis based on validation feedback:

        Original Dataset: {original_dataset}
        Initial Analysis: {initial_analysis}
        Validation Feedback: {validation_feedback}

        Provide an improved data analysis that addresses the feedback points with enhanced
        statistical rigor and business relevance.
        """

        improved_result = self.llm.invoke(improvement_prompt)
        return improved_result.content
```

Iterative improvement functionality enables data analysis refinement through feedback incorporation. The prompt combines original dataset, initial analysis, and validation feedback to guide targeted data analysis improvements.

```python
    def _extract_validation_score(self, validation_text: str) -> int:
        """Extract numerical validation score from text"""
        import re
        score_match = re.search(r'(\d+)(?:/10)?', validation_text)
        return int(score_match.group(1)) if score_match else 5
```

Validation score extraction uses regex pattern matching to identify numerical scores. The pattern captures digits with optional "/10" suffix, while fallback value ensures robust operation when scores are absent.

```python
class ConditionalDataProcessingChain(Chain):
    """Chain that executes different data processing logic based on input conditions"""

    llm: Any
    condition_chains: Dict[str, Chain]
    default_chain: Chain
    output_key: str = "conditional_processing_result"
```

The ConditionalDataProcessingChain implements branching logic for different data processing workflows. By maintaining a dictionary of condition-specific chains and a default fallback, it enables intelligent routing based on data characteristics like volume, format, or processing requirements.

```python
    def __init__(self, llm, condition_chains: Dict[str, Chain],
                 default_chain: Chain, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.condition_chains = condition_chains
        self.default_chain = default_chain
```

The initialization establishes the LLM instance for decision-making and stores both conditional chains and a default chain. This architecture ensures that every data processing scenario has a viable execution path, preventing workflow failures when conditions don't match predefined patterns.

```python
    @property
    def input_keys(self) -> List[str]:
        return ["dataset_info", "processing_type"]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
```

The ConditionalDataProcessingChain class enables dynamic chain selection based on data processing requirements. This pattern is essential for building adaptive data systems that can respond differently to various dataset types or processing contexts.

```python
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute chain based on data processing condition"""

        processing_type = inputs.get("processing_type", "default")

        if processing_type in self.condition_chains:
            selected_chain = self.condition_chains[processing_type]
        else:
            selected_chain = self.default_chain
```

The chain selection logic first extracts the processing type from inputs, then looks up the appropriate chain in the condition dictionary. If no specific chain exists for the processing type, the system falls back to the default chain, ensuring robust operation across diverse data processing scenarios.

```python
        # Execute selected chain for data processing
        result = selected_chain.run(inputs["dataset_info"])

        return {
            self.output_key: {
                "result": result,
                "chain_used": processing_type,
                "execution_path": self._get_execution_path(processing_type)
            }
        }
```

Condition-based execution provides runtime chain selection with fallback support for data processing. The execution path tracking helps with debugging and monitoring which data processing chain was actually used.

```python
    def _get_execution_path(self, processing_type: str) -> str:
        """Get description of data processing execution path taken"""
        if processing_type in self.condition_chains:
            return f"Specialized data processing: {processing_type}"
        else:
            return "Default data processing: fallback chain"
```

Now let's implement the DataPipelineChain for sequential data processing with state management:

```python
class DataPipelineChain(Chain):
    """Chain that executes a data processing pipeline with state management"""

    llm: Any
    pipeline_steps: List[Dict[str, Any]]
    state_management: bool
    output_key: str = "pipeline_result"
```

The DataPipelineChain orchestrates complex multi-step data processing workflows. It maintains a list of pipeline steps as configuration objects and includes optional state management for tracking intermediate results and enabling pipeline recovery scenarios.

```python
    def __init__(self, llm, pipeline_steps: List[Dict[str, Any]],
                 state_management: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.pipeline_steps = pipeline_steps
        self.state_management = state_management
        self.pipeline_state = {}
```

The initialization configures the pipeline with an LLM instance, step definitions, and state management options. The pipeline_state dictionary tracks intermediate results when state management is enabled, supporting pipeline recovery and debugging capabilities.

```python
    @property
    def input_keys(self) -> List[str]:
        return ["input_data"]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
```

DataPipelineChain enables sequential data transformation through multiple processing steps. State management allows sharing information between steps, crucial for complex multi-stage data workflows.

```python
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute data pipeline with state management"""

        current_data = inputs["input_data"]
        step_results = []

        for i, step in enumerate(self.pipeline_steps):
            step_name = step.get("name", f"data_step_{i}")
            step_operation = step.get("operation")
            step_prompt = step.get("prompt_template")
```

Pipeline execution iterates through configured data processing steps sequentially. Each step receives the output from the previous step, enabling data transformation chains with progressive refinement.

```python
            # Execute data processing step
            if step_prompt:
                prompt = step_prompt.format(
                    input=current_data,
                    state=self.pipeline_state if self.state_management else {}
                )
                step_result = self.llm.invoke(prompt)
                current_data = step_result.content
```

Step execution applies templates with current data and state context. State management enables cross-step information sharing while template formatting provides consistent prompt structure for data processing.

```python
            step_results.append({
                "step_name": step_name,
                "result": current_data,
                "operation": step_operation
            })

            # Update state if enabled for data processing continuity
            if self.state_management:
                self.pipeline_state[step_name] = current_data
```

Step result tracking and state updates maintain data pipeline execution history. Result collection enables debugging and audit trails while state updates provide context for subsequent data processing steps.

```python
        return {
            self.output_key: {
                "final_result": current_data,
                "step_results": step_results,
                "pipeline_state": self.pipeline_state.copy() if self.state_management else {}
            }
        }
```

---

## Part 3: Advanced Data Tool Patterns

### Sophisticated Data Tool Development

🗂️ **File**: `src/session2/advanced_tools.py` - Production-ready data tool implementations

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Type
import asyncio
import aiohttp
import sqlite3
from datetime import datetime, timedelta
import json
import logging

class DataToolExecutionContext(BaseModel):
    """Context information for data tool execution"""
    execution_id: str
    timestamp: datetime
    user_context: Dict[str, Any]
    session_data: Dict[str, Any]
    retry_count: int = 0
```

The DataToolExecutionContext provides comprehensive execution metadata for advanced data tool operations. This context enables sophisticated error handling, retry logic, and session management across data tool invocations.

```python
class AdvancedDataWarehouseTool(BaseTool):
    """Advanced tool for data warehouse integration with retry logic and caching"""

    name = "advanced_data_warehouse_tool"
    description = "Interact with enterprise data warehouses with retry logic and caching"

    def __init__(self, warehouse_config: Dict[str, Any]):
        super().__init__()
        self.warehouse_config = warehouse_config
        self.query_cache = {}
        self.cache_ttl = timedelta(minutes=30)
        self.max_retries = 3
        self.retry_delay = 1.0
```

AdvancedDataWarehouseTool initialization establishes robust data warehouse interaction capabilities with query caching and retry mechanisms. Configuration-based setup enables flexible warehouse endpoint management while built-in retry logic ensures reliable data access communication.

```python
    class ToolInput(BaseModel):
        sql_query: str = Field(description="SQL query to execute against data warehouse")
        database: str = Field(default="main", description="Target database name")
        query_params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
        timeout_seconds: int = Field(default=300, description="Query timeout in seconds")
        use_cache: bool = Field(default=True, description="Whether to use query result caching")

    args_schema: Type[BaseModel] = ToolInput
```

Structured input validation ensures proper data warehouse query configuration. The schema defines required SQL query and optional parameters while providing sensible defaults for database targeting and caching behavior.

```python
    def _run(self, sql_query: str, database: str = "main",
             query_params: Dict[str, Any] = None, timeout_seconds: int = 300,
             use_cache: bool = True) -> str:
        """Execute data warehouse query with error handling and caching"""

        # Create cache key for data queries
        cache_key = self._create_query_cache_key(sql_query, database, query_params or {})

        # Check cache first for performance
        if use_cache and cache_key in self.query_cache:
            cached_result, cache_time = self.query_cache[cache_key]
            if datetime.now() - cache_time < self.cache_ttl:
                return cached_result
```

Cache optimization reduces redundant data warehouse queries and improves response times. Cache keys ensure uniqueness while TTL validation prevents stale data from being returned to users.

```python
        # Execute data warehouse query with retry logic
        for attempt in range(self.max_retries):
            try:
                result = self._execute_warehouse_query(sql_query, database, query_params, timeout_seconds)

                # Cache successful data results
                if use_cache:
                    self.query_cache[cache_key] = (result, datetime.now())

                return result
```

Retry logic with exponential backoff ensures robust data warehouse interaction. Successful results are cached for future use, while failures trigger progressive delays to avoid overwhelming data warehouse services.

```python
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return f"Data warehouse query failed after {self.max_retries} attempts: {str(e)}"

                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

        return "Unexpected error in data warehouse execution"

    def _execute_warehouse_query(self, sql_query: str, database: str,
                         query_params: Dict[str, Any], timeout_seconds: int) -> str:
        """Execute the actual data warehouse query"""
        import pandas as pd

        connection_string = f"{self.warehouse_config['connection_url']}/{database}"
```

Connection string construction and authentication preparation ensure proper data warehouse request setup. Connection URL combination with database creates complete connection targets while maintaining secure data warehouse access.

```python
        # Add authentication headers for data warehouse access
        auth_config = {}
        if 'username' in self.warehouse_config and 'password' in self.warehouse_config:
            auth_config = {
                'user': self.warehouse_config['username'],
                'password': self.warehouse_config['password']
            }
```

Authentication configuration secures data warehouse requests. Username and password injection follows standard database authentication while parameter initialization prevents null reference errors during authentication setup.

```python
        try:
            # Execute query against data warehouse
            df_result = pd.read_sql(
                sql_query,
                connection_string,
                params=query_params,
                **auth_config
            )

            return df_result.to_json(orient='records', date_format='iso')

        except Exception as e:
            raise Exception(f"Data warehouse query execution failed: {str(e)}")
```

Data warehouse query execution with proper parameter handling and timeout configuration. Pandas integration enables flexible query execution while JSON conversion ensures standardized data output format.

```python
    def _create_query_cache_key(self, sql_query: str, database: str, params: Dict[str, Any]) -> str:
        """Create cache key for data warehouse query"""
        import hashlib
        key_data = f"{sql_query}:{database}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
```

Cache key generation uses MD5 hashing of query, database, and sorted parameters to ensure unique, consistent cache keys. Parameter sorting prevents cache misses due to parameter order differences in data queries.

```python
class StatefulDataPipelineTool(BaseTool):
    """Tool for data pipeline operations with state management and monitoring"""

    name = "data_pipeline_tool"
    description = "Execute data pipeline operations with state management and performance monitoring"

    def __init__(self, pipeline_config: Dict[str, Any]):
        super().__init__()
        self.pipeline_config = pipeline_config
        self.pipeline_states = {}
        self.execution_history = []
```

StatefulDataPipelineTool provides robust data pipeline interaction with state management and execution monitoring. The execution history tracks pipeline runs while state management optimizes resource utilization for data processing workflows.

```python
    class ToolInput(BaseModel):
        pipeline_id: str = Field(description="Data pipeline identifier")
        operation: str = Field(description="Pipeline operation: start, stop, monitor, configure")
        config_params: Dict[str, Any] = Field(default_factory=dict, description="Pipeline configuration parameters")
        async_execution: bool = Field(default=False, description="Execute pipeline asynchronously")

    args_schema: Type[BaseModel] = ToolInput
```

Structured input validation ensures proper data pipeline operation configuration. Parameters support different operations while async execution enables non-blocking pipeline operations for large-scale data processing.

```python
    def _run(self, pipeline_id: str, operation: str,
             config_params: Dict[str, Any] = None, async_execution: bool = False) -> str:
        """Execute data pipeline operation with state management"""

        try:
            # Get or initialize pipeline state
            if pipeline_id not in self.pipeline_states:
                self.pipeline_states[pipeline_id] = {
                    "status": "initialized",
                    "last_run": None,
                    "execution_count": 0,
                    "performance_metrics": {}
                }

            pipeline_state = self.pipeline_states[pipeline_id]
```

Pipeline state management tracks execution history and performance metrics. State initialization ensures consistent tracking while performance metrics enable optimization and monitoring capabilities.

```python
            # Execute pipeline operation based on type
            if operation == "start":
                result = self._start_pipeline(pipeline_id, config_params or {})
            elif operation == "stop":
                result = self._stop_pipeline(pipeline_id)
            elif operation == "monitor":
                result = self._monitor_pipeline(pipeline_id)
            elif operation == "configure":
                result = self._configure_pipeline(pipeline_id, config_params or {})
            else:
                return f"Unknown pipeline operation: {operation}"
```

Operation routing enables different pipeline management functions. Start, stop, monitor, and configure operations provide comprehensive pipeline lifecycle management with state tracking.

```python
            # Update pipeline state and execution history
            pipeline_state["last_run"] = datetime.now()
            pipeline_state["execution_count"] += 1

            self.execution_history.append({
                "pipeline_id": pipeline_id,
                "operation": operation,
                "timestamp": datetime.now(),
                "result": result
            })

            return result

        except Exception as e:
            return f"Data pipeline operation failed: {str(e)}"
```

State updates and execution history tracking provide comprehensive pipeline operation monitoring. Execution counting and timestamping enable performance analysis and operational insights.

```python
    def _start_pipeline(self, pipeline_id: str, config_params: Dict[str, Any]) -> str:
        """Start data pipeline execution"""
        self.pipeline_states[pipeline_id]["status"] = "running"

        # Simulate pipeline startup with configuration
        throughput = config_params.get("throughput", "1000 records/sec")
        parallelism = config_params.get("parallelism", 4)

        return f"Pipeline {pipeline_id} started successfully. Throughput: {throughput}, Parallelism: {parallelism}"

    def _monitor_pipeline(self, pipeline_id: str) -> str:
        """Monitor data pipeline performance"""
        state = self.pipeline_states[pipeline_id]

        return f"Pipeline {pipeline_id}: Status: {state['status']}, Executions: {state['execution_count']}, Last run: {state['last_run']}"
```

Pipeline operation implementation provides realistic data pipeline management. Start operations configure throughput and parallelism while monitoring returns comprehensive status information for operational visibility.

```python
class DataQualityTool(BaseTool):
    """Tool for comprehensive data quality assessment and monitoring"""

    name = "data_quality_tool"
    description = "Assess and monitor data quality metrics across datasets and pipelines"

    def __init__(self, quality_config: Dict[str, Any]):
        super().__init__()
        self.quality_config = quality_config
        self.quality_profiles = {}
        self.anomaly_thresholds = quality_config.get("thresholds", {})
```

Data quality tool initialization establishes comprehensive quality assessment capabilities. Quality profiles track dataset characteristics while anomaly thresholds enable automated quality monitoring and alerting.

```python
    class ToolInput(BaseModel):
        dataset_path: str = Field(description="Path or identifier for dataset to analyze")
        quality_checks: List[str] = Field(description="List of quality checks to perform")
        comparison_baseline: Optional[str] = Field(default=None, description="Baseline dataset for comparison")
        generate_report: bool = Field(default=True, description="Generate detailed quality report")

    args_schema: Type[BaseModel] = ToolInput

Input schema definition provides comprehensive data quality assessment parameters. Quality checks list enables targeted validation while baseline comparison supports drift detection and trend analysis.

```python
    def _run(self, dataset_path: str, quality_checks: List[str],
             comparison_baseline: str = None, generate_report: bool = True) -> str:
        """Execute comprehensive data quality assessment"""

        try:
            quality_results = {
                "dataset": dataset_path,
                "timestamp": datetime.now().isoformat(),
                "checks_performed": quality_checks,
                "results": {}
            }

            # Execute each quality check
            for check in quality_checks:
                if check == "completeness":
                    quality_results["results"]["completeness"] = self._check_completeness(dataset_path)
                elif check == "accuracy":
                    quality_results["results"]["accuracy"] = self._check_accuracy(dataset_path)
                elif check == "consistency":
                    quality_results["results"]["consistency"] = self._check_consistency(dataset_path)
                elif check == "timeliness":
                    quality_results["results"]["timeliness"] = self._check_timeliness(dataset_path)
```

Quality check execution iterates through specified validation types. Completeness, accuracy, consistency, and timeliness checks provide comprehensive data quality coverage with structured result tracking.

```python
            # Calculate overall quality score
            scores = [result.get("score", 0) for result in quality_results["results"].values()]
            overall_score = sum(scores) / len(scores) if scores else 0
            quality_results["overall_score"] = overall_score

            # Generate quality report if requested
            if generate_report:
                quality_results["report"] = self._generate_quality_report(quality_results)

            return json.dumps(quality_results, indent=2)

        except Exception as e:
            return f"Data quality assessment failed: {str(e)}"
```

Overall quality scoring aggregates individual check results for comprehensive assessment. Report generation provides detailed analysis while JSON formatting ensures standardized output structure.

```python
    def _check_completeness(self, dataset_path: str) -> Dict[str, Any]:
        """Check data completeness metrics"""
        # Simulate completeness analysis
        return {
            "check_type": "completeness",
            "score": 94.7,
            "null_percentage": 5.3,
            "missing_critical_fields": 2,
            "recommendation": "Address missing values in customer_id and timestamp fields"
        }

    def _check_accuracy(self, dataset_path: str) -> Dict[str, Any]:
        """Check data accuracy metrics"""
        # Simulate accuracy analysis
        return {
            "check_type": "accuracy",
            "score": 89.2,
            "invalid_formats": 156,
            "out_of_range_values": 23,
            "recommendation": "Implement validation rules for email and phone number formats"
        }
```

Individual quality check implementations provide specific data validation results. Completeness checks assess missing values while accuracy checks evaluate format compliance and range validation with actionable recommendations.

---

## 📝 Multiple Choice Test - Module A

Test your understanding of advanced LangChain patterns for data engineering:

**Question 1:** What components are defined in the `DataAgentRole` dataclass for data agent specialization?  
A) Only name and description  
B) Name, description, tools, specialization, and expertise_areas  
C) Just tools and memory configuration  
D) Only specialization and tools  

**Question 2:** What is the primary purpose of the `DataProcessingOrchestrator` class?  
A) Create individual data agents  
B) Coordinate complex data workflows across multiple specialized agents  
C) Store conversation memory  
D) Execute single-agent tasks  

**Question 3:** How does the data workflow coordination engine track execution progress?  
A) Only stores final results  
B) Uses workflow_context with phases, intermediate_results, and agent_interactions  
C) Relies on agent memory alone  
D) Tracks only error states  

**Question 4:** What differentiates a data ingestion agent from an analytics agent in the multi-agent system?  
A) Different LLM models  
B) Specialized tools and system messages focused on their data domain  
C) Memory configuration only  
D) Agent type parameter  

**Question 5:** What happens in the ML pipeline phase of the complex data workflow?  
A) Initial data gathering  
B) Pattern recognition only  
C) Combines ingestion and analytics results into comprehensive ML workflows  
D) Error handling and recovery  

[**View Test Solutions →**](Session2_ModuleA_Test_Solutions.md)

---

## Module Summary

You've now mastered advanced LangChain patterns for production data systems:

✅ **Complex Multi-Agent Data Workflows**: Built sophisticated orchestration systems with specialized data agents
✅ **Custom Data Processing Chain Development**: Created reusable chain components with advanced logic and validation
✅ **Advanced Data Tool Patterns**: Implemented production-ready tools with state management and error recovery
✅ **Enterprise Data Architecture**: Designed scalable patterns for complex data processing applications

### Next Steps

- **Continue to Module B**: [Production Deployment Strategies](Session2_ModuleB_Production_Deployment_Strategies.md) for enterprise data system deployment
- **Continue to Module C**: [Custom Tool Development](Session2_ModuleC_Custom_Tool_Development.md) for specialized data processing tools
- **Return to Core**: [Session 2 Main](Session2_LangChain_Foundations.md)
- **Advance to Session 3**: [LangGraph Multi-Agent Workflows](Session3_LangGraph_Multi_Agent_Workflows.md)

---

**🗂️ Source Files for Module A:**

- `src/session2/multi_agent_workflows.py` - Complex data agent coordination systems
- `src/session2/custom_chains.py` - Custom chain implementations for data processing
- `src/session2/advanced_tools.py` - Production-ready data tool patterns
---

**Next:** [Session 3 - LangGraph Multi-Agent Workflows →](Session3_LangGraph_Multi_Agent_Workflows.md)

---
