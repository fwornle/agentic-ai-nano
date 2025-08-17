"""
Session 7: Agent-to-Agent Communication (A2A)

This package provides a comprehensive A2A communication system for coordinating
multiple agents using standardized protocols, service discovery, and event-driven
choreography patterns.

Key Components:
- A2A Protocol: Standardized message formats and agent profiles
- Agent Registry: Service discovery and health monitoring
- Message Router: Reliable message delivery and routing
- Agent Implementations: Customer service and technical support agents
- Choreography Engine: Event-driven coordination patterns
- Configuration: Centralized system configuration

Example Usage:
    from session7.a2a.protocol import A2AMessage, AgentProfile
    from session7.a2a.agent_registry import AgentRegistry
    from session7.a2a.message_router import MessageRouter
    from session7.agents.customer_service import CustomerServiceAgent
    from session7.coordination.choreography import ChoreographyEngine
    
    # Create A2A system components
    registry = AgentRegistry()
    router = MessageRouter(registry)
    choreography = ChoreographyEngine(router, registry)
    
    # Create and start agents
    cs_agent = CustomerServiceAgent("cs_001")
    await cs_agent.start(registry, router)
"""

__version__ = "1.0.0"
__author__ = "A2A Communication Team"

# Import key classes for easy access
from .a2a.protocol import (
    A2AMessage,
    AgentProfile,
    AgentCapability,
    MessageType,
    Priority,
    create_request_message,
    create_response_message,
    create_broadcast_message
)

from .a2a.agent_registry import AgentRegistry, AgentRegistryClient
from .a2a.message_router import MessageRouter, HTTPMessageTransport, InMemoryMessageTransport
from .agents.customer_service import CustomerServiceAgent, CustomerTicket
from .agents.technical_support import TechnicalSupportAgent, TechnicalIssue
from .coordination.choreography import ChoreographyEngine, EventPattern, ChoreographyEvent
from .config import A2ASystemConfig, ConfigurationManager, get_config

__all__ = [
    # Core protocol
    "A2AMessage",
    "AgentProfile", 
    "AgentCapability",
    "MessageType",
    "Priority",
    "create_request_message",
    "create_response_message",
    "create_broadcast_message",
    
    # Registry and routing
    "AgentRegistry",
    "AgentRegistryClient",
    "MessageRouter",
    "HTTPMessageTransport",
    "InMemoryMessageTransport",
    
    # Agent implementations
    "CustomerServiceAgent",
    "CustomerTicket",
    "TechnicalSupportAgent", 
    "TechnicalIssue",
    
    # Choreography
    "ChoreographyEngine",
    "EventPattern",
    "ChoreographyEvent",
    
    # Configuration
    "A2ASystemConfig",
    "ConfigurationManager",
    "get_config"
]