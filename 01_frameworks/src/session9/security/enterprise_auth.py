"""
Enterprise Authentication and Authorization System
Comprehensive security framework for production agent systems.
"""

from typing import Dict, List, Optional, Set, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import jwt
import bcrypt
import asyncio
import logging
import time
import secrets
import hashlib
import os
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationMethod(Enum):
    """Supported authentication methods."""
    BASIC = "basic"
    OAUTH2 = "oauth2"
    SAML = "saml"
    LDAP = "ldap"
    MFA = "mfa"
    CERTIFICATE = "certificate"
    API_KEY = "api_key"

class SessionStatus(Enum):
    """Session status values."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    LOCKED = "locked"

@dataclass
class UserProfile:
    """Comprehensive user profile with enterprise attributes."""
    user_id: str
    username: str
    email: str
    full_name: str
    department: str
    job_title: str
    manager_id: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserContext:
    """User authentication and authorization context."""
    user_id: str
    username: str
    email: str
    roles: Set[str]
    permissions: Set[str]
    department: str
    security_clearance: str
    session_id: str
    ip_address: str
    user_agent: str
    mfa_verified: bool = False
    last_authenticated: Optional[datetime] = None
    session_expires: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    profile: Optional[UserProfile] = None

@dataclass
class AuthenticationResult:
    """Result of authentication attempt."""
    success: bool
    user_context: Optional[UserContext] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    error_message: Optional[str] = None
    requires_mfa: bool = False
    mfa_methods: List[str] = field(default_factory=list)
    account_locked: bool = False
    password_expired: bool = False

class AuthenticationError(Exception):
    """Authentication-related errors."""
    pass

class AuthorizationError(Exception):
    """Authorization-related errors."""
    pass

class MFAProvider(ABC):
    """Abstract base for MFA providers."""
    
    @abstractmethod
    async def generate_challenge(self, user_id: str) -> Dict[str, Any]:
        """Generate MFA challenge for user."""
        pass
    
    @abstractmethod
    async def verify_response(self, user_id: str, challenge: str, response: str) -> bool:
        """Verify MFA response."""
        pass

class TOTPMFAProvider(MFAProvider):
    """Time-based One-Time Password MFA provider."""
    
    def __init__(self):
        self.user_secrets: Dict[str, str] = {}  # In production, store securely
    
    async def generate_challenge(self, user_id: str) -> Dict[str, Any]:
        """Generate TOTP challenge."""
        if user_id not in self.user_secrets:
            # Generate new secret for user
            secret = secrets.token_urlsafe(32)
            self.user_secrets[user_id] = secret
        
        return {
            "type": "totp",
            "message": "Please enter the 6-digit code from your authenticator app",
            "setup_required": user_id not in self.user_secrets
        }
    
    async def verify_response(self, user_id: str, challenge: str, response: str) -> bool:
        """Verify TOTP code."""
        # Simplified TOTP verification (in production use proper TOTP library)
        if user_id not in self.user_secrets:
            return False
        
        # For demo purposes, accept specific codes
        valid_codes = ["123456", "654321", "000000"]
        return response in valid_codes

class SMSMFAProvider(MFAProvider):
    """SMS-based MFA provider."""
    
    def __init__(self):
        self.pending_codes: Dict[str, str] = {}
    
    async def generate_challenge(self, user_id: str) -> Dict[str, Any]:
        """Generate SMS challenge."""
        # Generate 6-digit code
        code = f"{secrets.randbelow(900000) + 100000:06d}"
        self.pending_codes[user_id] = code
        
        # In production, send SMS via SMS provider
        logger.info(f"SMS code for {user_id}: {code} (demo mode)")
        
        return {
            "type": "sms",
            "message": "A verification code has been sent to your phone",
            "code_length": 6
        }
    
    async def verify_response(self, user_id: str, challenge: str, response: str) -> bool:
        """Verify SMS code."""
        expected_code = self.pending_codes.get(user_id)
        if not expected_code:
            return False
        
        # Clean up used code
        del self.pending_codes[user_id]
        
        return response == expected_code

class SessionManager:
    """Manages user sessions with enterprise security features."""
    
    def __init__(self, secret_key: str, session_timeout_hours: int = 8):
        self.secret_key = secret_key
        self.session_timeout = timedelta(hours=session_timeout_hours)
        self.active_sessions: Dict[str, UserContext] = {}
        self.session_history: List[Dict[str, Any]] = []
        
    def create_session(self, user_context: UserContext) -> str:
        """Create new user session."""
        session_id = secrets.token_urlsafe(32)
        user_context.session_id = session_id
        user_context.session_expires = datetime.now() + self.session_timeout
        
        self.active_sessions[session_id] = user_context
        
        # Log session creation
        self.session_history.append({
            "event": "session_created",
            "session_id": session_id,
            "user_id": user_context.user_id,
            "timestamp": datetime.now().isoformat(),
            "ip_address": user_context.ip_address
        })
        
        logger.info(f"Created session for user {user_context.username}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserContext]:
        """Get active session."""
        if session_id not in self.active_sessions:
            return None
        
        user_context = self.active_sessions[session_id]
        
        # Check if session expired
        if (user_context.session_expires and 
            datetime.now() > user_context.session_expires):
            self.revoke_session(session_id)
            return None
        
        return user_context
    
    def refresh_session(self, session_id: str) -> bool:
        """Refresh session expiration."""
        if session_id not in self.active_sessions:
            return False
        
        user_context = self.active_sessions[session_id]
        user_context.session_expires = datetime.now() + self.session_timeout
        
        return True
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke user session."""
        if session_id not in self.active_sessions:
            return False
        
        user_context = self.active_sessions[session_id]
        del self.active_sessions[session_id]
        
        # Log session revocation
        self.session_history.append({
            "event": "session_revoked",
            "session_id": session_id,
            "user_id": user_context.user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Revoked session for user {user_context.username}")
        return True
    
    def revoke_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user."""
        sessions_to_revoke = [
            sid for sid, ctx in self.active_sessions.items() 
            if ctx.user_id == user_id
        ]
        
        for session_id in sessions_to_revoke:
            self.revoke_session(session_id)
        
        return len(sessions_to_revoke)
    
    def get_active_sessions(self, user_id: str = None) -> List[UserContext]:
        """Get active sessions (optionally filtered by user)."""
        sessions = list(self.active_sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        return sessions

class EnterpriseAuthManager:
    """Comprehensive authentication and authorization manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session_manager = SessionManager(
            secret_key=config.get("secret_key", "dev-secret-key"),
            session_timeout_hours=config.get("session_timeout_hours", 8)
        )
        
        # User storage (in production, use proper database)
        self.users: Dict[str, Dict[str, Any]] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Security tracking
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.blacklisted_tokens: Set[str] = set()
        
        # MFA providers
        self.mfa_providers = {
            "totp": TOTPMFAProvider(),
            "sms": SMSMFAProvider()
        }
        
        # Configuration
        self.max_failed_attempts = config.get("max_failed_attempts", 5)
        self.lockout_duration_minutes = config.get("lockout_duration_minutes", 15)
        self.password_expiry_days = config.get("password_expiry_days", 90)
        
        # Create demo users
        self._create_demo_users()
    
    def _create_demo_users(self):
        """Create demo users for testing."""
        # Only create demo users if explicitly enabled
        if not os.environ.get("CREATE_DEMO_USERS", "").lower() == "true":
            logger.info("Demo users creation disabled. Set CREATE_DEMO_USERS=true to enable.")
            return
            
        demo_password = os.environ.get("DEMO_PASSWORD", secrets.token_urlsafe(16))
        logger.info(f"Demo users password: {demo_password}")
        
        demo_users = [
            {
                "username": os.environ.get("DEMO_ADMIN_USER", "admin"),
                "email": os.environ.get("DEMO_ADMIN_EMAIL", "admin@company.com"),
                "full_name": "System Administrator",
                "department": "IT",
                "job_title": "System Administrator",
                "roles": {"admin", "user"},
                "security_clearance": "high"
            },
            {
                "username": os.environ.get("DEMO_ANALYST_USER", "analyst"),
                "email": os.environ.get("DEMO_ANALYST_EMAIL", "analyst@company.com"), 
                "full_name": "Data Analyst",
                "department": "Analytics",
                "job_title": "Senior Data Analyst",
                "roles": {"analyst", "user"},
                "security_clearance": "medium"
            },
            {
                "username": os.environ.get("DEMO_VIEWER_USER", "viewer"),
                "email": os.environ.get("DEMO_VIEWER_EMAIL", "viewer@company.com"),
                "full_name": "Report Viewer",
                "department": "Business",
                "job_title": "Business Analyst",
                "roles": {"viewer"},
                "security_clearance": "low"
            }
        ]
        
        for user_data in demo_users:
            self.create_user(
                username=user_data["username"],
                email=user_data["email"],
                password=demo_password,
                full_name=user_data["full_name"],
                department=user_data["department"],
                job_title=user_data["job_title"],
                roles=user_data["roles"],
                security_clearance=user_data["security_clearance"]
            )
    
    def create_user(self, username: str, email: str, password: str,
                   full_name: str, department: str, job_title: str,
                   roles: Set[str] = None, security_clearance: str = "low",
                   **kwargs) -> str:
        """Create a new user."""
        user_id = secrets.token_urlsafe(16)
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # Create user record
        self.users[username] = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "roles": roles or {"user"},
            "security_clearance": security_clearance,
            "created_at": datetime.now(),
            "is_active": True,
            "password_changed_at": datetime.now(),
            "mfa_enabled": False,
            "mfa_methods": []
        }
        
        # Create user profile
        self.user_profiles[user_id] = UserProfile(
            user_id=user_id,
            username=username,
            email=email,
            full_name=full_name,
            department=department,
            job_title=job_title,
            **kwargs
        )
        
        logger.info(f"Created user: {username}")
        return user_id
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts."""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        
        # Clean old attempts (older than lockout duration)
        cutoff_time = datetime.now() - timedelta(minutes=self.lockout_duration_minutes)
        attempts[:] = [attempt for attempt in attempts if attempt > cutoff_time]
        
        return len(attempts) >= self.max_failed_attempts
    
    def _record_failed_attempt(self, username: str):
        """Record a failed authentication attempt."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(datetime.now())
    
    def _clear_failed_attempts(self, username: str):
        """Clear failed attempts for successful authentication."""
        if username in self.failed_attempts:
            self.failed_attempts[username] = []
    
    async def authenticate(self, credentials: Dict[str, Any],
                         ip_address: str = "unknown",
                         user_agent: str = "unknown") -> AuthenticationResult:
        """Authenticate user with comprehensive security checks."""
        auth_method = credentials.get("method", "basic")
        username = credentials.get("username", "")
        
        try:
            # Check for account lockout
            if self._is_account_locked(username):
                return AuthenticationResult(
                    success=False,
                    error_message="Account locked due to too many failed attempts",
                    account_locked=True
                )
            
            # Route to appropriate authentication method
            if auth_method == AuthenticationMethod.BASIC.value:
                result = await self._authenticate_basic(credentials, ip_address, user_agent)
            elif auth_method == AuthenticationMethod.API_KEY.value:
                result = await self._authenticate_api_key(credentials, ip_address, user_agent)
            else:
                result = AuthenticationResult(
                    success=False,
                    error_message=f"Unsupported authentication method: {auth_method}"
                )
            
            # Handle authentication result
            if result.success:
                self._clear_failed_attempts(username)
            else:
                self._record_failed_attempt(username)
            
            return result
            
        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            self._record_failed_attempt(username)
            return AuthenticationResult(
                success=False,
                error_message="Authentication service error"
            )
    
    async def _authenticate_basic(self, credentials: Dict[str, Any],
                                ip_address: str, user_agent: str) -> AuthenticationResult:
        """Authenticate using username/password."""
        username = credentials.get("username", "")
        password = credentials.get("password", "")
        
        if not username or not password:
            return AuthenticationResult(
                success=False,
                error_message="Username and password required"
            )
        
        # Check if user exists
        if username not in self.users:
            return AuthenticationResult(
                success=False,
                error_message="Invalid credentials"
            )
        
        user_data = self.users[username]
        
        # Check if user is active
        if not user_data.get("is_active", True):
            return AuthenticationResult(
                success=False,
                error_message="Account disabled"
            )
        
        # Verify password
        password_hash = user_data["password_hash"]
        if not bcrypt.checkpw(password.encode(), password_hash.encode()):
            return AuthenticationResult(
                success=False,
                error_message="Invalid credentials"
            )
        
        # Check password expiry
        password_changed_at = user_data.get("password_changed_at")
        if password_changed_at:
            password_age = datetime.now() - password_changed_at
            if password_age.days > self.password_expiry_days:
                return AuthenticationResult(
                    success=False,
                    error_message="Password expired",
                    password_expired=True
                )
        
        # Create user context
        user_context = UserContext(
            user_id=user_data["user_id"],
            username=username,
            email=user_data["email"],
            roles=user_data["roles"],
            permissions=self._get_user_permissions(user_data["roles"]),
            department=self.user_profiles[user_data["user_id"]].department,
            security_clearance=user_data["security_clearance"],
            session_id="",  # Will be set by session manager
            ip_address=ip_address,
            user_agent=user_agent,
            last_authenticated=datetime.now(),
            profile=self.user_profiles[user_data["user_id"]]
        )
        
        # Check if MFA is required
        if user_data.get("mfa_enabled", False):
            return AuthenticationResult(
                success=False,
                requires_mfa=True,
                mfa_methods=user_data.get("mfa_methods", ["totp"]),
                user_context=user_context
            )
        
        # Create session
        session_id = self.session_manager.create_session(user_context)
        
        # Generate JWT token
        token = self._generate_jwt_token(user_context)
        
        return AuthenticationResult(
            success=True,
            user_context=user_context,
            token=token
        )
    
    async def _authenticate_api_key(self, credentials: Dict[str, Any],
                                  ip_address: str, user_agent: str) -> AuthenticationResult:
        """Authenticate using API key."""
        api_key = credentials.get("api_key", "")
        
        if not api_key:
            return AuthenticationResult(
                success=False,
                error_message="API key required"
            )
        
        # In production, store API keys securely with user mapping
        # For demo, use environment-based API keys with hashing
        import hashlib
        
        # Get API keys from environment variables
        admin_api_key = os.environ.get("ADMIN_API_KEY", "admin-api-key-123")
        analyst_api_key = os.environ.get("ANALYST_API_KEY", "analyst-api-key-456")
        
        api_key_users = {
            hashlib.sha256(admin_api_key.encode()).hexdigest(): os.environ.get("DEMO_ADMIN_USER", "admin"),
            hashlib.sha256(analyst_api_key.encode()).hexdigest(): os.environ.get("DEMO_ANALYST_USER", "analyst")
        }
        
        # Hash the provided API key for comparison
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if api_key_hash not in api_key_users:
            return AuthenticationResult(
                success=False,
                error_message="Invalid API key"
            )
        
        username = api_key_users[api_key_hash]
        
        # Direct authentication for API keys - no password verification needed
        if username not in self.users:
            return AuthenticationResult(
                success=False,
                error_message="Invalid API key mapping"
            )
        
        user_data = self.users[username]
        
        # Check if user is active
        if not user_data.get("is_active", True):
            return AuthenticationResult(
                success=False,
                error_message="Account disabled"
            )
        
        # Create user context directly
        user_context = UserContext(
            user_id=user_data["user_id"],
            username=username,
            email=user_data["email"],
            roles=user_data["roles"],
            permissions=self._get_user_permissions(user_data["roles"]),
            department=self.user_profiles[user_data["user_id"]].department,
            security_clearance=user_data["security_clearance"],
            session_id="",  # Will be set by session manager
            ip_address=ip_address,
            user_agent=user_agent,
            last_authenticated=datetime.now(),
            profile=self.user_profiles[user_data["user_id"]]
        )
        
        # Create session
        session_id = self.session_manager.create_session(user_context)
        
        # Generate JWT token
        token = self._generate_jwt_token(user_context)
        
        return AuthenticationResult(
            success=True,
            user_context=user_context,
            token=token
        )
    
    def _get_user_permissions(self, roles: Set[str]) -> Set[str]:
        """Get permissions based on user roles."""
        role_permissions = {
            "admin": {
                "read:all", "write:all", "delete:all", "admin:system",
                "manage:users", "manage:roles", "view:logs"
            },
            "analyst": {
                "read:data", "write:data", "read:reports", "create:reports"
            },
            "user": {
                "read:own", "write:own"
            },
            "viewer": {
                "read:reports"
            }
        }
        
        permissions = set()
        for role in roles:
            permissions.update(role_permissions.get(role, set()))
        
        return permissions
    
    def _generate_jwt_token(self, user_context: UserContext) -> str:
        """Generate JWT token for user."""
        payload = {
            "user_id": user_context.user_id,
            "username": user_context.username,
            "roles": list(user_context.roles),
            "session_id": user_context.session_id,
            "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.now().timestamp())
        }
        
        return jwt.encode(
            payload,
            self.session_manager.secret_key,
            algorithm="HS256"
        )
    
    def verify_jwt_token(self, token: str) -> Optional[UserContext]:
        """Verify JWT token and return user context."""
        try:
            if token in self.blacklisted_tokens:
                return None
            
            payload = jwt.decode(
                token,
                self.session_manager.secret_key,
                algorithms=["HS256"]
            )
            
            session_id = payload.get("session_id")
            if not session_id:
                return None
            
            return self.session_manager.get_session(session_id)
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    async def verify_mfa(self, username: str, mfa_method: str, 
                        challenge: str, response: str) -> bool:
        """Verify MFA response."""
        if mfa_method not in self.mfa_providers:
            return False
        
        provider = self.mfa_providers[mfa_method]
        return await provider.verify_response(username, challenge, response)
    
    def logout(self, session_id: str) -> bool:
        """Logout user by revoking session."""
        return self.session_manager.revoke_session(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[UserContext]:
        """Get active sessions for user."""
        return self.session_manager.get_active_sessions(user_id)

# Example usage and demo
async def demo_enterprise_auth():
    """Demonstrate enterprise authentication system."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    console.print(Panel.fit(
        "🔐 Enterprise Authentication Demo\n"
        "Demonstrating secure authentication and authorization",
        title="Security System",
        border_style="blue"
    ))
    
    # Create auth manager
    config = {
        "secret_key": "demo-secret-key-12345",
        "session_timeout_hours": 8,
        "max_failed_attempts": 3,
        "lockout_duration_minutes": 5
    }
    
    auth_manager = EnterpriseAuthManager(config)
    
    # Test authentication scenarios
    test_scenarios = [
        ("Valid admin login", "admin", "password123", True),
        ("Valid analyst login", "analyst", "password123", True),
        ("Invalid password", "admin", "wrongpassword", False),
        ("Non-existent user", "hacker", "password123", False),
        ("API key auth", None, None, True)  # Special case for API key
    ]
    
    console.print("\n🧪 Testing Authentication Scenarios:")
    
    auth_table = Table(title="Authentication Test Results")
    auth_table.add_column("Scenario", style="cyan")
    auth_table.add_column("Username", style="yellow")
    auth_table.add_column("Result", style="green")
    auth_table.add_column("Details", style="blue")
    
    for scenario, username, password, should_succeed in test_scenarios:
        if scenario == "API key auth":
            # Test API key authentication
            credentials = {
                "method": "api_key",
                "api_key": "admin-api-key-123"
            }
        else:
            credentials = {
                "method": "basic",
                "username": username,
                "password": password
            }
        
        result = await auth_manager.authenticate(
            credentials,
            ip_address="127.0.0.1",
            user_agent="Demo-Client/1.0"
        )
        
        success_icon = "✅" if result.success else "❌"
        expected_icon = "✅" if should_succeed else "❌"
        
        details = []
        if result.success:
            details.append(f"Token generated")
            if result.user_context:
                details.append(f"Roles: {', '.join(result.user_context.roles)}")
        else:
            details.append(result.error_message or "Authentication failed")
        
        auth_table.add_row(
            scenario,
            username or "API Key",
            f"{success_icon} ({expected_icon} expected)",
            " | ".join(details)
        )
    
    console.print(auth_table)
    
    # Test session management
    console.print("\n🎫 Testing Session Management:")
    
    # Create a valid session
    admin_creds = {"method": "basic", "username": "admin", "password": "password123"}
    admin_result = await auth_manager.authenticate(admin_creds, "127.0.0.1", "Demo")
    
    if admin_result.success:
        session_id = admin_result.user_context.session_id
        console.print(f"✅ Created session: {session_id[:16]}...")
        
        # Test token verification
        if admin_result.token:
            verified_context = auth_manager.verify_jwt_token(admin_result.token)
            if verified_context:
                console.print("✅ JWT token verification successful")
            else:
                console.print("❌ JWT token verification failed")
        
        # Test logout
        logout_success = auth_manager.logout(session_id)
        if logout_success:
            console.print("✅ Logout successful")
        else:
            console.print("❌ Logout failed")
    
    # Display user information
    console.print("\n👥 Demo Users Created:")
    
    users_table = Table(title="Available Demo Users")
    users_table.add_column("Username", style="cyan")
    users_table.add_column("Email", style="yellow")
    users_table.add_column("Department", style="green")
    users_table.add_column("Roles", style="blue")
    users_table.add_column("Security Level", style="magenta")
    
    for username, user_data in auth_manager.users.items():
        profile = auth_manager.user_profiles[user_data["user_id"]]
        
        users_table.add_row(
            username,
            user_data["email"],
            profile.department,
            ", ".join(user_data["roles"]),
            user_data["security_clearance"]
        )
    
    console.print(users_table)

if __name__ == "__main__":
    asyncio.run(demo_enterprise_auth())