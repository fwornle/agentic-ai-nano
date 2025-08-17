"""
Secure File System MCP Server - Session 2
A production-grade MCP server for safe file system operations.
"""

from mcp.server.fastmcp import FastMCP
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, AsyncIterator
import json
import base64
import logging
import sys

from config import FileSystemConfig
from utils.sandbox import FileSystemSandbox, SandboxError
from utils.validators import FileValidator

# Set up logging for security auditing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('filesystem_mcp.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize server components
config = FileSystemConfig()
mcp = FastMCP("Secure File System Server")
sandbox = FileSystemSandbox(config.base_path)
validator = FileValidator(config)

# Log server startup
logger.info(f"File System MCP Server initialized with sandbox at: {config.base_path}")


@mcp.tool()
async def list_directory(path: str = ".", pattern: str = "*") -> Dict:
    """
    List files and directories safely within the sandbox.
    
    Args:
        path: Directory path relative to sandbox root
        pattern: Glob pattern for filtering (e.g., "*.txt", "test_*")
    
    Returns:
        Directory contents with metadata
    """
    try:
        # Validate the path is safe
        safe_path = sandbox.validate_path(path)
        
        # Ensure it's actually a directory
        if not safe_path.is_dir():
            return {"error": f"'{path}' is not a directory"}
        
        items = []
        # Use glob to support patterns
        for item in safe_path.glob(pattern):
            # Calculate relative path for display
            relative_path = item.relative_to(config.base_path)
            
            # Gather metadata
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
        
        # Log the operation
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
        
        # Get file statistics
        stat = safe_path.stat()
        
        # Validate file type
        file_type = validator.validate_file_type(safe_path) if safe_path.is_file() else {}
        
        info = {
            "name": safe_path.name,
            "path": str(safe_path.relative_to(config.base_path)),
            "size": stat.st_size,
            "size_human": f"{stat.st_size / 1024:.2f} KB" if stat.st_size < 1024*1024 else f"{stat.st_size / (1024*1024):.2f} MB",
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "permissions": oct(stat.st_mode)[-3:],
            "is_directory": safe_path.is_dir(),
            "is_file": safe_path.is_file(),
            "is_symlink": safe_path.is_symlink(),
        }
        
        # Add file-specific info
        if safe_path.is_file():
            info.update(file_type)
            # Add checksum for text files
            if file_type.get("is_text", False):
                try:
                    info["checksum"] = validator.calculate_checksum(safe_path)
                except Exception as e:
                    info["checksum_error"] = str(e)
        
        logger.info(f"Retrieved info for: {path}")
        return info
        
    except SandboxError as e:
        logger.warning(f"Sandbox violation attempt: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        return {"error": f"Failed to get file info: {str(e)}"}


@mcp.tool()
async def read_file(
    path: str, 
    encoding: str = "utf-8", 
    start_line: Optional[int] = None,
    end_line: Optional[int] = None
) -> Dict:
    """
    Read file contents with support for both text and binary files.
    
    Args:
        path: File path relative to sandbox
        encoding: Text file encoding (default: utf-8)
        start_line: Starting line number (1-based) for partial reads
        end_line: Ending line number (inclusive) for partial reads
    
    Returns:
        File contents (text or base64-encoded binary)
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        if not safe_path.is_file():
            return {"error": f"'{path}' is not a file"}
        
        # Check file size
        if not validator.validate_file_size(safe_path):
            size_mb = safe_path.stat().st_size / (1024 * 1024)
            return {"error": f"File too large ({size_mb:.1f} MB, max {config.max_file_size / (1024*1024)} MB)"}
        
        # Detect file type
        file_type = validator.validate_file_type(safe_path)
        
        # Handle binary files
        if file_type["is_binary"]:
            async with aiofiles.open(safe_path, 'rb') as f:
                content = await f.read()
                
            logger.info(f"Read binary file: {path} ({len(content)} bytes)")
            
            return {
                "path": str(safe_path.relative_to(config.base_path)),
                "content": base64.b64encode(content).decode('ascii'),
                "encoding": "base64",
                "mime_type": file_type["mime_type"],
                "size": len(content)
            }
        
        # Handle text files
        try:
            async with aiofiles.open(safe_path, 'r', encoding=encoding) as f:
                if start_line or end_line:
                    # Read specific lines
                    lines = await f.readlines()
                    start_idx = (start_line - 1) if start_line else 0
                    end_idx = end_line if end_line else len(lines)
                    
                    # Validate line numbers
                    if start_idx < 0 or start_idx >= len(lines):
                        return {"error": f"Invalid start_line: {start_line}"}
                    if end_idx > len(lines):
                        end_idx = len(lines)
                    
                    content = ''.join(lines[start_idx:end_idx])
                    logger.info(f"Read text file: {path} (lines {start_idx+1}-{end_idx})")
                else:
                    # Read entire file
                    content = await f.read()
                    logger.info(f"Read text file: {path} ({len(content)} chars)")
            
            return {
                "path": str(safe_path.relative_to(config.base_path)),
                "content": content,
                "encoding": encoding,
                "lines": content.count('\n') + 1,
                "size": len(content)
            }
            
        except UnicodeDecodeError:
            # Try reading as binary if text decoding fails
            return await read_file(path, encoding="base64")
            
    except SandboxError as e:
        logger.warning(f"Sandbox violation attempt: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return {"error": f"Failed to read file: {str(e)}"}


@mcp.tool()
async def write_file(
    path: str, 
    content: str, 
    encoding: str = "utf-8",
    create_dirs: bool = False,
    append: bool = False
) -> Dict:
    """
    Write content to a file with comprehensive safety checks.
    
    Args:
        path: File path relative to sandbox
        content: Content to write (text or base64 for binary)
        encoding: Text encoding or "base64" for binary
        create_dirs: Create parent directories if needed
        append: Append to existing file instead of overwriting
    
    Returns:
        Success status with file metadata
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        # Validate filename
        if not sandbox.is_safe_filename(safe_path.name):
            return {"error": f"Unsafe filename: {safe_path.name}"}
        
        # Check file extension
        extension = safe_path.suffix.lower()
        if extension and extension not in config.allowed_extensions:
            return {"error": f"File type '{extension}' not allowed"}
        
        # Create parent directories if requested
        if create_dirs:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directories for: {path}")
        
        # Ensure parent directory exists
        if not safe_path.parent.exists():
            return {"error": "Parent directory does not exist (use create_dirs=true to create it)"}
        
        # Handle binary content
        if encoding == "base64":
            try:
                binary_content = base64.b64decode(content)
                mode = 'ab' if append else 'wb'
                
                async with aiofiles.open(safe_path, mode) as f:
                    await f.write(binary_content)
                    
                logger.info(f"Wrote binary file: {path} ({len(binary_content)} bytes, append={append})")
                
            except Exception as e:
                return {"error": f"Invalid base64 content: {str(e)}"}
        else:
            # Handle text content
            mode = 'a' if append else 'w'
            
            # Optional: Check content safety
            # if not validator.is_safe_content(content):
            #     return {"error": "Content contains potentially unsafe patterns"}
            
            async with aiofiles.open(safe_path, mode, encoding=encoding) as f:
                await f.write(content)
                
            logger.info(f"Wrote text file: {path} ({len(content)} chars, append={append})")
        
        # Return success with file info
        stat = safe_path.stat()
        return {
            "success": True,
            "path": str(safe_path.relative_to(config.base_path)),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "mode": "append" if append else "overwrite"
        }
        
    except SandboxError as e:
        logger.warning(f"Sandbox violation attempt: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        return {"error": f"Failed to write file: {str(e)}"}


@mcp.tool()
async def delete_file(path: str) -> Dict:
    """
    Delete a file or empty directory.
    
    Args:
        path: File or directory path relative to sandbox
    
    Returns:
        Success status or error
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        if not safe_path.exists():
            return {"error": f"Path '{path}' does not exist"}
        
        if safe_path.is_file():
            safe_path.unlink()
            logger.info(f"Deleted file: {path}")
            return {"success": True, "deleted": "file", "path": str(safe_path.relative_to(config.base_path))}
        
        elif safe_path.is_dir():
            # Only delete empty directories for safety
            try:
                safe_path.rmdir()
                logger.info(f"Deleted empty directory: {path}")
                return {"success": True, "deleted": "directory", "path": str(safe_path.relative_to(config.base_path))}
            except OSError:
                return {"error": "Directory is not empty. Only empty directories can be deleted."}
        
        else:
            return {"error": f"Path '{path}' is neither a file nor directory"}
            
    except SandboxError as e:
        logger.warning(f"Sandbox violation attempt: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return {"error": f"Failed to delete: {str(e)}"}


@mcp.tool()
async def search_files(
    pattern: str,
    search_type: str = "name",
    path: str = ".",
    max_results: int = 100,
    case_sensitive: bool = False
) -> Dict:
    """
    Search for files by name or content.
    
    Args:
        pattern: Search pattern (glob for names, text for content)
        search_type: "name" or "content"
        path: Starting directory for search
        max_results: Maximum results to return
        case_sensitive: Whether search is case-sensitive
    
    Returns:
        List of matching files with context
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        if not safe_path.is_dir():
            return {"error": f"'{path}' is not a directory"}
        
        results = []
        count = 0
        
        if search_type == "name":
            # Search by filename using glob patterns
            for file_path in safe_path.rglob(pattern):
                if count >= max_results:
                    break
                    
                if file_path.is_file():
                    relative = file_path.relative_to(config.base_path)
                    stat = file_path.stat()
                    results.append({
                        "path": str(relative),
                        "name": file_path.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                    count += 1
                    
        elif search_type == "content":
            # Search file contents
            search_pattern = pattern if case_sensitive else pattern.lower()
            
            for file_path in safe_path.rglob("*"):
                if count >= max_results:
                    break
                    
                if file_path.is_file():
                    # Only search text files
                    file_type = validator.validate_file_type(file_path)
                    
                    if file_type["is_text"] and validator.validate_file_size(file_path):
                        try:
                            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                                content = await f.read()
                                
                            # Search in content
                            search_content = content if case_sensitive else content.lower()
                            
                            if search_pattern in search_content:
                                # Find matching lines for context
                                lines = content.splitlines()
                                matching_lines = []
                                
                                for i, line in enumerate(lines):
                                    line_to_search = line if case_sensitive else line.lower()
                                    if search_pattern in line_to_search:
                                        matching_lines.append({
                                            "line_number": i + 1,
                                            "content": line.strip()[:config.line_preview_length]
                                        })
                                
                                relative = file_path.relative_to(config.base_path)
                                results.append({
                                    "path": str(relative),
                                    "name": file_path.name,
                                    "matches": matching_lines[:5]  # First 5 matches
                                })
                                count += 1
                                
                        except Exception:
                            # Skip files that can't be read
                            pass
        else:
            return {"error": "search_type must be 'name' or 'content'"}
        
        logger.info(f"Search completed: '{pattern}' in {path} (found {len(results)} results)")
        
        return {
            "query": pattern,
            "type": search_type,
            "total_results": len(results),
            "results": results,
            "truncated": count >= max_results
        }
        
    except SandboxError as e:
        logger.warning(f"Sandbox violation attempt: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        return {"error": f"Search failed: {str(e)}"}


@mcp.tool()
async def create_directory(path: str) -> Dict:
    """
    Create a new directory.
    
    Args:
        path: Directory path relative to sandbox
    
    Returns:
        Success status or error
    """
    try:
        safe_path = sandbox.validate_path(path)
        
        if safe_path.exists():
            if safe_path.is_dir():
                return {"error": f"Directory '{path}' already exists"}
            else:
                return {"error": f"Path '{path}' exists but is not a directory"}
        
        # Create the directory
        safe_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created directory: {path}")
        
        return {
            "success": True,
            "path": str(safe_path.relative_to(config.base_path)),
            "created": datetime.now().isoformat()
        }
        
    except SandboxError as e:
        logger.warning(f"Sandbox violation attempt: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Error creating directory: {e}")
        return {"error": f"Failed to create directory: {str(e)}"}


# Resources
@mcp.resource("fs://config")
def get_server_config() -> Dict:
    """Expose server configuration as a resource."""
    return {
        "sandbox_path": str(config.base_path),
        "max_file_size": config.max_file_size,
        "max_file_size_human": f"{config.max_file_size / (1024*1024)} MB",
        "allowed_extensions": sorted(list(config.allowed_extensions)),
        "features": {
            "search": True,
            "binary_support": True,
            "file_deletion": True,
            "directory_creation": True,
            "content_validation": True
        }
    }


@mcp.resource("fs://stats")
def get_filesystem_stats() -> Dict:
    """Get statistics about the sandbox filesystem."""
    total_size = 0
    file_count = 0
    dir_count = 0
    file_types = {}
    
    try:
        for item in config.base_path.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                total_size += size
                file_count += 1
                
                # Count file types
                ext = item.suffix.lower()
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1
                    
            elif item.is_dir():
                dir_count += 1
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
    
    return {
        "sandbox_path": str(config.base_path),
        "total_files": file_count,
        "total_directories": dir_count,
        "total_size_bytes": total_size,
        "total_size_human": f"{total_size / (1024*1024):.2f} MB",
        "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]),
        "generated_at": datetime.now().isoformat()
    }


# Prompts
@mcp.prompt()
def analyze_codebase_prompt(language: str = "python") -> str:
    """Generate a prompt for analyzing a codebase."""
    extensions = {
        "python": "*.py",
        "javascript": "*.js",
        "typescript": "*.ts",
        "java": "*.java",
        "cpp": "*.cpp",
        "go": "*.go",
        "rust": "*.rs"
    }
    
    pattern = extensions.get(language, "*")
    
    return f"""Please analyze the {language} codebase in the current directory:

1. Use list_directory to explore the project structure
2. Use search_files with pattern="{pattern}" to find all {language} files
3. Read key files like README, setup/config files, and main modules
4. Analyze the code structure and provide insights on:
   - Project organization and architecture
   - Key dependencies and technologies used
   - Code patterns and best practices followed
   - Potential improvements or issues
   - Documentation completeness

Start by listing the root directory and looking for documentation files."""


@mcp.prompt()
def find_and_fix_prompt(issue: str) -> str:
    """Generate a prompt for finding and fixing issues."""
    return f"""Help me find and fix issues related to: {issue}

1. Use search_files with search_type="content" to find files containing relevant code
2. Read the files to understand the current implementation
3. Identify specific problems or improvements needed
4. Propose fixes with detailed explanations
5. If approved, use write_file to implement the fixes

Please search thoroughly and consider:
- Error handling
- Edge cases
- Performance implications
- Security considerations
- Code style consistency"""


@mcp.prompt()
def backup_files_prompt(file_pattern: str = "*") -> str:
    """Generate a prompt for creating file backups."""
    return f"""Create backups of files matching pattern: {file_pattern}

1. Use search_files to find all files matching the pattern
2. For each file:
   - Read the file content
   - Create a backup with .backup extension
   - Log what was backed up
3. Provide a summary of all backups created

This helps protect against accidental changes or deletions."""


if __name__ == "__main__":
    # Create example files in sandbox for testing
    example_dir = config.base_path / "examples"
    example_dir.mkdir(exist_ok=True)
    
    # Create sample files
    (example_dir / "hello.txt").write_text("Hello from the secure file system server!")
    (example_dir / "data.json").write_text(json.dumps({
        "message": "This is sample data",
        "timestamp": datetime.now().isoformat(),
        "features": ["secure", "fast", "reliable"]
    }, indent=2))
    
    # Create a sample Python file
    (example_dir / "sample.py").write_text('''#!/usr/bin/env python3
"""Sample Python file for testing."""

def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("MCP User"))
''')
    
    # Create subdirectory
    (example_dir / "docs").mkdir(exist_ok=True)
    (example_dir / "docs" / "README.md").write_text("""# File System MCP Server

This is a secure file system server that provides:
- Safe file operations within a sandbox
- Support for text and binary files
- Advanced search capabilities
- Comprehensive security features

## Security Features
- Path traversal prevention
- File type validation
- Size limits
- Audit logging
""")
    
    print(f"🔒 Secure File System MCP Server")
    print(f"📁 Sandbox directory: {config.base_path}")
    print(f"📊 Max file size: {config.max_file_size / (1024*1024)} MB")
    print(f"📝 Allowed extensions: {len(config.allowed_extensions)} types")
    print(f"✅ Server ready for connections!")
    print()
    print("Example files created in sandbox/examples/")
    
    # Run the server
    mcp.run()