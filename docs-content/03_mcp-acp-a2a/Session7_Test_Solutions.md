# Session 7: Agent to Agent Communication - Test Solutions

## 📝 Multiple Choice Test - Session 7

**Question 1:** What is the primary purpose of Agent-to-Agent (A2A) communication?  

A) To reduce computational costs  
B) To improve individual agent performance  
C) To enable multiple agents to collaborate and coordinate actions ✅  
D) To replace human operators  

**Explanation:** A2A communication enables multiple AI agents to collaborate, share information, and coordinate actions to solve complex problems requiring diverse expertise and coordination.

**Question 2:** Which message type is used for finding agents with specific capabilities?  

A) RESPONSE  
B) HEARTBEAT  
C) DISCOVERY ✅  
D) REQUEST  

**Explanation:** DISCOVERY messages are specifically designed for agent discovery requests, allowing agents to find other agents with required capabilities in the network.

**Question 3:** What information is essential for proper A2A message routing?  

A) Just the timestamp  
B) Only the priority level  
C) Only the message content  
D) Sender ID, recipient ID, and message type ✅  

**Explanation:** Proper message routing requires sender identification, recipient targeting, and message type classification to ensure messages reach the correct destination with appropriate handling.

**Question 4:** What is the difference between orchestration and choreography in multi-agent systems?  

A) Orchestration uses centralized control, choreography uses distributed coordination ✅  
B) Choreography requires more memory  
C) There is no difference  
D) Orchestration is faster than choreography  

**Explanation:** Orchestration involves centralized control where a coordinator directs workflow execution, while choreography involves distributed coordination where agents follow predefined interaction patterns.

**Question 5:** How do agents announce their capabilities in an A2A system?  

A) Using ANNOUNCEMENT messages with capability metadata ✅  
B) Through manual configuration  
C) Via external databases only  
D) Through file-based configurations  

**Explanation:** Agents use ANNOUNCEMENT messages containing detailed capability metadata to inform other agents about their available services and expertise areas.

**Question 6:** What mechanism ensures A2A communication reliability when agents become unavailable?  

A) Faster processing  
B) Increased memory allocation  
C) Message queuing with retry logic and timeouts ✅  
D) Multiple network interfaces  

**Explanation:** Message queuing with retry logic and timeout mechanisms ensures communication reliability by handling temporary agent unavailability and network issues.

**Question 7:** What is the purpose of capability negotiation in A2A systems?  

A) To improve performance  
B) To match agent capabilities with task requirements ✅  
C) To simplify configuration  
D) To reduce costs  

**Explanation:** Capability negotiation matches available agent capabilities with specific task requirements, ensuring that tasks are assigned to agents with appropriate skills and resources.

**Question 8:** When should URGENT priority be used for A2A messages?  

A) For time-critical operations requiring immediate attention ✅  
B) For data backup operations  
C) For routine status updates  
D) For all important messages  

**Explanation:** URGENT priority should be reserved for time-critical operations that require immediate attention, such as emergency shutdowns or critical error conditions.

**Question 9:** What is the purpose of correlation IDs in A2A messaging?  

A) To validate message integrity  
B) To encrypt messages  
C) To compress message content  
D) To link related messages in multi-step workflows ✅  

**Explanation:** Correlation IDs link related messages across multi-step workflows, enabling proper tracking and coordination of complex interactions between agents.

**Question 10:** What is a key benefit of collaborative agent teams in A2A systems?  

A) Diverse expertise and parallel problem-solving capabilities ✅  
B) Lower computational requirements  
C) Reduced network traffic  
D) Simpler implementation  

**Explanation:** Collaborative agent teams leverage diverse expertise and enable parallel problem-solving, allowing complex tasks to be broken down and solved more efficiently than single-agent approaches.

---

## 🧭 Navigation

**Back to Test:** [Session 7 Test Questions →](Session7_Advanced_Choreography.md#multiple-choice-test)

---
