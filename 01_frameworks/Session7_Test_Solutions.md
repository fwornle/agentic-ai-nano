# Session 7: Building Your First ADK Agent - Test Solutions

## 📝 Multiple Choice Test

### Question 1: Conversation Memory
**What is the primary role of the ConversationMemory class?**

A) Store user preferences  
B) Maintain conversation context and history ✅  
C) Handle tool integration  
D) Manage cloud deployment  

**Explanation:** ConversationMemory maintains the context and history of conversations, allowing agents to provide contextually relevant responses across multiple interaction turns.

---

### Question 2: Tool Selection
**How does the ADK agent determine when to use MCP tools?**

A) Random selection  
B) User explicitly requests tools  
C) Response analysis and pattern matching ✅  
D) Fixed rule-based system  

**Explanation:** The agent analyzes user messages for patterns and keywords to intelligently determine when specific MCP tools should be invoked, using confidence-based selection.

---

### Question 3: Async Processing
**What advantage does async processing provide in agent implementations?**

A) Simpler code structure  
B) Better error handling  
C) Non-blocking operations and improved performance ✅  
D) Easier debugging  

**Explanation:** Async processing allows agents to handle multiple concurrent requests efficiently without blocking, significantly improving overall performance and responsiveness.

---

### Question 4: Context Management
**How does the agent maintain context across conversation turns?**

A) Static variables  
B) ConversationMemory with turn tracking ✅  
C) External database  
D) Cloud storage  

**Explanation:** The ConversationMemory system tracks individual conversation turns with timestamps, roles, and metadata, maintaining context across the entire conversation session.

---

### Question 5: System Prompt
**What is the purpose of the system prompt in agent responses?**

A) User identification  
B) Provide context about available tools and agent capabilities ✅  
C) Error handling  
D) Performance optimization  

**Explanation:** The system prompt informs the Gemini model about the agent's capabilities, available tools, and operational context, enabling more accurate and helpful responses.

---

## Scoring Guide

- **5 correct**: Expert level - Ready for advanced ADK agent development
- **4 correct**: Proficient - Strong understanding of ADK fundamentals
- **3 correct**: Competent - Good grasp of core concepts
- **2 correct**: Developing - Review memory and tool integration sections
- **Below 2**: Beginner - Revisit session materials and examples

## Key Concepts Summary

1. **ConversationMemory**: Essential for maintaining context across conversation turns
2. **Tool Integration**: Pattern-based intelligent tool selection for MCP capabilities
3. **Async Processing**: Non-blocking operations for improved performance
4. **Context Management**: Turn tracking with timestamps and metadata
5. **System Prompts**: Informing models about agent capabilities and available tools

---

[Return to Session 7](Session7_First_ADK_Agent.md)
