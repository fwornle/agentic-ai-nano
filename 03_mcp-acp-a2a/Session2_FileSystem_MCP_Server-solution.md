# Session 2: File System MCP Server - Solution Guide

## 🧪 Multiple Choice Quiz - Answer Key

### Quick Check Questions

1. **What is the primary purpose of the sandbox in our file system server?**
   - A) To improve performance
   - B) To prevent unauthorized file access ✅ **CORRECT**
   - C) To compress files
   - D) To cache file contents

   **Explanation:** The sandbox is our primary security boundary that restricts all file operations to a designated directory, preventing path traversal attacks and unauthorized access to system files.

2. **Which method do we use to safely resolve file paths?**
   - A) `os.path.join()`
   - B) `Path.resolve()` ✅ **CORRECT**
   - C) `str.replace()`
   - D) `Path.absolute()`

   **Explanation:** `Path.resolve()` is critical because it resolves symlinks, normalizes the path, and converts it to an absolute path, which is essential for our security checks.

3. **How do we handle binary files in the read_file tool?**
   - A) Reject them with an error
   - B) Convert to hexadecimal
   - C) Encode as base64 ✅ **CORRECT**
   - D) Read as UTF-8

   **Explanation:** Binary files are encoded as base64 strings to safely transmit them over the JSON-RPC protocol without corruption.

4. **What type of validation do we perform on file types?**
   - A) Extension only
   - B) MIME type only
   - C) Both extension and MIME type ✅ **CORRECT**
   - D) File size only

   **Explanation:** We validate both the file extension (user-provided) and MIME type (content-based detection) to prevent disguised malicious files and ensure accurate file type identification.

5. **Which logging level do we use for security violations?**
   - A) DEBUG
   - B) INFO
   - C) WARNING ✅ **CORRECT**
   - D) ERROR

   **Explanation:** Security violations like sandbox escape attempts are logged at WARNING level to indicate suspicious activity that should be monitored but doesn't necessarily break the application.

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
    except Exception as e:
        logger.error(f"Unexpected error during move: {e}")
        return {"error": f"Move operation failed: {str(e)}"}
```

### Enhanced Version with Copy Option:

```python
@mcp.tool()
async def move_or_copy_file(
    source: str, 
    destination: str, 
    operation: str = "move",
    overwrite: bool = False
) -> Dict:
    """
    Move or copy a file within the sandbox.
    
    Args:
        source: Source file path relative to sandbox
        destination: Destination file path relative to sandbox  
        operation: "move" or "copy"
        overwrite: Allow overwriting existing files
    
    Returns:
        Success status with operation details
    """
    if operation not in ["move", "copy"]:
        return {"error": "Operation must be 'move' or 'copy'"}
    
    try:
        # Same validation as above...
        safe_source = sandbox.validate_path(source)
        safe_destination = sandbox.validate_path(destination)
        
        # ... validation code ...
        
        if operation == "move":
            safe_source.rename(safe_destination)
            logger.info(f"File moved: {source} -> {destination}")
        else:  # copy
            import shutil
            shutil.copy2(safe_source, safe_destination)
            logger.info(f"File copied: {source} -> {destination}")
        
        # ... return success response ...
        
    except Exception as e:
        return {"error": f"{operation.title()} operation failed: {str(e)}"}
```

### Key Security Considerations Implemented:

1. **Path Validation:** Both source and destination paths are validated through the sandbox
2. **Filename Safety:** Destination filename is checked for dangerous characters
3. **Extension Validation:** Destination file extension must be in allowed list
4. **Existence Checks:** Verify source exists and destination handling with overwrite logic
5. **Permission Handling:** Graceful handling of permission errors
6. **Comprehensive Logging:** All operations are logged for audit trail
7. **Error Recovery:** Verification that move operation completed successfully
8. **Type Safety:** Ensure we're only moving files, not directories

### Test Cases:

```python
# Test basic move
result = await move_file("test.txt", "moved_test.txt")

# Test with overwrite
result = await move_file("source.txt", "existing.txt", overwrite=True)

# Test security violation
result = await move_file("test.txt", "../../../etc/passwd")

# Test invalid destination
result = await move_file("test.txt", "unsafe../name.txt")
```

---

## 🎯 Advanced Extensions

1. **Batch Operations:** Create a `move_multiple_files()` tool that can move several files at once

2. **Atomic Moves:** Implement transaction-like behavior where if any file in a batch fails, all moves are rolled back

3. **Progress Tracking:** For large files, provide progress updates during the move operation

4. **Backup on Overwrite:** Automatically create a backup when overwriting files

5. **Move with Validation:** Validate file content hasn't been corrupted during the move operation

---

## 🔒 Security Insights

The move operation is particularly security-sensitive because:

- **Double Path Validation:** Both source and destination must be validated
- **Filename Injection:** Malicious destination names could create security issues
- **Race Conditions:** File system operations can have timing-based vulnerabilities
- **Permission Escalation:** Moving files could potentially change their security context
- **Data Integrity:** Ensuring the file wasn't corrupted or modified during the move

This implementation addresses these concerns through comprehensive validation, logging, and error handling.