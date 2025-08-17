# Session 2: Building a Secure File System MCP Server - Test Solutions

## 📝 Multiple Choice Test

### Question 1: Security Challenge
**What is the primary purpose of the sandbox in our file system server?**

A) To improve performance  
B) To prevent unauthorized file access ✅  
C) To compress files  
D) To cache file contents  

**Explanation:** The sandbox is the critical security boundary that restricts all file operations to a designated directory, preventing access to sensitive system files and implementing defense-in-depth security.

---

### Question 2: Path Resolution
**Which method is used to safely resolve file paths and prevent directory traversal attacks?**

A) `os.path.join()`  
B) `Path.resolve()` ✅  
C) `str.replace()`  
D) `Path.absolute()`  

**Explanation:** `Path.resolve()` resolves all symlinks and normalizes paths (including `..` components), which is essential for preventing directory traversal attacks like `../../../etc/passwd`.

---

### Question 3: Binary File Handling
**How are binary files handled in the read_file tool?**

A) Rejected with an error  
B) Converted to hexadecimal  
C) Encoded as base64 ✅  
D) Read as UTF-8  

**Explanation:** Binary files are encoded as base64 strings for safe transmission through the JSON-RPC protocol, since JSON cannot directly contain binary data.

---

### Question 4: File Type Validation
**What type of validation is performed on file types for security?**

A) Extension only  
B) MIME type only  
C) Both extension and MIME type ✅  
D) File size only  

**Explanation:** The server validates both file extensions (whitelist approach) and MIME types (content-based detection) to prevent disguised malicious files from bypassing security checks.

---

### Question 5: Security Logging
**Which logging level is used for security violations in the file system server?**

A) DEBUG  
B) INFO  
C) WARNING ✅  
D) ERROR  

**Explanation:** Security violations like sandbox escape attempts are logged at WARNING level to ensure they're captured in production logs without being as severe as system errors.

---

### Question 6: Path Validation Security
**What happens when a file path attempts to escape the sandbox?**

A) The server crashes  
B) A SandboxError is raised ✅  
C) The path is automatically corrected  
D) Access is granted with a warning  

**Explanation:** The `validate_path()` method raises a `SandboxError` when paths attempt to escape the sandbox, providing a clear security boundary that can be handled gracefully.

---

### Question 7: File Size Limits
**Why does the server implement file size limits?**

A) To save disk space  
B) To prevent denial of service attacks ✅  
C) To improve search performance  
D) To maintain file quality  

**Explanation:** File size limits (10MB default) prevent memory exhaustion attacks where malicious users could attempt to crash the server by requesting very large files.

---

### Question 8: Allowed File Extensions
**What approach does the server use for file type restrictions?**

A) Blacklist dangerous extensions  
B) Whitelist safe extensions ✅  
C) Allow all extensions  
D) Check file signatures only  

**Explanation:** The server uses a whitelist approach, only allowing known safe file extensions (`.txt`, `.md`, `.json`, etc.), which is more secure than trying to block all dangerous types.

---

### Question 9: Search Performance
**How does the search_files tool prevent performance issues?**

A) By caching all file content  
B) By limiting maximum results returned ✅  
C) By using external search engines  
D) By compressing search results  

**Explanation:** The search tool limits results (default 100) and respects file size limits to prevent performance degradation from exhaustive searches or large file processing.

---

### Question 10: Asynchronous I/O
**What is the primary benefit of using `aiofiles` for file operations?**

A) Faster disk access  
B) Better error handling  
C) Non-blocking operations ✅  
D) Automatic file compression  

**Explanation:** `aiofiles` enables asynchronous file I/O operations that don't block the server thread, allowing it to handle multiple requests concurrently for better performance.

---

## Scoring Guide

- **10 correct**: Expert level - Ready for production MCP server security  
- **8-9 correct**: Proficient - Strong understanding of secure file systems  
- **6-7 correct**: Competent - Good grasp of security concepts  
- **4-5 correct**: Developing - Review sandboxing and validation sections  
- **Below 4**: Beginner - Revisit security fundamentals and practice examples  

## Key Concepts Summary

1. **Sandboxing**: Critical security boundary preventing unauthorized file access  
2. **Path Validation**: Use `Path.resolve()` and prefix checking to prevent traversal attacks  
3. **Defense in Depth**: Multiple security layers including validation, logging, and limits  
4. **Binary Handling**: Base64 encoding for safe JSON transmission  
5. **Performance Security**: Size limits and result caps prevent denial of service  

---

[Return to Session 2](Session2_FileSystem_MCP_Server.md)