# Session 2: Building a Secure File System MCP Server - Test Solutions

## 📝 Multiple Choice Test - Answer Key

### Question 1: Sandbox Purpose
**What is the primary purpose of the sandbox in our file system server?**

a) To improve performance  
b) To prevent unauthorized file access ✅  
c) To compress files  
d) To cache file contents  
**Correct Answer: b) To prevent unauthorized file access**

**Explanation:** The sandbox is the critical security boundary that restricts all file operations to a designated directory, preventing access to sensitive system files and implementing defense-in-depth security.

---

### Question 2: Path Resolution
**Which method is used to safely resolve file paths and prevent directory traversal attacks?**

a) `os.path.join()`  
b) `Path.resolve()` ✅  
c) `str.replace()`  
d) `Path.absolute()`  
**Correct Answer: b) `Path.resolve()`**

**Explanation:** `Path.resolve()` resolves all symlinks and normalizes paths (including `..` components), which is essential for preventing directory traversal attacks like `../../../etc/passwd`.

---

### Question 3: Binary File Handling
**How are binary files handled in the read_file tool?**

a) Rejected with an error  
b) Converted to hexadecimal  
c) Encoded as base64 ✅  
d) Read as UTF-8  
**Correct Answer: c) Encoded as base64**

**Explanation:** Binary files are encoded as base64 strings for safe transmission through the JSON-RPC protocol, since JSON cannot directly contain binary data.

---

### Question 4: File Type Validation
**What type of validation is performed on file types for security?**

a) Extension only  
b) MIME type only  
c) Both extension and MIME type ✅  
d) File size only  
**Correct Answer: c) Both extension and MIME type**

**Explanation:** The server validates both the file extension (user-provided) and MIME type (content-based detection) to prevent disguised malicious files and ensure accurate file type identification.

---

### Question 5: Security Logging
**Which logging level is used for security violations in the file system server?**

a) DEBUG  
b) INFO  
c) WARNING ✅  
d) ERROR  
**Correct Answer: c) WARNING**

**Explanation:** Security violations like sandbox escape attempts are logged at WARNING level to indicate suspicious activity that should be monitored but doesn't necessarily break the application.

---

### Question 6: Sandbox Violations
**What happens when a file path attempts to escape the sandbox?**

a) The server crashes  
b) A SandboxError is raised ✅  
c) The path is automatically corrected  
d) Access is granted with a warning  
**Correct Answer: b) A SandboxError is raised**

**Explanation:** The server raises a SandboxError exception when paths attempt to escape the designated sandbox directory, providing a clear security boundary enforcement mechanism.

---

### Question 7: File Size Limits
**Why does the server implement file size limits?**

a) To save disk space  
b) To prevent denial of service attacks ✅  
c) To improve search performance  
d) To maintain file quality  
**Correct Answer: b) To prevent denial of service attacks**

**Explanation:** File size limits prevent attackers from uploading extremely large files that could exhaust server memory or disk space, causing denial of service attacks.

---

### Question 8: File Type Restrictions
**What approach does the server use for file type restrictions?**

a) Blacklist dangerous extensions  
b) Whitelist safe extensions ✅  
c) Allow all extensions  
d) Check file signatures only  
**Correct Answer: b) Whitelist safe extensions**

**Explanation:** The server uses a whitelist approach, only allowing predefined safe file extensions, which is more secure than blacklisting dangerous extensions that can be easily circumvented.

---

### Question 9: Search Performance
**How does the search_files tool prevent performance issues?**

a) By caching all file content  
b) By limiting maximum results returned ✅  
c) By using external search engines  
d) By compressing search results  
**Correct Answer: b) By limiting maximum results returned**

**Explanation:** The search tool implements result limits to prevent performance degradation when searching through large file sets, ensuring consistent response times.

---

### Question 10: Async File Operations
**What is the primary benefit of using `aiofiles` for file operations?**

a) Non-blocking file I/O operations ✅  
b) Better error handling  
c) Faster disk access  
d) Automatic file compression  
**Correct Answer: a) Non-blocking file I/O operations**

**Explanation:** `aiofiles` provides asynchronous file operations that don't block the event loop, allowing the server to handle multiple concurrent requests efficiently.

---

## 💡 Practical Exercise Solution

**Challenge:** Extend the server with a tool that safely moves/renames files.

### Complete Solution:

```python
@mcp.tool()
async def move_file(source: str, destination: str, overwrite: bool = False) -> Dict:
    """
    Move or rename a file within the sandbox.
    
    This tool safely moves files while maintaining all security boundaries
    and providing comprehensive validation.
    
    Args:
        source: Source file path relative to sandbox
        destination: Destination file path relative to sandbox
        overwrite: Allow overwriting existing files (default: False)
    
    Returns:
        Success status with operation details or error information
    """
    try:
        # Validate both paths are within sandbox
        safe_source = sandbox.validate_path(source)
        safe_destination = sandbox.validate_path(destination)
        
        # Check source exists and is a file
        if not safe_source.exists():
            return {"error": f"Source file '{source}' does not exist"}
        
        if not safe_source.is_file():
            return {"error": f"Source '{source}' is not a file (directories not supported)"}
        
        # Validate destination filename
        if not sandbox.is_safe_filename(safe_destination.name):
            return {"error": f"Unsafe destination filename: {safe_destination.name}"}
        
        # Check destination file extension is allowed
        dest_extension = safe_destination.suffix.lower()
        if dest_extension and dest_extension not in config.allowed_extensions:
            return {"error": f"Destination file type '{dest_extension}' not allowed"}
        
        # Check if destination already exists
        if safe_destination.exists():
            if not overwrite:
                return {
                    "error": f"Destination '{destination}' already exists. Use overwrite=true to replace it."
                }
            
            # Additional check: ensure destination is a file if overwriting
            if not safe_destination.is_file():
                return {"error": f"Cannot overwrite '{destination}': not a file"}
            
            logger.warning(f"Overwriting existing file: {destination}")
        
        # Create destination directory if it doesn't exist
        safe_destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Get source file info before moving (for logging)
        source_stat = safe_source.stat()
        source_size = source_stat.st_size
        
        # Perform the move operation
        safe_source.rename(safe_destination)
        
        # Verify the move was successful
        if not safe_destination.exists():
            return {"error": "Move operation failed: destination file not found after move"}
        
        if safe_source.exists():
            return {"error": "Move operation failed: source file still exists after move"}
        
        # Get destination file info
        dest_stat = safe_destination.stat()
        
        # Log the successful operation
        logger.info(f"File moved: {source} -> {destination} ({source_size} bytes)")
        
        return {
            "success": True,
            "operation": "move",
            "source": source,
            "destination": destination,
            "size": dest_stat.st_size,
            "modified": datetime.fromtimestamp(dest_stat.st_mtime).isoformat(),
            "overwritten": overwrite and safe_destination.exists()
        }
        
    except SandboxError as e:
        logger.warning(f"Sandbox violation in move operation: {e}")
        return {"error": str(e)}
    except PermissionError as e:
        logger.error(f"Permission denied during move: {e}")
        return {"error": f"Permission denied: {str(e)}"}
    except OSError as e:
        logger.error(f"OS error during move: {e}")
        return {"error": f"File system error: {str(e)}"}
```

### Key Learning Points:

1. **Comprehensive Path Validation:** Both source and destination paths must be validated against the sandbox
2. **File Type Security:** Destination file extensions are validated against the allowed list
3. **Existence Checks:** Verify source exists and handle destination conflicts appropriately
4. **Error Recovery:** Verify the operation completed successfully before returning success
5. **Detailed Logging:** Log all operations for security monitoring and debugging
6. **Graceful Error Handling:** Different exception types are handled with appropriate responses

### Security Considerations:

- **Sandbox Enforcement:** All paths are validated to prevent directory traversal
- **Overwrite Protection:** Explicit permission required to overwrite existing files
- **File Type Validation:** Destination files must have allowed extensions
- **Operation Verification:** Success is verified by checking file system state
- **Audit Trail:** All operations are logged for security monitoring

### Extension Ideas:

1. **Atomic Operations:** Implement temporary files to ensure operation atomicity
2. **Batch Operations:** Support moving multiple files in a single operation
3. **Copy Operations:** Add similar functionality for file copying
4. **Directory Support:** Extend to support moving entire directories
5. **Backup on Overwrite:** Create backups when overwriting files

---

## Scoring Guide

- **9-10 correct**: Excellent understanding of secure file system implementation
- **7-8 correct**: Good grasp of security concepts, review specific areas where questions were missed
- **5-6 correct**: Basic understanding present, recommend reviewing security sections
- **Below 5**: Recommend thoroughly reviewing Session 2 content and security best practices

## Key Concepts Review

If you missed questions in these areas, review the corresponding sections:

**Security Fundamentals (Questions 1, 2, 5, 6):**
- Review sandbox implementation and path validation
- Focus on security logging and violation handling
- Study directory traversal prevention techniques

**File Handling (Questions 3, 4, 7, 8):**
- Review binary file encoding strategies
- Focus on file type validation approaches
- Study whitelist vs blacklist security models

**Performance & Architecture (Questions 9, 10):**
- Review async programming benefits
- Focus on performance optimization techniques
- Study scalability considerations

---

[← Return to Session 2](Session2_FileSystem_MCP_Server.md)