# Session 5: Building Secure MCP Servers - Test Solutions

## 📝 Multiple Choice Test

### Question 1: Security Architecture
**What security approach does the session recommend for MCP servers?**

A) Client-side security only  
B) Single-layer authentication only  
C) Defense-in-depth with multiple security layers ✅  
D) Network security only  
**Correct Answer: C) Defense-in-depth with multiple security layers**

**Explanation:** Defense-in-depth provides multiple security layers including authentication, authorization, network security, and application security to protect against various attack vectors.

---

### Question 2: JWT Token Security
**What is the minimum recommended length for JWT secret keys?**

A) 16 characters  
B) 64 characters  
C) 32 characters ✅  
D) 24 characters  
**Correct Answer: C) 32 characters**

**Explanation:** JWT secret keys should be at least 32 characters to provide adequate cryptographic security. Shorter keys are vulnerable to brute force attacks.

---

### Question 3: Token Management
**How should refresh tokens be handled for maximum security?**

A) Include them in URL parameters  
B) Store them in localStorage  
C) Store them in browser cookies only  
D) Use Redis with automatic expiration and blacklisting ✅  
**Correct Answer: D) Use Redis with automatic expiration and blacklisting**

**Explanation:** Redis provides secure server-side storage with automatic expiration and blacklisting capabilities, preventing token replay attacks and ensuring proper lifecycle management.

---

### Question 4: Rate Limiting Strategy
**Which rate limiting algorithm provides the best balance of fairness and burst handling?**

A) Fixed window  
B) Sliding window  
C) Leaky bucket  
D) Token bucket ✅  
**Correct Answer: D) Token bucket**

**Explanation:** Token bucket algorithm allows controlled bursts while maintaining overall rate limits, providing better user experience than strict fixed-window approaches.

---

### Question 5: Role-Based Access Control
**What is the advantage of role-based permissions over user-specific permissions?**

A) Higher security  
B) Better performance  
C) Easier management and scalability ✅  
D) Simpler implementation  
**Correct Answer: C) Easier management and scalability**

**Explanation:** Role-based access control (RBAC) provides easier management and better scalability by grouping permissions into roles that can be assigned to multiple users, reducing administrative overhead.

---

### Question 6: Input Validation
**What is the recommended approach for validating MCP tool inputs?**

A) Server-side validation using Pydantic models ✅  
B) Database constraints only  
C) Client-side validation only  
D) No validation needed  
**Correct Answer: A) Server-side validation using Pydantic models**

**Explanation:** Server-side validation using Pydantic models provides comprehensive type checking, data sanitization, and protection against injection attacks while maintaining data integrity.

---

### Question 7: TLS Configuration
**What TLS version should be the minimum requirement for production MCP servers?**

A) SSL 3.0  
B) TLS 1.1  
C) TLS 1.0  
D) TLS 1.2 ✅  
**Correct Answer: D) TLS 1.2**

**Explanation:** TLS 1.2 is the minimum recommended version for production systems as earlier versions have known security vulnerabilities and are deprecated.

---

### Question 8: API Key Management
**How should API keys be rotated securely in production?**

A) Rotate only when compromised  
B) Automatic rotation with overlap periods ✅  
C) Never rotate keys  
D) Manual rotation monthly  
**Correct Answer: B) Automatic rotation with overlap periods**

**Explanation:** Automatic API key rotation with overlap periods ensures continuous service availability while maintaining security through regular key refresh cycles.

---

### Question 9: Audit Logging
**What information is most critical to include in security audit logs?**

A) System performance metrics  
B) Only successful operations  
C) Debug information only  
D) Authentication events and permission changes ✅  
**Correct Answer: D) Authentication events and permission changes**

**Explanation:** Security audit logs should capture authentication events, authorization decisions, and permission changes to enable security monitoring and compliance reporting.

---

### Question 10: DDoS Protection
**Which technique is most effective for protecting MCP servers from DDoS attacks?**

A) Blocking all international traffic  
B) Using only strong authentication  
C) Implementing multiple rate limiting layers ✅  
D) Increasing server capacity  
**Correct Answer: C) Implementing multiple rate limiting layers**

**Explanation:** Multiple rate limiting layers (per-IP, per-user, per-endpoint) provide comprehensive DDoS protection by preventing various attack patterns while maintaining legitimate user access.

---

## Scoring Guide

- **10 correct**: Expert level - Ready for enterprise security implementations  
- **8-9 correct**: Proficient - Strong understanding of MCP security principles  
- **6-7 correct**: Competent - Good grasp of authentication and authorization  
- **4-5 correct**: Developing - Review JWT and RBAC sections  
- **Below 4**: Beginner - Revisit security fundamentals and best practices  

## Key Concepts Summary

1. **Defense-in-Depth**: Multiple security layers provide comprehensive protection  
2. **JWT Security**: Minimum 32-character keys with proper lifecycle management  
3. **RBAC**: Role-based permissions for scalable access control  
4. **Input Validation**: Server-side Pydantic models prevent injection attacks  
5. **Rate Limiting**: Token bucket algorithm with multiple layers for DDoS protection  

---

[Return to Session 5](Session5_Secure_MCP_Server.md)