# Session 8 - Module D: Security & Compliance (45 minutes)

**Prerequisites**: [Session 8 Core Section Complete](Session8_Agno_Production_Ready_Agents.md)  
**Target Audience**: Security engineers and compliance specialists  
**Cognitive Load**: 4 security concepts

---

## 🎯 Module Overview

This module explores enterprise security and compliance frameworks for Agno agent systems including zero-trust architecture, data encryption, audit logging, privacy controls, and regulatory compliance (GDPR, HIPAA, SOC2). You'll learn to build security-first agent systems that meet enterprise compliance requirements.

### Learning Objectives
By the end of this module, you will:
- Implement zero-trust security architecture for agent communications
- Design comprehensive data encryption and privacy protection systems
- Create audit logging and compliance monitoring frameworks
- Build regulatory compliance systems for GDPR, HIPAA, and SOC2 requirements

---

## Part 1: Zero-Trust Security Architecture (20 minutes)

### Comprehensive Security Framework

🗂️ **File**: `src/session8/security_architecture.py` - Zero-trust security implementation

```python
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import hashlib
import jwt
import logging
from enum import Enum
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecurityLevel(Enum):
    """Security clearance levels for agent operations"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

class AuthenticationMethod(Enum):
    """Authentication methods supported"""
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    OAUTH2 = "oauth2"
    MUTUAL_TLS = "mutual_tls"
    CERTIFICATE = "certificate"

@dataclass
class SecurityContext:
    """Security context for agent operations"""
    user_id: str
    session_id: str
    security_level: SecurityLevel
    authentication_method: AuthenticationMethod
    permissions: List[str] = field(default_factory=list)
    data_classification: str = "internal"
    audit_required: bool = True
    encryption_required: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

class ZeroTrustSecurityManager:
    """Zero-trust security manager for agent systems"""
    
    def __init__(self, encryption_key: bytes = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.security_policies = {}
        self.active_sessions = {}
        self.audit_logger = logging.getLogger("security_audit")
        self.threat_detection = ThreatDetectionSystem()
        
    def setup_security_policies(self) -> Dict[str, Any]:
        """Configure comprehensive security policies"""
        
        security_config = {
            "authentication": {
                "session_timeout_minutes": 60,
                "max_concurrent_sessions": 5,
                "password_policy": {
                    "min_length": 12,
                    "require_special_chars": True,
                    "require_numbers": True,
                    "require_uppercase": True,
                    "history_count": 12
                },
                "mfa_required": True,
                "certificate_validation": True
            },
            
            "authorization": {
                "rbac_enabled": True,
                "attribute_based_access": True,
                "dynamic_permissions": True,
                "principle_of_least_privilege": True,
                "permission_inheritance": False
            },
            
            "encryption": {
                "data_at_rest": {
                    "algorithm": "AES-256-GCM",
                    "key_rotation_days": 90,
                    "encrypted_fields": [
                        "conversation_content",
                        "user_data", 
                        "agent_responses",
                        "tool_parameters"
                    ]
                },
                "data_in_transit": {
                    "tls_version": "1.3",
                    "cipher_suites": [
                        "TLS_AES_256_GCM_SHA384",
                        "TLS_CHACHA20_POLY1305_SHA256"
                    ],
                    "certificate_pinning": True
                }
            },
            
            "audit_logging": {
                "enabled": True,
                "log_level": "INFO",
                "retention_days": 2555,  # 7 years
                "real_time_monitoring": True,
                "log_integrity_checking": True,
                "log_events": [
                    "authentication_attempts",
                    "authorization_decisions",
                    "data_access",
                    "configuration_changes",
                    "security_incidents"
                ]
            },
            
            "threat_detection": {
                "enabled": True,
                "behavioral_analysis": True,
                "anomaly_detection": True,
                "real_time_alerts": True,
                "threat_intelligence": True
            }
        }
        
        self.security_policies = security_config
        return security_config
    
    async def authenticate_request(self, request_data: Dict[str, Any]) -> SecurityContext:
        """Authenticate and authorize agent requests with zero-trust principles"""
        
        # Extract authentication credentials
        auth_header = request_data.get("authorization")
        api_key = request_data.get("api_key")
        client_cert = request_data.get("client_certificate")
        
        if not auth_header and not api_key and not client_cert:
            raise SecurityException("No authentication credentials provided")
        
        # Determine authentication method
        auth_method = self._determine_auth_method(request_data)
        
        # Perform authentication
        user_identity = await self._authenticate_identity(request_data, auth_method)
        
        # Create security context
        security_context = SecurityContext(
            user_id=user_identity["user_id"],
            session_id=self._generate_session_id(),
            security_level=SecurityLevel(user_identity.get("security_level", "internal")),
            authentication_method=auth_method,
            permissions=user_identity.get("permissions", []),
            data_classification=user_identity.get("data_classification", "internal")
        )
        
        # Verify authorization
        await self._authorize_request(security_context, request_data)
        
        # Log security event
        await self._log_security_event("authentication_success", {
            "user_id": security_context.user_id,
            "auth_method": auth_method.value,
            "source_ip": request_data.get("source_ip"),
            "user_agent": request_data.get("user_agent")
        })
        
        # Store active session
        self.active_sessions[security_context.session_id] = security_context
        
        return security_context
    
    async def _authenticate_identity(self, request_data: Dict[str, Any], 
                                   auth_method: AuthenticationMethod) -> Dict[str, Any]:
        """Authenticate user identity based on method"""
        
        if auth_method == AuthenticationMethod.JWT_TOKEN:
            return await self._authenticate_jwt(request_data.get("authorization"))
        elif auth_method == AuthenticationMethod.API_KEY:
            return await self._authenticate_api_key(request_data.get("api_key"))
        elif auth_method == AuthenticationMethod.MUTUAL_TLS:
            return await self._authenticate_mtls(request_data.get("client_certificate"))
        else:
            raise SecurityException(f"Unsupported authentication method: {auth_method}")
    
    async def _authenticate_jwt(self, auth_header: str) -> Dict[str, Any]:
        """Authenticate JWT token"""
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
            
            # Decode and validate JWT
            decoded_token = jwt.decode(
                token, 
                self._get_jwt_secret(),
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            
            # Additional validation
            if not decoded_token.get("user_id"):
                raise SecurityException("Invalid token: missing user_id")
            
            if datetime.now() > datetime.fromtimestamp(decoded_token.get("exp", 0)):
                raise SecurityException("Token expired")
            
            return {
                "user_id": decoded_token["user_id"],
                "permissions": decoded_token.get("permissions", []),
                "security_level": decoded_token.get("security_level", "internal"),
                "data_classification": decoded_token.get("data_classification", "internal")
            }
            
        except jwt.InvalidTokenError as e:
            raise SecurityException(f"JWT authentication failed: {str(e)}")
    
    async def _authorize_request(self, security_context: SecurityContext, 
                               request_data: Dict[str, Any]):
        """Authorize request based on security context and policies"""
        
        requested_action = request_data.get("action", "unknown")
        requested_resource = request_data.get("resource", "unknown")
        
        # Check if user has required permissions
        required_permission = f"{requested_action}:{requested_resource}"
        
        if required_permission not in security_context.permissions and "admin:*" not in security_context.permissions:
            await self._log_security_event("authorization_denied", {
                "user_id": security_context.user_id,
                "requested_permission": required_permission,
                "user_permissions": security_context.permissions
            })
            raise SecurityException(f"Access denied: insufficient permissions for {required_permission}")
        
        # Check security level requirements
        resource_security_level = self._get_resource_security_level(requested_resource)
        if security_context.security_level.value < resource_security_level.value:
            raise SecurityException(f"Access denied: insufficient security clearance")
        
        # Additional context-based checks
        await self._perform_contextual_authorization(security_context, request_data)
    
    async def encrypt_sensitive_data(self, data: Any, 
                                   security_context: SecurityContext) -> Dict[str, Any]:
        """Encrypt sensitive data based on classification"""
        
        if not security_context.encryption_required:
            return {"encrypted": False, "data": data}
        
        # Convert data to JSON string for encryption
        data_string = json.dumps(data) if not isinstance(data, str) else data
        
        # Encrypt the data
        encrypted_data = self.cipher_suite.encrypt(data_string.encode())
        
        # Create encryption metadata
        encryption_metadata = {
            "algorithm": "Fernet",
            "encrypted_at": datetime.now().isoformat(),
            "encrypted_by": security_context.user_id,
            "key_version": "v1",
            "data_classification": security_context.data_classification
        }
        
        return {
            "encrypted": True,
            "data": base64.b64encode(encrypted_data).decode(),
            "metadata": encryption_metadata
        }
    
    async def decrypt_sensitive_data(self, encrypted_package: Dict[str, Any],
                                   security_context: SecurityContext) -> Any:
        """Decrypt sensitive data with authorization checks"""
        
        if not encrypted_package.get("encrypted"):
            return encrypted_package.get("data")
        
        # Verify user has permission to decrypt this data
        metadata = encrypted_package.get("metadata", {})
        data_classification = metadata.get("data_classification", "internal")
        
        if not self._can_access_classification(security_context, data_classification):
            raise SecurityException("Access denied: insufficient clearance for data classification")
        
        # Decrypt the data
        try:
            encrypted_data = base64.b64decode(encrypted_package["data"].encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(decrypted_data.decode())
            except json.JSONDecodeError:
                return decrypted_data.decode()
                
        except Exception as e:
            raise SecurityException(f"Decryption failed: {str(e)}")
    
    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _get_jwt_secret(self) -> str:
        """Get JWT signing secret (in production, use secure key management)"""
        return "your-super-secret-jwt-key-change-this-in-production"

class SecurityException(Exception):
    """Security-related exceptions"""
    pass

class ThreatDetectionSystem:
    """Advanced threat detection for agent systems"""
    
    def __init__(self):
        self.threat_patterns = {}
        self.anomaly_baseline = {}
        self.active_threats = []
        self.logger = logging.getLogger("threat_detection")
        
    def setup_threat_detection(self) -> Dict[str, Any]:
        """Configure threat detection patterns"""
        
        threat_config = {
            "patterns": {
                "brute_force": {
                    "failed_attempts_threshold": 5,
                    "time_window_minutes": 5,
                    "block_duration_minutes": 30
                },
                "anomalous_behavior": {
                    "request_rate_threshold": 1000,  # requests per minute
                    "unusual_access_patterns": True,
                    "geographic_anomalies": True
                },
                "data_exfiltration": {
                    "large_response_threshold_mb": 10,
                    "rapid_requests_threshold": 50,
                    "sensitive_data_access_monitoring": True
                },
                "injection_attacks": {
                    "sql_injection_patterns": True,
                    "prompt_injection_detection": True,
                    "code_injection_patterns": True
                }
            },
            
            "response_actions": {
                "low_risk": ["log_event", "monitor_closely"],
                "medium_risk": ["rate_limit", "require_additional_auth"],
                "high_risk": ["block_temporarily", "alert_security_team"],
                "critical": ["block_permanently", "emergency_response"]
            }
        }
        
        self.threat_patterns = threat_config
        return threat_config
    
    async def analyze_request_for_threats(self, request_data: Dict[str, Any],
                                        security_context: SecurityContext) -> Dict[str, Any]:
        """Analyze request for potential security threats"""
        
        threat_analysis = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_data.get("request_id"),
            "user_id": security_context.user_id,
            "threats_detected": [],
            "risk_level": "low",
            "recommended_actions": []
        }
        
        # Check for brute force patterns
        brute_force_risk = await self._detect_brute_force(security_context.user_id)
        if brute_force_risk["detected"]:
            threat_analysis["threats_detected"].append("brute_force_attempt")
            threat_analysis["risk_level"] = "high"
        
        # Check for prompt injection
        prompt_injection_risk = await self._detect_prompt_injection(request_data.get("prompt", ""))
        if prompt_injection_risk["detected"]:
            threat_analysis["threats_detected"].append("prompt_injection")
            threat_analysis["risk_level"] = max(threat_analysis["risk_level"], "medium")
        
        # Check for anomalous behavior
        behavioral_risk = await self._detect_behavioral_anomalies(request_data, security_context)
        if behavioral_risk["detected"]:
            threat_analysis["threats_detected"].append("behavioral_anomaly")
            threat_analysis["risk_level"] = max(threat_analysis["risk_level"], "medium")
        
        # Determine recommended actions
        if threat_analysis["threats_detected"]:
            threat_analysis["recommended_actions"] = self.threat_patterns["response_actions"].get(
                threat_analysis["risk_level"], ["log_event"]
            )
        
        return threat_analysis
    
    async def _detect_prompt_injection(self, prompt: str) -> Dict[str, Any]:
        """Detect potential prompt injection attacks"""
        
        injection_patterns = [
            "ignore previous instructions",
            "forget your role", 
            "you are now",
            "system:",
            "assistant:",
            "user:",
            "<script>",
            "eval(",
            "execute",
            "rm -rf",
            "DROP TABLE"
        ]
        
        prompt_lower = prompt.lower()
        detected_patterns = []
        
        for pattern in injection_patterns:
            if pattern.lower() in prompt_lower:
                detected_patterns.append(pattern)
        
        return {
            "detected": len(detected_patterns) > 0,
            "patterns": detected_patterns,
            "confidence": min(len(detected_patterns) * 0.3, 1.0)
        }
    
    async def _detect_behavioral_anomalies(self, request_data: Dict[str, Any],
                                         security_context: SecurityContext) -> Dict[str, Any]:
        """Detect anomalous user behavior patterns"""
        
        user_id = security_context.user_id
        
        # Simple anomaly detection (in production, use ML models)
        current_time = datetime.now()
        request_rate = self._calculate_recent_request_rate(user_id)
        
        anomalies = []
        
        # High request rate anomaly
        if request_rate > 100:  # More than 100 requests per minute
            anomalies.append("high_request_rate")
        
        # Unusual time access
        if current_time.hour < 6 or current_time.hour > 22:  # Outside normal hours
            anomalies.append("unusual_access_time")
        
        # Geographic anomaly (simplified)
        user_ip = request_data.get("source_ip", "")
        if self._is_unusual_geographic_location(user_id, user_ip):
            anomalies.append("geographic_anomaly")
        
        return {
            "detected": len(anomalies) > 0,
            "anomalies": anomalies,
            "risk_score": len(anomalies) * 0.3
        }
```

---

## Part 2: Compliance and Audit Framework (15 minutes)

### Regulatory Compliance System

🗂️ **File**: `src/session8/compliance_framework.py` - Comprehensive compliance management

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
from enum import Enum

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    CCPA = "ccpa"

@dataclass
class DataSubject:
    """Data subject for privacy compliance"""
    subject_id: str
    subject_type: str  # user, patient, customer
    consent_records: List[Dict[str, Any]] = field(default_factory=list)
    data_retention_policy: Optional[str] = None
    deletion_requests: List[Dict[str, Any]] = field(default_factory=list)
    
class ComplianceManager:
    """Comprehensive compliance management system"""
    
    def __init__(self):
        self.compliance_policies = {}
        self.audit_trail = []
        self.data_subjects = {}
        self.retention_policies = {}
        self.logger = logging.getLogger("compliance")
        
    def setup_compliance_frameworks(self) -> Dict[str, Any]:
        """Configure multiple compliance frameworks"""
        
        compliance_config = {
            "gdpr": {
                "enabled": True,
                "data_controller": "Your Company Ltd",
                "dpo_contact": "dpo@company.com",
                "lawful_basis": "consent",
                "retention_period_months": 24,
                "rights_supported": [
                    "access", "rectification", "erasure", 
                    "portability", "restrict_processing", "object"
                ],
                "consent_management": {
                    "explicit_consent_required": True,
                    "consent_withdrawal": True,
                    "consent_records_retention": 84  # months
                },
                "privacy_by_design": {
                    "data_minimization": True,
                    "purpose_limitation": True,
                    "storage_limitation": True,
                    "pseudonymization": True
                }
            },
            
            "hipaa": {
                "enabled": True,
                "covered_entity": "Healthcare Provider Inc",
                "business_associate_agreements": True,
                "minimum_necessary": True,
                "phi_safeguards": {
                    "access_controls": True,
                    "audit_controls": True,
                    "integrity": True,
                    "transmission_security": True
                },
                "breach_notification": {
                    "breach_threshold": 500,  # individuals affected
                    "notification_timeline_hours": 72,
                    "hhs_notification_days": 60
                }
            },
            
            "soc2": {
                "enabled": True,
                "trust_service_criteria": [
                    "security", "availability", "processing_integrity",
                    "confidentiality", "privacy"
                ],
                "control_objectives": {
                    "logical_access": True,
                    "system_operations": True,
                    "change_management": True,
                    "risk_mitigation": True
                },
                "audit_requirements": {
                    "continuous_monitoring": True,
                    "annual_assessment": True,
                    "third_party_audit": True
                }
            }
        }
        
        self.compliance_policies = compliance_config
        return compliance_config
    
    async def process_data_subject_request(self, request_type: str, 
                                         subject_id: str,
                                         request_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process data subject rights requests (GDPR Article 12-22)"""
        
        request_id = f"DSR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{subject_id}"
        
        # Log the request
        await self._log_compliance_event("data_subject_request", {
            "request_id": request_id,
            "request_type": request_type,
            "subject_id": subject_id,
            "timestamp": datetime.now().isoformat()
        })
        
        if request_type == "access":  # Right of Access (Article 15)
            return await self._process_access_request(subject_id, request_id)
        elif request_type == "rectification":  # Right to Rectification (Article 16)
            return await self._process_rectification_request(subject_id, request_details, request_id)
        elif request_type == "erasure":  # Right to Erasure (Article 17)
            return await self._process_erasure_request(subject_id, request_id)
        elif request_type == "portability":  # Right to Data Portability (Article 20)
            return await self._process_portability_request(subject_id, request_id)
        else:
            return {
                "request_id": request_id,
                "status": "unsupported",
                "message": f"Request type {request_type} not supported"
            }
    
    async def _process_access_request(self, subject_id: str, request_id: str) -> Dict[str, Any]:
        """Process GDPR Article 15 - Right of Access"""
        
        # Collect all personal data for the subject
        personal_data = await self._collect_personal_data(subject_id)
        
        # Prepare structured response
        access_response = {
            "request_id": request_id,
            "subject_id": subject_id,
            "status": "completed",
            "data_collected": {
                "processing_purposes": personal_data.get("purposes", []),
                "categories_of_data": personal_data.get("categories", []),
                "recipients": personal_data.get("recipients", []),
                "retention_period": personal_data.get("retention_period"),
                "rights_information": [
                    "rectification", "erasure", "restrict_processing",
                    "object", "portability", "withdraw_consent"
                ],
                "data_source": personal_data.get("source", "directly_provided"),
                "automated_decision_making": personal_data.get("automated_decisions", False)
            },
            "personal_data": personal_data.get("data", {}),
            "response_format": "structured_json",
            "generated_at": datetime.now().isoformat()
        }
        
        # Ensure response is provided within GDPR timeline (1 month)
        response_deadline = datetime.now() + timedelta(days=30)
        access_response["response_deadline"] = response_deadline.isoformat()
        
        return access_response
    
    async def _process_erasure_request(self, subject_id: str, request_id: str) -> Dict[str, Any]:
        """Process GDPR Article 17 - Right to Erasure"""
        
        # Check if erasure is legally possible
        erasure_assessment = await self._assess_erasure_feasibility(subject_id)
        
        if not erasure_assessment["can_erase"]:
            return {
                "request_id": request_id,
                "status": "denied",
                "reason": erasure_assessment["reason"],
                "legal_basis": erasure_assessment["legal_basis"]
            }
        
        # Perform data erasure
        erasure_results = await self._perform_data_erasure(subject_id)
        
        # Notify third parties if required
        if erasure_results["third_party_notification_required"]:
            await self._notify_third_parties_of_erasure(subject_id, erasure_results["shared_with"])
        
        return {
            "request_id": request_id,
            "status": "completed",
            "erasure_completed_at": datetime.now().isoformat(),
            "data_erased": erasure_results["erased_categories"],
            "systems_affected": erasure_results["systems"],
            "third_parties_notified": erasure_results.get("third_parties_notified", [])
        }
    
    async def implement_data_retention_policies(self) -> Dict[str, Any]:
        """Implement automated data retention and disposal"""
        
        retention_results = {
            "processed_at": datetime.now().isoformat(),
            "policies_applied": [],
            "data_disposed": [],
            "errors": []
        }
        
        for framework, config in self.compliance_policies.items():
            if not config.get("enabled"):
                continue
                
            # Apply retention policies based on framework
            if framework == "gdpr":
                gdpr_results = await self._apply_gdpr_retention_policy(config)
                retention_results["policies_applied"].append(gdpr_results)
                
            elif framework == "hipaa":
                hipaa_results = await self._apply_hipaa_retention_policy(config)
                retention_results["policies_applied"].append(hipaa_results)
        
        return retention_results
    
    async def _apply_gdpr_retention_policy(self, gdpr_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply GDPR-specific retention policies"""
        
        retention_period = gdpr_config.get("retention_period_months", 24)
        cutoff_date = datetime.now() - timedelta(days=retention_period * 30)
        
        # Find data eligible for deletion
        eligible_data = await self._find_data_older_than(cutoff_date)
        
        deletion_results = {
            "framework": "gdpr",
            "retention_period_months": retention_period,
            "cutoff_date": cutoff_date.isoformat(),
            "records_identified": len(eligible_data),
            "records_deleted": 0,
            "errors": []
        }
        
        # Process deletions
        for data_record in eligible_data:
            try:
                # Check if there's a legal basis to retain
                if await self._has_legal_basis_to_retain(data_record):
                    continue
                
                # Perform deletion
                await self._delete_data_record(data_record)
                deletion_results["records_deleted"] += 1
                
            except Exception as e:
                deletion_results["errors"].append({
                    "record_id": data_record.get("id"),
                    "error": str(e)
                })
        
        return deletion_results
    
    async def generate_compliance_report(self, framework: ComplianceFramework,
                                       report_period_days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive compliance reports"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=report_period_days)
        
        report = {
            "framework": framework.value,
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "period_days": report_period_days
            },
            "compliance_status": "compliant",  # Default, will be updated
            "metrics": {},
            "violations": [],
            "recommendations": [],
            "generated_at": datetime.now().isoformat()
        }
        
        if framework == ComplianceFramework.GDPR:
            report.update(await self._generate_gdpr_report(start_date, end_date))
        elif framework == ComplianceFramework.HIPAA:
            report.update(await self._generate_hipaa_report(start_date, end_date))
        elif framework == ComplianceFramework.SOC2:
            report.update(await self._generate_soc2_report(start_date, end_date))
        
        return report
    
    async def _generate_gdpr_report(self, start_date: datetime, 
                                  end_date: datetime) -> Dict[str, Any]:
        """Generate GDPR-specific compliance report"""
        
        # Collect GDPR-specific metrics
        gdpr_metrics = {
            "data_subject_requests": await self._count_dsr_by_type(start_date, end_date),
            "consent_records": await self._count_consent_activities(start_date, end_date),
            "data_breaches": await self._count_data_breaches(start_date, end_date),
            "retention_compliance": await self._assess_retention_compliance(),
            "third_party_transfers": await self._count_international_transfers(start_date, end_date)
        }
        
        # Assess compliance status
        violations = []
        
        # Check DSR response times
        overdue_dsrs = await self._find_overdue_dsrs()
        if overdue_dsrs:
            violations.append({
                "type": "dsr_response_time",
                "severity": "high", 
                "description": f"{len(overdue_dsrs)} data subject requests overdue",
                "remediation": "Process overdue requests immediately"
            })
        
        # Check for consent compliance
        invalid_consents = await self._find_invalid_consents()
        if invalid_consents:
            violations.append({
                "type": "invalid_consent",
                "severity": "medium",
                "description": f"{len(invalid_consents)} invalid consent records found",
                "remediation": "Update consent records and re-obtain consent where necessary"
            })
        
        return {
            "gdpr_metrics": gdpr_metrics,
            "violations": violations,
            "compliance_status": "non_compliant" if violations else "compliant"
        }

class AuditTrailManager:
    """Comprehensive audit trail management"""
    
    def __init__(self):
        self.audit_events = []
        self.integrity_hashes = {}
        self.logger = logging.getLogger("audit")
        
    async def log_audit_event(self, event_type: str, 
                            event_data: Dict[str, Any],
                            security_context: Optional[Dict[str, Any]] = None):
        """Log auditable events with integrity protection"""
        
        audit_entry = {
            "event_id": self._generate_event_id(),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "event_data": event_data,
            "security_context": security_context or {},
            "system_context": {
                "service_version": "1.0.0",
                "environment": "production",
                "node_id": "agent-node-1"
            }
        }
        
        # Add integrity hash
        audit_entry["integrity_hash"] = self._calculate_integrity_hash(audit_entry)
        
        # Store audit entry
        self.audit_events.append(audit_entry)
        
        # Log to external audit system
        await self._send_to_audit_system(audit_entry)
    
    def _generate_event_id(self) -> str:
        """Generate unique audit event ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _calculate_integrity_hash(self, audit_entry: Dict[str, Any]) -> str:
        """Calculate integrity hash for audit entry"""
        
        # Remove the hash field itself from calculation
        entry_copy = {k: v for k, v in audit_entry.items() if k != "integrity_hash"}
        entry_json = json.dumps(entry_copy, sort_keys=True)
        
        import hashlib
        return hashlib.sha256(entry_json.encode()).hexdigest()
```

---

## Part 3: Privacy and Data Protection (10 minutes)

### Advanced Privacy Controls

🗂️ **File**: `src/session8/privacy_protection.py` - Privacy-preserving agent systems

```python
from typing import Dict, List, Any, Optional
import hashlib
import json
from datetime import datetime, timedelta

class PrivacyPreservingAgentSystem:
    """Privacy-preserving techniques for agent operations"""
    
    def __init__(self):
        self.anonymization_techniques = {}
        self.pseudonymization_keys = {}
        self.differential_privacy_params = {}
        
    def setup_privacy_techniques(self) -> Dict[str, Any]:
        """Configure privacy-preserving techniques"""
        
        privacy_config = {
            "data_anonymization": {
                "enabled": True,
                "techniques": ["k_anonymity", "l_diversity", "t_closeness"],
                "k_value": 5,  # k-anonymity parameter
                "l_value": 2,  # l-diversity parameter
                "t_value": 0.2  # t-closeness parameter
            },
            
            "differential_privacy": {
                "enabled": True,
                "epsilon": 1.0,  # Privacy budget
                "delta": 1e-5,   # Failure probability
                "noise_mechanism": "laplace"
            },
            
            "pseudonymization": {
                "enabled": True,
                "key_rotation_days": 90,
                "deterministic": False,  # Use random pseudonyms
                "format_preserving": True
            },
            
            "homomorphic_encryption": {
                "enabled": False,  # Computationally expensive
                "scheme": "ckks",  # For approximate computations
                "key_size": 4096
            }
        }
        
        return privacy_config
    
    def anonymize_dataset(self, dataset: List[Dict[str, Any]], 
                         sensitive_attributes: List[str]) -> Dict[str, Any]:
        """Apply k-anonymity and l-diversity to dataset"""
        
        # Implementation would include:
        # 1. Identify quasi-identifiers
        # 2. Apply generalization and suppression
        # 3. Ensure k-anonymity constraint
        # 4. Apply l-diversity for sensitive attributes
        
        anonymized_data = []
        for record in dataset:
            anonymized_record = self._anonymize_record(record, sensitive_attributes)
            anonymized_data.append(anonymized_record)
        
        return {
            "original_records": len(dataset),
            "anonymized_records": len(anonymized_data),
            "anonymization_applied": True,
            "data": anonymized_data,
            "privacy_metrics": {
                "k_anonymity": self._calculate_k_anonymity(anonymized_data),
                "l_diversity": self._calculate_l_diversity(anonymized_data, sensitive_attributes)
            }
        }
    
    def apply_differential_privacy(self, query_result: float, 
                                 sensitivity: float = 1.0,
                                 epsilon: float = 1.0) -> float:
        """Apply differential privacy to query results"""
        
        import random
        import math
        
        # Laplace mechanism
        scale = sensitivity / epsilon
        noise = random.laplace(0, scale)
        
        return query_result + noise
    
    def _anonymize_record(self, record: Dict[str, Any], 
                         sensitive_attrs: List[str]) -> Dict[str, Any]:
        """Anonymize individual record"""
        
        anonymized = record.copy()
        
        # Generalize age to age groups
        if "age" in record:
            age = record["age"]
            if age < 25:
                anonymized["age_group"] = "18-24"
            elif age < 35:
                anonymized["age_group"] = "25-34"
            elif age < 45:
                anonymized["age_group"] = "35-44"
            else:
                anonymized["age_group"] = "45+"
            del anonymized["age"]
        
        # Generalize location to broader regions
        if "zip_code" in record:
            zip_code = str(record["zip_code"])
            anonymized["region"] = zip_code[:3] + "**"
            del anonymized["zip_code"]
        
        # Remove or pseudonymize direct identifiers
        identifiers = ["name", "email", "phone", "ssn"]
        for identifier in identifiers:
            if identifier in anonymized:
                if identifier in sensitive_attrs:
                    anonymized[identifier] = self._pseudonymize_value(anonymized[identifier])
                else:
                    del anonymized[identifier]
        
        return anonymized
```

---

## 🎯 Module Summary

You've now mastered security and compliance for enterprise Agno systems:

✅ **Zero-Trust Architecture**: Implemented comprehensive authentication, authorization, and threat detection  
✅ **Data Encryption**: Built end-to-end encryption with key management and secure data handling  
✅ **Compliance Framework**: Created GDPR, HIPAA, and SOC2 compliance systems with automated reporting  
✅ **Privacy Protection**: Implemented advanced privacy-preserving techniques including anonymization and differential privacy  
✅ **Audit Trail**: Designed comprehensive audit logging with integrity protection and compliance monitoring

### Next Steps
- **Return to Core**: [Session 8 Main](Session8_Agno_Production_Ready_Agents.md)
- **Review Other Modules**: [Advanced Monitoring](Session8_ModuleA_Advanced_Monitoring_Observability.md), [Enterprise Scaling](Session8_ModuleB_Enterprise_Scaling_Architecture.md), [Performance Optimization](Session8_ModuleC_Performance_Optimization.md)
- **Advance to Session 9**: [Session 9 - Advanced Framework Patterns](Session9_Advanced_Framework_Patterns.md)

---

**🗂️ Source Files for Module D:**
- `src/session8/security_architecture.py` - Zero-trust security implementation
- `src/session8/compliance_framework.py` - Regulatory compliance management
- `src/session8/privacy_protection.py` - Privacy-preserving techniques