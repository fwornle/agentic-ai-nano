# src/session2/langchain_multi_agent.py
"""
Multi-Agent System implementation using LangChain framework.
"""

from langchain.agents import Tool, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from typing import Dict, List, Any
from datetime import datetime
import asyncio


class LangChainMultiAgentSystem:
    """Multi-agent system using LangChain"""
    
    def __init__(self, llm):
        self.llm = llm
        self.agents = {}
        self.communication_history = []
        
    def create_specialized_agent(
        self, 
        name: str, 
        role: str, 
        tools: List[Tool], 
        system_message: str = ""
    ):
        """Create a specialized agent with specific role and tools"""
        
        # Create memory for this agent
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Add role-specific system message to memory
        if system_message:
            memory.chat_memory.add_message(
                HumanMessage(content=f"You are {name}. {system_message}")
            )
        
        # Create agent
        agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=memory
        )
        
        self.agents[name] = {
            "agent": agent,
            "role": role,
            "tools": [tool.name for tool in tools],
            "system_message": system_message
        }
        
        print(f"Created agent '{name}' with role: {role}")
    
    async def send_message_to_agent(
        self, 
        agent_name: str, 
        message: str, 
        from_agent: str = "user"
    ) -> str:
        """Send message to specific agent"""
        if agent_name not in self.agents:
            return f"Agent '{agent_name}' not found"
        
        agent_info = self.agents[agent_name]
        
        try:
            response = await agent_info["agent"].arun(message)
            
            # Log communication
            self.communication_history.append({
                "from": from_agent,
                "to": agent_name,
                "message": message,
                "response": response,
                "timestamp": datetime.now()
            })
            
            return response
            
        except Exception as e:
            return f"Error communicating with {agent_name}: {str(e)}"
    
    async def collaborative_workflow(
        self, 
        task: str, 
        workflow_steps: List[Dict[str, Any]]
    ) -> str:
        """Execute collaborative workflow between multiple agents"""
        
        workflow_results = []
        context = {"original_task": task}
        
        for step in workflow_steps:
            agent_name = step["agent"]
            step_instruction = step["instruction"]
            
            # Add context from previous steps
            if workflow_results:
                context_info = "\n".join([
                    f"{r['agent']}: {r['result'][:100]}..." 
                    for r in workflow_results[-2:]  # Last 2 results
                ])
                full_instruction = f"""
                Original task: {task}
                
                Previous results:
                {context_info}
                
                Your task: {step_instruction}
                """
            else:
                full_instruction = f"Original task: {task}\n\nYour task: {step_instruction}"
            
            # Execute step
            result = await self.send_message_to_agent(
                agent_name, 
                full_instruction, 
                "workflow_coordinator"
            )
            
            workflow_results.append({
                "step": len(workflow_results) + 1,
                "agent": agent_name,
                "instruction": step_instruction,
                "result": result
            })
            
            # Update context
            context[f"step_{len(workflow_results)}"] = result
        
        # Synthesize final result
        final_result = await self._synthesize_workflow_results(task, workflow_results)
        return final_result
    
    async def _synthesize_workflow_results(
        self, 
        original_task: str, 
        results: List[Dict]
    ) -> str:
        """Synthesize results from collaborative workflow"""
        
        results_summary = "\n\n".join([
            f"Step {r['step']} - {r['agent']}:\n{r['result']}"
            for r in results
        ])
        
        synthesis_prompt = f"""
        Original Task: {original_task}
        
        Collaborative Results:
        {results_summary}
        
        Synthesize these results into a comprehensive final response.
        Highlight key insights and ensure the original task is fully addressed.
        """
        
        response = await self.llm.ainvoke(synthesis_prompt)
        return response.content
    
    async def agent_conversation(
        self, 
        agent1: str, 
        agent2: str, 
        topic: str, 
        max_turns: int = 5
    ) -> List[Dict]:
        """Facilitate conversation between two agents"""
        
        conversation = []
        current_speaker = agent1
        current_message = f"Let's discuss: {topic}"
        
        for turn in range(max_turns):
            # Send message to current speaker
            response = await self.send_message_to_agent(
                current_speaker, 
                current_message,
                "conversation_facilitator"
            )
            
            conversation.append({
                "turn": turn + 1,
                "speaker": current_speaker,
                "message": current_message,
                "response": response
            })
            
            # Switch speakers
            current_speaker = agent2 if current_speaker == agent1 else agent1
            current_message = response  # Response becomes next message
        
        return conversation
    
    def get_system_status(self) -> Dict:
        """Get status of multi-agent system"""
        return {
            "total_agents": len(self.agents),
            "agent_info": {
                name: {
                    "role": info["role"],
                    "tools": info["tools"]
                }
                for name, info in self.agents.items()
            },
            "total_communications": len(self.communication_history),
            "recent_communications": self.communication_history[-5:]
        }


# Example specialized agents
async def demo_multi_agent_system():
    from llm_setup import LLMFactory
    from langchain_tools import CalculatorTool, weather_tool, email_tool
    
    llm = LLMFactory.create_llm("openai")
    
    # Create multi-agent system
    system = LangChainMultiAgentSystem(llm)
    
    # Create specialized agents
    system.create_specialized_agent(
        name="data_analyst",
        role="Data Analysis Specialist",
        tools=[CalculatorTool()],
        system_message="You specialize in data analysis and mathematical calculations. Provide precise, well-reasoned analysis."
    )
    
    system.create_specialized_agent(
        name="researcher",
        role="Research Specialist", 
        tools=[weather_tool],
        system_message="You specialize in gathering and synthesizing information from various sources."
    )
    
    system.create_specialized_agent(
        name="communicator",
        role="Communication Specialist",
        tools=[email_tool],
        system_message="You specialize in clear, professional communication and report writing."
    )
    
    # Execute collaborative workflow
    workflow = [
        {
            "agent": "researcher",
            "instruction": "Research current weather conditions in New York, London, and Tokyo"
        },
        {
            "agent": "data_analyst", 
            "instruction": "Analyze the weather data and calculate average temperatures and temperature ranges"
        },
        {
            "agent": "communicator",
            "instruction": "Create a professional summary report of the weather analysis"
        }
    ]
    
    result = await system.collaborative_workflow(
        "Create a global weather analysis report for our executive team",
        workflow
    )
    
    print("Collaborative Workflow Result:")
    print(result)
    
    # Agent conversation example
    conversation = await system.agent_conversation(
        "data_analyst",
        "researcher", 
        "Best practices for weather data analysis",
        max_turns=3
    )
    
    print("\nAgent Conversation:")
    for turn in conversation:
        print(f"Turn {turn['turn']} - {turn['speaker']}: {turn['response'][:100]}...")
    
    print("\nSystem Status:", system.get_system_status())