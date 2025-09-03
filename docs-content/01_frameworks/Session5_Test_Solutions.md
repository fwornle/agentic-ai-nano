# Session 5: PydanticAI Type-Safe Agents - Test Solutions

## 📝 Multiple Choice Test

**Question 1:** What is the primary advantage of PydanticAI over traditional agent frameworks?  

A) Faster execution speed  
B) Lower computational cost  
C) Better user interface  
D) Automatic validation and structured outputs with compile-time type checking ✅  

**Explanation:** PydanticAI's core strength lies in combining strong type safety with automatic validation and structured outputs, providing compile-time type checking that catches errors early in development.

---

**Question 2:** Which validation constraint ensures a field value falls within a specific numeric range?  

A) Field(range=(0, 100))  
B) Field(between=0:100)  
C) Field(min=0, max=100)  
D) Field(ge=0, le=100) ✅  

**Explanation:** The `ge` (greater than or equal) and `le` (less than or equal) constraints provide inclusive numeric bounds for field validation.

---

**Question 3:** What happens when PydanticAI model validation fails?  

A) Application crashes immediately  
B) Silent failure with default values  
C) Warning message is logged  
D) ValidationError is raised with detailed field information ✅  

**Explanation:** ValidationError provides comprehensive debugging information including specific field errors, making it easy to identify and fix validation issues.

---

**Question 4:** How do you define a tool function for a PydanticAI agent?  

A) Using @tool decorator  
B) Using def tool() syntax  
C) Using @function decorator  
D) Using @agent.tool decorator ✅  

**Explanation:** The @agent.tool decorator is the standard way to define tool functions that can be called by PydanticAI agents.

---

**Question 5:** What is the purpose of RunContext in PydanticAI?  

A) Handles error messages  
B) Provides runtime configuration and dependencies ✅  
C) Manages conversation history  
D) Controls execution speed  

**Explanation:** RunContext manages runtime configuration, dependencies, and execution context, providing agents with necessary runtime information and services.

---

**Question 6:** Which decorator enables cross-field validation in Pydantic models?  

A) @cross_validator  
B) @model_validator  
C) @root_validator ✅  
D) @field_validator  

**Explanation:** The @root_validator decorator enables validation logic that can access and validate relationships between multiple fields in a model.

---

**Question 7:** How do you implement custom validation logic for complex business rules?  

A) Custom @validator decorator with logic ✅  
B) External validation services  
C) Built-in validators only  
D) Database constraints  

**Explanation:** Custom validators using the @validator decorator provide maximum flexibility for implementing complex business rules and validation logic.

---

**Question 8:** What's the best practice for handling validation errors in production?  

A) Return generic error messages  
B) Log errors and continue silently  
C) Structured error responses with user-friendly messages ✅  
D) Crash and restart  

**Explanation:** Production systems should provide structured, user-friendly error messages while maintaining security and providing sufficient debugging information.

---

**Question 9:** How do you implement conditional validation based on another field's value?  

A) Database triggers  
B) External validation functions  
C) @field_validator with conditions  
D) @root_validator accessing all field values ✅  

**Explanation:** Root validators can access all field values simultaneously, enabling conditional validation logic based on relationships between fields.

---

**Question 10:** What's the recommended approach for validating enum-like fields?  

A) String validation with allowed values  
B) Custom validation functions  
C) Database foreign keys  
D) Use Python Enum with automatic validation ✅  

**Explanation:** Python Enums provide built-in type safety with automatic serialization and validation support, making them ideal for enum-like fields.

---

**Question 11:** Which pattern prevents cascading failures in agent systems?  

A) Caching strategies  
B) Circuit breaker with fallback mechanisms ✅  
C) Retry with exponential backoff  
D) Load balancing only  

**Explanation:** The circuit breaker pattern prevents cascade failures by detecting service degradation and providing fallback mechanisms, enabling graceful system degradation.

---

**Question 12:** How should you handle timeouts in PydanticAI agent execution?  

A) Simple sleep() calls  
B) Manual timeout tracking  
C) asyncio.wait_for() with proper exception handling ✅  
D) Infinite waiting  

**Explanation:** asyncio.wait_for() provides controlled timeout management with proper exception handling for async operations.

---

**Question 13:** What's the best approach for rate limiting agent requests?  

A) Semaphores with configurable limits ✅  
B) Random throttling  
C) Simple counters  
D) Fixed delays  

**Explanation:** Semaphores provide controlled concurrency limiting while maintaining performance and preventing resource exhaustion.

---

**Question 14:** Which metrics are most important for monitoring PydanticAI agents?  

A) CPU usage only  
B) Memory usage only  
C) Success rate, response time, and validation failures ✅  
D) Network throughput only  

**Explanation:** Success rate, response time, and validation failures are key indicators of agent reliability, performance, and data quality.

---

**Question 15:** How should you manage configuration in production PydanticAI applications?  

A) Environment variables with Pydantic Settings ✅  
B) Hard-coded values  
C) JSON files only  
D) Database storage  

**Explanation:** Environment variables with Pydantic Settings provide flexibility, validation, and security for configuration management.

---

**Question 16:** What's the most robust retry strategy for failed agent operations?  

A) Exponential backoff with circuit breaker ✅  
B) Fixed interval retries  
C) Linear backoff  
D) Random intervals  

**Explanation:** Exponential backoff with circuit breaker provides the most robust recovery mechanism, preventing system overload while maintaining resilience.

---

**Question 17:** How do you handle partial failures in multi-step agent workflows?  

A) Manual intervention only  
B) Circuit breaker with fallback strategies ✅  
C) Fail entire workflow  
D) Ignore failures  

**Explanation:** Circuit breakers with fallback strategies maintain service availability and prevent cascade failures during partial system outages.

---

**Question 18:** Which logging strategy provides the best observability?  

A) Simple text logs  
B) Debug statements only  
C) Error logs only  
D) Structured logging with correlation IDs ✅  

**Explanation:** Structured logging with correlation IDs enables effective monitoring, debugging, and tracing across distributed agent systems.

---

**Question 19:** How should you integrate PydanticAI with existing systems?  

A) Direct database access  
B) File-based integration  
C) Adapter pattern with Pydantic models ✅  
D) Manual data transformation  

**Explanation:** The adapter pattern with Pydantic models ensures type safety and validation throughout the integration chain while providing clean interfaces.

---

**Question 20:** What's the best practice for handling transient errors?  

A) Exponential backoff with jitter and max retries ✅  
B) Immediate failure  
C) Manual recovery only  
D) Fixed retries  

**Explanation:** Exponential backoff with jitter prevents overwhelming failing services while providing reasonable recovery attempts.

---

**Question 21:** Which caching strategy works best for PydanticAI agents?  

A) No caching  
B) Infinite caching  
C) Random cache eviction  
D) LRU cache with TTL for frequently accessed data ✅  

**Explanation:** LRU cache with TTL provides optimal balance of performance improvement and memory management for frequently accessed data.

---

**Question 22:** What is the benefit of batch processing in PydanticAI applications?  

A) Simpler code structure  
B) Easier debugging  
C) Better error messages  
D) Improved throughput and resource utilization ✅  

**Explanation:** Batch processing reduces overhead per item and enables more efficient resource utilization, significantly improving overall throughput.

---

**Question 23:** How should you optimize PydanticAI model validation performance?  

A) Use field-level caching and validation shortcuts ✅  
B) Disable all validation  
C) Validate only critical fields  
D) Use external validation services  

**Explanation:** Field-level caching and validation shortcuts maintain data integrity while improving performance for frequently validated data.

---

**Question 24:** Which approach minimizes memory usage in large-scale PydanticAI deployments?  

A) Cache all data permanently  
B) Load everything in memory  
C) Implement lazy loading with weak references and cleanup ✅  
D) Use only global variables  

**Explanation:** Lazy loading with weak references and proper cleanup prevents memory leaks and enables efficient memory usage in long-running applications.

---

**Question 25:** What is the most effective way to monitor PydanticAI agent performance?  

A) Automated metrics collection with alerts and dashboards ✅  
B) Manual log review  
C) Periodic manual testing  
D) User feedback only  

**Explanation:** Automated metrics collection with alerts and dashboards provides real-time visibility into agent performance and enables proactive issue resolution.

---

## Scoring Guide

- **23-25 correct**: Expert level - Ready for advanced PydanticAI implementations  
- **20-22 correct**: Proficient - Strong understanding of PydanticAI patterns  
- **16-19 correct**: Competent - Good grasp of core concepts  
- **12-15 correct**: Developing - Review validation and error handling sections  
- **Below 12**: Beginner - Revisit session materials and practice examples  

## Key Concepts Summary

1. **Type Safety**: PydanticAI's primary advantage is compile-time type checking with runtime validation  
2. **Validation Patterns**: Field validators, root validators, and custom validation for comprehensive data integrity  
3. **Error Handling**: Circuit breakers, structured error responses, and graceful degradation for production resilience  
4. **Performance Optimization**: Caching, batching, lazy loading, and monitoring for optimal resource utilization  
5. **Production Deployment**: Environment-based configuration, comprehensive monitoring, and automated metrics collection  

---

[Return to Session 5](Session5_PydanticAI_Type_Safe_Agents.md)
---

**Next:** [Session 6 - Atomic Agents Modular Architecture →](Session6_Atomic_Agents_Modular_Architecture.md)

---
