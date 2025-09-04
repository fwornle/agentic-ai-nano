# Session 5: Building Secure MCP Servers - Test Solutions

## 📝 Multiple Choice Test - Session 5

**Question 1:** What security approach does the session recommend for MCP servers?  

A) Client-side security only  
B) Single-layer authentication only  
C) Defense-in-depth with multiple security layers ✅  
D) Network security only  

**Explanation:** Defense-in-depth provides multiple security layers including authentication, authorization, network security, and application security to protect against various attack vectors.

**Question 2:** What is the minimum recommended length for JWT secret keys?  

A) 16 characters  
B) 64 characters  
C) 32 characters ✅  
D) 24 characters  

**Explanation:** JWT secret keys should be at least 32 characters to provide adequate cryptographic security. Shorter keys are vulnerable to brute force attacks.

**Question 3:** How should refresh tokens be handled for maximum security?  

A) Include them in URL parameters  
B) Store them in localStorage  
C) Store them in browser cookies only  
D) Use Redis with automatic expiration and blacklisting ✅  

**Explanation:** Redis provides secure server-side storage with automatic expiration and blacklisting capabilities, preventing token replay attacks and ensuring proper lifecycle management.

**Question 4:** Which rate limiting algorithm provides the best balance of fairness and burst handling?  

A) Fixed window  
B) Sliding window  
C) Leaky bucket  
D) Token bucket ✅  

**Explanation:** Token bucket algorithm allows controlled bursts while maintaining overall rate limits, providing better user experience than strict fixed-window approaches.

**Question 5:** What is the advantage of role-based permissions over user-specific permissions?  

A) Higher security  
B) Better performance  
C) Easier management and scalability ✅  
D) Simpler implementation  

**Explanation:** Role-based access control (RBAC) provides easier management and better scalability by grouping permissions into roles that can be assigned to multiple users, reducing administrative overhead.

**Question 6:** What is the recommended approach for validating MCP tool inputs?  

A) Server-side validation using Pydantic models ✅  
B) Database constraints only  
C) Client-side validation only  
D) No validation needed  

**Explanation:** Server-side validation using Pydantic models provides comprehensive type checking, data sanitization, and protection against injection attacks while maintaining data integrity.

**Question 7:** What TLS version should be the minimum requirement for production MCP servers?  

A) SSL 3.0  
B) TLS 1.1  
C) TLS 1.0  
D) TLS 1.2 ✅  

**Explanation:** TLS 1.2 is the minimum recommended version for production systems as earlier versions have known security vulnerabilities and are deprecated.

**Question 8:** How should API keys be rotated securely in production?  

A) Rotate only when compromised  
B) Automatic rotation with overlap periods ✅  
C) Never rotate keys  
D) Manual rotation monthly  

**Explanation:** Automatic API key rotation with overlap periods ensures continuous service availability while maintaining security through regular key refresh cycles.

**Question 9:** What information is most critical to include in security audit logs?  

A) System performance metrics  
B) Only successful operations  
C) Debug information only  
D) Authentication events and permission changes ✅  

**Explanation:** Security audit logs should capture authentication events, authorization decisions, and permission changes to enable security monitoring and compliance reporting.

**Question 10:** Which technique is most effective for protecting MCP servers from DDoS attacks?  

A) Blocking all international traffic  
B) Using only strong authentication  
C) Implementing multiple rate limiting layers ✅  
D) Increasing server capacity  

**Explanation:** Multiple rate limiting layers (per-IP, per-user, per-endpoint) provide comprehensive DDoS protection by preventing various attack patterns while maintaining legitimate user access.

---

## 🧭 Navigation

**Back to Test:** [Session 5 Test Questions →](Session5_Production_Rate_Limiting.md#multiple-choice-test-session-5)

---
