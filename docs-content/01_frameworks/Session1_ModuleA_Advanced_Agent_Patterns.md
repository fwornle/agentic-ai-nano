# Session 1 - Module A: Advanced Agent Patterns

> **⚠️ ADVANCED OPTIONAL MODULE**
> Prerequisites: Complete Session 1 core content first.

In 2023, a Fortune 500 financial services company discovered their AI data processing assistant had developed an unexpected capability: it could critique its own data transformation recommendations, identify flaws in its ETL logic, and systematically improve its approach over multiple iterations. What started as a simple rule-based data validation system had evolved into something resembling expert data engineering judgment - the ability to step back, analyze pipeline performance, and consciously optimize processing strategies.

This wasn't magic. It was the strategic implementation of advanced agent patterns that separate amateur data processing systems from the sophisticated reasoning engines powering today's most successful data platforms. When Netflix deploys AI for content recommendation pipeline optimization or when Spotify's streaming data systems coordinate real-time analytics processing, they rely on these same meta-cognitive patterns you're about to master.

The transformation from simple "process and store" to sophisticated self-optimizing data systems represents a fundamental shift in data architecture - one that enables agents to tackle the complex, multi-step challenges that define modern data engineering success.

## Part 1: Sophisticated Reasoning Loops

### The Reflection Pattern Implementation

🗂️ **File**: `src/session1/reflection_agent.py` - Advanced ReAct implementation

The reflection pattern enables agents to iteratively improve their data processing decisions through self-critique and refinement:

### Traditional Approach:

```text
Data Input → Process → Store Result
```

### Reflection Approach:

```text
Data Input → Initial Processing → Critique Quality → Optimize → Validate → Final Processing
```

### Reflection Agent Structure

Understanding Bare Metal Self-Improvement: This reflection agent demonstrates the foundational pattern of iterative self-improvement for data processing. It inherits from BaseAgent and adds the ability to critique and enhance its own data processing strategies through multiple iterations.

```python
# From src/session1/reflection_agent.py
from base_agent import BaseAgent
from typing import Dict

class ReflectionAgent(BaseAgent):
    """Agent that reflects on and improves its own data processing outputs"""

    def __init__(self, name: str, llm_client, max_iterations: int = 3):
        super().__init__(name, "Agent with data processing reflection capabilities", llm_client)
        self.max_iterations = max_iterations  # Prevent infinite optimization loops
        self.reflection_history = []          # Track data processing improvements
```

The ReflectionAgent demonstrates the foundational pattern of iterative self-improvement for data processing. By limiting iterations to 3, it prevents the agent from getting stuck in endless optimization cycles that could consume excessive compute resources in production environments.

**Why Limit Iterations?** Without a maximum, the agent could get stuck in endless data processing optimization loops, consuming excessive compute resources in production pipelines.

### The Core Reflection Loop

The core reflection loop orchestrates the iterative data processing improvement process:

```python
# From src/session1/reflection_agent.py (continued)
async def _generate_response(self, message: str, context: Dict = None) -> str:
    """Generate data processing response with reflection and optimization"""
    current_response = await self._initial_data_processing(message, context)

    for iteration in range(self.max_iterations):
        # Step 1: Reflect on current data processing approach
        critique = await self._reflect_on_processing(message, current_response)

        # Step 2: If processing approach is optimal, return it
        if self._is_processing_satisfactory(critique):
            self.logger.info(f"Data processing optimal after {iteration + 1} iterations")
            break
```

The core reflection loop orchestrates iterative improvement. Each iteration evaluates the current approach and determines whether optimization is needed. The satisfaction check prevents unnecessary processing when the solution is already adequate for data engineering requirements.

```python
        # Step 3: Optimize processing based on critique
        improved_response = await self._improve_processing(
            message, current_response, critique
        )

        # Step 4: Track the optimization process for pipeline metrics
        self._track_reflection(iteration, current_response, critique, improved_response)

        current_response = improved_response

    return current_response
```

The optimization phase generates improved processing strategies based on the critique, while tracking captures the entire improvement process for performance analysis. This creates a detailed audit trail of how the agent's data processing approach evolved.

### Reflection Methods Implementation

### Initial Data Processing Generation:

```python
async def _initial_data_processing(self, message: str, context: Dict = None) -> str:
    """Generate initial data processing approach without reflection"""
    system_prompt = f"""
    You are {self.name}, {self.description}.
    Design an optimal data processing approach for the given requirements.
    Focus on throughput, data quality, and cost efficiency for large-scale systems.
    Consider partitioning strategies, batch sizing, and resource utilization.
    """

    prompt = f"{system_prompt}\n\nProcessing requirements: {message}"
    response = await self._call_llm(prompt)
    return response
```

The initial processing method generates the first approach without reflection, focusing on key data engineering concerns: throughput optimization for high-volume processing, data quality assurance for reliable analytics, and cost efficiency for sustainable operations. This establishes the baseline that reflection will iteratively improve.

### Self-Critique Implementation:

The reflection method analyzes the agent's own data processing approach using structured evaluation criteria focused on data engineering concerns:

```python
async def _reflect_on_processing(self, original_message: str, response: str) -> str:
    """Generate critique of the current data processing approach"""
    critique_prompt = f"""
    Analyze this data processing approach and provide constructive criticism.

    Processing requirements: {original_message}
    Proposed approach: {response}

    Evaluate from a data engineering perspective:
    1. Scalability: Can this handle petabyte-scale datasets?
    2. Performance: Are batch sizes and parallelization optimal?
    3. Cost efficiency: Does this minimize cloud compute costs?
    4. Data quality: Are validation and error handling comprehensive?
    5. Reliability: Will this maintain SLAs under high load?
    6. Monitoring: Can pipeline health be effectively tracked?
```

The reflection method analyzes the processing approach using six critical data engineering evaluation criteria. Each criterion addresses a specific aspect of production-scale data processing: scalability for growth, performance for efficiency, cost control for sustainability, quality for reliability, SLA compliance for business requirements, and monitoring for operational visibility.

```python
    Provide specific suggestions for improvement based on production data engineering best practices.
    If the approach is already optimal for enterprise scale, say "SATISFACTORY".
    """

    critique = await self._call_llm(critique_prompt)
    return critique
```

The critique focuses on actionable improvements based on proven data engineering practices. The "SATISFACTORY" keyword provides a clear stopping condition that prevents endless optimization when the approach already meets enterprise-scale requirements.

The "SATISFACTORY" keyword provides a clear stopping condition, preventing endless optimization cycles when the processing approach is already production-ready.

### Data Processing Improvement:

The improvement process takes the critique and generates an enhanced processing strategy that specifically addresses the identified data engineering issues:

```python
async def _improve_processing(self, message: str, current_response: str, critique: str) -> str:
    """Improve data processing approach based on critique"""
    improvement_prompt = f"""
    Optimize the following data processing approach based on the critique provided.

    Original requirements: {message}
    Current processing approach: {current_response}
    Critique focusing on data engineering concerns: {critique}

    Generate an improved approach that addresses the critique while maintaining:
    - High throughput for large datasets
    - Cost optimization for cloud deployment
    - Robust error handling and data quality validation
    - Scalable architecture for petabyte-scale processing
    """

    improved = await self._call_llm(improvement_prompt)
    return improved
```

The improvement process generates enhanced processing strategies that specifically address critique points while preserving essential data engineering principles. This targeted optimization ensures that reflection doesn't just change the approach randomly but systematically addresses identified weaknesses while maintaining proven strengths.

## Part 2: Multi-Step Planning

### Planning Agent Architecture

🗂️ **File**: `src/session1/react_agent.py` - Multi-step data pipeline planning implementation

Complex data processing tasks require breaking down into manageable steps with proper execution order and dependency handling:

```python
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class DataProcessingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

The status enumeration provides clear state tracking for each pipeline step, enabling proper workflow management and error handling. This structured approach prevents ambiguous states and enables automated workflow orchestration based on step completion status.

```python
@dataclass
class DataPipelineStep:
    id: str
    description: str
    dependencies: List[str]
    estimated_time: int
    resource_requirements: Dict[str, any]  # CPU, memory, storage needs
    status: DataProcessingStatus = DataProcessingStatus.PENDING
    result: Optional[str] = None
```

The DataPipelineStep dataclass captures comprehensive information for each processing stage: unique identification, clear description of the operation, dependency relationships for proper sequencing, time estimates for resource planning, resource requirements for cloud deployment, execution status for tracking, and result storage for downstream steps.

The `DataPipelineStep` dataclass captures all essential information for data pipeline execution: what to process (description), when to process it (dependencies), resource requirements for cloud deployment, and execution outcomes (status and result).

```python
class DataPipelinePlanningAgent(BaseAgent):
    """Agent that breaks down complex data processing tasks into executable pipeline steps"""

    def __init__(self, name: str, llm_client):
        super().__init__(name, "Multi-step data pipeline planning agent", llm_client)
        self.current_plan: Optional[List[DataPipelineStep]] = None
        self.execution_history: List[Dict] = []
        self.resource_tracker = DataResourceTracker()  # Track cloud resource usage
```

The planning agent specializes in decomposing complex data workflows into executable steps with proper dependency management. The resource tracker monitors cloud service consumption, enabling cost optimization and capacity planning across distributed processing environments.

### Pipeline Plan Generation

The planning system breaks complex data processing workflows into manageable, executable steps with clear dependencies and resource allocation:

```python
async def create_data_pipeline_plan(self, complex_data_task: str) -> List[DataPipelineStep]:
    """Break down complex data processing task into executable pipeline steps"""

    planning_prompt = f"""
    Break down this complex data processing task into specific, executable pipeline steps:
    Task: {complex_data_task}

    For each step, provide:
    1. Clear description of data processing operation
    2. Dependencies (which steps must complete first for data availability)
    3. Estimated time in minutes for large-scale processing
    4. Resource requirements (CPU, memory, storage for cloud deployment)
    5. Data quality checkpoints and validation requirements

    Consider:
    - Optimal batch sizing for throughput
    - Parallelization opportunities
    - Data partitioning strategies
    - Error handling and recovery mechanisms
    - Cost optimization through efficient resource usage

    Format as a numbered list with dependencies and resource requirements noted.
    Be specific about data volumes, formats, and processing requirements.
    """
```

The planning prompt guides the LLM to consider essential data engineering factors when decomposing complex tasks. Each consideration addresses a critical aspect of production data processing: batch sizing for performance, parallelization for scale, partitioning for efficiency, error handling for reliability, and cost optimization for sustainability.

```python
    plan_text = await self._call_llm(planning_prompt)

    # Parse the plan into DataPipelineStep objects
    steps = self._parse_data_pipeline_plan(plan_text)
    self.current_plan = steps

    return steps
```

The LLM-generated plan text is parsed into structured DataPipelineStep objects that can be programmatically executed. This transformation enables the agent to move from natural language planning to executable workflow orchestration in cloud environments.

The LLM generates a text-based data processing plan which is then parsed into structured objects for programmatic execution in cloud environments.

```python
def _parse_data_pipeline_plan(self, plan_text: str) -> List[DataPipelineStep]:
    """Parse LLM-generated data pipeline plan into structured steps"""
    steps = []
    lines = plan_text.strip().split('\n')

    for i, line in enumerate(lines):
        if line.strip() and any(line.startswith(str(j)) for j in range(1, 20)):
            # Extract data processing step information
            step_id = f"data_step_{i+1}"
            description = line.split('.', 1)[1].strip() if '.' in line else line.strip()
```

The parser identifies numbered steps from the LLM output and extracts meaningful descriptions. This text-to-structure conversion enables programmatic execution of naturally expressed data processing workflows.

```python
            # Extract data processing dependencies and resource requirements
            dependencies = self._extract_data_dependencies(description)
            resource_reqs = self._extract_resource_requirements(description)

            steps.append(DataPipelineStep(
                id=step_id,
                description=description,
                dependencies=dependencies,
                estimated_time=15,  # Default for data processing operations
                resource_requirements=resource_reqs
            ))

    return steps
```

Dependency and resource extraction creates the metadata necessary for intelligent pipeline orchestration. Each step includes dependency relationships for proper sequencing and resource requirements for optimal cloud deployment and cost management.

Dependency and resource extraction ensures proper pipeline orchestration with appropriate cloud resource allocation for each data processing step.

### Data Pipeline Execution Engine

The execution engine manages the sequential execution of data pipeline steps while respecting dependencies and resource constraints:

```python
async def execute_data_pipeline(self) -> Dict[str, any]:
    """Execute the current data pipeline with dependency and resource management"""
    if not self.current_plan:
        return {"error": "No data pipeline to execute"}

    execution_log = []
    completed_steps = set()
    resource_usage = {"total_cost": 0, "peak_memory": 0, "total_compute_hours": 0}

    while len(completed_steps) < len(self.current_plan):
        # Find next executable step (dependencies satisfied, resources available)
        next_step = self._find_next_executable_data_step(completed_steps)

        if not next_step:
            return {"error": "No executable steps found - check dependencies or resource constraints"}
```

The execution engine orchestrates pipeline steps while respecting both logical dependencies and resource constraints. This dual consideration ensures steps execute in the correct order while maintaining optimal resource utilization across the cloud infrastructure.

```python
        # Allocate resources and execute the data processing step
        self.logger.info(f"Executing data processing step: {next_step.description}")
        next_step.status = DataProcessingStatus.IN_PROGRESS

        # Track resource allocation for cost monitoring
        allocated_resources = await self.resource_tracker.allocate_resources(
            next_step.resource_requirements
        )

        try:
            result = await self._execute_data_step(next_step, allocated_resources)
            next_step.result = result
            next_step.status = DataProcessingStatus.COMPLETED
            completed_steps.add(next_step.id)
```

Resource allocation and execution tracking provide comprehensive visibility into processing performance. Each step transitions through clear status states while resource allocation ensures optimal cloud resource utilization and cost control.

```python
            # Update resource usage tracking
            resource_usage = self.resource_tracker.update_usage(
                allocated_resources, result.get('metrics', {})
            )

            execution_log.append({
                "step": next_step.description,
                "result": result,
                "status": "completed",
                "resources_used": allocated_resources,
                "processing_metrics": result.get('metrics', {})
            })
```

Comprehensive logging captures both functional results and operational metrics, enabling post-execution analysis, cost optimization, and performance tuning for future data processing workflows.

```python
        except Exception as e:
            next_step.status = DataProcessingStatus.FAILED
            execution_log.append({
                "step": next_step.description,
                "error": str(e),
                "status": "failed",
                "resources_allocated": allocated_resources
            })
            # Release allocated resources on failure
            await self.resource_tracker.release_resources(allocated_resources)
            break
        finally:
            # Always release resources after step completion
            await self.resource_tracker.release_resources(allocated_resources)

    return {
        "execution_log": execution_log,
        "completed_steps": len(completed_steps),
        "total_steps": len(self.current_plan),
        "success": len(completed_steps) == len(self.current_plan),
        "resource_usage": resource_usage,
        "cost_analysis": self.resource_tracker.generate_cost_report()
    }
```

Robust error handling ensures proper resource cleanup even when steps fail, preventing resource leaks in cloud environments. The comprehensive return structure provides complete visibility into execution results, resource utilization, and cost implications for operational analysis.

Comprehensive resource management ensures proper cleanup and provides detailed cost analysis for data processing operations.

```python
async def _execute_data_step(self, step: DataPipelineStep, resources: Dict) -> str:
    """Execute an individual data pipeline step with allocated resources"""
    execution_prompt = f"""
    Execute this specific data processing task:
    {step.description}

    Allocated resources: {resources}

    Provide a detailed result including:
    1. What data processing operations were completed
    2. Data volume processed and throughput achieved
    3. Quality metrics and validation results
    4. Performance metrics (processing time, resource utilization)
    5. Any data quality issues or anomalies detected

    Be specific about data formats, processing efficiency, and outcomes.
    """

    result = await self._call_llm(execution_prompt)
    return result
```

Individual step execution uses focused prompts that emphasize operational metrics essential for data engineering: processing completion status, throughput performance, quality validation outcomes, resource efficiency, and anomaly detection. These metrics enable comprehensive pipeline monitoring and optimization.

Individual step execution uses focused prompts that emphasize data engineering metrics and quality outcomes essential for production pipeline monitoring.

## Part 3: Multi-Agent Orchestration

### Data Processing Agent Coordinator Architecture

🗂️ **File**: `src/session1/multi_agent_system.py` - Multi-agent data processing coordination

Understanding Bare Metal Multi-Agent Coordination: This coordinator class manages multiple specialized data processing agents working together on complex data workflows. It handles agent registration, message routing, and communication tracking optimized for data engineering operations.

```python
from typing import Dict, List, Any
from base_agent import BaseAgent, AgentMessage
from datetime import datetime

class DataProcessingCoordinator:
    """Coordinates multiple specialized data processing agents in a distributed system"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}  # Specialized data processing agents
        self.message_history = []               # All inter-agent data processing messages
        self.communication_patterns = {}       # Track data flow patterns
        self.pipeline_metrics = {}            # Track processing performance metrics
```

The coordinator manages multiple specialized agents working together on complex data processing workflows. It maintains comprehensive tracking of agent communications, data flow patterns, and performance metrics essential for optimizing distributed data processing operations.

```python
    def register_data_agent(self, agent: BaseAgent):
        """Register a specialized data processing agent with the coordinator"""
        self.agents[agent.name] = agent
        self.communication_patterns[agent.name] = []
        self.pipeline_metrics[agent.name] = {"processed_data_gb": 0, "processing_time": 0}
        print(f"✓ Registered data processing agent: {agent.name} ({agent.description})")
```

Agent registration establishes the coordination infrastructure, initializing communication tracking and performance metrics for each specialized agent. This setup enables comprehensive monitoring and optimization of multi-agent data processing workflows.

### Message Routing System

The routing system manages communication between data processing agents while maintaining detailed logs for pipeline analysis:

```python
async def route_data_message(self, message: str, to_agent: str, from_agent: str = "pipeline_controller") -> str:
    """Route data processing message to specific agent and track communication"""
    if to_agent not in self.agents:
        return f"Error: Data processing agent '{to_agent}' not found"

    # Log data processing communication pattern
    self.communication_patterns[to_agent].append({
        "from": from_agent,
        "message_type": self._classify_data_message(message),
        "message": message[:50] + "..." if len(message) > 50 else message,
        "timestamp": datetime.now()
    })
```

Message routing includes comprehensive communication tracking that captures sender, message classification, content summary, and timing. This data enables analysis of communication efficiency and optimization of agent coordination patterns in distributed data processing environments.

```python
    # Process message with target data processing agent
    agent = self.agents[to_agent]
    response = await agent.process_message(message)

    # Store complete data processing conversation
    self.message_history.append({
        "from": from_agent,
        "to": to_agent,
        "message": message,
        "response": response,
        "processing_metrics": self._extract_processing_metrics(response),
        "timestamp": datetime.now()
    )

    return response
```

Complete conversation history maintains full context of inter-agent communications with extracted processing metrics. This comprehensive logging enables debugging, performance analysis, and optimization of multi-agent data processing workflows.

The complete message history stores full conversations with extracted processing metrics for debugging, performance analysis, and data pipeline audit purposes.

### Collaborative Data Processing Task Management

Complex data processing workflows are broken down and delegated to the most appropriate specialized agents:

```python
async def delegate_data_processing_task(self, task: str) -> Dict[str, Any]:
    """Delegate complex data processing task to appropriate specialized agents"""

    # Step 1: Analyze data processing requirements to determine which agents are needed
    task_analysis = await self._analyze_data_task_requirements(task)

    # Step 2: Create delegation plan based on data processing capabilities
    delegation_plan = self._create_data_delegation_plan(task_analysis)

    # Step 3: Execute delegation plan with resource coordination
```

The three-phase delegation approach ensures systematic task decomposition and agent assignment. Task analysis identifies required capabilities, delegation planning maps work to appropriate specialists, and coordinated execution maintains workflow integrity across distributed agents.

```python
    results = {}
    processing_metrics = {}
    for agent_name, subtask in delegation_plan.items():
        if agent_name in self.agents:
            start_time = datetime.now()
            result = await self.route_data_message(subtask, agent_name, "coordinator")
            end_time = datetime.now()

            results[agent_name] = result
            processing_metrics[agent_name] = {
                "processing_time": (end_time - start_time).total_seconds(),
                "data_processed": self._extract_data_volume(result),
                "resource_efficiency": self._calculate_efficiency(result)
            }
```

Execution tracking captures both functional results and operational metrics for each agent's contribution. This comprehensive monitoring enables performance optimization and resource allocation improvements for future multi-agent data processing workflows.

```python
    # Step 4: Integrate data processing results
    final_result = await self._integrate_data_results(task, results)

    return {
        "original_task": task,
        "delegation_plan": delegation_plan,
        "agent_results": results,
        "processing_metrics": processing_metrics,
        "integrated_result": final_result,
        "total_data_processed": sum(m.get('data_processed', 0) for m in processing_metrics.values()),
        "pipeline_efficiency": self._calculate_pipeline_efficiency(processing_metrics)
    }
```

Result integration combines individual agent outputs into cohesive data processing outcomes. The comprehensive return structure provides complete visibility into task delegation, execution results, performance metrics, and overall pipeline efficiency for operational analysis and optimization.

The final integration step combines individual agent results into a cohesive data processing outcome with comprehensive metrics for pipeline monitoring and optimization.

Task analysis uses the LLM to understand which specialized data processing agents are needed:

```python
async def _analyze_data_task_requirements(self, task: str) -> Dict[str, Any]:
    """Analyze what types of data processing agents are needed for this task"""
    analysis_prompt = f"""
    Analyze this data processing task and determine what types of specialized agents would be needed:
    Task: {task}

    Available specialized data processing agents: {list(self.agents.keys())}

    Consider the data processing pipeline requirements:
    1. Data ingestion and validation needs
    2. Transformation and enrichment requirements
    3. Quality assurance and anomaly detection needs
    4. Storage optimization and partitioning requirements
    5. Analytics and reporting capabilities needed

    For each needed agent type, specify:
    1. What specific data processing subtask they should handle
    2. Why this specialized agent is appropriate for this data operation
    3. Expected data volume and processing requirements
    4. Dependencies on other agents' outputs

    Return analysis focusing on data engineering optimization and scalability.
    """

    # This would use an LLM to analyze - simplified for example
    return {"required_agents": list(self.agents.keys())[:2]}  # Simplified
```

Task analysis uses structured evaluation criteria to identify the specialized capabilities needed for complex data processing workflows. The analysis considers the complete data processing pipeline from ingestion through analytics, ensuring comprehensive coverage of all required capabilities and optimal agent selection for the specific task requirements.

The analysis provides context about available specialized data processing agents and requests specific justifications for agent selection, ensuring intelligent task distribution optimized for data engineering workflows rather than random assignment.

## Module Summary

You've now mastered advanced agent patterns for data engineering including:

✅ **Reflection Agents**: Implemented self-improvement through iterative critique and refinement of data processing strategies
✅ **Multi-Step Planning**: Built systems that decompose complex data workflows into executable pipeline plans
✅ **Multi-Agent Orchestration**: Created coordination systems for specialized data processing agent collaboration
✅ **Self-Improvement Mechanisms**: Designed agents that enhance their data processing performance over time

---

## 📝 Multiple Choice Test - Session 1

Test your understanding of advanced agent patterns:

**Question 1:** What is the key mechanism that prevents infinite loops in data processing reflection agents?  
A) Memory limitations  
B) Maximum iteration limits with satisfactory conditions  
C) Network timeouts  
D) User intervention  

**Question 2:** In multi-step data pipeline planning, what is the primary purpose of dependency management?  
A) Reducing memory usage  
B) Ensuring pipeline steps execute in the correct order with proper data flow  
C) Speeding up execution  
D) Simplifying code structure  

**Question 3:** What does the planning agent's `_parse_data_pipeline_plan` method accomplish?  
A) Generates new plans from scratch  
B) Converts LLM-generated text into structured DataPipelineStep objects  
C) Executes individual pipeline steps  
D) Validates plan correctness  

**Question 4:** In multi-agent data processing orchestration, what information is stored in communication patterns?  
A) Complete message history with full content  
B) Summarized message data with data processing context, sender, recipient, and timestamp  
C) Only error messages  
D) Agent performance metrics  

**Question 5:** What is the three-phase approach used in collaborative data processing task management?  
A) Planning, execution, validation  
B) Analysis, delegation, integration  
C) Data task analysis, delegation plan creation, coordinated execution  
D) Registration, routing, completion  

[View Solutions →](Session1_Test_Solutions.md)

---

## 🧭 Navigation

**Previous:** [Session 0 - Introduction →](Session0_Introduction_to_Agent_Frameworks_Patterns.md)  
**Next:** [Session 2 - Implementation →](Session2_LangChain_Foundations.md)

---
