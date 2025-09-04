# ⚙️ Session 2 Advanced: Enterprise Security Patterns

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths
> Time Investment: 2-3 hours
> Outcome: Deep mastery of file system security architecture

## Advanced Learning Outcomes

After completing this advanced module, you will master:

- **Content-Based File Validation**: Advanced MIME type detection and content analysis  
- **Enterprise Audit Systems**: Comprehensive logging and monitoring infrastructure  
- **Rate Limiting & DoS Protection**: Production-grade resource management  
- **Advanced Filename Security**: Comprehensive injection prevention patterns  

## Content-Based File Validation

File extensions can be easily faked - a malicious executable could be named `document.txt`. Content-based validation examines actual file bytes to determine the true file type, preventing disguised malicious files.

### Advanced File Type Detection Implementation

Create enterprise-grade file validation that examines actual content:

```python
# utils/validators.py - Content-based security validation
from pathlib import Path
from typing import Dict, Any
import magic
import hashlib

class FileValidator:
    """Enterprise-grade file validation with content analysis."""

    def __init__(self, config):
        self.config = config
        # Initialize content-based MIME detection (more secure than extensions)
        self.mime_detector = magic.Magic(mime=True)
```

**Security Enhancement**: Using both MIME type detection and file description provides double validation against disguised malicious files.

Add descriptive file type detection:

```python
        # Initialize descriptive file type detection
        self.file_detector = magic.Magic()
```

### Resource Protection Validation

Implement comprehensive resource limit checking:

```python
    def validate_file_size(self, path: Path) -> Dict[str, Any]:
        """Comprehensive file size validation with detailed metrics."""
        try:
            file_size = path.stat().st_size

            # Check against configured limits
            size_valid = file_size <= self.config.max_file_size

            return {
                'size_valid': size_valid,
                'size_bytes': file_size,
                'size_human': self._format_file_size(file_size),
                'limit_bytes': self.config.max_file_size,
                'utilization_percent': (file_size / self.config.max_file_size) * 100
            }
        except (OSError, PermissionError):
            return {'size_valid': False, 'error': 'Cannot access file'}
```

Add human-readable file size formatting:

```python
    def _format_file_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
```

### Advanced File Type Detection

Check both file extension and actual content for security:

```python
    def validate_file_type(self, path: Path) -> Dict[str, Any]:
        """
        Validate file type and return metadata.

        We check both extension AND content to prevent disguised files.
        """
        extension = path.suffix.lower()

        # Get MIME type by reading file content (more secure than trusting extension)
        mime_type = self.mime_detector.from_file(str(path))

        # Check against allowed extensions
        allowed = extension in self.config.allowed_extensions
```

Properly categorize files for appropriate handling:

```python
        # Detect if file is text or binary for proper handling
        is_text = mime_type.startswith('text/') or mime_type in [
            'application/json', 'application/xml', 'application/yaml'
        ]

        return {
            "allowed": allowed,
            "extension": extension,
            "mime_type": mime_type,
            "is_text": is_text,
            "is_binary": not is_text
        }
```

### File Integrity Verification

Add checksum calculation for file integrity:

```python
    def calculate_checksum(self, path: Path) -> str:
        """
        Calculate SHA256 checksum of file.

        Useful for integrity verification and change detection.
        """
        sha256_hash = hashlib.sha256()

        # Read in chunks to handle large files efficiently
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()
```

## Enterprise Audit Systems

### Comprehensive Security Audit Implementation

Create advanced audit logging for compliance and security monitoring:

```python
# security/audit.py - Enterprise audit logging
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class SecurityAuditor:
    """
    Enterprise-grade security audit system.

    Provides SOC2/ISO27001 compliant logging and monitoring.
    """

    def __init__(self, config):
        self.config = config
        self.setup_audit_logging()
```

Configure structured logging for security events:

```python
    def setup_audit_logging(self):
        """Configure structured security audit logging."""
        # Create audit log directory
        audit_dir = Path("logs/audit")
        audit_dir.mkdir(parents=True, exist_ok=True)

        # Configure audit logger with rotation
        self.audit_logger = logging.getLogger('security.audit')
        self.audit_logger.setLevel(logging.INFO)

        # Create file handler with daily rotation
        handler = logging.FileHandler(
            audit_dir / f"security-audit-{datetime.now().strftime('%Y-%m-%d')}.log"
        )

        # Use JSON format for structured logging
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)
```

### Security Event Logging

Implement comprehensive security event tracking:

```python
    def log_security_event(self, event_type: str, details: Dict[str, Any],
                          client_id: Optional[str] = None, risk_level: str = "medium"):
        """
        Log security events with full context.

        Args:
            event_type: Type of security event (access, violation, etc.)
            details: Event-specific details
            client_id: Identifier for the client/user
            risk_level: Risk assessment (low, medium, high, critical)
        """
        audit_record = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "risk_level": risk_level,
            "client_id": client_id or "anonymous",
            "details": details,
            "server_version": "1.0.0"
        }

        # Log as JSON for easy parsing
        self.audit_logger.info(json.dumps(audit_record))
```

### File Operation Tracking

Track all file operations for compliance:

```python
    def log_file_operation(self, operation: str, path: str, success: bool,
                          client_id: Optional[str] = None, metadata: Dict = None):
        """Log file operations with full context."""
        details = {
            "operation": operation,
            "path": path,
            "success": success,
            "metadata": metadata or {}
        }

        risk_level = "low" if success else "medium"
        self.log_security_event("file_operation", details, client_id, risk_level)
```

### Security Violation Detection

Detect and log security violations:

```python
    def log_security_violation(self, violation_type: str, attempted_path: str,
                              client_id: Optional[str] = None, details: Dict = None):
        """Log security violations with high priority."""
        violation_details = {
            "violation_type": violation_type,
            "attempted_path": attempted_path,
            "blocked": True,
            "additional_details": details or {}
        }

        # Security violations are always high risk
        self.log_security_event("security_violation", violation_details,
                               client_id, "high")
```

## Advanced Rate Limiting & DoS Protection

### Sophisticated Rate Limiting Implementation

Create advanced rate limiting for production deployments:

```python
# security/rate_limiter.py - Advanced rate limiting
import asyncio
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque

class AdvancedRateLimiter:
    """
    Multi-tier rate limiting with burst protection.

    Implements sliding window rate limiting with multiple time windows
    for sophisticated DoS protection.
    """

    def __init__(self, config):
        self.config = config
        # Client tracking with multiple time windows
        self.client_requests = defaultdict(lambda: {
            'minute': deque(),
            'hour': deque(),
            'day': deque()
        })

        # Rate limits for different time windows
        self.limits = {
            'minute': config.rate_limit_per_minute,
            'hour': config.rate_limit_per_minute * 60,
            'day': config.rate_limit_per_minute * 60 * 24
        }
```

### Sliding Window Rate Limiting

Implement precise rate limiting with sliding windows:

```python
    def is_rate_limited(self, client_id: str) -> Tuple[bool, Dict[str, int]]:
        """
        Check if client is rate limited using sliding window algorithm.

        Returns:
            Tuple of (is_limited, remaining_requests_by_window)
        """
        now = time.time()
        client_data = self.client_requests[client_id]

        # Clean old requests and count current
        remaining = {}

        for window, requests in client_data.items():
            # Remove expired requests
            window_duration = self._get_window_duration(window)
            cutoff_time = now - window_duration

            while requests and requests[0] < cutoff_time:
                requests.popleft()

            # Calculate remaining requests for this window
            current_count = len(requests)
            remaining[window] = max(0, self.limits[window] - current_count)

        # Client is limited if ANY window is exceeded
        is_limited = any(remaining[window] <= 0 for window in remaining)

        return is_limited, remaining
```

Add helper method for window duration calculation:

```python
    def _get_window_duration(self, window: str) -> int:
        """Get duration in seconds for time window."""
        durations = {
            'minute': 60,
            'hour': 3600,
            'day': 86400
        }
        return durations[window]
```

### Request Registration

Track successful requests across all time windows:

```python
    def register_request(self, client_id: str):
        """Register a successful request for rate limiting tracking."""
        now = time.time()
        client_data = self.client_requests[client_id]

        # Add current timestamp to all tracking windows
        for window in client_data:
            client_data[window].append(now)
```

### Burst Detection

Detect and prevent burst attacks:

```python
    def detect_burst_pattern(self, client_id: str) -> bool:
        """
        Detect suspicious burst patterns that might indicate attacks.

        Returns True if burst pattern detected.
        """
        client_data = self.client_requests[client_id]
        recent_requests = client_data['minute']

        if len(recent_requests) < 10:
            return False

        # Check if 10+ requests happened in last 10 seconds
        now = time.time()
        recent_burst = sum(1 for req_time in recent_requests
                          if now - req_time < 10)

        return recent_burst >= 10
```

## Advanced Filename Security Patterns

### Comprehensive Filename Validation

Implement enterprise-grade filename security:

```python
    def validate_advanced_filename(self, filename: str) -> Tuple[bool, List[str]]:
        """
        Advanced filename security validation.

        Returns:
            Tuple of (is_safe, list_of_violations)
        """
        violations = []

        # Basic length checks
        if len(filename) == 0:
            violations.append("Empty filename")
        if len(filename) > 255:
            violations.append("Filename too long (max 255 characters)")

        # Unicode normalization attack prevention
        import unicodedata
        normalized = unicodedata.normalize('NFC', filename)
        if normalized != filename:
            violations.append("Unicode normalization attack detected")
```

Check for advanced injection patterns:

```python
        # Advanced injection patterns
        dangerous_patterns = {
            'null_byte': '\x00',
            'line_feed': '\n',
            'carriage_return': '\r',
            'tab': '\t',
            'shell_expansion': ['${', '$(', '`'],
            'path_traversal': ['../', '..\\', '../'],
            'reserved_names': ['CON', 'PRN', 'AUX', 'NUL'] +
                             [f'COM{i}' for i in range(1, 10)] +
                             [f'LPT{i}' for i in range(1, 10)]
        }

        filename_upper = filename.upper()

        for pattern_type, patterns in dangerous_patterns.items():
            if isinstance(patterns, str):
                patterns = [patterns]

            for pattern in patterns:
                if pattern.upper() in filename_upper:
                    violations.append(f"Dangerous pattern detected: {pattern_type}")
```

Return comprehensive validation results:

```python
        return len(violations) == 0, violations
```

### Security Pattern Detection

Detect sophisticated attack patterns in filenames:

```python
    def detect_filename_attack_patterns(self, filename: str) -> Dict[str, bool]:
        """Detect specific attack patterns in filenames."""
        patterns = {
            'polyglot_attack': self._detect_polyglot(filename),
            'homograph_attack': self._detect_homograph(filename),
            'extension_confusion': self._detect_extension_confusion(filename),
            'reserved_device': self._detect_reserved_device(filename)
        }

        return patterns
```

Implement polyglot attack detection:

```python
    def _detect_polyglot(self, filename: str) -> bool:
        """Detect polyglot file attacks (files with multiple valid interpretations)."""
        # Look for multiple extensions or embedded format signatures
        extensions = [ext.lower() for ext in filename.split('.')[1:]]

        # Suspicious: multiple executable extensions
        executable_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr'}
        exec_count = sum(1 for ext in extensions if f'.{ext}' in executable_extensions)

        return exec_count > 0 and len(extensions) > 1
```

Implement homograph attack detection:

```python
    def _detect_homograph(self, filename: str) -> bool:
        """Detect homograph attacks using similar-looking characters."""
        # Check for mixed scripts (Latin + Cyrillic, etc.)
        import unicodedata

        scripts = set()
        for char in filename:
            script = unicodedata.name(char, '').split()[0] if unicodedata.name(char, '') else 'UNKNOWN'
            scripts.add(script)

        # Suspicious if mixing Latin with other scripts
        return len(scripts) > 2 and 'LATIN' in scripts
```

---

## 🧭 Navigation

**Previous:** [Session 1 - Foundations →](Session1_Basic_MCP_Server.md)  
**Next:** [Session 3 - Advanced Patterns →](Session3_LangChain_MCP_Integration.md)

---
