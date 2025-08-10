# src/session2/langchain_reflection.py
"""
Reflection Agent implementation using LangChain framework.
"""

from langchain.agents import Tool, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StdOutCallbackHandler
from langchain.schema import SystemMessage
from typing import List, Dict
from datetime import datetime
import asyncio


class LangChainReflectionAgent:
    """Reflection agent using LangChain framework"""
    
    def __init__(self, llm, max_iterations: int = 3):
        self.llm = llm
        self.max_iterations = max_iterations
        self.reflection_history = []
        
        # Create reflection tool
        self.reflection_tool = Tool(
            name="reflect_on_response",
            description="Critically evaluate and improve a response",
            func=self._reflect_on_response
        )
        
        # Initialize agent with reflection capability
        self.agent = initialize_agent(
            tools=[self.reflection_tool],
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        )
    
    def _reflect_on_response(self, response: str) -> str:
        """Reflect on and potentially improve a response"""
        reflection_prompt = f"""
        Critically evaluate this response and determine if it can be improved:
        
        Response: {response}
        
        Consider:
        1. Accuracy and correctness
        2. Completeness and depth
        3. Clarity and organization
        4. Relevance and usefulness
        
        If the response is already excellent, return "SATISFACTORY: [brief explanation]"
        If it needs improvement, return "IMPROVE: [specific suggestions]"
        """
        
        critique = self.llm.invoke(reflection_prompt).content
        return critique
    
    async def process_with_reflection(self, message: str) -> str:
        """Process message with reflection pattern"""
        current_response = await self._initial_response(message)
        
        for iteration in range(self.max_iterations):
            # Reflect on current response
            critique = self._reflect_on_response(current_response)
            
            # Check if satisfactory
            if "SATISFACTORY" in critique:
                self.reflection_history.append({
                    "message": message,
                    "iterations": iteration + 1,
                    "final_response": current_response,
                    "final_critique": critique
                })
                break
            
            # Improve response
            improvement_prompt = f"""
            Original question: {message}
            Current response: {current_response}
            Critique: {critique}
            
            Based on the critique, provide an improved version of the response.
            Focus on addressing the specific issues mentioned.
            """
            
            improved_response = self.llm.invoke(improvement_prompt).content
            current_response = improved_response
        
        return current_response
    
    async def _initial_response(self, message: str) -> str:
        """Generate initial response"""
        initial_prompt = f"""
        Provide a helpful and comprehensive response to: {message}
        
        Focus on being accurate, complete, and well-organized.
        """
        
        response = self.llm.invoke(initial_prompt).content
        return response


# Example usage
async def demo_langchain_reflection():
    from llm_setup import LLMFactory
    
    llm = LLMFactory.create_llm("openai")
    reflection_agent = LangChainReflectionAgent(llm)
    
    response = await reflection_agent.process_with_reflection(
        "Explain the benefits and drawbacks of renewable energy"
    )
    
    print("Final Response:", response)