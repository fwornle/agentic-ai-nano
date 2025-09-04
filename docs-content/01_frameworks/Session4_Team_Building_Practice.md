# 📝 Session 4: Team Building Practice - Hands-On CrewAI Orchestration

> **📝 PARTICIPANT PATH CONTENT**
> Prerequisites: Complete 🎯 
    assert len(crew.agents) == 3
    assert len(crew.tasks) == 3
    assert crew.process == Process.sequential
    assert crew.memory == True  # Essential for data context

    print("✅ Data crew creation test passed!")
```

This test verifies that our crew has the expected number of agents and tasks, uses sequential processing, and has memory enabled for context sharing.

Next, let's verify that agents have the correct role assignments:

```python
def test_agent_role_assignments():
    """Test that agents have proper role assignments"""
    agents = create_data_discovery_crew()

    roles = [agent.role for agent in agents]
    expected_roles = ['Lead Data Researcher', 'Data Quality Validator', 'Data Insights Synthesizer']

    for expected_role in expected_roles:
        assert expected_role in roles, f"Missing role: {expected_role}"

    print("✅ Agent role assignment test passed!")
```

This ensures that each agent has been assigned the correct specialized role for effective team collaboration.

### Execution Flow Tests

Now let's test the basic execution workflow:

```python
def test_data_crew_execution():
    """Test basic data crew execution workflow"""
    crew = assemble_data_discovery_crew("Customer transaction data analysis")

    # This would normally run the actual crew
    # For testing, we just verify structure
    assert crew is not None
    assert hasattr(crew, 'kickoff')
    assert crew.cache == True  # Verify performance optimization

    print("✅ Data crew execution test passed!")
```

This test ensures our crew has the necessary execution capabilities and performance optimizations.

Finally, let's verify hierarchical coordination works correctly:

```python
def test_hierarchical_coordination():
    """Test hierarchical crew coordination"""
    crew = create_hierarchical_data_workflow()

    # Verify manager is present and has delegation capability
    manager = crew.agents[0]  # First agent should be the manager
    assert manager.role == 'Data Engineering Manager'
    assert manager.allow_delegation == True

    print("✅ Hierarchical coordination test passed!")
```

This confirms that our hierarchical teams have proper management oversight and delegation capabilities.

### Running the Test Suite

Here's a simple test runner to execute all our crew tests:

```python
def run_crew_tests():
    """Run comprehensive crew testing suite"""

    tests = [
        test_data_crew_creation,
        test_agent_role_assignments,
        test_data_crew_execution,
        test_hierarchical_coordination
    ]

    print("Running CrewAI team tests...")
```

The test runner iterates through each test function and provides feedback on success or failure:

```python
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed: {test.__name__} - {str(e)}")

    print("All tests completed!")

# Execute tests
if __name__ == "__main__":
    run_crew_tests()
```

This provides comprehensive testing coverage to ensure your CrewAI teams function correctly before deployment.

## Communication and Memory Patterns

How agents share information and build on each other's work - creating true collaboration rather than just sequential processing for data engineering workflows.

First, let's create a crew with enhanced memory capabilities:

```python
# Memory-enabled communication for data processing context
def create_memory_enabled_data_crew():
    """Data processing crew with enhanced memory and communication"""

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        memory=True,  # Essential for maintaining data processing context
        verbose=True,
        embedder={
            "provider": "openai",
            "config": {"model": "text-embedding-3-small"}
        }
    )

    return crew
```

This configuration enables agents to remember and reference previous work across the team.

For advanced communication patterns, context sharing strategies, and sophisticated memory management, see ⚙️ [Advanced Orchestration](Session4_Advanced_Orchestration.md).

## Practical Exercises

Try these hands-on exercises to reinforce your learning:

### Exercise 1: Build a Custom Data Team

Create a three-agent crew for analyzing social media data:

1. **Social Media Researcher**: Finds and catalogs social media data sources
2. **Sentiment Analysis Specialist**: Analyzes emotional content and trends
3. **Engagement Metrics Analyst**: Measures and reports on engagement patterns

### Exercise 2: Implement Hierarchical Coordination

Build a hierarchical crew with a manager coordinating specialized agents.

### Exercise 3: Advanced Task Dependencies

Create workflows where tasks build upon each other's results with context sharing.

---

## 🧭 Navigation

**Previous:** [Session 3 - Advanced Patterns →](Session3_Multi_Agent_Implementation.md)  
**Next:** [Session 5 - Type-Safe Development →](Session5_PydanticAI_Type_Safe_Agents.md)

---
