# Session 6 - Module A: Advanced Composition Patterns (35 minutes)

**Prerequisites**: [Session 6 Core Section Complete](Session6_Atomic_Agents_Modular_Architecture.md)  
**Target Audience**: Implementers building sophisticated atomic systems  
**Cognitive Load**: 4 advanced concepts

---

## 🎯 Module Overview

This module explores sophisticated atomic agent composition patterns including pipeline orchestration, parallel processing, dynamic agent assembly, and CLI integration for DevOps workflows. You'll learn to build complex, maintainable systems from simple atomic components using proven architectural patterns.

### Learning Objectives
By the end of this module, you will:
- Design sequential and parallel agent pipelines with robust error handling
- Implement dynamic agent composition systems that adapt to runtime requirements
- Create CLI tools for atomic agent management and DevOps integration
- Build sophisticated context-aware agent orchestration systems

---

## Part 1: Agent Pipeline Orchestration (20 minutes)

### Sequential Processing Pipelines

🗂️ **File**: `src/session6/advanced_composition.py` - Sophisticated pipeline patterns

Complex atomic systems emerge from combining simple agents through well-designed composition patterns:

```python
from typing import List, Dict, Any, TypeVar, Generic, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime
from atomic_schemas import TaskInput, TaskOutput, AnalysisInput, AnalysisOutput

T_Input = TypeVar('T_Input')
T_Output = TypeVar('T_Output')
T_Intermediate = TypeVar('T_Intermediate')

@dataclass
class PipelineStage:
    """Definition of a pipeline processing stage"""
    stage_id: str
    agent: Any  # AtomicAgent instance
    stage_name: str
    description: str
    error_policy: str = "stop"  # stop, skip, retry
    retry_count: int = 3
    timeout_seconds: int = 60

@dataclass
class PipelineContext:
    """Context passed through pipeline execution"""
    pipeline_id: str
    execution_start: datetime
    stage_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_log: List[Dict[str, Any]] = field(default_factory=list)

class AdvancedAtomicPipeline:
    """Sophisticated pipeline orchestration with error handling and monitoring"""
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.stages: List[PipelineStage] = []
        self.middleware_functions: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        self.performance_metrics = {}
        
    def add_stage(self, stage: PipelineStage) -> 'AdvancedAtomicPipeline':
        """Add a processing stage to the pipeline"""
        self.stages.append(stage)
        return self  # Enable fluent interface
    
    def add_middleware(self, middleware_func: Callable) -> 'AdvancedAtomicPipeline':
        """Add middleware function for cross-cutting concerns"""
        self.middleware_functions.append(middleware_func)
        return self
    
    async def execute(self, initial_input: Any, context: Optional[PipelineContext] = None) -> Dict[str, Any]:
        """Execute the complete pipeline with comprehensive monitoring"""
        
        if context is None:
            context = PipelineContext(
                pipeline_id=self.pipeline_id,
                execution_start=datetime.now()
            )
        
        current_data = initial_input
        execution_results = []
        
        try:
            for stage_index, stage in enumerate(self.stages):
                stage_start_time = datetime.now()
                
                # Apply middleware before stage execution
                for middleware in self.middleware_functions:
                    current_data = await self._apply_middleware(
                        middleware, current_data, stage, context
                    )
                
                # Execute stage with error handling
                stage_result = await self._execute_stage_with_resilience(
                    stage, current_data, context
                )
                
                # Record stage execution
                stage_duration = (datetime.now() - stage_start_time).total_seconds()
                
                stage_record = {
                    "stage_index": stage_index,
                    "stage_id": stage.stage_id,
                    "stage_name": stage.stage_name,
                    "execution_time": stage_duration,
                    "status": stage_result.get("status", "unknown"),
                    "input_size": len(str(current_data)),
                    "output_size": len(str(stage_result.get("output", ""))),
                    "timestamp": stage_start_time.isoformat()
                }
                
                context.stage_history.append(stage_record)
                execution_results.append(stage_record)
                
                # Handle stage result
                if stage_result["status"] == "success":
                    current_data = stage_result["output"]
                elif stage_result["status"] == "error":
                    if stage.error_policy == "stop":
                        break
                    elif stage.error_policy == "skip":
                        self.logger.warning(f"Skipping failed stage: {stage.stage_id}")
                        continue
                    # For retry policy, _execute_stage_with_resilience handles retries
                
                self.logger.info(f"Stage {stage.stage_id} completed in {stage_duration:.2f}s")
        
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {str(e)}")
            context.error_log.append({
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "stage": "pipeline_orchestration"
            })
        
        # Calculate overall metrics
        total_execution_time = (datetime.now() - context.execution_start).total_seconds()
        
        return {
            "pipeline_id": self.pipeline_id,
            "final_output": current_data,
            "execution_summary": {
                "total_stages": len(self.stages),
                "successful_stages": len([r for r in execution_results if r["status"] == "success"]),
                "failed_stages": len([r for r in execution_results if r["status"] == "error"]),
                "total_execution_time": total_execution_time,
                "average_stage_time": total_execution_time / len(self.stages) if self.stages else 0
            },
            "stage_details": execution_results,
            "context": context,
            "performance_metrics": self._calculate_performance_metrics(execution_results)
        }
    
    async def _execute_stage_with_resilience(self, stage: PipelineStage, 
                                           input_data: Any, 
                                           context: PipelineContext) -> Dict[str, Any]:
        """Execute stage with retry logic and timeout handling"""
        
        for attempt in range(stage.retry_count):
            try:
                # Execute stage with timeout
                stage_task = asyncio.create_task(stage.agent.process(input_data))
                output = await asyncio.wait_for(stage_task, timeout=stage.timeout_seconds)
                
                return {
                    "status": "success",
                    "output": output,
                    "attempt": attempt + 1,
                    "retry_needed": False
                }
                
            except asyncio.TimeoutError:
                error_msg = f"Stage {stage.stage_id} timed out after {stage.timeout_seconds}s"
                self.logger.warning(f"{error_msg} (attempt {attempt + 1})")
                
                if attempt == stage.retry_count - 1:  # Last attempt
                    context.error_log.append({
                        "error": error_msg,
                        "stage_id": stage.stage_id,
                        "attempt": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return {
                        "status": "error",
                        "error": error_msg,
                        "attempt": attempt + 1,
                        "retry_exhausted": True
                    }
                    
            except Exception as e:
                error_msg = f"Stage {stage.stage_id} failed: {str(e)}"
                self.logger.warning(f"{error_msg} (attempt {attempt + 1})")
                
                if attempt == stage.retry_count - 1:  # Last attempt
                    context.error_log.append({
                        "error": error_msg,
                        "stage_id": stage.stage_id,
                        "attempt": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return {
                        "status": "error",
                        "error": error_msg,
                        "attempt": attempt + 1,
                        "retry_exhausted": True
                    }
            
            # Wait before retry
            await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff, max 10s
        
        return {"status": "error", "error": "Unexpected retry loop exit"}

class ParallelAtomicProcessor:
    """Advanced parallel processing with load balancing and fault tolerance"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.logger = logging.getLogger(__name__)
        
    async def process_batch(self, agent_input_pairs: List[tuple], 
                          batch_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process multiple agent-input pairs with sophisticated load balancing"""
        
        if batch_context is None:
            batch_context = {"batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}
        
        batch_start_time = datetime.now()
        
        # Create processing tasks with semaphore control
        tasks = []
        for i, (agent, input_data) in enumerate(agent_input_pairs):
            task = self._process_with_semaphore(
                agent, input_data, f"task_{i}", batch_context
            )
            tasks.append(task)
        
        # Execute all tasks with progress monitoring
        results = await self._execute_with_monitoring(tasks, batch_context)
        
        # Calculate batch metrics
        batch_duration = (datetime.now() - batch_start_time).total_seconds()
        successful_tasks = len([r for r in results if not isinstance(r, Exception)])
        failed_tasks = len(results) - successful_tasks
        
        return {
            "batch_id": batch_context["batch_id"],
            "results": results,
            "batch_summary": {
                "total_tasks": len(agent_input_pairs),
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": successful_tasks / len(agent_input_pairs),
                "batch_duration": batch_duration,
                "average_task_time": batch_duration / len(agent_input_pairs),
                "concurrency_used": min(len(agent_input_pairs), self.max_concurrent)
            },
            "performance_metrics": self._calculate_batch_metrics(results, batch_duration)
        }
    
    async def _process_with_semaphore(self, agent: Any, input_data: Any, 
                                    task_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process single agent with semaphore-controlled concurrency"""
        
        async with self.semaphore:
            task_start_time = datetime.now()
            
            try:
                result = await agent.process(input_data)
                task_duration = (datetime.now() - task_start_time).total_seconds()
                
                return {
                    "task_id": task_id,
                    "status": "success",
                    "result": result,
                    "execution_time": task_duration,
                    "agent_id": getattr(agent, 'agent_id', 'unknown'),
                    "timestamp": task_start_time.isoformat()
                }
                
            except Exception as e:
                task_duration = (datetime.now() - task_start_time).total_seconds()
                self.logger.error(f"Task {task_id} failed: {str(e)}")
                
                return {
                    "task_id": task_id,
                    "status": "error",
                    "error": str(e),
                    "execution_time": task_duration,
                    "agent_id": getattr(agent, 'agent_id', 'unknown'),
                    "timestamp": task_start_time.isoformat()
                }
    
    async def _execute_with_monitoring(self, tasks: List, context: Dict[str, Any]) -> List[Any]:
        """Execute tasks with progress monitoring and graceful error handling"""
        
        results = []
        completed = 0
        total_tasks = len(tasks)
        
        # Use asyncio.as_completed for progress monitoring
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                results.append(result)
                completed += 1
                
                # Log progress
                progress = (completed / total_tasks) * 100
                self.logger.info(f"Batch progress: {completed}/{total_tasks} ({progress:.1f}%)")
                
            except Exception as e:
                results.append(e)
                completed += 1
                self.logger.error(f"Task failed in batch: {str(e)}")
        
        return results
```

---

## Part 2: Dynamic Agent Assembly and CLI Integration (15 minutes)

### Runtime Agent Composition

🗂️ **File**: `src/session6/dynamic_assembly.py` - Runtime composition systems

```python
from typing import Dict, List, Any, Type, Optional
import importlib
import inspect
from dataclasses import dataclass
from enum import Enum

class AgentCapability(Enum):
    """Standard atomic agent capabilities"""
    TASK_PROCESSING = "task_processing"
    CONTENT_ANALYSIS = "content_analysis"
    DATA_TRANSFORMATION = "data_transformation"
    COMMUNICATION = "communication"
    VALIDATION = "validation"
    REPORTING = "reporting"

@dataclass
class AgentDefinition:
    """Runtime agent definition"""
    agent_class: str
    module_path: str
    capabilities: List[AgentCapability]
    input_schema: str
    output_schema: str
    configuration: Dict[str, Any]
    resource_requirements: Dict[str, Any]

class DynamicAgentRegistry:
    """Registry for dynamic agent discovery and instantiation"""
    
    def __init__(self):
        self.registered_agents: Dict[str, AgentDefinition] = {}
        self.capability_index: Dict[AgentCapability, List[str]] = {}
        self.schema_compatibility: Dict[str, List[str]] = {}
        
    def register_agent(self, agent_id: str, definition: AgentDefinition):
        """Register an agent definition for dynamic instantiation"""
        
        self.registered_agents[agent_id] = definition
        
        # Index by capabilities
        for capability in definition.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = []
            self.capability_index[capability].append(agent_id)
        
        # Index schema compatibility
        output_schema = definition.output_schema
        if output_schema not in self.schema_compatibility:
            self.schema_compatibility[output_schema] = []
        
        # Find agents that can consume this output
        for other_id, other_def in self.registered_agents.items():
            if other_def.input_schema == output_schema:
                self.schema_compatibility[output_schema].append(other_id)
    
    def find_agents_by_capability(self, capability: AgentCapability) -> List[str]:
        """Find all agents with specified capability"""
        return self.capability_index.get(capability, [])
    
    def find_compatible_agents(self, output_schema: str) -> List[str]:
        """Find agents compatible with given output schema"""
        return self.schema_compatibility.get(output_schema, [])
    
    async def instantiate_agent(self, agent_id: str, configuration_overrides: Dict[str, Any] = None) -> Any:
        """Dynamically instantiate an agent from its definition"""
        
        if agent_id not in self.registered_agents:
            raise ValueError(f"Agent {agent_id} not registered")
        
        definition = self.registered_agents[agent_id]
        
        # Load agent class dynamically
        module = importlib.import_module(definition.module_path)
        agent_class = getattr(module, definition.agent_class)
        
        # Merge configurations
        config = definition.configuration.copy()
        if configuration_overrides:
            config.update(configuration_overrides)
        
        # Instantiate agent
        return agent_class(**config)
    
    def suggest_pipeline(self, start_capability: AgentCapability, 
                        end_capability: AgentCapability) -> List[str]:
        """Suggest agent pipeline from start to end capability"""
        
        start_agents = self.find_agents_by_capability(start_capability)
        end_agents = self.find_agents_by_capability(end_capability)
        
        # Simple pipeline suggestion (could be enhanced with graph algorithms)
        pipeline_suggestions = []
        
        for start_agent_id in start_agents:
            start_def = self.registered_agents[start_agent_id]
            compatible_agents = self.find_compatible_agents(start_def.output_schema)
            
            for middle_agent_id in compatible_agents:
                middle_def = self.registered_agents[middle_agent_id]
                if end_capability in middle_def.capabilities:
                    pipeline_suggestions.append([start_agent_id, middle_agent_id])
                else:
                    # Look for one more hop
                    final_compatible = self.find_compatible_agents(middle_def.output_schema)
                    for end_agent_id in final_compatible:
                        end_def = self.registered_agents[end_agent_id]
                        if end_capability in end_def.capabilities:
                            pipeline_suggestions.append([start_agent_id, middle_agent_id, end_agent_id])
        
        return pipeline_suggestions

class AtomicCLI:
    """Advanced CLI for atomic agent management and DevOps integration"""
    
    def __init__(self, config_path: str = "atomic_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.agent_registry = DynamicAgentRegistry()
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load atomic agent configuration with schema validation"""
        
        default_config = {
            "agents": {},
            "pipelines": {},
            "providers": {},
            "cli_settings": {
                "log_level": "INFO",
                "output_format": "json",
                "auto_save": True
            },
            "monitoring": {
                "enabled": True,
                "metrics_retention_days": 7,
                "performance_alerts": True
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                return default_config
        else:
            return default_config
    
    def register_builtin_agents(self):
        """Register common atomic agent types"""
        
        # Task Processing Agent
        self.agent_registry.register_agent("task_processor", AgentDefinition(
            agent_class="TaskProcessorAgent",
            module_path="atomic_agents.task_processor",
            capabilities=[AgentCapability.TASK_PROCESSING],
            input_schema="TaskInput",
            output_schema="TaskOutput",
            configuration={"model": "gpt-4o-mini", "temperature": 0.3},
            resource_requirements={"memory_mb": 512, "cpu_cores": 1}
        ))
        
        # Content Analysis Agent
        self.agent_registry.register_agent("content_analyzer", AgentDefinition(
            agent_class="ContentAnalysisAgent",
            module_path="atomic_agents.content_analysis",
            capabilities=[AgentCapability.CONTENT_ANALYSIS],
            input_schema="AnalysisInput",
            output_schema="AnalysisOutput",
            configuration={"model": "gpt-4o", "temperature": 0.1},
            resource_requirements={"memory_mb": 1024, "cpu_cores": 1}
        ))
        
        # Data Transformer Agent
        self.agent_registry.register_agent("data_transformer", AgentDefinition(
            agent_class="DataTransformerAgent",
            module_path="atomic_agents.data_transformer",
            capabilities=[AgentCapability.DATA_TRANSFORMATION],
            input_schema="TransformInput",
            output_schema="TransformOutput",
            configuration={"model": "gpt-4o-mini", "temperature": 0.0},
            resource_requirements={"memory_mb": 256, "cpu_cores": 1}
        ))
    
    async def create_dynamic_pipeline(self, capability_sequence: List[AgentCapability]) -> AdvancedAtomicPipeline:
        """Create pipeline dynamically based on capability requirements"""
        
        if len(capability_sequence) < 2:
            raise ValueError("Pipeline requires at least 2 capabilities")
        
        pipeline = AdvancedAtomicPipeline(f"dynamic_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Find agents for each capability
        selected_agents = []
        for i, capability in enumerate(capability_sequence):
            candidates = self.agent_registry.find_agents_by_capability(capability)
            
            if not candidates:
                raise ValueError(f"No agents found for capability: {capability}")
            
            # Select best agent (could use more sophisticated selection logic)
            selected_agent_id = candidates[0]  # Simple: pick first
            
            # Validate schema compatibility with previous agent
            if i > 0:
                prev_agent_def = self.agent_registry.registered_agents[selected_agents[-1]]
                current_agent_def = self.agent_registry.registered_agents[selected_agent_id]
                
                if prev_agent_def.output_schema != current_agent_def.input_schema:
                    # Try to find compatible agent
                    compatible_agents = self.agent_registry.find_compatible_agents(prev_agent_def.output_schema)
                    capability_compatible = [
                        agent_id for agent_id in compatible_agents
                        if capability in self.agent_registry.registered_agents[agent_id].capabilities
                    ]
                    
                    if capability_compatible:
                        selected_agent_id = capability_compatible[0]
                    else:
                        raise ValueError(f"No schema-compatible agents found for {capability}")
            
            selected_agents.append(selected_agent_id)
        
        # Instantiate agents and add to pipeline
        for i, agent_id in enumerate(selected_agents):
            agent_instance = await self.agent_registry.instantiate_agent(agent_id)
            
            stage = PipelineStage(
                stage_id=f"stage_{i}_{agent_id}",
                agent=agent_instance,
                stage_name=f"Stage {i+1}: {agent_id}",
                description=f"Process using {agent_id} agent",
                error_policy="retry",
                retry_count=2
            )
            
            pipeline.add_stage(stage)
        
        return pipeline
```

---

## 🎯 Module Summary

You've now mastered advanced atomic agent composition patterns:

✅ **Pipeline Orchestration**: Built sophisticated sequential processing with error handling and monitoring  
✅ **Parallel Processing**: Implemented load-balanced parallel execution with fault tolerance  
✅ **Dynamic Assembly**: Created runtime agent composition systems with capability-based selection  
✅ **CLI Integration**: Designed DevOps-friendly command-line tools for atomic agent management

### Next Steps
- **Continue to Module B**: [Enterprise Modular Systems](Session6_ModuleB_Enterprise_Modular_Systems.md) for production-scale architectures
- **Return to Core**: [Session 6 Main](Session6_Atomic_Agents_Modular_Architecture.md)
- **Advance to Session 7**: [First ADK Agent](Session7_First_ADK_Agent.md)

---

**🗂️ Source Files for Module A:**
- `src/session6/advanced_composition.py` - Sophisticated pipeline patterns
- `src/session6/dynamic_assembly.py` - Runtime composition systems
- `src/session6/atomic_cli.py` - DevOps CLI integration