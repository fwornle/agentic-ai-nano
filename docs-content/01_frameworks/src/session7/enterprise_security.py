"""
Agno Enterprise Security and Compliance
Session 7: Agno Production-Ready Agents

This module implements comprehensive enterprise security including authentication,
authorization, data protection, compliance validation, and audit logging.
"""

import asyncio
import logging
import json
import hashlib
import secrets
import base64
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import re
import uuid

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    import jwt
    from passlib.context import CryptContext
except ImportError:
    print("Warning: Cryptography libraries not available, using mock implementations")
    Fernet = None
    jwt = None
    CryptContext = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"

class DataClassification(Enum):
    """Data classification types"""
    PII = "personally_identifiable_information"
    PHI = "protected_health_information"
    FINANCIAL = "financial_data"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    TRADE_SECRET = "trade_secret"
    PUBLIC = "public_data"

class AccessLevel(Enum):
    """Access control levels"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"

@dataclass
class User:
    """User identity and attributes"""
    user_id: str
    username: str
    email: str
    roles: List[str]
    departments: List[str]
    security_clearance: SecurityLevel = SecurityLevel.INTERNAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked: bool = False
    mfa_enabled: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Permission:
    """Permission definition"""
    resource: str
    action: AccessLevel
    conditions: Dict[str, Any] = field(default_factory=dict)
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

@dataclass
class SecurityPolicy:
    """Security policy definition"""
    name: str
    description: str
    rules: List[Dict[str, Any]]
    compliance_frameworks: List[ComplianceFramework]
    effective_date: datetime
    review_date: datetime
    version: str = "1.0"

@dataclass
class AuditEvent:
    """Security audit event"""
    event_id: str
    event_type: str
    user_id: Optional[str]
    resource: str
    action: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0

class EncryptionService:
    """Advanced encryption service for data protection"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        """Initialize encryption service"""
        if Fernet is None:
            logger.warning("Cryptography not available, using mock encryption")
            self.cipher_suite = None
            return
            
        if master_key:
            self.master_key = master_key
        else:
            self.master_key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.master_key)
        self.key_derivation_cache: Dict[str, bytes] = {}
        
        logger.info("Encryption service initialized")
    
    def encrypt_data(self, data: Union[str, bytes], key_id: Optional[str] = None) -> Dict[str, Any]:
        """Encrypt data with optional key derivation"""
        if self.cipher_suite is None:
            # Mock implementation
            return {
                "encrypted_data": base64.b64encode(data.encode() if isinstance(data, str) else data).decode(),
                "key_id": key_id or "mock_key",
                "algorithm": "mock-aes-256-gcm",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Use specific key if provided
            cipher = self.cipher_suite
            if key_id:
                cipher = self._get_derived_cipher(key_id)
            
            encrypted_data = cipher.encrypt(data)
            
            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "key_id": key_id or "master",
                "algorithm": "fernet",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise SecurityException(f"Data encryption failed: {e}")
    
    def decrypt_data(self, encrypted_data: str, key_id: Optional[str] = None) -> bytes:
        """Decrypt data"""
        if self.cipher_suite is None:
            # Mock implementation
            return base64.b64decode(encrypted_data.encode())
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            # Use specific key if provided
            cipher = self.cipher_suite
            if key_id and key_id != "master":
                cipher = self._get_derived_cipher(key_id)
            
            decrypted_data = cipher.decrypt(encrypted_bytes)
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise SecurityException(f"Data decryption failed: {e}")
    
    def _get_derived_cipher(self, key_id: str) -> 'Fernet':
        """Get or create derived encryption key"""
        if key_id in self.key_derivation_cache:
            return Fernet(self.key_derivation_cache[key_id])
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=key_id.encode('utf-8')[:16].ljust(16, b'\x00'),
            iterations=100000,
            backend=default_backend()
        )
        
        derived_key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        self.key_derivation_cache[key_id] = derived_key
        
        return Fernet(derived_key)
    
    def generate_hash(self, data: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Generate secure hash with salt"""
        if not salt:
            salt = secrets.token_hex(32)
        
        # Use SHA-256 with salt
        hash_input = f"{data}{salt}".encode('utf-8')
        hash_digest = hashlib.sha256(hash_input).hexdigest()
        
        return {
            "hash": hash_digest,
            "salt": salt,
            "algorithm": "sha256"
        }

class AuthenticationService:
    """Advanced authentication service"""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
        self.user_store: Dict[str, User] = {}
        self.session_store: Dict[str, Dict[str, Any]] = {}
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None
        
        # Authentication policies
        self.auth_policies = {
            "max_failed_attempts": 5,
            "lockout_duration": 900,  # 15 minutes
            "session_timeout": 3600,  # 1 hour
            "password_min_length": 12,
            "password_require_complexity": True,
            "mfa_required_roles": ["admin", "security_officer"],
            "jwt_secret": secrets.token_urlsafe(32)
        }
        
        logger.info("Authentication service initialized")
    
    def register_user(self, username: str, email: str, password: str, 
                     roles: List[str] = None, departments: List[str] = None) -> User:
        """Register new user"""
        # Validate password strength
        if not self._validate_password_strength(password):
            raise SecurityException("Password does not meet complexity requirements")
        
        # Check if user already exists
        if self._user_exists(username, email):
            raise SecurityException("User already exists")
        
        # Create user
        user_id = str(uuid.uuid4())
        
        # Hash password
        if self.password_context:
            password_hash = self.password_context.hash(password)
        else:
            # Mock hash
            hash_result = self.encryption_service.generate_hash(password)
            password_hash = hash_result["hash"]
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles or ["user"],
            departments=departments or ["general"],
            mfa_enabled=any(role in self.auth_policies["mfa_required_roles"] for role in (roles or []))
        )
        
        # Store user (in production, use secure database)
        self.user_store[user_id] = user
        
        # Store password hash separately (encrypted)
        password_data = self.encryption_service.encrypt_data(password_hash)
        
        logger.info(f"User registered: {username} ({user_id})")
        return user
    
    async def authenticate_user(self, username: str, password: str, 
                              mfa_token: Optional[str] = None,
                              client_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Authenticate user with optional MFA"""
        client_info = client_info or {}
        
        # Find user
        user = self._find_user_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: user not found - {username}")
            raise AuthenticationException("Invalid credentials")
        
        # Check account lock
        if user.account_locked:
            logger.warning(f"Authentication failed: account locked - {username}")
            raise AuthenticationException("Account locked due to multiple failed attempts")
        
        # Verify password
        # (In production, retrieve and decrypt stored password hash)
        password_valid = self._verify_password(password, "stored_hash")  # Simplified
        
        if not password_valid:
            user.failed_login_attempts += 1
            
            if user.failed_login_attempts >= self.auth_policies["max_failed_attempts"]:
                user.account_locked = True
                logger.warning(f"Account locked due to failed attempts: {username}")
            
            raise AuthenticationException("Invalid credentials")
        
        # Verify MFA if required
        if user.mfa_enabled and not mfa_token:
            return {
                "status": "mfa_required",
                "message": "Multi-factor authentication required",
                "user_id": user.user_id
            }
        
        if user.mfa_enabled and mfa_token:
            if not self._verify_mfa_token(user.user_id, mfa_token):
                raise AuthenticationException("Invalid MFA token")
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        
        # Create session
        session = await self._create_user_session(user, client_info)
        
        logger.info(f"User authenticated: {username}")
        return {
            "status": "success",
            "user": asdict(user),
            "session": session
        }
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets complexity requirements"""
        if len(password) < self.auth_policies["password_min_length"]:
            return False
        
        if self.auth_policies["password_require_complexity"]:
            # Check for uppercase, lowercase, digit, and special character
            if not (re.search(r'[A-Z]', password) and
                   re.search(r'[a-z]', password) and
                   re.search(r'[0-9]', password) and
                   re.search(r'[!@#$%^&*(),.?\":{}|<>]', password)):
                return False
        
        return True
    
    def _user_exists(self, username: str, email: str) -> bool:
        """Check if user already exists"""
        for user in self.user_store.values():
            if user.username == username or user.email == email:
                return True
        return False
    
    def _find_user_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        for user in self.user_store.values():
            if user.username == username:
                return user
        return None
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        if self.password_context:
            return self.password_context.verify(password, stored_hash)
        else:
            # Mock verification
            return len(password) >= 8  # Simplified
    
    def _verify_mfa_token(self, user_id: str, token: str) -> bool:
        """Verify MFA token (TOTP, SMS, etc.)"""
        # Mock MFA verification
        return len(token) == 6 and token.isdigit()
    
    async def _create_user_session(self, user: User, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create authenticated user session"""
        session_id = secrets.token_urlsafe(32)
        
        # Create JWT token
        if jwt:
            token_payload = {
                "user_id": user.user_id,
                "username": user.username,
                "roles": user.roles,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(seconds=self.auth_policies["session_timeout"])
            }
            
            access_token = jwt.encode(token_payload, self.auth_policies["jwt_secret"], algorithm="HS256")
        else:
            access_token = f"mock_token_{session_id}"
        
        session = {
            "session_id": session_id,
            "access_token": access_token,
            "user_id": user.user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=self.auth_policies["session_timeout"]),
            "client_info": client_info
        }
        
        self.session_store[session_id] = session
        return session

class AuthorizationService:
    """Role-based access control (RBAC) service"""
    
    def __init__(self):
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.permissions: Dict[str, List[Permission]] = {}  # user_id -> permissions
        self.role_hierarchy: Dict[str, List[str]] = {}  # role -> inherited roles
        self.resource_policies: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default roles and permissions
        self._initialize_default_rbac()
        
        logger.info("Authorization service initialized")
    
    def _initialize_default_rbac(self):
        """Initialize default roles and permissions"""
        # Define roles
        self.roles = {
            "user": {
                "name": "Standard User",
                "description": "Basic user with read access",
                "permissions": ["read_public", "read_own_data"]
            },
            "analyst": {
                "name": "Data Analyst",
                "description": "Can analyze data and create reports",
                "permissions": ["read_public", "read_confidential", "create_reports", "execute_queries"]
            },
            "admin": {
                "name": "Administrator",
                "description": "Full system administration access",
                "permissions": ["read_all", "write_all", "delete_all", "manage_users", "manage_system"]
            },
            "security_officer": {
                "name": "Security Officer",
                "description": "Security and compliance management",
                "permissions": ["read_all", "audit_access", "manage_security", "view_audit_logs"]
            }
        }
        
        # Define role hierarchy
        self.role_hierarchy = {
            "admin": ["analyst", "user"],
            "security_officer": ["analyst", "user"],
            "analyst": ["user"]
        }
    
    def create_role(self, role_name: str, description: str, permissions: List[str]):
        """Create new role"""
        self.roles[role_name] = {
            "name": role_name,
            "description": description,
            "permissions": permissions
        }
        
        logger.info(f"Created role: {role_name}")
    
    def assign_role_to_user(self, user_id: str, role: str):
        """Assign role to user"""
        if role not in self.roles:
            raise AuthorizationException(f"Role does not exist: {role}")
        
        # Get user permissions from role
        role_permissions = self._get_role_permissions(role)
        
        if user_id not in self.permissions:
            self.permissions[user_id] = []
        
        # Add role permissions to user
        for perm_name in role_permissions:
            permission = Permission(
                resource="*",  # Wildcard for role-based permissions
                action=AccessLevel.READ,  # Default, will be refined by permission name
                conditions={"role": role, "permission": perm_name}
            )
            self.permissions[user_id].append(permission)
        
        logger.info(f"Assigned role {role} to user {user_id}")
    
    def grant_permission(self, user_id: str, resource: str, action: AccessLevel,
                        conditions: Dict[str, Any] = None, expires_at: datetime = None):
        """Grant specific permission to user"""
        permission = Permission(
            resource=resource,
            action=action,
            conditions=conditions or {},
            expires_at=expires_at
        )
        
        if user_id not in self.permissions:
            self.permissions[user_id] = []
        
        self.permissions[user_id].append(permission)
        
        logger.info(f"Granted permission {action.value} on {resource} to user {user_id}")
    
    def check_permission(self, user_id: str, resource: str, action: AccessLevel,
                        context: Dict[str, Any] = None) -> bool:
        """Check if user has permission for action on resource"""
        context = context or {}
        
        user_permissions = self.permissions.get(user_id, [])
        
        for permission in user_permissions:
            # Check if permission is expired
            if permission.expires_at and datetime.utcnow() > permission.expires_at:
                continue
            
            # Check resource match (exact or wildcard)
            if not (permission.resource == resource or permission.resource == "*"):
                continue
            
            # Check action match
            if permission.action != action and permission.action != AccessLevel.ADMIN:
                continue
            
            # Check conditions
            if permission.conditions:
                if not self._evaluate_conditions(permission.conditions, context):
                    continue
            
            logger.debug(f"Permission granted: {user_id} {action.value} {resource}")
            return True
        
        logger.warning(f"Permission denied: {user_id} {action.value} {resource}")
        return False
    
    def _get_role_permissions(self, role: str) -> Set[str]:
        """Get all permissions for role including inherited ones"""
        permissions = set()
        
        if role in self.roles:
            permissions.update(self.roles[role]["permissions"])
        
        # Add inherited permissions
        if role in self.role_hierarchy:
            for inherited_role in self.role_hierarchy[role]:
                permissions.update(self._get_role_permissions(inherited_role))
        
        return permissions
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate permission conditions against context"""
        for condition_key, condition_value in conditions.items():
            if condition_key not in context:
                return False
            
            context_value = context[condition_key]
            
            # Handle different condition types
            if isinstance(condition_value, list):
                if context_value not in condition_value:
                    return False
            elif context_value != condition_value:
                return False
        
        return True

class DataProtectionService:
    """Data classification and protection service"""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
        self.classification_rules: Dict[str, Dict[str, Any]] = {}
        self.protection_policies: Dict[DataClassification, Dict[str, Any]] = {}
        
        self._initialize_classification_rules()
        self._initialize_protection_policies()
        
        logger.info("Data protection service initialized")
    
    def _initialize_classification_rules(self):
        """Initialize data classification rules"""
        self.classification_rules = {
            "pii_patterns": {
                "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
                "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "phone": r'\b\d{3}-\d{3}-\d{4}\b',
                "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            },
            "phi_patterns": {
                "medical_record": r'MRN[-\s]?\d+',
                "patient_id": r'Patient[-\s]?ID[-\s]?\d+',
                "diagnosis_code": r'ICD[-\s]?\d+[.-]\d+'
            },
            "financial_patterns": {
                "account_number": r'Account[-\s]?\d{8,12}',
                "routing_number": r'Routing[-\s]?\d{9}',
                "transaction_id": r'TXN[-\s]?\d+'
            }
        }
    
    def _initialize_protection_policies(self):
        """Initialize data protection policies"""
        self.protection_policies = {
            DataClassification.PII: {
                "encryption_required": True,
                "access_logging": True,
                "retention_days": 2555,  # 7 years
                "anonymization_required": True,
                "restricted_roles": ["analyst", "admin", "security_officer"]
            },
            DataClassification.PHI: {
                "encryption_required": True,
                "access_logging": True,
                "retention_days": 2190,  # 6 years
                "anonymization_required": True,
                "restricted_roles": ["admin", "security_officer"],
                "compliance_frameworks": [ComplianceFramework.HIPAA]
            },
            DataClassification.FINANCIAL: {
                "encryption_required": True,
                "access_logging": True,
                "retention_days": 3650,  # 10 years
                "anonymization_required": False,
                "restricted_roles": ["analyst", "admin", "security_officer"],
                "compliance_frameworks": [ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2]
            },
            DataClassification.PUBLIC: {
                "encryption_required": False,
                "access_logging": False,
                "retention_days": 365,
                "anonymization_required": False,
                "restricted_roles": []
            }
        }
    
    def classify_data(self, data: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Classify data and determine protection requirements"""
        classifications = []
        confidence_scores = {}
        
        # Check for PII patterns
        pii_matches = self._check_patterns(data, self.classification_rules["pii_patterns"])
        if pii_matches:
            classifications.append(DataClassification.PII)
            confidence_scores[DataClassification.PII.value] = len(pii_matches) * 0.3
        
        # Check for PHI patterns
        phi_matches = self._check_patterns(data, self.classification_rules["phi_patterns"])
        if phi_matches:
            classifications.append(DataClassification.PHI)
            confidence_scores[DataClassification.PHI.value] = len(phi_matches) * 0.4
        
        # Check for financial patterns
        financial_matches = self._check_patterns(data, self.classification_rules["financial_patterns"])
        if financial_matches:
            classifications.append(DataClassification.FINANCIAL)
            confidence_scores[DataClassification.FINANCIAL.value] = len(financial_matches) * 0.3
        
        # Default to public if no sensitive patterns found
        if not classifications:
            classifications.append(DataClassification.PUBLIC)
            confidence_scores[DataClassification.PUBLIC.value] = 1.0
        
        # Determine highest classification level
        primary_classification = self._determine_primary_classification(classifications)
        
        return {
            "primary_classification": primary_classification.value,
            "all_classifications": [c.value for c in classifications],
            "confidence_scores": confidence_scores,
            "protection_policy": self.protection_policies[primary_classification],
            "patterns_found": {
                "pii": pii_matches,
                "phi": phi_matches,
                "financial": financial_matches
            }
        }
    
    def apply_data_protection(self, data: str, classification_result: Dict[str, Any],
                            user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply appropriate data protection measures"""
        primary_classification = DataClassification(classification_result["primary_classification"])
        protection_policy = classification_result["protection_policy"]
        
        protected_data = data
        protection_applied = []
        
        # Apply encryption if required
        if protection_policy.get("encryption_required", False):
            encrypted = self.encryption_service.encrypt_data(data)
            protected_data = encrypted["encrypted_data"]
            protection_applied.append("encryption")
        
        # Apply anonymization if required
        if protection_policy.get("anonymization_required", False):
            anonymized = self._anonymize_sensitive_data(protected_data, classification_result)
            protected_data = anonymized["data"]
            protection_applied.extend(anonymized["methods"])
        
        # Apply access restrictions
        restricted_roles = protection_policy.get("restricted_roles", [])
        if restricted_roles and user_context:
            user_roles = user_context.get("roles", [])
            if not any(role in restricted_roles for role in user_roles):
                raise SecurityException("Insufficient privileges to access this data classification")
        
        return {
            "protected_data": protected_data,
            "original_classification": primary_classification.value,
            "protection_applied": protection_applied,
            "access_policy": {
                "restricted_roles": restricted_roles,
                "retention_days": protection_policy.get("retention_days"),
                "compliance_frameworks": protection_policy.get("compliance_frameworks", [])
            }
        }
    
    def _check_patterns(self, data: str, patterns: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check data against classification patterns"""
        matches = []
        
        for pattern_name, pattern in patterns.items():
            regex_matches = re.finditer(pattern, data)
            for match in regex_matches:
                matches.append({
                    "pattern": pattern_name,
                    "matched_text": match.group(),
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })
        
        return matches
    
    def _determine_primary_classification(self, classifications: List[DataClassification]) -> DataClassification:
        """Determine the highest priority classification"""
        # Classification priority (highest to lowest)
        priority_order = [
            DataClassification.PHI,
            DataClassification.PII,
            DataClassification.FINANCIAL,
            DataClassification.INTELLECTUAL_PROPERTY,
            DataClassification.TRADE_SECRET,
            DataClassification.PUBLIC
        ]
        
        for classification in priority_order:
            if classification in classifications:
                return classification
        
        return DataClassification.PUBLIC
    
    def _anonymize_sensitive_data(self, data: str, classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive data patterns"""
        anonymized_data = data
        methods_applied = []
        
        # Anonymize PII patterns
        pii_patterns = classification_result["patterns_found"]["pii"]
        for match in pii_patterns:
            if match["pattern"] == "ssn":
                anonymized_data = anonymized_data.replace(match["matched_text"], "***-**-****")
                methods_applied.append("ssn_masking")
            elif match["pattern"] == "email":
                email_parts = match["matched_text"].split("@")
                if len(email_parts) == 2:
                    masked_email = f"{email_parts[0][:2]}***@{email_parts[1]}"
                    anonymized_data = anonymized_data.replace(match["matched_text"], masked_email)
                    methods_applied.append("email_masking")
            elif match["pattern"] == "credit_card":
                # Mask all but last 4 digits
                cc_number = re.sub(r'[-\s]', '', match["matched_text"])
                masked_cc = f"****-****-****-{cc_number[-4:]}"
                anonymized_data = anonymized_data.replace(match["matched_text"], masked_cc)
                methods_applied.append("credit_card_masking")
        
        return {
            "data": anonymized_data,
            "methods": methods_applied
        }

class ComplianceValidator:
    """Compliance framework validation service"""
    
    def __init__(self):
        self.frameworks: Dict[ComplianceFramework, Dict[str, Any]] = {}
        self.validation_rules: Dict[ComplianceFramework, List[Callable]] = {}
        
        self._initialize_compliance_frameworks()
        
        logger.info("Compliance validator initialized")
    
    def _initialize_compliance_frameworks(self):
        """Initialize compliance framework definitions"""
        self.frameworks = {
            ComplianceFramework.GDPR: {
                "name": "General Data Protection Regulation",
                "requirements": [
                    "data_minimization",
                    "consent_management",
                    "right_to_erasure",
                    "data_portability",
                    "breach_notification"
                ]
            },
            ComplianceFramework.HIPAA: {
                "name": "Health Insurance Portability and Accountability Act",
                "requirements": [
                    "minimum_necessary_standard",
                    "access_controls",
                    "audit_controls",
                    "integrity_controls",
                    "transmission_security"
                ]
            },
            ComplianceFramework.SOC2: {
                "name": "Service Organization Control 2",
                "requirements": [
                    "security_principle",
                    "availability_principle",
                    "processing_integrity_principle",
                    "confidentiality_principle",
                    "privacy_principle"
                ]
            },
            ComplianceFramework.PCI_DSS: {
                "name": "Payment Card Industry Data Security Standard",
                "requirements": [
                    "secure_network",
                    "protect_cardholder_data",
                    "vulnerability_management",
                    "access_controls",
                    "monitoring_testing"
                ]
            }
        }
    
    def validate_request_compliance(self, request_data: Dict[str, Any],
                                   frameworks: List[ComplianceFramework]) -> Dict[str, Any]:
        """Validate request against compliance frameworks"""
        validation_results = {}
        overall_compliant = True
        violations = []
        
        for framework in frameworks:
            framework_result = self._validate_framework_compliance(request_data, framework)
            validation_results[framework.value] = framework_result
            
            if not framework_result["compliant"]:
                overall_compliant = False
                violations.extend(framework_result["violations"])
        
        return {
            "overall_compliant": overall_compliant,
            "framework_results": validation_results,
            "violations": violations,
            "validation_timestamp": datetime.utcnow().isoformat()
        }
    
    def _validate_framework_compliance(self, request_data: Dict[str, Any],
                                     framework: ComplianceFramework) -> Dict[str, Any]:
        """Validate specific framework compliance"""
        violations = []
        
        if framework == ComplianceFramework.GDPR:
            violations.extend(self._validate_gdpr_compliance(request_data))
        elif framework == ComplianceFramework.HIPAA:
            violations.extend(self._validate_hipaa_compliance(request_data))
        elif framework == ComplianceFramework.SOC2:
            violations.extend(self._validate_soc2_compliance(request_data))
        elif framework == ComplianceFramework.PCI_DSS:
            violations.extend(self._validate_pci_compliance(request_data))
        
        return {
            "framework": framework.value,
            "compliant": len(violations) == 0,
            "violations": violations,
            "requirements_checked": len(self.frameworks[framework]["requirements"])
        }
    
    def _validate_gdpr_compliance(self, request_data: Dict[str, Any]) -> List[str]:
        """Validate GDPR compliance"""
        violations = []
        
        # Check for consent management
        if request_data.get("data_subject_consent") is None:
            violations.append("Missing data subject consent documentation")
        
        # Check for data minimization
        if request_data.get("data_minimization_rationale") is None:
            violations.append("Missing data minimization rationale")
        
        # Check for lawful basis
        if request_data.get("lawful_basis") is None:
            violations.append("Missing lawful basis for processing")
        
        return violations
    
    def _validate_hipaa_compliance(self, request_data: Dict[str, Any]) -> List[str]:
        """Validate HIPAA compliance"""
        violations = []
        
        # Check for minimum necessary standard
        if request_data.get("minimum_necessary_justification") is None:
            violations.append("Missing minimum necessary justification")
        
        # Check for access controls
        user_context = request_data.get("user_context", {})
        if not user_context.get("authorized_for_phi"):
            violations.append("User not authorized for PHI access")
        
        return violations
    
    def _validate_soc2_compliance(self, request_data: Dict[str, Any]) -> List[str]:
        """Validate SOC 2 compliance"""
        violations = []
        
        # Check security controls
        if not request_data.get("security_controls_enabled"):
            violations.append("Security controls not properly enabled")
        
        return violations
    
    def _validate_pci_compliance(self, request_data: Dict[str, Any]) -> List[str]:
        """Validate PCI DSS compliance"""
        violations = []
        
        # Check for cardholder data handling
        if request_data.get("contains_cardholder_data") and not request_data.get("pci_compliant_environment"):
            violations.append("Cardholder data processed outside PCI compliant environment")
        
        return violations

class AuditLogger:
    """Comprehensive audit logging service"""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
        self.audit_store: List[AuditEvent] = []  # In production, use persistent storage
        self.risk_analyzer = SecurityRiskAnalyzer()
        
        logger.info("Audit logger initialized")
    
    async def log_security_event(self, event_type: str, user_id: str, resource: str,
                                action: str, success: bool = True, 
                                details: Dict[str, Any] = None,
                                client_info: Dict[str, Any] = None) -> str:
        """Log security-related event"""
        event_id = str(uuid.uuid4())
        
        # Calculate risk score
        risk_score = await self.risk_analyzer.calculate_risk_score(
            event_type, user_id, resource, action, success, details, client_info
        )
        
        audit_event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            resource=resource,
            action=action,
            timestamp=datetime.utcnow(),
            ip_address=client_info.get("ip_address") if client_info else None,
            user_agent=client_info.get("user_agent") if client_info else None,
            success=success,
            details=details or {},
            risk_score=risk_score
        )
        
        # Encrypt sensitive audit data
        encrypted_details = self.encryption_service.encrypt_data(json.dumps(details or {}))
        audit_event.details["encrypted"] = encrypted_details
        
        self.audit_store.append(audit_event)
        
        # Log high-risk events immediately
        if risk_score > 0.8:
            logger.error(f"High-risk security event: {event_type} by {user_id} (risk: {risk_score:.2f})")
        
        return event_id
    
    def get_audit_trail(self, user_id: Optional[str] = None, 
                       resource: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve audit trail with filtering"""
        filtered_events = self.audit_store.copy()
        
        # Apply filters
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if resource:
            filtered_events = [e for e in filtered_events if e.resource == resource]
        
        if start_date:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_date]
        
        if end_date:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_date]
        
        # Convert to serializable format
        return [asdict(event) for event in filtered_events]
    
    def generate_compliance_report(self, framework: ComplianceFramework,
                                 start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance audit report"""
        relevant_events = [
            e for e in self.audit_store
            if start_date <= e.timestamp <= end_date
        ]
        
        report = {
            "framework": framework.value,
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_events": len(relevant_events),
            "failed_events": len([e for e in relevant_events if not e.success]),
            "high_risk_events": len([e for e in relevant_events if e.risk_score > 0.8]),
            "unique_users": len(set(e.user_id for e in relevant_events if e.user_id)),
            "event_breakdown": self._analyze_event_breakdown(relevant_events),
            "compliance_violations": self._identify_compliance_violations(relevant_events, framework)
        }
        
        return report

class SecurityRiskAnalyzer:
    """Analyze and score security risks"""
    
    def __init__(self):
        self.risk_patterns = {
            "failed_login": 0.3,
            "privilege_escalation": 0.8,
            "data_access_outside_hours": 0.6,
            "bulk_data_access": 0.7,
            "admin_action": 0.4,
            "configuration_change": 0.5
        }
    
    async def calculate_risk_score(self, event_type: str, user_id: str, resource: str,
                                 action: str, success: bool, details: Dict[str, Any] = None,
                                 client_info: Dict[str, Any] = None) -> float:
        """Calculate risk score for security event"""
        base_score = 0.1  # Base risk score
        
        # Event type risk
        base_score += self.risk_patterns.get(event_type, 0.2)
        
        # Failed action increases risk
        if not success:
            base_score += 0.3
        
        # Time-based risk (outside business hours)
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:  # Outside 6 AM - 10 PM
            base_score += 0.2
        
        # IP address risk (simplified)
        if client_info and client_info.get("ip_address"):
            if self._is_suspicious_ip(client_info["ip_address"]):
                base_score += 0.4
        
        # Bulk access risk
        if details and details.get("record_count", 0) > 100:
            base_score += 0.3
        
        return min(1.0, base_score)  # Cap at 1.0
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious (simplified)"""
        # In production, check against threat intelligence feeds
        suspicious_patterns = ["10.0.0.", "192.168.", "127.0.0.1"]
        return not any(ip_address.startswith(pattern) for pattern in suspicious_patterns)

# Custom Exceptions
class SecurityException(Exception):
    """Base security exception"""
    pass

class AuthenticationException(SecurityException):
    """Authentication-related exception"""
    pass

class AuthorizationException(SecurityException):
    """Authorization-related exception"""
    pass

async def demonstrate_enterprise_security():
    """Comprehensive demonstration of enterprise security features"""
    print("=" * 80)
    print("AGNO ENTERPRISE SECURITY & COMPLIANCE DEMONSTRATION")
    print("=" * 80)
    
    # Initialize security services
    encryption_service = EncryptionService()
    auth_service = AuthenticationService(encryption_service)
    authz_service = AuthorizationService()
    data_protection = DataProtectionService(encryption_service)
    compliance_validator = ComplianceValidator()
    audit_logger = AuditLogger(encryption_service)
    
    print(f"\n1. Security Services Initialization")
    print("-" * 40)
    print(f"✓ Encryption Service")
    print(f"✓ Authentication Service")
    print(f"✓ Authorization Service (RBAC)")
    print(f"✓ Data Protection Service")
    print(f"✓ Compliance Validator")
    print(f"✓ Audit Logger")
    
    # User registration and authentication
    print(f"\n2. User Registration & Authentication")
    print("-" * 45)
    
    # Register test users
    analyst_user = auth_service.register_user(
        username="alice_analyst",
        email="alice@company.com",
        password="SecurePass123!",
        roles=["analyst"],
        departments=["data_science"]
    )
    
    admin_user = auth_service.register_user(
        username="bob_admin",
        email="bob@company.com",
        password="AdminPass456!",
        roles=["admin"],
        departments=["it"]
    )
    
    print(f"Registered users:")
    print(f"  - {analyst_user.username} (roles: {analyst_user.roles})")
    print(f"  - {admin_user.username} (roles: {admin_user.roles})")
    
    # Authenticate user
    auth_result = await auth_service.authenticate_user(
        username="alice_analyst",
        password="SecurePass123!",
        client_info={"ip_address": "192.168.1.100", "user_agent": "AgnoClient/1.0"}
    )
    
    print(f"Authentication result: {auth_result['status']}")
    print(f"Session expires: {auth_result['session']['expires_at']}")
    
    # Authorization setup
    print(f"\n3. Role-Based Access Control")
    print("-" * 35)
    
    # Assign roles to users
    authz_service.assign_role_to_user(analyst_user.user_id, "analyst")
    authz_service.assign_role_to_user(admin_user.user_id, "admin")
    
    # Test permissions
    can_read = authz_service.check_permission(
        analyst_user.user_id, "customer_data", AccessLevel.READ, 
        {"department": "data_science"}
    )
    can_admin = authz_service.check_permission(
        analyst_user.user_id, "system_config", AccessLevel.ADMIN
    )
    
    print(f"Analyst can read customer data: {can_read}")
    print(f"Analyst can admin system: {can_admin}")
    
    # Data classification and protection
    print(f"\n4. Data Classification & Protection")
    print("-" * 42)
    
    test_data = """
    Customer Information:
    Name: John Doe
    Email: john.doe@email.com
    SSN: 123-45-6789
    Credit Card: 4532-1234-5678-9012
    Phone: 555-123-4567
    Medical Record: MRN 12345
    """
    
    # Classify data
    classification = data_protection.classify_data(test_data)
    print(f"Data classification: {classification['primary_classification']}")
    print(f"All classifications found: {classification['all_classifications']}")
    print(f"Patterns detected: {len(classification['patterns_found']['pii'])} PII, "
          f"{len(classification['patterns_found']['phi'])} PHI")
    
    # Apply data protection
    try:
        protected = data_protection.apply_data_protection(
            test_data, classification,
            user_context={"roles": ["analyst"], "user_id": analyst_user.user_id}
        )
        print(f"Protection applied: {protected['protection_applied']}")
        print(f"Data anonymized: {'anonymization' in protected['protection_applied']}")
    
    except SecurityException as e:
        print(f"Data protection error: {e}")
    
    # Compliance validation
    print(f"\n5. Compliance Validation")
    print("-" * 30)
    
    compliance_request = {
        "data_subject_consent": True,
        "lawful_basis": "legitimate_interest",
        "minimum_necessary_justification": "Required for data analysis",
        "user_context": {"authorized_for_phi": True},
        "contains_cardholder_data": True,
        "pci_compliant_environment": True
    }
    
    compliance_result = compliance_validator.validate_request_compliance(
        compliance_request,
        [ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.PCI_DSS]
    )
    
    print(f"Overall compliant: {compliance_result['overall_compliant']}")
    print(f"Frameworks validated: {list(compliance_result['framework_results'].keys())}")
    if compliance_result['violations']:
        print(f"Violations found: {len(compliance_result['violations'])}")
        for violation in compliance_result['violations']:
            print(f"  - {violation}")
    
    # Audit logging
    print(f"\n6. Security Audit Logging")
    print("-" * 30)
    
    # Log various security events
    await audit_logger.log_security_event(
        event_type="user_login",
        user_id=analyst_user.user_id,
        resource="system",
        action="authenticate",
        success=True,
        details={"login_method": "password"},
        client_info={"ip_address": "192.168.1.100"}
    )
    
    await audit_logger.log_security_event(
        event_type="data_access",
        user_id=analyst_user.user_id,
        resource="customer_database",
        action="select",
        success=True,
        details={"record_count": 150, "classification": "PII"},
        client_info={"ip_address": "192.168.1.100"}
    )
    
    await audit_logger.log_security_event(
        event_type="failed_login",
        user_id="unknown_user",
        resource="system",
        action="authenticate",
        success=False,
        details={"reason": "invalid_password"},
        client_info={"ip_address": "203.0.113.1"}  # Suspicious external IP
    )
    
    # Generate audit reports
    audit_trail = audit_logger.get_audit_trail(
        start_date=datetime.utcnow() - timedelta(hours=1)
    )
    
    print(f"Audit events logged: {len(audit_trail)}")
    print(f"Event types:")
    event_types = set(event['event_type'] for event in audit_trail)
    for event_type in sorted(event_types):
        count = len([e for e in audit_trail if e['event_type'] == event_type])
        print(f"  - {event_type}: {count}")
    
    # Risk analysis
    high_risk_events = [e for e in audit_trail if e['risk_score'] > 0.7]
    print(f"High-risk events: {len(high_risk_events)}")
    
    # Encryption demonstration
    print(f"\n7. Data Encryption")
    print("-" * 25)
    
    sensitive_data = "Patient ID: 12345, Diagnosis: Confidential Medical Information"
    
    # Encrypt data
    encrypted = encryption_service.encrypt_data(sensitive_data, "patient_data_key")
    print(f"Original data length: {len(sensitive_data)} characters")
    print(f"Encrypted data length: {len(encrypted['encrypted_data'])} characters")
    print(f"Encryption algorithm: {encrypted['algorithm']}")
    
    # Decrypt data
    decrypted = encryption_service.decrypt_data(
        encrypted['encrypted_data'], 
        encrypted['key_id']
    ).decode('utf-8')
    print(f"Decryption successful: {decrypted == sensitive_data}")
    
    print(f"\n" + "=" * 80)
    print("ENTERPRISE SECURITY DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Security Features Demonstrated:")
    print("- Strong authentication with password complexity requirements")
    print("- Role-based access control (RBAC) with permission inheritance")
    print("- Automatic data classification with pattern recognition")
    print("- Data protection with encryption and anonymization")
    print("- Multi-framework compliance validation (GDPR, HIPAA, PCI DSS)")
    print("- Comprehensive security audit logging with risk scoring")
    print("- Advanced encryption with key derivation")
    print("- Enterprise-grade security policies and controls")

if __name__ == "__main__":
    # Run comprehensive demonstration
    asyncio.run(demonstrate_enterprise_security())