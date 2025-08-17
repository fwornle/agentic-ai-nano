"""
Session 6: Atomic Agents Modular Architecture

This package provides a complete implementation of atomic agent architecture patterns,
demonstrating how to build composable, type-safe agent systems that scale from simple
tasks to enterprise deployments.

Key Components:
- AtomicAgent: Base class for type-safe agents
- AtomicPipeline: Compose agents into workflows  
- AtomicOrchestrator: Production service management
- ContextProvider: Dependency injection pattern
"""

from atomic_foundation import (
    AtomicAgent,
    AtomicContext, 
    AtomicError,
    ValidationError,
    ExecutionError
)

from text_processor_agent import (
    TextProcessorAgent,
    TextInput,
    TextOutput
)

from context_providers import (
    ContextProvider,
    DatabaseContextProvider
)

from composition_engine import (
    AtomicPipeline,
    AtomicParallelExecutor
)

from production_orchestrator import (
    AtomicOrchestrator,
    ServiceRegistration,
    MetricsCollector,
    AtomicLoadBalancer
)

__all__ = [
    # Core classes
    'AtomicAgent',
    'AtomicContext',
    'AtomicError',
    'ValidationError', 
    'ExecutionError',
    
    # Example agent
    'TextProcessorAgent',
    'TextInput',
    'TextOutput',
    
    # Context providers
    'ContextProvider',
    'DatabaseContextProvider',
    
    # Composition
    'AtomicPipeline',
    'AtomicParallelExecutor',
    
    # Production
    'AtomicOrchestrator',
    'ServiceRegistration',
    'MetricsCollector',
    'AtomicLoadBalancer'
]

__version__ = "1.0.0"
__author__ = "Atomic Agents Framework"