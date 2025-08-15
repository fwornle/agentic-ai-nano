# Session 2 - Module A: Advanced LangChain Patterns (60 minutes)

**Prerequisites**: [Session 2 Core Section Complete](Session2_LangChain_Foundations.md)  
**Target Audience**: Implementers seeking deeper LangChain understanding  
**Cognitive Load**: 6 advanced concepts

---

## 🎯 Module Overview

This module explores sophisticated LangChain patterns including complex multi-agent workflows, custom chain development, and advanced tool patterns. You'll learn how to build production-ready systems with LangChain's most powerful features.

### Learning Objectives
By the end of this module, you will:
- Build complex multi-agent workflows with specialized agents working together
- Create custom chain classes with advanced logic and reusable components
- Implement sophisticated tools with state management and error recovery
- Design scalable LangChain architectures for enterprise applications

---

## Part 1: Complex Multi-Agent Workflows (20 minutes)

### Advanced Orchestration Patterns

🗂️ **File**: `src/session2/multi_agent_workflows.py` - Complex agent coordination

Multi-agent systems in LangChain require sophisticated coordination patterns where specialized agents collaborate on complex tasks:

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
class AgentRole:
    name: str
    description: str
    tools: List[BaseTool]
    specialization: str
    expertise_areas: List[str]

class MultiAgentOrchestrator:
    """Orchestrates complex workflows across multiple specialized agents"""
    
    def __init__(self, llm):
        self.llm = llm
        self.agents: Dict[str, Any] = {}
        self.workflow_history: List[Dict[str, Any]] = []
        self.shared_memory = ConversationBufferMemory(
            memory_key="shared_context",
            return_messages=True
        )
```

### Specialized Agent Creation

```python
def create_research_agent(self) -> Any:
    """Create agent specialized in research and information gathering"""
    
    research_tools = [
        self._create_web_search_tool(),
        self._create_document_analysis_tool(),
        self._create_fact_checking_tool()
    ]
    
    research_memory = ConversationBufferMemory(
        memory_key="research_history",
        return_messages=True
    )
    
    research_agent = initialize_agent(
        tools=research_tools,
        llm=self.llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=research_memory,
        verbose=True,
        agent_kwargs={
            "system_message": """You are a research specialist focused on gathering 
            accurate, comprehensive information. Your role is to:
            1. Search for relevant information
            2. Analyze documents and sources
            3. Verify facts and cross-reference data
            4. Provide well-sourced, reliable insights"""
        }
    )
    
    return research_agent

def create_analysis_agent(self) -> Any:
    """Create agent specialized in data analysis and pattern recognition"""
    
    analysis_tools = [
        self._create_data_processing_tool(),
        self._create_statistical_analysis_tool(),
        self._create_visualization_tool()
    ]
    
    analysis_memory = ConversationBufferMemory(
        memory_key="analysis_history",
        return_messages=True
    )
    
    analysis_agent = initialize_agent(
        tools=analysis_tools,
        llm=self.llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=analysis_memory,
        verbose=True,
        agent_kwargs={
            "system_message": """You are a data analysis specialist. Your role is to:
            1. Process and clean data
            2. Identify patterns and trends
            3. Perform statistical analysis
            4. Create visualizations and insights"""
        }
    )
    
    return analysis_agent

def create_synthesis_agent(self) -> Any:
    """Create agent specialized in synthesizing information and creating reports"""
    
    synthesis_tools = [
        self._create_document_generation_tool(),
        self._create_summary_tool(),
        self._create_recommendation_tool()
    ]
    
    synthesis_memory = ConversationBufferMemory(
        memory_key="synthesis_history",
        return_messages=True
    )
    
    synthesis_agent = initialize_agent(
        tools=synthesis_tools,
        llm=self.llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=synthesis_memory,
        verbose=True,
        agent_kwargs={
            "system_message": """You are a synthesis specialist. Your role is to:
            1. Combine information from multiple sources
            2. Create comprehensive reports
            3. Generate actionable recommendations
            4. Present findings in clear, structured formats"""
        }
    )
    
    return synthesis_agent
```

### Workflow Coordination Engine

```python
async def execute_complex_workflow(self, task: str, workflow_type: str = "research_analysis") -> Dict[str, Any]:
    """Execute complex multi-agent workflow with dynamic coordination"""
    
    workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
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
    
    try:
        # Phase 1: Research and Information Gathering
        research_results = await self._execute_research_phase(task, workflow_context)
        workflow_context["phases"].append("research")
        workflow_context["intermediate_results"]["research"] = research_results
        
        # Phase 2: Data Analysis and Pattern Recognition
        analysis_results = await self._execute_analysis_phase(
            research_results, workflow_context
        )
        workflow_context["phases"].append("analysis")
        workflow_context["intermediate_results"]["analysis"] = analysis_results
        
        # Phase 3: Synthesis and Report Generation
        synthesis_results = await self._execute_synthesis_phase(
            research_results, analysis_results, workflow_context
        )
        workflow_context["phases"].append("synthesis")
        workflow_context["intermediate_results"]["synthesis"] = synthesis_results
        
        # Phase 4: Quality Review and Finalization
        final_results = await self._execute_review_phase(
            synthesis_results, workflow_context
        )
        
        workflow_context["completed_at"] = datetime.now()
        workflow_context["final_results"] = final_results
        workflow_context["success"] = True
        
        return workflow_context
        
    except Exception as e:
        workflow_context["error"] = str(e)
        workflow_context["success"] = False
        workflow_context["failed_at"] = datetime.now()
        return workflow_context

async def _execute_research_phase(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute research phase with specialized research agent"""
    
    research_agent = self.agents.get("research") or self.create_research_agent()
    self.agents["research"] = research_agent
    
    research_prompt = f"""
    Conduct comprehensive research on the following task:
    {task}
    
    Focus on:
    1. Gathering relevant background information
    2. Identifying key data sources
    3. Finding expert opinions and analysis
    4. Collecting statistical data and trends
    
    Provide detailed findings with sources.
    """
    
    research_result = research_agent.run(research_prompt)
    
    context["agent_interactions"].append({
        "agent": "research",
        "phase": "research",
        "timestamp": datetime.now(),
        "input": research_prompt,
        "output": research_result
    })
    
    return {
        "findings": research_result,
        "sources_found": self._extract_sources(research_result),
        "confidence_level": self._assess_research_confidence(research_result)
    }

async def _execute_analysis_phase(self, research_data: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute analysis phase with specialized analysis agent"""
    
    analysis_agent = self.agents.get("analysis") or self.create_analysis_agent()
    self.agents["analysis"] = analysis_agent
    
    analysis_prompt = f"""
    Analyze the following research findings:
    {research_data['findings']}
    
    Perform:
    1. Pattern identification and trend analysis
    2. Statistical analysis of any numerical data
    3. Correlation analysis between different data points
    4. Identification of key insights and implications
    
    Provide structured analysis with supporting evidence.
    """
    
    analysis_result = analysis_agent.run(analysis_prompt)
    
    context["agent_interactions"].append({
        "agent": "analysis",
        "phase": "analysis",
        "timestamp": datetime.now(),
        "input": analysis_prompt,
        "output": analysis_result
    })
    
    return {
        "analysis": analysis_result,
        "patterns_identified": self._extract_patterns(analysis_result),
        "statistical_insights": self._extract_statistics(analysis_result),
        "confidence_level": self._assess_analysis_confidence(analysis_result)
    }

async def _execute_synthesis_phase(self, research_data: Dict[str, Any], 
                                 analysis_data: Dict[str, Any],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute synthesis phase with specialized synthesis agent"""
    
    synthesis_agent = self.agents.get("synthesis") or self.create_synthesis_agent()
    self.agents["synthesis"] = synthesis_agent
    
    synthesis_prompt = f"""
    Synthesize the following research and analysis:
    
    Research Findings:
    {research_data['findings']}
    
    Analysis Results:
    {analysis_data['analysis']}
    
    Create a comprehensive report that includes:
    1. Executive summary
    2. Key findings and insights
    3. Actionable recommendations
    4. Supporting evidence and data
    5. Potential risks and limitations
    
    Format as a professional report.
    """
    
    synthesis_result = synthesis_agent.run(synthesis_prompt)
    
    context["agent_interactions"].append({
        "agent": "synthesis",
        "phase": "synthesis",
        "timestamp": datetime.now(),
        "input": synthesis_prompt,
        "output": synthesis_result
    })
    
    return {
        "report": synthesis_result,
        "recommendations": self._extract_recommendations(synthesis_result),
        "action_items": self._extract_action_items(synthesis_result),
        "quality_score": self._assess_report_quality(synthesis_result)
    }
```

---

## Part 2: Custom Chain Development (20 minutes)

### Advanced Chain Architecture

🗂️ **File**: `src/session2/custom_chains.py` - Custom chain implementations

```python
from langchain.chains.base import Chain
from langchain.schema import BasePromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.prompts import PromptTemplate
from typing import Dict, List, Any, Optional
import asyncio
from abc import ABC, abstractmethod

class CustomAnalysisChain(Chain):
    """Custom chain for sophisticated analysis workflows"""
    
    llm: Any
    analysis_prompt: BasePromptTemplate
    validation_prompt: BasePromptTemplate
    output_key: str = "analysis_result"
    
    def __init__(self, llm, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.analysis_prompt = PromptTemplate(
            template="""
            Perform detailed analysis on the following data:
            {input_data}
            
            Analysis Framework:
            1. Data Quality Assessment
            2. Pattern Recognition
            3. Trend Analysis
            4. Anomaly Detection
            5. Insight Generation
            
            Provide structured analysis with confidence scores.
            """,
            input_variables=["input_data"]
        )
        
        self.validation_prompt = PromptTemplate(
            template="""
            Validate the following analysis for accuracy and completeness:
            {analysis}
            
            Check for:
            1. Logical consistency
            2. Evidence support
            3. Completeness of analysis
            4. Potential biases or errors
            
            Provide validation score (1-10) and improvement suggestions.
            """,
            input_variables=["analysis"]
        )
    
    @property
    def input_keys(self) -> List[str]:
        return ["input_data"]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute the analysis chain"""
        
        # Step 1: Perform initial analysis
        analysis_result = self.llm.invoke(
            self.analysis_prompt.format(input_data=inputs["input_data"])
        )
        
        # Step 2: Validate analysis quality
        validation_result = self.llm.invoke(
            self.validation_prompt.format(analysis=analysis_result.content)
        )
        
        # Step 3: Determine if re-analysis is needed
        validation_score = self._extract_validation_score(validation_result.content)
        
        if validation_score < 7:
            # Re-analyze with improvements
            improved_analysis = self._improve_analysis(
                inputs["input_data"], 
                analysis_result.content,
                validation_result.content
            )
            final_analysis = improved_analysis
        else:
            final_analysis = analysis_result.content
        
        return {
            self.output_key: {
                "analysis": final_analysis,
                "validation_score": validation_score,
                "validation_feedback": validation_result.content,
                "iterations": 2 if validation_score < 7 else 1
            }
        }
    
    def _improve_analysis(self, original_data: str, initial_analysis: str, 
                         validation_feedback: str) -> str:
        """Improve analysis based on validation feedback"""
        
        improvement_prompt = f"""
        Improve the following analysis based on validation feedback:
        
        Original Data: {original_data}
        Initial Analysis: {initial_analysis}
        Validation Feedback: {validation_feedback}
        
        Provide an improved analysis that addresses the feedback points.
        """
        
        improved_result = self.llm.invoke(improvement_prompt)
        return improved_result.content
    
    def _extract_validation_score(self, validation_text: str) -> int:
        """Extract numerical validation score from text"""
        import re
        score_match = re.search(r'(\d+)(?:/10)?', validation_text)
        return int(score_match.group(1)) if score_match else 5

class ConditionalChain(Chain):
    """Chain that executes different logic based on input conditions"""
    
    llm: Any
    condition_chains: Dict[str, Chain]
    default_chain: Chain
    output_key: str = "conditional_result"
    
    def __init__(self, llm, condition_chains: Dict[str, Chain], 
                 default_chain: Chain, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.condition_chains = condition_chains
        self.default_chain = default_chain
    
    @property
    def input_keys(self) -> List[str]:
        return ["input_data", "condition_type"]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute chain based on condition"""
        
        condition_type = inputs.get("condition_type", "default")
        
        if condition_type in self.condition_chains:
            selected_chain = self.condition_chains[condition_type]
        else:
            selected_chain = self.default_chain
        
        # Execute selected chain
        result = selected_chain.run(inputs["input_data"])
        
        return {
            self.output_key: {
                "result": result,
                "chain_used": condition_type,
                "execution_path": self._get_execution_path(condition_type)
            }
        }
    
    def _get_execution_path(self, condition_type: str) -> str:
        """Get description of execution path taken"""
        if condition_type in self.condition_chains:
            return f"Conditional path: {condition_type}"
        else:
            return "Default path: fallback chain"

class PipelineChain(Chain):
    """Chain that executes a pipeline of operations with state management"""
    
    llm: Any
    pipeline_steps: List[Dict[str, Any]]
    state_management: bool
    output_key: str = "pipeline_result"
    
    def __init__(self, llm, pipeline_steps: List[Dict[str, Any]], 
                 state_management: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.pipeline_steps = pipeline_steps
        self.state_management = state_management
        self.pipeline_state = {}
    
    @property
    def input_keys(self) -> List[str]:
        return ["input_data"]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute pipeline with state management"""
        
        current_data = inputs["input_data"]
        step_results = []
        
        for i, step in enumerate(self.pipeline_steps):
            step_name = step.get("name", f"step_{i}")
            step_operation = step.get("operation")
            step_prompt = step.get("prompt_template")
            
            # Execute step
            if step_prompt:
                prompt = step_prompt.format(
                    input=current_data,
                    state=self.pipeline_state if self.state_management else {}
                )
                step_result = self.llm.invoke(prompt)
                current_data = step_result.content
            
            step_results.append({
                "step_name": step_name,
                "result": current_data,
                "operation": step_operation
            })
            
            # Update state if enabled
            if self.state_management:
                self.pipeline_state[step_name] = current_data
        
        return {
            self.output_key: {
                "final_result": current_data,
                "step_results": step_results,
                "pipeline_state": self.pipeline_state.copy() if self.state_management else {}
            }
        }
```

---

## Part 3: Advanced Tool Patterns (20 minutes)

### Sophisticated Tool Development

🗂️ **File**: `src/session2/advanced_tools.py` - Production-ready tool implementations

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

class ToolExecutionContext(BaseModel):
    """Context information for tool execution"""
    execution_id: str
    timestamp: datetime
    user_context: Dict[str, Any]
    session_data: Dict[str, Any]
    retry_count: int = 0

class AdvancedAPITool(BaseTool):
    """Advanced tool for API integration with retry logic and caching"""
    
    name = "advanced_api_tool"
    description = "Interact with external APIs with retry logic and caching"
    
    def __init__(self, api_config: Dict[str, Any]):
        super().__init__()
        self.api_config = api_config
        self.cache = {}
        self.cache_ttl = timedelta(minutes=30)
        self.max_retries = 3
        self.retry_delay = 1.0
        
    class ToolInput(BaseModel):
        endpoint: str = Field(description="API endpoint to call")
        method: str = Field(default="GET", description="HTTP method")
        params: Dict[str, Any] = Field(default_factory=dict, description="API parameters")
        headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
        use_cache: bool = Field(default=True, description="Whether to use caching")
    
    args_schema: Type[BaseModel] = ToolInput
    
    def _run(self, endpoint: str, method: str = "GET", 
             params: Dict[str, Any] = None, headers: Dict[str, str] = None,
             use_cache: bool = True) -> str:
        """Execute API call with error handling and caching"""
        
        # Create cache key
        cache_key = self._create_cache_key(endpoint, method, params or {})
        
        # Check cache first
        if use_cache and cache_key in self.cache:
            cached_result, cache_time = self.cache[cache_key]
            if datetime.now() - cache_time < self.cache_ttl:
                return cached_result
        
        # Execute API call with retry logic
        for attempt in range(self.max_retries):
            try:
                result = self._execute_api_call(endpoint, method, params, headers)
                
                # Cache successful result
                if use_cache:
                    self.cache[cache_key] = (result, datetime.now())
                
                return result
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return f"API call failed after {self.max_retries} attempts: {str(e)}"
                
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        return "Unexpected error in API execution"
    
    def _execute_api_call(self, endpoint: str, method: str, 
                         params: Dict[str, Any], headers: Dict[str, str]) -> str:
        """Execute the actual API call"""
        import requests
        
        url = f"{self.api_config['base_url']}/{endpoint}"
        
        # Add authentication headers
        if 'api_key' in self.api_config:
            headers = headers or {}
            headers['Authorization'] = f"Bearer {self.api_config['api_key']}"
        
        response = requests.request(
            method=method,
            url=url,
            params=params if method == "GET" else None,
            json=params if method != "GET" else None,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        return response.text
    
    def _create_cache_key(self, endpoint: str, method: str, params: Dict[str, Any]) -> str:
        """Create cache key for request"""
        import hashlib
        key_data = f"{endpoint}:{method}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

class StatefulDatabaseTool(BaseTool):
    """Tool for database operations with connection management"""
    
    name = "database_tool"
    description = "Execute database queries with connection management and transaction support"
    
    def __init__(self, db_config: Dict[str, Any]):
        super().__init__()
        self.db_config = db_config
        self.connection_pool = {}
        self.transaction_stack = []
        
    class ToolInput(BaseModel):
        query: str = Field(description="SQL query to execute")
        params: List[Any] = Field(default_factory=list, description="Query parameters")
        transaction: bool = Field(default=False, description="Execute in transaction")
        connection_id: str = Field(default="default", description="Connection identifier")
    
    args_schema: Type[BaseModel] = ToolInput
    
    def _run(self, query: str, params: List[Any] = None, 
             transaction: bool = False, connection_id: str = "default") -> str:
        """Execute database query with connection management"""
        
        try:
            connection = self._get_connection(connection_id)
            cursor = connection.cursor()
            
            if transaction and connection_id not in self.transaction_stack:
                connection.execute("BEGIN TRANSACTION")
                self.transaction_stack.append(connection_id)
            
            # Execute query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Handle different query types
            if query.strip().lower().startswith(('select', 'with')):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                # Format results as JSON
                formatted_results = []
                for row in results:
                    formatted_results.append(dict(zip(columns, row)))
                
                return json.dumps(formatted_results, indent=2)
            
            else:
                # For INSERT, UPDATE, DELETE
                rows_affected = cursor.rowcount
                if not transaction:
                    connection.commit()
                
                return f"Query executed successfully. Rows affected: {rows_affected}"
                
        except Exception as e:
            if connection_id in self.transaction_stack:
                connection.rollback()
                self.transaction_stack.remove(connection_id)
            
            return f"Database error: {str(e)}"
    
    def _get_connection(self, connection_id: str):
        """Get or create database connection"""
        if connection_id not in self.connection_pool:
            self.connection_pool[connection_id] = sqlite3.connect(
                self.db_config.get('database_path', ':memory:'),
                check_same_thread=False
            )
        
        return self.connection_pool[connection_id]
    
    def commit_transaction(self, connection_id: str = "default") -> str:
        """Commit pending transaction"""
        if connection_id in self.transaction_stack:
            connection = self.connection_pool[connection_id]
            connection.commit()
            self.transaction_stack.remove(connection_id)
            return "Transaction committed successfully"
        
        return "No active transaction to commit"
    
    def rollback_transaction(self, connection_id: str = "default") -> str:
        """Rollback pending transaction"""
        if connection_id in self.transaction_stack:
            connection = self.connection_pool[connection_id]
            connection.rollback()
            self.transaction_stack.remove(connection_id)
            return "Transaction rolled back successfully"
        
        return "No active transaction to rollback"

class WorkflowTool(BaseTool):
    """Tool for executing complex workflows with state management"""
    
    name = "workflow_tool"
    description = "Execute complex workflows with step-by-step state management"
    
    def __init__(self, workflow_definitions: Dict[str, Any]):
        super().__init__()
        self.workflow_definitions = workflow_definitions
        self.active_workflows = {}
        
    class ToolInput(BaseModel):
        workflow_name: str = Field(description="Name of workflow to execute")
        workflow_data: Dict[str, Any] = Field(description="Input data for workflow")
        step_name: Optional[str] = Field(default=None, description="Specific step to execute")
        workflow_id: Optional[str] = Field(default=None, description="Existing workflow ID")
    
    args_schema: Type[BaseModel] = ToolInput
    
    def _run(self, workflow_name: str, workflow_data: Dict[str, Any],
             step_name: Optional[str] = None, workflow_id: Optional[str] = None) -> str:
        """Execute workflow or workflow step"""
        
        if workflow_name not in self.workflow_definitions:
            return f"Workflow '{workflow_name}' not found"
        
        # Create or get existing workflow instance
        if workflow_id:
            if workflow_id not in self.active_workflows:
                return f"Workflow instance '{workflow_id}' not found"
            workflow_instance = self.active_workflows[workflow_id]
        else:
            workflow_id = f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            workflow_instance = self._create_workflow_instance(
                workflow_name, workflow_id, workflow_data
            )
            self.active_workflows[workflow_id] = workflow_instance
        
        # Execute specific step or continue workflow
        if step_name:
            result = self._execute_workflow_step(workflow_instance, step_name)
        else:
            result = self._execute_next_workflow_step(workflow_instance)
        
        return json.dumps({
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "current_step": workflow_instance["current_step"],
            "status": workflow_instance["status"],
            "result": result,
            "completed_steps": workflow_instance["completed_steps"]
        }, indent=2)
    
    def _create_workflow_instance(self, workflow_name: str, workflow_id: str,
                                 workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new workflow instance"""
        workflow_def = self.workflow_definitions[workflow_name]
        
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "definition": workflow_def,
            "data": workflow_data,
            "current_step": 0,
            "status": "active",
            "completed_steps": [],
            "step_results": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    
    def _execute_next_workflow_step(self, workflow_instance: Dict[str, Any]) -> str:
        """Execute the next step in the workflow"""
        steps = workflow_instance["definition"]["steps"]
        current_step_index = workflow_instance["current_step"]
        
        if current_step_index >= len(steps):
            workflow_instance["status"] = "completed"
            return "Workflow completed successfully"
        
        step = steps[current_step_index]
        result = self._execute_workflow_step(workflow_instance, step["name"])
        
        # Advance to next step
        workflow_instance["current_step"] += 1
        workflow_instance["completed_steps"].append(step["name"])
        workflow_instance["updated_at"] = datetime.now()
        
        return result
    
    def _execute_workflow_step(self, workflow_instance: Dict[str, Any], step_name: str) -> str:
        """Execute a specific workflow step"""
        steps = {step["name"]: step for step in workflow_instance["definition"]["steps"]}
        
        if step_name not in steps:
            return f"Step '{step_name}' not found in workflow"
        
        step = steps[step_name]
        step_type = step.get("type", "action")
        
        # Execute based on step type
        if step_type == "action":
            return self._execute_action_step(workflow_instance, step)
        elif step_type == "condition":
            return self._execute_condition_step(workflow_instance, step)
        elif step_type == "parallel":
            return self._execute_parallel_step(workflow_instance, step)
        else:
            return f"Unknown step type: {step_type}"
    
    def _execute_action_step(self, workflow_instance: Dict[str, Any], step: Dict[str, Any]) -> str:
        """Execute an action step"""
        action = step.get("action", "")
        parameters = step.get("parameters", {})
        
        # Replace parameters with workflow data
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("${"):
                param_path = value[2:-1]
                parameters[key] = self._get_nested_value(workflow_instance["data"], param_path)
        
        # Store step result
        result = f"Executed action: {action} with parameters: {parameters}"
        workflow_instance["step_results"][step["name"]] = result
        
        return result
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from data using dot notation"""
        keys = path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
```

---

## 🎯 Module Summary

You've now mastered advanced LangChain patterns for production systems:

✅ **Complex Multi-Agent Workflows**: Built sophisticated orchestration systems with specialized agents  
✅ **Custom Chain Development**: Created reusable chain components with advanced logic and validation  
✅ **Advanced Tool Patterns**: Implemented production-ready tools with state management and error recovery  
✅ **Enterprise Architecture**: Designed scalable patterns for complex LangChain applications

### Next Steps
- **Continue to Module B**: [Production Deployment Strategies](Session2_ModuleB_Production_Deployment_Strategies.md) for enterprise deployment
- **Continue to Module C**: [Custom Tool Development](Session2_ModuleC_Custom_Tool_Development.md) for specialized tools
- **Return to Core**: [Session 2 Main](Session2_LangChain_Foundations.md)
- **Advance to Session 3**: [LangGraph Multi-Agent Workflows](Session3_LangGraph_Multi_Agent_Workflows.md)

---

**🗂️ Source Files for Module A:**
- `src/session2/multi_agent_workflows.py` - Complex agent coordination systems
- `src/session2/custom_chains.py` - Custom chain implementations
- `src/session2/advanced_tools.py` - Production-ready tool patterns