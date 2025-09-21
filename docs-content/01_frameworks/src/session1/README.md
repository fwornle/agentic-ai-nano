# Session 1: Bare Metal Agents - Source Code

This directory contains the complete implementation of all five fundamental agentic patterns covered in Session 1.

## 📁 Files Overview

### Core Implementation Files (Course Content)

- **`base_agent_course.py`** - Foundation BaseAgent class matching course content
- **`reflection_agent_course.py`** - ReflectiveAgent with performance optimization
- **`tool_use_agent_course.py`** - ToolUseAgent with cloud service integration
- **`planning_agent_course.py`** - PlanningAgent for workflow orchestration
- **`react_agent_course.py`** - ReActAgent with adaptive processing
- **`multi_agent_system_course.py`** - Multi-agent coordination system
- **`demo_runner_course.py`** - Comprehensive demonstration of all patterns

### Alternative Implementation Files

- **`base_agent.py`** - Alternative agent architecture implementation
- **`reflection_agent.py`** - Alternative reflection pattern implementation
- **`react_agent.py`** - Alternative ReAct pattern implementation
- **`tool_use_agent.py`** - Alternative tool use implementation
- **`multi_agent_system.py`** - Alternative multi-agent system
- **`tools.py`** - Tool definitions and utilities
- **`test_agents.py`** - Test suite for agent implementations
- **`demo_runner.py`** - Alternative demo runner

## 🚀 Quick Start

### Run Individual Patterns

```bash
# Test BaseAgent foundation
python base_agent_course.py

# Test ReflectiveAgent optimization
python reflection_agent_course.py

# Test ToolUseAgent integration
python tool_use_agent_course.py

# Test PlanningAgent orchestration
python planning_agent_course.py

# Test ReActAgent adaptation
python react_agent_course.py

# Test Multi-Agent coordination
python multi_agent_system_course.py
```

### Run Complete Demo

```bash
# Full demonstration (comprehensive)
python demo_runner_course.py

# Quick demonstration (faster)
python demo_runner_course.py --quick
```

## 🎯 Pattern Implementations

### 1. BaseAgent Foundation (`base_agent_course.py`)

**Key Features:**
- Cloud-native deployment architecture
- Cost optimization with model selection
- Kubernetes resource management
- Comprehensive monitoring integration

**Run Example:**
```python
from base_agent_course import BaseAgent

agent = BaseAgent(model_name="gpt-4", max_memory_mb=512)
result = agent.run({"type": "analytics_query", "content": "Analyze revenue trends"})
print(result)
```

### 2. Reflection Pattern (`reflection_agent_course.py`)

**Key Features:**
- Performance analysis and optimization
- Cost tracking across operations
- Strategy adaptation based on metrics
- Historical performance trending

**Run Example:**
```python
from reflection_agent_course import ReflectiveAgent

agent = ReflectiveAgent(model_name="gpt-4")
metrics = {
    "throughput_gb_per_hour": 150.5,
    "cost_per_gb": 0.02,
    "error_rate": 2.3,
    "queue_depth": 15,
    "avg_latency_ms": 450
}
analysis = agent.run_performance_analysis(metrics)
print(analysis)
```

### 3. Tool Use Pattern (`tool_use_agent_course.py`)

**Key Features:**
- Cloud service integration (S3, PostgreSQL, Kafka, Airflow, Elasticsearch, Grafana)
- Workflow orchestration across services
- Comprehensive error handling and retry logic
- Real-time monitoring and status updates

**Run Example:**
```python
from tool_use_agent_course import ToolUseAgent

agent = ToolUseAgent()
result = agent.execute_tool("query_data_lake", bucket_name="analytics-lake")
print(result)
```

### 4. Planning Pattern (`planning_agent_course.py`)

**Key Features:**
- Intelligent resource allocation
- Infrastructure-aware planning
- Cost-optimized execution strategies
- Parallel processing opportunities identification

**Run Example:**
```python
from planning_agent_course import PlanningAgent

agent = PlanningAgent()
batch = {
    "size_gb": 50,
    "data_types": ["JSON", "Parquet"],
    "priority": "real-time",
    "sla_hours": 2,
    "processing_type": "analytics",
    "budget": 100
}
plan = agent.create_processing_plan(batch)
print(plan)
```

### 5. ReAct Pattern (`react_agent_course.py`)

**Key Features:**
- Reasoning transparency with thought processes
- Adaptive strategy adjustment based on failures
- Multiple retry mechanisms with learning
- Comprehensive failure analysis and recovery

**Run Example:**
```python
from react_agent_course import ReActAgent

agent = ReActAgent()
batch = {
    "size_gb": 25,
    "source": "legacy_system",
    "validation_errors": 100,
    "data_types": ["CSV", "XML"]
}
result = agent.process_with_reasoning(batch, max_retries=3)
print(result)
```

### 6. Multi-Agent System (`multi_agent_system_course.py`)

**Key Features:**
- Specialized agents for each pipeline stage
- Coordinated execution with dependency management
- Quality-based processing strategy selection
- Comprehensive pipeline analytics and monitoring

**Run Example:**
```python
from multi_agent_system_course import DataPipelineCoordinator

coordinator = DataPipelineCoordinator()
batch = {
    "batch_id": "test_batch_001",
    "sources": ["s3", "database", "api"],
    "size_multiplier": 1.0
}
result = coordinator.orchestrate_data_pipeline(batch)
print(result)
```

## 💡 Key Differences: Course vs Alternative Files

### Course Files (`*_course.py`)
- **Focused on data processing use cases**
- **Production-ready with enterprise features**
- **Kubernetes and cloud-native architecture**
- **Cost optimization and monitoring**
- **Matches Session 1 course content exactly**

### Alternative Files (`*.py`)
- **General-purpose agent architecture**
- **Framework-agnostic implementations**
- **Focus on agent communication patterns**
- **Educational examples and testing**

## 🧪 Testing and Validation

All course files include:
- ✅ **Runnable Examples**: Each file can be executed standalone
- ✅ **Error Handling**: Comprehensive exception handling and graceful degradation
- ✅ **Monitoring**: Built-in metrics and logging
- ✅ **Documentation**: Inline comments and docstrings
- ✅ **Production Ready**: Enterprise-scale patterns and practices

## 📈 Expected Output

When running the demo, you'll see:

1. **Real-time processing metrics** and performance tracking
2. **Cost analysis** and optimization decisions
3. **Resource allocation** and infrastructure management
4. **Agent coordination** and workflow orchestration  
5. **Adaptive learning** and strategy improvements
6. **Quality assessments** and compliance monitoring

## 🔧 Dependencies

All files are designed to run with minimal dependencies:
- **Python 3.7+** (standard library only)
- **No external packages required** for basic functionality
- **Optional**: pandas for advanced data processing (mocked in course files)

This ensures you can run and experiment with the code immediately without complex environment setup.

---

**Next Step**: Proceed to [Session 2: LangChain Foundations](../../Session2_LangChain_Foundations.md) to see how these patterns translate to framework-based implementations.