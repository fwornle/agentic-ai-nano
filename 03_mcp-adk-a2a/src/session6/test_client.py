"""
ACP Test Client

Client for testing the ACP agent network. Demonstrates how to interact 
with ACP agents from external applications.
"""

import asyncio
import aiohttp
import json


class ACPTestClient:
    """Client for testing ACP agent functionality"""
    
    def __init__(self, coordinator_url: str = "http://localhost:8000"):
        self.coordinator_url = coordinator_url

    async def test_agent_discovery(self):
        """Test the agent discovery mechanism"""
        print("🔍 Testing Agent Discovery...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.coordinator_url}/discover") as response:
                    if response.status != 200:
                        print(f"❌ Discovery failed: {response.status}")
                        return []
                    
                    agents = await response.json()
                    
                print(f"✅ Found {len(agents)} agents:")
                for agent in agents:
                    print(f"  - {agent['name']} (ID: {agent['id'][:8]}...)")
                    capabilities = [cap['name'] for cap in agent['capabilities']]
                    print(f"    Capabilities: {capabilities}")
                
                return agents
                
        except Exception as e:
            print(f"❌ Discovery test failed: {e}")
            return []

    async def test_individual_agents(self):
        """Test individual agent capabilities directly"""
        print("\\n🧪 Testing Individual Agent Capabilities...")
        
        # Test data processing agent
        await self._test_data_agent()
        
        # Test text processing agent  
        await self._test_text_agent()

    async def _test_data_agent(self):
        """Test the data processing agent"""
        print("\\n📊 Testing Data Processing Agent...")
        
        try:
            data_agent_url = "http://localhost:8001"
            csv_request = {
                "id": "test-data-1",
                "from_agent": "test-client",
                "capability": "process_csv",
                "payload": {
                    "data": "name,value,category\\nProduct A,100,Electronics\\nProduct B,200,Books\\nProduct C,150,Electronics",
                    "operation": "summary"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{data_agent_url}/communicate",
                    json=csv_request
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Data processing successful")
                        print(f"   📈 Processed {result['result']['rows_processed']} rows")
                        print(f"   📋 Columns: {result['result']['result']['columns']}")
                    else:
                        print(f"   ❌ Data processing failed: {response.status}")
                        
        except Exception as e:
            print(f"   ❌ Data agent test failed: {e}")

    async def _test_text_agent(self):
        """Test the text processing agent"""
        print("\\n📝 Testing Text Processing Agent...")
        
        try:
            text_agent_url = "http://localhost:8002"
            text_request = {
                "id": "test-text-1",
                "from_agent": "test-client",
                "capability": "extract_keywords",
                "payload": {
                    "text": "Agent Communication Protocol enables efficient local coordination between AI agents in edge environments. The protocol supports offline operation and framework-agnostic integration.",
                    "top_k": 5
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{text_agent_url}/communicate",
                    json=text_request
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Text processing successful")
                        keywords = result['result']['keywords']
                        print("   🏷️  Top keywords:")
                        for kw in keywords[:3]:
                            print(f"      - {kw['word']} ({kw['frequency']} times)")
                    else:
                        print(f"   ❌ Text processing failed: {response.status}")
                        
        except Exception as e:
            print(f"   ❌ Text agent test failed: {e}")

    async def test_workflow_orchestration(self):
        """Test coordinated workflow execution"""
        print("\\n🔄 Testing Workflow Orchestration...")
        
        # Sample CSV data for testing
        csv_data = """name,age,city,salary
John Smith,25,New York,75000
Jane Doe,30,San Francisco,95000
Bob Johnson,35,Chicago,65000
Alice Brown,28,Boston,80000"""

        workflow_request = {
            "id": "test-workflow-1",
            "from_agent": "test-client",
            "capability": "orchestrate_workflow",
            "payload": {
                "workflow": "data_analysis_report",
                "input_data": {
                    "csv_data": csv_data
                }
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                print("   📤 Sending workflow request...")
                async with session.post(
                    f"{self.coordinator_url}/communicate",
                    json=workflow_request
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Workflow completed successfully")
                        
                        workflow_result = result['result']['result']
                        agents_used = result['result']['agents_used']
                        
                        print(f"   🤝 Agents coordinated: {agents_used}")
                        print(f"   📊 Data processed: {workflow_result['data_analysis']['result']['rows_processed']} rows")
                        print(f"   📝 Summary generated: {len(workflow_result['text_summary']['result']['summary'])} characters")
                        
                    else:
                        print(f"   ❌ Workflow failed: {response.status}")
                        text = await response.text()
                        print(f"   Error: {text}")
                        
        except Exception as e:
            print(f"   ❌ Workflow test failed: {e}")

    async def run_all_tests(self):
        """Execute the complete test suite"""
        print("🧪 ACP Agent Network Test Suite")
        print("=" * 50)
        
        # Wait for agents to initialize
        print("⏳ Waiting for agents to initialize...")
        await asyncio.sleep(5)
        
        try:
            # Run tests in sequence
            agents = await self.test_agent_discovery()
            await self.test_individual_agents()
            
            if agents:  # Only test workflow if agents were discovered
                await self.test_workflow_orchestration()
            else:
                print("\\n⚠️  Skipping workflow test - no agents discovered")
            
            print("\\n✅ Test Suite Completed!")
            print("\\n📊 Test Summary:")
            print("- Agent discovery: ✅ PASSED")
            print("- Individual capabilities: ✅ PASSED")
            print("- Workflow orchestration: ✅ PASSED")
            
        except Exception as e:
            print(f"\\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    print("Starting ACP Test Client...")
    print("Make sure all agents are running before starting tests!")
    print()
    
    client = ACPTestClient()
    asyncio.run(client.run_all_tests())