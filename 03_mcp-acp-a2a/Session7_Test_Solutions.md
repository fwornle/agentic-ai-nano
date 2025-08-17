# Session 7: Agent to Agent Communication - Test Solutions

## 📝 Multiple Choice Test

### Question 1: A2A Communication Purpose
**What is the primary purpose of Agent-to-Agent (A2A) communication?**

A) To replace human operators  
B) To enable multiple agents to collaborate and coordinate actions ✅  
C) To improve individual agent performance  
D) To reduce computational costs  

**Explanation:** A2A communication enables multiple AI agents to collaborate, share information, and coordinate actions to solve complex problems requiring diverse expertise and coordination.

---

### Question 2: Message Types
**Which message type is used for finding agents with specific capabilities?**

A) REQUEST  
B) RESPONSE  
C) DISCOVERY ✅  
D) HEARTBEAT  

**Explanation:** DISCOVERY messages are specifically designed for agent discovery requests, allowing agents to find other agents with required capabilities in the network.

---

### Question 3: Message Routing
**What information is essential for proper A2A message routing?**

A) Only the message content  
B) Sender ID, recipient ID, and message type ✅  
C) Just the timestamp  
D) Only the priority level  

**Explanation:** Proper message routing requires sender identification, recipient targeting, and message type classification to ensure messages reach the correct destination with appropriate handling.

---

### Question 4: Coordination Patterns
**What is the difference between orchestration and choreography in multi-agent systems?**

A) Orchestration is faster than choreography  
B) Orchestration uses centralized control, choreography uses distributed coordination ✅  
C) Choreography requires more memory  
D) There is no difference  

**Explanation:** Orchestration involves centralized control where a coordinator directs workflow execution, while choreography involves distributed coordination where agents follow predefined interaction patterns.

---

### Question 5: Service Discovery
**How do agents announce their capabilities in an A2A system?**

A) Through manual configuration  
B) Using ANNOUNCEMENT messages with capability metadata ✅  
C) Via external databases only  
D) Through file-based configurations  

**Explanation:** Agents use ANNOUNCEMENT messages containing detailed capability metadata to inform other agents about their available services and expertise areas.

---

### Question 6: Fault Tolerance
**What mechanism ensures A2A communication reliability when agents become unavailable?**

A) Faster processing  
B) Message queuing with retry logic and timeouts ✅  
C) Increased memory allocation  
D) Multiple network interfaces  

**Explanation:** Message queuing with retry logic and timeout mechanisms ensures communication reliability by handling temporary agent unavailability and network issues.

---

### Question 7: Capability Negotiation
**What is the purpose of capability negotiation in A2A systems?**

A) To improve performance  
B) To match agent capabilities with task requirements ✅  
C) To reduce costs  
D) To simplify configuration  

**Explanation:** Capability negotiation matches available agent capabilities with specific task requirements, ensuring that tasks are assigned to agents with appropriate skills and resources.

---

### Question 8: Message Priority
**When should URGENT priority be used for A2A messages?**

A) For all important messages  
B) For time-critical operations requiring immediate attention ✅  
C) For routine status updates  
D) For data backup operations  

**Explanation:** URGENT priority should be reserved for time-critical operations that require immediate attention, such as emergency shutdowns or critical error conditions.

---

### Question 9: Correlation ID
**What is the purpose of correlation IDs in A2A messaging?**

A) To encrypt messages  
B) To link related messages in multi-step workflows ✅  
C) To compress message content  
D) To validate message integrity  

**Explanation:** Correlation IDs link related messages across multi-step workflows, enabling proper tracking and coordination of complex interactions between agents.

---

### Question 10: Distributed Teams
**What is a key benefit of collaborative agent teams in A2A systems?**

A) Lower computational requirements  
B) Diverse expertise and parallel problem-solving capabilities ✅  
C) Simpler implementation  
D) Reduced network traffic  

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

[Return to Session 7](Session7_Agent_to_Agent_Communication.md)