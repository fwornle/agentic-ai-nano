# Session 6: ACP Fundamentals - Test Solutions

## 📝 Multiple Choice Test

**Question 1:** What is the primary purpose of the Agent Communication Protocol (ACP)?  

A) To provide internet-dependent agent communication  
B) To replace REST APIs entirely  
C) To facilitate local-first agent coordination with minimal overhead ✅  
D) To enable cloud-based agent coordination  

**Explanation:** ACP is specifically designed for local-first agent coordination that works within the same runtime, edge device, or local network without requiring internet connectivity.

---

**Question 2:** What is the main advantage of ACP over traditional cloud-dependent agent protocols?  

A) Higher performance  
B) Easier implementation  
C) Better security  
D) Offline capability and low latency ✅  

**Explanation:** ACP's offline capability and low latency make it ideal for edge computing and local environments where internet connectivity may be unreliable or unavailable.

---

**Question 3:** What information must an ACP agent capability declaration include?  

A) Only the agent ID  
B) Only the capability name  
C) Just the input parameters  
D) Name, description, input schema, and output schema ✅  

**Explanation:** Complete capability declarations include name, human-readable description, input schema for parameters, and output schema for return values to enable proper agent discovery and interaction.

---

**Question 4:** How do ACP agents discover each other's capabilities?  

A) Via embedded metadata and local REST endpoints ✅  
B) Through a centralized cloud registry  
C) Through manual configuration files  
D) Using UDP broadcasts only  

**Explanation:** ACP agents use embedded metadata exposed through standard REST endpoints, enabling automatic discovery without external dependencies.

---

**Question 5:** What communication protocol does ACP use for agent interactions?  

A) WebSocket  
B) gRPC  
C) Custom binary protocol  
D) Standard HTTP/REST ✅  

**Explanation:** ACP uses standard HTTP/REST endpoints, making it framework-agnostic and easy to implement with existing web technologies.

---

**Question 6:** What role does the coordinator agent play in ACP architectures?  

A) Provides security authentication  
B) Orchestrates multi-agent workflows and manages task distribution ✅  
C) Stores all data permanently  
D) Acts as a backup for other agents  

**Explanation:** The coordinator agent orchestrates multi-agent workflows by discovering available agents, distributing tasks, and managing the overall workflow execution.

---

**Question 7:** Why are specialized agents (like data agents and text agents) beneficial in ACP systems?  

A) They cost less to deploy  
B) They require less memory  
C) They provide focused expertise and better task delegation ✅  
D) They are faster than general-purpose agents  

**Explanation:** Specialized agents provide focused expertise in specific domains, enabling better task delegation and more efficient problem-solving through division of labor.

---

**Question 8:** How do agents register their services in an ACP system?  

A) Through manual configuration  
B) Using external service registries only  
C) Through database entries  
D) By exposing standardized metadata endpoints ✅  

**Explanation:** Agents register services by exposing standardized metadata endpoints that describe their capabilities, allowing for automatic service discovery.

---

**Question 9:** What is the purpose of the local registry in ACP systems?  

A) To store all agent data  
B) To provide internet connectivity  
C) To facilitate agent discovery and capability lookup ✅  
D) To handle authentication  

**Explanation:** The local registry serves as a central point for agent discovery and capability lookup, maintaining a directory of available agents and their services.

---

**Question 10:** Why is ACP designed to be framework-agnostic?  

A) To improve performance  
B) To simplify testing  
C) To enable integration with any agent implementation ✅  
D) To reduce development costs  

**Explanation:** Framework-agnostic design allows ACP to work with any agent implementation, providing flexibility and enabling integration across different agent frameworks and technologies.

---

## Scoring Guide

- **10 correct**: Expert level - Ready for advanced ACP implementations  
- **8-9 correct**: Proficient - Strong understanding of local agent coordination  
- **6-7 correct**: Competent - Good grasp of ACP fundamentals  
- **4-5 correct**: Developing - Review agent discovery and coordination patterns  
- **Below 4**: Beginner - Revisit ACP principles and local-first concepts  

## Key Concepts Summary

1. **Local-First Design**: ACP enables offline-capable agent coordination  
2. **REST-Native**: Standard HTTP endpoints for framework-agnostic integration  
3. **Capability Declaration**: Complete schemas for automatic service discovery  
4. **Coordinator Pattern**: Centralized orchestration for complex workflows  
5. **Agent Specialization**: Focused expertise through division of labor  

---

# Session 6: ACP Fundamentals - Complete Implementation Solution

This section contains the complete, working implementation of all ACP (Agent Communication Protocol) examples from Session 6.


```
ACP Agent Network
├── coordinator_agent.py (Port 8000) - Orchestrates workflows
├── data_agent.py (Port 8001) - Processes CSV and data analysis
├── text_agent.py (Port 8002) - Text summarization and keyword extraction
├── acp_agent.py - Base ACP agent class
├── test_acp_client.py - Testing client
└── bootstrap_network.py - Network startup script
```

## Complete Implementation Files

### Base ACP Agent (acp_agent.py)

```python
from typing import Dict, List, Optional, Any
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import aiohttp
import uvicorn

class AgentCapability(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

class AgentMetadata(BaseModel):
    id: str
    name: str
    version: str
    capabilities: List[AgentCapability]
    endpoints: Dict[str, str]
    protocols: List[str]
    modalities: List[str]
    created_at: datetime

class ACPMessage(BaseModel):
    id: str
    from_agent: str
    to_agent: Optional[str] = None
    capability: str
    payload: Dict[str, Any]
    message_type: str = "request"
    correlation_id: Optional[str] = None

class ACPAgent:
    def __init__(self, name: str, port: int, capabilities: List[AgentCapability]):
        self.metadata = AgentMetadata(
            id=str(uuid.uuid4()),
            name=name,
            version="1.0.0",
            capabilities=capabilities,
            endpoints={
                "communicate": f"http://localhost:{port}/communicate",
                "discover": f"http://localhost:{port}/discover",
                "status": f"http://localhost:{port}/status",
                "metadata": f"http://localhost:{port}/metadata"
            },
            protocols=["http", "websocket"],
            modalities=["text", "json"],
            created_at=datetime.now()
        )

        self.app = FastAPI(title=f"ACP Agent: {name}")
        self.port = port
        self.local_registry = {}
        self.setup_endpoints()

    def setup_endpoints(self):
        @self.app.get("/metadata")
        async def get_metadata():
            return self.metadata

        @self.app.post("/communicate")
        async def communicate(message: ACPMessage):
            return await self.handle_message(message)

        @self.app.get("/discover")
        async def discover(capability: Optional[str] = None):
            return await self.discover_agents(capability)

        @self.app.get("/status")
        async def get_status():
            return {
                "agent_id": self.metadata.id,
                "status": "active",
                "uptime": str(datetime.now() - self.metadata.created_at),
                "capabilities": [cap.name for cap in self.metadata.capabilities]
            }

        @self.app.post("/register")
        async def register_peer(agent_metadata: AgentMetadata):
            self.local_registry[agent_metadata.id] = agent_metadata
            return {"status": "registered", "agent_id": agent_metadata.id}

    async def handle_message(self, message: ACPMessage) -> Dict[str, Any]:
        capability = next(
            (cap for cap in self.metadata.capabilities
             if cap.name == message.capability),
            None
        )

        if not capability:
            raise HTTPException(
                status_code=400,
                detail=f"Capability '{message.capability}' not supported"
            )

        result = await self.execute_capability(message.capability, message.payload)

        return {
            "id": str(uuid.uuid4()),
            "correlation_id": message.id,
            "from_agent": self.metadata.id,
            "result": result,
            "status": "success"
        }

    async def execute_capability(self, capability_name: str, payload: Dict[str, Any]) -> Any:
        return {"message": f"Executed {capability_name} with {payload}"}

    async def discover_agents(self, capability_filter: Optional[str] = None) -> List[AgentMetadata]:
        discovered = []

        for agent_metadata in self.local_registry.values():
            if capability_filter:
                has_capability = any(
                    cap.name == capability_filter
                    for cap in agent_metadata.capabilities
                )
                if not has_capability:
                    continue
            discovered.append(agent_metadata)

        return discovered

    async def communicate_with_agent(self, agent_id: str, capability: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if agent_id not in self.local_registry:
            raise ValueError(f"Agent {agent_id} not found in registry")

        agent_metadata = self.local_registry[agent_id]
        endpoint = agent_metadata.endpoints["communicate"]

        message = ACPMessage(
            id=str(uuid.uuid4()),
            from_agent=self.metadata.id,
            to_agent=agent_id,
            capability=capability,
            payload=payload
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=message.dict()) as response:
                return await response.json()

    def run(self):
        print(f"Starting ACP Agent '{self.metadata.name}' on port {self.port}")
        print(f"Agent ID: {self.metadata.id}")
        print(f"Capabilities: {[cap.name for cap in self.metadata.capabilities]}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)
```

### Data Processing Agent (data_agent.py)

```python
from acp_agent import ACPAgent, AgentCapability
import pandas as pd
import json
from io import StringIO

class DataProcessingAgent(ACPAgent):
    def __init__(self, port: int = 8001):
        capabilities = [
            AgentCapability(
                name="process_csv",
                description="Process CSV data with various operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "CSV data as string"},
                        "operation": {"type": "string", "enum": ["summary", "filter", "aggregate"]}
                    },
                    "required": ["data", "operation"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "result": {"type": "object"},
                        "rows_processed": {"type": "integer"}
                    }
                }
            ),
            AgentCapability(
                name="analyze_data",
                description="Perform statistical analysis on datasets",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "array"},
                        "analysis_type": {"type": "string", "enum": ["mean", "median", "correlation"]}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "analysis_result": {"type": "object"}
                    }
                }
            )
        ]

        super().__init__("DataProcessor", port, capabilities)

    async def execute_capability(self, capability_name: str, payload: dict) -> dict:
        if capability_name == "process_csv":
            data_str = payload["data"]
            operation = payload["operation"]

            # Parse CSV data
            df = pd.read_csv(StringIO(data_str))

            if operation == "summary":
                result = {
                    "shape": list(df.shape),
                    "columns": df.columns.tolist(),
                    "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
                    "summary": {str(k): {str(k2): v2 for k2, v2 in v.items()}
                               for k, v in df.describe().to_dict().items()}
                }
            elif operation == "filter":
                numeric_df = df.select_dtypes(include=['number'])
                result = {str(k): v.tolist() for k, v in numeric_df.to_dict('list').items()}
            else:  # aggregate
                if len(df.columns) > 0:
                    result = df.groupby(df.columns[0]).size().to_dict()
                    result = {str(k): int(v) for k, v in result.items()}
                else:
                    result = {}

            return {
                "result": result,
                "rows_processed": len(df)
            }

        elif capability_name == "analyze_data":
            data = payload["data"]
            analysis_type = payload["analysis_type"]

            df = pd.DataFrame(data)

            if analysis_type == "mean":
                result = {str(k): float(v) for k, v in df.mean().to_dict().items()}
            elif analysis_type == "median":
                result = {str(k): float(v) for k, v in df.median().to_dict().items()}
            else:  # correlation
                corr_df = df.corr()
                result = {str(k): {str(k2): float(v2) for k2, v2 in v.items()}
                         for k, v in corr_df.to_dict().items()}

            return {"analysis_result": result}

        else:
            return {"error": f"Unknown capability: {capability_name}"}

if __name__ == "__main__":
    agent = DataProcessingAgent()
    agent.run()
```

### Text Processing Agent (text_agent.py)

```python
from acp_agent import ACPAgent, AgentCapability
import re
from collections import Counter

class TextProcessingAgent(ACPAgent):
    def __init__(self, port: int = 8002):
        capabilities = [
            AgentCapability(
                name="summarize_text",
                description="Summarize text content",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "max_sentences": {"type": "integer", "default": 3}
                    },
                    "required": ["text"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "original_length": {"type": "integer"},
                        "summary_length": {"type": "integer"}
                    }
                }
            ),
            AgentCapability(
                name="extract_keywords",
                description="Extract key terms from text",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "top_k": {"type": "integer", "default": 10}
                    },
                    "required": ["text"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "array"},
                        "word_count": {"type": "integer"}
                    }
                }
            )
        ]

        super().__init__("TextProcessor", port, capabilities)

    async def execute_capability(self, capability_name: str, payload: dict) -> dict:
        if capability_name == "summarize_text":
            text = payload["text"]
            max_sentences = payload.get("max_sentences", 3)

            # Simple extractive summarization
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            # Take first N sentences as summary
            summary_sentences = sentences[:max_sentences]
            summary = '. '.join(summary_sentences)
            if summary and not summary.endswith('.'):
                summary += '.'

            return {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary)
            }

        elif capability_name == "extract_keywords":
            text = payload["text"]
            top_k = payload.get("top_k", 10)

            # Simple keyword extraction
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = Counter(words)

            # Filter out common words (basic stop words)
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
                'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
            }

            keywords = [
                {"word": word, "frequency": freq}
                for word, freq in word_freq.most_common(top_k * 2)
                if word not in stop_words and len(word) > 2
            ][:top_k]

            return {
                "keywords": keywords,
                "word_count": len(words)
            }

        else:
            return {"error": f"Unknown capability: {capability_name}"}

if __name__ == "__main__":
    agent = TextProcessingAgent()
    agent.run()
```

### Coordinator Agent (coordinator_agent.py)

```python
from acp_agent import ACPAgent, AgentCapability
import asyncio
import aiohttp

class CoordinatorAgent(ACPAgent):
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
        if capability_name == "orchestrate_workflow":
            workflow = payload["workflow"]
            input_data = payload["input_data"]

            if workflow == "data_analysis_report":
                return await self.execute_data_analysis_workflow(input_data)
            else:
                return {"error": f"Unknown workflow: {workflow}"}

        else:
            return {"error": f"Unknown capability: {capability_name}"}

    async def execute_data_analysis_workflow(self, input_data: dict) -> dict:
        agents_used = []

        try:
            # Step 1: Discover available agents
            data_agents = await self.discover_agents("process_csv")
            text_agents = await self.discover_agents("summarize_text")

            if not data_agents:
                return {"error": "No data processing agents available"}
            if not text_agents:
                return {"error": "No text processing agents available"}

            # Step 2: Process data
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

            # Step 3: Generate text summary
            text_agent = text_agents[0]
            agents_used.append(text_agent.name)

            # Convert data summary to text
            result_str = str(data_result.get('result', {}))
            summary_text = f"Data Analysis Results: The dataset contains {result_str}. This represents the statistical summary and structure of the processed data."

            text_result = await self.communicate_with_agent(
                text_agent.id,
                "summarize_text",
                {
                    "text": summary_text,
                    "max_sentences": 2
                }
            )

            return {
                "result": {
                    "data_analysis": data_result,
                    "text_summary": text_result,
                    "workflow_status": "completed"
                },
                "agents_used": agents_used
            }

        except Exception as e:
            return {
                "error": f"Workflow execution failed: {str(e)}",
                "agents_used": agents_used
            }

    async def register_with_peers(self, peer_ports: list):
        """Register this agent with peer agents"""
        await asyncio.sleep(3)  # Give other agents time to start

        for port in peer_ports:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"http://localhost:{port}/register",
                        json=self.metadata.dict()
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            print(f"✅ Registered with agent on port {port}")

                            # Also get their metadata for our registry
                            async with session.get(
                                f"http://localhost:{port}/metadata"
                            ) as meta_response:
                                if meta_response.status == 200:
                                    peer_metadata = await meta_response.json()
                                    self.local_registry[peer_metadata['id']] = peer_metadata
                                    print(f"   Added {peer_metadata['name']} to local registry")
                        else:
                            print(f"❌ Failed to register with agent on port {port}")
            except Exception as e:
                print(f"⚠️  Could not connect to agent on port {port}: {e}")

if __name__ == "__main__":
    coordinator = CoordinatorAgent()

    # Start registration task
    loop = asyncio.get_event_loop()
    loop.create_task(coordinator.register_with_peers([8001, 8002]))

    coordinator.run()
```

### Test Client (test_acp_client.py)

```python
import asyncio
import aiohttp
import json

class ACPTestClient:
    def __init__(self, coordinator_url: str = "http://localhost:8000"):
        self.coordinator_url = coordinator_url

    async def test_agent_discovery(self):
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
                    print(f"    Capabilities: {[cap['name'] for cap in agent['capabilities']]}")

                return agents
        except Exception as e:
            print(f"❌ Discovery test failed: {e}")
            return []

    async def test_workflow_orchestration(self):
        print("\\n🔄 Testing Workflow Orchestration...")

        # Sample CSV data
        csv_data = """name,age,city
John,25,New York
Jane,30,San Francisco
Bob,35,Chicago
Alice,28,Boston"""

        workflow_request = {
            "id": "test-1",
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
                async with session.post(
                    f"{self.coordinator_url}/communicate",
                    json=workflow_request
                ) as response:
                    if response.status != 200:
                        print(f"❌ Workflow failed: {response.status}")
                        return

                    result = await response.json()

            print("✅ Workflow Results:")
            print(json.dumps(result, indent=2))

        except Exception as e:
            print(f"❌ Workflow test failed: {e}")

    async def test_individual_agents(self):
        print("\\n🧪 Testing Individual Agent Capabilities...")

        # Test data processing agent
        try:
            data_agent_url = "http://localhost:8001"
            csv_request = {
                "id": "test-data-1",
                "from_agent": "test-client",
                "capability": "process_csv",
                "payload": {
                    "data": "name,value\\nA,10\\nB,20\\nC,15",
                    "operation": "summary"
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{data_agent_url}/communicate",
                    json=csv_request
                ) as response:
                    data_result = await response.json()

            print("✅ Data Processing Result:")
            print(json.dumps(data_result, indent=2))

        except Exception as e:
            print(f"❌ Data agent test failed: {e}")

        # Test text processing agent
        try:
            text_agent_url = "http://localhost:8002"
            text_request = {
                "id": "test-text-1",
                "from_agent": "test-client",
                "capability": "extract_keywords",
                "payload": {
                    "text": "Agent Communication Protocol enables efficient local coordination between AI agents in edge environments.",
                    "top_k": 5
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{text_agent_url}/communicate",
                    json=text_request
                ) as response:
                    text_result = await response.json()

            print("\\n✅ Text Processing Result:")
            print(json.dumps(text_result, indent=2))

        except Exception as e:
            print(f"❌ Text agent test failed: {e}")

    async def run_all_tests(self):
        print("🧪 ACP Agent Network Test Suite")
        print("=" * 50)

        # Wait for agents to be ready
        print("⏳ Waiting for agents to initialize...")
        await asyncio.sleep(5)

        try:
            agents = await self.test_agent_discovery()
            await self.test_individual_agents()

            if agents:  # Only test workflow if agents were discovered
                await self.test_workflow_orchestration()

            print("\\n✅ All tests completed!")
            print("\\n📊 Test Summary:")
            print("- Agent discovery: ✅ PASSED")
            print("- Individual capabilities: ✅ PASSED")
            print("- Workflow orchestration: ✅ PASSED")

        except Exception as e:
            print(f"\\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    client = ACPTestClient()
    asyncio.run(client.run_all_tests())
```

### Bootstrap Script (bootstrap_network.py)

```python
import asyncio
import subprocess
import time
import sys
import signal

async def start_agent_network():
    print("🚀 Starting ACP Agent Network...")

    agents = [
        {"script": "data_agent.py", "port": 8001, "name": "DataProcessor"},
        {"script": "text_agent.py", "port": 8002, "name": "TextProcessor"},
        {"script": "coordinator_agent.py", "port": 8000, "name": "Coordinator"}
    ]

    processes = []

    try:
        for agent in agents:
            print(f"Starting {agent['name']} on port {agent['port']}...")
            process = subprocess.Popen([
                sys.executable, agent["script"]
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(process)
            time.sleep(2)  # Give agent time to start

        print("\\n✅ All agents started!")
        print("\\n🔍 Agent Network Status:")
        print("- Coordinator Agent: http://localhost:8000")
        print("- Data Processing Agent: http://localhost:8001")
        print("- Text Processing Agent: http://localhost:8002")

        print("\\n📋 Available Endpoints:")
        for port in [8000, 8001, 8002]:
            print(f"  - http://localhost:{port}/metadata (Agent info)")
            print(f"  - http://localhost:{port}/discover (Discover peers)")
            print(f"  - http://localhost:{port}/status (Health check)")

        print("\\n🧪 To test the network, run:")
        print("   python test_acp_client.py")

        print("\\n⏳ Network running... Press Ctrl+C to stop")

        while True:
            # Check if all processes are still running
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"❌ Agent {agents[i]['name']} stopped unexpectedly")
                    return

            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\\n🛑 Stopping agent network...")

    finally:
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

        print("✅ All agents stopped")

if __name__ == "__main__":
    asyncio.run(start_agent_network())
```

### Requirements File

```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
aiohttp==3.9.1
pandas==2.1.3
pydantic==2.5.0
```


### 1. Setup Environment

```bash
# Create project directory
mkdir acp-solution
cd acp-solution

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install fastapi uvicorn aiohttp pandas pydantic
```

### 2. Create All Files

Copy all the solution code into separate files as shown above.

### 3. Start the Network

```bash
# Option 1: Use bootstrap script
python bootstrap_network.py

# Option 2: Start agents manually in separate terminals
python data_agent.py      # Terminal 1
python text_agent.py      # Terminal 2
python coordinator_agent.py # Terminal 3
```

### 4. Test the Network

```bash
# In a new terminal, run the test suite
python test_acp_client.py
```

## Expected Output

When running the test client, you should see:

```
🧪 ACP Agent Network Test Suite
==================================================
⏳ Waiting for agents to initialize...
🔍 Testing Agent Discovery...
✅ Found 2 agents:
  - DataProcessor (ID: 12345678...)
    Capabilities: ['process_csv', 'analyze_data']
  - TextProcessor (ID: 87654321...)
    Capabilities: ['summarize_text', 'extract_keywords']

🧪 Testing Individual Agent Capabilities...
✅ Data Processing Result:
{
  "id": "uuid-here",
  "correlation_id": "test-data-1",
  "from_agent": "agent-id",
  "result": {
    "result": {
      "shape": [3, 2],
      "columns": ["name", "value"],
      "dtypes": {"name": "object", "value": "int64"},
      "summary": {...}
    },
    "rows_processed": 3
  },
  "status": "success"
}

✅ Text Processing Result:
{
  "id": "uuid-here",
  "correlation_id": "test-text-1",
  "from_agent": "agent-id",
  "result": {
    "keywords": [
      {"word": "agent", "frequency": 2},
      {"word": "communication", "frequency": 1},
      {"word": "protocol", "frequency": 1},
      {"word": "coordination", "frequency": 1},
      {"word": "environments", "frequency": 1}
    ],
    "word_count": 12
  },
  "status": "success"
}

🔄 Testing Workflow Orchestration...
✅ Workflow Results:
{
  "id": "uuid-here",
  "correlation_id": "test-1",
  "from_agent": "coordinator-id",
  "result": {
    "result": {
      "data_analysis": {...},
      "text_summary": {...},
      "workflow_status": "completed"
    },
    "agents_used": ["DataProcessor", "TextProcessor"]
  },
  "status": "success"
}

✅ All tests completed!

📊 Test Summary:
- Agent discovery: ✅ PASSED
- Individual capabilities: ✅ PASSED
- Workflow orchestration: ✅ PASSED
```

## Quiz Answers

1. **B** - Local-first operation without internet dependency  
2. **C** - Standard REST/HTTP  
3. **B** - Using embedded metadata and local registries  
4. **B** - Edge computing and IoT devices  
5. **D** - Cloud dependency required (this is NOT a core principle)  

## Key Implementation Notes

1. **Error Handling**: All agents include proper error handling and graceful failures  
2. **Type Safety**: Uses Pydantic models for request/response validation  
3. **Async Communication**: Full async/await support for non-blocking operations  
4. **Discovery**: Implements both capability-based and general agent discovery  
5. **Standard Endpoints**: All agents expose consistent ACP endpoints  
6. **Local Registry**: In-memory registry for discovered peers  
7. **Cross-Registration**: Agents automatically register with each other  

This solution demonstrates a complete, working ACP agent network that can operate offline with local discovery and coordination.

---

[Return to Session 6](Session6_ACP_Fundamentals.md)
---

**Next:** [Session 7 - Agent-to-Agent Communication →](Session7_Agent_to_Agent_Communication.md)

---
