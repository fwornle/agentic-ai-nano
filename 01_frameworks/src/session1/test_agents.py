# src/session1/test_agents.py
"""
Comprehensive test suite for bare metal agent implementations.
"""

import asyncio
from reflection_agent import ReflectionAgent
from tool_use_agent import ToolUseAgent
from react_agent import ReActAgent
from tools import CalculatorTool, WebSearchTool
from multi_agent_system import AgentCoordinator


class MockLLMClient:
    """Mock LLM client for testing without real API calls"""
    
    def __init__(self):
        self.call_count = 0
    
    async def chat(self, prompt: str) -> str:
        self.call_count += 1
        
        # Return contextually appropriate responses
        if "critique" in prompt.lower():
            return "SATISFACTORY - The response is clear and accurate."
        elif "json" in prompt.lower() and "needs_tools" in prompt:
            return '{"needs_tools": true, "reasoning": "Math calculation needed", "relevant_tools": ["calculator"]}'
        elif "json" in prompt.lower() and "action" in prompt:
            return '{"action": "calculator", "action_input": {"expression": "15 + 25"}, "reasoning": "Need to calculate"}'
        elif "thought" in prompt.lower():
            return "I need to calculate this mathematical expression using the calculator tool."
        else:
            return "This is a test response demonstrating agent functionality."


# Test individual agent patterns
async def test_reflection_agent():
    """Test reflection agent with self-improvement"""
    print("\n🔄 Testing Reflection Agent...")
    llm_client = MockLLMClient()
    agent = ReflectionAgent("TestReflection", llm_client, max_iterations=2)
    
    response = await agent.process_message("Explain the benefits of renewable energy.")
    
    assert isinstance(response, str) and len(response) > 0
    assert hasattr(agent, 'reflection_history')
    print(f"  ✓ Reflection agent working correctly")


async def test_tool_use_agent():
    """Test tool use agent with calculator"""
    print("\n🔧 Testing Tool Use Agent...")
    llm_client = MockLLMClient()
    calculator = CalculatorTool()
    agent = ToolUseAgent("TestToolUse", llm_client, tools=[calculator])
    
    response = await agent.process_message("What is 25 * 4?")
    
    assert isinstance(response, str) and len(response) > 0
    stats = agent.get_tool_usage_stats()
    print(f"  ✓ Tool use agent executed {stats.get('total_uses', 0)} tool operations")


async def test_react_agent():
    """Test ReAct agent with visible reasoning"""
    print("\n🧐 Testing ReAct Agent...")
    llm_client = MockLLMClient()
    calculator = CalculatorTool()
    agent = ReActAgent("TestReAct", llm_client, tools=[calculator], max_steps=3)
    
    response = await agent.process_message("Calculate the square of 12")
    
    assert "Step" in response  # Should show reasoning steps
    analysis = agent.get_react_analysis()
    print(f"  ✓ ReAct agent completed reasoning in {analysis.get('average_steps', 0):.1f} average steps")


async def test_multi_agent_system():
    """Test multi-agent coordination"""
    print("\n🔗 Testing Multi-Agent System...")
    coordinator = AgentCoordinator()
    llm_client = MockLLMClient()
    
    # Create specialized agents
    calculator_agent = ToolUseAgent("Calculator", llm_client, [CalculatorTool()])
    reflection_agent = ReflectionAgent("Reviewer", llm_client)
    
    # Register agents
    coordinator.register_agent(calculator_agent)
    coordinator.register_agent(reflection_agent)
    
    # Test collaborative task
    task = "Calculate 15% tip on $80 and review the calculation"
    roles = {
        "Calculator": "Calculate 15% of $80",
        "Reviewer": "Review the calculation for accuracy"
    }
    
    result = await coordinator.collaborative_task(task, roles)
    stats = coordinator.get_system_stats()
    
    assert stats["total_agents"] == 2
    print(f"  ✓ Multi-agent system coordinated {stats['total_agents']} agents")
    print(f"  ✓ Processed {stats['total_messages']} inter-agent messages")


# Main test runner
async def run_comprehensive_tests():
    """Run all bare metal agent tests"""
    print("=== Bare Metal Agent Test Suite ===")
    
    await test_reflection_agent()
    await test_tool_use_agent()
    await test_react_agent()
    await test_multi_agent_system()
    
    print("\n✓ All tests passed! Your bare metal agents are working correctly.\n")


if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())