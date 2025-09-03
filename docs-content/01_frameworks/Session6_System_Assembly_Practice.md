# 📝 Session 6: System Assembly Practice

> **📝 PARTICIPANT PATH CONTENT**
> Prerequisites: Complete 🎯 [Architecture Essentials](Session6_Atomic_Architecture_Essentials.md) and 📝 [Building Components](Session6_Building_Atomic_Components.md)
> Time Investment: 1.5-2 hours
> Outcome: Assemble atomic components into complete data processing systems

## Learning Outcomes

After completing this module, you will be able to:

- Assemble atomic components into integrated data processing systems  
- Design component communication patterns for data flow  
- Implement coordination logic for multi-agent workflows  
- Test and validate complete system integration  

## System Assembly Fundamentals

Building complete data processing systems from atomic components requires careful coordination and clear communication patterns. Let's explore how to assemble components that work together seamlessly.

### Basic Assembly Patterns

The simplest way to assemble atomic components is through direct coordination where one component manages the interaction between others:

```python
class BasicDataProcessingSystem:
    """Simple assembly of atomic components for data processing"""

    def __init__(self):
        # Initialize our atomic components
        self.ingestion_agent = self._create_ingestion_agent()
        self.transform_agent = self._create_transform_agent()
        self.validation_agent = self._create_validation_agent()

    def _create_ingestion_agent(self):
        """Create data ingestion specialist"""
        return BaseAgent(
            agent_name="data_ingestion_specialist",
            system_prompt="Expert at data ingestion and initial processing",
            memory=ChatMemory(max_messages=10),
            tools=[]
        )

    def _create_transform_agent(self):
        """Create data transformation specialist"""
        return BaseAgent(
            agent_name="data_transformation_specialist",
            system_prompt="Specialized in data format conversion and mapping",
            memory=None,  # Stateless for efficiency
            tools=[]
        )

    def _create_validation_agent(self):
        """Create data validation specialist"""
        return BaseAgent(
            agent_name="data_validation_specialist",
            system_prompt="Ensure data quality and schema compliance",
            memory=ChatMemory(max_messages=5),
            tools=[]
        )
```

This basic assembly creates specialized agents for different processing stages, each focused on their specific responsibility.

### Sequential Processing Workflow

Let's implement a sequential workflow that processes data through each component in order:

```python
def process_data_pipeline(self, raw_data: str, target_schema: str) -> Dict:
    """Process data through sequential pipeline stages"""

    workflow_state = {
        "input": raw_data,
        "target_schema": target_schema,
        "processing_stages": [],
        "current_data": raw_data
    }

    # Stage 1: Data ingestion and initial processing
    ingestion_result = self.ingestion_agent.run(
        f"Process raw data for ingestion: {raw_data[:200]}"
    )
    workflow_state["processing_stages"].append({
        "stage": "ingestion",
        "result": ingestion_result,
        "status": "completed"
    })
    workflow_state["current_data"] = ingestion_result

    # Stage 2: Data transformation
    transform_prompt = f"Transform data to schema:\nData: {workflow_state['current_data'][:200]}\nTarget: {target_schema}"
    transform_result = self.transform_agent.run(transform_prompt)
    workflow_state["processing_stages"].append({
        "stage": "transformation",
        "result": transform_result,
        "status": "completed"
    })
    workflow_state["current_data"] = transform_result

    return workflow_state
```

This sequential approach ensures data flows through each processing stage in a controlled manner, with each stage building on the previous stage's output.

### Parallel Processing Assembly

For higher throughput, we can process different aspects of data in parallel:

```python
import asyncio
from typing import List, Dict, Any

class ParallelDataProcessingSystem:
    """Assembly pattern for parallel data processing"""

    def __init__(self):
        self.processing_agents = {
            "quality_check": self._create_quality_agent(),
            "format_converter": self._create_format_agent(),
            "metadata_extractor": self._create_metadata_agent()
        }

    async def process_parallel(self, data_items: List[str]) -> Dict:
        """Process multiple data items in parallel"""

        async def process_single_item(item: str, agent_type: str):
            """Process single data item with specific agent"""
            agent = self.processing_agents[agent_type]
            result = agent.run(f"Process data item: {item}")
            return {"agent": agent_type, "input": item, "result": result}

        # Create parallel processing tasks
        tasks = []
        for item in data_items:
            for agent_type in self.processing_agents.keys():
                tasks.append(process_single_item(item, agent_type))

        # Execute all tasks in parallel
        parallel_results = await asyncio.gather(*tasks)

        return {
            "processing_mode": "parallel",
            "total_tasks": len(tasks),
            "results": parallel_results,
            "status": "completed"
        }
```

This parallel processing system demonstrates how atomic components can work simultaneously on different aspects of data processing, improving overall throughput.

### Component Communication Patterns

For complex systems, components need to communicate with each other. Here's a pattern for inter-component communication:

```python
class ComponentCommunicationSystem:
    """System with inter-component communication patterns"""

    def __init__(self):
        self.components = {}
        self.communication_log = []
        self.shared_context = {}

    def register_component(self, name: str, agent: BaseAgent):
        """Register a component in the system"""
        self.components[name] = agent
        self.shared_context[name] = {"status": "ready", "last_result": None}

    def send_message(self, from_component: str, to_component: str, message: str):
        """Send message between components"""
        self.communication_log.append({
            "from": from_component,
            "to": to_component,
            "message": message,
            "timestamp": "current_time"
        })

        # Process message with target component
        if to_component in self.components:
            result = self.components[to_component].run(
                f"Message from {from_component}: {message}"
            )
            self.shared_context[to_component]["last_result"] = result
            return result

        return None

    def coordinate_processing(self, data: str) -> Dict:
        """Coordinate processing across multiple components"""
        coordination_results = {}

        # Component 1 processes initial data
        if "processor_a" in self.components:
            result_a = self.components["processor_a"].run(
                f"Initial processing: {data}"
            )
            coordination_results["processor_a"] = result_a
            self.shared_context["processor_a"]["last_result"] = result_a

        # Component 2 processes based on Component 1's result
        if "processor_b" in self.components and "processor_a" in coordination_results:
            context_info = f"Previous result: {coordination_results['processor_a'][:100]}"
            result_b = self.components["processor_b"].run(
                f"Secondary processing with context: {context_info}"
            )
            coordination_results["processor_b"] = result_b

        return {
            "coordination_complete": True,
            "results": coordination_results,
            "communication_log": self.communication_log,
            "shared_context": self.shared_context
        }
```

This communication system allows components to share information and coordinate their processing efforts.

### Integration Testing Framework

Testing assembled systems requires validating both individual components and their integration:

```python
class SystemIntegrationTester:
    """Framework for testing assembled atomic systems"""

    def __init__(self, system_under_test):
        self.system = system_under_test
        self.test_results = []

    def test_component_integration(self):
        """Test that components work together correctly"""
        test_data = "Test data payload for integration testing"

        try:
            # Test basic system processing
            result = self.system.process_data_pipeline(test_data, "test_schema")

            # Validate integration points
            assert "processing_stages" in result
            assert len(result["processing_stages"]) > 0
            assert result["processing_stages"][-1]["status"] == "completed"

            self.test_results.append({
                "test": "component_integration",
                "status": "passed",
                "details": "Components integrate successfully"
            })

        except Exception as e:
            self.test_results.append({
                "test": "component_integration",
                "status": "failed",
                "error": str(e)
            })

    def test_data_flow(self):
        """Test data flows correctly between components"""
        test_cases = [
            {"input": "simple data", "schema": "basic_schema"},
            {"input": "complex data structure", "schema": "advanced_schema"},
            {"input": "", "schema": "empty_handling_schema"}
        ]

        for test_case in test_cases:
            try:
                result = self.system.process_data_pipeline(
                    test_case["input"], test_case["schema"]
                )

                # Verify data transformation chain
                assert "current_data" in result
                assert result["current_data"] != test_case["input"]  # Data was processed

                self.test_results.append({
                    "test": f"data_flow_{test_case['schema']}",
                    "status": "passed"
                })

            except Exception as e:
                self.test_results.append({
                    "test": f"data_flow_{test_case['schema']}",
                    "status": "failed",
                    "error": str(e)
                })

    def get_test_summary(self) -> Dict:
        """Get comprehensive test summary"""
        passed = [r for r in self.test_results if r["status"] == "passed"]
        failed = [r for r in self.test_results if r["status"] == "failed"]

        return {
            "total_tests": len(self.test_results),
            "passed": len(passed),
            "failed": len(failed),
            "success_rate": len(passed) / len(self.test_results) if self.test_results else 0,
            "detailed_results": self.test_results
        }
```

This testing framework validates that your assembled system works correctly at both the component and integration levels.

### Production-Ready Assembly Example

Here's a complete example of a production-ready system assembly:

**File**: [`src/session6/production_system_assembly.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/01_frameworks/src/session6/production_system_assembly.py)

```python
class ProductionDataProcessingSystem:
    """Production-ready assembly of atomic agents"""

    def __init__(self, config: Dict):
        self.config = config
        self.components = self._initialize_components()
        self.metrics = {"processed_items": 0, "errors": 0, "uptime": "start_time"}

    def _initialize_components(self):
        """Initialize all system components with production configuration"""
        return {
            "ingestion": BaseAgent(
                agent_name="production_ingestion",
                system_prompt="Production data ingestion with error handling",
                memory=ChatMemory(max_messages=self.config.get("memory_limit", 20)),
                max_tokens=self.config.get("max_tokens", 500)
            ),
            "validation": BaseAgent(
                agent_name="production_validation",
                system_prompt="Production data validation with quality metrics",
                memory=None,  # Stateless for performance
                max_tokens=300
            ),
            "transformation": BaseAgent(
                agent_name="production_transformation",
                system_prompt="Production data transformation with monitoring",
                memory=None,
                max_tokens=400
            )
        }

    def process_with_monitoring(self, data: str) -> Dict:
        """Process data with comprehensive monitoring"""
        processing_id = f"proc_{hash(data)}"
        start_time = "current_timestamp"

        try:
            # Stage 1: Ingestion with error handling
            ingestion_result = self.components["ingestion"].run(
                f"Ingest and validate: {data[:200]}"
            )

            # Stage 2: Data validation
            validation_result = self.components["validation"].run(
                f"Validate processed data: {ingestion_result[:200]}"
            )

            # Stage 3: Final transformation
            final_result = self.components["transformation"].run(
                f"Final transform: {validation_result[:200]}"
            )

            # Update metrics
            self.metrics["processed_items"] += 1

            return {
                "processing_id": processing_id,
                "status": "success",
                "processing_time": "calculated_duration",
                "stages": {
                    "ingestion": {"status": "completed", "output_size": len(ingestion_result)},
                    "validation": {"status": "completed", "output_size": len(validation_result)},
                    "transformation": {"status": "completed", "output_size": len(final_result)}
                },
                "final_result": final_result,
                "metrics": self.metrics.copy()
            }

        except Exception as e:
            self.metrics["errors"] += 1
            return {
                "processing_id": processing_id,
                "status": "error",
                "error": str(e),
                "metrics": self.metrics.copy()
            }

    def health_check(self) -> Dict:
        """System health check for monitoring"""
        return {
            "system_status": "healthy",
            "components": {name: "operational" for name in self.components.keys()},
            "metrics": self.metrics,
            "configuration": {
                "memory_limit": self.config.get("memory_limit", 20),
                "max_tokens": self.config.get("max_tokens", 500)
            }
        }
```

This production system includes error handling, monitoring, and health checks essential for real-world deployment.

## Hands-On Assembly Exercise

Now it's time to practice system assembly. Build your own assembled system using this framework:

```python
class MyDataProcessingSystem:
    """Your custom assembled data processing system"""

    def __init__(self):
        # Initialize your components here
        self.components = {}
        self.setup_components()

    def setup_components(self):
        """Set up your atomic components"""
        # Add your component initialization here
        pass

    def process_data(self, input_data: Any) -> Any:
        """Your main processing workflow"""
        # Implement your data processing pipeline here
        pass

    def validate_system(self) -> bool:
        """Validate your system is working correctly"""
        # Add system validation logic here
        pass
```

### Assembly Best Practices

When assembling atomic systems, follow these best practices:

#### Component Coordination  
- **Clear Interfaces**: Each component should have well-defined input/output contracts  
- **Error Handling**: Handle failures gracefully without cascading to other components  
- **State Management**: Keep components stateless when possible for better scalability  

#### Data Flow Design  
- **Schema Consistency**: Ensure data schemas are compatible between components  
- **Validation Points**: Add validation at each stage to catch issues early  
- **Transformation Tracking**: Track how data changes through the pipeline  

#### Monitoring and Observability  
- **Metrics Collection**: Track processing times, error rates, and throughput  
- **Health Checks**: Implement health checks for each component  
- **Logging**: Log important processing events for debugging and monitoring  

## Testing Your Assembly

Use this testing checklist to validate your assembled system:

- [ ] Individual components work correctly in isolation  
- [ ] Components integrate properly with expected data flow  
- [ ] Error handling works correctly when components fail  
- [ ] System performance meets requirements under normal load  
- [ ] Monitoring and health checks function properly  
- [ ] System can be deployed and managed in production  

## Common Assembly Patterns

### Pipeline Pattern
Sequential processing where each component feeds the next:
Data → Component A → Component B → Component C → Result

### Fork-Join Pattern
Parallel processing that recombines results:
Data → [Component A, Component B, Component C] → Combine → Result

### Event-Driven Pattern
Components respond to events and trigger other components:
Event → Component A → Trigger → Component B → Process → Result

## Next Steps

With system assembly mastered, you're ready to explore advanced topics:

- ⚙️ [Advanced Orchestration](Session6_Advanced_Orchestration.md) - Complex workflow patterns and dynamic assembly  
- ⚙️ [Production Deployment](Session6_Production_Deployment.md) - Enterprise deployment and scaling strategies  

Or dive into specialized advanced modules:

- ⚙️ [Module A: Advanced Composition Patterns](Session6_ModuleA_Advanced_Composition_Patterns.md)  
- ⚙️ [Module B: Enterprise Modular Systems](Session6_ModuleB_Enterprise_Modular_Systems.md)  
---

**Next:** [Session 7 - First ADK Agent →](Session7_First_ADK_Agent.md)

---
