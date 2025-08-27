# Session 0: Introduction to Agent Frameworks & Patterns

Modern AI development has evolved from simple prompt-response interactions to sophisticated agent systems that can reason, use tools, and collaborate. This session covers the five core patterns that power every production agent system and compares the leading frameworks used to implement them.

![Agent Evolution Overview](images/agent-evolution-overview.png)

---

## Part 1: From Prompts to Agents

#### The Evolution of AI Interaction

The journey from simple prompt-response to sophisticated agent systems:

![Agent Evolution Overview](images/agent-evolution-overview.png)

```python

# Traditional prompt-response (limited)

response = llm.generate("What's the weather today?")

# ❌ No context, no tools, no reasoning

# Modern agent approach (powerful)

agent = Agent(tools=[weather_tool, calendar_tool])
response = agent.run("Plan my outdoor activities for this week")

# ✅ Uses tools, plans ahead, considers context

```

#### What Makes an Agent "Agentic"?

Four key characteristics define agentic systems:

1. **Autonomy**: Makes decisions without constant human input
2. **Reactivity**: Responds to environmental changes
3. **Proactivity**: Takes initiative toward goals
4. **Social Ability**: Interacts with other agents/humans

---

## Part 2: The Five Core Agentic Patterns

Every agent framework implements these fundamental patterns:

![Overview of LLM Patterns](images/agentic-5-patterns.png)

#### Pattern 1: Reflection

**Purpose**: Self-improvement through self-evaluation

The Reflection pattern addresses a fundamental challenge: LLMs often produce outputs that "sound good" but may have subtle errors or miss important aspects. By implementing a self-review cycle, agents can catch and correct their own mistakes before finalizing responses.

**How it works:**

- Generate initial response
- Critically evaluate the output ("Was that complete? Anything missing?")
- Revise and improve based on self-critique
- No additional models needed - just structured prompting

```python

# Reflection pattern example

response = agent.generate(task)
reflection = agent.reflect_on(response)
improved_response = agent.improve_based_on(reflection)

# Real-world implementation
initial = agent.answer("Explain database indexing")
critique = agent.evaluate(initial, 
    prompts=["Is this technically accurate?",
             "Are all key concepts covered?",
             "Would a beginner understand this?"])
final = agent.revise(initial, critique)
```

**Benefits:** Dramatically reduces errors in code generation, summaries, and detail-heavy tasks. Gives the model a "pause button and mirror" to double-check its work.

![Reflection Pattern](images/reflection-pattern.png)

#### Pattern 2: Tool Use

**Purpose**: Extending capabilities through external tools

LLMs have knowledge cutoffs and can't access your databases, files, or real-time data. The Tool Use pattern solves this by connecting models to external resources, transforming them from isolated text generators into systems that can fetch real data and perform actual operations.

**Key insight:** Your LLM doesn't need to know everything - it just needs to know how to fetch what it needs.

**Common tool integrations:**

- Vector databases for semantic search
- APIs (Stripe, WolframAlpha, internal endpoints)
- Code execution environments (REPL, sandboxes)
- File systems and databases
- Web search and scraping tools

```python

# Tool use pattern example

tools = [calculator, web_search, file_reader]
agent = Agent(tools=tools)
result = agent.run("Calculate the GDP growth rate for France in 2023")

# Production implementation with function calling
tools = [
    {"name": "query_db", "func": database.execute},
    {"name": "search_web", "func": web_api.search},
    {"name": "run_code", "func": sandbox.execute}
]
agent = Agent(tools=tools, function_calling=True)
# Agent stops hallucinating and starts pulling real data
```

**Implementation requirements:** Function-calling capabilities, routing logic, error handling, and often frameworks like LangChain or Semantic Kernel for orchestration.

**Result:** Agents stop guessing and start working with real, verifiable data.

![Tool Use Pattern](images/tool-use-pattern.png)

#### Pattern 3: ReAct (Reasoning + Acting)

**Purpose**: Iterative reasoning and action cycles

ReAct combines Reflection and Tool Use into a powerful loop where the agent thinks and acts iteratively. Instead of answering everything in one shot, the model reasons step-by-step and adjusts its actions as it learns more. This transforms agents from reactive responders to navigators that can adapt in real-time.

**The ReAct Loop:**

1. **Reason** about the current situation
2. **Act** based on that reasoning
3. **Observe** the results
4. **Update** understanding and repeat

**Real-world example:**

- Goal: "Find the user's recent unpaid invoices"
- Step 1: Query payments database
- Step 2: Notice results are outdated
- Step 3: Check with user for date range
- Step 4: Adjust query and repeat

```python

# ReAct pattern: Thought -> Action -> Observation -> Thought

while not task_complete:
    thought = agent.think(current_state)
    action = agent.decide_action(thought)  
    observation = agent.execute(action)
    current_state = agent.update_state(observation)

# Production implementation
class ReActAgent:
    def solve(self, task):
        context = {"task": task, "history": []}
        
        while not self.is_complete(context):
            thought = self.reason(context)  # "Need user data from DB"
            action = self.select_tool(thought)  # Choose query_database
            result = self.execute(action)  # Run the query
            context = self.update(context, thought, action, result)
            
            # Agent can now course-correct based on results
            if "error" in result:
                thought = "Query failed, trying alternative approach..."
```

**Requirements for ReAct:**

- Tools for taking action
- Memory for keeping context
- Reasoning loop to track progress

**Why it matters:** ReAct makes agents flexible. Instead of rigid scripts, they think through each step, adapt in real-time, and course-correct when new information arrives.

![ReAct Pattern](images/react-pattern.png)

#### Pattern 4: Planning

**Purpose**: Breaking complex tasks into manageable steps

LLMs excel at quick answers but struggle with multi-step tasks. The Planning pattern transforms agents from reactive helpers into proactive problem-solvers by breaking complex goals into structured, manageable steps that can be executed systematically.

**Key insight:** Intelligence isn't just about answers - it's about how those answers are formed. The process matters.

**How Planning works:**

1. Analyze the complex goal
2. Decompose into logical sub-tasks
3. Sequence steps appropriately
4. Execute each step methodically
5. Track progress and adjust as needed

**Real-world example:**

- Request: "Help me launch a product"
- Agent creates plan:
  1. Define target audience
  2. Design landing page
  3. Set up email campaigns
  4. Draft announcement copy
  5. Schedule social media posts
- Then tackles each part systematically

```python

# Planning pattern example

plan = agent.create_plan("Organize a team meeting")

# Plan: [1. Check calendars, 2. Find common time, 3. Book room, 4. Send invites]

for step in plan:
    agent.execute_step(step)

# Advanced implementation with dynamic planning
class PlanningAgent:
    def execute_task(self, goal):
        # Break down the complex goal
        plan = self.decompose(goal)
        
        # Store plan for persistence (can resume later)
        self.save_plan(plan)
        
        for step in plan:
            result = self.execute_step(step)
            
            # Dynamically adjust plan based on results
            if result.requires_replanning:
                plan = self.revise_plan(plan, result)
        
        return self.summarize_results()
```

**Implementation approaches:**

- Embed planning in prompts ("First, break this task into steps...")
- Let the model generate its own plans dynamically
- Store plans for persistence and resumability
- Use hierarchical planning for complex projects

**Result:** Agents move from reactive to proactive, handling workflows and multi-step tasks with systematic precision.

![Planning Pattern](images/planning-pattern.png)

#### Pattern 5: Multi-Agent Collaboration

**Purpose**: Specialized agents working together

Why rely on one generalist agent when you can have a team of specialists? The Multi-Agent pattern assigns different roles to different agents, each handling their piece of the puzzle. They collaborate, iterate, and sometimes even debate to produce superior results.

**Key insight:** The magic happens when agents disagree - that's when you get sharper insights and deeper thinking.

**Typical multi-agent roles:**

- **Researcher**: Gathers information and facts
- **Planner**: Outlines steps and strategies
- **Coder**: Writes implementation code
- **Reviewer**: Double-checks everything for quality
- **PM**: Keeps the team coordinated and on track

**Collaboration dynamics:**

- Agents communicate through a controller or message bus
- Each agent has a specific role and expertise area
- They can critique each other's work
- Iterative refinement through discussion

```python

# Multi-agent pattern

research_agent = Agent(role="researcher", tools=[web_search])
writer_agent = Agent(role="writer", tools=[document_tools])
editor_agent = Agent(role="editor", tools=[grammar_check])

result = orchestrate([research_agent, writer_agent, editor_agent], task="Write report")

# Advanced multi-agent implementation
class MultiAgentSystem:
    def __init__(self):
        self.agents = {
            "researcher": ResearchAgent(tools=[web_search, arxiv_api]),
            "architect": DesignAgent(speciality="system_design"),
            "developer": CodingAgent(languages=["python", "javascript"]),
            "tester": QAAgent(tools=[test_runner, coverage_analyzer]),
            "reviewer": ReviewAgent(focus=["security", "performance"])
        }
    
    def execute(self, project):
        # Agents work in coordinated phases
        research = self.agents["researcher"].investigate(project)
        design = self.agents["architect"].create_design(research)
        
        # Multiple agents can work in parallel
        implementation = self.agents["developer"].build(design)
        tests = self.agents["tester"].create_tests(design)
        
        # Agents review and critique each other's work
        review = self.agents["reviewer"].evaluate(implementation, tests)
        
        # Iterate based on feedback
        if review.has_issues:
            self.refine_with_feedback(review.feedback)
        
        return self.compile_results()
```

**Implementation approaches:**

- Simple: Give each agent a name and job description
- Intermediate: Let agents message each other through a controller
- Advanced: Implement voting, consensus mechanisms, and conflict resolution

**Benefits:**

- Specialized expertise in each domain
- Parallel processing of complex tasks
- Higher quality through peer review
- Emergent problem-solving through collaboration

![Multi-Agent Pattern](images/multi-agent-pattern.png)

---

### Part 3: Framework Landscape Overview


#### Framework Categories

Modern agent frameworks fall into three main categories:

```python

# 1. Development-Focused (Learning & Prototyping)

frameworks = ["LangChain", "LangGraph"] 

# 2. Production-Focused (Enterprise Deployment)

frameworks = ["PydanticAI", "Agno", "Google ADK"]

# 3. Modular/Atomic (Compositional Architecture)

frameworks = ["Atomic Agents", "CrewAI"]
```

#### Framework Comparison Matrix

![Framework Comparison Matrix](images/framework-comparison-matrix.png)

### Enterprise Framework Analysis

| Framework | Production Ready | Enterprise Adoption | Primary Use Case |
|-----------|------------------|-------------------|------------------|
| **LangChain** | ⭐⭐⭐ | Most popular, modular orchestration | Prototyping, educational systems |
| **LangGraph** | ⭐⭐⭐⭐ | Complex state workflows | Advanced automation pipelines |
| **CrewAI** | ⭐⭐⭐⭐ | Role-based multi-agent systems | Content creation, research automation |
| **PydanticAI** | ⭐⭐⭐⭐⭐ | Type-safe, FastAPI-style development | Production APIs, structured outputs |
| **Atomic Agents** | ⭐⭐⭐⭐ | Microservice architectures | Modular enterprise systems |
| **Google ADK** | ⭐⭐⭐⭐⭐ | Google Cloud native | Enterprise Google Workspace integration |
| **Agno** | ⭐⭐⭐⭐ | Production monitoring focus | Deployed agent oversight |

**2025 Industry Selection Guidelines:**

```python

# Framework selection decision tree

if use_case == "learning_prototyping":
    choose(LangChain, CrewAI)  # Fastest onboarding
elif use_case == "enterprise_production":
    choose(PydanticAI, Google_ADK)  # Type safety + monitoring
elif use_case == "complex_workflows":
    choose(LangGraph)  # Advanced state management
elif use_case == "microservice_architecture":
    choose(Atomic_Agents)  # Compositional systems
```

### Production Deployment Considerations

- **Hidden Costs**: LangChain's modularity can create configuration complexity in production
- **Type Safety**: PydanticAI reduces runtime errors through schema validation
- **Monitoring**: Agno and ADK provide built-in observability for production systems
- **Vendor Lock-in**: Consider framework dependencies before committing to enterprise deployment

---

## Part 4: Next Steps

#### Your Learning Journey

This module follows a progressive skill-building path:

```text
Week 1: Foundation & Core Patterns
Session 1: Bare Metal → Session 2: LangChain → Session 3: LangGraph 
Session 4: CrewAI → Session 5: PydanticAI → Session 6: Atomic Agents

Week 2: Production & Enterprise  
Session 7: Google ADK → Session 8: Agno → Session 9: Multi-Agent Patterns
Session 10: Enterprise Integration

Capstone: Multi-Framework Agent Ecosystem
```


## Chapter Summary

### Key Takeaways

1. **Agent Evolution**: Modern AI has evolved from simple prompt-response to sophisticated autonomous systems with four key characteristics: autonomy, reactivity, proactivity, and social ability

2. **Five Core Patterns**: All production agent systems implement these fundamental patterns:
   - **Reflection**: Self-improvement through self-evaluation
   - **Tool Use**: Extending capabilities through external tools
   - **ReAct**: Iterative reasoning and action cycles
   - **Planning**: Breaking complex tasks into manageable steps
   - **Multi-Agent Collaboration**: Specialized agents working together

3. **Framework Landscape**: Seven leading frameworks address different production needs:
   - **LangChain**: Modular orchestration for prototyping
   - **LangGraph**: Complex state workflows
   - **CrewAI**: Role-based multi-agent systems
   - **PydanticAI**: Type-safe production development
   - **Atomic Agents**: Microservice architectures
   - **Google ADK**: Enterprise Google integration
   - **Agno**: Production monitoring focus

4. **Selection Criteria**: Framework choice depends on use case requirements:
   - Learning/Prototyping → LangChain, CrewAI
   - Enterprise Production → PydanticAI, Google ADK
   - Complex Workflows → LangGraph
   - Microservices → Atomic Agents

### Self-Assessment Checklist

- [ ] I understand the evolution from prompts to agents
- [ ] I can identify the 5 core agentic patterns in practice
- [ ] I can compare frameworks and their production strengths
- [ ] I'm ready to start building agents in Session 1

### Optional Deep-Dive Modules

**⚠️ OPTIONAL CONTENT - Choose based on your goals:**

- **[Module A: Historical Context & Evolution](Session0_ModuleA_Historical_Context_Evolution.md)** - Evolution from rule-based systems to modern agents
- **[Module B: Advanced Pattern Theory](Session0_ModuleB_Advanced_Pattern_Theory.md)** - Mathematical foundations of agent behavior

---

## Multiple Choice Test - Session 0

Test your understanding of agent frameworks and patterns:

**Question 1:** Which agentic pattern involves an agent evaluating and improving its own outputs?  
A) Multi-Agent  
B) Planning  
C) Tool Use  
D) Reflection  

**Question 2:** The ReAct pattern combines which two key capabilities?  
A) Reflecting and Acting  
B) Reading and Acting  
C) Retrieving and Acting  
D) Reasoning and Acting  

**Question 3:** Which framework is best suited for high-performance applications with minimal resource usage?  
A) PydanticAI  
B) LangChain  
C) Agno  
D) CrewAI  

**Question 4:** What is the primary advantage of the Multi-Agent pattern?  
A) Lower resource usage  
B) Reduced complexity  
C) Specialized expertise collaboration  
D) Faster execution  

**Question 5:** Which framework emphasizes type safety through schema validation?  
A) PydanticAI  
B) CrewAI  
C) LangChain  
D) Agno  

[**🗂️ View Test Solutions →**](Session0_Test_Solutions.md)

---

## Navigation

**Previous:** [Module 1: Agent Frameworks](index.md) (Introduction)  
**Next:** [Session 1 - Bare Metal Agents →](Session1_Bare_Metal_Agents.md)

---
