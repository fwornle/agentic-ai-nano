# src/session1/react_agent.py
"""
ReAct Agent implementation with visible reasoning process.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
import json
from datetime import datetime
from base_agent import BaseAgent, Tool


@dataclass
class ReActStep:
    """Represents a single ReAct step"""
    step_number: int
    thought: str                           # What the agent thinks
    action: Optional[str] = None          # What action it takes (if any)
    action_input: Optional[Dict] = None   # Parameters for the action
    observation: Optional[str] = None     # What it observes after acting


class ReActAgent(BaseAgent):
    """Agent implementing ReAct (Reasoning and Acting) pattern"""
    
    def __init__(self, name: str, llm_client, tools: List[Tool] = None, max_steps: int = 10):
        super().__init__(
            name,
            "Agent using ReAct pattern for transparent reasoning",
            llm_client,
            tools
        )
        self.max_steps = max_steps    # Prevent infinite reasoning loops
        self.react_history = []       # Store all reasoning sessions

    async def _generate_response(self, message: str, context: Dict = None) -> str:
        """Generate response using ReAct pattern"""
        steps = []
        step_number = 1
        
        # Start with initial thought
        current_thought = await self._initial_thought(message)
        
        # ReAct loop: Think → Act → Observe → Repeat
        while step_number <= self.max_steps:
            step = ReActStep(step_number=step_number, thought=current_thought)
            
            # Decide what action to take based on current thought
            action_decision = await self._decide_action(message, steps, current_thought)

            # Check if ready to give final answer
            if action_decision.get("action") == "ANSWER":
                final_answer = await self._generate_final_answer(message, steps)
                step.observation = f"Final Answer: {final_answer}"
                steps.append(step)
                break
            
            # Execute the decided action
            if action_decision.get("action"):
                step.action = action_decision["action"]
                step.action_input = action_decision.get("action_input", {})
                
                # Perform action and observe result
                observation = await self._execute_action(step.action, step.action_input)
                step.observation = observation
                
                # Generate next thought based on observation
                current_thought = await self._next_thought(message, steps + [step], observation)

            steps.append(step)
            step_number += 1
        
        # Store reasoning session for analysis
        self._store_reasoning_session(message, steps)
        
        # Format and return response
        return self._format_react_response(steps)

    async def _initial_thought(self, message: str) -> str:
        """Generate initial thought about the problem"""
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.get_available_tools()
        ])
        
        prompt = f"""
        You need to answer this question: {message}
        
        Available tools:
        {tools_desc}
        
        Think about how to approach this problem. What information do you need?
        What steps might be required? Start with a clear thought about your approach.
        
        Respond with just your thought, starting with "I need to..."
        """
        
        return await self._call_llm(prompt)

    async def _decide_action(self, message: str, steps: List[ReActStep], thought: str) -> Dict:
        """Decide next action based on current thought and history"""
        steps_summary = self._format_steps_for_prompt(steps)
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.get_available_tools()
        ])
        
        prompt = f"""
        Question: {message}
        
        Previous steps:
        {steps_summary}
        
        Current thought: {thought}
        
        Available tools:
        {tools_desc}
        
        Based on your current thought, decide what action to take next.
        You can either:
        1. Use a tool (provide tool name and parameters)
        2. Answer the question directly if you have enough information
        
        Respond with JSON:
        {{
            "action": "tool_name" or "ANSWER",
            "action_input": {{"param": "value"}} or null,
            "reasoning": "why you chose this action"
        }}
        """
        
        response = await self._call_llm(prompt)
        
        try:
            return json.loads(self._extract_json(response))
        except Exception:
            return {"action": "ANSWER", "reasoning": "Failed to parse action decision"}

    async def _execute_action(self, action: str, action_input: Dict) -> str:
        """Execute an action and return observation"""
        if action == "ANSWER":
            return "Ready to provide final answer"
        
        # Execute the tool and format observation
        result = await self.execute_tool(action, **action_input)
        
        if result["success"]:
            return f"Successfully executed {action}. Result: {result['result']}"
        else:
            return f"Failed to execute {action}. Error: {result['error']}"

    async def _next_thought(self, message: str, steps: List[ReActStep], observation: str) -> str:
        """Generate next thought based on observation"""
        steps_summary = self._format_steps_for_prompt(steps)
        
        prompt = f"""
        Question: {message}
        
        Steps so far:
        {steps_summary}
        
        Latest observation: {observation}
        
        Based on this observation, what should you think about next?
        Do you have enough information to answer the question?
        What additional information might you need?
        
        Provide your next thought:
        """
        
        return await self._call_llm(prompt)

    def _format_react_response(self, steps: List[ReActStep]) -> str:
        """Format final response showing ReAct reasoning process"""
        response = ["## ReAct Reasoning Process\n"]
        
        for step in steps:
            response.append(f"**Step {step.step_number}:**")
            response.append(f"*Thought:* {step.thought}")
            
            if step.action and step.action != "ANSWER":
                response.append(f"*Action:* {step.action} with {step.action_input}")
            
            if step.observation:
                if "Final Answer:" in step.observation:
                    response.append(f"*{step.observation}*")
                else:
                    response.append(f"*Observation:* {step.observation}")
            
            response.append("")  # Empty line for readability
        
        return "\n".join(response)

    def _store_reasoning_session(self, message: str, steps: List[ReActStep]):
        """Store reasoning session for later analysis"""
        self.react_history.append({
            "message": message,
            "steps": steps,
            "timestamp": datetime.now()
        })

    def _format_steps_for_prompt(self, steps: List[ReActStep]) -> str:
        """Format steps for inclusion in prompts"""
        formatted = []
        for step in steps:
            formatted.append(f"Step {step.step_number}:")
            formatted.append(f"  Thought: {step.thought}")
            if step.action:
                formatted.append(f"  Action: {step.action} {step.action_input}")
            if step.observation:
                formatted.append(f"  Observation: {step.observation}")
        return "\n".join(formatted)

    async def _generate_final_answer(self, message: str, steps: List[ReActStep]) -> str:
        """Generate final answer based on reasoning process"""
        steps_summary = self._format_steps_for_prompt(steps)
        
        prompt = f"""
        Question: {message}
        
        Reasoning process:
        {steps_summary}
        
        Based on your reasoning and the information gathered, provide a comprehensive
        final answer to the question. Be specific and cite the information you used.
        """
        
        return await self._call_llm(prompt)

    def get_react_analysis(self) -> Dict:
        """Analyze ReAct performance for optimization"""
        if not self.react_history:
            return {"total_conversations": 0}
        
        total_steps = sum(len(h["steps"]) for h in self.react_history)
        avg_steps = total_steps / len(self.react_history)
        
        # Analyze action usage patterns
        action_counts = {}
        for history in self.react_history:
            for step in history["steps"]:
                if step.action:
                    action = step.action
                    action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            "total_conversations": len(self.react_history),
            "average_steps": avg_steps,
            "total_steps": total_steps,
            "action_distribution": action_counts,
            "most_recent": self.react_history[-1] if self.react_history else None
        }

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text response"""
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        return json_match.group() if json_match else "{}"

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM - flexible integration"""
        if hasattr(self.llm_client, 'chat'):
            return await self.llm_client.chat(prompt)
        return f"Simulated response to: {prompt[:50]}..."