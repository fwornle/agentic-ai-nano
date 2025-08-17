"""
Agno Basic Agent Implementations
Session 7: Agno Production-Ready Agents

This module demonstrates Agno's 5-level agent architecture with production-ready
configurations and examples.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

try:
    # Agno framework imports (simulated structure based on documentation)
    from agno import Agent
    from agno.tools import DuckDuckGoTools, CalculatorTool, WebSearchTool
    from agno.config import AgentConfig
    from agno.exceptions import AgentError, ConfigurationError
except ImportError:
    # Fallback implementations for demonstration
    print("Warning: Agno not available, using mock implementations")
    
    class Agent:
        def __init__(self, name: str, model: str = "gpt-4o", **kwargs):
            self.name = name
            self.model = model
            self.config = kwargs
            
        async def run(self, prompt: str) -> 'AgentResponse':
            return AgentResponse(f"Agent {self.name} processed: {prompt}")
    
    class AgentResponse:
        def __init__(self, content: str):
            self.content = content
            self.processing_time = 0.5
            self.model = "gpt-4o"
            
    class DuckDuckGoTools:
        pass
        
    class CalculatorTool:
        pass
        
    class WebSearchTool:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Metrics tracking for agent performance"""
    requests_processed: int = 0
    total_processing_time: float = 0.0
    successful_responses: int = 0
    failed_responses: int = 0
    average_response_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def update(self, processing_time: float, success: bool):
        """Update metrics with new request data"""
        self.requests_processed += 1
        self.total_processing_time += processing_time
        
        if success:
            self.successful_responses += 1
        else:
            self.failed_responses += 1
            
        self.average_response_time = self.total_processing_time / self.requests_processed

class Level1BasicAgent:
    """
    Level 1: Simple Function Calling Agent
    
    Basic agent with simple tool usage and configuration.
    Demonstrates Agno's simplicity for rapid development.
    """
    
    def __init__(self, name: str = "basic_research_agent"):
        """Initialize Level 1 basic agent"""
        self.name = name
        self.metrics = AgentMetrics()
        
        try:
            self.agent = Agent(
                name=self.name,
                model="gpt-4o",
                tools=[DuckDuckGoTools()],
                instructions="""
                You are a research assistant that provides accurate information.
                Use web search tools to gather current information.
                Always cite your sources and provide factual responses.
                """
            )
            logger.info(f"Initialized Level 1 agent: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Level 1 agent: {e}")
            raise ConfigurationError(f"Agent initialization failed: {e}")
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a simple research query"""
        start_time = datetime.utcnow()
        
        try:
            # Execute the query with the agent
            result = await self.agent.run(query)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update(processing_time, True)
            
            return {
                "query": query,
                "response": result.content,
                "processing_time": processing_time,
                "agent_name": self.name,
                "model_used": result.model,
                "timestamp": start_time.isoformat(),
                "success": True
            }
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update(processing_time, False)
            
            logger.error(f"Query processing failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "processing_time": processing_time,
                "agent_name": self.name,
                "timestamp": start_time.isoformat(),
                "success": False
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current agent performance metrics"""
        return {
            "agent_name": self.name,
            "requests_processed": self.metrics.requests_processed,
            "success_rate": (
                self.metrics.successful_responses / max(1, self.metrics.requests_processed)
            ),
            "average_response_time": self.metrics.average_response_time,
            "uptime": (datetime.utcnow() - self.metrics.created_at).total_seconds(),
            "total_processing_time": self.metrics.total_processing_time
        }

class Level2ReasoningAgent:
    """
    Level 2: Reasoning and Planning Agent
    
    Advanced agent with Chain of Thought reasoning and planning capabilities.
    Suitable for complex problem-solving tasks.
    """
    
    def __init__(self, name: str = "reasoning_problem_solver"):
        """Initialize Level 2 reasoning agent"""
        self.name = name
        self.metrics = AgentMetrics()
        
        try:
            self.agent = Agent(
                name=self.name,
                model="gpt-4o",
                tools=[DuckDuckGoTools(), CalculatorTool(), WebSearchTool()],
                instructions="""
                You are an analytical problem solver with advanced reasoning capabilities.
                
                For complex questions, follow this approach:
                1. Break down the problem into manageable components
                2. Research each component thoroughly using available tools
                3. Apply logical reasoning to connect the findings
                4. Synthesize information into a comprehensive solution
                5. Validate your reasoning and provide confidence levels
                
                Always show your reasoning process and cite sources.
                """,
                # Reasoning configuration (simulated)
                reasoning_enabled=True,
                chain_of_thought=True,
                plan_and_solve=True,
                temperature=0.1  # Lower temperature for consistent reasoning
            )
            logger.info(f"Initialized Level 2 reasoning agent: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Level 2 agent: {e}")
            raise ConfigurationError(f"Reasoning agent initialization failed: {e}")
    
    async def solve_complex_problem(self, problem: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Solve complex problems using reasoning and planning capabilities
        
        Args:
            problem: The problem statement to solve
            context: Additional context or constraints
            
        Returns:
            Comprehensive solution with reasoning steps
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare the enhanced prompt with reasoning instructions
            enhanced_prompt = f"""
            Problem to Solve: {problem}
            
            Additional Context: {context if context else 'None provided'}
            
            Please solve this problem using systematic reasoning:
            1. Problem Analysis: Break down the key components
            2. Information Gathering: Identify what research is needed
            3. Solution Development: Create a step-by-step approach
            4. Validation: Check the solution for completeness and accuracy
            5. Implementation Guidance: Provide actionable next steps
            """
            
            result = await self.agent.run(enhanced_prompt)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update(processing_time, True)
            
            return {
                "problem": problem,
                "context": context,
                "solution": result.content,
                "reasoning_steps": self._extract_reasoning_steps(result.content),
                "processing_time": processing_time,
                "agent_name": self.name,
                "model_used": result.model,
                "timestamp": start_time.isoformat(),
                "confidence_level": self._assess_confidence(result.content),
                "success": True
            }
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update(processing_time, False)
            
            logger.error(f"Problem solving failed: {e}")
            return {
                "problem": problem,
                "error": str(e),
                "processing_time": processing_time,
                "agent_name": self.name,
                "timestamp": start_time.isoformat(),
                "success": False
            }
    
    def _extract_reasoning_steps(self, content: str) -> List[str]:
        """Extract reasoning steps from agent response"""
        # Simple extraction logic - in production, use more sophisticated parsing
        steps = []
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['step', 'analysis', 'solution', 'validation']):
                steps.append(line.strip())
        
        return steps[:10]  # Limit to first 10 steps
    
    def _assess_confidence(self, content: str) -> float:
        """Assess confidence level based on response content"""
        # Simple confidence assessment - in production, use more sophisticated analysis
        confidence_indicators = [
            'certain', 'confident', 'clearly', 'definitely', 'proven',
            'established', 'confirmed', 'validated'
        ]
        
        uncertainty_indicators = [
            'possibly', 'maybe', 'might', 'could be', 'uncertain',
            'unclear', 'unknown', 'estimated'
        ]
        
        content_lower = content.lower()
        confidence_score = 0.5  # Base confidence
        
        for indicator in confidence_indicators:
            if indicator in content_lower:
                confidence_score += 0.1
        
        for indicator in uncertainty_indicators:
            if indicator in content_lower:
                confidence_score -= 0.1
        
        return max(0.0, min(1.0, confidence_score))

class StructuredOutputAgent:
    """
    Agent with enforced structured outputs for enterprise integration
    
    Uses Pydantic models to ensure consistent, type-safe responses
    that can be easily integrated with downstream systems.
    """
    
    def __init__(self, name: str = "structured_analyst"):
        """Initialize structured output agent"""
        self.name = name
        self.metrics = AgentMetrics()
        
        # Define response structure
        class AnalysisResponse(BaseModel):
            summary: str = Field(description="Brief summary of the analysis")
            key_findings: List[str] = Field(description="List of key findings")
            recommendations: List[str] = Field(description="List of recommendations")
            confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence level")
            data_sources: List[str] = Field(description="Sources used in analysis")
            analysis_date: datetime = Field(default_factory=datetime.utcnow)
            metadata: Dict[str, Any] = Field(default_factory=dict)
        
        self.response_model = AnalysisResponse
        
        try:
            self.agent = Agent(
                name=self.name,
                model="gpt-4o",
                tools=[DuckDuckGoTools(), WebSearchTool()],
                response_model=self.response_model,  # Enforce structured output
                instructions="""
                You are an analytical agent that provides structured analysis.
                
                Always return your analysis in the specified JSON structure with:
                - A clear summary of your findings
                - Key findings as bullet points
                - Actionable recommendations
                - Your confidence level (0.0 to 1.0)
                - All data sources used
                
                Ensure all responses are complete and well-structured.
                """
            )
            logger.info(f"Initialized structured output agent: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize structured agent: {e}")
            raise ConfigurationError(f"Structured agent initialization failed: {e}")
    
    async def analyze_topic(self, topic: str, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze a topic with structured output
        
        Args:
            topic: The topic to analyze
            focus_areas: Specific areas to focus the analysis on
            
        Returns:
            Structured analysis results
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare focused analysis prompt
            focus_instruction = ""
            if focus_areas:
                focus_instruction = f"Pay special attention to: {', '.join(focus_areas)}"
            
            prompt = f"""
            Analyze the following topic comprehensively: {topic}
            
            {focus_instruction}
            
            Provide a structured analysis that includes:
            - Executive summary of the topic
            - Key findings and insights
            - Strategic recommendations
            - Data sources and references
            - Your confidence in the analysis
            
            Ensure your response follows the required JSON structure.
            """
            
            result = await self.agent.run(prompt)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update(processing_time, True)
            
            # Parse structured response
            if hasattr(result, 'structured_output'):
                structured_data = result.structured_output.dict()
            else:
                # Fallback parsing for demonstration
                structured_data = {
                    "summary": f"Analysis of {topic}",
                    "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
                    "recommendations": ["Recommendation 1", "Recommendation 2"],
                    "confidence_score": 0.8,
                    "data_sources": ["Web research", "Public data"],
                    "analysis_date": datetime.utcnow(),
                    "metadata": {"focus_areas": focus_areas}
                }
            
            return {
                "topic": topic,
                "focus_areas": focus_areas,
                "analysis": structured_data,
                "processing_time": processing_time,
                "agent_name": self.name,
                "timestamp": start_time.isoformat(),
                "success": True
            }
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update(processing_time, False)
            
            logger.error(f"Structured analysis failed: {e}")
            return {
                "topic": topic,
                "error": str(e),
                "processing_time": processing_time,
                "agent_name": self.name,
                "timestamp": start_time.isoformat(),
                "success": False
            }

class AgentFactory:
    """Factory for creating different types of agents"""
    
    @staticmethod
    def create_basic_agent(name: str = "basic_agent") -> Level1BasicAgent:
        """Create a Level 1 basic agent"""
        return Level1BasicAgent(name)
    
    @staticmethod
    def create_reasoning_agent(name: str = "reasoning_agent") -> Level2ReasoningAgent:
        """Create a Level 2 reasoning agent"""
        return Level2ReasoningAgent(name)
    
    @staticmethod
    def create_structured_agent(name: str = "structured_agent") -> StructuredOutputAgent:
        """Create a structured output agent"""
        return StructuredOutputAgent(name)

async def demonstrate_basic_agents():
    """Demonstrate basic agent capabilities"""
    print("=" * 60)
    print("AGNO BASIC AGENTS DEMONSTRATION")
    print("=" * 60)
    
    # Level 1 Basic Agent Demo
    print("\n1. Level 1 Basic Agent - Simple Research")
    print("-" * 40)
    
    basic_agent = AgentFactory.create_basic_agent("demo_research_agent")
    
    research_query = "What are the key benefits of using production-ready agent frameworks?"
    result = await basic_agent.process_query(research_query)
    
    print(f"Query: {result['query']}")
    print(f"Success: {result['success']}")
    print(f"Processing Time: {result['processing_time']:.2f}s")
    if result['success']:
        print(f"Response: {result['response'][:200]}...")
    else:
        print(f"Error: {result['error']}")
    
    print(f"\nAgent Metrics: {basic_agent.get_metrics()}")
    
    # Level 2 Reasoning Agent Demo
    print("\n\n2. Level 2 Reasoning Agent - Complex Problem Solving")
    print("-" * 50)
    
    reasoning_agent = AgentFactory.create_reasoning_agent("demo_problem_solver")
    
    complex_problem = """
    A mid-size company wants to implement AI agents to improve customer service
    while maintaining data privacy and staying within a $100K budget.
    What is the best approach?
    """
    
    context = {
        "company_size": "500 employees",
        "current_budget": "$100,000",
        "privacy_requirements": "GDPR compliant",
        "timeline": "6 months"
    }
    
    solution = await reasoning_agent.solve_complex_problem(complex_problem, context)
    
    print(f"Problem: {solution['problem'][:100]}...")
    print(f"Success: {solution['success']}")
    print(f"Processing Time: {solution['processing_time']:.2f}s")
    if solution['success']:
        print(f"Confidence Level: {solution['confidence_level']:.2f}")
        print(f"Reasoning Steps: {len(solution['reasoning_steps'])} identified")
        print(f"Solution: {solution['solution'][:300]}...")
    else:
        print(f"Error: {solution['error']}")
    
    # Structured Output Agent Demo
    print("\n\n3. Structured Output Agent - Enterprise Analysis")
    print("-" * 50)
    
    structured_agent = AgentFactory.create_structured_agent("demo_analyst")
    
    analysis_topic = "Market trends in AI automation for 2024"
    focus_areas = ["Enterprise adoption", "Cost benefits", "Implementation challenges"]
    
    analysis = await structured_agent.analyze_topic(analysis_topic, focus_areas)
    
    print(f"Topic: {analysis['topic']}")
    print(f"Focus Areas: {analysis['focus_areas']}")
    print(f"Success: {analysis['success']}")
    print(f"Processing Time: {analysis['processing_time']:.2f}s")
    
    if analysis['success']:
        analysis_data = analysis['analysis']
        print(f"\nStructured Analysis:")
        print(f"- Summary: {analysis_data['summary'][:150]}...")
        print(f"- Key Findings: {len(analysis_data['key_findings'])} findings")
        print(f"- Recommendations: {len(analysis_data['recommendations'])} recommendations")
        print(f"- Confidence Score: {analysis_data['confidence_score']:.2f}")
    else:
        print(f"Error: {analysis['error']}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    # Configure environment
    os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key-here")
    
    # Run demonstration
    asyncio.run(demonstrate_basic_agents())