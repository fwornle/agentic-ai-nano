# src/session6/demo_runner_course.py
"""
Comprehensive demo runner for Atomic Agents modular architecture.
Demonstrates all key concepts from Session 6 with practical examples.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, List
import sys
import traceback

# Import course implementations
from atomic_agents_course import (
    # Core architecture
    AtomicContext, AtomicResult, AtomicAgent,
    TextProcessorAgent, DataValidationAgent,
    TextProcessingInput, DataValidationInput,
    AtomicPipeline, AtomicParallelExecutor,
    atomic_registry,
    
    # Demo functions
    demonstrate_basic_atomic_agent,
    demonstrate_data_validation,
    demonstrate_pipeline_composition,
    demonstrate_parallel_execution,
    demonstrate_atomic_registry
)

from modular_composition_course import (
    # Advanced composition patterns
    AdaptiveOrchestrator, ConditionalRouter, CompositionStrategy,
    DynamicSystemAssembler, SystemBlueprint, AssembledSystem,
    
    # Demo functions
    demonstrate_adaptive_orchestration,
    demonstrate_dynamic_system_assembly,
    demonstrate_conditional_routing
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DemoScenario:
    """Base class for demo scenarios."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.results: Dict[str, Any] = {}
    
    async def run(self) -> Dict[str, Any]:
        """Run the demo scenario."""
        logger.info(f"Starting scenario: {self.name}")
        start_time = datetime.now()
        
        try:
            await self.execute()
            self.results['status'] = 'success'
        except Exception as e:
            self.results['status'] = 'failed'
            self.results['error'] = str(e)
            self.results['traceback'] = traceback.format_exc()
            logger.error(f"Scenario {self.name} failed: {e}")
        
        self.results['execution_time'] = (datetime.now() - start_time).total_seconds()
        logger.info(f"Completed scenario: {self.name} ({self.results['status']})")
        
        return self.results
    
    async def execute(self):
        """Override in subclasses."""
        raise NotImplementedError

class AtomicArchitectureScenario(DemoScenario):
    """Demonstrate core atomic architecture principles."""
    
    def __init__(self):
        super().__init__(
            "Atomic Architecture Principles",
            "Single responsibility, composability, and modular design"
        )
    
    async def execute(self):
        print(f"\n🎯 {self.name}")
        print("=" * 50)
        
        print("\n1. Single Responsibility Demonstration")
        print("-" * 40)
        
        # Create agents with single responsibilities
        text_agent = TextProcessorAgent()
        validator_agent = DataValidationAgent()
        
        # Show each agent's specific capabilities
        print(f"✅ Text Processor Agent: {text_agent.agent_id}")
        print(f"   Single Responsibility: Text processing operations only")
        print(f"   Supported Operations: summarize, extract_keywords, sentiment, word_count")
        
        print(f"✅ Data Validator Agent: {validator_agent.agent_id}")
        print(f"   Single Responsibility: Data validation operations only") 
        print(f"   Supported Validations: basic, schema, range, format, completeness")
        
        # Demonstrate focused execution
        context = AtomicContext(user_id="architecture_demo")
        
        # Text processing - stays in domain
        text_input = TextProcessingInput(
            content="Atomic agents provide focused, composable intelligence",
            operation="extract_keywords"
        )
        
        text_result = await text_agent._execute_with_metrics(text_input, context)
        
        print(f"\n✅ Text Processing Result:")
        print(f"   Keywords: {text_result.data.result if text_result.success else text_result.error}")
        print(f"   Processing Time: {text_result.processing_time_ms:.1f}ms")
        
        # Data validation - stays in domain
        validation_input = DataValidationInput(
            data={"id": 123, "name": "Test User"},
            validation_type="schema"
        )
        
        validation_result = await validator_agent._execute_with_metrics(validation_input, context)
        
        print(f"\n✅ Data Validation Result:")
        if validation_result.success:
            output = validation_result.data
            print(f"   Valid: {output.is_valid}")
            print(f"   Errors: {output.errors}")
            print(f"   Warnings: {output.warnings}")
        print(f"   Processing Time: {validation_result.processing_time_ms:.1f}ms")
        
        self.results['agents_demonstrated'] = 2
        self.results['single_responsibility'] = True
        
        print("\n2. Composability Demonstration")
        print("-" * 30)
        
        # Show how agents compose without tight coupling
        pipeline = AtomicPipeline("architecture_demo_pipeline")
        pipeline.add_agent(text_agent)
        pipeline.add_agent(validator_agent)
        
        # Compose different types of agents
        composite_result = await pipeline.execute(text_input, context)
        
        print(f"✅ Composite Pipeline Execution:")
        print(f"   Success: {composite_result.success}")
        print(f"   Agents Composed: {len(pipeline.agents)}")
        print(f"   Total Processing Time: {composite_result.processing_time_ms:.1f}ms")
        
        self.results['composability_demonstrated'] = True
        self.results['pipeline_executed'] = True
        
        print("\n3. Modular Metrics")
        print("-" * 20)
        
        # Show individual agent metrics
        text_metrics = text_agent.get_metrics()
        validator_metrics = validator_agent.get_metrics()
        
        print(f"✅ Text Agent Metrics:")
        print(f"   Executions: {text_metrics['execution_count']}")
        print(f"   Success Rate: {text_metrics['success_rate']:.1%}")
        
        print(f"✅ Validator Agent Metrics:")
        print(f"   Executions: {validator_metrics['execution_count']}")
        print(f"   Success Rate: {validator_metrics['success_rate']:.1%}")
        
        self.results['metrics_collected'] = True

class CompositionPatternsScenario(DemoScenario):
    """Demonstrate advanced composition patterns."""
    
    def __init__(self):
        super().__init__(
            "Advanced Composition Patterns",
            "Sequential, parallel, conditional, and adaptive composition"
        )
    
    async def execute(self):
        print(f"\n🎯 {self.name}")
        print("=" * 50)
        
        orchestrator = AdaptiveOrchestrator()
        orchestrator.auto_register_agents()
        
        composition_results = []
        
        print("\n1. Sequential Composition")
        print("-" * 25)
        
        # Long text triggers sequential processing
        long_text_input = TextProcessingInput(
            content="Sequential composition allows atomic agents to work together in a coordinated manner. Each agent processes the data and passes results to the next agent in the chain. This pattern is ideal for complex transformations that require multiple steps. The modular design ensures that each step can be developed, tested, and maintained independently while still working together seamlessly.",
            operation="summarize"
        )
        
        context = AtomicContext(user_id="composition_demo")
        sequential_result = await orchestrator.execute(long_text_input, context)
        
        print(f"✅ Sequential Processing:")
        print(f"   Strategy: {sequential_result.metadata.get('composition_strategy')}")
        print(f"   Processing Time: {sequential_result.metadata.get('total_orchestration_time_ms', 0):.1f}ms")
        print(f"   Success: {sequential_result.success}")
        
        composition_results.append(('sequential', sequential_result.success))
        
        print("\n2. Parallel Composition") 
        print("-" * 22)
        
        # Multiple tasks for parallel execution
        parallel_tasks = [
            (TextProcessorAgent(), TextProcessingInput(content="Great news!", operation="sentiment")),
            (TextProcessorAgent(), TextProcessingInput(content="Bad news.", operation="sentiment")),
            (TextProcessorAgent(), TextProcessingInput(content="Neutral information.", operation="sentiment"))
        ]
        
        executor = AtomicParallelExecutor(max_concurrent=3)
        parallel_results = await executor.execute_parallel(parallel_tasks, context)
        
        print(f"✅ Parallel Processing:")
        print(f"   Tasks Executed: {len(parallel_tasks)}")
        print(f"   Successful: {sum(1 for r in parallel_results if r.success)}")
        
        for i, result in enumerate(parallel_results):
            if result.success and hasattr(result.data, 'result'):
                print(f"   Task {i+1}: {result.data.result} ({result.processing_time_ms:.1f}ms)")
        
        composition_results.append(('parallel', all(r.success for r in parallel_results)))
        
        print("\n3. Adaptive Composition")
        print("-" * 22)
        
        # Test adaptive strategy selection
        adaptive_inputs = [
            TextProcessingInput(content="Simple sentiment test", operation="sentiment"),
            TextProcessingInput(content="Word counting test", operation="word_count")
        ]
        
        adaptive_results = []
        for i, test_input in enumerate(adaptive_inputs):
            adaptive_context = AtomicContext(user_id=f"adaptive_{i}")
            result = await orchestrator.execute(test_input, adaptive_context)
            adaptive_results.append(result)
            
            print(f"✅ Adaptive Test {i+1}:")
            print(f"   Strategy: {result.metadata.get('composition_strategy')}")
            print(f"   Success: {result.success}")
        
        composition_results.append(('adaptive', all(r.success for r in adaptive_results)))
        
        # Analytics
        analytics = orchestrator.get_performance_analytics()
        print(f"\n📊 Composition Analytics:")
        print(f"   Strategies Used: {len(analytics['strategies_used'])}")
        print(f"   Total Executions: {analytics['total_executions']}")
        
        self.results['composition_patterns'] = len(composition_results)
        self.results['patterns_successful'] = sum(1 for _, success in composition_results if success)
        self.results['analytics'] = analytics

class DynamicSystemsScenario(DemoScenario):
    """Demonstrate dynamic system assembly and management."""
    
    def __init__(self):
        super().__init__(
            "Dynamic System Assembly",
            "Blueprint-driven system composition and runtime assembly"
        )
    
    async def execute(self):
        print(f"\n🎯 {self.name}")
        print("=" * 50)
        
        print("\n1. System Blueprint Creation")
        print("-" * 30)
        
        # Create multiple system blueprints
        blueprints = []
        
        # Text analysis system blueprint
        text_blueprint = SystemBlueprint("text_analysis_system")
        text_blueprint.add_component("analyzer", "text_processor", {"agent_id": "text_analyzer_1"})
        text_blueprint.add_component("validator", "data_validator", {"agent_id": "result_validator_1"})
        text_blueprint.connect("analyzer", "validator")
        text_blueprint.set_configuration("timeout_ms", 3000)
        
        blueprints.append(text_blueprint)
        
        # Quality assurance system blueprint
        qa_blueprint = SystemBlueprint("qa_system")
        qa_blueprint.add_component("primary_qa", "data_validator")
        qa_blueprint.add_component("secondary_qa", "data_validator")
        qa_blueprint.add_component("processor", "text_processor")
        qa_blueprint.connect("primary_qa", "secondary_qa")
        qa_blueprint.connect("secondary_qa", "processor")
        qa_blueprint.set_configuration("strict_validation", True)
        
        blueprints.append(qa_blueprint)
        
        print(f"✅ Created {len(blueprints)} system blueprints")
        for blueprint in blueprints:
            print(f"   - {blueprint.name}: {len(blueprint.components)} components")
        
        print("\n2. Dynamic System Assembly")
        print("-" * 30)
        
        assembler = DynamicSystemAssembler()
        
        # Register blueprints
        for blueprint in blueprints:
            assembler.register_blueprint(blueprint)
        
        print(f"✅ Registered blueprints: {assembler.get_blueprints()}")
        
        # Assemble systems
        assembled_systems = []
        for blueprint in blueprints:
            system = assembler.assemble_system(blueprint.name)
            assembled_systems.append(system)
            print(f"✅ Assembled: {system.system_id}")
        
        print(f"✅ Total assembled systems: {len(assembled_systems)}")
        
        print("\n3. System Execution")
        print("-" * 20)
        
        # Execute assembled systems
        execution_results = []
        context = AtomicContext(user_id="dynamic_demo")
        
        # Test text analysis system
        text_system = assembled_systems[0]
        text_input = TextProcessingInput(
            content="Dynamic system assembly enables flexible architecture",
            operation="extract_keywords"
        )
        
        text_result = await text_system.execute(text_input, context)
        execution_results.append(('text_analysis', text_result.success))
        
        print(f"✅ Text Analysis System:")
        print(f"   Success: {text_result.success}")
        print(f"   System Time: {text_result.metadata.get('system_execution_time_ms', 0):.1f}ms")
        
        if text_result.success and hasattr(text_result.data, 'result'):
            print(f"   Result: {text_result.data.result}")
        
        # Test QA system  
        qa_system = assembled_systems[1]
        qa_input = DataValidationInput(
            data={"id": 456, "name": "QA Test", "status": "active"},
            validation_type="schema"
        )
        
        qa_result = await qa_system.execute(qa_input, context)
        execution_results.append(('qa_system', qa_result.success))
        
        print(f"✅ QA System:")
        print(f"   Success: {qa_result.success}")
        print(f"   System Time: {qa_result.metadata.get('system_execution_time_ms', 0):.1f}ms")
        
        print("\n4. System Information")
        print("-" * 20)
        
        for system in assembled_systems:
            info = system.get_system_info()
            print(f"✅ System: {info['system_id']}")
            print(f"   Blueprint: {info['blueprint_name']}")
            print(f"   Components: {info['component_count']}")
            print(f"   Connections: {info['connection_count']}")
            print(f"   Executions: {info['executions']}")
        
        self.results['blueprints_created'] = len(blueprints)
        self.results['systems_assembled'] = len(assembled_systems)
        self.results['executions_successful'] = sum(1 for _, success in execution_results if success)
        self.results['total_executions'] = len(execution_results)

class PerformanceOptimizationScenario(DemoScenario):
    """Demonstrate performance optimization and monitoring."""
    
    def __init__(self):
        super().__init__(
            "Performance Optimization",
            "Metrics collection, performance analysis, and optimization strategies"
        )
    
    async def execute(self):
        print(f"\n🎯 {self.name}")
        print("=" * 50)
        
        print("\n1. Performance Baseline")
        print("-" * 25)
        
        # Create test agents
        text_agent = TextProcessorAgent()
        validator_agent = DataValidationAgent()
        
        # Collect baseline metrics
        baseline_operations = 20
        context = AtomicContext(user_id="performance_demo")
        
        print(f"✅ Running {baseline_operations} operations for baseline...")
        
        # Text processing baseline
        for i in range(baseline_operations):
            text_input = TextProcessingInput(
                content=f"Performance test operation {i} with varying content length",
                operation="word_count" if i % 2 == 0 else "sentiment"
            )
            await text_agent._execute_with_metrics(text_input, context)
        
        # Validation baseline
        for i in range(baseline_operations):
            validation_input = DataValidationInput(
                data={"id": i, "name": f"Test_{i}", "value": i * 10},
                validation_type="basic" if i % 2 == 0 else "schema"
            )
            await validator_agent._execute_with_metrics(validation_input, context)
        
        text_metrics = text_agent.get_metrics()
        validator_metrics = validator_agent.get_metrics()
        
        print(f"✅ Text Agent Baseline:")
        print(f"   Executions: {text_metrics['execution_count']}")
        print(f"   Avg Time: {text_metrics['average_processing_time_ms']:.2f}ms")
        print(f"   Success Rate: {text_metrics['success_rate']:.1%}")
        
        print(f"✅ Validator Agent Baseline:")
        print(f"   Executions: {validator_metrics['execution_count']}")
        print(f"   Avg Time: {validator_metrics['average_processing_time_ms']:.2f}ms")
        print(f"   Success Rate: {validator_metrics['success_rate']:.1%}")
        
        print("\n2. Parallel Performance")
        print("-" * 23)
        
        # Test parallel execution performance
        parallel_tasks = [
            (TextProcessorAgent(), TextProcessingInput(content=f"Parallel test {i}", operation="word_count"))
            for i in range(10)
        ]
        
        start_time = datetime.now()
        executor = AtomicParallelExecutor(max_concurrent=5)
        parallel_results = await executor.execute_parallel(parallel_tasks, context)
        parallel_time = (datetime.now() - start_time).total_seconds() * 1000
        
        successful_parallel = sum(1 for r in parallel_results if r.success)
        
        print(f"✅ Parallel Execution:")
        print(f"   Tasks: {len(parallel_tasks)}")
        print(f"   Successful: {successful_parallel}")
        print(f"   Total Time: {parallel_time:.1f}ms")
        print(f"   Avg per Task: {parallel_time/len(parallel_tasks):.1f}ms")
        
        print("\n3. Pipeline Performance")
        print("-" * 23)
        
        # Test pipeline performance vs individual execution
        pipeline = AtomicPipeline("performance_pipeline")
        pipeline.add_agent(TextProcessorAgent())
        pipeline.add_agent(DataValidationAgent())
        
        # Execute pipeline multiple times
        pipeline_times = []
        for i in range(10):
            test_input = TextProcessingInput(
                content=f"Pipeline performance test {i}",
                operation="summarize"
            )
            
            pipeline_result = await pipeline.execute(test_input, context)
            if pipeline_result.success:
                pipeline_times.append(pipeline_result.processing_time_ms)
        
        pipeline_metrics = pipeline.get_metrics()
        
        print(f"✅ Pipeline Performance:")
        print(f"   Executions: {pipeline_metrics['total_executions']}")
        print(f"   Success Rate: {pipeline_metrics['success_rate']:.1%}")
        print(f"   Avg Time: {pipeline_metrics['average_processing_time_ms']:.2f}ms")
        
        if pipeline_times:
            print(f"   Min Time: {min(pipeline_times):.1f}ms")
            print(f"   Max Time: {max(pipeline_times):.1f}ms")
        
        print("\n4. Registry Performance")
        print("-" * 22)
        
        # Test agent registry performance
        registry_times = []
        
        for i in range(50):
            start = datetime.now()
            agent = atomic_registry.create_agent("text_processor")
            creation_time = (datetime.now() - start).total_seconds() * 1000
            registry_times.append(creation_time)
            
            # Test quick execution
            simple_input = TextProcessingInput(content="Registry test", operation="word_count")
            await agent._execute_with_metrics(simple_input, context)
        
        print(f"✅ Registry Performance:")
        print(f"   Agent Creations: {len(registry_times)}")
        print(f"   Avg Creation Time: {sum(registry_times)/len(registry_times):.2f}ms")
        print(f"   Min Creation Time: {min(registry_times):.2f}ms")
        print(f"   Max Creation Time: {max(registry_times):.2f}ms")
        
        # Registry metrics
        instance_metrics = atomic_registry.get_instance_metrics()
        print(f"   Total Instances: {len(instance_metrics)}")
        
        self.results['baseline_operations'] = baseline_operations * 2  # Both agents
        self.results['parallel_success_rate'] = successful_parallel / len(parallel_tasks)
        self.results['pipeline_executions'] = len(pipeline_times)
        self.results['registry_creations'] = len(registry_times)
        self.results['avg_creation_time_ms'] = sum(registry_times)/len(registry_times)

async def run_comprehensive_demo():
    """Run all demo scenarios comprehensively."""
    print("🚀 Atomic Agents Modular Architecture - Comprehensive Demo")
    print("=" * 60)
    print("\nThis demo showcases all key concepts from Session 6:")
    print("• Single responsibility and composable design")
    print("• Advanced composition patterns and orchestration")
    print("• Dynamic system assembly and blueprint management")
    print("• Performance optimization and monitoring")
    print("• Production-ready modular architecture patterns")
    
    scenarios = [
        AtomicArchitectureScenario(),
        CompositionPatternsScenario(),
        DynamicSystemsScenario(),
        PerformanceOptimizationScenario()
    ]
    
    demo_results = {
        'demo_start_time': datetime.now().isoformat(),
        'scenarios': [],
        'overall_stats': {}
    }
    
    for scenario in scenarios:
        result = await scenario.run()
        demo_results['scenarios'].append({
            'name': scenario.name,
            'description': scenario.description,
            'status': result['status'],
            'execution_time': result['execution_time'],
            'details': result
        })
    
    # Calculate overall statistics
    successful_scenarios = len([s for s in demo_results['scenarios'] if s['status'] == 'success'])
    total_execution_time = sum(s['execution_time'] for s in demo_results['scenarios'])
    
    demo_results['overall_stats'] = {
        'total_scenarios': len(scenarios),
        'successful_scenarios': successful_scenarios,
        'success_rate': successful_scenarios / len(scenarios) * 100,
        'total_execution_time': total_execution_time,
        'demo_end_time': datetime.now().isoformat()
    }
    
    print(f"\n🎯 Demo Complete!")
    print("=" * 30)
    print(f"Scenarios Run: {demo_results['overall_stats']['total_scenarios']}")
    print(f"Success Rate: {demo_results['overall_stats']['success_rate']:.1f}%")
    print(f"Total Execution Time: {demo_results['overall_stats']['total_execution_time']:.2f}s")
    
    print(f"\n📋 Scenario Summary:")
    for scenario in demo_results['scenarios']:
        status_icon = "✅" if scenario['status'] == 'success' else "❌"
        print(f"   {status_icon} {scenario['name']}: {scenario['status']} ({scenario['execution_time']:.2f}s)")
    
    print(f"\n🎓 Key Learning Outcomes Achieved:")
    print("• ✅ Single responsibility principle with focused atomic agents")
    print("• ✅ Composable architecture through clean interfaces")
    print("• ✅ Advanced orchestration with adaptive strategy selection")
    print("• ✅ Dynamic system assembly from reusable blueprints")
    print("• ✅ Performance monitoring and optimization patterns")
    print("• ✅ Production-ready modular architecture deployment")
    
    print(f"\n💡 Production Deployment Characteristics:")
    print("• Microservices-inspired atomic agent design")
    print("• Horizontal scaling through component replication")
    print("• Fault isolation through modular boundaries")
    print("• Dynamic topology adaptation based on workload")
    print("• Comprehensive metrics for performance optimization")
    print("• Blueprint-driven system deployment and management")
    
    return demo_results

if __name__ == "__main__":
    print("🎯 Starting Atomic Agents Modular Architecture Demo...")
    print("This comprehensive demo will showcase modular design principles.\n")
    
    try:
        demo_results = asyncio.run(run_comprehensive_demo())
        
        # Optional: Save results to file for analysis
        with open('atomic_demo_results.json', 'w') as f:
            json.dump(demo_results, f, indent=2, default=str)
        
        print(f"\n💾 Demo results saved to 'atomic_demo_results.json'")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)