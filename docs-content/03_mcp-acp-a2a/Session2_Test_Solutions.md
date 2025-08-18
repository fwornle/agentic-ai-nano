# Session 2: Building a Secure File System MCP Server - Test Solutions

## 📝 Multiple Choice Test

### Question 1: Security Challenge
**What is the primary purpose of the sandbox in our file system server?**

A) To compress files  
B) To cache file contents  
C) To improve performance  
D) To prevent unauthorized file access ✅  
**Correct Answer: D) To prevent unauthorized file access**

**Explanation:** The sandbox is the critical security boundary that restricts all file operations to a designated directory, preventing access to sensitive system files and implementing defense-in-depth security.

---

### Question 2: Path Resolution
**Which method is used to safely resolve file paths and prevent directory traversal attacks?**

A) `Path.absolute()`  
B) `os.path.join()`  
C) `str.replace()`  
D) `Path.resolve()` ✅  
**Correct Answer: D) `Path.resolve()`**

**Explanation:** `Path.resolve()` resolves all symlinks and normalizes paths (including `..` components), which is essential for preventing directory traversal attacks like `../../../etc/passwd`.

---

### Question 3: Binary File Handling
**How are binary files handled in the read_file tool?**

A) Read as UTF-8  
B) Converted to hexadecimal  
C) Rejected with an error  
D) Encoded as base64 ✅  
**Correct Answer: D) Encoded as base64**

**Explanation:** Binary files are encoded as base64 strings for safe transmission through the JSON-RPC protocol, since JSON cannot directly contain binary data.

---

### Question 4: File Type Validation
**What type of validation is performed on file types for security?**

A) MIME type only  
B) File size only  
C) Both extension and MIME type ✅  
D) Extension only  
**Correct Answer: C) Both extension and MIME type**

**Explanation:** The server validates both file extensions (whitelist approach) and MIME types (content-based detection) to prevent disguised malicious files from bypassing security checks.

---

### Question 5: Security Logging
**Which logging level is used for security violations in the file system server?**

A) INFO  
B) ERROR  
C) DEBUG  
D) WARNING ✅  
**Correct Answer: D) WARNING**

**Explanation:** Security violations like sandbox escape attempts are logged at WARNING level to ensure they're captured in production logs without being as severe as system errors.

---

### Question 6: Path Validation Security
**What happens when a file path attempts to escape the sandbox?**

A) A SandboxError is raised ✅  
B) The server crashes  
C) Access is granted with a warning  
D) The path is automatically corrected  
**Correct Answer: A) A SandboxError is raised**

**Explanation:** The `validate_path()` method raises a `SandboxError` when paths attempt to escape the sandbox, providing a clear security boundary that can be handled gracefully.

---

### Question 7: File Size Limits
**Why does the server implement file size limits?**

A) To prevent denial of service attacks ✅  
B) To improve search performance  
C) To save disk space  
D) To maintain file quality  
**Correct Answer: A) To prevent denial of service attacks**

**Explanation:** File size limits (10MB default) prevent memory exhaustion attacks where malicious users could attempt to crash the server by requesting very large files.

---

### Question 8: Allowed File Extensions
**What approach does the server use for file type restrictions?**

A) Blacklist dangerous extensions  
B) Check file signatures only  
C) Whitelist safe extensions ✅  
D) Allow all extensions  
**Correct Answer: C) Whitelist safe extensions**

**Explanation:** The server uses a whitelist approach, only allowing known safe file extensions (`.txt`, `.md`, `.json`, etc.), which is more secure than trying to block all dangerous types.

---

### Question 9: Search Performance
**How does the search_files tool prevent performance issues?**

A) By using external search engines  
B) By caching all file content  
C) By limiting maximum results returned ✅  
D) By compressing search results  
**Correct Answer: C) By limiting maximum results returned**

**Explanation:** The search tool limits results (default 100) and respects file size limits to prevent performance degradation from exhaustive searches or large file processing.

---

### Question 10: Asynchronous I/O
**What is the primary benefit of using `aiofiles` for file operations?**

A) Automatic file compression  
B) Non-blocking operations ✅  
C) Better error handling  
D) Faster disk access  
**Correct Answer: B) Non-blocking operations**

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