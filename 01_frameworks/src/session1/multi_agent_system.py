# src/session1/multi_agent_system.py
"""
Multi-Agent System with coordination and communication patterns.
"""

from typing import Dict, List, Any
from base_agent import BaseAgent, AgentMessage
from datetime import datetime


class AgentCoordinator:
    """Coordinates multiple specialized agents in a system"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}  # Registered agents
        self.message_history = []               # All inter-agent messages
        self.communication_patterns = {}       # Track who talks to whom

    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent with the coordinator"""
        self.agents[agent.name] = agent
        self.communication_patterns[agent.name] = []
        print(f"✓ Registered agent: {agent.name} ({agent.description})")

    async def route_message(self, message: str, to_agent: str, from_agent: str = "user") -> str:
        """Route message to specific agent and track communication"""
        if to_agent not in self.agents:
            return f"Error: Agent '{to_agent}' not found"
        
        # Log communication pattern
        self.communication_patterns[to_agent].append({
            "from": from_agent,
            "message": message[:50] + "..." if len(message) > 50 else message,
            "timestamp": datetime.now()
        })

        # Process message with target agent
        agent = self.agents[to_agent]
        response = await agent.process_message(message)
        
        # Store complete conversation
        self.message_history.append({
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "response": response,
            "timestamp": datetime.now()
        })
        
        return response

    async def collaborative_task(self, task: str, agent_roles: Dict[str, str]) -> str:
        """Coordinate multiple agents on a collaborative task"""
        results = {}
        
        # Assign roles and execute in parallel or sequence
        for agent_name, role_instruction in agent_roles.items():
            if agent_name in self.agents:
                full_instruction = f"Role: {role_instruction}\n\nTask: {task}"
                
                print(f"🔄 Delegating to {agent_name}: {role_instruction}")
                response = await self.route_message(full_instruction, agent_name, "coordinator")
                results[agent_name] = response
                print(f"✓ Completed by {agent_name}")
        
        # Synthesize collaborative results
        synthesis = await self._synthesize_collaborative_results(task, results)
        return synthesis

    async def _synthesize_collaborative_results(self, task: str, results: Dict[str, str]) -> str:
        """Combine results from multiple agents into coherent response"""
        synthesis = [f"# Collaborative Task Results\n**Task:** {task}\n"]
        
        for agent_name, result in results.items():
            synthesis.append(f"## Contribution from {agent_name}")
            synthesis.append(result)
            synthesis.append("")  # Empty line
        
        synthesis.append("## Summary")
        synthesis.append("All specialized agents have contributed their expertise to complete this collaborative task.")
        
        return "\n".join(synthesis)

    def get_system_stats(self) -> Dict:
        """Get comprehensive statistics about the multi-agent system"""
        # Calculate communication patterns
        total_messages = len(self.message_history)
        agent_activity = {}
        
        for msg in self.message_history:
            agent = msg["to"]
            if agent not in agent_activity:
                agent_activity[agent] = 0
            agent_activity[agent] += 1
        
        return {
            "total_agents": len(self.agents),
            "agent_names": list(self.agents.keys()),
            "total_messages": total_messages,
            "agent_activity": agent_activity,
            "most_active_agent": max(agent_activity, key=agent_activity.get) if agent_activity else None,
            "communication_patterns": self.communication_patterns,
            "recent_activity": self.message_history[-5:]  # Last 5 messages
        }