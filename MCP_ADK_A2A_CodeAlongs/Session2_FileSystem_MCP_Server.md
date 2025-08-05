# Session 2: File System MCP Server - Code-Along Tutorial

## 🎯 Learning Objectives
- Build a production-grade file system MCP server
- Implement safe file operations with sandboxing
- Handle binary files and streaming
- Add search capabilities and file watching
- Implement proper error handling and validation

## 📚 Pre-Session Reading
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/concepts/security)
- [Python pathlib Documentation](https://docs.python.org/3/library/pathlib.html)

---

## Part 1: Project Setup (10 minutes)

### Step 1.1: Create Enhanced Project Structure
```bash
# Create project directory
mkdir mcp-filesystem-server
cd mcp-filesystem-server

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastmcp aiofiles watchdog python-magic-bin
```

### Step 1.2: Project Structure
```
mcp-filesystem-server/
├── filesystem_server.py
├── file_watcher.py
├── config.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── sandbox.py
├── tests/
│   └── test_filesystem.py
└── requirements.txt
```

### Step 1.3: Configuration Module
```python
# config.py
import os
from pathlib import Path
from typing import List, Set

class FileSystemConfig:
    """Configuration for the file system MCP server."""
    
    def __init__(self, base_path: str = None):
        # Set base path (sandbox root)
        self.base_path = Path(base_path or os.getcwd()) / "sandbox"
        self.base_path.mkdir(exist_ok=True)
        
        # Security settings
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions: Set[str] = {
            '.txt', '.md', '.json', '.yaml', '.yml',
            '.py', '.js', '.ts', '.html', '.css',
            '.csv', '.log', '.conf', '.ini'
        }
        
        # Forbidden patterns
        self.forbidden_patterns: List[str] = [
            '..', '~/', '/etc/', '/usr/', '/var/',
            'C:\\Windows', 'C:\\Program Files'
        ]
        
        # Performance settings
        self.chunk_size = 8192  # For streaming
        self.search_limit = 1000  # Max search results
```

---

## Part 2: Security and Validation (20 minutes)

### Step 2.1: Path Validation and Sandboxing
```python
# utils/sandbox.py
from pathlib import Path
from typing import Optional
import os

class SandboxError(Exception):
    """Raised when attempting to access files outside sandbox."""
    pass

class FileSystemSandbox:
    """Ensures all file operations stay within allowed directories."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path.resolve()
    
    def validate_path(self, path: str) -> Path:
        """
        Validate and resolve a path within the sandbox.
        
        Args:
            path: Requested file path
            
        Returns:
            Resolved safe path
            
        Raises:
            SandboxError: If path escapes sandbox
        """
        try:
            # Resolve the path
            requested_path = (self.base_path / path).resolve()
            
            # Check if path is within sandbox
            if not str(requested_path).startswith(str(self.base_path)):
                raise SandboxError(f"Path '{path}' escapes sandbox")
            
            return requested_path
            
        except Exception as e:
            raise SandboxError(f"Invalid path '{path}': {str(e)}")
    
    def is_safe_filename(self, filename: str) -> bool:
        """Check if filename is safe."""
        dangerous_chars = ['/', '\\', '..', '~', '\0']
        return not any(char in filename for char in dangerous_chars)
```

### Step 2.2: File Validators
```python
# utils/validators.py
from pathlib import Path
from typing import Dict, Any
import magic
import hashlib

class FileValidator:
    """Validates files for safety and compliance."""
    
    def __init__(self, config):
        self.config = config
        self.mime = magic.Magic(mime=True)
    
    def validate_file_size(self, path: Path) -> bool:
        """Check if file size is within limits."""
        return path.stat().st_size <= self.config.max_file_size
    
    def validate_file_type(self, path: Path) -> Dict[str, Any]:
        """Validate file type and return metadata."""
        extension = path.suffix.lower()
        mime_type = self.mime.from_file(str(path))
        
        # Check against allowed extensions
        allowed = extension in self.config.allowed_extensions
        
        return {
            "allowed": allowed,
            "extension": extension,
            "mime_type": mime_type,
            "is_text": mime_type.startswith('text/'),
            "is_binary": not mime_type.startswith('text/')
        }
    
    def calculate_checksum(self, path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
```

---

## Part 3: Building the File System MCP Server (30 minutes)

### Step 3.1: Server Initialization
```python
# filesystem_server.py
from mcp.server.fastmcp import FastMCP
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, AsyncIterator
import json
import base64

from config import FileSystemConfig
from utils.sandbox import FileSystemSandbox, SandboxError
from utils.validators import FileValidator

# Initialize server components
config = FileSystemConfig()
mcp = FastMCP("File System Server")
sandbox = FileSystemSandbox(config.base_path)
validator = FileValidator(config)

# Store for file watchers
active_watchers = {}
```

### Step 3.2: File Listing and Navigation Tools
```python
@mcp.tool()
async def list_directory(path: str = ".", pattern: str = "*") -> Dict:
    """
    List files and directories.
    
    Args:
        path: Directory path relative to sandbox
        pattern: Glob pattern for filtering (e.g., "*.txt")
    
    Returns:
        Directory contents with metadata
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        if not safe_path.is_dir():
            return {"error": f"'{path}' is not a directory"}
        
        items = []
        for item in safe_path.glob(pattern):
            relative_path = item.relative_to(config.base_path)
            
            # Get file metadata
            stat = item.stat()
            items.append({
                "name": item.name,
                "path": str(relative_path),
                "type": "directory" if item.is_dir() else "file",
                "size": stat.st_size if item.is_file() else None,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:]
            })
        
        # Sort: directories first, then files
        items.sort(key=lambda x: (x["type"] != "directory", x["name"]))
        
        return {
            "path": str(safe_path.relative_to(config.base_path)),
            "total_items": len(items),
            "items": items
        }
        
    except SandboxError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to list directory: {str(e)}"}

@mcp.tool()
async def get_file_info(path: str) -> Dict:
    """
    Get detailed information about a file.
    
    Args:
        path: File path relative to sandbox
    
    Returns:
        Detailed file metadata
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        if not safe_path.exists():
            return {"error": f"File '{path}' not found"}
        
        stat = safe_path.stat()
        file_type = validator.validate_file_type(safe_path)
        
        info = {
            "name": safe_path.name,
            "path": str(safe_path.relative_to(config.base_path)),
            "size": stat.st_size,
            "size_human": f"{stat.st_size / 1024:.2f} KB",
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "permissions": oct(stat.st_mode)[-3:],
            "is_directory": safe_path.is_dir(),
            "is_file": safe_path.is_file(),
            "is_symlink": safe_path.is_symlink(),
            **file_type
        }
        
        # Add checksum for files
        if safe_path.is_file() and info["is_text"]:
            info["checksum"] = validator.calculate_checksum(safe_path)
        
        return info
        
    except SandboxError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to get file info: {str(e)}"}
```

### Step 3.3: File Reading and Writing Tools
```python
@mcp.tool()
async def read_file(path: str, encoding: str = "utf-8", 
                   start_line: Optional[int] = None,
                   end_line: Optional[int] = None) -> Dict:
    """
    Read file contents.
    
    Args:
        path: File path relative to sandbox
        encoding: File encoding (default: utf-8)
        start_line: Starting line number (1-based)
        end_line: Ending line number (inclusive)
    
    Returns:
        File contents or error
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        if not safe_path.is_file():
            return {"error": f"'{path}' is not a file"}
        
        # Validate file
        if not validator.validate_file_size(safe_path):
            return {"error": f"File too large (max {config.max_file_size} bytes)"}
        
        file_type = validator.validate_file_type(safe_path)
        
        # Handle binary files
        if file_type["is_binary"]:
            async with aiofiles.open(safe_path, 'rb') as f:
                content = await f.read()
                return {
                    "path": str(safe_path.relative_to(config.base_path)),
                    "content": base64.b64encode(content).decode('ascii'),
                    "encoding": "base64",
                    "mime_type": file_type["mime_type"]
                }
        
        # Handle text files
        async with aiofiles.open(safe_path, 'r', encoding=encoding) as f:
            if start_line or end_line:
                lines = await f.readlines()
                start_idx = (start_line - 1) if start_line else 0
                end_idx = end_line if end_line else len(lines)
                content = ''.join(lines[start_idx:end_idx])
            else:
                content = await f.read()
        
        return {
            "path": str(safe_path.relative_to(config.base_path)),
            "content": content,
            "encoding": encoding,
            "lines": content.count('\n') + 1,
            "size": len(content)
        }
        
    except SandboxError as e:
        return {"error": str(e)}
    except UnicodeDecodeError:
        return {"error": f"Cannot decode file with encoding '{encoding}'"}
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}

@mcp.tool()
async def write_file(path: str, content: str, 
                    encoding: str = "utf-8",
                    create_dirs: bool = False,
                    append: bool = False) -> Dict:
    """
    Write content to a file.
    
    Args:
        path: File path relative to sandbox
        content: Content to write
        encoding: File encoding (default: utf-8)
        create_dirs: Create parent directories if needed
        append: Append to file instead of overwriting
    
    Returns:
        Success status or error
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        # Validate filename
        if not sandbox.is_safe_filename(safe_path.name):
            return {"error": f"Unsafe filename: {safe_path.name}"}
        
        # Create parent directories if requested
        if create_dirs:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if parent directory exists
        if not safe_path.parent.exists():
            return {"error": f"Parent directory does not exist"}
        
        # Write file
        mode = 'a' if append else 'w'
        async with aiofiles.open(safe_path, mode, encoding=encoding) as f:
            await f.write(content)
        
        # Return file info
        stat = safe_path.stat()
        return {
            "success": True,
            "path": str(safe_path.relative_to(config.base_path)),
            "size": stat.st_size,
            "mode": "appended" if append else "written",
            "timestamp": datetime.now().isoformat()
        }
        
    except SandboxError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}
```

### Step 3.4: File Operations Tools
```python
@mcp.tool()
async def create_directory(path: str, parents: bool = True) -> Dict:
    """
    Create a directory.
    
    Args:
        path: Directory path relative to sandbox
        parents: Create parent directories if needed
    
    Returns:
        Success status or error
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        if safe_path.exists():
            return {"error": f"Path '{path}' already exists"}
        
        safe_path.mkdir(parents=parents, exist_ok=False)
        
        return {
            "success": True,
            "path": str(safe_path.relative_to(config.base_path)),
            "created": datetime.now().isoformat()
        }
        
    except SandboxError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to create directory: {str(e)}"}

@mcp.tool()
async def delete_file(path: str, recursive: bool = False) -> Dict:
    """
    Delete a file or directory.
    
    Args:
        path: Path to delete
        recursive: Delete directories recursively
    
    Returns:
        Success status or error
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        if not safe_path.exists():
            return {"error": f"Path '{path}' not found"}
        
        # Prevent deleting sandbox root
        if safe_path == config.base_path:
            return {"error": "Cannot delete sandbox root"}
        
        if safe_path.is_dir():
            if recursive:
                import shutil
                shutil.rmtree(safe_path)
            else:
                safe_path.rmdir()  # Only works if empty
        else:
            safe_path.unlink()
        
        return {
            "success": True,
            "path": str(path),
            "deleted": datetime.now().isoformat()
        }
        
    except SandboxError as e:
        return {"error": str(e)}
    except OSError as e:
        return {"error": f"Cannot delete: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to delete: {str(e)}"}

@mcp.tool()
async def move_file(source: str, destination: str, 
                   overwrite: bool = False) -> Dict:
    """
    Move or rename a file/directory.
    
    Args:
        source: Source path
        destination: Destination path
        overwrite: Overwrite if destination exists
    
    Returns:
        Success status or error
    """
    try:
        src_path = sandbox.validate_path(source)
        dst_path = sandbox.validate_path(destination)
        
        if not src_path.exists():
            return {"error": f"Source '{source}' not found"}
        
        if dst_path.exists() and not overwrite:
            return {"error": f"Destination '{destination}' already exists"}
        
        # Perform move/rename
        src_path.rename(dst_path)
        
        return {
            "success": True,
            "source": str(source),
            "destination": str(destination),
            "timestamp": datetime.now().isoformat()
        }
        
    except SandboxError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to move file: {str(e)}"}
```

### Step 3.5: Search Functionality
```python
@mcp.tool()
async def search_files(pattern: str, content: Optional[str] = None,
                      path: str = ".", 
                      case_sensitive: bool = False,
                      file_pattern: str = "*") -> Dict:
    """
    Search for files by name pattern and/or content.
    
    Args:
        pattern: Search pattern for filenames
        content: Search for this text in files
        path: Directory to search in
        case_sensitive: Case-sensitive search
        file_pattern: File pattern to search (e.g., "*.txt")
    
    Returns:
        Search results with matches
    """
    try:
        safe_path = sandbox.validate_path(path)
        results = []
        
        # Search for files
        for file_path in safe_path.rglob(file_pattern):
            if not file_path.is_file():
                continue
                
            # Check filename pattern
            filename_match = False
            if pattern:
                if case_sensitive:
                    filename_match = pattern in file_path.name
                else:
                    filename_match = pattern.lower() in file_path.name.lower()
            
            # Check content if specified
            content_matches = []
            if content and file_path.is_file():
                try:
                    file_type = validator.validate_file_type(file_path)
                    if file_type["is_text"]:
                        async with aiofiles.open(file_path, 'r') as f:
                            lines = await f.readlines()
                            for i, line in enumerate(lines, 1):
                                if case_sensitive:
                                    if content in line:
                                        content_matches.append({
                                            "line": i,
                                            "text": line.strip()
                                        })
                                else:
                                    if content.lower() in line.lower():
                                        content_matches.append({
                                            "line": i,
                                            "text": line.strip()
                                        })
                except:
                    pass  # Skip files that can't be read
            
            # Add to results if matched
            if filename_match or content_matches:
                results.append({
                    "path": str(file_path.relative_to(config.base_path)),
                    "filename_match": filename_match,
                    "content_matches": content_matches[:5],  # Limit matches
                    "total_matches": len(content_matches)
                })
            
            # Limit results
            if len(results) >= config.search_limit:
                break
        
        return {
            "query": {
                "pattern": pattern,
                "content": content,
                "path": str(safe_path.relative_to(config.base_path)),
                "case_sensitive": case_sensitive
            },
            "total_results": len(results),
            "results": results
        }
        
    except SandboxError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}
```

### Step 3.6: Resources and Prompts
```python
@mcp.resource("filesystem://stats")
async def get_filesystem_stats() -> Dict:
    """Get file system statistics."""
    total_size = 0
    file_count = 0
    dir_count = 0
    
    for item in config.base_path.rglob("*"):
        if item.is_file():
            total_size += item.stat().st_size
            file_count += 1
        elif item.is_dir():
            dir_count += 1
    
    return {
        "sandbox_path": str(config.base_path),
        "total_files": file_count,
        "total_directories": dir_count,
        "total_size_bytes": total_size,
        "total_size_human": f"{total_size / (1024*1024):.2f} MB",
        "max_file_size": config.max_file_size,
        "allowed_extensions": list(config.allowed_extensions)
    }

@mcp.prompt()
def file_analysis_prompt(path: str) -> str:
    """Generate a file analysis prompt."""
    return f"""Analyze the file at '{path}' and provide:
    1. File type and format analysis
    2. Content summary (if text file)
    3. Potential security concerns
    4. Suggested operations or improvements
    
    Use the file system tools to gather this information."""

@mcp.prompt()
def directory_organization_prompt(path: str = ".") -> str:
    """Generate a directory organization prompt."""
    return f"""Analyze the directory structure at '{path}' and:
    1. Provide an overview of the organization
    2. Identify any issues (empty dirs, large files, etc.)
    3. Suggest improvements to the structure
    4. Create a summary report of the contents"""
```

---

## Part 4: Testing and Integration (10 minutes)

### Step 4.1: Test Suite
```python
# tests/test_filesystem.py
import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from filesystem_server import (
    list_directory, read_file, write_file,
    create_directory, search_files
)

class TestFileSystemServer:
    @pytest.fixture
    def setup_sandbox(self):
        """Create a temporary sandbox for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Update config to use temp directory
            original_base = config.base_path
            config.base_path = Path(tmpdir) / "sandbox"
            config.base_path.mkdir()
            
            yield config.base_path
            
            # Restore original
            config.base_path = original_base
    
    @pytest.mark.asyncio
    async def test_write_and_read_file(self, setup_sandbox):
        """Test writing and reading a file."""
        # Write file
        result = await write_file("test.txt", "Hello, World!")
        assert result["success"] == True
        
        # Read file
        result = await read_file("test.txt")
        assert result["content"] == "Hello, World!"
    
    @pytest.mark.asyncio
    async def test_sandbox_escape_prevention(self, setup_sandbox):
        """Test that sandbox escape is prevented."""
        # Try to escape sandbox
        result = await read_file("../../etc/passwd")
        assert "error" in result
        assert "escapes sandbox" in result["error"]
    
    @pytest.mark.asyncio
    async def test_search_functionality(self, setup_sandbox):
        """Test file search."""
        # Create test files
        await write_file("doc1.txt", "Hello world")
        await write_file("doc2.txt", "Hello universe")
        await write_file("readme.md", "# Project")
        
        # Search by content
        result = await search_files("", content="Hello")
        assert result["total_results"] == 2
        
        # Search by filename
        result = await search_files("doc", file_pattern="*.txt")
        assert result["total_results"] == 2
```

### Step 4.2: Run the Server
```python
# Add to end of filesystem_server.py
if __name__ == "__main__":
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create initial structure
    (config.base_path / "documents").mkdir(exist_ok=True)
    (config.base_path / "data").mkdir(exist_ok=True)
    
    # Create a welcome file
    welcome_path = config.base_path / "README.md"
    welcome_path.write_text("""# File System MCP Server

Welcome to the sandboxed file system!

## Available Directories:
- `/documents` - For text documents
- `/data` - For data files

## Security:
All operations are sandboxed to this directory.
""")
    
    print(f"Starting File System MCP Server...")
    print(f"Sandbox root: {config.base_path}")
    print(f"Allowed extensions: {', '.join(config.allowed_extensions)}")
    
    # Run the server
    mcp.run()
```

---

## 🧪 Testing Your Understanding

### Quick Check Questions

1. **What is the primary security mechanism used in this file system server?**
   - A) Encryption
   - B) Sandboxing
   - C) Authentication
   - D) Rate limiting

2. **How are binary files handled when reading?**
   - A) They're converted to text
   - B) They're rejected
   - C) They're base64 encoded
   - D) They're compressed

3. **What prevents directory traversal attacks?**
   - A) Input validation only
   - B) Path resolution and validation
   - C) File permissions
   - D) User authentication

4. **Which tool would you use to find all Python files containing "import requests"?**
   - A) `list_directory`
   - B) `read_file`
   - C) `search_files`
   - D) `get_file_info`

5. **What happens when trying to write to a file outside the sandbox?**
   - A) The file is created in sandbox
   - B) A `SandboxError` is raised
   - C) The operation silently fails
   - D) The path is automatically adjusted

### Practical Exercise

Implement a new tool that:
1. Compares two text files
2. Returns differences line by line
3. Handles encoding issues gracefully
4. Validates both files exist and are text files

```python
# Your implementation here
@mcp.tool()
async def compare_files(file1: str, file2: str, 
                       context_lines: int = 3) -> Dict:
    """Compare two text files and return differences."""
    # TODO: Implement this function
    pass
```

---

## 📝 Session Summary

You've learned to:
- ✅ Build a secure file system MCP server with sandboxing
- ✅ Handle both text and binary files appropriately
- ✅ Implement comprehensive file operations (CRUD)
- ✅ Add search functionality for files and content
- ✅ Validate paths and prevent security vulnerabilities
- ✅ Create proper error handling and logging

### Next Session Preview
In Session 3, we'll integrate MCP servers with LangChain to:
- Connect multiple MCP servers
- Build agents that use file system tools
- Create chains and workflows
- Handle tool errors in agent flows

### Homework
1. Add a `compress_files` tool that creates zip archives
2. Implement file watching functionality for real-time updates
3. Add a `diff_files` tool for comparing files
4. Create file type specific handlers (JSON, CSV, etc.)

### Answer Key
1. B) Sandboxing
2. C) They're base64 encoded
3. B) Path resolution and validation
4. C) `search_files`
5. B) A `SandboxError` is raised

---

## Additional Resources
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [Python aiofiles Documentation](https://github.com/Tinche/aiofiles)
- [File System Security Best Practices](https://modelcontextprotocol.io/docs/concepts/security)