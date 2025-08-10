# src/session1/reflection_agent.py
"""
Reflection Agent implementation that critiques and improves its own outputs.
"""

from typing import Dict
from datetime import datetime
from base_agent import BaseAgent


class ReflectionAgent(BaseAgent):
    """Agent that reflects on and improves its own outputs"""
    
    def __init__(self, name: str, llm_client, max_iterations: int = 3):
        super().__init__(name, "Agent with reflection capabilities", llm_client)
        self.max_iterations = max_iterations  # Prevent infinite loops
        self.reflection_history = []          # Track improvement process

    async def _generate_response(self, message: str, context: Dict = None) -> str:
        """Generate response with reflection and improvement"""
        current_response = await self._initial_response(message, context)
        
        for iteration in range(self.max_iterations):
            # Step 1: Reflect on current response
            critique = await self._reflect_on_response(message, current_response)
            
            # Step 2: If response is good enough, return it
            if self._is_response_satisfactory(critique):
                self.logger.info(f"Response satisfactory after {iteration + 1} iterations")
                break
            
            # Step 3: Improve response based on critique
            improved_response = await self._improve_response(
                message, current_response, critique
            )
            
            # Step 4: Track the improvement process
            self._track_reflection(iteration, current_response, critique, improved_response)
            
            current_response = improved_response
        
        return current_response

    async def _initial_response(self, message: str, context: Dict = None) -> str:
        """Generate initial response without reflection"""
        system_prompt = f"""
        You are {self.name}, {self.description}.
        Provide a helpful response to the user's message.
        This is your initial response - focus on being accurate and comprehensive.
        """
        
        prompt = f"{system_prompt}\n\nUser message: {message}"
        response = await self._call_llm(prompt)
        return response

    async def _reflect_on_response(self, original_message: str, response: str) -> str:
        """Critically evaluate the response"""
        reflection_prompt = f"""
        Please critique the following response to determine if it can be improved:
        
        Original Question: {original_message}
        Response: {response}
        
        Evaluate the response on these criteria:
        1. Accuracy and correctness
        2. Completeness and thoroughness  
        3. Clarity and organization
        4. Relevance to the question
        5. Actionability (if applicable)
        
        Provide specific, constructive feedback on what could be improved.
        If the response is already excellent, say "SATISFACTORY".
        """
        
        critique = await self._call_llm(reflection_prompt)
        return critique

    async def _improve_response(self, message: str, current_response: str, critique: str) -> str:
        """Improve response based on critique"""
        improvement_prompt = f"""
        Original Question: {message}
        Current Response: {current_response}
        Critique: {critique}
        
        Based on the critique, provide an improved version of the response.
        Address the specific issues mentioned while maintaining the strengths.
        Make the response better without making it unnecessarily longer.
        """
        
        improved = await self._call_llm(improvement_prompt)
        return improved

    def _is_response_satisfactory(self, critique: str) -> bool:
        """Determine if response is satisfactory based on critique"""
        return "SATISFACTORY" in critique.upper()

    def _track_reflection(self, iteration: int, original: str, critique: str, improved: str):
        """Track reflection history for analysis"""
        self.reflection_history.append({
            "iteration": iteration + 1,
            "original": original,
            "critique": critique,
            "improved": improved,
            "timestamp": datetime.now()
        })

    def get_reflection_summary(self) -> Dict:
        """Get summary of reflection process"""
        if not self.reflection_history:
            return {"total_reflections": 0}
        
        return {
            "total_reflections": len(self.reflection_history),
            "average_iterations": sum(
                r["iteration"] for r in self.reflection_history
            ) / len(self.reflection_history),
            "recent_reflections": self.reflection_history[-5:]  # Last 5
        }

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM with prompt - implement based on your LLM client"""
        if hasattr(self.llm_client, 'chat'):
            response = await self.llm_client.chat(prompt)
            return response
        else:
            # Fallback simulation for testing
            return f"Simulated response to: {prompt[:50]}..."