# Session 7: Agent-to-Agent Communication - Solution Guide

## 🧪 Multiple Choice Quiz - Answer Key

### Quick Check Questions

1. **What is the primary advantage of A2A communication over direct API calls?**
   - A) Better performance
   - B) Dynamic discovery and loose coupling ✅ **CORRECT**
   - C) Simpler implementation
   - D) Lower latency

   **Explanation:** A2A communication enables dynamic agent discovery and loose coupling, allowing agents to find and communicate with each other without hard-coded dependencies, making the system more flexible and scalable.

2. **In orchestration patterns, who controls the workflow execution?**
   - A) Each individual agent
   - B) The first agent in the chain
   - C) A central orchestrator ✅ **CORRECT**
   - D) The user interface

   **Explanation:** In orchestration patterns, a central orchestrator manages the entire workflow, coordinating the sequence of agent interactions and handling dependencies between steps.

3. **What triggers actions in choreography patterns?**
   - A) Direct commands
   - B) Scheduled timers
   - C) Published events ✅ **CORRECT**
   - D) User requests

   **Explanation:** Choreography patterns are event-driven, where agents react to published events and coordinate their actions based on predefined event patterns and conditions.

4. **How does agent discovery work in the A2A system?**
   - A) Fixed configuration files
   - B) Capability-based matching in registry ✅ **CORRECT**
   - C) Random selection
   - D) First-come-first-served

   **Explanation:** Agent discovery uses capability-based matching where agents register their capabilities in a registry, and requesters can find suitable agents by specifying required capabilities.

5. **What is the purpose of message correlation IDs?**
   - A) Security authentication
   - B) Performance optimization
   - C) Linking requests with responses ✅ **CORRECT**
   - D) Message encryption

   **Explanation:** Correlation IDs link related messages together, particularly pairing requests with their corresponding responses in asynchronous communication scenarios.

---

## 💡 Practical Exercise Solution

**Challenge:** Create a multi-agent customer service system with A2A coordination.

### Complete Solution:

```python
# customer_service/choreography.py
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

from a2a.choreography import ChoreographyEngine, EventPattern
from a2a.protocol import A2AMessage, MessageType, Priority

logger = logging.getLogger(__name__)

class CustomerServiceChoreography:
    """Multi-agent customer service system with A2A coordination."""
    
    def __init__(self, choreography_engine: ChoreographyEngine):
        self.engine = choreography_engine
        self.ticket_database = {}  # In production, use real database
        self.escalation_queue = []
        
        self._setup_patterns()
        self._setup_event_handlers()
    
    def _setup_patterns(self):
        """Set up choreography patterns for customer service."""
        
        patterns = [
            # Initial inquiry routing
            EventPattern(
                event_type="customer_inquiry",
                condition="data.get('priority') == 'high' or 'urgent' in data.get('subject', '').lower()",
                action="route_to_priority_agent",
                target_capability="priority_customer_support",
                priority=10
            ),
            EventPattern(
                event_type="customer_inquiry",
                condition="'technical' in data.get('category', '').lower() or 'bug' in data.get('subject', '').lower()",
                action="route_to_technical_support",
                target_capability="technical_support",
                priority=9
            ),
            EventPattern(
                event_type="customer_inquiry",
                condition="'billing' in data.get('category', '').lower() or 'payment' in data.get('subject', '').lower()",
                action="route_to_billing_support",
                target_capability="billing_support",
                priority=8
            ),
            EventPattern(
                event_type="customer_inquiry",
                condition="data.get('customer_tier') == 'premium'",
                action="route_to_premium_support",
                target_capability="premium_customer_support",
                priority=7
            ),
            EventPattern(
                event_type="customer_inquiry",
                condition="true",  # Default catch-all
                action="route_to_general_support",
                target_capability="general_customer_support",
                priority=1
            ),
            
            # Issue analysis and escalation
            EventPattern(
                event_type="issue_analyzed",
                condition="data.get('complexity_score', 0) > 7",
                action="escalate_to_specialist",
                target_capability="specialist_support",
                priority=9
            ),
            EventPattern(
                event_type="issue_analyzed",
                condition="data.get('estimated_resolution_time', 0) > 240",  # > 4 hours
                action="notify_customer_delay",
                target_capability="customer_communication",
                priority=8
            ),
            EventPattern(
                event_type="issue_analyzed",
                condition="'security' in data.get('tags', []) or 'breach' in data.get('description', '').lower()",
                action="trigger_security_protocol",
                target_capability="security_incident_response",
                priority=10
            ),
            
            # Resolution and follow-up
            EventPattern(
                event_type="solution_proposed",
                condition="data.get('confidence_score', 0) > 0.8",
                action="implement_solution",
                target_capability="solution_implementation",
                priority=6
            ),
            EventPattern(
                event_type="solution_proposed",
                condition="data.get('confidence_score', 0) <= 0.8",
                action="request_peer_review",
                target_capability="peer_review",
                priority=5
            ),
            EventPattern(
                event_type="solution_implemented",
                condition="data.get('success') == True",
                action="close_ticket_and_survey",
                target_capability="ticket_management",
                priority=4
            ),
            EventPattern(
                event_type="solution_implemented",
                condition="data.get('success') == False",
                action="escalate_failed_resolution",
                target_capability="escalation_management",
                priority=8
            ),
            
            # Customer feedback and satisfaction
            EventPattern(
                event_type="customer_feedback",
                condition="data.get('satisfaction_score', 0) < 3",  # Out of 5
                action="trigger_recovery_process",
                target_capability="customer_recovery",
                priority=7
            ),
            EventPattern(
                event_type="customer_feedback",
                condition="data.get('satisfaction_score', 0) >= 4",
                action="update_agent_performance",
                target_capability="performance_tracking",
                priority=3
            ),
            
            # Escalation patterns
            EventPattern(
                event_type="escalation_requested",
                condition="data.get('escalation_level') == 'supervisor'",
                action="notify_supervisor",
                target_capability="supervisor_notification",
                priority=8
            ),
            EventPattern(
                event_type="escalation_requested",
                condition="data.get('escalation_level') == 'manager'",
                action="notify_manager",
                target_capability="manager_notification",
                priority=9
            ),
            EventPattern(
                event_type="escalation_timeout",
                condition="data.get('timeout_minutes', 0) > 60",
                action="auto_escalate",
                target_capability="auto_escalation",
                priority=10
            )
        ]
        
        for pattern in patterns:
            self.engine.register_event_pattern(pattern)
        
        logger.info(f"Registered {len(patterns)} customer service choreography patterns")
    
    def _setup_event_handlers(self):
        """Set up event handlers for customer service events."""
        
        self.engine.register_event_handler("ticket_created", self._handle_ticket_created)
        self.engine.register_event_handler("agent_assigned", self._handle_agent_assigned)
        self.engine.register_event_handler("resolution_attempted", self._handle_resolution_attempted)
        self.engine.register_event_handler("escalation_triggered", self._handle_escalation_triggered)
        self.engine.register_event_handler("customer_contacted", self._handle_customer_contacted)
    
    async def handle_customer_inquiry(self, inquiry_data: Dict[str, Any]) -> str:
        """Handle a new customer inquiry and start the choreographed process."""
        
        # Create ticket
        ticket_id = f"ticket_{int(datetime.now().timestamp())}"
        
        ticket = {
            "ticket_id": ticket_id,
            "customer_id": inquiry_data.get("customer_id"),
            "subject": inquiry_data.get("subject"),
            "description": inquiry_data.get("description"),
            "category": inquiry_data.get("category", "general"),
            "priority": inquiry_data.get("priority", "normal"),
            "customer_tier": inquiry_data.get("customer_tier", "standard"),
            "created_at": datetime.now().isoformat(),
            "status": "open",
            "assigned_agent": None,
            "resolution_attempts": [],
            "escalation_history": []
        }
        
        self.ticket_database[ticket_id] = ticket
        
        # Publish customer inquiry event to trigger choreography
        await self.engine.publish_event(
            event_type="customer_inquiry",
            event_data=ticket,
            source_agent="customer_service_system"
        )
        
        logger.info(f"Created ticket {ticket_id} and triggered choreography")
        return ticket_id
    
    async def _handle_ticket_created(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle ticket creation event."""
        
        ticket_data = message.payload.get("event", {}).get("data", {})
        ticket_id = ticket_data.get("ticket_id")
        
        if ticket_id in self.ticket_database:
            # Analyze ticket complexity
            complexity_score = self._analyze_ticket_complexity(ticket_data)
            
            # Update ticket with analysis
            self.ticket_database[ticket_id]["complexity_score"] = complexity_score
            self.ticket_database[ticket_id]["analysis_completed_at"] = datetime.now().isoformat()
            
            # Publish analysis event
            await self.engine.publish_event(
                event_type="issue_analyzed",
                event_data={
                    **ticket_data,
                    "complexity_score": complexity_score,
                    "estimated_resolution_time": complexity_score * 30  # minutes
                },
                source_agent="ticket_analyzer"
            )
        
        return {"status": "ticket_analyzed", "ticket_id": ticket_id}
    
    async def _handle_agent_assigned(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle agent assignment event."""
        
        event_data = message.payload.get("event", {}).get("data", {})
        ticket_id = event_data.get("ticket_id")
        agent_id = event_data.get("assigned_agent")
        
        if ticket_id in self.ticket_database:
            self.ticket_database[ticket_id]["assigned_agent"] = agent_id
            self.ticket_database[ticket_id]["assigned_at"] = datetime.now().isoformat()
            
            # Start resolution timer
            asyncio.create_task(self._start_resolution_timer(ticket_id))
        
        return {"status": "agent_assignment_recorded", "ticket_id": ticket_id}
    
    async def _handle_resolution_attempted(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle resolution attempt event."""
        
        event_data = message.payload.get("event", {}).get("data", {})
        ticket_id = event_data.get("ticket_id")
        resolution_data = event_data.get("resolution")
        
        if ticket_id in self.ticket_database:
            self.ticket_database[ticket_id]["resolution_attempts"].append({
                "attempt_id": len(self.ticket_database[ticket_id]["resolution_attempts"]) + 1,
                "timestamp": datetime.now().isoformat(),
                "resolution": resolution_data,
                "success": event_data.get("success", False)
            })
            
            if event_data.get("success"):
                # Publish solution implemented event
                await self.engine.publish_event(
                    event_type="solution_implemented",
                    event_data={
                        **event_data,
                        "success": True
                    },
                    source_agent="support_agent"
                )
            else:
                # Check if escalation is needed
                attempt_count = len(self.ticket_database[ticket_id]["resolution_attempts"])
                if attempt_count >= 3:
                    await self.engine.publish_event(
                        event_type="escalation_requested",
                        event_data={
                            **event_data,
                            "escalation_level": "supervisor",
                            "reason": "multiple_failed_attempts"
                        },
                        source_agent="auto_escalation_system"
                    )
        
        return {"status": "resolution_attempt_recorded", "ticket_id": ticket_id}
    
    async def _handle_escalation_triggered(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle escalation trigger event."""
        
        event_data = message.payload.get("event", {}).get("data", {})
        ticket_id = event_data.get("ticket_id")
        escalation_level = event_data.get("escalation_level", "supervisor")
        reason = event_data.get("reason", "unspecified")
        
        if ticket_id in self.ticket_database:
            escalation_entry = {
                "escalated_at": datetime.now().isoformat(),
                "level": escalation_level,
                "reason": reason,
                "escalated_by": message.sender_id
            }
            
            self.ticket_database[ticket_id]["escalation_history"].append(escalation_entry)
            self.ticket_database[ticket_id]["status"] = f"escalated_{escalation_level}"
            
            # Add to escalation queue for processing
            self.escalation_queue.append({
                "ticket_id": ticket_id,
                "level": escalation_level,
                "timestamp": datetime.now().isoformat()
            })
        
        return {"status": "escalation_processed", "ticket_id": ticket_id}
    
    async def _handle_customer_contacted(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle customer contact event."""
        
        event_data = message.payload.get("event", {}).get("data", {})
        ticket_id = event_data.get("ticket_id")
        contact_type = event_data.get("contact_type", "email")
        
        if ticket_id in self.ticket_database:
            if "customer_contacts" not in self.ticket_database[ticket_id]:
                self.ticket_database[ticket_id]["customer_contacts"] = []
            
            self.ticket_database[ticket_id]["customer_contacts"].append({
                "timestamp": datetime.now().isoformat(),
                "type": contact_type,
                "content": event_data.get("content"),
                "agent": message.sender_id
            })
        
        return {"status": "customer_contact_logged", "ticket_id": ticket_id}
    
    def _analyze_ticket_complexity(self, ticket_data: Dict[str, Any]) -> int:
        """Analyze ticket complexity and return a score (1-10)."""
        
        score = 1
        description = ticket_data.get("description", "").lower()
        subject = ticket_data.get("subject", "").lower()
        category = ticket_data.get("category", "").lower()
        
        # Keyword-based complexity scoring
        high_complexity_keywords = [
            "integration", "api", "database", "security", "performance",
            "crash", "error", "bug", "system", "network", "server"
        ]
        
        medium_complexity_keywords = [
            "configuration", "setup", "install", "update", "upgrade",
            "account", "access", "permission", "settings"
        ]
        
        # Check for high complexity indicators
        for keyword in high_complexity_keywords:
            if keyword in description or keyword in subject:
                score += 2
        
        # Check for medium complexity indicators
        for keyword in medium_complexity_keywords:
            if keyword in description or keyword in subject:
                score += 1
        
        # Category-based scoring
        if category in ["technical", "billing", "security"]:
            score += 2
        elif category in ["account", "general"]:
            score += 1
        
        # Priority-based scoring
        priority = ticket_data.get("priority", "normal")
        if priority == "urgent":
            score += 3
        elif priority == "high":
            score += 2
        
        # Customer tier affects complexity handling
        if ticket_data.get("customer_tier") == "enterprise":
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    async def _start_resolution_timer(self, ticket_id: str):
        """Start a timer for resolution timeout."""
        
        # Wait for reasonable resolution time based on complexity
        ticket = self.ticket_database.get(ticket_id)
        if not ticket:
            return
        
        complexity = ticket.get("complexity_score", 5)
        timeout_minutes = complexity * 15  # 15 minutes per complexity point
        
        await asyncio.sleep(timeout_minutes * 60)  # Convert to seconds
        
        # Check if ticket is still unresolved
        current_ticket = self.ticket_database.get(ticket_id)
        if current_ticket and current_ticket.get("status") == "open":
            await self.engine.publish_event(
                event_type="escalation_timeout",
                event_data={
                    "ticket_id": ticket_id,
                    "timeout_minutes": timeout_minutes,
                    "complexity_score": complexity
                },
                source_agent="timeout_monitor"
            )
    
    def get_ticket_status(self, ticket_id: str) -> Dict[str, Any]:
        """Get current status of a ticket."""
        
        ticket = self.ticket_database.get(ticket_id)
        if not ticket:
            return {"error": "Ticket not found"}
        
        return {
            "ticket_id": ticket_id,
            "status": ticket.get("status"),
            "assigned_agent": ticket.get("assigned_agent"),
            "complexity_score": ticket.get("complexity_score"),
            "resolution_attempts": len(ticket.get("resolution_attempts", [])),
            "escalation_level": ticket.get("escalation_history", [])[-1].get("level") if ticket.get("escalation_history") else None,
            "created_at": ticket.get("created_at"),
            "last_updated": max(
                ticket.get("assigned_at", ""),
                ticket.get("analysis_completed_at", ""),
                *[attempt.get("timestamp", "") for attempt in ticket.get("resolution_attempts", [])],
                *[esc.get("escalated_at", "") for esc in ticket.get("escalation_history", [])]
            )
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics for monitoring."""
        
        total_tickets = len(self.ticket_database)
        open_tickets = len([t for t in self.ticket_database.values() if t.get("status") == "open"])
        escalated_tickets = len([t for t in self.ticket_database.values() if "escalated" in t.get("status", "")])
        
        # Calculate average resolution time for closed tickets
        closed_tickets = [t for t in self.ticket_database.values() if t.get("status") == "closed"]
        avg_resolution_time = 0
        
        if closed_tickets:
            total_time = 0
            for ticket in closed_tickets:
                created = datetime.fromisoformat(ticket.get("created_at"))
                # Find last resolution attempt
                attempts = ticket.get("resolution_attempts", [])
                if attempts:
                    resolved = datetime.fromisoformat(attempts[-1].get("timestamp"))
                    total_time += (resolved - created).total_seconds() / 60  # minutes
            
            avg_resolution_time = total_time / len(closed_tickets)
        
        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "escalated_tickets": escalated_tickets,
            "escalation_queue_size": len(self.escalation_queue),
            "average_resolution_time_minutes": round(avg_resolution_time, 2),
            "complexity_distribution": self._get_complexity_distribution()
        }
    
    def _get_complexity_distribution(self) -> Dict[str, int]:
        """Get distribution of ticket complexities."""
        
        distribution = {"low": 0, "medium": 0, "high": 0}
        
        for ticket in self.ticket_database.values():
            complexity = ticket.get("complexity_score", 5)
            if complexity <= 3:
                distribution["low"] += 1
            elif complexity <= 7:
                distribution["medium"] += 1
            else:
                distribution["high"] += 1
        
        return distribution

# Usage example and demonstration
async def demo_customer_service():
    """Demonstrate the customer service choreography system."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    # Initialize choreography engine (assuming it's already set up)
    from a2a.choreography import ChoreographyEngine
    from a2a.router import MessageRouter
    from a2a.registry import AgentRegistry
    import redis
    
    # Mock setup
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    registry = AgentRegistry(redis_client)
    router = MessageRouter(registry)
    choreography = ChoreographyEngine(router)
    
    # Create customer service system
    cs_system = CustomerServiceChoreography(choreography)
    
    console.print(Panel.fit(
        "🎧 Customer Service A2A Demo\nMulti-agent coordination for customer support",
        title="Customer Service Choreography",
        border_style="blue"
    ))
    
    # Simulate customer inquiries
    inquiries = [
        {
            "customer_id": "cust_001",
            "subject": "Login API integration issues",
            "description": "Unable to authenticate users through our API integration",
            "category": "technical",
            "priority": "high",
            "customer_tier": "enterprise"
        },
        {
            "customer_id": "cust_002", 
            "subject": "Billing discrepancy",
            "description": "Charged twice for the same subscription",
            "category": "billing",
            "priority": "normal",
            "customer_tier": "standard"
        },
        {
            "customer_id": "cust_003",
            "subject": "Account access issues",
            "description": "Cannot access dashboard after password reset",
            "category": "account",
            "priority": "urgent",
            "customer_tier": "premium"
        }
    ]
    
    ticket_ids = []
    for inquiry in inquiries:
        ticket_id = await cs_system.handle_customer_inquiry(inquiry)
        ticket_ids.append(ticket_id)
        console.print(f"✅ Created ticket: {ticket_id} for {inquiry['subject']}")
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Show ticket statuses
    status_table = Table(title="Ticket Status")
    status_table.add_column("Ticket ID", style="cyan")
    status_table.add_column("Status", style="yellow")
    status_table.add_column("Complexity", style="red")
    status_table.add_column("Assigned Agent", style="green")
    status_table.add_column("Escalation", style="magenta")
    
    for ticket_id in ticket_ids:
        status = cs_system.get_ticket_status(ticket_id)
        status_table.add_row(
            ticket_id,
            status.get("status", "unknown"),
            str(status.get("complexity_score", "N/A")),
            status.get("assigned_agent", "none"),
            status.get("escalation_level", "none")
        )
    
    console.print(status_table)
    
    # Show system metrics
    metrics = cs_system.get_system_metrics()
    metrics_panel = Panel(
        f"Total Tickets: {metrics['total_tickets']}\n"
        f"Open Tickets: {metrics['open_tickets']}\n"
        f"Escalated Tickets: {metrics['escalated_tickets']}\n"
        f"Avg Resolution Time: {metrics['average_resolution_time_minutes']} min\n"
        f"Complexity Distribution: {metrics['complexity_distribution']}",
        title="System Metrics",
        border_style="green"
    )
    console.print(metrics_panel)

if __name__ == "__main__":
    asyncio.run(demo_customer_service())
```

### Key Features Implemented:

1. **Intelligent Routing**: Routes inquiries based on content analysis, priority, and customer tier
2. **Dynamic Escalation**: Automatically escalates based on complexity, failed attempts, and timeouts
3. **Event-Driven Coordination**: Uses choreography patterns for reactive agent coordination
4. **Comprehensive Tracking**: Tracks tickets, resolution attempts, and escalation history
5. **Performance Monitoring**: Provides system metrics and complexity analysis

### Advanced Customer Service Patterns:

```python
# Additional patterns for enhanced customer service

class AdvancedServicePatterns:
    """Advanced patterns for customer service optimization."""
    
    @staticmethod
    def create_sentiment_analysis_patterns() -> List[EventPattern]:
        """Patterns for sentiment-based routing."""
        return [
            EventPattern(
                event_type="customer_message",
                condition="data.get('sentiment_score', 0) < -0.5",  # Very negative
                action="route_to_empathy_specialist",
                target_capability="empathy_specialist",
                priority=9
            ),
            EventPattern(
                event_type="customer_message",
                condition="'angry' in data.get('sentiment_keywords', []) or 'frustrated' in data.get('sentiment_keywords', [])",
                action="apply_de_escalation_protocol",
                target_capability="de_escalation_specialist",
                priority=8
            )
        ]
    
    @staticmethod
    def create_workload_balancing_patterns() -> List[EventPattern]:
        """Patterns for intelligent workload balancing."""
        return [
            EventPattern(
                event_type="agent_overloaded",
                condition="data.get('current_tickets', 0) > data.get('max_capacity', 10)",
                action="redistribute_tickets",
                target_capability="workload_balancer",
                priority=7
            ),
            EventPattern(
                event_type="queue_backlog",
                condition="data.get('queue_size', 0) > 50",
                action="activate_overflow_agents",
                target_capability="agent_scheduler",
                priority=6
            )
        ]
    
    @staticmethod
    def create_knowledge_sharing_patterns() -> List[EventPattern]:
        """Patterns for knowledge sharing and learning."""
        return [
            EventPattern(
                event_type="resolution_successful",
                condition="data.get('was_novel_solution', False) == True",
                action="update_knowledge_base",
                target_capability="knowledge_management",
                priority=4
            ),
            EventPattern(
                event_type="similar_issues_detected",
                condition="data.get('similarity_score', 0) > 0.8",
                action="suggest_previous_solutions",
                target_capability="solution_recommendation",
                priority=5
            )
        ]
```

### Testing Scenarios:

1. **High Priority Technical Issue**: Tests immediate routing to technical specialists
2. **Billing Dispute**: Tests routing to billing team with appropriate escalation
3. **Premium Customer Issue**: Tests priority handling for premium tier customers
4. **Multiple Failed Resolutions**: Tests automatic escalation after failed attempts
5. **Timeout Escalation**: Tests time-based escalation for unresolved issues

This comprehensive customer service system demonstrates the power of A2A choreography for complex, multi-agent coordination scenarios.