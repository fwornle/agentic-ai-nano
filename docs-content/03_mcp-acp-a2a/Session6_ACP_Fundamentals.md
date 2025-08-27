# Session 6: Agent Communication Protocol (ACP) - Local-First Multi-Agent Networks

The Agent Communication Protocol (ACP) enables agents to discover and communicate within local environments without cloud dependencies. This session covers ACP architecture, agent discovery mechanisms, specialized agent creation, and multi-agent workflow orchestration.

![ACP Architecture](images/acp-architecture-overview.png)

---

## Part 1: ACP Architecture Fundamentals

ACP addresses how agents efficiently coordinate within edge environments and local networks without cloud dependencies.

### Traditional vs ACP Approach:

**Traditional Cloud-Centric:**
```
Agent A → Cloud API Gateway → Message Queue → Agent B
   ↓         (requires internet)         (high latency)     ↓
Complex setup     Security risks        Dependency failure    Cost scaling
```

**ACP Local-First:**
```
Agent A ←→ Local Event Bus ←→ Agent B
   ↓      (IPC/local network)     ↓
RESTful API    Millisecond latency    Autonomous operation
```

### ACP Core Architecture

ACP defines three core layers based on the IBM BeeAI standard:

1. **Discovery Layer**: Local broadcast mechanisms for agent capability advertisement
2. **Communication Layer**: RESTful interfaces for message exchange and streaming
3. **Coordination Layer**: Event-driven patterns for workflow orchestration

### Key Technical Features:
- **Decentralized Discovery**: Agents advertise capabilities through local broadcast without external registries
- **RESTful Communication**: Standard HTTP endpoints enable cross-framework interoperability
- **Event-Driven Architecture**: Local message buses provide real-time coordination
- **Autonomous Operation**: Full functionality during network partitions or offline scenarios
- **Low Latency**: Local IPC communication provides sub-millisecond response times

---

## Part 2: Implementing ACP Agents

Let's start by understanding the basic structure of an ACP agent. We'll build this step by step.

### Step 2.1: Agent Metadata and Capabilities

Every ACP agent must describe what it can do. This is called **capability declaration**:

```python

# From [`src/session6/acp_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session6/acp_agent.py)

class AgentCapability(BaseModel):
    """Defines what an agent can do"""
    name: str                    # e.g., "process_data"
    description: str             # Human-readable description
    input_schema: Dict[str, Any] # What parameters it needs
    output_schema: Dict[str, Any] # What it returns
```


### Example Capability:
```python
weather_capability = AgentCapability(
    name="get_weather",
    description="Get current weather for any city",
    input_schema={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"}
        },
        "required": ["city"]
    },
    output_schema={
        "type": "object", 
        "properties": {
            "temperature": {"type": "number"},
            "condition": {"type": "string"}
        }
    }
)
```

### Step 2.2: Agent Identity and Discovery

Each agent needs a unique identity and way to be discovered:

```python

# From [`src/session6/acp_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session6/acp_agent.py)

class AgentMetadata(BaseModel):
    """Complete agent information for discovery"""
    id: str                      # Unique identifier
    name: str                    # Human-readable name
    capabilities: List[AgentCapability]  # What it can do
    endpoints: Dict[str, str]    # How to reach it
    protocols: List[str]         # Communication methods
    created_at: datetime         # When it started
```

### Real Example:
```python
agent_metadata = AgentMetadata(
    id="agent-123e4567-e89b-12d3-a456-426614174000",
    name="WeatherAgent",
    capabilities=[weather_capability],
    endpoints={
        "communicate": "http://localhost:8001/communicate",
        "discover": "http://localhost:8001/discover"
    },
    protocols=["http"],
    created_at=datetime.now()
)
```

### Step 2.3: Standard ACP Endpoints

Every ACP agent exposes four standard REST endpoints:

```python

# From [`src/session6/acp_agent.py`] - simplified

@app.get("/metadata")
async def get_metadata():
    """Return this agent's information"""
    return self.metadata

@app.post("/communicate") 
async def communicate(message: ACPMessage):
    """Handle requests from other agents"""
    return await self.handle_message(message)
```

Additional endpoints for discovery and health checks:

```python
@app.get("/discover")
async def discover(capability: Optional[str] = None):
    """Find other agents, optionally filtered by capability"""
    return await self.discover_agents(capability)

@app.get("/status")
async def get_status():
    """Health check - is this agent working?"""
    return {"status": "active", "uptime": "..."}
```


---

## Part 3: Creating Specialized Agents

Now let's build specialized agents for different tasks. We'll create three agents that work together:

### Step 3.1: Data Processing Agent

Our first specialized agent handles CSV data processing and analysis.

### Capabilities Declaration:
```python

# From [`src/session6/data_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session6/data_agent.py)

capabilities = [
    AgentCapability(
        name="process_csv",
        description="Process CSV data with various operations",
        input_schema={
            "type": "object",
            "properties": {
                "data": {"type": "string"},  # CSV as text
                "operation": {"type": "string", "enum": ["summary", "filter"]}
            }
        }
    )
]
```

### Key Implementation Pattern:
```python
async def execute_capability(self, capability_name: str, payload: dict) -> dict:
    """Route capability requests to specific handlers"""
    
    if capability_name == "process_csv":
        return await self._process_csv(payload)
    else:
        return {"error": f"Unknown capability: {capability_name}"}
```


### Sample CSV Processing:
```python
async def _process_csv(self, payload: dict) -> dict:
    data_str = payload["data"]
    operation = payload["operation"]
    
    # Parse CSV using pandas
    df = pd.read_csv(StringIO(data_str))
    
    if operation == "summary":
        return {
            "result": {
                "rows": len(df),
                "columns": df.columns.tolist(),
                "summary": df.describe().to_dict()
            },
            "rows_processed": len(df)
        }
```

**Test It:** Start the data agent and try:
```bash
curl -X POST http://localhost:8001/communicate \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-1",
    "from_agent": "tester", 
    "capability": "process_csv",
    "payload": {
      "data": "name,age\nJohn,25\nJane,30",
      "operation": "summary"
    }
  }'
```

### Step 3.2: Text Processing Agent

Our second agent specializes in natural language processing tasks.

### Capabilities Declaration:
```python

# From [`src/session6/text_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session6/text_agent.py)

capabilities = [
    AgentCapability(
        name="summarize_text",
        description="Summarize text content",
        input_schema={
            "properties": {
                "text": {"type": "string"},
                "max_sentences": {"type": "integer", "default": 3}
            }
        }
    ),
    AgentCapability(
        name="extract_keywords", 
        description="Extract key terms from text"
    )
]
```

### Text Summarization Implementation:
```python
async def _summarize_text(self, payload: dict) -> dict:
    text = payload["text"]
    max_sentences = payload.get("max_sentences", 3)
    
    # Simple extractive summarization
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Take first N sentences (basic approach)
    summary = '. '.join(sentences[:max_sentences])
    
    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary)
    }
```


### Step 3.3: Coordinator Agent - The Orchestrator

The coordinator agent doesn't process data itself—it **orchestrates other agents** to complete complex workflows.

### The Coordination Pattern:

ACP coordination follows a clear discovery-then-execute pattern. Let's break this down into stages:

### Stage 1: Agent Discovery and Validation
```python

# From [`src/session6/coordinator_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session6/coordinator_agent.py) - Discovery phase

async def _execute_data_analysis_workflow(self, input_data: dict) -> dict:
    agents_used = []
    
    # Step 1: Discover required agents using capability-based lookup
    print("🔍 Discovering agents...")
    data_agents = await self.discover_agents("process_csv")
    text_agents = await self.discover_agents("summarize_text")
    
    # Validate agents are available before proceeding
    if not data_agents or not text_agents:
        raise ValueError("Required agents not available")
```


### Stage 2: Data Processing Coordination
```python
    # Step 2: Coordinate data processing with the discovered agent
    print("📊 Processing data...")
    data_result = await self.communicate_with_agent(
        data_agents[0].id,           # Target the first available data agent
        "process_csv",               # Request specific capability
        {"data": input_data["csv_data"], "operation": "summary"}
    )
    
    # Track which agents participated in the workflow
    agents_used.append(data_agents[0].id)
```


### Stage 3: Text Processing and Result Aggregation
```python
    # Step 3: Generate summary using processed data
    print("📝 Generating summary...")
    summary_text = f"Analysis Results: {data_result['result']}"
    text_result = await self.communicate_with_agent(
        text_agents[0].id,
        "summarize_text",
        {"text": summary_text, "max_sentences": 2}
    )
    
    agents_used.append(text_agents[0].id)
    
    # Return aggregated results from multiple agents
    return {
        "data_analysis": data_result,
        "text_summary": text_result,
        "agents_used": agents_used
    }
```

### Key Coordination Concepts:

1. **Discovery Before Action**: Always find available agents first
2. **Error Handling**: Check if required agents are available
3. **Sequential Execution**: Process data, then summarize results
4. **Result Aggregation**: Combine outputs from multiple agents

---

## Part 4: Agent Discovery and Registration

### How Agents Find Each Other

ACP uses a **local registry pattern** where agents register with each other:

```python

# From [`src/session6/coordinator_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session6/coordinator_agent.py)

async def register_with_peers(self, peer_ports: list):
    """Register with known peer agents"""
    
    for port in peer_ports:
        try:
            # Send our metadata to the peer
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://localhost:{port}/register",
                    json=self.metadata.dict()
                ) as response:
                    if response.status == 200:
                        print(f"✅ Registered with agent on port {port}")
        except Exception as e:
            print(f"⚠️ Could not connect to port {port}: {e}")
```

### Discovery Process Flow

```
1. Agent A starts up
2. Agent A registers with known peers (ports 8001, 8002)
3. Peers store Agent A's metadata in their local registries  
4. When Agent A calls /discover, peers return their stored metadata
5. Agent A can now communicate with discovered agents
```

### Discovery Request Example:
```python

# Find all agents that can process CSV

data_agents = await self.discover_agents("process_csv")

# Find any available agents

all_agents = await self.discover_agents()
```

---

## Part 5: Running the Complete Network

### Step 5.1: Starting the Network

We've created a bootstrap script to manage the entire network:

```python

# From [`src/session6/bootstrap.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session6/bootstrap.py) - simplified

agents = [
    {"script": "data_agent.py", "port": 8001, "name": "DataProcessor"},
    {"script": "text_agent.py", "port": 8002, "name": "TextProcessor"},  
    {"script": "coordinator_agent.py", "port": 8000, "name": "Coordinator"}
]

for agent in agents:
    print(f"Starting {agent['name']} on port {agent['port']}...")
    process = subprocess.Popen([sys.executable, agent["script"]])
    time.sleep(2)  # Let each agent start
```

### Start the Network:
```bash
cd [`src/session6`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session6)
pip install -r requirements.txt
python bootstrap.py
```

### Expected Output:
```
Starting ACP Agent Network...
   🔧 Starting DataProcessor on port 8001...
   🔧 Starting TextProcessor on port 8002...
   🔧 Starting Coordinator on port 8000...

✅ All agents started successfully!

🔍 ACP Network Status:
DataProcessor    | Port 8001 | 🟢 Running  
TextProcessor    | Port 8002 | 🟢 Running
Coordinator      | Port 8000 | 🟢 Running
```

### Step 5.2: Testing the Network

Run the test client to verify everything works:

```bash
python test_client.py
```

The test verifies agent discovery, individual capabilities, and complete workflow execution.

### Sample Test Output:
```
🧪 ACP Agent Network Test Suite
🔍 Testing Agent Discovery...
✅ Found 2 agents:
  - DataProcessor (capabilities: ['process_csv', 'analyze_data'])
  - TextProcessor (capabilities: ['summarize_text', 'extract_keywords'])

📊 Testing Data Processing Agent...
   ✅ Data processing successful
   Processed 4 rows
   📋 Columns: ['name', 'age', 'city', 'salary']

🔄 Testing Workflow Orchestration...
   📤 Sending workflow request...
   ✅ Workflow completed successfully
   🤝 Agents coordinated: ['DataProcessor', 'TextProcessor']
```

---

## Part 6: Understanding the Communication Flow

### Message Structure

Every ACP message follows this standard format:

```python

# From [`src/session6/acp_agent.py`](https://github.com/fwornle/agentic-ai-nano/blob/main/docs-content/03_mcp-acp-a2a/src/session6/acp_agent.py)

class ACPMessage(BaseModel):
    id: str                    # Unique message ID
    from_agent: str           # Who sent it
    to_agent: Optional[str]   # Who should receive it (optional)
    capability: str           # What to do
    payload: Dict[str, Any]   # Input parameters
    message_type: str = "request"  # request/response/notification
```

### Complete Communication Example

Let's trace a complete workflow execution:

**1. Client Request:**
```json
{
  "id": "workflow-123",
  "from_agent": "test-client",
  "capability": "orchestrate_workflow",
  "payload": {
    "workflow": "data_analysis_report",
    "input_data": {"csv_data": "name,age\nJohn,25"}
  }
}
```

**2. Coordinator Discovery:**
```bash
GET http://localhost:8000/discover?capability=process_csv

# Returns: [{"id": "data-agent-456", "name": "DataProcessor", ...}]

```

**3. Coordinator → Data Agent:**
```json
{
  "id": "msg-789", 
  "from_agent": "coordinator-123",
  "to_agent": "data-agent-456",
  "capability": "process_csv",
  "payload": {
    "data": "name,age\nJohn,25",
    "operation": "summary"
  }
}
```

**4. Data Agent Response:**
```json
{
  "id": "response-101",
  "correlation_id": "msg-789",
  "from_agent": "data-agent-456", 
  "result": {
    "rows_processed": 1,
    "result": {"columns": ["name", "age"], "shape": [1, 2]}
  },
  "status": "success"
}
```

**5. Coordinator → Text Agent:**
```json
{
  "capability": "summarize_text",
  "payload": {
    "text": "Analysis Results: 1 row with columns name, age",
    "max_sentences": 2
  }
}
```

**6. Final Response to Client:**
```json
{
  "result": {
    "data_analysis": {...},
    "text_summary": {...},
    "workflow_status": "completed"
  },
  "agents_used": ["DataProcessor", "TextProcessor"]
}
```

---

## Key Takeaways

1. **Local-First Design**: ACP agents work without internet, perfect for edge environments
2. **Standard REST**: No specialized libraries—any HTTP client can communicate
3. **Capability-Based Discovery**: Agents find each other by what they can do, not who they are
4. **Orchestration Pattern**: Coordinator agents manage complex workflows without doing the work themselves
5. **Error Resilience**: Always check if required agents are available before starting workflows

## What's Next?

In the next session, you'll learn how these local ACP agents can communicate with external systems using **Agent-to-Agent (A2A) Protocol** for enterprise-scale collaboration across organizational boundaries.

---

## Multiple Choice Test - Session 6

Test your understanding of ACP Fundamentals:

**Question 1:** What is the primary purpose of the Agent Communication Protocol (ACP)?

A) To provide internet-dependent agent communication  
B) To replace REST APIs entirely  
C) To facilitate local-first agent coordination with minimal overhead  
D) To enable cloud-based agent coordination  

**Question 2:** What is the main advantage of ACP over traditional cloud-dependent agent protocols?

A) Higher performance  
B) Easier implementation  
C) Better security  
D) Offline capability and low latency  

**Question 3:** What information must an ACP agent capability declaration include?

A) Only the agent ID  
B) Only the capability name  
C) Just the input parameters  
D) Name, description, input schema, and output schema  

**Question 4:** How do ACP agents discover each other's capabilities?

A) Via embedded metadata and local REST endpoints  
B) Through a centralized cloud registry  
C) Through manual configuration files  
D) Using UDP broadcasts only  

**Question 5:** What communication protocol does ACP use for agent interactions?

A) WebSocket  
B) gRPC  
C) Custom binary protocol  
D) Standard HTTP/REST  

**Question 6:** What role does the coordinator agent play in ACP architectures?

A) Provides security authentication  
B) Orchestrates multi-agent workflows and manages task distribution  
C) Stores all data permanently  
D) Acts as a backup for other agents  

**Question 7:** Why are specialized agents (like data agents and text agents) beneficial in ACP systems?

A) They cost less to deploy  
B) They require less memory  
C) They provide focused expertise and better task delegation  
D) They are faster than general-purpose agents  

**Question 8:** How do agents register their services in an ACP system?

A) Through manual configuration  
B) Using external service registries only  
C) Through database entries  
D) By exposing standardized metadata endpoints  

**Question 9:** What is the purpose of the local registry in ACP systems?

A) To store all agent data  
B) To provide internet connectivity  
C) To facilitate agent discovery and capability lookup  
D) To handle authentication  

**Question 10:** Why is ACP designed to be framework-agnostic?

A) To improve performance  
B) To simplify testing  
C) To enable integration with any agent implementation  
D) To reduce development costs  

[**🗂️ View Test Solutions →**](Session6_Test_Solutions.md)

---

## Navigation

**Previous:** [Session 5 - Secure MCP Server](Session5_Secure_MCP_Server.md)

**Note:** Advanced ACP patterns and production deployment strategies are covered in Sessions 8 and 9, focusing on advanced workflows and production deployment.

**Next:** [Session 7 - Agent-to-Agent Communication →](Session7_Agent_to_Agent_Communication.md)