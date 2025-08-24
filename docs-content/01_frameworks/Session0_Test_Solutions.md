# Session 0: Introduction to Agent Frameworks & Patterns - Test Solutions

## 📝 Multiple Choice Test

### Question 1: Agentic Patterns

### Which agentic pattern involves an agent evaluating and improving its own outputs?

A) Multi-Agent  
B) Planning  
C) Tool Use  
D) Reflection ✅  
### Correct Answer: D) Reflection

**Explanation:** The reflection pattern specifically involves agents evaluating and improving their own outputs through iterative self-assessment. This pattern includes generating initial output, reflecting on quality, and refining based on critique.

---

### Question 2: ReAct Pattern

### The ReAct pattern combines which two key capabilities?

A) Reflecting and Acting  
B) Reading and Acting  
C) Retrieving and Acting  
D) Reasoning and Acting ✅  
### Correct Answer: D) Reasoning and Acting

**Explanation:** ReAct stands for Reasoning and Acting, combining these capabilities in iterative loops. The agent reasons about what to do next, takes action, observes results, and continues the reasoning-action cycle.

---

### Question 3: Performance-Optimized Framework

### Which framework is best suited for high-performance applications with minimal resource usage?

A) PydanticAI  
B) LangChain  
C) Agno ✅  
D) CrewAI  
### Correct Answer: C) Agno

**Explanation:** Agno is optimized for performance with claims of 50x more memory efficiency and 10,000x faster agent instantiation, making it ideal for high-performance applications.

---

### Question 4: Multi-Agent Advantage

### What is the primary advantage of the Multi-Agent pattern?

A) Lower resource usage  
B) Reduced complexity  
C) Specialized expertise collaboration ✅  
D) Faster execution  
### Correct Answer: C) Specialized expertise collaboration

**Explanation:** Multi-Agent patterns allow different agents with specialized skills to collaborate on complex problems, leveraging the expertise of each agent for optimal results.

---

### Question 5: Type Safety Framework

### Which framework emphasizes type safety through schema validation?

A) PydanticAI ✅  
B) CrewAI  
C) LangChain  
D) Agno  
### Correct Answer: A) PydanticAI

**Explanation:** PydanticAI is built around Pydantic models for strong type safety and schema validation, ensuring data integrity throughout the agent system.

---

### Question 6: Planning Pattern Use Case

### The Planning pattern is most useful for:

A) Simple query-response interactions  
B) Real-time data processing  
C) Static content generation  
D) Complex multi-step workflows ✅  
### Correct Answer: D) Complex multi-step workflows

**Explanation:** Planning patterns excel at breaking down complex tasks into manageable, sequenced subtasks, making them ideal for complex multi-step workflows.

---

### Question 7: Tool Selection Logic

### In the Tool Use pattern, what determines which tool an agent selects?

A) Random selection  
B) Execution speed  
C) Task requirements and tool descriptions ✅  
D) Tool availability  
### Correct Answer: C) Task requirements and tool descriptions

**Explanation:** Agents analyze task needs against available tool capabilities and descriptions to make intelligent selection decisions about which tools to use.

---

### Question 8: Graph-Based Architecture

### Which framework uses a graph-based architecture for precise control flow?

A) PydanticAI  
B) CrewAI  
C) LangGraph ✅  
D) Agno  
### Correct Answer: C) LangGraph

**Explanation:** LangGraph extends LangChain with graph-based architecture using nodes and edges for precise control flow, allowing complex agent workflows.

---

### Question 9: Framework Benefits

### The primary benefit of using agent frameworks over bare metal implementation is:

A) Pre-built components and patterns ✅  
B) Simpler deployment  
C) Lower costs  
D) Better performance  
### Correct Answer: A) Pre-built components and patterns

**Explanation:** Frameworks provide tested implementations of common patterns, reducing development time and complexity while ensuring reliability.

---

### Question 10: Collaboration Patterns

### Which collaboration pattern involves agents working on different aspects simultaneously?

A) Parallel Processing ✅  
B) Hierarchical Teams  
C) Debate and Consensus  
D) Sequential Processing  
### Correct Answer: A) Parallel Processing

**Explanation:** Parallel processing involves multiple agents working simultaneously on different aspects of a problem, enabling faster overall completion.

---

### Question 11: Bare Metal Implementation

### When would you choose bare metal Python implementation over frameworks?

A) Enterprise integration  
B) Production applications  
C) Team collaboration projects  
D) Learning fundamentals and custom research ✅  
### Correct Answer: D) Learning fundamentals and custom research

**Explanation:** Bare metal implementation provides complete control and understanding of underlying mechanisms, making it ideal for learning and custom research.

---

### Question 12: Reflection Pattern Phases

### The reflection pattern typically involves how many phases?

A) 2 phases: Generate and Reflect  
B) 4 phases: Generate, Reflect, Refine, Validate  
C) 5 phases: Generate, Reflect, Refine, Test, Deploy  
D) 3 phases: Generate, Reflect, Refine ✅  
### Correct Answer: D) 3 phases: Generate, Reflect, Refine

**Explanation:** The core reflection pattern involves generating initial output, reflecting on quality, then refining based on critique - three essential phases.

---

### Question 13: Enterprise Framework Features

### What makes ADK particularly suitable for enterprise applications?

A) Fastest execution speed  
B) Built-in security, monitoring, and Google Cloud integration ✅  
C) Open source licensing  
D) Simplest learning curve  
### Correct Answer: B) Built-in security, monitoring, and Google Cloud integration

**Explanation:** ADK provides enterprise features like security, compliance, monitoring, and cloud-native integration, making it suitable for business applications.

---

### Question 14: Manager Agent Role

### In multi-agent systems, what is the role of a "Manager Agent"?

A) Store data and state  
B) Provide user interface  
C) Coordinate worker agents and manage interactions ✅  
D) Execute all tasks directly  
### Correct Answer: C) Coordinate worker agents and manage interactions

**Explanation:** Manager agents orchestrate team activities and handle inter-agent communication, coordinating the work of specialized worker agents.

---

### Question 15: Pattern Selection for Real-time Data

### Which pattern would be most appropriate for a task requiring real-time stock price analysis?

A) Multi-Agent (for collaboration)  
B) Reflection (for self-improvement)  
C) Tool Use (for accessing live data APIs) ✅  
D) Planning (for multi-step workflows)  
### Correct Answer: C) Tool Use (for accessing live data APIs)

**Explanation:** Real-time stock analysis requires accessing external APIs for current market data, making Tool Use the most appropriate pattern for this scenario.

---

## Performance Scoring

- **15/15 Correct**: Excellent understanding of agent frameworks and patterns
- **12-14 Correct**: Good grasp with minor knowledge gaps
- **9-11 Correct**: Adequate understanding, review specific patterns and frameworks
- **6-8 Correct**: Needs review of core concepts and framework differences
- **0-5 Correct**: Recommend re-reading session materials and practicing with examples

---

## Key Concepts Review

### Five Core Agentic Patterns

1. **Reflection**: Self-evaluation and iterative improvement
2. **Tool Use**: Dynamic tool selection and external capability extension
3. **ReAct**: Reasoning and Acting in interactive loops
4. **Planning**: Multi-step workflow decomposition and execution
5. **Multi-Agent**: Specialized collaboration and expertise sharing

### Framework Comparison Matrix

- **LangChain**: Comprehensive ecosystem with extensive tool integration
- **LangGraph**: Graph-based workflows with precise control flow
- **CrewAI**: Team-oriented collaboration and role-based agents
- **PydanticAI**: Type-safe agents with schema validation
- **Atomic Agents**: Modular, composable agent components
- **ADK**: Enterprise-grade with security and monitoring
- **Agno**: Performance-optimized for high-throughput applications

### Pattern Selection Guidelines

- **Simple Tasks**: Direct prompting or basic Tool Use
- **Quality-Critical Work**: Reflection pattern for iterative improvement
- **External Data Needs**: Tool Use for API and database access
- **Complex Workflows**: Planning pattern for step-by-step execution
- **Specialized Collaboration**: Multi-Agent for expert coordination
- **Real-time Processing**: ReAct for dynamic response handling

---

## Answer Summary

1. B  2. B  3. C  4. B  5. D  6. B  7. C  8. B  9. C  10. B  11. B  12. B  13. B  14. C  15. B

---

[← Back to Session 0](Session0_Introduction_to_Agent_Frameworks_Patterns.md) | [Next: Session 1 →](Session1_Bare_Metal_Agents.md)
