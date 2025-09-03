# 🎯📝 Session 2: Building a Secure File System MCP Server

This session covers building a production-grade file system MCP server with comprehensive security features including sandboxing, path validation, input sanitization, and audit logging. You'll implement secure file operations that prevent directory traversal attacks while supporting both text and binary files.

![File System Security Architecture](images/filesystem-security-architecture.png)
*Multi-layered security architecture showing path validation, sandboxing, permission checks, and audit logging*

## 🎯📝⚙️ Learning Path Overview

This session offers three distinct learning paths designed to match your goals and time investment:

=== "🎯 Observer (30-45 min)"

    **Focus**: Understanding concepts and architecture
    
    **Activities**: File system security fundamentals, defense-in-depth strategies, security threats
    
    **Ideal for**: Decision makers, architects, overview learners

=== "📝 Participant (3-4 hours)"

    **Focus**: Guided implementation and analysis
    
    **Activities**: Build secure file system MCP server, implement sandboxing and validation
    
    **Ideal for**: Developers, technical leads, hands-on learners

=== "⚙️ Implementer (6-8 hours)"

    **Focus**: Complete implementation and customization
    
    **Activities**: Advanced security patterns, production deployment, enterprise hardening
    
    **Ideal for**: Senior engineers, architects, specialists

## 🎯 Observer Path: Essential Security Concepts

### Understanding File System Security Fundamentals

File system access represents one of the highest-risk attack vectors in AI agent systems. Common threats include:

- **Path Traversal**: Malicious inputs like `../../../etc/passwd` accessing sensitive system files
- **System File Access**: Reading critical files like `/etc/passwd`, `C:\Windows\System32\config\SAM`
- **Arbitrary Write Operations**: Creating malicious files in system directories  
- **Denial of Service**: Large file operations that exhaust system resources  

### Defense-in-Depth Strategy Overview

Our server implements multiple security layers:

1. **Sandboxing**: Physical isolation to designated directories  
2. **Path Validation**: Mathematical verification of file paths  
3. **Input Sanitization**: Content filtering and validation  
4. **Audit Logging**: Complete operation tracking  
5. **Resource Limits**: Prevention of resource exhaustion  

### Project Setup Essentials

Create a modular file system server with security-first architecture:

```bash
# Create project with full security stack
mkdir mcp-filesystem-server
cd mcp-filesystem-server

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

Install the essential production dependencies:

```bash
# Install production dependencies
pip install fastmcp aiofiles watchdog
pip install python-magic-bin cryptography
```

**Security-focused dependencies explained**:

- `fastmcp`: MCP protocol framework with built-in security features
- `aiofiles`: Async I/O prevents blocking operations that could cause DoS
- `python-magic-bin`: Content-based file type detection (more secure than extensions)
- `watchdog`: Real-time file system monitoring for security events
- `cryptography`: File integrity verification and encryption support

### Security Directory Structure

Create a modular architecture that separates security concerns:

```text
mcp-filesystem-server/
├── filesystem_server.py    # Main MCP server implementation
├── config.py              # Security configuration
├── utils/                 # Security utilities
│   ├── __init__.py
│   ├── sandbox.py         # Path validation & sandboxing
│   └── validators.py      # File type & content validation
├── security/              # Advanced security features
│   ├── __init__.py
│   ├── audit.py          # Logging and monitoring
│   └── rate_limiter.py   # DoS protection
├── tests/                 # Security test suite
│   └── test_security.py
└── requirements.txt       # Dependency list
```

This modular architecture separates security concerns, enables unit testing, and maintains clear separation between business logic and security.

### Understanding Sandboxing Principles

A sandbox creates an isolated environment where file operations can only occur within a designated directory tree. Sandboxing provides mathematical certainty that file operations cannot escape designated boundaries.

The core security principle: Using `resolve()` eliminates relative path components and symlink tricks that attackers use to escape sandboxes.

### Mathematical Path Validation

The critical security check that provides absolute containment uses string prefix checking after path resolution:

```python
# CRITICAL SECURITY CHECK: Mathematical path containment
if not str(resolved_path).startswith(str(self.base_path)):
    raise SandboxError(f"Security violation: '{path}' escapes sandbox")
```

**Security Mathematics**: String prefix checking after path resolution provides mathematical certainty - if the resolved path doesn't start with our base path string, it's physically impossible for it to be within our sandbox.

## 📝 Participant Path: Practical Implementation

*Prerequisites: Complete Observer Path sections above*

### Security Configuration Implementation

The configuration module is the security control center where all security settings are defined:

```python
# config.py - Security-first configuration
from pathlib import Path
import os

class FileSystemConfig:
    """Centralized security configuration for MCP file system server."""

    def __init__(self, base_path: str = None):
        # Create isolated sandbox - AI agents can ONLY access this directory
        self.base_path = Path(base_path or os.getcwd()) / "sandbox"
        self.base_path.mkdir(exist_ok=True)
```

**Security Principle**: The sandbox path is the critical security boundary - everything outside this directory is inaccessible to AI agents.

Add file size protection to prevent memory exhaustion attacks:

```python
        # File size protection (prevents memory exhaustion attacks)
        self.max_file_size = 10 * 1024 * 1024  # 10MB industry-standard limit

        # Extension whitelist (based on 2024 security best practices)
        self.allowed_extensions = {
            # Documentation formats
            '.txt', '.md', '.rst', '.adoc',
            # Data formats
            '.json', '.yaml', '.yml', '.toml', '.csv',
            # Code formats
            '.py', '.js', '.ts', '.java', '.go', '.rs'
        }
```

This uses a whitelist approach for security (OWASP recommended), prevents DoS attacks through size limits, and covers typical enterprise file types without executable risks.

### Path Traversal Defense Implementation

Define patterns that indicate potential security threats:

```python
        # Path traversal attack patterns (based on CISA threat intelligence)
        self.forbidden_patterns = [
            # Directory traversal patterns
            '..', '../', '..\\',
            # Unix system directories
            '/etc/', '/usr/', '/var/', '/root/', '/boot/',
            # Windows system directories
            'C:\\Windows', 'C:\\Program Files', 'C:\\ProgramData'
        ]
```

These patterns defend against real attack vectors documented by security organizations.

Add performance and DoS protection:

```python
        # Performance limits (DoS prevention)
        self.chunk_size = 8192          # Streaming chunk size for large files
        self.search_limit = 1000        # Max search results per query
        self.max_concurrent_ops = 10    # Concurrent file operations limit
        self.rate_limit_per_minute = 100  # Operations per minute per client
```

### Sandbox Security Implementation

Create the core security boundary enforcement:

```python
# utils/sandbox.py - Core security boundary
from pathlib import Path

class SandboxError(Exception):
    """Security violation: attempted access outside sandbox."""
    pass

class FileSystemSandbox:
    """Mathematically enforces file access boundaries."""

    def __init__(self, base_path: Path):
        # Convert to absolute path - prevents relative path tricks
        self.base_path = base_path.resolve()
```

**Key Security Principle**: Using `resolve()` eliminates relative path components and symlink tricks that attackers use to escape sandboxes.

Implement the cryptographically secure path validation:

```python
    def validate_path(self, path: str) -> Path:
        """
        Cryptographically secure path validation.

        Uses mathematical path resolution to prevent ALL known
        directory traversal attack vectors.
        """
        try:
            # Step 1: Construct path within sandbox
            candidate_path = self.base_path / path

            # Step 2: Resolve ALL relative components and symlinks
            resolved_path = candidate_path.resolve()
```

**Technical Detail**: The `resolve()` method performs canonical path resolution, eliminating `..`, `.`, and symlink components that could be used to escape the sandbox.

Complete the validation with the mathematical boundary verification:

```python
            # CRITICAL SECURITY CHECK: Mathematical path containment
            if not str(resolved_path).startswith(str(self.base_path)):
                raise SandboxError(f"Security violation: '{path}' escapes sandbox")

            return resolved_path

        except (OSError, ValueError, PermissionError):
            # ANY path resolution failure is treated as a security threat
            raise SandboxError(f"Path access denied: {path}")
        except Exception:
            # Catch-all for unknown path manipulation attempts
            raise SandboxError(f"Security error processing path: {path}")
```

**Security Design**: We intentionally provide minimal error information to prevent attackers from learning about the file system structure through error messages.

### Building the MCP Server Foundation

Import all necessary modules and security components:

```python
# filesystem_server.py
from mcp.server.fastmcp import FastMCP
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json
import base64
import logging
```

Import our custom security modules:

```python
from config import FileSystemConfig
from utils.sandbox import FileSystemSandbox, SandboxError
```

Set up comprehensive logging for security monitoring:

```python
# Set up logging for security auditing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize server components
config = FileSystemConfig()
mcp = FastMCP("File System Server")
sandbox = FileSystemSandbox(config.base_path)

logger.info(f"File System MCP Server initialized with sandbox at: {config.base_path}")
```

### Core File Operations Implementation

Define the directory listing tool with proper security validation:

```python
@mcp.tool()
async def list_directory(path: str = ".", pattern: str = "*") -> Dict:
    """
    List files and directories safely within the sandbox.

    Args:
        path: Directory path relative to sandbox root
        pattern: Glob pattern for filtering (e.g., "*.txt", "test_*")
    """
    try:
        # First, validate the path is safe
        safe_path = sandbox.validate_path(path)

        if not safe_path.is_dir():
            return {"error": f"'{path}' is not a directory"}
```

Path validation and directory check ensure we're working with safe, valid directories.

Gather information about each file and directory:

```python
        items = []
        # Use glob to support patterns like "*.py"
        for item in safe_path.glob(pattern):
            # Calculate relative path for display
            relative_path = item.relative_to(config.base_path)

            # Gather metadata about each item
            stat = item.stat()
            items.append({
                "name": item.name,
                "path": str(relative_path),
                "type": "directory" if item.is_dir() else "file",
                "size": stat.st_size if item.is_file() else None,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
```

Sort results and create the response:

```python
        # Sort for consistent output: directories first, then files
        items.sort(key=lambda x: (x["type"] != "directory", x["name"]))

        # Log the operation for security auditing
        logger.info(f"Listed directory: {path} (found {len(items)} items)")

        return {
            "path": str(safe_path.relative_to(config.base_path)),
            "total_items": len(items),
            "items": items
        }

    except SandboxError as e:
        logger.warning(f"Sandbox violation attempt: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Error listing directory: {e}")
        return {"error": f"Failed to list directory: {str(e)}"}
```

### Secure File Reading Implementation

Implement file reading that handles both text and binary files:

```python
@mcp.tool()
async def read_file(path: str, encoding: str = "utf-8",
                   start_line: Optional[int] = None,
                   end_line: Optional[int] = None) -> Dict:
    """
    Read file contents with support for both text and binary files.
    """
    try:
        safe_path = sandbox.validate_path(path)

        if not safe_path.is_file():
            return {"error": f"'{path}' is not a file"}

        # Check file size to prevent memory exhaustion
        stat = safe_path.stat()
        if stat.st_size > config.max_file_size:
            return {"error": f"File too large (max {config.max_file_size} bytes)"}
```

Detect file type and handle accordingly:

```python
        # Detect if this is a binary file
        is_binary = safe_path.suffix.lower() not in {'.txt', '.md', '.json', '.py', '.js'}

        # Handle binary files by encoding to base64
        if is_binary:
            async with aiofiles.open(safe_path, 'rb') as f:
                content = await f.read()

            return {
                "path": str(safe_path.relative_to(config.base_path)),
                "content": base64.b64encode(content).decode('ascii'),
                "encoding": "base64"
            }
```

Handle text files with optional line selection:

```python
        # Handle text files with optional line selection
        async with aiofiles.open(safe_path, 'r', encoding=encoding) as f:
            if start_line or end_line:
                # Read specific lines for large files
                lines = await f.readlines()
                start_idx = (start_line - 1) if start_line else 0
                end_idx = end_line if end_line else len(lines)
                content = ''.join(lines[start_idx:end_idx])
            else:
                # Read entire file
                content = await f.read()
```

This implementation allows reading partial file content for better performance with large files.

Generate the response with metadata:

```python
        return {
            "path": str(safe_path.relative_to(config.base_path)),
            "content": content,
            "encoding": encoding,
            "lines": content.count('\n') + 1
        }
```

Handle any security violations or errors:

```python
    except SandboxError as e:
        logger.warning(f"Sandbox violation attempt: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return {"error": f"Failed to read file: {str(e)}"}
```

### Server Launch Implementation

Add the server startup code:

```python
if __name__ == "__main__":
    # Create example files in sandbox for testing
    example_dir = config.base_path / "examples"
    example_dir.mkdir(exist_ok=True)

    # Create a sample text file
    (example_dir / "hello.txt").write_text("Hello from the secure file system server!")

    # Create a sample JSON file
    (example_dir / "data.json").write_text(json.dumps({
        "message": "This is sample data",
        "timestamp": datetime.now().isoformat()
    }, indent=2))

    print(f"🔒 Secure File System MCP Server")
    print(f"📁 Sandbox directory: {config.base_path}")
    print(f"Server ready for connections!")

    # Run the server
    mcp.run()
```

## ⚙️ Implementer Path: Complete Advanced Features

*Prerequisites: Complete Observer and Participant paths above*

For comprehensive coverage of advanced file system server topics, continue with these specialized modules:

- ⚙️ [Advanced Security Patterns](Session2_Advanced_Security_Patterns.md) - Enterprise-grade security implementations  
- ⚙️ [Production Implementation Guide](Session2_Production_Implementation.md) - Complete server with all advanced features  
- ⚙️ [Enterprise File Operations](Session2_Enterprise_File_Operations.md) - Advanced file manipulation and monitoring  

## 📝 Practice Exercises

**Observer Path Exercise**: Set up the basic project structure and configuration with security boundaries.

**Participant Path Exercise**: Implement the complete directory listing and file reading tools with proper error handling.

**Implementer Path Exercise**: Build the full production server with advanced security features, monitoring, and enterprise deployment capabilities.

## 📝 Quick Assessment

Test your understanding of the key concepts:

**Question 1**: What is the primary security mechanism that prevents directory traversal attacks?
A) File extension validation
B) Mathematical path resolution with `resolve()`
C) File size limits
D) Content type checking

**Question 2**: Why do we use a whitelist approach for file extensions?
A) It's faster than blacklists
B) It's more secure than blacklists
C) It uses less memory
D) It's easier to maintain

**Question 3**: What happens when a path tries to escape the sandbox?
A) The server crashes
B) A `SandboxError` is raised
C) The path is automatically corrected
D) A warning is logged

[View complete assessment in Production Implementation Guide →](Session2_Production_Implementation.md)
---

## Navigation

**Previous:** [Session 1 - Foundations →](Session1_*.md)  
**Next:** [Session 3 - Advanced Patterns →](Session3_*.md)

---
