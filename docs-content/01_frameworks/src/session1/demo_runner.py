# src/session1/demo_runner.py
"""
Comprehensive demonstration of all bare metal agent patterns.
"""

import asyncio
import os
from multi_agent_system import AgentCoordinator
from reflection_agent import ReflectionAgent
from tool_use_agent import ToolUseAgent
from react_agent import ReActAgent
from tools import CalculatorTool, WebSearchTool, FileOperationTool
from test_agents import MockLLMClient


async def demo_bare_metal_agents():
    """Comprehensive demonstration of all agent patterns"""
    print("=== Bare Metal Agent Framework Demo ===")
    print("Demonstrating the five core agentic patterns\n")
    
    # Setup
    llm_client = MockLLMClient()
    coordinator = AgentCoordinator()
    
    # Create demo data directory
    os.makedirs("./demo_data", exist_ok=True)
    
    # Create specialized agents
    calculator_tool = CalculatorTool()
    search_tool = WebSearchTool()
    file_tool = FileOperationTool(["./demo_data/"])
    
    # 1. Reflection Agent - Self-improving responses
    print("🔄 Creating Reflection Agent (self-improvement)")
    reflection_agent = ReflectionAgent("SelfImprover", llm_client, max_iterations=2)
    coordinator.register_agent(reflection_agent)
    
    # 2. Tool Use Agent - Smart tool selection
    print("🔧 Creating Tool Use Agent (smart tool selection)")
    tool_agent = ToolUseAgent("ToolExpert", llm_client, [calculator_tool, file_tool])
    coordinator.register_agent(tool_agent)
    
    # 3. ReAct Agent - Transparent reasoning
    print("🧐 Creating ReAct Agent (visible reasoning)")
    react_agent = ReActAgent("Reasoner", llm_client, [calculator_tool, search_tool], max_steps=5)
    coordinator.register_agent(react_agent)
    
    print(f"\n✓ Created {coordinator.get_system_stats()['total_agents']} specialized agents")
    
    # Demonstration scenarios
    print("\n=== Demonstration Scenarios ===")
    
    # Scenario 1: Complex calculation with reasoning
    print("\n1. Complex Mathematical Problem:")
    task1 = "Calculate compound interest: $1000 at 5% annually for 3 years"
    result1 = await coordinator.route_message(task1, "Reasoner")
    print(f"Result: {result1[:200]}...")
    
    # Scenario 2: Multi-agent collaboration
    print("\n2. Collaborative Analysis:")
    task2 = "Analyze the cost-benefit of solar panels for a home"
    roles = {
        "ToolExpert": "Calculate potential energy savings and costs",
        "SelfImprover": "Create a comprehensive recommendation report",
        "Reasoner": "Research and reason through the decision factors"
    }
    result2 = await coordinator.collaborative_task(task2, roles)
    print(f"Collaborative result completed with {len(roles)} agents")
    
    # System statistics
    stats = coordinator.get_system_stats()
    print(f"\n=== Final Statistics ===")
    print(f"Total agents: {stats['total_agents']}")
    print(f"Messages processed: {stats['total_messages']}")
    print(f"Most active agent: {stats.get('most_active_agent', 'N/A')}")
    
    print("\n✓ Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(demo_bare_metal_agents())