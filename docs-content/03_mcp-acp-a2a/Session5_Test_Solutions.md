# Session 5: Building Secure MCP Servers - Test Solutions

## 📝 Multiple Choice Test

**Question 1:** What security approach does the session recommend for MCP servers?  

A) Client-side security only  
B) Single-layer authentication only  
C) Defense-in-depth with multiple security layers ✅  
D) Network security only  


**Explanation:** Defense-in-depth provides multiple security layers including authentication, authorization, network security, and application security to protect against various attack vectors.

---

**Question 2:** What is the minimum recommended length for JWT secret keys?  

A) 16 characters  
B) 64 characters  
C) 32 characters ✅  
D) 24 characters  


**Explanation:** JWT secret keys should be at least 32 characters to provide adequate cryptographic security. Shorter keys are vulnerable to brute force attacks.

---

**Question 3:** How should refresh tokens be handled for maximum security?  

A) Include them in URL parameters  
B) Store them in localStorage  
C) Store them in browser cookies only  
D) Use Redis with automatic expiration and blacklisting ✅  


**Explanation:** Redis provides secure server-side storage with automatic expiration and blacklisting capabilities, preventing token replay attacks and ensuring proper lifecycle management.

---

**Question 4:** Which rate limiting algorithm provides the best balance of fairness and burst handling?  

A) Fixed window  
B) Sliding window  
C) Leaky bucket  
D) Token bucket ✅  


**Explanation:** Token bucket algorithm allows controlled bursts while maintaining overall rate limits, providing better user experience than strict fixed-window approaches.

---

**Question 5:** What is the advantage of role-based permissions over user-specific permissions?  

A) Higher security  
B) Better performance  
C) Easier management and scalability ✅  
D) Simpler implementation  


**Explanation:** Role-based access control (RBAC) provides easier management and better scalability by grouping permissions into roles that can be assigned to multiple users, reducing administrative overhead.

---

**Question 6:** What is the recommended approach for validating MCP tool inputs?  

A) Server-side validation using Pydantic models ✅  
B) Database constraints only  
C) Client-side validation only  
D) No validation needed  


**Explanation:** Server-side validation using Pydantic models provides comprehensive type checking, data sanitization, and protection against injection attacks while maintaining data integrity.

---

**Question 7:** What TLS version should be the minimum requirement for production MCP servers?  

A) SSL 3.0  
B) TLS 1.1  
C) TLS 1.0  
D) TLS 1.2 ✅  


**Explanation:** TLS 1.2 is the minimum recommended version for production systems as earlier versions have known security vulnerabilities and are deprecated.

---

**Question 8:** How should API keys be rotated securely in production?  

A) Rotate only when compromised  
B) Automatic rotation with overlap periods ✅  
C) Never rotate keys  
D) Manual rotation monthly  


**Explanation:** Automatic API key rotation with overlap periods ensures continuous service availability while maintaining security through regular key refresh cycles.

---

**Question 9:** What information is most critical to include in security audit logs?  

A) System performance metrics  
B) Only successful operations  
C) Debug information only  
D) Authentication events and permission changes ✅  


**Explanation:** Security audit logs should capture authentication events, authorization decisions, and permission changes to enable security monitoring and compliance reporting.

---

**Question 10:** Which technique is most effective for protecting MCP servers from DDoS attacks?  

A) Blocking all international traffic  
B) Using only strong authentication  
C) Implementing multiple rate limiting layers ✅  
D) Increasing server capacity  


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

## Practical Exercise Solution

**Challenge:** Implement a security audit system that tracks suspicious activity.

### Complete Security Audit System

```python
# src/security/audit_system.py
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict
import redis
import logging

logger = logging.getLogger(__name__)

class SecurityAuditSystem:
    """Comprehensive security audit and threat detection system."""

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.audit_prefix = "audit:"
        self.metrics_prefix = "metrics:"

        # Threat detection thresholds
        self.thresholds = {
            "failed_auth_attempts": 5,  # per 15 minutes
            "permission_denials": 10,   # per hour
            "rate_limit_hits": 3,       # per 10 minutes
            "unusual_access_score": 7.0  # anomaly detection score
        }

    async def log_security_event(self, event_type: str, user_id: str,
                                details: Dict[str, Any]):
        """Log a security-related event for audit trail."""
        event = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "session_id": details.get("session_id"),
            "ip_address": details.get("ip_address"),
            "user_agent": details.get("user_agent")
        }

        # Store event in Redis with TTL
        event_key = f"{self.audit_prefix}{event_type}:{datetime.now().strftime('%Y%m%d')}"

        try:
            # Add to daily event log (expires after 90 days)
            self.redis_client.lpush(event_key, json.dumps(event))
            self.redis_client.expire(event_key, 90 * 24 * 60 * 60)

            # Update metrics counters
            await self._update_security_metrics(event_type, user_id, details)

            # Check for suspicious patterns
            await self._detect_suspicious_activity(event_type, user_id, details)

            logger.info(f"Security event logged: {event_type} for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    async def _update_security_metrics(self, event_type: str, user_id: str,
                                     details: Dict[str, Any]):
        """Update security metrics for trend analysis."""
        current_hour = datetime.now().strftime('%Y%m%d%H')
        metrics_key = f"{self.metrics_prefix}{current_hour}"

        # Increment counters
        self.redis_client.hincrby(metrics_key, f"total_{event_type}", 1)
        self.redis_client.hincrby(metrics_key, f"user_{user_id}_{event_type}", 1)

        # Set expiration (keep for 30 days)
        self.redis_client.expire(metrics_key, 30 * 24 * 60 * 60)

    async def _detect_suspicious_activity(self, event_type: str, user_id: str,
                                        details: Dict[str, Any]):
        """Detect suspicious activity patterns and trigger alerts."""
        current_time = datetime.now()

        # Check failed authentication attempts (15-minute window)
        if event_type == "auth_failed":
            window_start = current_time - timedelta(minutes=15)
            failed_attempts = await self._count_events_in_window(
                "auth_failed", user_id, window_start, current_time
            )

            if failed_attempts >= self.thresholds["failed_auth_attempts"]:
                await self._trigger_security_alert(
                    "excessive_failed_auth",
                    user_id,
                    {"attempts": failed_attempts, "window": "15min"}
                )

        # Check permission denials (1-hour window)
        elif event_type == "permission_denied":
            window_start = current_time - timedelta(hours=1)
            denials = await self._count_events_in_window(
                "permission_denied", user_id, window_start, current_time
            )

            if denials >= self.thresholds["permission_denials"]:
                await self._trigger_security_alert(
                    "excessive_permission_denials",
                    user_id,
                    {"denials": denials, "window": "1hour"}
                )

        # Check rate limit violations (10-minute window)
        elif event_type == "rate_limit_exceeded":
            window_start = current_time - timedelta(minutes=10)
            violations = await self._count_events_in_window(
                "rate_limit_exceeded", user_id, window_start, current_time
            )

            if violations >= self.thresholds["rate_limit_hits"]:
                await self._trigger_security_alert(
                    "potential_abuse",
                    user_id,
                    {"violations": violations, "window": "10min"}
                )

    async def _count_events_in_window(self, event_type: str, user_id: str,
                                    start_time: datetime, end_time: datetime) -> int:
        """Count security events for a user within a time window."""
        count = 0
        current_date = start_time.date()
        end_date = end_time.date()

        # Check events across date boundaries if necessary
        while current_date <= end_date:
            event_key = f"{self.audit_prefix}{event_type}:{current_date.strftime('%Y%m%d')}"

            try:
                events = self.redis_client.lrange(event_key, 0, -1)

                for event_json in events:
                    event = json.loads(event_json)
                    event_time = datetime.fromisoformat(event["timestamp"])

                    if (start_time <= event_time <= end_time and
                        event["user_id"] == user_id):
                        count += 1

            except Exception as e:
                logger.error(f"Error counting events: {e}")

            current_date += timedelta(days=1)

        return count

    async def _trigger_security_alert(self, alert_type: str, user_id: str,
                                    context: Dict[str, Any]):
        """Trigger security alert for immediate attention."""
        alert = {
            "alert_type": alert_type,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "severity": "high",
            "context": context,
            "requires_action": True
        }

        # Store alert
        alert_key = f"alerts:{alert_type}:{datetime.now().strftime('%Y%m%d')}"
        self.redis_client.lpush(alert_key, json.dumps(alert))
        self.redis_client.expire(alert_key, 30 * 24 * 60 * 60)  # 30 days

        # Log critical alert
        logger.critical(
            f"SECURITY ALERT: {alert_type} detected for user {user_id}. "
            f"Context: {context}"
        )

        # In production, this would also:
        # - Send notifications to security team
        # - Update SIEM system
        # - Potentially trigger automatic protective actions

    async def get_security_audit(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get comprehensive security audit report."""
        end_time = datetime.now()

        # Parse time range
        if time_range == "24h":
            start_time = end_time - timedelta(hours=24)
        elif time_range == "7d":
            start_time = end_time - timedelta(days=7)
        elif time_range == "30d":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(hours=24)

        # Collect audit data
        audit_report = {
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration": time_range
            },
            "summary": await self._generate_audit_summary(start_time, end_time),
            "security_events": await self._get_security_events(start_time, end_time),
            "threat_analysis": await self._analyze_threats(start_time, end_time),
            "recommendations": await self._generate_recommendations(start_time, end_time)
        }

        return audit_report

    async def _generate_audit_summary(self, start_time: datetime,
                                    end_time: datetime) -> Dict[str, Any]:
        """Generate high-level audit summary."""
        summary = {
            "total_events": 0,
            "unique_users": set(),
            "event_types": defaultdict(int),
            "high_risk_events": 0
        }

        current_date = start_time.date()
        end_date = end_time.date()

        while current_date <= end_date:
            date_str = current_date.strftime('%Y%m%d')

            # Check all event types for this date
            for event_type in ["auth_failed", "auth_success", "permission_denied",
                             "rate_limit_exceeded", "api_key_used"]:
                event_key = f"{self.audit_prefix}{event_type}:{date_str}"

                try:
                    events = self.redis_client.lrange(event_key, 0, -1)

                    for event_json in events:
                        event = json.loads(event_json)
                        event_time = datetime.fromisoformat(event["timestamp"])

                        if start_time <= event_time <= end_time:
                            summary["total_events"] += 1
                            summary["unique_users"].add(event["user_id"])
                            summary["event_types"][event_type] += 1

                            if event_type in ["auth_failed", "permission_denied",
                                            "rate_limit_exceeded"]:
                                summary["high_risk_events"] += 1

                except Exception as e:
                    logger.error(f"Error processing events for {date_str}: {e}")

            current_date += timedelta(days=1)

        summary["unique_users"] = len(summary["unique_users"])
        summary["event_types"] = dict(summary["event_types"])

        return summary

    async def _get_security_events(self, start_time: datetime,
                                 end_time: datetime) -> List[Dict[str, Any]]:
        """Get detailed security events for the time period."""
        events = []
        current_date = start_time.date()
        end_date = end_time.date()

        while current_date <= end_date and len(events) < 100:  # Limit results
            date_str = current_date.strftime('%Y%m%d')

            for event_type in ["auth_failed", "permission_denied", "rate_limit_exceeded"]:
                event_key = f"{self.audit_prefix}{event_type}:{date_str}"

                try:
                    event_list = self.redis_client.lrange(event_key, 0, -1)

                    for event_json in event_list:
                        if len(events) >= 100:
                            break

                        event = json.loads(event_json)
                        event_time = datetime.fromisoformat(event["timestamp"])

                        if start_time <= event_time <= end_time:
                            events.append(event)

                except Exception as e:
                    logger.error(f"Error retrieving events: {e}")

            current_date += timedelta(days=1)

        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x["timestamp"], reverse=True)

        return events

    async def _analyze_threats(self, start_time: datetime,
                             end_time: datetime) -> Dict[str, Any]:
        """Analyze threat patterns and risk levels."""
        analysis = {
            "risk_level": "low",
            "active_threats": [],
            "patterns_detected": [],
            "ip_analysis": defaultdict(int)
        }

        # Get recent security events
        events = await self._get_security_events(start_time, end_time)

        # Analyze IP addresses
        for event in events:
            ip = event.get("details", {}).get("ip_address", "unknown")
            analysis["ip_analysis"][ip] += 1

        # Identify suspicious IPs (multiple events from same IP)
        suspicious_ips = [ip for ip, count in analysis["ip_analysis"].items()
                         if count > 10]

        if suspicious_ips:
            analysis["active_threats"].append({
                "type": "suspicious_ip_activity",
                "details": suspicious_ips,
                "severity": "medium"
            })
            analysis["risk_level"] = "medium"

        # Check for unusual patterns
        failed_auth_count = len([e for e in events if e["event_type"] == "auth_failed"])
        if failed_auth_count > 50:
            analysis["patterns_detected"].append("high_failed_authentication_rate")
            analysis["risk_level"] = "high"

        return analysis

    async def _generate_recommendations(self, start_time: datetime,
                                      end_time: datetime) -> List[str]:
        """Generate security recommendations based on audit findings."""
        recommendations = []

        # Get audit summary for analysis
        summary = await self._generate_audit_summary(start_time, end_time)
        threat_analysis = await self._analyze_threats(start_time, end_time)

        # Analyze patterns and generate recommendations
        if summary["high_risk_events"] > 100:
            recommendations.append(
                "Consider implementing stricter rate limiting due to high number of security events"
            )

        if summary["event_types"].get("auth_failed", 0) > 50:
            recommendations.append(
                "Review authentication system - high number of failed attempts detected"
            )

        if threat_analysis["risk_level"] == "high":
            recommendations.append(
                "Immediate security review recommended - high-risk patterns detected"
            )

        if not recommendations:
            recommendations.append("Security posture appears normal - continue monitoring")

        return recommendations

# Integration with MCP Server
@mcp.tool()
@require_permission(Permission.VIEW_METRICS)
async def get_security_audit(time_range: str = "24h") -> Dict:
    """
    Get security audit information for the specified time range.

    Args:
        time_range: Time period to audit ("24h", "7d", "30d")

    Returns:
        Comprehensive security audit report
    """
    audit_system = SecurityAuditSystem(redis_client)
    return await audit_system.get_security_audit(time_range)
```

### Key Features Implemented

1. **Comprehensive Logging**: Tracks all security events with detailed metadata
2. **Threat Detection**: Identifies suspicious patterns in real-time
3. **Automated Alerting**: Triggers alerts for potential security incidents
4. **Audit Reporting**: Generates detailed security reports
5. **Risk Analysis**: Evaluates threat levels and provides recommendations

This security audit system provides comprehensive monitoring and analysis capabilities for MCP server security.

---

[Return to Session 5](Session5_Secure_MCP_Server.md)
---

## 🧭 Navigation

**Previous:** [Session 4 - Production MCP Deployment ←](Session4_Production_MCP_Deployment.md)
**Next:** [Session 6 - ACP Fundamentals →](Session6_ACP_Fundamentals.md)
---
