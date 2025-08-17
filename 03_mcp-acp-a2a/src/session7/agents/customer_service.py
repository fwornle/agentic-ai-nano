"""
Customer Service Agent Implementation

This module implements a customer service agent that can handle various
customer inquiries, route issues to appropriate specialists, and coordinate
with other agents using A2A communication.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from ..a2a.protocol import (
    A2AMessage, AgentProfile, AgentCapability, 
    create_request_message, create_response_message,
    Priority, MessageType
)
from ..a2a.agent_registry import AgentRegistry, AgentRegistryClient
from ..a2a.message_router import MessageRouter

logger = logging.getLogger(__name__)


@dataclass
class CustomerTicket:
    """Represents a customer support ticket."""
    ticket_id: str
    customer_id: str
    subject: str
    description: str
    category: str = "general"
    priority: str = "normal"
    status: str = "open"
    assigned_agent: str = None
    created_at: str = None
    updated_at: str = None
    resolution: str = None
    satisfaction_score: float = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "customer_id": self.customer_id,
            "subject": self.subject,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolution": self.resolution,
            "satisfaction_score": self.satisfaction_score,
            "metadata": self.metadata
        }


class CustomerServiceAgent:
    """Customer service agent with A2A communication capabilities."""
    
    def __init__(self, agent_id: str, name: str = None, endpoint: str = None):
        self.agent_id = agent_id
        self.name = name or f"Customer Service Agent {agent_id}"
        self.endpoint = endpoint or f"http://localhost:8000/agents/{agent_id}"
        
        # Agent state
        self.tickets: Dict[str, CustomerTicket] = {}
        self.customer_profiles: Dict[str, Dict] = {}
        self.knowledge_base: Dict[str, str] = {}
        self.is_running = False
        
        # Performance metrics
        self.metrics = {
            "tickets_handled": 0,
            "tickets_resolved": 0,
            "tickets_escalated": 0,
            "average_resolution_time": 0.0,
            "customer_satisfaction": 0.0,
            "last_updated": datetime.now().isoformat()
        }
        
        # A2A components (will be injected)
        self.registry: Optional[AgentRegistry] = None
        self.registry_client: Optional[AgentRegistryClient] = None
        self.router: Optional[MessageRouter] = None
        
        # Initialize capabilities and profile
        self._setup_capabilities()
        self._setup_knowledge_base()
    
    def _setup_capabilities(self):
        """Setup agent capabilities."""
        capabilities = [
            AgentCapability(
                name="customer_inquiry_handling",
                description="Handle general customer inquiries and questions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "inquiry": {"type": "string"},
                        "customer_id": {"type": "string"},
                        "priority": {"type": "string"},
                        "category": {"type": "string"}
                    },
                    "required": ["inquiry", "customer_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "response": {"type": "string"},
                        "ticket_created": {"type": "boolean"},
                        "ticket_id": {"type": "string"},
                        "escalation_needed": {"type": "boolean"}
                    }
                },
                cost=1.0,
                latency=2.0,
                reliability=0.95
            ),
            AgentCapability(
                name="ticket_management",
                description="Create, update, and manage customer tickets",
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["create", "update", "close", "escalate"]},
                        "ticket_data": {"type": "object"}
                    },
                    "required": ["action"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "ticket_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                },
                cost=0.5,
                latency=1.0,
                reliability=0.98
            ),
            AgentCapability(
                name="customer_communication",
                description="Communicate with customers via various channels",
                input_schema={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"},
                        "message": {"type": "string"},
                        "channel": {"type": "string"},
                        "urgency": {"type": "string"}
                    },
                    "required": ["customer_id", "message"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "sent": {"type": "boolean"},
                        "delivery_status": {"type": "string"},
                        "response_expected": {"type": "boolean"}
                    }
                },
                cost=0.8,
                latency=1.5,
                reliability=0.96
            )
        ]
        
        self.agent_profile = AgentProfile(
            agent_id=self.agent_id,
            name=self.name,
            description="Customer service agent specializing in inquiry handling and ticket management",
            capabilities=capabilities,
            endpoint=self.endpoint,
            status="active",
            load=0.0
        )
    
    def _setup_knowledge_base(self):
        """Setup basic knowledge base for common inquiries."""
        self.knowledge_base = {
            "account_login": "To reset your account login, please visit our password reset page or contact technical support if you continue experiencing issues.",
            "billing_question": "For billing inquiries, please provide your account number and describe the specific issue. Our billing team can help resolve payment and subscription questions.",
            "technical_issue": "For technical issues, please provide detailed steps to reproduce the problem and any error messages. Our technical support team will investigate.",
            "feature_request": "Thank you for your feature suggestion! We've recorded your request and our product team will consider it for future releases.",
            "refund_request": "Refund requests are processed according to our refund policy. Please provide your order number and reason for the refund request.",
            "account_cancellation": "We're sorry to see you go! Please let us know the reason for cancellation and we'll help process your request."
        }
    
    async def start(self, registry: AgentRegistry, router: MessageRouter):
        """Start the customer service agent."""
        if self.is_running:
            return
        
        self.registry = registry
        self.router = router
        
        # Create registry client
        self.registry_client = AgentRegistryClient(registry, self.agent_profile)
        await self.registry_client.start()
        
        # Register message handlers
        self._register_message_handlers()
        
        self.is_running = True
        logger.info(f"Customer service agent {self.agent_id} started")
    
    async def stop(self):
        """Stop the customer service agent."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.registry_client:
            await self.registry_client.stop()
        
        logger.info(f"Customer service agent {self.agent_id} stopped")
    
    def _register_message_handlers(self):
        """Register message handlers with the router."""
        self.router.register_handler("handle_inquiry", self._handle_inquiry)
        self.router.register_handler("create_ticket", self._handle_create_ticket)
        self.router.register_handler("update_ticket", self._handle_update_ticket)
        self.router.register_handler("close_ticket", self._handle_close_ticket)
        self.router.register_handler("escalate_ticket", self._handle_escalate_ticket)
        self.router.register_handler("get_ticket_status", self._handle_get_ticket_status)
        self.router.register_handler("send_customer_message", self._handle_send_customer_message)
    
    async def _handle_inquiry(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle a customer inquiry."""
        try:
            payload = message.payload
            inquiry = payload.get("inquiry", "")
            customer_id = payload.get("customer_id", "")
            priority = payload.get("priority", "normal")
            category = payload.get("category", "general")
            
            # Analyze inquiry and determine response
            response, needs_escalation, escalation_type = self._analyze_inquiry(inquiry, category)
            
            # Create ticket for tracking
            ticket = CustomerTicket(
                ticket_id=f"CS-{int(datetime.now().timestamp())}",
                customer_id=customer_id,
                subject=inquiry[:50] + "..." if len(inquiry) > 50 else inquiry,
                description=inquiry,
                category=category,
                priority=priority,
                assigned_agent=self.agent_id
            )
            
            self.tickets[ticket.ticket_id] = ticket
            self.metrics["tickets_handled"] += 1
            
            # Update agent load
            await self._update_load()
            
            # If escalation is needed, route to appropriate specialist
            if needs_escalation:
                await self._escalate_ticket(ticket, escalation_type)
                self.metrics["tickets_escalated"] += 1
            
            return {
                "response": response,
                "ticket_created": True,
                "ticket_id": ticket.ticket_id,
                "escalation_needed": needs_escalation,
                "escalation_type": escalation_type if needs_escalation else None
            }
            
        except Exception as e:
            logger.error(f"Error handling inquiry: {e}")
            return {
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your inquiry. Please try again or contact support.",
                "ticket_created": False
            }
    
    async def _handle_create_ticket(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle ticket creation request."""
        try:
            ticket_data = message.payload.get("ticket_data", {})
            
            ticket = CustomerTicket(
                ticket_id=f"CS-{int(datetime.now().timestamp())}",
                customer_id=ticket_data.get("customer_id", "unknown"),
                subject=ticket_data.get("subject", "No subject"),
                description=ticket_data.get("description", ""),
                category=ticket_data.get("category", "general"),
                priority=ticket_data.get("priority", "normal"),
                assigned_agent=self.agent_id
            )
            
            self.tickets[ticket.ticket_id] = ticket
            self.metrics["tickets_handled"] += 1
            
            await self._update_load()
            
            return {
                "success": True,
                "ticket_id": ticket.ticket_id,
                "status": ticket.status
            }
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_update_ticket(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle ticket update request."""
        try:
            ticket_id = message.payload.get("ticket_id")
            updates = message.payload.get("updates", {})
            
            if ticket_id not in self.tickets:
                return {
                    "success": False,
                    "error": "Ticket not found"
                }
            
            ticket = self.tickets[ticket_id]
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(ticket, field):
                    setattr(ticket, field, value)
            
            ticket.updated_at = datetime.now().isoformat()
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "status": ticket.status
            }
            
        except Exception as e:
            logger.error(f"Error updating ticket: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_close_ticket(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle ticket closure request."""
        try:
            ticket_id = message.payload.get("ticket_id")
            resolution = message.payload.get("resolution", "")
            satisfaction_score = message.payload.get("satisfaction_score")
            
            if ticket_id not in self.tickets:
                return {
                    "success": False,
                    "error": "Ticket not found"
                }
            
            ticket = self.tickets[ticket_id]
            ticket.status = "closed"
            ticket.resolution = resolution
            ticket.updated_at = datetime.now().isoformat()
            
            if satisfaction_score is not None:
                ticket.satisfaction_score = satisfaction_score
                self._update_satisfaction_metrics(satisfaction_score)
            
            self.metrics["tickets_resolved"] += 1
            
            # Update resolution time metrics
            self._update_resolution_time_metrics(ticket)
            
            await self._update_load()
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "status": "closed"
            }
            
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_escalate_ticket(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle ticket escalation request."""
        try:
            ticket_id = message.payload.get("ticket_id")
            escalation_type = message.payload.get("escalation_type", "technical_support")
            reason = message.payload.get("reason", "")
            
            if ticket_id not in self.tickets:
                return {
                    "success": False,
                    "error": "Ticket not found"
                }
            
            ticket = self.tickets[ticket_id]
            result = await self._escalate_ticket(ticket, escalation_type, reason)
            
            return {
                "success": result,
                "ticket_id": ticket_id,
                "escalated_to": escalation_type
            }
            
        except Exception as e:
            logger.error(f"Error escalating ticket: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_get_ticket_status(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle ticket status request."""
        try:
            ticket_id = message.payload.get("ticket_id")
            
            if ticket_id not in self.tickets:
                return {
                    "success": False,
                    "error": "Ticket not found"
                }
            
            ticket = self.tickets[ticket_id]
            
            return {
                "success": True,
                "ticket": ticket.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting ticket status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_send_customer_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle customer message sending request."""
        try:
            customer_id = message.payload.get("customer_id")
            message_text = message.payload.get("message")
            channel = message.payload.get("channel", "email")
            
            # In a real implementation, this would integrate with notification services
            # For now, we'll simulate the message sending
            
            logger.info(f"Sending message to customer {customer_id} via {channel}: {message_text}")
            
            return {
                "sent": True,
                "delivery_status": "queued",
                "response_expected": False
            }
            
        except Exception as e:
            logger.error(f"Error sending customer message: {e}")
            return {
                "sent": False,
                "error": str(e)
            }
    
    def _analyze_inquiry(self, inquiry: str, category: str) -> tuple[str, bool, str]:
        """Analyze customer inquiry and determine response and escalation needs."""
        inquiry_lower = inquiry.lower()
        
        # Check for keywords that indicate specific issues
        if any(keyword in inquiry_lower for keyword in ["password", "login", "access", "signin"]):
            response = self.knowledge_base.get("account_login", "Let me help you with your account access issue.")
            if "urgent" in inquiry_lower or "can't access" in inquiry_lower:
                return response, True, "technical_support"
            return response, False, None
        
        elif any(keyword in inquiry_lower for keyword in ["bill", "charge", "payment", "invoice"]):
            response = self.knowledge_base.get("billing_question", "Let me help you with your billing inquiry.")
            return response, False, None
        
        elif any(keyword in inquiry_lower for keyword in ["bug", "error", "broken", "not working"]):
            response = self.knowledge_base.get("technical_issue", "I'll help you with this technical issue.")
            return response, True, "technical_support"
        
        elif any(keyword in inquiry_lower for keyword in ["feature", "suggestion", "improvement"]):
            response = self.knowledge_base.get("feature_request", "Thank you for your feature suggestion!")
            return response, False, None
        
        elif any(keyword in inquiry_lower for keyword in ["refund", "money back", "return"]):
            response = self.knowledge_base.get("refund_request", "I can help you with your refund request.")
            return response, True, "billing_support"
        
        elif any(keyword in inquiry_lower for keyword in ["cancel", "close account", "delete"]):
            response = self.knowledge_base.get("account_cancellation", "I can help you with account cancellation.")
            return response, True, "retention_specialist"
        
        else:
            # General inquiry
            response = "Thank you for contacting us. I've received your inquiry and will help you resolve this issue."
            # Escalate if the inquiry is complex or lengthy
            if len(inquiry) > 200 or "urgent" in inquiry_lower:
                return response, True, "general_support"
            return response, False, None
    
    async def _escalate_ticket(self, ticket: CustomerTicket, escalation_type: str, reason: str = "") -> bool:
        """Escalate a ticket to appropriate specialist."""
        try:
            # Find agents with required capability
            agents = await self.registry.discover_agents(
                required_capabilities=[escalation_type],
                status_filter="active"
            )
            
            if not agents:
                logger.warning(f"No agents found with capability {escalation_type}")
                return False
            
            # Send escalation message to the best available agent
            target_agent = agents[0]  # Lowest load agent
            
            escalation_message = create_request_message(
                sender_id=self.agent_id,
                action="handle_escalated_ticket",
                payload={
                    "ticket": ticket.to_dict(),
                    "escalation_type": escalation_type,
                    "escalation_reason": reason,
                    "original_agent": self.agent_id
                },
                recipient_id=target_agent.agent_id,
                priority=Priority.HIGH,
                requires_response=True
            )
            
            response = await self.router.send_message(escalation_message)
            
            if response and response.payload.get("accepted", False):
                # Update ticket status
                ticket.status = "escalated"
                ticket.assigned_agent = target_agent.agent_id
                ticket.updated_at = datetime.now().isoformat()
                ticket.metadata["escalation_history"] = ticket.metadata.get("escalation_history", [])
                ticket.metadata["escalation_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "from_agent": self.agent_id,
                    "to_agent": target_agent.agent_id,
                    "type": escalation_type,
                    "reason": reason
                })
                
                logger.info(f"Escalated ticket {ticket.ticket_id} to {target_agent.agent_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error escalating ticket: {e}")
            return False
    
    async def _update_load(self):
        """Update agent load based on current tickets."""
        open_tickets = sum(1 for ticket in self.tickets.values() if ticket.status == "open")
        max_capacity = 20  # Maximum tickets this agent can handle
        
        load = min(open_tickets / max_capacity, 1.0)
        
        if self.registry_client:
            await self.registry_client.update_status(
                load=load,
                status="busy" if load > 0.8 else "active"
            )
    
    def _update_satisfaction_metrics(self, satisfaction_score: float):
        """Update customer satisfaction metrics."""
        if self.metrics["customer_satisfaction"] == 0.0:
            self.metrics["customer_satisfaction"] = satisfaction_score
        else:
            # Running average
            current_avg = self.metrics["customer_satisfaction"]
            resolved_count = self.metrics["tickets_resolved"]
            self.metrics["customer_satisfaction"] = (
                (current_avg * (resolved_count - 1) + satisfaction_score) / resolved_count
            )
    
    def _update_resolution_time_metrics(self, ticket: CustomerTicket):
        """Update average resolution time metrics."""
        try:
            created = datetime.fromisoformat(ticket.created_at)
            updated = datetime.fromisoformat(ticket.updated_at)
            resolution_time = (updated - created).total_seconds() / 60  # minutes
            
            if self.metrics["average_resolution_time"] == 0.0:
                self.metrics["average_resolution_time"] = resolution_time
            else:
                # Running average
                current_avg = self.metrics["average_resolution_time"]
                resolved_count = self.metrics["tickets_resolved"]
                self.metrics["average_resolution_time"] = (
                    (current_avg * (resolved_count - 1) + resolution_time) / resolved_count
                )
        
        except Exception as e:
            logger.error(f"Error updating resolution time metrics: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        self.metrics["last_updated"] = datetime.now().isoformat()
        self.metrics["current_tickets"] = len([t for t in self.tickets.values() if t.status == "open"])
        return self.metrics.copy()
    
    def get_tickets(self, status: str = None) -> List[Dict[str, Any]]:
        """Get tickets, optionally filtered by status."""
        tickets = list(self.tickets.values())
        
        if status:
            tickets = [t for t in tickets if t.status == status]
        
        return [ticket.to_dict() for ticket in tickets]


# Factory function for easy agent creation
def create_customer_service_agent(
    agent_id: str,
    name: str = None,
    endpoint: str = None,
    knowledge_base: Dict[str, str] = None
) -> CustomerServiceAgent:
    """Create a customer service agent with optional customizations."""
    
    agent = CustomerServiceAgent(agent_id, name, endpoint)
    
    if knowledge_base:
        agent.knowledge_base.update(knowledge_base)
    
    return agent