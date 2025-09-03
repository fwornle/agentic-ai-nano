# ⚙️ Session 2 Advanced: Production Implementation Guide

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths + Advanced Security Patterns
> Time Investment: 3-4 hours
> Outcome: Complete production-ready file system MCP server

## Complete Production Server Implementation

This module provides the complete, production-ready file system MCP server with all advanced features integrated.

### Complete File Writing Implementation

Implement secure file writing with comprehensive validation:

```python
@mcp.tool()
async def write_file(path: str, content: str,
                    encoding: str = "utf-8",
                    create_dirs: bool = False,
                    append: bool = False) -> Dict:
    """
    Write content to a file with comprehensive safety checks.

    Args:
        path: File path relative to sandbox
        content: Content to write (text or base64 for binary)
        encoding: Text encoding or "base64" for binary
        create_dirs: Create parent directories if needed
        append: Append to existing file instead of overwriting
    """
    try:
        safe_path = sandbox.validate_path(path)

        # Validate the filename doesn't contain directory separators
        if not sandbox.is_safe_filename(safe_path.name):
            return {"error": f"Unsafe filename: {safe_path.name}"}
```

Check file extension against allowed types:

```python
        # Check file extension is allowed
        file_type = {"extension": safe_path.suffix.lower()}
        if file_type["extension"] not in config.allowed_extensions:
            return {"error": f"File type '{file_type['extension']}' not allowed"}
```

Handle directory creation and validation:

```python
        # Create parent directories if requested and safe
        if create_dirs:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directories for: {path}")

        # Ensure parent directory exists
        if not safe_path.parent.exists():
            return {"error": "Parent directory does not exist"}
```

Process binary content (base64 encoded):

```python
        # Handle binary content (base64 encoded)
        if encoding == "base64":
            try:
                binary_content = base64.b64decode(content)
                mode = 'ab' if append else 'wb'

                async with aiofiles.open(safe_path, mode) as f:
                    await f.write(binary_content)

                logger.info(f"Wrote binary file: {path} ({len(binary_content)} bytes)")

            except Exception as e:
                return {"error": f"Invalid base64 content: {str(e)}"}
```

Handle text content and return success status:

```python
        else:
            # Handle text content
            mode = 'a' if append else 'w'

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
```

### Advanced File Search Implementation

Implement powerful search capabilities:

```python
@mcp.tool()
async def search_files(
    pattern: str,
    search_type: str = "name",
    path: str = ".",
    max_results: int = 100
) -> Dict:
    """
    Search for files by name or content.

    Args:
        pattern: Search pattern (glob for names, text for content)
        search_type: "name" or "content"
        path: Starting directory for search
        max_results: Maximum results to return
    """
    try:
        safe_path = sandbox.validate_path(path)

        if not safe_path.is_dir():
            return {"error": f"'{path}' is not a directory"}

        results = []
        count = 0
```

Implement filename-based search:

```python
        if search_type == "name":
            # Search by filename using glob patterns
            for file_path in safe_path.rglob(pattern):
                if count >= max_results:
                    break

                if file_path.is_file():
                    relative = file_path.relative_to(config.base_path)
                    results.append({
                        "path": str(relative),
                        "name": file_path.name,
                        "size": file_path.stat().st_size
                    })
                    count += 1
```

Implement content-based search with safety checks:

```python
        elif search_type == "content":
            # Search file contents
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
```

Process matches and provide context:

```python
                            # Case-insensitive search
                            if pattern.lower() in content.lower():
                                # Find matching lines for context
                                lines = content.splitlines()
                                matching_lines = []

                                for i, line in enumerate(lines):
                                    if pattern.lower() in line.lower():
                                        matching_lines.append({
                                            "line_number": i + 1,
                                            "content": line.strip()[:100]  # First 100 chars
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
```

Return search results:

```python
        else:
            return {"error": "search_type must be 'name' or 'content'"}

        logger.info(f"Search completed: {pattern} in {path} (found {len(results)} results)")

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
```

### Complete File Information Tool

Implement comprehensive file information gathering:

```python
@mcp.tool()
async def get_file_info(path: str) -> Dict:
    """Get detailed information about a file."""
    try:
        safe_path = sandbox.validate_path(path)

        if not safe_path.exists():
            return {"error": f"File '{path}' not found"}

        # Get file statistics and validate file type
        stat = safe_path.stat()
        file_type = validator.validate_file_type(safe_path)

        info = {
            "name": safe_path.name,
            "path": str(safe_path.relative_to(config.base_path)),
            "size": stat.st_size,
            "size_human": f"{stat.st_size / 1024:.2f} KB",
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_directory": safe_path.is_dir(),
            **file_type  # Include MIME type, extension, etc.
        }

        # Add checksum for text files
        if safe_path.is_file() and info["is_text"]:
            info["checksum"] = validator.calculate_checksum(safe_path)

        return info

    except SandboxError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to get file info: {str(e)}"}
```

### MCP Resources and Prompts

Add resources to expose server capabilities:

```python
@mcp.resource("fs://config")
def get_server_config() -> Dict:
    """Expose server configuration as a resource."""
    return {
        "sandbox_path": str(config.base_path),
        "max_file_size": config.max_file_size,
        "allowed_extensions": list(config.allowed_extensions),
        "features": {
            "search": True,
            "binary_support": True,
            "file_watching": False,
            "compression": False
        }
    }
```

Add filesystem statistics resource:

```python
@mcp.resource("fs://stats")
def get_filesystem_stats() -> Dict:
    """Get statistics about the sandbox filesystem."""
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
        "total_files": file_count,
        "total_directories": dir_count,
        "total_size_bytes": total_size,
        "total_size_human": f"{total_size / (1024*1024):.2f} MB"
    }
```

### Code Analysis Prompt

Generate structured prompts for code analysis:

```python
@mcp.prompt()
def analyze_codebase_prompt(language: str = "python") -> str:
    """Generate a prompt for analyzing a codebase."""
    return f"""Please analyze the {language} codebase in the current directory:

1. Use list_directory to explore the project structure
2. Identify key files using search_files with common {language} patterns
3. Read important files like README, configuration, and main modules
4. Provide insights on:
   - Project structure and organization
   - Key dependencies and technologies used
   - Code quality and patterns
   - Potential improvements

Start by listing the root directory and looking for documentation files."""
```

Add issue resolution prompt:

```python
@mcp.prompt()
def find_and_fix_prompt(issue: str) -> str:
    """Generate a prompt for finding and fixing issues."""
    return f"""Help me find and fix issues related to: {issue}

1. Search for files that might contain the issue using search_files
2. Read the relevant files to understand the current implementation
3. Identify the specific problems
4. Suggest fixes with code examples
5. If approved, write the fixed version back to the files

Please be thorough in your search and analysis."""
```

### Complete Server Startup

Add comprehensive server initialization:

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

    # Create a sample Python file
    (example_dir / "example.py").write_text('''
def greet(name):
    """Simple greeting function."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("MCP Server"))
''')

    print(f"🔒 Secure File System MCP Server")
    print(f"📁 Sandbox directory: {config.base_path}")
    print(f"🛡️  Security features enabled:")
    print(f"   - Path validation and sandboxing")
    print(f"   - Content-based file type detection")
    print(f"   - Rate limiting and DoS protection")
    print(f"   - Comprehensive audit logging")
    print(f"Server ready for connections!")

    # Run the server
    mcp.run()
```

## Production Features Summary

Your complete production file system server now includes:

### Security Features

- **Sandboxing**: Restricts operations to designated directory  
- **Path Validation**: Prevents directory traversal attacks  
- **Content-Based File Type Detection**: Checks extensions AND MIME types  
- **Size Limits**: Prevents memory exhaustion  
- **Input Sanitization**: Validates filenames and paths  
- **Audit Logging**: Tracks all operations for compliance  

### Core Capabilities

- **Directory Browsing**: With metadata and filtering  
- **File Reading**: Text and binary support with partial reads  
- **File Writing**: With safety checks and directory creation  
- **Content Search**: Across multiple files with context  
- **File Information**: Including checksums and metadata  
- **Resources**: Configuration and statistics exposure  
- **Prompts**: For common file system analysis tasks  

### Production Features

- **Async I/O**: Non-blocking operations  
- **Result Limits**: On search results and file sizes  
- **Comprehensive Logging**: For monitoring and debugging  
- **Modular Design**: Easy to extend and maintain  
- **Error Handling**: Graceful failure modes  
- **Resource Management**: Efficient memory and CPU usage  

## Complete Assessment

Test your understanding of the complete implementation:

**Question 1**: What is the primary purpose of the sandbox in our file system server?
A) To improve performance
B) To prevent unauthorized file access
C) To compress files
D) To cache file contents

**Question 2**: Which method is used to safely resolve file paths and prevent directory traversal attacks?
A) `os.path.join()`
B) `Path.resolve()`
C) `str.replace()`
D) `Path.absolute()`

**Question 3**: How are binary files handled in the read_file tool?
A) Rejected with an error
B) Converted to hexadecimal
C) Encoded as base64
D) Read as UTF-8

**Question 4**: What type of validation is performed on file types for security?
A) Extension only
B) MIME type only
C) Both extension and MIME type
D) File size only

**Question 5**: Which logging level is used for security violations in the file system server?
A) DEBUG
B) INFO
C) WARNING
D) ERROR

**Question 6**: What happens when a file path attempts to escape the sandbox?
A) The server crashes
B) A SandboxError is raised
C) The path is automatically corrected
D) Access is granted with a warning

**Question 7**: Why does the server implement file size limits?
A) To save disk space
B) To prevent denial of service attacks
C) To improve search performance
D) To maintain file quality

**Question 8**: What approach does the server use for file type restrictions?
A) Blacklist dangerous extensions
B) Whitelist safe extensions
C) Allow all extensions
D) Check file signatures only

**Question 9**: How does the search_files tool prevent performance issues?
A) By caching all file content
B) By limiting maximum results returned
C) By using external search engines
D) By compressing search results

**Question 10**: What is the primary benefit of using `aiofiles` for file operations?
A) Faster disk access
B) Better error handling
C) Non-blocking operations
D) Automatic file compression

### Solutions

1. **B** - To prevent unauthorized file access  
2. **B** - `Path.resolve()`
3. **C** - Encoded as base64  
4. **C** - Both extension and MIME type  
5. **C** - WARNING  
6. **B** - A SandboxError is raised  
7. **B** - To prevent denial of service attacks  
8. **B** - Whitelist safe extensions  
9. **B** - By limiting maximum results returned  
10. **C** - Non-blocking operations  
---

## 🧭 Navigation

**Previous:** [Session 1 - Basic MCP Server ←](Session1_Basic_MCP_Server.md)
**Next:** [Session 3 - LangChain MCP Integration →](Session3_LangChain_MCP_Integration.md)
---
