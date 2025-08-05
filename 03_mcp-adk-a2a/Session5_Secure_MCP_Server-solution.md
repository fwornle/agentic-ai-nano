# Session 5: Secure MCP Server - Solution Guide

## 🧪 Multiple Choice Quiz - Answer Key

### Quick Check Questions

1. **Why do we use short-lived access tokens (30 minutes) instead of long-lived ones?**
   - A) To reduce server load
   - B) To limit exposure if tokens are compromised ✅ **CORRECT**
   - C) To improve performance
   - D) To simplify implementation

   **Explanation:** Short-lived tokens minimize the window of opportunity for attackers if a token is compromised. Even if stolen, the token will expire quickly, limiting potential damage.

2. **What is the purpose of token blacklisting?**
   - A) To improve token performance
   - B) To enable secure logout and token revocation ✅ **CORRECT**
   - C) To reduce memory usage
   - D) To simplify token validation

   **Explanation:** Token blacklisting allows us to immediately invalidate tokens when users log out or when we detect suspicious activity, even before the token's natural expiration.

3. **How does the token bucket rate limiter work?**
   - A) It counts requests per minute
   - B) It blocks all requests after a limit
   - C) It allows bursts but limits average rate ✅ **CORRECT**
   - D) It only limits failed requests

   **Explanation:** Token bucket allows short bursts of traffic (using accumulated tokens) while maintaining a sustainable average rate through token refill.

4. **Why do we hash API keys before storing them?**
   - A) To save storage space
   - B) To improve lookup performance
   - C) To prevent key theft from database breaches ✅ **CORRECT**
   - D) To enable key rotation

   **Explanation:** Hashing API keys ensures that even if the database is compromised, attackers cannot directly use the stored keys since they only have the hashes, not the original keys.

5. **What does "fail secure" mean in security systems?**
   - A) Always allow access when in doubt
   - B) Always deny access when systems fail ✅ **CORRECT**
   - C) Log all security events
   - D) Use multiple authentication methods

   **Explanation:** "Fail secure" means that when systems encounter errors or uncertainty, they should default to denying access rather than granting it, prioritizing security over availability.

---

## 💡 Practical Exercise Solution

**Challenge:** Implement a security audit system that tracks suspicious activity.

### Complete Solution:

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
            # Add to daily event list
            self.redis_client.lpush(event_key, json.dumps(event))
            self.redis_client.expire(event_key, 86400 * 30)  # 30 days retention
            
            # Update real-time metrics
            await self._update_metrics(event_type, user_id, event)
            
            # Check for threat patterns
            await self._analyze_threat_patterns(event)
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def get_security_audit(self, time_range: str = "24h") -> Dict:
        """
        Get comprehensive security audit information.
        
        Args:
            time_range: Time range for audit (1h, 24h, 7d, 30d)
            
        Returns:
            Security audit report with metrics and alerts
        """
        # Parse time range
        hours = self._parse_time_range(time_range)
        start_time = datetime.now() - timedelta(hours=hours)
        
        try:
            # Collect metrics from Redis
            audit_data = {
                "time_range": time_range,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "summary": await self._get_audit_summary(hours),
                "failed_authentications": await self._get_failed_auth_events(hours),
                "permission_denials": await self._get_permission_denial_events(hours),
                "rate_limit_violations": await self._get_rate_limit_events(hours),
                "unusual_access_patterns": await self._get_anomaly_events(hours),
                "top_threats": await self._get_top_threats(hours),
                "user_activity": await self._get_user_activity_summary(hours),
                "geographic_analysis": await self._get_geographic_analysis(hours)
            }
            
            return audit_data
            
        except Exception as e:
            logger.error(f"Failed to generate audit report: {e}")
            return {"error": "Failed to generate audit report"}
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours."""
        if time_range.endswith('h'):
            return int(time_range[:-1])
        elif time_range.endswith('d'):
            return int(time_range[:-1]) * 24
        else:
            return 24  # Default to 24 hours
    
    async def _get_audit_summary(self, hours: int) -> Dict:
        """Get high-level audit summary."""
        summary = {
            "total_events": 0,
            "failed_authentications": 0,
            "permission_denials": 0,
            "rate_limit_violations": 0,
            "unique_users": set(),
            "unique_ips": set(),
            "threat_level": "LOW"
        }
        
        # Count events by type
        event_types = ["auth_failed", "permission_denied", "rate_limit_exceeded", "anomaly_detected"]
        
        for event_type in event_types:
            events = await self._get_events_by_type(event_type, hours)
            
            for event in events:
                summary["total_events"] += 1
                summary["unique_users"].add(event.get("user_id", "unknown"))
                summary["unique_ips"].add(event.get("details", {}).get("ip_address", "unknown"))
                
                if event_type == "auth_failed":
                    summary["failed_authentications"] += 1
                elif event_type == "permission_denied":
                    summary["permission_denials"] += 1
                elif event_type == "rate_limit_exceeded":
                    summary["rate_limit_violations"] += 1
        
        # Determine threat level
        summary["threat_level"] = self._calculate_threat_level(summary)
        
        # Convert sets to counts
        summary["unique_users"] = len(summary["unique_users"])
        summary["unique_ips"] = len(summary["unique_ips"])
        
        return summary
    
    async def _get_events_by_type(self, event_type: str, hours: int) -> List[Dict]:
        """Get events of specific type within time range."""
        events = []
        current_time = datetime.now()
        
        # Check events for each day in the range
        for i in range((hours // 24) + 1):
            check_date = current_time - timedelta(days=i)
            event_key = f"{self.audit_prefix}{event_type}:{check_date.strftime('%Y%m%d')}"
            
            try:
                event_list = self.redis_client.lrange(event_key, 0, -1)
                for event_json in event_list:
                    event = json.loads(event_json)
                    event_time = datetime.fromisoformat(event["timestamp"])
                    
                    # Filter by actual time range
                    if event_time >= (current_time - timedelta(hours=hours)):
                        events.append(event)
                        
            except Exception as e:
                logger.warning(f"Error retrieving events for {event_key}: {e}")
        
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)
    
    async def _analyze_threat_patterns(self, event: Dict):
        """Analyze event patterns for threat detection."""
        event_type = event["event_type"]
        user_id = event["user_id"]
        ip_address = event["details"].get("ip_address")
        
        # Track failed authentication attempts
        if event_type == "auth_failed":
            await self._track_failed_auth_pattern(user_id, ip_address)
        
        # Track permission abuse
        elif event_type == "permission_denied":
            await self._track_permission_abuse_pattern(user_id, ip_address)
        
        # Track rate limiting patterns
        elif event_type == "rate_limit_exceeded":
            await self._track_rate_limit_pattern(user_id, ip_address)
    
    async def _track_failed_auth_pattern(self, user_id: str, ip_address: str):
        """Track patterns of failed authentication attempts."""
        window_key = f"pattern:auth_failed:{user_id}:{datetime.now().strftime('%Y%m%d%H')}"
        
        try:
            count = self.redis_client.incr(window_key)
            self.redis_client.expire(window_key, 3600)  # 1 hour expiry
            
            if count >= self.thresholds["failed_auth_attempts"]:
                await self._trigger_security_alert(
                    "BRUTE_FORCE_ATTEMPT",
                    f"User {user_id} from IP {ip_address} has {count} failed auth attempts in 1 hour"
                )
                
        except Exception as e:
            logger.error(f"Error tracking auth pattern: {e}")
    
    async def _track_permission_abuse_pattern(self, user_id: str, ip_address: str):
        """Track patterns of permission violations."""
        window_key = f"pattern:perm_denied:{user_id}:{datetime.now().strftime('%Y%m%d%H')}"
        
        try:
            count = self.redis_client.incr(window_key)
            self.redis_client.expire(window_key, 3600)
            
            if count >= self.thresholds["permission_denials"]:
                await self._trigger_security_alert(
                    "PRIVILEGE_ESCALATION_ATTEMPT",
                    f"User {user_id} has {count} permission denials in 1 hour"
                )
                
        except Exception as e:
            logger.error(f"Error tracking permission pattern: {e}")
    
    async def _trigger_security_alert(self, alert_type: str, message: str):
        """Trigger a security alert."""
        alert = {
            "alert_type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "severity": "HIGH"
        }
        
        # Store alert
        alert_key = f"alerts:{datetime.now().strftime('%Y%m%d')}"
        self.redis_client.lpush(alert_key, json.dumps(alert))
        self.redis_client.expire(alert_key, 86400 * 7)  # 7 days retention
        
        # Log alert
        logger.warning(f"SECURITY ALERT: {alert_type} - {message}")
        
        # In production, you would send notifications here
        # await self._send_alert_notification(alert)
    
    def _calculate_threat_level(self, summary: Dict) -> str:
        """Calculate overall threat level based on metrics."""
        score = 0
        
        # Weight different threat indicators
        score += summary["failed_authentications"] * 0.3
        score += summary["permission_denials"] * 0.2
        score += summary["rate_limit_violations"] * 0.1
        
        # Determine threat level
        if score >= 50:
            return "CRITICAL"
        elif score >= 20:
            return "HIGH"
        elif score >= 10:
            return "MEDIUM"
        else:
            return "LOW"

# Integration with MCP Server
@mcp.tool()
@require_permission(Permission.VIEW_METRICS)
async def get_security_audit(time_range: str = "24h") -> Dict:
    """
    Get security audit information for the specified time range.
    
    This tool provides comprehensive security metrics including:
    - Failed authentication attempts
    - Permission denied events
    - Rate limit violations
    - Unusual access patterns
    - Threat level assessment
    
    Args:
        time_range: Time range for audit (1h, 24h, 7d, 30d)
        
    Returns:
        Security audit report with metrics and alerts
    """
    audit_system = SecurityAuditSystem(redis_client)
    return await audit_system.get_security_audit(time_range)

@mcp.tool()
@require_permission(Permission.ADMIN_USERS)
async def get_threat_alerts(severity: str = "HIGH") -> List[Dict]:
    """
    Get current threat alerts filtered by severity.
    
    Args:
        severity: Minimum severity level (LOW, MEDIUM, HIGH, CRITICAL)
        
    Returns:
        List of active security alerts
    """
    alerts = []
    
    try:
        # Get alerts from the last 7 days
        for i in range(7):
            check_date = datetime.now() - timedelta(days=i)
            alert_key = f"alerts:{check_date.strftime('%Y%m%d')}"
            
            alert_list = redis_client.lrange(alert_key, 0, -1)
            for alert_json in alert_list:
                alert = json.loads(alert_json)
                
                # Filter by severity
                if _severity_level(alert["severity"]) >= _severity_level(severity):
                    alerts.append(alert)
        
        return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)
        
    except Exception as e:
        logger.error(f"Error retrieving threat alerts: {e}")
        return []

def _severity_level(severity: str) -> int:
    """Convert severity string to numeric level."""
    levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    return levels.get(severity, 1)

# Example usage and testing
async def demo_security_audit():
    """Demonstrate the security audit system."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    # Get security audit
    audit_data = await get_security_audit("24h")
    
    # Display summary
    summary = audit_data["summary"]
    
    summary_table = Table(title="Security Audit Summary (24h)")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="yellow")
    
    summary_table.add_row("Total Events", str(summary["total_events"]))
    summary_table.add_row("Failed Authentications", str(summary["failed_authentications"]))
    summary_table.add_row("Permission Denials", str(summary["permission_denials"]))
    summary_table.add_row("Rate Limit Violations", str(summary["rate_limit_violations"]))
    summary_table.add_row("Unique Users", str(summary["unique_users"]))
    summary_table.add_row("Unique IPs", str(summary["unique_ips"]))
    summary_table.add_row("Threat Level", summary["threat_level"])
    
    console.print(summary_table)
    
    # Display recent alerts
    alerts = await get_threat_alerts("MEDIUM")
    if alerts:
        console.print("\n🚨 Recent Security Alerts:")
        for alert in alerts[:5]:
            alert_panel = Panel(
                f"[red]{alert['alert_type']}[/red]\n{alert['message']}\n[dim]{alert['timestamp']}[/dim]",
                border_style="red"
            )
            console.print(alert_panel)

if __name__ == "__main__":
    asyncio.run(demo_security_audit())
```

### Key Features Implemented:

1. **Comprehensive Event Tracking**: Logs all security-related events with detailed metadata
2. **Pattern Analysis**: Detects suspicious patterns like brute force attacks and privilege escalation attempts
3. **Threat Level Assessment**: Calculates overall security threat level based on multiple indicators
4. **Real-time Alerting**: Triggers alerts when suspicious patterns are detected
5. **Flexible Reporting**: Provides audit reports for different time ranges with detailed breakdowns

### Advanced Extensions:

```python
# Additional security features you could implement:

class AdvancedThreatDetection:
    """Advanced threat detection using machine learning."""
    
    def __init__(self):
        # In production, you might use scikit-learn or similar
        self.anomaly_threshold = 0.7
    
    def detect_anomaly(self, user_behavior: Dict) -> float:
        """Detect anomalous user behavior using statistical analysis."""
        # Analyze factors like:
        # - Time of access patterns
        # - Geographical location changes
        # - Tool usage patterns
        # - Request frequency variations
        
        anomaly_score = 0.0
        
        # Time-based anomaly (accessing at unusual hours)
        if self._is_unusual_time(user_behavior.get("access_time")):
            anomaly_score += 0.3
        
        # Location-based anomaly (access from new location)
        if self._is_new_location(user_behavior.get("ip_address")):
            anomaly_score += 0.4
        
        # Usage pattern anomaly (unusual tool combinations)
        if self._is_unusual_tool_usage(user_behavior.get("tools_used", [])):
            anomaly_score += 0.3
        
        return anomaly_score
    
    def _is_unusual_time(self, access_time: str) -> bool:
        """Check if access time is unusual for the user."""
        # Implementation would analyze historical access patterns
        return False
    
    def _is_new_location(self, ip_address: str) -> bool:
        """Check if IP address represents a new geographical location."""
        # Implementation would use GeoIP data
        return False
    
    def _is_unusual_tool_usage(self, tools_used: List[str]) -> bool:
        """Check if tool usage pattern is unusual."""
        # Implementation would analyze historical tool usage
        return False

# Automated response system
class AutomatedSecurityResponse:
    """Automated security response system."""
    
    async def respond_to_threat(self, threat_type: str, severity: str, context: Dict):
        """Automatically respond to detected threats."""
        
        if threat_type == "BRUTE_FORCE_ATTEMPT":
            await self._handle_brute_force(context)
        elif threat_type == "PRIVILEGE_ESCALATION_ATTEMPT":
            await self._handle_privilege_escalation(context)
        elif threat_type == "ANOMALY_DETECTED":
            await self._handle_anomaly(context)
    
    async def _handle_brute_force(self, context: Dict):
        """Handle brute force attack attempts."""
        user_id = context.get("user_id")
        ip_address = context.get("ip_address")
        
        # Temporarily disable user account
        await self._disable_user_temporarily(user_id, duration_minutes=15)
        
        # Block IP address temporarily
        await self._block_ip_temporarily(ip_address, duration_minutes=60)
        
        # Send notification to security team
        await self._notify_security_team(f"Brute force detected: {user_id} from {ip_address}")
```

### Testing Scenarios:

1. **Brute Force Attack**: Simulate multiple failed login attempts from the same IP
2. **Privilege Escalation**: Test user attempting to access admin-only functions
3. **Rate Limit Abuse**: Generate high-frequency requests to trigger rate limiting
4. **Geographical Anomaly**: Simulate access from unusual locations
5. **Time Anomaly**: Test access during unusual hours for a user

This comprehensive security audit system provides the foundation for a robust security monitoring and response capability in your MCP servers.