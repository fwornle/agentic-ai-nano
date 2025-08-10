# src/session2/langchain_planning.py
"""
Planning Agent implementation using LangChain framework.
"""

from langchain.agents import Tool, AgentType, initialize_agent
from langchain.experimental.plan_and_execute import PlanAndExecuteAgentExecutor, load_agent_executor, load_chat_planner
from langchain.memory import ConversationBufferMemory
from typing import List, Dict
from datetime import datetime
import json


class LangChainPlanningAgent:
    """Planning agent using LangChain's Plan-and-Execute framework"""
    
    def __init__(self, llm, tools: List[Tool]):
        self.llm = llm
        self.tools = tools
        
        # Create planner
        self.planner = load_chat_planner(llm)
        
        # Create executor
        self.executor = load_agent_executor(llm, tools, verbose=True)
        
        # Create plan-and-execute agent
        self.agent = PlanAndExecuteAgentExecutor(
            planner=self.planner,
            executor=self.executor,
            verbose=True
        )
        
        self.execution_history = []
    
    async def execute_complex_task(self, task: str) -> str:
        """Execute complex multi-step task with planning"""
        print(f"📋 Planning and executing: {task}")
        
        try:
            result = await self.agent.arun(task)
            
            # Store execution history
            self.execution_history.append({
                "task": task,
                "result": result,
                "timestamp": datetime.now()
            })
            
            return result
            
        except Exception as e:
            return f"Planning and execution failed: {str(e)}"
    
    def get_last_plan(self) -> Dict:
        """Get details of the last execution plan"""
        if hasattr(self.agent, 'planner') and hasattr(self.agent.planner, 'last_plan'):
            return self.agent.planner.last_plan
        return {}


# Custom hierarchical planning agent
class HierarchicalPlanningAgent:
    """Custom planning agent with hierarchical task decomposition"""
    
    def __init__(self, llm, tools: List[Tool]):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.planning_history = []
    
    async def execute_with_planning(self, goal: str) -> str:
        """Execute goal with hierarchical planning"""
        # Step 1: Create high-level plan
        high_level_plan = await self._create_high_level_plan(goal)
        
        # Step 2: Decompose into detailed steps
        detailed_plan = await self._create_detailed_plan(goal, high_level_plan)
        
        # Step 3: Execute plan
        execution_result = await self._execute_plan(detailed_plan)
        
        # Store planning history
        self.planning_history.append({
            "goal": goal,
            "high_level_plan": high_level_plan,
            "detailed_plan": detailed_plan,
            "execution_result": execution_result,
            "timestamp": datetime.now()
        })
        
        return execution_result
    
    async def _create_high_level_plan(self, goal: str) -> List[str]:
        """Create high-level plan steps"""
        tools_desc = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
        
        prompt = f"""
        Goal: {goal}
        
        Available tools:
        {tools_desc}
        
        Create a high-level plan to achieve this goal. Break it down into 3-7 major steps.
        
        Respond with JSON:
        {{
            "steps": [
                "Step 1 description",
                "Step 2 description",
                ...
            ]
        }}
        """
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            plan_data = json.loads(response.content)
            return plan_data.get("steps", [])
        except Exception:
            return ["Failed to create high-level plan"]
    
    async def _create_detailed_plan(self, goal: str, high_level_plan: List[str]) -> List[Dict]:
        """Create detailed execution plan"""
        detailed_steps = []
        
        for i, high_level_step in enumerate(high_level_plan):
            prompt = f"""
            Goal: {goal}
            High-level step {i+1}: {high_level_step}
            
            Available tools: {list(self.tools.keys())}
            
            Break this high-level step into specific actions.
            
            Respond with JSON:
            {{
                "actions": [
                    {{
                        "action": "tool_name or direct_response",
                        "input": "input for tool or response text",
                        "expected_output": "what this action should produce"
                    }}
                ]
            }}
            """
            
            response = await self.llm.ainvoke(prompt)
            
            try:
                step_data = json.loads(response.content)
                for action in step_data.get("actions", []):
                    action["high_level_step"] = i + 1
                    action["high_level_description"] = high_level_step
                    detailed_steps.append(action)
            except Exception:
                detailed_steps.append({
                    "action": "direct_response",
                    "input": f"Failed to detail step: {high_level_step}",
                    "high_level_step": i + 1,
                    "high_level_description": high_level_step
                })
        
        return detailed_steps
    
    async def _execute_plan(self, detailed_plan: List[Dict]) -> str:
        """Execute the detailed plan"""
        results = []
        
        for i, step in enumerate(detailed_plan):
            print(f"Executing step {i+1}: {step['action']}")
            
            if step["action"] in self.tools:
                # Execute tool
                tool = self.tools[step["action"]]
                try:
                    result = tool._run(step["input"])
                    results.append(f"Step {i+1}: {result}")
                except Exception as e:
                    results.append(f"Step {i+1} failed: {str(e)}")
            
            elif step["action"] == "direct_response":
                # Direct response without tool
                results.append(f"Step {i+1}: {step['input']}")
            
            else:
                results.append(f"Step {i+1}: Unknown action {step['action']}")
        
        # Synthesize final result
        return await self._synthesize_results(detailed_plan, results)
    
    async def _synthesize_results(self, plan: List[Dict], results: List[str]) -> str:
        """Synthesize execution results into final response"""
        plan_summary = "\n".join([
            f"Step {i+1}: {step['action']} - {step['expected_output']}"
            for i, step in enumerate(plan)
        ])
        
        results_summary = "\n".join(results)
        
        prompt = f"""
        Planned steps:
        {plan_summary}
        
        Execution results:
        {results_summary}
        
        Synthesize these results into a comprehensive final response.
        Highlight key findings and ensure the original goal is addressed.
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    def get_planning_analysis(self) -> Dict:
        """Analyze planning performance"""
        if not self.planning_history:
            return {"total_plans": 0}
        
        avg_steps = sum(
            len(p["detailed_plan"]) for p in self.planning_history
        ) / len(self.planning_history)
        
        return {
            "total_plans": len(self.planning_history),
            "average_steps_per_plan": avg_steps,
            "recent_plans": self.planning_history[-3:],  # Last 3 plans
            "most_complex_plan": max(
                self.planning_history,
                key=lambda p: len(p["detailed_plan"])
            ) if self.planning_history else None
        }


# Example usage
async def demo_planning_agents():
    from llm_setup import LLMFactory
    from langchain_tools import CalculatorTool, weather_tool, email_tool
    
    llm = LLMFactory.create_llm("openai")
    tools = [CalculatorTool(), weather_tool, email_tool]
    
    # Built-in planning agent
    builtin_agent = LangChainPlanningAgent(llm, tools)
    response1 = await builtin_agent.execute_complex_task(
        "Research the weather in 3 different cities, calculate the average temperature, and send a summary email"
    )
    
    # Custom hierarchical planning agent
    custom_agent = HierarchicalPlanningAgent(llm, tools)
    response2 = await custom_agent.execute_with_planning(
        "Plan a data analysis workflow: get weather data for 5 cities, calculate statistics, and create a summary report"
    )
    
    print("Built-in Planning Response:", response1)
    print("Custom Planning Response:", response2)
    print("Planning Analysis:", custom_agent.get_planning_analysis())