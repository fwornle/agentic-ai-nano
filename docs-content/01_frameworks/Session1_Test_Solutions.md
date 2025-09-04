# Session 1: Bare Metal Agents - Test Solutions

## 📝 Multiple Choice Test - Session 1

**Question 1:** What is the primary benefit of implementing agents from scratch before using frameworks?  
A) Lower resource usage  
B) Easier deployment  
C) Better performance  
D) Deeper understanding of agent mechanics ✅  

**Explanation:** Building agents from scratch provides deep insight into the core mechanics, patterns, and architecture decisions that frameworks abstract away, enabling better framework selection and customization.

**Question 2:** In the BaseAgent class, what is the purpose of the conversation_history attribute?  
A) Maintaining context across interactions ✅  
B) Error tracking  
C) Performance monitoring  
D) Tool execution logs  

**Explanation:** The conversation_history maintains the context of previous interactions, allowing agents to understand the conversation flow and provide contextually relevant responses.

**Question 3:** Which method must be implemented by all subclasses of BaseAgent?  
A) get_available_tools()  
B) process_message()  
C) add_tool()  
D) _generate_response() ✅  

**Explanation:** The _generate_response() method is the abstract method that each agent subclass must implement to define its specific response generation logic.

**Question 4:** How does the Tool abstract base class ensure consistency across different tool implementations?  
A) By handling errors automatically  
B) By providing default implementations  
C) By requiring execute() and _get_parameters() methods ✅  
D) By managing tool state  

**Explanation:** The Tool abstract base class defines a consistent interface by requiring all tools to implement execute() for functionality and _get_parameters() for metadata.

**Question 5:** What design pattern is demonstrated by the BaseAgent and its subclasses?  
A) Strategy Pattern  
B) Factory Pattern  
C) Template Method Pattern ✅  
D) Observer Pattern  

**Explanation:** The Template Method Pattern defines the skeleton of an algorithm in the base class while letting subclasses override specific steps - exactly how BaseAgent works with _generate_response().

---

## 🧭 Navigation

**Back to Test:** [Session 1 Test Questions →](Session1_Bare_Metal_Agents.md#knowledge-check-session-1)

---
