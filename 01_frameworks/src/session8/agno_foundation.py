# Agno Foundation Classes
# Core production-ready agent implementations

from agno import Agent
from agno.tools import DuckDuckGoTools
from agno.reasoning import ChainOfThought, PlanAndSolve
from agno import Team
from agno.agents import AnalystAgent, WriterAgent, ReviewerAgent
from agno.config import AgentConfig
from agno.monitoring import PrometheusMetrics
from agno.storage import PostgresStorage
from datetime import datetime
import os


# Level 1: Simple Function Calling Agent
def create_basic_agent():
    """Create a basic research agent"""
    research_agent = Agent(
        name="research_assistant",
        model="gpt-4o",
        tools=[DuckDuckGoTools()],
        instructions="You are a research assistant that provides accurate information."
    )
    return research_agent


# Level 2: Reasoning and Planning Agent
def create_reasoning_agent():
    """Create an agent with reasoning capabilities"""
    reasoning_agent = Agent(
        name="problem_solver",
        model="gpt-4o",
        reasoning=[
            ChainOfThought(),
            PlanAndSolve()
        ],
        tools=[DuckDuckGoTools()],
        instructions="""
        You are an analytical problem solver. For complex questions:
        1. Break down the problem into steps
        2. Research each component thoroughly  
        3. Synthesize findings into a comprehensive solution
        """
    )
    return reasoning_agent


# Level 3: Multi-Agent Collaboration
def create_specialist_agents():
    """Create specialized agents for team collaboration"""
    analyst = AnalystAgent(
        name="market_analyst",
        model="gpt-4o",
        instructions="Analyze market data and identify trends."
    )

    writer = WriterAgent(
        name="content_writer", 
        model="gpt-4o",
        instructions="Create compelling content based on analysis."
    )

    reviewer = ReviewerAgent(
        name="quality_reviewer",
        model="gpt-4o", 
        instructions="Review content for accuracy and compliance."
    )
    
    return analyst, writer, reviewer


def create_collaborative_team():
    """Create a collaborative team of agents"""
    analyst, writer, reviewer = create_specialist_agents()
    
    content_team = Team(
        name="content_creation_team",
        agents=[analyst, writer, reviewer],
        workflow="sequential",  # analyst -> writer -> reviewer
        max_iterations=3
    )
    
    return content_team


class ProductionAgent(Agent):
    """Production-ready agent with enterprise features"""
    
    def __init__(self, config: AgentConfig):
        # Initialize base agent with production settings
        super().__init__(
            name=config.name,
            model=config.model,
            temperature=config.temperature,  # Lower for consistency
            max_tokens=config.max_tokens
        )
        
        self.config = config
        self.startup_time = datetime.utcnow()
        
        # Set up core production components
        self._initialize_production_components()
    
    def _initialize_production_components(self):
        """Initialize monitoring and storage for production use"""
        
        # Prometheus metrics for observability
        self.metrics = PrometheusMetrics(
            agent_name=self.config.name,
            labels={
                "environment": "production",
                "version": "1.0.0"
            }
        )
        
        # PostgreSQL storage for audit trails
        self.storage = PostgresStorage(
            connection_url=self.config.storage_url,
            table_prefix=f"agent_{self.config.name}"
        )
        
        # Production middleware stack
        self.add_middleware([
            self._request_logging,      # Audit all interactions
            self._performance_monitoring,  # Track SLA metrics
            self._error_handling        # Graceful failure handling
        ])
        
        print(f"Production agent {self.config.name} initialized with monitoring")
    
    async def _request_logging(self, request, response):
        """Comprehensive logging for audit and debugging"""
        try:
            await self.storage.log_interaction(
                agent_name=self.name,
                request_data={
                    "content": request.content,
                    "user_id": getattr(request, 'user_id', 'anonymous'),
                    "timestamp": datetime.utcnow(),
                    "session_id": getattr(request, 'session_id', None)
                },
                response_data={
                    "content": response.content,
                    "processing_time": response.processing_time,
                    "tokens_used": getattr(response, 'tokens_used', 0),
                    "model": response.model
                },
                metadata={
                    "success": not response.error,
                    "error_message": str(response.error) if response.error else None
                }
            )
        except Exception as e:
            # Never let logging failures break the main request
            print(f"Logging failed for {self.name}: {e}")
    
    async def _performance_monitoring(self, request, response):
        """Track performance metrics for SLA monitoring"""
        try:
            # Increment request counter
            self.metrics.increment_counter("requests_total", {
                "status": "error" if response.error else "success",
                "model": response.model
            })
            
            # Track response time distribution
            self.metrics.record_histogram("response_time_seconds", 
                                        response.processing_time)
            
            # Track token usage for cost monitoring
            if hasattr(response, 'tokens_used'):
                self.metrics.record_histogram("tokens_per_request", 
                                            response.tokens_used)
                
        except Exception as e:
            print(f"Metrics recording failed for {self.name}: {e}")
    
    async def _error_handling(self, request, response):
        """Graceful error handling and alerting"""
        if response.error:
            try:
                # Log error for investigation
                await self.storage.log_error(
                    agent_name=self.name,
                    error=response.error,
                    request_context=request.content[:200],  # Truncate for storage
                    timestamp=datetime.utcnow()
                )
                
                # Update error metrics
                self.metrics.increment_counter("errors_total", {
                    "error_type": type(response.error).__name__
                })
                
                # Critical errors should trigger alerts
                if isinstance(response.error, (TimeoutError, ConnectionError)):
                    await self._trigger_alert(response.error)
                    
            except Exception as e:
                print(f"Error handling failed for {self.name}: {e}")

    async def _trigger_alert(self, error):
        """Trigger alert for critical errors"""
        # Implementation would integrate with alerting system
        print(f"ALERT: Critical error in {self.name}: {error}")


def create_production_config():
    """Create production-ready agent configuration"""
    return AgentConfig(
        # Model configuration
        model="gpt-4o",
        temperature=0.1,  # Low temperature for consistency
        max_tokens=2048,
        timeout=30,  # Request timeout
        
        # Performance settings
        max_retries=3,
        retry_delay=1.0,
        batch_size=10,
        
        # Production features
        enable_monitoring=True,
        enable_caching=True,
        log_level="INFO",
        
        # Storage configuration
        storage_backend="postgres",
        storage_url=os.getenv("DATABASE_URL")
    )


# Example usage
if __name__ == "__main__":
    # Create basic agent
    basic_agent = create_basic_agent()
    result = basic_agent.run("What is the current state of AI in healthcare?")
    print(f"Research Result: {result.content}")
    
    # Create reasoning agent
    reasoning_agent = create_reasoning_agent()
    complex_problem = """
    How can a mid-size company implement AI to improve customer service 
    while maintaining data privacy and staying within a $100K budget?
    """
    solution = reasoning_agent.run(complex_problem)
    print(f"Reasoned Solution: {solution.content}")
    
    # Create collaborative team
    team = create_collaborative_team()
    task = "Create a whitepaper on AI adoption trends in fintech for Q4 2024"
    team_result = team.run(task)
    print(f"Team Output: {team_result.content}")
    print(f"Collaboration Steps: {len(team_result.steps)}")