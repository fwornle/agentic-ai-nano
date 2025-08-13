"""
A2A Message Protocol Definitions

This module defines the core message structures and protocols for Agent-to-Agent
communication, including message types, agent capabilities, and profiles.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid
import json


class MessageType(Enum):
    """Types of A2A messages."""
    REQUEST = "request"           # Request for service
    RESPONSE = "response"         # Response to request
    BROADCAST = "broadcast"       # Broadcast to multiple agents
    DISCOVERY = "discovery"       # Agent discovery request
    ANNOUNCEMENT = "announcement" # Agent capability announcement
    HEARTBEAT = "heartbeat"      # Agent health check
    ERROR = "error"              # Error notification


class Priority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class A2AMessage:
    """Standard A2A communication message."""
    
    # Message identification
    message_id: str = None
    correlation_id: str = None  # Links related messages
    message_type: MessageType = MessageType.REQUEST
    
    # Routing information
    sender_id: str = None
    recipient_id: str = None    # Specific agent or None for broadcast
    reply_to: str = None        # Where to send response
    
    # Message metadata
    timestamp: str = None
    priority: Priority = Priority.NORMAL
    ttl: int = 300             # Time to live in seconds
    
    # Content
    action: str = None          # What action to perform
    payload: Dict[str, Any] = None
    capabilities_required: List[str] = None
    
    # Response handling
    requires_response: bool = False
    timeout: int = 30          # Response timeout in seconds
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.payload is None:
            self.payload = {}
        if self.capabilities_required is None:
            self.capabilities_required = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        data = asdict(self)
        # Convert enums to their values
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary."""
        # Convert enum values back to enums
        if 'message_type' in data:
            data['message_type'] = MessageType(data['message_type'])
        if 'priority' in data:
            data['priority'] = Priority(data['priority'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Serialize message to JSON."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'A2AMessage':
        """Deserialize message from JSON."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class AgentCapability:
    """Describes an agent's capability."""
    
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    cost: float = 0.0           # Resource cost
    latency: float = 1.0        # Expected latency in seconds
    reliability: float = 0.95   # Reliability score (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCapability':
        """Create capability from dictionary."""
        return cls(**data)


@dataclass
class AgentProfile:
    """Agent profile for discovery and coordination."""
    
    agent_id: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    endpoint: str               # How to reach this agent
    status: str = "active"      # active, busy, maintenance, offline
    load: float = 0.0          # Current load (0-1)  
    last_heartbeat: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['capabilities'] = [cap.to_dict() for cap in self.capabilities]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentProfile':
        """Create profile from dictionary."""
        # Convert capability dictionaries back to AgentCapability objects
        capabilities = []
        for cap_data in data.get('capabilities', []):
            capabilities.append(AgentCapability.from_dict(cap_data))
        
        data['capabilities'] = capabilities
        return cls(**data)
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability."""
        return any(cap.name == capability_name for cap in self.capabilities)
    
    def get_capability(self, capability_name: str) -> Optional[AgentCapability]:
        """Get a specific capability by name."""
        for cap in self.capabilities:
            if cap.name == capability_name:
                return cap
        return None


# Factory functions for common message types
def create_request_message(
    sender_id: str,
    action: str,
    payload: Dict[str, Any] = None,
    recipient_id: str = None,
    capabilities_required: List[str] = None,
    priority: Priority = Priority.NORMAL,
    requires_response: bool = True,
    timeout: int = 30
) -> A2AMessage:
    """Create a request message."""
    return A2AMessage(
        message_type=MessageType.REQUEST,
        sender_id=sender_id,
        recipient_id=recipient_id,
        action=action,
        payload=payload or {},
        capabilities_required=capabilities_required or [],
        priority=priority,
        requires_response=requires_response,
        timeout=timeout
    )


def create_response_message(
    sender_id: str,
    recipient_id: str,
    correlation_id: str,
    payload: Dict[str, Any] = None,
    success: bool = True,
    error_message: str = None
) -> A2AMessage:
    """Create a response message."""
    response_payload = payload or {}
    if not success and error_message:
        response_payload["error"] = error_message
    response_payload["success"] = success
    
    return A2AMessage(
        message_type=MessageType.RESPONSE,
        sender_id=sender_id,
        recipient_id=recipient_id,
        correlation_id=correlation_id,
        payload=response_payload
    )


def create_broadcast_message(
    sender_id: str,
    action: str,
    payload: Dict[str, Any] = None,
    capabilities_required: List[str] = None,
    priority: Priority = Priority.NORMAL
) -> A2AMessage:
    """Create a broadcast message."""
    return A2AMessage(
        message_type=MessageType.BROADCAST,
        sender_id=sender_id,
        action=action,
        payload=payload or {},
        capabilities_required=capabilities_required or [],
        priority=priority
    )


def create_discovery_message(
    sender_id: str,
    capabilities_required: List[str] = None,
    metadata: Dict[str, Any] = None
) -> A2AMessage:
    """Create an agent discovery message."""
    payload = {"metadata": metadata or {}}
    if capabilities_required:
        payload["capabilities_required"] = capabilities_required
    
    return A2AMessage(
        message_type=MessageType.DISCOVERY,
        sender_id=sender_id,
        action="discover_agents",
        payload=payload,
        capabilities_required=capabilities_required or []
    )


def create_heartbeat_message(
    sender_id: str,
    load: float = 0.0,
    status: str = "active",
    metadata: Dict[str, Any] = None
) -> A2AMessage:
    """Create a heartbeat message."""
    return A2AMessage(
        message_type=MessageType.HEARTBEAT,
        sender_id=sender_id,
        action="heartbeat",
        payload={
            "load": load,
            "status": status,
            "metadata": metadata or {}
        }
    )


# Common capability definitions for reuse
COMMON_CAPABILITIES = {
    "customer_support": AgentCapability(
        name="customer_support",
        description="General customer support and inquiry handling",
        input_schema={
            "type": "object",
            "properties": {
                "inquiry": {"type": "string"},
                "customer_id": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]}
            },
            "required": ["inquiry", "customer_id"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "resolution_status": {"type": "string"},
                "follow_up_required": {"type": "boolean"}
            }
        },
        cost=1.0,
        latency=2.0,
        reliability=0.95
    ),
    
    "technical_support": AgentCapability(
        name="technical_support",
        description="Technical issue diagnosis and resolution",
        input_schema={
            "type": "object",
            "properties": {
                "issue_description": {"type": "string"},
                "error_logs": {"type": "string"},
                "system_info": {"type": "object"},
                "priority": {"type": "string"}
            },
            "required": ["issue_description"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "diagnosis": {"type": "string"},
                "solution_steps": {"type": "array", "items": {"type": "string"}},
                "estimated_time": {"type": "number"},
                "escalation_needed": {"type": "boolean"}
            }
        },
        cost=2.0,
        latency=5.0,
        reliability=0.90
    ),
    
    "notification_service": AgentCapability(
        name="notification_service",
        description="Send notifications via various channels",
        input_schema={
            "type": "object",
            "properties": {
                "recipient": {"type": "string"},
                "message": {"type": "string"},
                "channel": {"type": "string", "enum": ["email", "sms", "push"]},
                "priority": {"type": "string"}
            },
            "required": ["recipient", "message", "channel"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "sent": {"type": "boolean"},
                "delivery_id": {"type": "string"},
                "estimated_delivery": {"type": "string"}
            }
        },
        cost=0.5,
        latency=1.0,
        reliability=0.98
    ),
    
    "data_analysis": AgentCapability(
        name="data_analysis",
        description="Analyze data and provide insights",
        input_schema={
            "type": "object",
            "properties": {
                "dataset": {"type": "object"},
                "analysis_type": {"type": "string"},
                "parameters": {"type": "object"}
            },
            "required": ["dataset", "analysis_type"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "insights": {"type": "array"},
                "charts": {"type": "array"},
                "confidence": {"type": "number"}
            }
        },
        cost=3.0,
        latency=10.0,
        reliability=0.85
    )
}


def get_common_capability(name: str) -> Optional[AgentCapability]:
    """Get a predefined common capability."""
    return COMMON_CAPABILITIES.get(name)


def list_common_capabilities() -> List[str]:
    """List all available common capabilities."""
    return list(COMMON_CAPABILITIES.keys())