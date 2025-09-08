# 📝 Session 2: LangChain Practical Implementation

> **📝 PARTICIPANT PATH CONTENT**
> Prerequisites: Complete [🎯 Observer Path](Session2_LangChain_Foundations.md)
> Time Investment: 2-3 hours
> Outcome: Build production-ready data intelligence agents

## Learning Outcomes

After completing this practical implementation module, you will be able to:

- Create robust data processing chains with error handling  
- Build agents with custom tools for data system integration  
- Implement production-grade memory management strategies  
- Deploy agents with monitoring and reliability patterns  

## Practical Implementation: Building Real-World Data Systems

Now we move from concepts to practice, creating agents that solve actual data engineering problems and provide real value to data teams and infrastructure.

### Exercise Files

Practice with these implementation examples that demonstrate LangChain patterns in action for data systems:

- [`src/session2/langchain_basics_course.py`](src/session2/langchain_basics_course.py) - Foundation patterns and core concepts
- [`src/session2/langchain_agents_course.py`](src/session2/langchain_agents_course.py) - Complete agent implementation with data tools

### Validation Commands

Test your understanding with these commands that verify your implementations work correctly with data scenarios:

```bash
cd src/session2
python langchain_basics.py        # Architecture validation
python langchain_tool_use.py      # Agent workflow testing
```

## Advanced Chain Patterns with Error Handling

Building on the basic chains from the Observer Path, we now implement production-ready patterns that handle real-world data processing challenges.

### Prompt Templates with Validation

Prompt templates create reusable, parameterized prompts with variables, solving the challenge of how to maintain consistency while adapting to different data contexts:

```python
template = """
Role: {role}
Data Analysis Task: {task}
Dataset Context: {context}
Output Format: {format}
"""
```

Define the template with input validation - this creates a flexible framework for various data analysis scenarios:

```python
from langchain.prompts import PromptTemplate

def create_validated_prompt(role, task, context, format):
    """Create prompt template with input validation"""
    # Validate required parameters
    if not all([role, task, context, format]):
        raise ValueError("All template parameters are required")

    template = """
    Role: {role}
    Data Analysis Task: {task}
    Dataset Context: {context}
    Output Format: {format}
    """

    return PromptTemplate(
        template=template,
        input_variables=["role", "task", "context", "format"]
    )
```

### Using Templates with Chains

Combine the template with a chain for dynamic data analysis responses - this is where templates become powerful, adaptive interfaces for data intelligence:

```python
def create_analysis_chain(llm):
    """Create reusable analysis chain with error handling"""
    try:
        prompt = create_validated_prompt(
            role="Data Quality Engineer",
            task="Analyze streaming data anomalies",
            context="Real-time customer behavior data from e-commerce platform",
            format="JSON with severity levels and recommended actions"
        )

        return LLMChain(llm=llm, prompt=prompt)
    except Exception as e:
        print(f"Chain creation failed: {e}")
        return None
```

### Error Handling and Retry Logic

Robust error handling is crucial for production data systems, transforming brittle demos into resilient data infrastructure. Common failures include API rate limits, network timeouts, and service unavailability:

```python
from langchain.callbacks import StdOutCallbackHandler
import time

def run_with_retry(chain, inputs, max_retries=3):
    """Execute chain with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            return chain.run(inputs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e

            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed: {e}")
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    return None
```

### Usage Example with Complete Error Handling

Use the retry function with proper error handling - this ensures your data processing applications maintain uptime and reliability:

```python
def analyze_data_with_resilience(chain, data_report):
    """Analyze data with complete error handling and logging"""
    try:
        result = run_with_retry(
            chain,
            {"data_report": data_report}
        )

        if result:
            print(f"Analysis completed successfully: {result[:100]}...")
            return result
        else:
            print("Analysis failed after all retries")
            return "Unable to complete analysis - please try again later"

    except Exception as e:
        print(f"Critical error in data analysis: {e}")
        return f"Analysis system error: {str(e)}"
```

## Advanced Tool Creation & Integration

Moving beyond basic tools, we create sophisticated data processing capabilities with proper error handling and validation.

### Tool Creation Methods - Extended Implementation

#### Method 3: Production Tool with Full Error Handling

Create production-ready tools with comprehensive error handling and logging:

```python
from langchain.agents import Tool
import logging
import json

def create_production_data_tool():
    """Create enterprise-grade data warehouse tool"""

    def query_data_warehouse_safe(sql_query: str) -> str:
        """Execute SQL query with comprehensive error handling"""
        try:
            # Input validation
            if not sql_query or not isinstance(sql_query, str):
                return "Error: Invalid SQL query provided"

            # Log query attempt
            logging.info(f"Executing query: {sql_query[:100]}...")

            # Simulate database connection and query
            # In production: connect to actual data warehouse
            if "DROP" in sql_query.upper() or "DELETE" in sql_query.upper():
                return "Error: Destructive operations not allowed"

            # Mock successful query execution
            result = {
                "status": "success",
                "rows_returned": 1847,
                "execution_time": "2.3s",
                "query": sql_query[:50] + "..." if len(sql_query) > 50 else sql_query
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logging.error(f"Database query failed: {e}")
            return f"Database connection error: {str(e)}"

    return Tool(
        name="DataWarehouse",
        description="Execute safe SQL queries against enterprise data warehouse with error handling",
        func=query_data_warehouse_safe
    )
```

### Streaming Pipeline Monitoring Tool

Create a comprehensive monitoring tool for real-time data pipelines:

```python
def create_streaming_monitor_tool():
    """Create comprehensive streaming pipeline monitoring tool"""

    def monitor_streaming_pipeline_detailed(pipeline_id: str) -> str:
        """Monitor streaming pipeline with detailed metrics and error detection"""
        try:
            if not pipeline_id:
                return "Error: Pipeline ID required"

            # Simulate comprehensive pipeline monitoring
            # In production: integrate with Apache Kafka, Apache Storm, etc.

            metrics = {
                "pipeline_id": pipeline_id,
                "status": "RUNNING",
                "metrics": {
                    "events_per_second": 15000,
                    "average_latency_ms": 150,
                    "error_rate": 0.02,
                    "consumer_lag": 50
                },
                "health_checks": {
                    "kafka_connection": "HEALTHY",
                    "database_connection": "HEALTHY",
                    "memory_usage": "78%",
                    "cpu_usage": "45%"
                },
                "alerts": []
            }

            # Add alerts based on metrics
            if metrics["metrics"]["error_rate"] > 0.01:
                metrics["alerts"].append("Warning: Error rate above threshold")

            if metrics["metrics"]["consumer_lag"] > 100:
                metrics["alerts"].append("Warning: Consumer lag high")

            return json.dumps(metrics, indent=2)

        except Exception as e:
            return f"Monitoring system error: {str(e)}"

    return Tool(
        name="StreamingMonitor",
        description="Monitor real-time streaming pipelines with comprehensive metrics and alerting",
        func=monitor_streaming_pipeline_detailed
    )
```

### Data Quality Assessment Tool

Build a comprehensive data quality assessment system:

```python
def create_data_quality_tool():
    """Create advanced data quality assessment tool"""

    def assess_data_quality_comprehensive(dataset_path: str) -> str:
        """Perform comprehensive data quality assessment"""
        try:
            if not dataset_path:
                return "Error: Dataset path required"

            # Simulate comprehensive data quality analysis
            # In production: integrate with Great Expectations, Deequ, etc.

            quality_report = {
                "dataset": dataset_path,
                "timestamp": "2024-01-15T10:30:00Z",
                "overall_score": 94.7,
                "dimensions": {
                    "completeness": {
                        "score": 98.2,
                        "null_rate": 1.8,
                        "missing_patterns": ["customer_phone", "secondary_email"]
                    },
                    "validity": {
                        "score": 92.5,
                        "schema_compliance": 98.2,
                        "format_violations": ["date_format", "phone_format"]
                    },
                    "consistency": {
                        "score": 95.1,
                        "duplicate_rate": 2.3,
                        "cross_field_consistency": 97.8
                    },
                    "accuracy": {
                        "score": 91.8,
                        "reference_data_match": 89.5,
                        "business_rule_violations": 12
                    }
                },
                "recommendations": [
                    "Implement phone number validation",
                    "Add date format standardization",
                    "Review duplicate detection logic"
                ]
            }

            return json.dumps(quality_report, indent=2)

        except Exception as e:
            return f"Data quality assessment failed: {str(e)}"

    return Tool(
        name="DataQualityAssessment",
        description="Comprehensive data quality assessment with scoring and recommendations",
        func=assess_data_quality_comprehensive
    )
```

## Agent Workflows & Complex Reasoning

Building sophisticated agents that can handle multi-step data analysis workflows with proper error recovery.

### Tool Calling in Action - Production Implementation

Run the agent with complex data requests that need multiple tools - watch as it breaks down data problems like an experienced data engineer:

```python
def create_production_data_agent():
    """Create production-ready data analysis agent"""

    # Initialize tools
    tools = [
        create_production_data_tool(),
        create_streaming_monitor_tool(),
        create_data_quality_tool()
    ]

    # Configure memory with size limits
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=10,  # Keep last 10 interactions
        return_messages=True
    )

    # Create agent with error handling
    try:
        agent = initialize_agent(
            tools=tools,
            llm=create_llm(),
            agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,  # Show reasoning in development
            handle_parsing_errors=True,  # Graceful error handling
            max_iterations=5  # Prevent infinite loops
        )

        return agent
    except Exception as e:
        print(f"Agent creation failed: {e}")
        return None
```

### Complex Multi-Tool Analysis

Execute sophisticated analysis workflows that require coordination of multiple data systems:

```python
def run_comprehensive_data_analysis():
    """Execute comprehensive data analysis workflow"""

    agent = create_production_data_agent()
    if not agent:
        return "Failed to create agent"

    complex_request = """
    I need a comprehensive analysis of our data infrastructure:

    1. Check the quality of our customer behavior dataset
    2. Monitor the performance of streaming pipeline 'customer-events-v2'
    3. Query the data warehouse for any customer behavior anomalies in the last 24 hours
    4. Provide recommendations based on all findings
    """

    try:
        response = agent.run(complex_request)
        print("=== COMPREHENSIVE DATA ANALYSIS RESULTS ===")
        print(response)
        return response

    except Exception as e:
        print(f"Analysis workflow failed: {e}")
        return f"Workflow error: {str(e)}"
```

### Agent Thought Process - Production Monitoring

With verbose=True, you can see the agent's reasoning - this reveals the sophisticated data analysis decision-making happening behind the scenes:

```text
Thought: I need to analyze data infrastructure comprehensively across multiple systems
Action: DataQualityAssessment with customer behavior dataset
Observation: Quality score 94.7%, some phone format issues identified
Thought: Now I need to check streaming pipeline performance
Action: StreamingMonitor for customer-events-v2 pipeline
Observation: Pipeline healthy, processing 15K events/sec with minimal lag
Thought: Finally, I need to query the warehouse for recent anomalies
Action: DataWarehouse with anomaly detection query for last 24 hours
Observation: Found 3 behavioral pattern changes requiring investigation
Thought: I have all the data - time to synthesize comprehensive recommendations
Final Answer: Your data infrastructure shows good overall health (94.7% quality score) with strong streaming performance (15K events/sec). However, I identified 3 areas needing attention: phone format validation, behavioral anomaly investigation, and consumer lag monitoring. Recommended actions: implement phone validation rules, investigate the 3 detected behavioral changes, and set up proactive lag alerting.
```

## State Persistence & Production Memory

Implement enterprise-grade memory management with persistence and recovery capabilities.

### State Persistence - Production Implementation

Saving memory allows agents to remember previous data analysis sessions across conversations, creating continuity like data team relationships that build analytical understanding over time.

### Enhanced Persistence Functions

Implement robust file-based persistence with error handling and validation:

```python
import json
import os
from datetime import datetime

def save_conversation_robust(memory, filename, metadata=None):
    """Save conversation with metadata and error handling"""
    try:
        # Create backup directory if it doesn't exist
        os.makedirs("conversation_backups", exist_ok=True)

        # Prepare conversation data
        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "messages": []
        }

        # Extract messages from memory
        messages = memory.chat_memory.messages
        for msg in messages:
            conversation_data["messages"].append({
                "type": type(msg).__name__,
                "content": str(msg)
            })

        # Save with backup
        filepath = os.path.join("conversation_backups", filename)
        with open(filepath, 'w') as f:
            json.dump(conversation_data, f, indent=2)

        print(f"✅ Conversation saved: {len(messages)} messages to {filepath}")
        return True

    except Exception as e:
        print(f"❌ Failed to save conversation: {e}")
        return False
```

### Enhanced Loading Functions

Load previous conversations with validation and error recovery:

```python
def load_conversation_robust(memory, filename):
    """Load conversation with validation and error recovery"""
    try:
        filepath = os.path.join("conversation_backups", filename)

        if not os.path.exists(filepath):
            print(f"📝 No previous conversation found at {filepath} - starting fresh")
            return False

        with open(filepath, 'r') as f:
            conversation_data = json.load(f)

        # Validate data structure
        if "messages" not in conversation_data:
            print("⚠️ Invalid conversation file format")
            return False

        messages = conversation_data["messages"]
        metadata = conversation_data.get("metadata", {})

        print(f"📖 Loaded conversation: {len(messages)} messages from {conversation_data.get('timestamp', 'unknown time')}")

        if metadata:
            print(f"📋 Session metadata: {metadata}")

        # Note: Full message reconstruction would require LangChain message objects
        # This is a simplified example showing the persistence pattern

        return True

    except Exception as e:
        print(f"❌ Failed to load conversation: {e}")
        return False
```

### Context Management - Production Specialization

Context gives agents personality and specialized data knowledge, transforming generic AI into domain-specific data experts:

- **Role**: Data Quality Engineer vs ML Pipeline Specialist - different expertise and analytical approaches  
- **Knowledge**: Domain-specific data understanding that shapes analytical responses  
- **Style**: Communication preferences that match data team expectations  

### Creating Specialized Production Agents

Define a function to build specialized data agents with comprehensive configuration:

```python
def create_specialized_production_agent(role_description, tools_list, expertise_context=None):
    """Build production agent with specialized expertise and comprehensive configuration"""

    # Build specialized system prompt
    system_prompt = f"""
    You are {role_description}.

    Core Expertise:
    - Deep knowledge of data engineering best practices
    - Experience with production data systems and reliability
    - Focus on actionable insights and practical recommendations
    - Understanding of compliance and security requirements

    Communication Style:
    - Provide clear, concise analysis with specific recommendations
    - Include relevant metrics and data quality indicators
    - Highlight potential risks and mitigation strategies
    - Structure responses for technical and business audiences

    Additional Context:
    {expertise_context or "No additional context provided"}

    Always maintain focus on data reliability, security, and operational excellence.
    """

    # Configure production-grade memory
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=8,  # Optimal for context without token limits
        return_messages=True
    )

    # Create agent with production configuration
    try:
        agent = initialize_agent(
            tools=tools_list,
            llm=create_llm(),
            agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=False,  # Disable in production
            handle_parsing_errors=True,
            max_iterations=4,  # Prevent runaway execution
            agent_kwargs={"system_message": system_prompt}
        )

        return agent
    except Exception as e:
        print(f"Specialized agent creation failed: {e}")
        return None
```

### Creating Expert Production Agents

Build different specialized data agents for production environments:

```python
# Data Quality Specialist
def create_data_quality_specialist():
    """Create specialized data quality engineering agent"""
    return create_specialized_production_agent(
        role_description="a senior data quality engineer with 8+ years of experience ensuring data reliability and accuracy across enterprise data systems",
        tools_list=[create_data_quality_tool(), create_production_data_tool()],
        expertise_context="Expert in data validation frameworks, quality metrics, and automated testing pipelines. Experienced with Great Expectations, Apache Griffin, and custom validation systems."
    )

# ML Pipeline Expert
def create_ml_pipeline_specialist():
    """Create specialized ML pipeline engineering agent"""
    return create_specialized_production_agent(
        role_description="an ML infrastructure engineer specialized in deploying and monitoring machine learning pipelines at scale",
        tools_list=[create_streaming_monitor_tool(), create_production_data_tool()],
        expertise_context="Expert in MLOps, model deployment, performance monitoring, and pipeline orchestration. Experienced with Kubeflow, MLflow, and production ML system architecture."
    )
```

## Build Your Own Data Intelligence Agent

Create a practical data assistant following this comprehensive structure - this exercise brings together everything you've learned for real data engineering scenarios:

```python
def create_data_intelligence_agent():
    """
    Build comprehensive data intelligence agent

    Implementation Checklist:
    1. ✅ Define tools: data warehouse, streaming monitor, quality checker
    2. ✅ Set up conversation memory for analytical continuity
    3. ✅ Add error handling for data access failures
    4. ✅ Configure specialized expertise and context
    5. ✅ Test with complex multi-step data analysis requests
    """

    # Step 1: Initialize production tools
    tools = [
        create_production_data_tool(),
        create_streaming_monitor_tool(),
        create_data_quality_tool()
    ]

    # Step 2: Configure memory with persistence
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=10,
        return_messages=True
    )

    # Step 3: Create agent with comprehensive error handling
    try:
        agent = initialize_agent(
            tools=tools,
            llm=create_llm(),
            agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,  # Enable for development
            handle_parsing_errors=True,
            max_iterations=5
        )

        print("✅ Data Intelligence Agent created successfully")
        return agent

    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return None

def test_data_intelligence_agent():
    """Test the agent with comprehensive data analysis request"""
    agent = create_data_intelligence_agent()
    if not agent:
        return

    # Test with complex multi-system request
    test_request = """
    Analyze our customer data pipeline performance and check quality metrics:

    1. Assess data quality of customer behavior dataset
    2. Monitor streaming pipeline 'customer-events-v2' performance
    3. Query warehouse for recent processing anomalies
    4. Provide comprehensive recommendations for improvements
    """

    try:
        print("🧠 Running comprehensive data analysis...")
        response = agent.run(test_request)
        print("=" * 50)
        print("📊 ANALYSIS COMPLETE")
        print("=" * 50)
        print(response)

    except Exception as e:
        print(f"❌ Test failed: {e}")

# Execute the test
if __name__ == "__main__":
    test_data_intelligence_agent()
```

## Self-Assessment Checklist

Verify your understanding before moving to advanced topics:

**Core Concepts:**  
- [ ] I can explain LangChain's 4 building blocks (LLM, Tools, Memory, Agent) and their interactions  
- [ ] I understand when to use different chain patterns for data workflows  
- [ ] I can implement error handling and retry logic for production reliability  

**Practical Implementation:**  
- [ ] I can create custom tools with comprehensive error handling  
- [ ] I can build agents that coordinate multiple data systems effectively  
- [ ] I can implement memory persistence for conversation continuity  

**Production Readiness:**  
- [ ] I understand production considerations for agent deployment  
- [ ] I can create specialized agents with domain expertise  
- [ ] I know when to use LangChain vs alternatives for data systems  

## 🎯 Quick Review: Observer Path Concepts

If you need to review fundamental concepts covered in the Observer Path:

**[🎯 Return to Observer Path →](Session2_LangChain_Foundations.md)**

## ⚙️ Next Steps: Advanced Architecture

Ready for enterprise-grade patterns and sophisticated architectures?

**Choose your advanced learning path:**  
- [⚙️ Advanced Agent Architecture](Session2_Advanced_Agent_Architecture.md) - Complex orchestration and workflow patterns  
- [⚙️ Production Memory Systems](Session2_Production_Memory_Systems.md) - Enterprise state management and persistence  
- [⚙️ Enterprise Tool Development](Session2_Enterprise_Tool_Development.md) - Custom integrations and specialized capabilities

---

## 🧭 Navigation

**Previous:** [Session 1 - Foundations →](Session1_Bare_Metal_Agents.md)  
**Next:** [Session 3 - Advanced Patterns →](Session3_Multi_Agent_Implementation.md)

---
