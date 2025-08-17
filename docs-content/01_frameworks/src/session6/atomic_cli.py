# From src/session6/atomic_cli.py
import click
import asyncio
import json
from pathlib import Path

from atomic_foundation import AtomicContext
from text_processor_agent import TextInput, TextProcessorAgent
from composition_engine import AtomicPipeline

@click.group()
@click.option('--config', default='config.json', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Atomic Agents CLI interface."""
    ctx.ensure_object(dict)
    
    # Load configuration
    config_path = Path(config)
    if config_path.exists():
        with open(config_path) as f:
            ctx.obj['config'] = json.load(f)
    else:
        ctx.obj['config'] = {}

@cli.command()
@click.option('--text', required=True, help='Text to process')
@click.option('--operation', type=click.Choice(['summarize', 'extract_keywords', 'sentiment']), 
              default='summarize', help='Processing operation')
@click.option('--output', help='Output file path')
@click.pass_context
def process_text(ctx, text, operation, output):
    """Process text using atomic text processor agent."""
    
    async def run_processing():
        # Create atomic context
        context = AtomicContext(
            user_id='cli-user',
            metadata={'cli_command': 'process_text'}
        )
        
        # Create input
        text_input = TextInput(
            content=text,
            operation=operation
        )
        
        # Execute agent
        agent = TextProcessorAgent()
        result = await agent.execute(text_input, context)
        
        # Output results
        output_data = {
            'result': result.result,
            'confidence': result.confidence,
            'processing_time_ms': result.processing_time_ms,
            'word_count': result.word_count,
            'metadata': result.metadata
        }
        
        if output:
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            click.echo(f"Results written to {output}")
        else:
            click.echo(json.dumps(output_data, indent=2))
    
    # Run async operation
    asyncio.run(run_processing())

@cli.command()
@click.option('--config-file', required=True, help='Pipeline configuration file')
@click.option('--input-file', required=True, help='Input data file')
@click.option('--output-file', help='Output file path')
@click.pass_context
def run_pipeline(ctx, config_file, input_file, output_file):
    """Execute an atomic agent pipeline from configuration."""
    
    async def run_pipeline_execution():
        # Load pipeline configuration
        with open(config_file) as f:
            pipeline_config = json.load(f)
        
        # Load input data
        with open(input_file) as f:
            input_data = json.load(f)
        
        # Build pipeline from configuration (simplified)
        pipeline = AtomicPipeline(pipeline_config.get('name', 'CLI Pipeline'))
        
        # Add agents based on configuration
        for agent_config in pipeline_config.get('agents', []):
            if agent_config['type'] == 'text_processor':
                pipeline.add_agent(TextProcessorAgent())
        
        # Create context
        context = AtomicContext(
            user_id='cli-user',
            metadata={
                'cli_command': 'run_pipeline',
                'config_file': config_file,
                'input_file': input_file
            }
        )
        
        # Execute pipeline
        result = await pipeline.execute(input_data, context)
        
        # Output results
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(result.dict(), f, indent=2)
            click.echo(f"Pipeline results written to {output_file}")
        else:
            click.echo(json.dumps(result.dict(), indent=2))
    
    # Run async operation
    asyncio.run(run_pipeline_execution())

if __name__ == '__main__':
    cli()