"""
Coordination Patterns

This package contains coordination patterns and choreography engines
for orchestrating complex multi-agent workflows.
"""

from .choreography import (
    ChoreographyEngine,
    EventPattern,
    ChoreographyEvent,
    EventType,
    CustomerServiceChoreography,
    TechnicalSupportChoreography,
    create_customer_service_choreography,
    create_technical_support_choreography,
    create_hybrid_choreography
)

__all__ = [
    # Core choreography
    "ChoreographyEngine",
    "EventPattern",
    "ChoreographyEvent",
    "EventType",
    
    # Predefined patterns
    "CustomerServiceChoreography",
    "TechnicalSupportChoreography",
    
    # Factory functions
    "create_customer_service_choreography",
    "create_technical_support_choreography",
    "create_hybrid_choreography"
]