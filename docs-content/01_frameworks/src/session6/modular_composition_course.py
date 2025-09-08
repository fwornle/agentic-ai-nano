# src/session6/modular_composition_course.py
"""
Advanced modular composition patterns for atomic agents.
Demonstrates sophisticated orchestration and dynamic system assembly.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid

# Import base atomic framework
from atomic_agents_course import (
    AtomicAgent, AtomicContext, AtomicResult, 
    TextProcessorAgent, DataValidationAgent,
    TextProcessingInput, DataValidationInput,
    atomic_registry
)

# Advanced Composition Patterns

class CompositionStrategy(Enum):
    """Different strategies for composing atomic agents."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ADAPTIVE = "adaptive"
    TREE = "tree"
    GRAPH = "graph"

@dataclass
class CompositionRule:
    """Rules for dynamic agent composition."""
    condition: Callable[[Any, AtomicContext], bool]
    strategy: CompositionStrategy
    agents: List[str]  # Agent names or types
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConditionalRouter:
    """Route execution based on data characteristics and context."""
    
    def __init__(self):
        self.rules: List[CompositionRule] = []
        self.default_strategy = CompositionStrategy.SEQUENTIAL
        self.execution_history: List[Dict[str, Any]] = []
    
    def add_rule(self, rule: CompositionRule) -> None:
        """Add a composition rule."""
        self.rules.append(rule)
    
    def add_simple_rule(
        self, 
        condition: Callable[[Any, AtomicContext], bool],
        strategy: CompositionStrategy,
        agent_types: List[str]
    ) -> None:
        """Add a simple composition rule."""
        rule = CompositionRule(
            condition=condition,
            strategy=strategy,
            agents=agent_types
        )
        self.rules.append(rule)
    
    async def route(self, input_data: Any, context: AtomicContext) -> Dict[str, Any]:
        """Determine the best composition strategy for the input."""
        
        # Evaluate each rule
        for rule in self.rules:
            try:
                if rule.condition(input_data, context):
                    return {
                        'strategy': rule.strategy,
                        'agents': rule.agents,
                        'rule_metadata': rule.metadata,
                        'matched': True
                    }
            except Exception as e:
                # Log rule evaluation error but continue
                context.add_metadata(f'rule_error_{rule.strategy.value}', str(e))
        
        # No rules matched, use default
        return {
            'strategy': self.default_strategy,
            'agents': ['text_processor'],  # Default fallback
            'rule_metadata': {},
            'matched': False
        }

class AdaptiveOrchestrator:
    """Orchestrate atomic agents with adaptive composition strategies."""
    
    def __init__(self):
        self.router = ConditionalRouter()
        self.execution_metrics: Dict[str, List[float]] = {}  # Strategy -> processing times
        self.agents: Dict[str, AtomicAgent] = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default composition rules."""
        
        # Text processing rules
        self.router.add_simple_rule(
            condition=lambda data, ctx: hasattr(data, 'content') and len(data.content) > 500,
            strategy=CompositionStrategy.SEQUENTIAL,
            agent_types=['text_processor', 'data_validator']
        )
        
        # Parallel processing for simple operations
        self.router.add_simple_rule(
            condition=lambda data, ctx: hasattr(data, 'operation') and data.operation in ['sentiment', 'word_count'],
            strategy=CompositionStrategy.PARALLEL,
            agent_types=['text_processor', 'text_processor']  # Same agent, different configs
        )
        
        # Data validation priority
        self.router.add_simple_rule(
            condition=lambda data, ctx: isinstance(data, dict) and 'validate_first' in ctx.metadata,
            strategy=CompositionStrategy.SEQUENTIAL,
            agent_types=['data_validator', 'text_processor']
        )
    
    def register_agent(self, agent_type: str, agent: AtomicAgent) -> None:
        """Register an atomic agent with the orchestrator."""
        self.agents[agent_type] = agent
    
    def auto_register_agents(self) -> None:
        """Automatically register common agent types."""
        self.register_agent('text_processor', TextProcessorAgent())
        self.register_agent('data_validator', DataValidationAgent())
    
    async def execute(self, input_data: Any, context: AtomicContext) -> AtomicResult:
        """Execute with adaptive composition."""
        
        start_time = time.time()
        
        # Determine composition strategy
        routing_decision = await self.router.route(input_data, context)
        strategy = routing_decision['strategy']
        agent_types = routing_decision['agents']
        
        # Ensure we have the required agents
        missing_agents = [agent_type for agent_type in agent_types if agent_type not in self.agents]
        if missing_agents:
            return AtomicResult(
                success=False,
                error=f"Missing required agents: {missing_agents}"
            )
        
        try:
            # Execute based on strategy
            if strategy == CompositionStrategy.SEQUENTIAL:
                result = await self._execute_sequential(agent_types, input_data, context)
            elif strategy == CompositionStrategy.PARALLEL:
                result = await self._execute_parallel(agent_types, input_data, context)
            elif strategy == CompositionStrategy.CONDITIONAL:
                result = await self._execute_conditional(agent_types, input_data, context)
            elif strategy == CompositionStrategy.ADAPTIVE:
                result = await self._execute_adaptive(agent_types, input_data, context)
            else:
                result = await self._execute_sequential(agent_types, input_data, context)
            
            # Record execution metrics
            execution_time = (time.time() - start_time) * 1000
            if strategy.value not in self.execution_metrics:
                self.execution_metrics[strategy.value] = []
            self.execution_metrics[strategy.value].append(execution_time)
            
            # Enhance result metadata
            result.metadata.update({
                'composition_strategy': strategy.value,
                'agents_used': agent_types,
                'routing_matched': routing_decision['matched'],
                'total_orchestration_time_ms': execution_time
            })
            
            return result
            
        except Exception as e:
            return AtomicResult(
                success=False,
                error=f"Orchestration failed: {e}",
                metadata={
                    'composition_strategy': strategy.value,
                    'agents_attempted': agent_types
                }
            )
    
    async def _execute_sequential(self, agent_types: List[str], input_data: Any, context: AtomicContext) -> AtomicResult:
        """Execute agents sequentially."""
        current_data = input_data
        
        for agent_type in agent_types:
            agent = self.agents[agent_type]
            result = await agent._execute_with_metrics(current_data, context)
            
            if not result.success:
                return result
            
            # Use output as input for next agent (if applicable)
            if result.data is not None:
                current_data = result.data
        
        return AtomicResult(
            success=True,
            data=current_data,
            metadata={'execution_type': 'sequential'}
        )
    
    async def _execute_parallel(self, agent_types: List[str], input_data: Any, context: AtomicContext) -> AtomicResult:
        """Execute agents in parallel."""
        
        # Create tasks for parallel execution
        tasks = []
        for agent_type in agent_types:
            agent = self.agents[agent_type]
            tasks.append(agent._execute_with_metrics(input_data, context))
        
        # Execute all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Agent {agent_types[i]}: {result}")
            elif result.success:
                successful_results.append(result.data)
            else:
                errors.append(f"Agent {agent_types[i]}: {result.error}")
        
        if errors and not successful_results:
            return AtomicResult(
                success=False,
                error=f"All parallel agents failed: {'; '.join(errors)}"
            )
        
        return AtomicResult(
            success=True,
            data=successful_results,
            metadata={
                'execution_type': 'parallel',
                'successful_agents': len(successful_results),
                'failed_agents': len(errors),
                'errors': errors if errors else None
            }
        )
    
    async def _execute_conditional(self, agent_types: List[str], input_data: Any, context: AtomicContext) -> AtomicResult:
        """Execute agents based on conditions."""
        
        # Simple conditional logic - can be extended
        if len(agent_types) >= 2:
            # Try first agent, if it fails, try second
            primary_agent = self.agents[agent_types[0]]
            result = await primary_agent._execute_with_metrics(input_data, context)
            
            if result.success:
                return result
            
            # Primary failed, try fallback
            fallback_agent = self.agents[agent_types[1]]
            fallback_result = await fallback_agent._execute_with_metrics(input_data, context)
            
            fallback_result.metadata.update({
                'execution_type': 'conditional_fallback',
                'primary_agent': agent_types[0],
                'primary_error': result.error
            })
            
            return fallback_result
        
        # Single agent - just execute
        agent = self.agents[agent_types[0]]
        return await agent._execute_with_metrics(input_data, context)
    
    async def _execute_adaptive(self, agent_types: List[str], input_data: Any, context: AtomicContext) -> AtomicResult:
        """Execute with adaptive strategy based on historical performance."""
        
        # Choose strategy based on historical performance
        best_strategy = self._get_best_performing_strategy()
        
        if best_strategy == CompositionStrategy.PARALLEL:
            return await self._execute_parallel(agent_types, input_data, context)
        else:
            return await self._execute_sequential(agent_types, input_data, context)
    
    def _get_best_performing_strategy(self) -> CompositionStrategy:
        """Get the best performing strategy based on metrics."""
        if not self.execution_metrics:
            return CompositionStrategy.SEQUENTIAL
        
        # Calculate average execution times
        strategy_averages = {}
        for strategy, times in self.execution_metrics.items():
            if times:
                strategy_averages[strategy] = sum(times) / len(times)
        
        if not strategy_averages:
            return CompositionStrategy.SEQUENTIAL
        
        # Return strategy with lowest average time
        best_strategy_name = min(strategy_averages, key=strategy_averages.get)
        return CompositionStrategy(best_strategy_name)
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive performance analytics."""
        
        analytics = {
            'strategies_used': list(self.execution_metrics.keys()),
            'total_executions': sum(len(times) for times in self.execution_metrics.values()),
            'strategy_performance': {}
        }
        
        for strategy, times in self.execution_metrics.items():
            if times:
                analytics['strategy_performance'][strategy] = {
                    'executions': len(times),
                    'average_time_ms': sum(times) / len(times),
                    'min_time_ms': min(times),
                    'max_time_ms': max(times),
                    'total_time_ms': sum(times)
                }
        
        return analytics

# Dynamic System Assembly

class SystemBlueprint:
    """Blueprint for dynamically assembling atomic agent systems."""
    
    def __init__(self, name: str):
        self.name = name
        self.components: Dict[str, Dict[str, Any]] = {}
        self.connections: List[Dict[str, str]] = []
        self.configuration: Dict[str, Any] = {}
    
    def add_component(self, component_id: str, agent_type: str, config: Dict[str, Any] = None) -> 'SystemBlueprint':
        """Add a component to the blueprint."""
        self.components[component_id] = {
            'agent_type': agent_type,
            'config': config or {},
            'connections': []
        }
        return self
    
    def connect(self, from_component: str, to_component: str, connection_type: str = "data_flow") -> 'SystemBlueprint':
        """Connect two components in the blueprint."""
        if from_component not in self.components or to_component not in self.components:
            raise ValueError(f"Components must be added before connecting")
        
        connection = {
            'from': from_component,
            'to': to_component,
            'type': connection_type
        }
        
        self.connections.append(connection)
        self.components[from_component]['connections'].append(connection)
        return self
    
    def set_configuration(self, key: str, value: Any) -> 'SystemBlueprint':
        """Set system-level configuration."""
        self.configuration[key] = value
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Export blueprint as dictionary."""
        return {
            'name': self.name,
            'components': self.components,
            'connections': self.connections,
            'configuration': self.configuration
        }

class DynamicSystemAssembler:
    """Assembles atomic agent systems from blueprints."""
    
    def __init__(self):
        self.assembled_systems: Dict[str, 'AssembledSystem'] = {}
        self.blueprints: Dict[str, SystemBlueprint] = {}
    
    def register_blueprint(self, blueprint: SystemBlueprint) -> None:
        """Register a system blueprint."""
        self.blueprints[blueprint.name] = blueprint
    
    def assemble_system(self, blueprint_name: str, system_id: str = None) -> 'AssembledSystem':
        """Assemble a system from a blueprint."""
        
        if blueprint_name not in self.blueprints:
            raise ValueError(f"Blueprint '{blueprint_name}' not found")
        
        blueprint = self.blueprints[blueprint_name]
        system_id = system_id or f"{blueprint_name}_{uuid.uuid4().hex[:8]}"
        
        # Create system instance
        system = AssembledSystem(system_id, blueprint)
        
        # Instantiate components
        for component_id, component_spec in blueprint.components.items():
            agent_type = component_spec['agent_type']
            config = component_spec['config']
            
            # Create agent instance
            if agent_type == 'text_processor':
                agent = TextProcessorAgent(**config)
            elif agent_type == 'data_validator':
                agent = DataValidationAgent(**config)
            else:
                # Try registry
                agent = atomic_registry.create_agent(agent_type, **config)
                if not agent:
                    raise ValueError(f"Unknown agent type: {agent_type}")
            
            system.add_component(component_id, agent)
        
        # Setup connections
        for connection in blueprint.connections:
            system.add_connection(connection['from'], connection['to'], connection['type'])
        
        # Apply configuration
        system.apply_configuration(blueprint.configuration)
        
        self.assembled_systems[system_id] = system
        return system
    
    def get_system(self, system_id: str) -> Optional['AssembledSystem']:
        """Get an assembled system by ID."""
        return self.assembled_systems.get(system_id)
    
    def list_systems(self) -> List[str]:
        """List all assembled system IDs."""
        return list(self.assembled_systems.keys())
    
    def get_blueprints(self) -> List[str]:
        """List all available blueprints."""
        return list(self.blueprints.keys())

class AssembledSystem:
    """A dynamically assembled system of atomic agents."""
    
    def __init__(self, system_id: str, blueprint: SystemBlueprint):
        self.system_id = system_id
        self.blueprint = blueprint
        self.components: Dict[str, AtomicAgent] = {}
        self.connections: Dict[str, List[str]] = {}  # from -> [to, to, ...]
        self.configuration: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def add_component(self, component_id: str, agent: AtomicAgent) -> None:
        """Add a component to the assembled system."""
        self.components[component_id] = agent
        self.connections[component_id] = []
    
    def add_connection(self, from_component: str, to_component: str, connection_type: str) -> None:
        """Add a connection between components."""
        if from_component not in self.connections:
            self.connections[from_component] = []
        self.connections[from_component].append(to_component)
    
    def apply_configuration(self, config: Dict[str, Any]) -> None:
        """Apply system-level configuration."""
        self.configuration.update(config)
    
    async def execute(self, input_data: Any, context: AtomicContext, entry_point: str = None) -> AtomicResult:
        """Execute the assembled system."""
        
        if not self.components:
            return AtomicResult(
                success=False,
                error="System has no components"
            )
        
        start_time = time.time()
        
        # Determine entry point
        if entry_point is None:
            entry_point = list(self.components.keys())[0]  # First component
        
        if entry_point not in self.components:
            return AtomicResult(
                success=False,
                error=f"Entry point '{entry_point}' not found"
            )
        
        try:
            # Execute starting from entry point
            result = await self._execute_component_chain(entry_point, input_data, context, set())
            
            # Record execution
            execution_time = (time.time() - start_time) * 1000
            execution_record = {
                'system_id': self.system_id,
                'entry_point': entry_point,
                'execution_time_ms': execution_time,
                'timestamp': datetime.now().isoformat(),
                'success': result.success
            }
            self.execution_history.append(execution_record)
            
            # Enhance result metadata
            result.metadata.update({
                'system_id': self.system_id,
                'entry_point': entry_point,
                'system_execution_time_ms': execution_time,
                'components_executed': len(self.components)
            })
            
            return result
            
        except Exception as e:
            return AtomicResult(
                success=False,
                error=f"System execution failed: {e}",
                metadata={'system_id': self.system_id}
            )
    
    async def _execute_component_chain(
        self, 
        component_id: str, 
        data: Any, 
        context: AtomicContext, 
        visited: set
    ) -> AtomicResult:
        """Execute a component and its connected components."""
        
        # Prevent infinite loops
        if component_id in visited:
            return AtomicResult(
                success=False,
                error=f"Circular dependency detected: {component_id}"
            )
        
        visited.add(component_id)
        
        # Execute current component
        component = self.components[component_id]
        result = await component._execute_with_metrics(data, context)
        
        if not result.success:
            return result
        
        # Execute connected components
        connected_components = self.connections.get(component_id, [])
        if connected_components:
            # For simplicity, execute the first connected component
            # In a more sophisticated system, this could be parallel or conditional
            next_component = connected_components[0]
            next_data = result.data if result.data is not None else data
            
            return await self._execute_component_chain(next_component, next_data, context, visited.copy())
        
        return result
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the assembled system."""
        return {
            'system_id': self.system_id,
            'blueprint_name': self.blueprint.name,
            'component_count': len(self.components),
            'connection_count': sum(len(connections) for connections in self.connections.values()),
            'executions': len(self.execution_history),
            'components': {
                comp_id: {
                    'agent_type': type(agent).__name__,
                    'agent_id': agent.agent_id,
                    'executions': agent.execution_count
                }
                for comp_id, agent in self.components.items()
            },
            'connections': self.connections,
            'configuration': self.configuration
        }

# Demo Functions

async def demonstrate_adaptive_orchestration():
    """Demonstrate adaptive orchestration patterns."""
    print("🧠 Adaptive Orchestration Demo")
    print("-" * 30)
    
    orchestrator = AdaptiveOrchestrator()
    orchestrator.auto_register_agents()
    
    test_cases = [
        # Long text -> Sequential processing
        TextProcessingInput(
            content="This is a very long text that contains multiple sentences and should trigger sequential processing according to our composition rules. It demonstrates how adaptive orchestration can route different types of input to different processing strategies based on the characteristics of the data. The system analyzes the input and makes intelligent decisions about how to process it most effectively.",
            operation="summarize"
        ),
        
        # Sentiment analysis -> Parallel processing
        TextProcessingInput(
            content="This is great news!",
            operation="sentiment"
        ),
        
        # Dictionary with validation flag -> Validation first
        {"data": "test data", "validate_first": True}
    ]
    
    for i, test_input in enumerate(test_cases):
        context = AtomicContext(user_id=f"adaptive_demo_{i}")
        
        # Add metadata for validation rule
        if isinstance(test_input, dict):
            context.add_metadata("validate_first", True)
        
        result = await orchestrator.execute(test_input, context)
        
        print(f"✅ Test Case {i+1}:")
        print(f"   Strategy: {result.metadata.get('composition_strategy', 'unknown')}")
        print(f"   Agents Used: {result.metadata.get('agents_used', [])}")
        print(f"   Success: {result.success}")
        print(f"   Processing Time: {result.metadata.get('total_orchestration_time_ms', 0):.1f}ms")
        
        if result.success and hasattr(result.data, 'result'):
            print(f"   Result: {result.data.result}")
        print()
    
    # Show performance analytics
    analytics = orchestrator.get_performance_analytics()
    print("📊 Orchestration Analytics:")
    print(f"   Strategies Used: {analytics['strategies_used']}")
    print(f"   Total Executions: {analytics['total_executions']}")
    
    for strategy, metrics in analytics['strategy_performance'].items():
        print(f"   {strategy}: {metrics['executions']} exec, avg {metrics['average_time_ms']:.1f}ms")

async def demonstrate_dynamic_system_assembly():
    """Demonstrate dynamic system assembly from blueprints."""
    print("\n🏗️ Dynamic System Assembly Demo")
    print("-" * 30)
    
    # Create a blueprint for text analysis system
    text_analysis_blueprint = SystemBlueprint("text_analysis_system")
    text_analysis_blueprint.add_component("text_processor", "text_processor", {"agent_id": "text_proc_1"})
    text_analysis_blueprint.add_component("validator", "data_validator", {"agent_id": "validator_1"})
    text_analysis_blueprint.connect("text_processor", "validator")
    text_analysis_blueprint.set_configuration("max_processing_time_ms", 5000)
    
    # Create a blueprint for data quality system
    data_quality_blueprint = SystemBlueprint("data_quality_system")
    data_quality_blueprint.add_component("primary_validator", "data_validator")
    data_quality_blueprint.add_component("secondary_processor", "text_processor")
    data_quality_blueprint.connect("primary_validator", "secondary_processor")
    data_quality_blueprint.set_configuration("validation_strict", True)
    
    # Create assembler and register blueprints
    assembler = DynamicSystemAssembler()
    assembler.register_blueprint(text_analysis_blueprint)
    assembler.register_blueprint(data_quality_blueprint)
    
    print(f"✅ Available Blueprints: {assembler.get_blueprints()}")
    
    # Assemble systems
    text_system = assembler.assemble_system("text_analysis_system", "text_system_001")
    quality_system = assembler.assemble_system("data_quality_system", "quality_system_001")
    
    print(f"✅ Assembled Systems: {assembler.list_systems()}")
    
    # Execute text analysis system
    context = AtomicContext(user_id="system_demo")
    text_input = TextProcessingInput(
        content="This system demonstrates modular composition",
        operation="extract_keywords"
    )
    
    result = await text_system.execute(text_input, context)
    
    print(f"\n✅ Text Analysis System Execution:")
    print(f"   Success: {result.success}")
    print(f"   System ID: {result.metadata.get('system_id')}")
    print(f"   Components Executed: {result.metadata.get('components_executed')}")
    print(f"   Execution Time: {result.metadata.get('system_execution_time_ms', 0):.1f}ms")
    
    if result.success and hasattr(result.data, 'result'):
        print(f"   Result: {result.data.result}")
    
    # Show system information
    print(f"\n📋 System Information:")
    system_info = text_system.get_system_info()
    print(f"   Components: {system_info['component_count']}")
    print(f"   Connections: {system_info['connection_count']}")
    print(f"   Blueprint: {system_info['blueprint_name']}")

async def demonstrate_conditional_routing():
    """Demonstrate conditional routing based on data characteristics."""
    print("\n🚏 Conditional Routing Demo")
    print("-" * 30)
    
    router = ConditionalRouter()
    
    # Add custom routing rules
    router.add_simple_rule(
        condition=lambda data, ctx: hasattr(data, 'content') and 'urgent' in data.content.lower(),
        strategy=CompositionStrategy.PARALLEL,
        agent_types=['text_processor', 'data_validator']
    )
    
    router.add_simple_rule(
        condition=lambda data, ctx: isinstance(data, dict) and data.get('priority') == 'high',
        strategy=CompositionStrategy.SEQUENTIAL,
        agent_types=['data_validator', 'text_processor', 'data_validator']
    )
    
    test_cases = [
        TextProcessingInput(content="This is urgent processing needed!", operation="summarize"),
        {"data": "test", "priority": "high"},
        TextProcessingInput(content="Regular processing", operation="word_count"),
        {"data": "normal", "priority": "normal"}
    ]
    
    for i, test_input in enumerate(test_cases):
        context = AtomicContext(user_id=f"routing_demo_{i}")
        
        routing_decision = await router.route(test_input, context)
        
        print(f"✅ Test Case {i+1}:")
        print(f"   Input Type: {type(test_input).__name__}")
        print(f"   Strategy: {routing_decision['strategy'].value}")
        print(f"   Agents: {routing_decision['agents']}")
        print(f"   Rule Matched: {routing_decision['matched']}")
        print()

async def run_modular_composition_demo():
    """Run comprehensive modular composition demonstration."""
    print("🚀 Modular Composition Patterns - Comprehensive Demo")
    print("=" * 55)
    print("\nDemonstrating advanced orchestration and dynamic assembly")
    print("Shows how atomic agents can be composed in sophisticated ways\n")
    
    try:
        await demonstrate_adaptive_orchestration()
        await demonstrate_dynamic_system_assembly()
        await demonstrate_conditional_routing()
        
        print("\n🎯 Modular Composition Demo Complete!")
        print("\nAdvanced Composition Benefits Demonstrated:")
        print("• ✅ Adaptive orchestration - intelligent strategy selection")
        print("• ✅ Dynamic assembly - runtime system composition")
        print("• ✅ Conditional routing - data-driven execution paths")
        print("• ✅ Blueprint patterns - reusable system designs")
        print("• ✅ Performance analytics - strategy optimization")
        print("• ✅ Component reuse - atomic agents in multiple systems")
        
        print(f"\n💡 Enterprise Architecture Characteristics:")
        print("• Microservices patterns with intelligent orchestration")
        print("• Dynamic system topology based on workload")
        print("• Fault isolation through component boundaries")
        print("• Automatic performance optimization")
        print("• Blueprint-driven system deployment")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise

if __name__ == "__main__":
    # Run modular composition demonstration
    asyncio.run(run_modular_composition_demo())