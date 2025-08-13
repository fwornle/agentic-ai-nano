"""
Agent Implementations

This package contains concrete agent implementations that demonstrate
A2A communication patterns for real-world scenarios.
"""

from .customer_service import (
    CustomerServiceAgent,
    CustomerTicket,
    create_customer_service_agent
)

from .technical_support import (
    TechnicalSupportAgent,
    TechnicalIssue,
    IssueSeverity,
    IssueCategory,
    create_technical_support_agent
)

__all__ = [
    # Customer service agent
    "CustomerServiceAgent",
    "CustomerTicket",
    "create_customer_service_agent",
    
    # Technical support agent
    "TechnicalSupportAgent",
    "TechnicalIssue",
    "IssueSeverity",
    "IssueCategory", 
    "create_technical_support_agent"
]