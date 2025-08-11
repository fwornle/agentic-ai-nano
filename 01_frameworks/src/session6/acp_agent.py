"""
Base ACP Agent Implementation

This module provides the foundational ACPAgent class that implements
the Agent Communication Protocol for local agent coordination.
"""

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
    """Defines what an agent can do"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class AgentMetadata(BaseModel):
    """Complete agent information for discovery"""
    id: str
    name: str
    version: str
    capabilities: List[AgentCapability]
    endpoints: Dict[str, str]
    protocols: List[str]
    modalities: List[str]
    created_at: datetime


class ACPMessage(BaseModel):
    """Standard ACP message format"""
    id: str
    from_agent: str
    to_agent: Optional[str] = None
    capability: str
    payload: Dict[str, Any]
    message_type: str = "request"
    correlation_id: Optional[str] = None


class ACPAgent:
    """Base class for all ACP-compatible agents"""
    
    def __init__(self, name: str, port: int, capabilities: List[AgentCapability]):
        # Create unique agent metadata
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
        
        # Set up FastAPI server
        self.app = FastAPI(title=f"ACP Agent: {name}")
        self.port = port
        self.local_registry = {}  # Store discovered peers
        self.setup_endpoints()

    def setup_endpoints(self):
        """Set up standard ACP REST endpoints"""
        
        @self.app.get("/metadata")
        async def get_metadata():
            """Return this agent's metadata"""
            return self.metadata

        @self.app.post("/communicate")
        async def communicate(message: ACPMessage):
            """Handle incoming messages from other agents"""
            return await self.handle_message(message)

        @self.app.get("/discover")
        async def discover(capability: Optional[str] = None):
            """Discover other agents with optional capability filter"""
            return await self.discover_agents(capability)

        @self.app.get("/status")
        async def get_status():
            """Return current agent status"""
            return {
                "agent_id": self.metadata.id,
                "status": "active",
                "uptime": str(datetime.now() - self.metadata.created_at),
                "capabilities": [cap.name for cap in self.metadata.capabilities]
            }

        @self.app.post("/register")
        async def register_peer(agent_metadata: AgentMetadata):
            """Register another agent in our local registry"""
            self.local_registry[agent_metadata.id] = agent_metadata
            return {"status": "registered", "agent_id": agent_metadata.id}

    async def handle_message(self, message: ACPMessage) -> Dict[str, Any]:
        """Process incoming ACP messages"""
        
        # Find the requested capability
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
        
        # Execute the capability (implemented in subclasses)
        result = await self.execute_capability(message.capability, message.payload)
        
        return {
            "id": str(uuid.uuid4()),
            "correlation_id": message.id,
            "from_agent": self.metadata.id,
            "result": result,
            "status": "success"
        }

    async def execute_capability(self, capability_name: str, payload: Dict[str, Any]) -> Any:
        """Override in subclass to implement specific capabilities"""
        return {"message": f"Executed {capability_name} with {payload}"}

    async def discover_agents(self, capability_filter: Optional[str] = None) -> List[AgentMetadata]:
        """Discover other agents in the local environment"""
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
        """Send message to another agent"""
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
        """Start the ACP agent server"""
        print(f"Starting ACP Agent '{self.metadata.name}' on port {self.port}")
        print(f"Agent ID: {self.metadata.id}")
        print(f"Capabilities: {[cap.name for cap in self.metadata.capabilities]}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)