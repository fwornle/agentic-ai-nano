# Session 7: Agent to Agent Communication - Test Solutions

## 📝 Multiple Choice Test

### Question 1: A2A Communication Purpose
**What is the primary purpose of Agent-to-Agent (A2A) communication?**  

A) To reduce computational costs  
B) To improve individual agent performance  
C) To enable multiple agents to collaborate and coordinate actions ✅  
D) To replace human operators  
**Correct Answer: C) To enable multiple agents to collaborate and coordinate actions**

**Explanation:** A2A communication enables multiple AI agents to collaborate, share information, and coordinate actions to solve complex problems requiring diverse expertise and coordination.

---

### Question 2: Message Types
**Which message type is used for finding agents with specific capabilities?**  

A) RESPONSE  
B) HEARTBEAT  
C) DISCOVERY ✅  
D) REQUEST  
**Correct Answer: C) DISCOVERY**

**Explanation:** DISCOVERY messages are specifically designed for agent discovery requests, allowing agents to find other agents with required capabilities in the network.

---

### Question 3: Message Routing
**What information is essential for proper A2A message routing?**  

A) Just the timestamp  
B) Only the priority level  
C) Only the message content  
D) Sender ID, recipient ID, and message type ✅  
**Correct Answer: D) Sender ID, recipient ID, and message type**

**Explanation:** Proper message routing requires sender identification, recipient targeting, and message type classification to ensure messages reach the correct destination with appropriate handling.

---

### Question 4: Coordination Patterns
**What is the difference between orchestration and choreography in multi-agent systems?**  

A) Orchestration uses centralized control, choreography uses distributed coordination ✅  
B) Choreography requires more memory  
C) There is no difference  
D) Orchestration is faster than choreography  
**Correct Answer: A) Orchestration uses centralized control, choreography uses distributed coordination**

**Explanation:** Orchestration involves centralized control where a coordinator directs workflow execution, while choreography involves distributed coordination where agents follow predefined interaction patterns.

---

### Question 5: Service Discovery
**How do agents announce their capabilities in an A2A system?**  

A) Using ANNOUNCEMENT messages with capability metadata ✅  
B) Through manual configuration  
C) Via external databases only  
D) Through file-based configurations  
**Correct Answer: A) Using ANNOUNCEMENT messages with capability metadata**

**Explanation:** Agents use ANNOUNCEMENT messages containing detailed capability metadata to inform other agents about their available services and expertise areas.

---

### Question 6: Fault Tolerance
**What mechanism ensures A2A communication reliability when agents become unavailable?**  

A) Faster processing  
B) Increased memory allocation  
C) Message queuing with retry logic and timeouts ✅  
D) Multiple network interfaces  
**Correct Answer: C) Message queuing with retry logic and timeouts**

**Explanation:** Message queuing with retry logic and timeout mechanisms ensures communication reliability by handling temporary agent unavailability and network issues.

---

### Question 7: Capability Negotiation
**What is the purpose of capability negotiation in A2A systems?**  

A) To improve performance  
B) To match agent capabilities with task requirements ✅  
C) To simplify configuration  
D) To reduce costs  
**Correct Answer: B) To match agent capabilities with task requirements**

**Explanation:** Capability negotiation matches available agent capabilities with specific task requirements, ensuring that tasks are assigned to agents with appropriate skills and resources.

---

### Question 8: Message Priority
**When should URGENT priority be used for A2A messages?**  

A) For time-critical operations requiring immediate attention ✅  
B) For data backup operations  
C) For routine status updates  
D) For all important messages  
**Correct Answer: A) For time-critical operations requiring immediate attention**

**Explanation:** URGENT priority should be reserved for time-critical operations that require immediate attention, such as emergency shutdowns or critical error conditions.

---

### Question 9: Correlation ID
**What is the purpose of correlation IDs in A2A messaging?**  

A) To validate message integrity  
B) To encrypt messages  
C) To compress message content  
D) To link related messages in multi-step workflows ✅  
**Correct Answer: D) To link related messages in multi-step workflows**

**Explanation:** Correlation IDs link related messages across multi-step workflows, enabling proper tracking and coordination of complex interactions between agents.

---

### Question 10: Distributed Teams
**What is a key benefit of collaborative agent teams in A2A systems?**  

A) Diverse expertise and parallel problem-solving capabilities ✅  
B) Lower computational requirements  
C) Reduced network traffic  
D) Simpler implementation  
**Correct Answer: A) Diverse expertise and parallel problem-solving capabilities**

**Explanation:** Collaborative agent teams leverage diverse expertise and enable parallel problem-solving, allowing complex tasks to be broken down and solved more efficiently than single-agent approaches.

---

## Scoring Guide

- **10 correct**: Expert level - Ready for complex multi-agent system design  
- **8-9 correct**: Proficient - Strong understanding of A2A communication patterns  
- **6-7 correct**: Competent - Good grasp of agent coordination concepts  
- **4-5 correct**: Developing - Review message protocols and coordination patterns  
- **Below 4**: Beginner - Revisit A2A fundamentals and communication principles  

## Key Concepts Summary

1. **A2A Protocol**: Structured communication enabling agent collaboration  
2. **Message Types**: DISCOVERY, REQUEST, RESPONSE, ANNOUNCEMENT for different purposes  
3. **Service Discovery**: Dynamic discovery of agents and their capabilities  
4. **Coordination Patterns**: Orchestration (centralized) vs choreography (distributed)  
5. **Fault Tolerance**: Message queuing and retry mechanisms for reliability  

---

## 💡 Practical Exercise Solution

**Challenge:** Create a multi-agent customer service system with A2A coordination.

### Complete A2A Customer Service System:

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
            data=inquiry_data,
            metadata={
                "ticket_id": ticket_id,
                "timestamp": datetime.now().isoformat(),
                "correlation_id": f"inquiry_{ticket_id}"
            }
        )
        
        logger.info(f"Customer inquiry processed: {ticket_id}")
        return ticket_id
```

### Key Features Implemented:

1. **Event-Driven Coordination**: Uses choreography patterns for distributed agent coordination
2. **Intelligent Routing**: Routes inquiries based on priority, category, and customer tier
3. **Escalation Management**: Automatic escalation based on complexity and timing
4. **Quality Assurance**: Peer review for uncertain solutions and customer feedback tracking
5. **Multi-Level Support**: Different agent capabilities for various support levels

This A2A customer service system demonstrates distributed coordination where agents respond to events and coordinate their actions without centralized control.

---

[Return to Session 7](Session7_Agent_to_Agent_Communication.md)