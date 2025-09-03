# ⚙️ Session 5 Advanced: Enterprise API Key Management

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths
> Time Investment: 2-3 hours
> Outcome: Master production-grade API key management systems

## Advanced Learning Outcomes

After completing this module, you will master:

- Cryptographically secure API key generation and storage  
- Enterprise key management with automatic rotation  
- Advanced usage tracking and analytics  
- Multi-tenant key isolation and rate limiting  

## The Enterprise API Key Vault

In the world of machine-to-machine communication, API keys are like diplomatic passports—they need to be secure, verifiable, and easily revocable when compromised. Let's build a system that treats each API key like a precious artifact.

### Advanced Key Management Architecture

Our enterprise API key manager handles millions of keys with perfect security and performance:

```python
# src/auth/api_keys.py

import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set
import uuid
import logging
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import redis

logger = logging.getLogger(__name__)

class EnterpriseAPIKeyManager:
    """Enterprise-grade API key management with advanced security features."""

    def __init__(self, redis_client, encryption_key: bytes = None):
        self.redis_client = redis_client
        self.key_prefix = "api_key:"
        self.default_expiry_days = 90
        self.key_length = 32  # 32 bytes = 256 bits of entropy

        # Initialize encryption for sensitive metadata
        self.encryption_key = encryption_key or self._derive_encryption_key()

        # Key rotation settings
        self.rotation_warning_days = 7
        self.max_keys_per_user = 10
```

The architecture supports encryption of sensitive metadata and automatic key rotation warnings.

### Cryptographically Secure Key Generation

The key generation process creates unpredictable, unique keys with comprehensive metadata:

```python
    def _generate_secure_key_components(self) -> tuple[str, str, str]:
        """Generate all secure components for a new API key."""
        key_id = str(uuid.uuid4())

        # Format: mcp_<environment>_<base64-url-safe-32-bytes>
        environment = os.getenv('ENVIRONMENT', 'dev')
        key_suffix = secrets.token_urlsafe(self.key_length)
        api_key = f"mcp_{environment}_{key_suffix}"

        # Generate additional security hash for verification
        verification_hash = self._generate_verification_hash(api_key, key_id)

        return key_id, api_key, verification_hash

    def _generate_verification_hash(self, api_key: str, key_id: str) -> str:
        """Generate verification hash for additional security layer."""
        combined = f"{api_key}:{key_id}:{secrets.token_hex(16)}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage using PBKDF2."""
        salt = b"mcp_api_key_salt_2025"  # In production: use unique salts
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # High iteration count for security
        )
        key_hash = kdf.derive(api_key.encode())
        return hashlib.sha256(key_hash).hexdigest()
```

PBKDF2 with high iteration counts provides resistance against rainbow table and brute force attacks.

### Comprehensive Key Metadata System

Each API key includes detailed metadata for auditing, monitoring, and management:

```python
    def _create_comprehensive_metadata(self, key_id: str, user_id: str,
                                     name: str, permissions: List[str],
                                     config: Dict[str, Any]) -> Dict:
        """Create comprehensive metadata for enterprise API key management."""
        now = datetime.now()

        base_metadata = {
            "key_id": key_id,
            "user_id": user_id,
            "organization_id": config.get("organization_id"),
            "project_id": config.get("project_id"),
            "name": name[:100],  # Limit name length
            "description": config.get("description", "")[:500],
            "permissions": permissions,
            "scopes": config.get("scopes", ["default"]),
            "rate_limits": config.get("rate_limits", self._get_default_rate_limits()),
            "created_at": now.isoformat(),
            "created_by": config.get("created_by", "system"),
            "expires_at": (now + timedelta(days=config.get("expiry_days", self.default_expiry_days))).isoformat(),
            "last_used": None,
            "usage_count": 0,
            "active": True,
            "tags": config.get("tags", []),
            "ip_whitelist": config.get("ip_whitelist", []),
            "environment": config.get("environment", os.getenv("ENVIRONMENT", "dev")),
            "rotation_schedule": config.get("rotation_schedule"),
            "security_tier": config.get("security_tier", "standard")
        }

        # Add usage tracking buckets
        base_metadata.update({
            "daily_usage": {},
            "monthly_usage": {},
            "error_count": 0,
            "last_error": None
        })

        return base_metadata

    def _get_default_rate_limits(self) -> Dict[str, int]:
        """Get default rate limits based on security tier."""
        return {
            "requests_per_minute": 1000,
            "requests_per_hour": 10000,
            "requests_per_day": 100000,
            "burst_limit": 50
        }
```

The comprehensive metadata enables sophisticated API key management, monitoring, and governance.

### Multi-Tenant Key Generation

Enterprise key generation supports multi-tenancy with isolation and governance:

```python
    def generate_enterprise_api_key(self, user_id: str, organization_id: str,
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enterprise API key with comprehensive governance."""

        # Validate user can create more keys
        if not self._can_create_key(user_id, organization_id):
            raise ValueError("Maximum number of keys reached for user/organization")

        # Validate permissions
        requested_permissions = config.get("permissions", [])
        if not self._validate_permissions(user_id, organization_id, requested_permissions):
            raise ValueError("Insufficient privileges for requested permissions")

        # Generate secure key components
        key_id, api_key, verification_hash = self._generate_secure_key_components()
        key_hash = self._hash_api_key(api_key)

        # Create comprehensive metadata
        config.update({
            "organization_id": organization_id,
            "verification_hash": verification_hash
        })

        metadata = self._create_comprehensive_metadata(
            key_id, user_id, config.get("name", "Unnamed Key"),
            requested_permissions, config
        )

        # Store with multi-level indexing
        self._store_enterprise_key(key_hash, metadata, organization_id, user_id)

        # Log key creation event
        logger.info(
            f"Enterprise API key generated",
            key_id=key_id,
            user_id=user_id,
            organization_id=organization_id,
            permissions=requested_permissions
        )

        return {
            "api_key": api_key,
            "key_id": key_id,
            "verification_hash": verification_hash,
            "expires_at": metadata["expires_at"],
            "rate_limits": metadata["rate_limits"],
            "scopes": metadata["scopes"]
        }
```

Multi-tenant support ensures proper isolation and governance across organizations.

### Advanced Validation with Performance Optimization

The validation system includes comprehensive security checks with caching for performance:

```python
    def validate_enterprise_api_key(self, api_key: str,
                                   request_context: Dict[str, Any]) -> Optional[Dict]:
        """Validate API key with comprehensive security and performance optimization."""

        # Step 1: Format and structure validation
        if not self._is_valid_enterprise_key_format(api_key):
            return None

        try:
            # Step 2: Check cache first for performance
            cached_result = self._get_cached_validation(api_key)
            if cached_result:
                return self._update_cached_usage(cached_result, request_context)

            # Step 3: Full validation from storage
            metadata = self._get_enterprise_key_metadata(api_key)
            if not metadata:
                return None

            # Step 4: Comprehensive security checks
            validation_result = self._perform_security_checks(metadata, request_context)
            if not validation_result["valid"]:
                logger.warning("API key security check failed",
                             reason=validation_result["reason"],
                             key_id=metadata.get("key_id"))
                return None

            # Step 5: Update usage and cache successful validation
            self._update_enterprise_key_usage(api_key, metadata, request_context)
            self._cache_validation_result(api_key, metadata)

            return metadata

        except Exception as e:
            logger.error(f"Enterprise API key validation error: {e}")
            self._increment_error_metrics(api_key)
            return None

    def _perform_security_checks(self, metadata: Dict,
                                request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive security checks on API key usage."""

        # Check 1: Key status and expiration
        if not metadata.get("active", False):
            return {"valid": False, "reason": "key_inactive"}

        if self._is_key_expired(metadata):
            return {"valid": False, "reason": "key_expired"}

        # Check 2: IP whitelist validation
        client_ip = request_context.get("client_ip")
        if metadata.get("ip_whitelist") and client_ip:
            if not self._is_ip_whitelisted(client_ip, metadata["ip_whitelist"]):
                return {"valid": False, "reason": "ip_not_whitelisted"}

        # Check 3: Environment validation
        request_env = request_context.get("environment")
        if request_env and metadata.get("environment"):
            if request_env != metadata["environment"]:
                return {"valid": False, "reason": "environment_mismatch"}

        # Check 4: Rate limiting
        if not self._check_rate_limits(metadata, request_context):
            return {"valid": False, "reason": "rate_limit_exceeded"}

        # Check 5: Scope validation
        requested_scope = request_context.get("scope")
        if requested_scope:
            if not self._is_scope_authorized(requested_scope, metadata["scopes"]):
                return {"valid": False, "reason": "scope_not_authorized"}

        return {"valid": True, "reason": "all_checks_passed"}
```

The comprehensive security checks ensure API keys are used only within authorized contexts.

### Advanced Usage Analytics and Monitoring

Track detailed usage patterns for security monitoring and capacity planning:

```python
    def _update_enterprise_key_usage(self, api_key: str, metadata: Dict,
                                    request_context: Dict[str, Any]):
        """Update comprehensive usage statistics and analytics."""
        try:
            key_hash = self._hash_api_key(api_key)
            redis_key = f"{self.key_prefix}{key_hash}"
            current_time = datetime.now()

            # Update basic usage stats
            metadata["last_used"] = current_time.isoformat()
            metadata["usage_count"] = metadata.get("usage_count", 0) + 1

            # Update time-based usage buckets
            self._update_usage_buckets(metadata, current_time, request_context)

            # Update geolocation tracking (if enabled)
            if request_context.get("track_location"):
                self._update_location_usage(metadata, request_context)

            # Update endpoint usage patterns
            endpoint = request_context.get("endpoint")
            if endpoint:
                self._update_endpoint_usage(metadata, endpoint)

            # Store updated metadata with preserved TTL
            ttl = self.redis_client.ttl(redis_key)
            if ttl > 0:
                self.redis_client.setex(redis_key, ttl, json.dumps(metadata))
            else:
                # Fallback: calculate TTL from expiry
                ttl_seconds = self._calculate_ttl_from_expiry(metadata)
                self.redis_client.setex(redis_key, ttl_seconds, json.dumps(metadata))

        except Exception as e:
            logger.warning(f"Failed to update enterprise key usage: {e}")

    def _update_usage_buckets(self, metadata: Dict, current_time: datetime,
                             request_context: Dict[str, Any]):
        """Update time-based usage analytics buckets."""

        # Daily usage bucket
        day_key = current_time.strftime("%Y-%m-%d")
        daily_usage = metadata.setdefault("daily_usage", {})
        daily_usage[day_key] = daily_usage.get(day_key, 0) + 1

        # Monthly usage bucket
        month_key = current_time.strftime("%Y-%m")
        monthly_usage = metadata.setdefault("monthly_usage", {})
        monthly_usage[month_key] = monthly_usage.get(month_key, 0) + 1

        # Clean old usage data (keep only recent history)
        self._cleanup_old_usage_data(daily_usage, monthly_usage, current_time)

        # Update usage patterns for anomaly detection
        self._update_usage_patterns(metadata, current_time, request_context)
```

Detailed usage analytics enable sophisticated monitoring and anomaly detection.

### Automatic Key Rotation System

Implement automatic key rotation for enhanced security:

```python
    def schedule_key_rotation(self, key_id: str, rotation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule automatic key rotation for enhanced security."""

        metadata = self._get_key_metadata_by_id(key_id)
        if not metadata:
            raise ValueError(f"Key not found: {key_id}")

        # Validate rotation permissions
        if not self._can_rotate_key(metadata):
            raise ValueError("Insufficient privileges for key rotation")

        rotation_schedule = {
            "enabled": True,
            "interval_days": rotation_config.get("interval_days", 90),
            "warning_days": rotation_config.get("warning_days", 7),
            "next_rotation": (datetime.now() + timedelta(days=rotation_config.get("interval_days", 90))).isoformat(),
            "auto_rotate": rotation_config.get("auto_rotate", False),
            "notify_users": rotation_config.get("notify_users", True)
        }

        # Update metadata with rotation schedule
        metadata["rotation_schedule"] = rotation_schedule
        self._store_updated_metadata(metadata)

        # Schedule background rotation job
        self._schedule_rotation_job(key_id, rotation_schedule)

        logger.info(f"Key rotation scheduled for key {key_id}")
        return rotation_schedule

    def perform_key_rotation(self, key_id: str) -> Dict[str, str]:
        """Perform automatic key rotation with overlap period."""

        old_metadata = self._get_key_metadata_by_id(key_id)
        if not old_metadata:
            raise ValueError(f"Key not found: {key_id}")

        # Generate new key with same configuration
        new_key_config = {
            "name": f"{old_metadata['name']} (Rotated)",
            "permissions": old_metadata["permissions"],
            "scopes": old_metadata["scopes"],
            "rate_limits": old_metadata["rate_limits"],
            "organization_id": old_metadata["organization_id"],
            "project_id": old_metadata["project_id"],
            "expiry_days": self.default_expiry_days
        }

        # Create new key
        new_key_result = self.generate_enterprise_api_key(
            old_metadata["user_id"],
            old_metadata["organization_id"],
            new_key_config
        )

        # Set overlap period for graceful transition
        overlap_days = 7
        old_metadata["rotation_info"] = {
            "rotated_at": datetime.now().isoformat(),
            "new_key_id": new_key_result["key_id"],
            "expires_at": (datetime.now() + timedelta(days=overlap_days)).isoformat()
        }

        # Mark old key for deprecation
        old_metadata["active"] = False
        old_metadata["deprecated"] = True
        self._store_updated_metadata(old_metadata)

        # Notify users about rotation
        if old_metadata.get("rotation_schedule", {}).get("notify_users", True):
            self._send_rotation_notification(old_metadata, new_key_result)

        logger.info(f"Key rotation completed: {key_id} -> {new_key_result['key_id']}")

        return {
            "old_key_id": key_id,
            "new_key_id": new_key_result["key_id"],
            "new_api_key": new_key_result["api_key"],
            "overlap_expires_at": old_metadata["rotation_info"]["expires_at"]
        }
```

Automatic rotation ensures keys are regularly refreshed while maintaining service continuity.

## Enterprise Governance Features

### Multi-Level Key Management

Implement organizational hierarchy for key governance:

```python
    def get_organization_keys(self, organization_id: str,
                             filters: Dict[str, Any] = None) -> List[Dict]:
        """Retrieve all API keys for an organization with filtering."""

        try:
            # Get all keys for organization
            org_key_pattern = f"org:{organization_id}:keys:*"
            key_refs = self.redis_client.keys(org_key_pattern)

            keys = []
            for key_ref in key_refs:
                key_hash = key_ref.decode().split(":")[-1]
                metadata = self._get_metadata_by_hash(key_hash)
                if metadata and self._matches_filters(metadata, filters):
                    # Remove sensitive information
                    safe_metadata = self._sanitize_metadata_for_listing(metadata)
                    keys.append(safe_metadata)

            return sorted(keys, key=lambda x: x["created_at"], reverse=True)

        except Exception as e:
            logger.error(f"Failed to retrieve organization keys: {e}")
            return []

    def bulk_key_operation(self, organization_id: str, operation: str,
                          key_ids: List[str], config: Dict[str, Any] = None) -> Dict[str, List]:
        """Perform bulk operations on multiple API keys."""

        results = {
            "successful": [],
            "failed": []
        }

        for key_id in key_ids:
            try:
                if operation == "deactivate":
                    self.deactivate_key(key_id, config)
                elif operation == "rotate":
                    self.perform_key_rotation(key_id)
                elif operation == "update_permissions":
                    self.update_key_permissions(key_id, config.get("permissions", []))
                else:
                    raise ValueError(f"Unknown operation: {operation}")

                results["successful"].append(key_id)

            except Exception as e:
                logger.error(f"Bulk operation failed for key {key_id}: {e}")
                results["failed"].append({"key_id": key_id, "error": str(e)})

        return results
```

Bulk operations enable efficient management of large numbers of API keys.

---

## 🧭 Navigation

**Previous:** [Session 4 - Team Orchestration →](Session4_*.md)  
**Next:** [Session 6 - Modular Architecture →](Session6_*.md)

---
