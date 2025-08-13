"""Security audit logging system for comprehensive monitoring."""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from enum import Enum


class SecurityEventType(Enum):
    """Types of security events to track."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    TOKEN_REVOKED = "token_revoked"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    API_KEY_USED = "api_key_used"
    INVALID_REQUEST = "invalid_request"


class SecurityAuditSystem:
    """Comprehensive security audit logging system."""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.logger = logging.getLogger("security_audit")
        self.event_prefix = "security_event:"
        self.metrics_prefix = "security_metrics:"
        
        # Setup audit logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [SECURITY] %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_security_event(self, event_type: SecurityEventType, 
                          user_id: str = None, details: Dict[str, Any] = None):
        """Log a security event with comprehensive context."""
        event_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "details": details or {},
            "severity": self._get_event_severity(event_type)
        }
        
        # Log to structured logger
        self.logger.info(json.dumps(event_data))
        
        # Store in Redis for analysis
        if self.redis_client:
            try:
                event_key = f"{self.event_prefix}{int(time.time())}"
                self.redis_client.setex(
                    event_key,
                    86400 * 7,  # Keep events for 7 days
                    json.dumps(event_data)
                )
                
                # Update metrics
                self._update_metrics(event_type, user_id)
                
            except Exception as e:
                self.logger.error(f"Failed to store security event: {e}")
    
    def _get_event_severity(self, event_type: SecurityEventType) -> str:
        """Determine severity level for event type."""
        high_severity = {
            SecurityEventType.LOGIN_FAILURE,
            SecurityEventType.PERMISSION_DENIED,
            SecurityEventType.SUSPICIOUS_ACTIVITY
        }
        
        medium_severity = {
            SecurityEventType.RATE_LIMIT_EXCEEDED,
            SecurityEventType.TOKEN_REVOKED,
            SecurityEventType.INVALID_REQUEST
        }
        
        if event_type in high_severity:
            return "HIGH"
        elif event_type in medium_severity:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _update_metrics(self, event_type: SecurityEventType, user_id: str):
        """Update security metrics counters."""
        try:
            # Global counter
            self.redis_client.incr(f"{self.metrics_prefix}{event_type.value}")
            
            # User-specific counter
            if user_id:
                self.redis_client.incr(
                    f"{self.metrics_prefix}user:{user_id}:{event_type.value}"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to update metrics: {e}")
    
    def get_security_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get security metrics for specified time range."""
        try:
            metrics = {}
            
            # Get event type counters
            for event_type in SecurityEventType:
                key = f"{self.metrics_prefix}{event_type.value}"
                count = self.redis_client.get(key) or 0
                metrics[event_type.value] = int(count)
            
            return {
                "time_range": time_range,
                "metrics": metrics,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get security metrics: {e}")
            return {"error": "Failed to retrieve metrics"}
    
    def detect_suspicious_activity(self, user_id: str) -> bool:
        """Detect suspicious activity patterns for a user."""
        try:
            # Check for excessive failed logins
            failed_logins = self.redis_client.get(
                f"{self.metrics_prefix}user:{user_id}:{SecurityEventType.LOGIN_FAILURE.value}"
            ) or 0
            
            if int(failed_logins) > 5:
                self.log_security_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    user_id,
                    {"reason": "excessive_failed_logins", "count": int(failed_logins)}
                )
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to detect suspicious activity: {e}")
            return False