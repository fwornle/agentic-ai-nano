"""
A2A Communication Core Components

This package contains the core components for Agent-to-Agent communication:
- Message protocols and formats
- Service discovery and registry
- Message routing and delivery
"""

from .protocol import (
    A2AMessage,
    AgentProfile,
    AgentCapability,
    MessageType,
    Priority,
    create_request_message,
    create_response_message,
    create_broadcast_message,
    create_discovery_message,
    create_heartbeat_message,
    get_common_capability,
    list_common_capabilities
)

from .agent_registry import AgentRegistry, AgentRegistryClient

from .message_router import (
    MessageRouter,
    MessageTransport,
    HTTPMessageTransport,
    InMemoryMessageTransport,
    RoutingRule,
    create_priority_routing_rule,
    create_capability_routing_rule,
    create_action_routing_rule,
    create_sender_routing_rule
)

__all__ = [
    # Protocol components
    "A2AMessage",
    "AgentProfile",
    "AgentCapability", 
    "MessageType",
    "Priority",
    "create_request_message",
    "create_response_message", 
    "create_broadcast_message",
    "create_discovery_message",
    "create_heartbeat_message",
    "get_common_capability",
    "list_common_capabilities",
    
    # Registry components
    "AgentRegistry",
    "AgentRegistryClient",
    
    # Router components
    "MessageRouter",
    "MessageTransport",
    "HTTPMessageTransport", 
    "InMemoryMessageTransport",
    "RoutingRule",
    "create_priority_routing_rule",
    "create_capability_routing_rule",
    "create_action_routing_rule", 
    "create_sender_routing_rule"
]