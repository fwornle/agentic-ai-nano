"""
Event Choreography Patterns

This module implements event-driven choreography patterns for agent coordination.
It allows agents to coordinate through events rather than direct orchestration,
enabling more flexible and scalable multi-agent workflows.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Callable, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from ..a2a.protocol import A2AMessage, MessageType, Priority, create_broadcast_message
from ..a2a.message_router import MessageRouter
from ..a2a.agent_registry import AgentRegistry

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Common event types for choreography."""
    CUSTOMER_INQUIRY = "customer_inquiry"
    TICKET_CREATED = "ticket_created"
    ISSUE_ANALYZED = "issue_analyzed"
    SOLUTION_PROPOSED = "solution_proposed"
    SOLUTION_IMPLEMENTED = "solution_implemented"
    ESCALATION_REQUESTED = "escalation_requested"
    ESCALATION_TIMEOUT = "escalation_timeout"
    CUSTOMER_FEEDBACK = "customer_feedback"
    AGENT_OVERLOADED = "agent_overloaded"
    SYSTEM_ALERT = "system_alert"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"


@dataclass
class EventPattern:
    """Defines an event pattern that triggers agent actions."""
    pattern_id: str
    event_type: str
    condition: str              # Python expression to evaluate
    action: str                 # Action to perform when pattern matches
    target_capability: str      # Required capability for handling agent
    priority: int = 1           # Pattern priority (higher = more important)
    description: str = ""       # Human-readable description
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventPattern':
        return cls(**data)


@dataclass
class ChoreographyEvent:
    """Represents an event in the choreography system."""
    event_id: str
    event_type: str
    timestamp: str
    source_agent: str = None
    data: Dict[str, Any] = None
    correlation_id: str = None  # Link related events
    ttl: int = 3600  # Time to live in seconds
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChoreographyEvent':
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if event has expired."""
        try:
            event_time = datetime.fromisoformat(self.timestamp)
            return (datetime.now() - event_time).total_seconds() > self.ttl
        except Exception:
            return True


class ChoreographyEngine:
    """Event-driven choreography engine for agent coordination."""
    
    def __init__(self, router: MessageRouter, registry: AgentRegistry = None):
        self.router = router
        self.registry = registry
        
        # Pattern and event management
        self.event_patterns: List[EventPattern] = []
        self.event_handlers: Dict[str, Callable] = {}
        self.event_history: List[ChoreographyEvent] = []
        self.active_workflows: Dict[str, Dict] = {}
        
        # Configuration
        self.max_history = 1000
        self.cleanup_interval = 300  # 5 minutes
        self.pattern_timeout = 30    # seconds
        
        # Statistics
        self.stats = {
            "events_published": 0,
            "events_processed": 0,
            "patterns_triggered": 0,
            "actions_executed": 0,
            "errors": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        # Background tasks
        self._cleanup_task = None
        self._running = False
        
        # Register default message handler
        self.router.register_handler("choreography_event", self._handle_choreography_event)
    
    async def start(self):
        """Start the choreography engine."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Choreography engine started")
    
    async def stop(self):
        """Stop the choreography engine."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Choreography engine stopped")
    
    def register_event_pattern(self, pattern: EventPattern):
        """Register an event pattern for choreography."""
        self.event_patterns.append(pattern)
        # Sort by priority (higher priority first)
        self.event_patterns.sort(key=lambda x: x.priority, reverse=True)
        logger.info(f"Registered event pattern: {pattern.pattern_id} for {pattern.event_type}")
    
    def unregister_event_pattern(self, pattern_id: str) -> bool:
        """Unregister an event pattern."""
        initial_count = len(self.event_patterns)
        self.event_patterns = [p for p in self.event_patterns if p.pattern_id != pattern_id]
        return len(self.event_patterns) < initial_count
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register a handler for specific event types."""
        self.event_handlers[event_type] = handler
        logger.info(f"Registered event handler: {event_type}")
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any], 
                          source_agent: str = None, correlation_id: str = None,
                          ttl: int = 3600) -> str:
        """Publish an event that may trigger choreographed actions."""
        
        event = ChoreographyEvent(
            event_id=f"evt_{int(datetime.now().timestamp() * 1000)}",
            event_type=event_type,
            source_agent=source_agent,
            data=event_data,
            correlation_id=correlation_id,
            ttl=ttl
        )
        
        # Add to event history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        self.stats["events_published"] += 1
        logger.info(f"Published event: {event_type} from {source_agent} (ID: {event.event_id})")
        
        # Process event patterns asynchronously
        asyncio.create_task(self._process_event_patterns(event))
        
        return event.event_id
    
    async def _process_event_patterns(self, event: ChoreographyEvent):
        """Process event against registered patterns."""
        
        try:
            self.stats["events_processed"] += 1
            triggered_patterns = []
            
            for pattern in self.event_patterns:
                if pattern.event_type == event.event_type or pattern.event_type == "*":
                    # Evaluate condition
                    if self._evaluate_condition(pattern.condition, event):
                        triggered_patterns.append(pattern)
                        self.stats["patterns_triggered"] += 1
            
            # Execute triggered actions
            tasks = []
            for pattern in triggered_patterns:
                task = asyncio.create_task(self._execute_choreography_action(pattern, event))
                tasks.append(task)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successful executions
                for result in results:
                    if not isinstance(result, Exception):
                        self.stats["actions_executed"] += 1
                    else:
                        self.stats["errors"] += 1
                        logger.error(f"Error in choreography action: {result}")
            
        except Exception as e:
            logger.error(f"Error processing event patterns: {e}")
            self.stats["errors"] += 1
    
    def _evaluate_condition(self, condition: str, event: ChoreographyEvent) -> bool:
        """Evaluate a condition expression against event data."""
        
        if not condition or condition == "true":
            return True
        
        try:
            # Create evaluation context
            context = {
                "event": event.to_dict(),
                "data": event.data,
                "source": event.source_agent,
                "timestamp": event.timestamp,
                "recent_events": [e.to_dict() for e in self.event_history[-10:]],  # Last 10 events
                "active_workflows": self.active_workflows,
                "stats": self.stats
            }
            
            # Add helper functions
            context.update({
                "len": len,
                "any": any,
                "all": all,
                "str": str,
                "int": int,
                "float": float,
                "datetime": datetime,
                "timedelta": timedelta
            })
            
            # Evaluate condition (be careful with eval in production!)
            result = eval(condition, {"__builtins__": {}}, context)
            return bool(result)
            
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False
    
    async def _execute_choreography_action(self, pattern: EventPattern, event: ChoreographyEvent):
        """Execute a choreography action triggered by an event pattern."""
        
        try:
            # Create action message
            action_message = A2AMessage(
                sender_id="choreography_engine",
                action=pattern.action,
                payload={
                    "trigger_event": event.to_dict(),
                    "pattern": pattern.to_dict(),
                    "choreography_context": {
                        "pattern_id": pattern.pattern_id,
                        "triggered_at": datetime.now().isoformat()
                    }
                },
                capabilities_required=[pattern.target_capability],
                priority=Priority.HIGH if pattern.priority >= 8 else Priority.NORMAL,
                requires_response=False  # Fire and forget for choreography
            )
            
            # Send to appropriate agent(s)
            if self.registry:
                # Find agents with required capability
                agents = await self.registry.discover_agents(
                    required_capabilities=[pattern.target_capability],
                    status_filter="active"
                )
                
                if agents:
                    # Send to the best available agent
                    action_message.recipient_id = agents[0].agent_id
                    await self.router.send_message(action_message)
                    logger.info(f"Executed choreography action: {pattern.action} -> {agents[0].agent_id}")
                else:
                    logger.warning(f"No agents found with capability: {pattern.target_capability}")
            else:
                # Broadcast if no registry available
                await self.router.send_message(action_message)
                logger.info(f"Broadcast choreography action: {pattern.action}")
            
        except Exception as e:
            logger.error(f"Failed to execute choreography action {pattern.action}: {e}")
            raise
    
    async def _handle_choreography_event(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle incoming choreography event messages."""
        
        try:
            event_type = message.payload.get("event_type")
            event_data = message.payload.get("event_data", {})
            source_agent = message.sender_id
            
            if event_type:
                # Publish the event to trigger patterns
                event_id = await self.publish_event(
                    event_type=event_type,
                    event_data=event_data,
                    source_agent=source_agent
                )
                
                # Check if we have a specific handler for this event type
                if event_type in self.event_handlers:
                    handler = self.event_handlers[event_type]
                    result = await handler(message)
                    return {
                        "status": "event_processed",
                        "event_id": event_id,
                        "handler_result": result
                    }
                
                return {
                    "status": "event_published",
                    "event_id": event_id
                }
            else:
                return {"error": "No event_type specified"}
                
        except Exception as e:
            logger.error(f"Error handling choreography event: {e}")
            return {"error": str(e)}
    
    def create_workflow_patterns(self, workflow_id: str, workflow_config: Dict[str, Any]) -> List[EventPattern]:
        """Create event patterns for a specific workflow."""
        
        patterns = []
        
        # Workflow start pattern
        patterns.append(EventPattern(
            pattern_id=f"{workflow_id}_start",
            event_type="workflow_trigger",
            condition=f"data.get('workflow_id') == '{workflow_id}'",
            action="start_workflow",
            target_capability="workflow_orchestrator",
            priority=9,
            description=f"Start workflow {workflow_id}",
            metadata={"workflow_id": workflow_id}
        ))
        
        # Step completion patterns
        steps = workflow_config.get("steps", [])
        for i, step in enumerate(steps):
            step_id = step.get("step_id", f"step_{i}")
            next_steps = step.get("next_steps", [])
            
            for next_step in next_steps:
                patterns.append(EventPattern(
                    pattern_id=f"{workflow_id}_{step_id}_to_{next_step}",
                    event_type="step_completed",
                    condition=f"data.get('workflow_id') == '{workflow_id}' and data.get('step_id') == '{step_id}' and data.get('success') == True",
                    action=f"execute_step_{next_step}",
                    target_capability=step.get("capability", "general_processing"),
                    priority=7,
                    description=f"Execute {next_step} after {step_id} in workflow {workflow_id}",
                    metadata={"workflow_id": workflow_id, "step_sequence": [step_id, next_step]}
                ))
        
        # Error handling patterns
        patterns.append(EventPattern(
            pattern_id=f"{workflow_id}_error_handler",
            event_type="step_failed",
            condition=f"data.get('workflow_id') == '{workflow_id}'",
            action="handle_workflow_error",
            target_capability="error_handling",
            priority=10,
            description=f"Handle errors in workflow {workflow_id}",
            metadata={"workflow_id": workflow_id}
        ))
        
        return patterns
    
    def get_event_history(self, event_type: str = None, source_agent: str = None, 
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history with optional filtering."""
        
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if source_agent:
            events = [e for e in events if e.source_agent == source_agent]
        
        # Return most recent events first
        events = events[-limit:]
        events.reverse()
        
        return [event.to_dict() for event in events]
    
    def get_active_patterns(self) -> List[Dict[str, Any]]:
        """Get list of active event patterns."""
        return [pattern.to_dict() for pattern in self.event_patterns]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get choreography engine statistics."""
        self.stats["last_updated"] = datetime.now().isoformat()
        self.stats["active_patterns"] = len(self.event_patterns)
        self.stats["event_history_size"] = len(self.event_history)
        self.stats["registered_handlers"] = len(self.event_handlers)
        return self.stats.copy()
    
    async def _periodic_cleanup(self):
        """Periodically clean up expired events and statistics."""
        while self._running:
            try:
                # Clean up expired events
                current_time = datetime.now()
                initial_count = len(self.event_history)
                
                self.event_history = [
                    event for event in self.event_history
                    if not event.is_expired()
                ]
                
                cleaned_count = initial_count - len(self.event_history)
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} expired events")
                
                # Clean up old workflow data
                expired_workflows = []
                for workflow_id, workflow_data in self.active_workflows.items():
                    started_at = workflow_data.get("started_at")
                    if started_at:
                        try:
                            start_time = datetime.fromisoformat(started_at)
                            if (current_time - start_time).total_seconds() > 3600:  # 1 hour
                                expired_workflows.append(workflow_id)
                        except Exception:
                            expired_workflows.append(workflow_id)
                
                for workflow_id in expired_workflows:
                    del self.active_workflows[workflow_id]
                    logger.info(f"Cleaned up expired workflow: {workflow_id}")
                
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in choreography cleanup: {e}")
                await asyncio.sleep(self.cleanup_interval)


# Predefined choreography patterns for common scenarios
class CustomerServiceChoreography:
    """Predefined patterns for customer service scenarios."""
    
    @staticmethod
    def create_patterns() -> List[EventPattern]:
        """Create customer service choreography patterns."""
        
        return [
            # Initial inquiry routing
            EventPattern(
                pattern_id="cs_priority_routing",
                event_type="customer_inquiry",
                condition="data.get('priority') == 'urgent' or 'urgent' in data.get('subject', '').lower()",
                action="route_to_priority_agent",
                target_capability="priority_customer_support",
                priority=10,
                description="Route urgent inquiries to priority support"
            ),
            EventPattern(
                pattern_id="cs_technical_routing",
                event_type="customer_inquiry",
                condition="'technical' in data.get('category', '').lower() or 'bug' in data.get('subject', '').lower()",
                action="route_to_technical_support",
                target_capability="technical_support",
                priority=9,
                description="Route technical issues to technical support"
            ),
            EventPattern(
                pattern_id="cs_billing_routing",
                event_type="customer_inquiry",
                condition="'billing' in data.get('category', '').lower() or 'payment' in data.get('subject', '').lower()",
                action="route_to_billing_support",
                target_capability="billing_support",
                priority=8,
                description="Route billing issues to billing support"
            ),
            
            # Issue analysis and escalation
            EventPattern(
                pattern_id="cs_complexity_escalation",
                event_type="issue_analyzed",
                condition="data.get('complexity_score', 0) > 7",
                action="escalate_to_specialist",
                target_capability="specialist_support",
                priority=9,
                description="Escalate high complexity issues to specialists"
            ),
            EventPattern(
                pattern_id="cs_delay_notification",
                event_type="issue_analyzed",
                condition="data.get('estimated_resolution_time', 0) > 240",  # > 4 hours
                action="notify_customer_delay",
                target_capability="customer_communication",
                priority=8,
                description="Notify customer of expected delays"
            ),
            
            # Resolution and follow-up
            EventPattern(
                pattern_id="cs_solution_implementation",
                event_type="solution_proposed",
                condition="data.get('confidence_score', 0) > 0.8",
                action="implement_solution",
                target_capability="solution_implementation",
                priority=6,
                description="Implement high-confidence solutions"
            ),
            EventPattern(
                pattern_id="cs_peer_review",
                event_type="solution_proposed",
                condition="data.get('confidence_score', 0) <= 0.8",
                action="request_peer_review",
                target_capability="peer_review",
                priority=5,
                description="Request peer review for uncertain solutions"
            ),
            
            # Customer feedback handling
            EventPattern(
                pattern_id="cs_feedback_recovery",
                event_type="customer_feedback",
                condition="data.get('satisfaction_score', 0) < 3",  # Out of 5
                action="trigger_recovery_process",
                target_capability="customer_recovery",
                priority=7,
                description="Trigger recovery for unsatisfied customers"
            ),
            
            # System monitoring
            EventPattern(
                pattern_id="cs_agent_overload",
                event_type="agent_overloaded",
                condition="data.get('current_load', 0) > 0.9",
                action="redistribute_workload",
                target_capability="workload_manager",
                priority=8,
                description="Redistribute work when agents are overloaded"
            )
        ]


class TechnicalSupportChoreography:
    """Predefined patterns for technical support scenarios."""
    
    @staticmethod
    def create_patterns() -> List[EventPattern]:
        """Create technical support choreography patterns."""
        
        return [
            # Issue categorization and routing
            EventPattern(
                pattern_id="tech_security_alert",
                event_type="technical_issue",
                condition="'security' in data.get('category', '').lower() or 'breach' in data.get('description', '').lower()",
                action="trigger_security_protocol",
                target_capability="security_incident_response",
                priority=10,
                description="Trigger security protocols for security-related issues"
            ),
            EventPattern(
                pattern_id="tech_critical_escalation",
                event_type="technical_issue",
                condition="data.get('severity') == 'critical'",
                action="immediate_escalation",
                target_capability="senior_technical_support",
                priority=10,
                description="Immediately escalate critical technical issues"
            ),
            
            # Diagnostic workflow
            EventPattern(
                pattern_id="tech_diagnostic_start",
                event_type="issue_assigned",
                condition="data.get('category') in ['api', 'database', 'network']",
                action="start_diagnostic_workflow",
                target_capability="diagnostic_specialist",
                priority=7,
                description="Start diagnostic workflow for complex technical issues"
            ),
            
            # Solution validation
            EventPattern(
                pattern_id="tech_solution_testing",
                event_type="solution_implemented",
                condition="data.get('requires_testing', False) == True",
                action="validate_solution",
                target_capability="solution_validation",
                priority=6,
                description="Validate solutions that require testing"
            ),
            
            # Knowledge sharing
            EventPattern(
                pattern_id="tech_knowledge_update",
                event_type="issue_resolved",
                condition="data.get('novel_solution', False) == True",
                action="update_knowledge_base",
                target_capability="knowledge_management",
                priority=4,
                description="Update knowledge base with novel solutions"
            )
        ]


# Factory functions for common choreography setups
def create_customer_service_choreography(router: MessageRouter, registry: AgentRegistry = None) -> ChoreographyEngine:
    """Create a choreography engine configured for customer service."""
    
    engine = ChoreographyEngine(router, registry)
    
    # Register customer service patterns
    for pattern in CustomerServiceChoreography.create_patterns():
        engine.register_event_pattern(pattern)
    
    return engine


def create_technical_support_choreography(router: MessageRouter, registry: AgentRegistry = None) -> ChoreographyEngine:
    """Create a choreography engine configured for technical support."""
    
    engine = ChoreographyEngine(router, registry)
    
    # Register technical support patterns
    for pattern in TechnicalSupportChoreography.create_patterns():
        engine.register_event_pattern(pattern)
    
    return engine


def create_hybrid_choreography(router: MessageRouter, registry: AgentRegistry = None) -> ChoreographyEngine:
    """Create a choreography engine with both customer service and technical support patterns."""
    
    engine = ChoreographyEngine(router, registry)
    
    # Register all patterns
    for pattern in CustomerServiceChoreography.create_patterns():
        engine.register_event_pattern(pattern)
    
    for pattern in TechnicalSupportChoreography.create_patterns():
        engine.register_event_pattern(pattern)
    
    return engine