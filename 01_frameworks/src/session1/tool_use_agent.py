# src/session1/tool_use_agent.py
"""
Tool Use Agent implementation with intelligent tool selection and planning.
"""

from base_agent import BaseAgent, Tool
from typing import Dict, List, Any
import json
from datetime import datetime


class ToolUseAgent(BaseAgent):
    """Agent capable of discovering, selecting, and using tools"""
    
    def __init__(self, name: str, llm_client, tools: List[Tool] = None):
        super().__init__(
            name, 
            "Agent with advanced tool use capabilities",
            llm_client,
            tools
        )
        self.tool_usage_history = []  # Track tool usage for analysis

    async def _generate_response(self, message: str, context: Dict = None) -> str:
        """Generate response with intelligent tool use"""
        
        # Step 1: Analyze if tools are needed
        tool_analysis = await self._analyze_tool_needs(message)
        
        # Step 2: Simple response if no tools needed
        if not tool_analysis.get("needs_tools", False):
            return await self._simple_response(message)
        
        # Step 3: Plan which tools to use and how
        tool_plan = await self._plan_tool_usage(message, tool_analysis)
        
        # Step 4: Execute the plan and synthesize response
        response = await self._execute_tool_plan(message, tool_plan)
        
        return response

    async def _analyze_tool_needs(self, message: str) -> Dict[str, Any]:
        """Analyze if message requires tool use"""
        available_tools = self.get_available_tools()
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in available_tools
        ])

        analysis_prompt = f"""
        Analyze if the following user message requires any tools to answer properly.
        
        User message: {message}
        
        Available tools:
        {tools_desc}
        
        Respond with JSON:
        {{
            "needs_tools": true/false,
            "reasoning": "explanation of why tools are/aren't needed",
            "relevant_tools": ["list", "of", "relevant", "tool", "names"]
        }}
        """

        response = await self._call_llm(analysis_prompt)
        
        try:
            return json.loads(self._extract_json(response))
        except Exception:
            return {"needs_tools": False, "reasoning": "Failed to parse analysis"}

    async def _plan_tool_usage(self, message: str, analysis: Dict) -> List[Dict]:
        """Create a step-by-step plan for tool usage"""
        relevant_tools = analysis.get("relevant_tools", [])
        tool_schemas = {
            tool["name"]: tool for tool in self.get_available_tools()
            if tool["name"] in relevant_tools
        }

        planning_prompt = f"""
        Create a plan to use tools to answer this message:
        
        User message: {message}
        Reasoning: {analysis.get('reasoning', '')}
        
        Available relevant tools:
        {json.dumps(tool_schemas, indent=2)}
        
        Create a step-by-step plan in JSON format:
        {{
            "steps": [
                {{
                    "step": 1,
                    "tool": "tool_name",
                    "parameters": {{"param1": "value1"}},
                    "purpose": "why this step is needed"
                }}
            ]
        }}
        """

        response = await self._call_llm(planning_prompt)
        
        try:
            plan = json.loads(self._extract_json(response))
            return plan.get("steps", [])
        except Exception:
            return []  # Fallback to no tools

    async def _execute_tool_plan(self, message: str, plan: List[Dict]) -> str:
        """Execute the tool plan and generate final response"""
        tool_results = []
        
        # Execute each step in the plan
        for step in plan:
            tool_name = step.get("tool")
            parameters = step.get("parameters", {})
            purpose = step.get("purpose", "")
            
            self.logger.info(f"Executing step {step.get('step')}: {purpose}")
            
            # Execute the tool
            result = await self.execute_tool(tool_name, **parameters)

            # Track the execution
            step_result = {
                "step": step.get("step"),
                "tool": tool_name,
                "parameters": parameters,
                "purpose": purpose,
                "result": result
            }
            tool_results.append(step_result)
            
            # Add to usage history
            self.tool_usage_history.append({
                "message": message,
                "tool": tool_name,
                "parameters": parameters,
                "result": result,
                "timestamp": datetime.now()
            })
        
        # Generate final response using all results
        return await self._synthesize_response(message, tool_results)

    async def _synthesize_response(self, message: str, tool_results: List[Dict]) -> str:
        """Create final response from tool results"""
        results_summary = "\n".join([
            f"Step {r['step']} - {r['tool']}: {r['result']}"
            for r in tool_results
        ])

        synthesis_prompt = f"""
        User asked: {message}
        
        I used tools to gather information:
        {results_summary}
        
        Based on these tool results, provide a comprehensive and helpful response to the user.
        Integrate the information naturally and cite the sources when relevant.
        Don't mention the internal tool execution details.
        """
        
        return await self._call_llm(synthesis_prompt)

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text response"""
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group()
        return "{}"

    async def _simple_response(self, message: str) -> str:
        """Generate simple response without tools"""
        prompt = f"Respond to the following message: {message}"
        return await self._call_llm(prompt)

    def get_tool_usage_stats(self) -> Dict:
        """Get statistics about tool usage for optimization"""
        if not self.tool_usage_history:
            return {"total_uses": 0}
        
        # Count usage by tool
        tool_counts = {}
        for usage in self.tool_usage_history:
            tool = usage["tool"]
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

        return {
            "total_uses": len(self.tool_usage_history),
            "tool_counts": tool_counts,
            "most_used_tool": max(tool_counts, key=tool_counts.get) if tool_counts else None,
            "recent_usage": self.tool_usage_history[-5:]  # Last 5 uses
        }

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM - flexible integration"""
        if hasattr(self.llm_client, 'chat'):
            return await self.llm_client.chat(prompt)
        return f"Simulated response to: {prompt[:50]}..."