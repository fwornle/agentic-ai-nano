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

[Return to Session 7](Session7_Agent_to_Agent_Communication.md)