# Session 5: Building Secure MCP Servers - Test Solutions

## 📝 Multiple Choice Test

### Question 1: Security Architecture
**What security approach does the session recommend for MCP servers?**

A) Single-layer authentication only  
B) Defense-in-depth with multiple security layers ✅  
C) Client-side security only  
D) Network security only  

**Explanation:** Defense-in-depth provides multiple security layers including authentication, authorization, network security, and application security to protect against various attack vectors.

---

### Question 2: JWT Token Security
**What is the minimum recommended length for JWT secret keys?**

A) 16 characters  
B) 24 characters  
C) 32 characters ✅  
D) 64 characters  

**Explanation:** JWT secret keys should be at least 32 characters to provide adequate cryptographic security. Shorter keys are vulnerable to brute force attacks.

---

### Question 3: Token Management
**How should refresh tokens be handled for maximum security?**

A) Store them in localStorage  
B) Use Redis with automatic expiration and blacklisting ✅  
C) Include them in URL parameters  
D) Store them in browser cookies only  

**Explanation:** Redis provides secure server-side storage with automatic expiration and blacklisting capabilities, preventing token replay attacks and ensuring proper lifecycle management.

---

### Question 4: Rate Limiting Strategy
**Which rate limiting algorithm provides the best balance of fairness and burst handling?**

A) Fixed window  
B) Sliding window  
C) Token bucket ✅  
D) Leaky bucket  

**Explanation:** Token bucket algorithm allows controlled bursts while maintaining overall rate limits, providing better user experience than strict fixed-window approaches.

---

### Question 5: Role-Based Access Control
**What is the advantage of role-based permissions over user-specific permissions?**

A) Better performance  
B) Easier management and scalability ✅  
C) Higher security  
D) Simpler implementation  

**Explanation:** Role-based access control (RBAC) provides easier management and better scalability by grouping permissions into roles that can be assigned to multiple users, reducing administrative overhead.

---

### Question 6: Input Validation
**What is the recommended approach for validating MCP tool inputs?**

A) Client-side validation only  
B) Server-side validation using Pydantic models ✅  
C) Database constraints only  
D) No validation needed  

**Explanation:** Server-side validation using Pydantic models provides comprehensive type checking, data sanitization, and protection against injection attacks while maintaining data integrity.

---

### Question 7: TLS Configuration
**What TLS version should be the minimum requirement for production MCP servers?**

A) TLS 1.0  
B) TLS 1.1  
C) TLS 1.2 ✅  
D) SSL 3.0  

**Explanation:** TLS 1.2 is the minimum recommended version for production systems as earlier versions have known security vulnerabilities and are deprecated.

---

### Question 8: API Key Management
**How should API keys be rotated securely in production?**

A) Manual rotation monthly  
B) Automatic rotation with overlap periods ✅  
C) Never rotate keys  
D) Rotate only when compromised  

**Explanation:** Automatic API key rotation with overlap periods ensures continuous service availability while maintaining security through regular key refresh cycles.

---

### Question 9: Audit Logging
**What information is most critical to include in security audit logs?**

A) Only successful operations  
B) Authentication events and permission changes ✅  
C) System performance metrics  
D) Debug information only  

**Explanation:** Security audit logs should capture authentication events, authorization decisions, and permission changes to enable security monitoring and compliance reporting.

---

### Question 10: DDoS Protection
**Which technique is most effective for protecting MCP servers from DDoS attacks?**

A) Increasing server capacity  
B) Implementing multiple rate limiting layers ✅  
C) Using only strong authentication  
D) Blocking all international traffic  

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