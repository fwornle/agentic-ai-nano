# ⚙️ Session 5 Advanced: Security Monitoring & Audit Systems

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths
> Time Investment: 3-4 hours
> Outcome: Master comprehensive security monitoring and audit systems

## Advanced Learning Outcomes

After completing this module, you will master:

- Real-time security event detection and alerting  
- Comprehensive audit logging with tamper-proof storage  
- Advanced threat detection using machine learning  
- Compliance monitoring and automated reporting  

## Enterprise Security Monitoring Architecture

Think of security monitoring as having an army of digital sentries who never sleep, never blink, and remember everything. They watch every entrance, monitor every transaction, and instantly alert you to any suspicious activity.

### Real-Time Security Event Detection

The security monitoring system processes events in real-time to detect threats as they emerge:

```python
# src/security/monitoring.py

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac
import redis
from kafka import KafkaProducer, KafkaConsumer
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    """Types of security events we monitor."""
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_DENIED = "authz_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    TOKEN_MISUSE = "token_misuse"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    SYSTEM_ANOMALY = "system_anomaly"

class SecuritySeverity(Enum):
    """Security event severity levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class SecurityEvent:
    """Comprehensive security event record."""
    event_id: str
    event_type: SecurityEventType
    severity: SecuritySeverity
    timestamp: datetime
    source_ip: str
    user_id: Optional[str]
    session_id: Optional[str]
    resource: str
    action: str
    success: bool
    metadata: Dict[str, Any]
    risk_score: float
    detection_rules: List[str]

class SecurityMonitoringEngine:
    """Real-time security monitoring and threat detection engine."""

    def __init__(self, config: Dict[str, Any]):
        self.redis_client = redis.Redis(**config["redis"])
        self.kafka_producer = KafkaProducer(
            **config["kafka"],
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')
        )

        # Monitoring configuration
        self.event_retention_days = config.get("event_retention_days", 90)
        self.alert_thresholds = config.get("alert_thresholds", self._default_thresholds())
        self.ml_models = {}

        # Initialize threat detection models
        self._initialize_ml_models()

        # Real-time event processing
        self.event_processors = {
            SecurityEventType.AUTHENTICATION_FAILURE: self._process_auth_failure,
            SecurityEventType.RATE_LIMIT_EXCEEDED: self._process_rate_limit_violation,
            SecurityEventType.SUSPICIOUS_PATTERN: self._process_suspicious_pattern,
            SecurityEventType.TOKEN_MISUSE: self._process_token_misuse
        }
```

The architecture uses Kafka for real-time event streaming and Redis for fast pattern detection.

### Advanced Threat Detection Using Machine Learning

Machine learning models analyze behavior patterns to detect sophisticated attacks:

```python
    def _initialize_ml_models(self):
        """Initialize machine learning models for threat detection."""

        # Anomaly detection model for user behavior
        self.ml_models["user_behavior"] = IsolationForest(
            contamination=0.1,  # Expect 10% anomalous behavior
            random_state=42
        )

        # Pattern detection for request sequences
        self.ml_models["request_patterns"] = IsolationForest(
            contamination=0.05,  # More conservative for request patterns
            random_state=42
        )

        # Initialize with baseline training data
        asyncio.create_task(self._train_baseline_models())

    async def _train_baseline_models(self):
        """Train ML models with historical baseline data."""
        try:
            # Get historical normal behavior data
            baseline_data = await self._get_baseline_training_data()

            if baseline_data and len(baseline_data) > 100:  # Need sufficient data
                # Train user behavior model
                user_features = self._extract_user_behavior_features(baseline_data)
                if len(user_features) > 50:
                    self.ml_models["user_behavior"].fit(user_features)
                    logger.info("User behavior anomaly model trained successfully")

                # Train request pattern model
                request_features = self._extract_request_pattern_features(baseline_data)
                if len(request_features) > 50:
                    self.ml_models["request_patterns"].fit(request_features)
                    logger.info("Request pattern anomaly model trained successfully")

        except Exception as e:
            logger.error(f"Failed to train baseline ML models: {e}")

    async def process_security_event(self, raw_event: Dict[str, Any]) -> SecurityEvent:
        """Process incoming security event with comprehensive analysis."""

        # Step 1: Create structured security event
        security_event = self._create_security_event(raw_event)

        # Step 2: Calculate risk score using multiple algorithms
        risk_score = await self._calculate_comprehensive_risk_score(security_event)
        security_event.risk_score = risk_score

        # Step 3: Apply ML-based threat detection
        ml_insights = await self._apply_ml_threat_detection(security_event)
        security_event.metadata.update(ml_insights)

        # Step 4: Check against known attack patterns
        pattern_matches = await self._check_attack_patterns(security_event)
        security_event.detection_rules.extend(pattern_matches)

        # Step 5: Store event for analysis and alerting
        await self._store_security_event(security_event)

        # Step 6: Generate alerts if thresholds exceeded
        await self._evaluate_alert_conditions(security_event)

        # Step 7: Update threat intelligence
        await self._update_threat_intelligence(security_event)

        return security_event
```

Multi-layered analysis combines rule-based detection with machine learning for comprehensive threat identification.

### Comprehensive Risk Score Calculation

The risk scoring system evaluates multiple factors to assess threat levels:

```python
    async def _calculate_comprehensive_risk_score(self, event: SecurityEvent) -> float:
        """Calculate comprehensive risk score for security event."""

        base_scores = {
            SecurityEventType.AUTHENTICATION_FAILURE: 3.0,
            SecurityEventType.AUTHORIZATION_DENIED: 4.0,
            SecurityEventType.RATE_LIMIT_EXCEEDED: 2.0,
            SecurityEventType.TOKEN_MISUSE: 8.0,
            SecurityEventType.PRIVILEGE_ESCALATION: 9.0,
            SecurityEventType.DATA_EXFILTRATION: 10.0
        }

        base_score = base_scores.get(event.event_type, 1.0)

        # Factor 1: IP reputation and geolocation risk
        ip_risk = await self._calculate_ip_risk(event.source_ip)

        # Factor 2: User behavior deviation
        user_risk = await self._calculate_user_behavior_risk(event.user_id, event)

        # Factor 3: Temporal patterns (time-based anomalies)
        temporal_risk = self._calculate_temporal_risk(event.timestamp)

        # Factor 4: Resource sensitivity
        resource_risk = await self._calculate_resource_sensitivity_risk(event.resource)

        # Factor 5: Historical context
        historical_risk = await self._calculate_historical_context_risk(event)

        # Weighted composite score
        composite_score = (
            base_score * 0.3 +           # 30% base event type
            ip_risk * 0.2 +              # 20% IP reputation
            user_risk * 0.25 +           # 25% user behavior
            temporal_risk * 0.1 +        # 10% timing anomalies
            resource_risk * 0.1 +        # 10% resource sensitivity
            historical_risk * 0.05       # 5% historical context
        )

        # Normalize to 0-10 scale
        normalized_score = min(10.0, max(0.0, composite_score))

        return round(normalized_score, 2)

    async def _calculate_ip_risk(self, ip_address: str) -> float:
        """Calculate risk score based on IP address characteristics."""

        try:
            # Check IP reputation databases
            reputation_score = await self._check_ip_reputation(ip_address)

            # Check geolocation risk
            geo_risk = await self._calculate_geolocation_risk(ip_address)

            # Check if IP is from known bad networks
            network_risk = await self._check_network_reputation(ip_address)

            # Historical behavior of this IP
            historical_ip_risk = await self._calculate_ip_historical_risk(ip_address)

            return min(10.0, reputation_score + geo_risk + network_risk + historical_ip_risk)

        except Exception as e:
            logger.warning(f"IP risk calculation failed for {ip_address}: {e}")
            return 1.0  # Default low risk if calculation fails

    async def _calculate_user_behavior_risk(self, user_id: Optional[str],
                                          event: SecurityEvent) -> float:
        """Calculate risk based on user behavior patterns."""

        if not user_id:
            return 2.0  # Anonymous users get moderate risk

        try:
            # Get recent user behavior history
            behavior_history = await self._get_user_behavior_history(user_id, hours=24)

            if not behavior_history:
                return 1.0  # New users get low risk initially

            # Extract behavior features
            features = self._extract_user_behavior_features([{
                "user_id": user_id,
                "timestamp": event.timestamp,
                "resource": event.resource,
                "action": event.action,
                "source_ip": event.source_ip,
                "success": event.success
            }])

            # Use ML model to detect anomalies
            if "user_behavior" in self.ml_models and features:
                anomaly_score = self.ml_models["user_behavior"].score_samples([features[0]])
                # Convert to risk score (lower anomaly score = higher risk)
                risk_score = max(0, (1.0 - anomaly_score[0]) * 10)
                return min(10.0, risk_score)

            # Fallback: rule-based behavior analysis
            return self._calculate_rule_based_behavior_risk(behavior_history, event)

        except Exception as e:
            logger.warning(f"User behavior risk calculation failed for {user_id}: {e}")
            return 1.0
```

The multi-factor risk calculation provides nuanced threat assessment beyond simple rule matching.

### Advanced Attack Pattern Detection

Detect sophisticated attack patterns across multiple events and timeframes:

```python
class AttackPatternDetector:
    """Advanced detection of complex attack patterns."""

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.pattern_definitions = self._load_attack_patterns()

    def _load_attack_patterns(self) -> Dict[str, Dict]:
        """Load attack pattern definitions."""
        return {
            "credential_stuffing": {
                "description": "Automated credential testing across multiple accounts",
                "indicators": [
                    {"event_type": "auth_failure", "min_count": 10, "time_window": 300},
                    {"source_diversity": {"min_users": 5, "max_success_rate": 0.1}},
                    {"temporal_pattern": {"regular_intervals": True, "burst_behavior": True}}
                ],
                "severity": SecuritySeverity.HIGH,
                "confidence_threshold": 0.8
            },

            "privilege_escalation_chain": {
                "description": "Sequential privilege escalation attempts",
                "indicators": [
                    {"event_sequence": ["authz_denied", "auth_failure", "authz_denied"]},
                    {"resource_progression": {"increasing_sensitivity": True}},
                    {"time_correlation": {"max_interval": 600}}
                ],
                "severity": SecuritySeverity.CRITICAL,
                "confidence_threshold": 0.9
            },

            "data_exfiltration_pattern": {
                "description": "Systematic data access and extraction",
                "indicators": [
                    {"resource_access": {"volume_threshold": 100, "diversity_threshold": 10}},
                    {"temporal_pattern": {"sustained_activity": True, "off_hours": True}},
                    {"data_sensitivity": {"high_value_resources": True}}
                ],
                "severity": SecuritySeverity.CRITICAL,
                "confidence_threshold": 0.85
            }
        }

    async def detect_attack_patterns(self, event: SecurityEvent) -> List[Dict[str, Any]]:
        """Detect complex attack patterns involving current event."""

        detected_patterns = []

        for pattern_name, pattern_def in self.pattern_definitions.items():
            try:
                # Check if event could be part of this attack pattern
                if self._event_matches_pattern_context(event, pattern_def):

                    # Analyze pattern indicators
                    confidence = await self._analyze_pattern_indicators(event, pattern_def)

                    if confidence >= pattern_def["confidence_threshold"]:
                        detected_patterns.append({
                            "pattern_name": pattern_name,
                            "description": pattern_def["description"],
                            "confidence": confidence,
                            "severity": pattern_def["severity"],
                            "indicators_matched": await self._get_matched_indicators(event, pattern_def),
                            "recommended_actions": self._get_recommended_actions(pattern_name)
                        })

            except Exception as e:
                logger.error(f"Pattern detection failed for {pattern_name}: {e}")

        return detected_patterns

    async def _analyze_pattern_indicators(self, event: SecurityEvent,
                                        pattern_def: Dict) -> float:
        """Analyze how well event matches pattern indicators."""

        total_score = 0.0
        max_score = 0.0

        for indicator in pattern_def["indicators"]:
            indicator_score, indicator_max = await self._evaluate_indicator(event, indicator)
            total_score += indicator_score
            max_score += indicator_max

        confidence = (total_score / max_score) if max_score > 0 else 0.0
        return min(1.0, confidence)

    async def _evaluate_indicator(self, event: SecurityEvent,
                                 indicator: Dict) -> tuple[float, float]:
        """Evaluate specific pattern indicator."""

        if "event_type" in indicator:
            return await self._evaluate_event_type_indicator(event, indicator)
        elif "source_diversity" in indicator:
            return await self._evaluate_source_diversity_indicator(event, indicator)
        elif "temporal_pattern" in indicator:
            return await self._evaluate_temporal_pattern_indicator(event, indicator)
        elif "event_sequence" in indicator:
            return await self._evaluate_sequence_indicator(event, indicator)
        elif "resource_access" in indicator:
            return await self._evaluate_resource_access_indicator(event, indicator)

        return 0.0, 1.0  # Default: no match, full weight
```

Sophisticated pattern detection identifies multi-stage attacks that span multiple events and timeframes.

### Tamper-Proof Audit Logging

Implement cryptographically secure audit logging that ensures integrity:

```python
class TamperProofAuditLogger:
    """Cryptographically secure audit logging system."""

    def __init__(self, config: Dict[str, Any]):
        self.signing_key = config["audit_signing_key"].encode()
        self.encryption_key = config.get("audit_encryption_key", "").encode()
        self.storage_backend = config["storage_backend"]
        self.chain_integrity = True

        # Initialize audit chain
        self.last_hash = self._get_last_audit_hash()

    async def log_audit_event(self, event_type: str, details: Dict[str, Any],
                             user_context: Optional[Dict[str, Any]] = None) -> str:
        """Log audit event with cryptographic integrity protection."""

        # Create comprehensive audit record
        audit_record = {
            "audit_id": self._generate_audit_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "user_context": user_context,
            "system_context": self._get_system_context(),
            "previous_hash": self.last_hash
        }

        # Calculate integrity hash
        record_hash = self._calculate_record_hash(audit_record)
        audit_record["record_hash"] = record_hash

        # Create digital signature
        signature = self._create_digital_signature(audit_record)
        audit_record["signature"] = signature

        # Encrypt sensitive data if required
        if self.encryption_key and self._should_encrypt(event_type):
            audit_record = self._encrypt_sensitive_data(audit_record)

        # Store with integrity checking
        storage_result = await self._store_audit_record(audit_record)

        # Update chain hash for next record
        self.last_hash = record_hash

        # Verify chain integrity periodically
        if self._should_verify_chain():
            asyncio.create_task(self._verify_audit_chain_integrity())

        return audit_record["audit_id"]

    def _calculate_record_hash(self, record: Dict[str, Any]) -> str:
        """Calculate cryptographic hash for audit record."""

        # Create canonical representation
        canonical_data = json.dumps(
            {k: v for k, v in record.items() if k not in ["record_hash", "signature"]},
            sort_keys=True,
            separators=(',', ':')
        )

        # Include previous hash for chaining
        hash_input = f"{canonical_data}:{record.get('previous_hash', '')}"

        # Calculate SHA-256 hash
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def _create_digital_signature(self, record: Dict[str, Any]) -> str:
        """Create HMAC signature for audit record."""

        # Create signature over the complete record including hash
        message = json.dumps(record, sort_keys=True, separators=(',', ':')).encode()
        signature = hmac.new(self.signing_key, message, hashlib.sha256).hexdigest()

        return signature

    async def verify_audit_record(self, audit_id: str) -> Dict[str, Any]:
        """Verify integrity of specific audit record."""

        try:
            # Retrieve record from storage
            record = await self._retrieve_audit_record(audit_id)
            if not record:
                return {"valid": False, "reason": "record_not_found"}

            # Verify digital signature
            stored_signature = record.pop("signature", "")
            calculated_signature = self._create_digital_signature(record)

            if not hmac.compare_digest(stored_signature, calculated_signature):
                return {"valid": False, "reason": "signature_verification_failed"}

            # Verify record hash
            stored_hash = record.get("record_hash", "")
            calculated_hash = self._calculate_record_hash(record)

            if stored_hash != calculated_hash:
                return {"valid": False, "reason": "hash_verification_failed"}

            return {
                "valid": True,
                "audit_id": audit_id,
                "timestamp": record.get("timestamp"),
                "verification_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Audit verification failed for {audit_id}: {e}")
            return {"valid": False, "reason": "verification_error", "error": str(e)}
```

Cryptographic integrity protection ensures audit logs cannot be tampered with undetected.

### Compliance Monitoring and Automated Reporting

Generate compliance reports automatically for various security frameworks:

```python
class ComplianceMonitor:
    """Automated compliance monitoring and reporting system."""

    def __init__(self, audit_logger: TamperProofAuditLogger):
        self.audit_logger = audit_logger
        self.compliance_frameworks = {
            "SOC2": self._load_soc2_requirements(),
            "ISO27001": self._load_iso27001_requirements(),
            "GDPR": self._load_gdpr_requirements(),
            "PCI_DSS": self._load_pci_dss_requirements()
        }

    async def generate_compliance_report(self, framework: str,
                                        time_range: str = "30d") -> Dict[str, Any]:
        """Generate comprehensive compliance report."""

        if framework not in self.compliance_frameworks:
            raise ValueError(f"Unsupported compliance framework: {framework}")

        requirements = self.compliance_frameworks[framework]

        # Analyze compliance for each requirement
        compliance_results = {}
        overall_score = 0.0

        for req_id, requirement in requirements.items():
            result = await self._assess_compliance_requirement(requirement, time_range)
            compliance_results[req_id] = result
            overall_score += result["score"]

        overall_score = overall_score / len(requirements) if requirements else 0

        # Generate executive summary
        summary = self._generate_compliance_summary(compliance_results, overall_score)

        # Create detailed report
        report = {
            "framework": framework,
            "generation_time": datetime.utcnow().isoformat(),
            "time_range": time_range,
            "overall_score": round(overall_score, 2),
            "compliance_status": "COMPLIANT" if overall_score >= 0.85 else "NON_COMPLIANT",
            "executive_summary": summary,
            "detailed_results": compliance_results,
            "recommendations": self._generate_compliance_recommendations(compliance_results)
        }

        return report
```

Automated compliance monitoring ensures continuous adherence to security frameworks.
---

## 🧭 Navigation

**Previous:** [Session 4 - Production MCP Deployment ←](Session4_Production_MCP_Deployment.md)
**Next:** [Session 6 - ACP Fundamentals →](Session6_ACP_Fundamentals.md)
---
