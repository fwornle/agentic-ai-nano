#!/usr/bin/env python3
"""
Example usage of Atomic Agents architecture.

This script demonstrates how to use the atomic agents for text processing,
including single agent execution, pipeline composition, and parallel execution.
"""

import asyncio
from atomic_foundation import AtomicContext
from text_processor_agent import TextInput, TextProcessorAgent
from composition_engine import AtomicPipeline, AtomicParallelExecutor
from context_providers import DatabaseContextProvider

async def basic_agent_example():
    """Demonstrate basic atomic agent usage."""
    print("\n=== Basic Atomic Agent Example ===")
    
    # Create context
    context = AtomicContext(user_id="demo-user", metadata={"example": "basic"})
    
    # Create input
    text_input = TextInput(
        content="Atomic agents represent the next evolution in agent architecture. They embrace modular, composable design patterns that scale from simple tasks to enterprise systems. Each atomic agent is designed to be self-contained yet seamlessly interoperable with others.",
        operation="summarize"
    )
    
    # Execute agent
    agent = TextProcessorAgent()
    result = await agent.execute(text_input, context)
    
    print(f"Input text length: {len(text_input.content)} characters")
    print(f"Summary: {result.result}")
    print(f"Confidence: {result.confidence}")
    print(f"Processing time: {result.processing_time_ms}ms")
    print(f"Word count: {result.word_count}")
    print(f"Agent ID: {result.metadata['agent_id']}")

async def pipeline_example():
    """Demonstrate pipeline composition."""
    print("\n=== Pipeline Composition Example ===")
    
    # Create pipeline
    pipeline = AtomicPipeline("Text Analysis Pipeline")
    pipeline.add_agent(TextProcessorAgent())
    
    # Create context and input
    context = AtomicContext(user_id="pipeline-user")
    text_input = TextInput(
        content="Machine learning and artificial intelligence continue to transform industries. The future of technology lies in intelligent systems that can adapt and learn.",
        operation="extract_keywords"
    )
    
    # Execute pipeline
    result = await pipeline.execute(text_input, context)
    
    print(f"Keywords extracted: {result.result}")
    print(f"Pipeline execution trace: {result.metadata.get('pipeline_trace', [])}")

async def parallel_execution_example():
    """Demonstrate parallel execution of multiple agents."""
    print("\n=== Parallel Execution Example ===")
    
    # Create context
    context = AtomicContext(user_id="parallel-user")
    
    # Prepare multiple text processing tasks
    tasks = [
        (TextProcessorAgent(), TextInput(content="This is positive and wonderful news!", operation="sentiment")),
        (TextProcessorAgent(), TextInput(content="Unfortunately, this is very disappointing and terrible.", operation="sentiment")),
        (TextProcessorAgent(), TextInput(content="This is a neutral statement about facts.", operation="sentiment"))
    ]
    
    # Execute in parallel
    executor = AtomicParallelExecutor(max_concurrent=3)
    results = await executor.execute_parallel(tasks, context)
    
    print("Sentiment analysis results:")
    for i, result in enumerate(results):
        print(f"  Text {i+1}: {result.result} (confidence: {result.confidence})")

async def error_handling_example():
    """Demonstrate error handling in atomic agents."""
    print("\n=== Error Handling Example ===")
    
    try:
        # Create context
        context = AtomicContext(user_id="error-test")
        
        # Try invalid operation
        text_input = TextInput(
            content="Test content",
            operation="invalid_operation"  # This will cause a validation error
        )
        
        agent = TextProcessorAgent()
        result = await agent.execute(text_input, context)
        
    except Exception as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")
        if hasattr(e, 'agent_name'):
            print(f"Error occurred in agent: {e.agent_name}")

async def main():
    """Run all examples."""
    print("Atomic Agents Architecture Examples")
    print("=" * 40)
    
    try:
        await basic_agent_example()
        await pipeline_example() 
        await parallel_execution_example()
        await error_handling_example()
        
        print("\n=== All Examples Completed Successfully ===")
        
    except Exception as e:
        print(f"\nError during example execution: {e}")
        raise

if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())