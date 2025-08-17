# src/session2/langchain_react.py
"""
ReAct Agent implementation using LangChain framework.
"""

from langchain.agents import Tool, AgentType, initialize_agent
from langchain.agents.react.base import ReActTextWorldAgent
from langchain.memory import ConversationBufferMemory
from typing import List, Dict
from datetime import datetime
import json


class LangChainReActAgent:
    """ReAct agent using LangChain's built-in implementation"""
    
    def __init__(self, llm, tools: List[Tool], max_iterations: int = 10):
        self.llm = llm
        self.tools = tools
        self.max_iterations = max_iterations
        
        # Create ReAct agent
        self.agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.REACT_DOCSTORE,  # ReAct pattern
            verbose=True,
            max_iterations=max_iterations,
            handle_parsing_errors=True
        )
        
        self.execution_history = []
    
    async def solve_problem(self, problem: str) -> str:
        """Solve problem using ReAct pattern"""
        print(f"🔍 Starting ReAct process for: {problem}")
        
        try:
            response = await self.agent.arun(problem)
            
            # Store execution info
            self.execution_history.append({
                "problem": problem,
                "response": response,
                "timestamp": datetime.now()
            })
            
            return response
            
        except Exception as e:
            return f"ReAct process failed: {str(e)}"
    
    def get_reasoning_chain(self) -> List[Dict]:
        """Get the reasoning chain from last execution"""
        # Access agent's intermediate steps
        if hasattr(self.agent, 'agent') and hasattr(self.agent.agent, 'get_intermediate_steps'):
            return self.agent.agent.get_intermediate_steps()
        return []


# Custom ReAct implementation for more control
class CustomReActAgent:
    """Custom ReAct implementation with detailed step tracking"""
    
    def __init__(self, llm, tools: List[Tool]):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.reasoning_steps = []
    
    async def solve_problem(self, problem: str, max_steps: int = 10) -> str:
        """Solve problem with custom ReAct implementation"""
        self.reasoning_steps = []
        
        current_step = 1
        current_thought = f"I need to solve: {problem}"
        
        while current_step <= max_steps:
            # Record thought
            step_info = {
                "step": current_step,
                "thought": current_thought,
                "action": None,
                "action_input": None,
                "observation": None
            }
            
            # Decide action based on thought
            action_decision = await self._decide_action(problem, current_thought)
            
            if action_decision["action"] == "ANSWER":
                step_info["observation"] = f"Final Answer: {action_decision['answer']}"
                self.reasoning_steps.append(step_info)
                return action_decision["answer"]
            
            # Execute action
            step_info["action"] = action_decision["action"]
            step_info["action_input"] = action_decision["action_input"]
            
            observation = await self._execute_action(
                action_decision["action"],
                action_decision["action_input"]
            )
            
            step_info["observation"] = observation
            self.reasoning_steps.append(step_info)
            
            # Generate next thought
            current_thought = await self._next_thought(problem, step_info, observation)
            current_step += 1
        
        return "Maximum steps reached without final answer"
    
    async def _decide_action(self, problem: str, thought: str) -> Dict:
        """Decide next action based on current thought"""
        tools_desc = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
        
        prompt = f"""
        Problem: {problem}
        Current thought: {thought}
        
        Available tools:
        {tools_desc}
        
        Based on your thought, decide what to do next.
        
        Respond with JSON:
        {{
            "action": "tool_name" or "ANSWER",
            "action_input": "input for tool" or null,
            "answer": "final answer if action is ANSWER" or null,
            "reasoning": "why you chose this action"
        }}
        """
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            return json.loads(response.content)
        except Exception:
            return {"action": "ANSWER", "answer": "Failed to parse action decision"}
    
    async def _execute_action(self, action: str, action_input: str) -> str:
        """Execute action and return observation"""
        if action not in self.tools:
            return f"Tool '{action}' not available"
        
        tool = self.tools[action]
        try:
            result = tool._run(action_input)
            return f"Tool {action} executed successfully. Result: {result}"
        except Exception as e:
            return f"Tool {action} failed: {str(e)}"
    
    async def _next_thought(self, problem: str, step_info: Dict, observation: str) -> str:
        """Generate next thought based on observation"""
        steps_summary = self._format_steps()
        
        prompt = f"""
        Problem: {problem}
        
        Previous steps:
        {steps_summary}
        
        Latest observation: {observation}
        
        Based on this observation, what should you think about next?
        Do you have enough information to solve the problem?
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    def _format_steps(self) -> str:
        """Format reasoning steps for display"""
        formatted = []
        for step in self.reasoning_steps:
            formatted.append(f"Step {step['step']}:")
            formatted.append(f"  Thought: {step['thought']}")
            if step['action']:
                formatted.append(f"  Action: {step['action']} - {step['action_input']}")
            if step['observation']:
                formatted.append(f"  Observation: {step['observation']}")
        return "\n".join(formatted)
    
    def get_reasoning_summary(self) -> Dict:
        """Get summary of reasoning process"""
        return {
            "total_steps": len(self.reasoning_steps),
            "steps": self.reasoning_steps,
            "formatted_reasoning": self._format_steps()
        }


# Example usage
async def demo_react_agents():
    from llm_setup import LLMFactory
    from langchain_tools import CalculatorTool, weather_tool
    
    llm = LLMFactory.create_llm("openai")
    tools = [CalculatorTool(), weather_tool]
    
    # Built-in ReAct agent
    builtin_agent = LangChainReActAgent(llm, tools)
    response1 = await builtin_agent.solve_problem(
        "What's the weather in New York and what would be 15% of the temperature?"
    )
    
    # Custom ReAct agent  
    custom_agent = CustomReActAgent(llm, tools)
    response2 = await custom_agent.solve_problem(
        "What's the weather in London and calculate the temperature in Celsius if it's currently 75°F?"
    )
    
    print("Built-in ReAct Response:", response1)
    print("Custom ReAct Response:", response2)
    print("Reasoning Summary:", custom_agent.get_reasoning_summary())