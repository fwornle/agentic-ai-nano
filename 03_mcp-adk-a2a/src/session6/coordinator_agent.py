"""
Coordinator Agent

Orchestrates workflows by discovering and communicating with other ACP agents.
Demonstrates multi-agent coordination and workflow management.
"""

from acp_agent import ACPAgent, AgentCapability
import asyncio
import aiohttp


class CoordinatorAgent(ACPAgent):
    """Agent that coordinates other agents to complete complex workflows"""
    
    def __init__(self, port: int = 8000):
        capabilities = [
            AgentCapability(
                name="orchestrate_workflow",
                description="Coordinate multiple agents to complete complex tasks",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow": {"type": "string"},
                        "input_data": {"type": "object"}
                    },
                    "required": ["workflow", "input_data"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "result": {"type": "object"},
                        "agents_used": {"type": "array"}
                    }
                }
            )
        ]
        
        super().__init__("Coordinator", port, capabilities)

    async def execute_capability(self, capability_name: str, payload: dict) -> dict:
        """Execute coordination capabilities"""
        
        if capability_name == "orchestrate_workflow":
            workflow = payload["workflow"]
            input_data = payload["input_data"]
            
            if workflow == "data_analysis_report":
                return await self._execute_data_analysis_workflow(input_data)
            else:
                return {"error": f"Unknown workflow: {workflow}"}
        
        else:
            return {"error": f"Unknown capability: {capability_name}"}

    async def _execute_data_analysis_workflow(self, input_data: dict) -> dict:
        """Coordinate data processing and text summarization workflow"""
        agents_used = []
        
        try:
            # Step 1: Discover required agents
            print("🔍 Discovering agents...")
            data_agents = await self.discover_agents("process_csv")
            text_agents = await self.discover_agents("summarize_text")
            
            # Validate we have required agents
            if not data_agents:
                return {"error": "No data processing agents available"}
            if not text_agents:
                return {"error": "No text processing agents available"}
            
            print(f"   Found {len(data_agents)} data agents and {len(text_agents)} text agents")
            
            # Step 2: Process data with data agent
            print("📊 Processing data...")
            data_agent = data_agents[0]
            agents_used.append(data_agent.name)
            
            data_result = await self.communicate_with_agent(
                data_agent.id,
                "process_csv",
                {
                    "data": input_data["csv_data"],
                    "operation": "summary"
                }
            )
            
            # Check for data processing errors
            if "error" in data_result.get("result", {}):
                return {"error": f"Data processing failed: {data_result['result']['error']}"}
            
            # Step 3: Generate text summary
            print("📝 Generating summary...")
            text_agent = text_agents[0]
            agents_used.append(text_agent.name)
            
            # Convert data summary to readable text
            result_info = data_result.get('result', {})
            result_str = str(result_info.get('result', {}))
            rows_processed = result_info.get('rows_processed', 0)
            
            summary_text = f"""Data Analysis Results: The dataset contains {rows_processed} rows. 
Statistical analysis shows: {result_str}. This represents the comprehensive 
summary and structure of the processed data including column information, 
data types, and statistical measures."""
            
            text_result = await self.communicate_with_agent(
                text_agent.id,
                "summarize_text",
                {
                    "text": summary_text,
                    "max_sentences": 2
                }
            )
            
            # Step 4: Combine results
            print("✅ Workflow completed successfully")
            
            return {
                "result": {
                    "data_analysis": data_result,
                    "text_summary": text_result,
                    "workflow_status": "completed",
                    "agents_coordinated": len(agents_used)
                },
                "agents_used": agents_used
            }
            
        except Exception as e:
            return {
                "error": f"Workflow execution failed: {str(e)}",
                "agents_used": agents_used
            }

    async def register_with_peers(self, peer_ports: list):
        """Register this coordinator with peer agents"""
        print("🔗 Registering with peer agents...")
        await asyncio.sleep(3)  # Give other agents time to start
        
        for port in peer_ports:
            try:
                async with aiohttp.ClientSession() as session:
                    # Register ourselves with the peer
                    async with session.post(
                        f"http://localhost:{port}/register",
                        json=self.metadata.dict()
                    ) as response:
                        if response.status == 200:
                            print(f"   ✅ Registered with agent on port {port}")
                            
                            # Get their metadata for our registry
                            async with session.get(
                                f"http://localhost:{port}/metadata"
                            ) as meta_response:
                                if meta_response.status == 200:
                                    peer_metadata = await meta_response.json()
                                    self.local_registry[peer_metadata['id']] = peer_metadata
                                    print(f"   📝 Added {peer_metadata['name']} to registry")
                        else:
                            print(f"   ❌ Failed to register with port {port}")
            except Exception as e:
                print(f"   ⚠️  Could not connect to port {port}: {e}")


if __name__ == "__main__":
    coordinator = CoordinatorAgent()
    
    # Start registration with known peer ports
    loop = asyncio.get_event_loop()
    loop.create_task(coordinator.register_with_peers([8001, 8002]))
    
    coordinator.run()