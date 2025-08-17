# From src/session6/composition_engine.py
from typing import List, Type, Any, Dict, Tuple
import asyncio
import uuid
from datetime import datetime

from atomic_foundation import AtomicAgent, AtomicContext, AtomicError, ExecutionError
from context_providers import ContextProvider

class AtomicPipeline:
    """Compose multiple atomic agents into a processing pipeline."""
    
    def __init__(self, name: str):
        self.name = name
        self.pipeline_id = str(uuid.uuid4())
        self.agents: List[AtomicAgent] = []
        self.context_providers: Dict[str, ContextProvider] = {}
        
    def add_agent(self, agent: AtomicAgent) -> 'AtomicPipeline':
        """Add an agent to the pipeline (builder pattern)."""
        self.agents.append(agent)
        return self
    
    def add_context_provider(self, provider: ContextProvider) -> 'AtomicPipeline':
        """Add a context provider to the pipeline."""
        self.context_providers[provider.get_provider_type()] = provider
        return self
    
    async def execute(self, initial_input: Any, context: AtomicContext) -> Any:
        """Execute the entire pipeline with data flowing between agents."""
        current_data = initial_input
        execution_trace = []
        
        # Enrich context with providers
        enriched_context = await self._enrich_context(context)
        
        for i, agent in enumerate(self.agents):
            try:
                step_start = datetime.utcnow()
                
                # Execute current agent
                current_data = await agent.execute(current_data, enriched_context)
                
                # Record execution trace
                step_duration = (datetime.utcnow() - step_start).total_seconds() * 1000
                execution_trace.append({
                    "step": i + 1,
                    "agent": agent.name,
                    "duration_ms": step_duration,
                    "success": True
                })
                
            except AtomicError as e:
                # Record failure and stop pipeline
                execution_trace.append({
                    "step": i + 1,
                    "agent": agent.name,
                    "error": str(e),
                    "success": False
                })
                
                raise ExecutionError(
                    f"Pipeline failed at step {i + 1} ({agent.name}): {str(e)}",
                    self.name,
                    enriched_context,
                    {"execution_trace": execution_trace}
                )
        
        # Add execution trace to final result
        if hasattr(current_data, 'metadata'):
            current_data.metadata["pipeline_trace"] = execution_trace
        
        return current_data
    
    async def _enrich_context(self, context: AtomicContext) -> AtomicContext:
        """Enrich context with data from context providers."""
        enriched_metadata = context.metadata.copy()
        
        for provider_type, provider in self.context_providers.items():
            try:
                provider_data = await provider.provide(context)
                enriched_metadata[f"{provider_type}_context"] = provider_data
            except Exception as e:
                # Log provider error but continue execution
                enriched_metadata[f"{provider_type}_error"] = str(e)
        
        # Create new context with enriched metadata
        enriched_context = AtomicContext(
            request_id=context.request_id,
            timestamp=context.timestamp,
            user_id=context.user_id,
            session_id=context.session_id,
            metadata=enriched_metadata
        )
        
        return enriched_context

class AtomicParallelExecutor:
    """Execute multiple atomic agents in parallel."""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_parallel(
        self, 
        agent_tasks: List[Tuple[AtomicAgent, Any]], 
        context: AtomicContext
    ) -> List[Any]:
        """Execute multiple agents concurrently with concurrency control."""
        
        async def execute_with_semaphore(agent: AtomicAgent, input_data: Any):
            async with self.semaphore:
                return await agent.execute(input_data, context)
        
        # Create tasks for all agents
        tasks = [
            execute_with_semaphore(agent, input_data) 
            for agent, input_data in agent_tasks
        ]
        
        # Execute all tasks concurrently
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Separate successful results from exceptions
            successful_results = []
            errors = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    errors.append({
                        "agent": agent_tasks[i][0].name,
                        "error": str(result)
                    })
                else:
                    successful_results.append(result)
            
            if errors:
                raise ExecutionError(
                    f"Parallel execution had {len(errors)} failures",
                    "ParallelExecutor",
                    context,
                    {"errors": errors, "successful_count": len(successful_results)}
                )
            
            return successful_results
            
        except Exception as e:
            raise ExecutionError(
                f"Parallel execution failed: {str(e)}",
                "ParallelExecutor", 
                context
            )