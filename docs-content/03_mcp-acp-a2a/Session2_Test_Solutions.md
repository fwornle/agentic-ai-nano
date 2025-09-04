# Session 2: Building a Secure File System MCP Server - Test Solutions

## 📝 Multiple Choice Test - Session 2

**Question 1:** What is the primary purpose of the sandbox in our file system server?  

A) To improve performance  
B) To prevent unauthorized file access ✅  
C) To compress files  
D) To cache file contents  

**Explanation:** The sandbox is the critical security boundary that restricts all file operations to a designated directory, preventing access to sensitive system files and implementing defense-in-depth security.

**Question 2:** Which method is used to safely resolve file paths and prevent directory traversal attacks?  

A) `os.path.join()`  
B) `Path.resolve()` ✅  
C) `str.replace()`  
D) `Path.absolute()`  

**Explanation:** `Path.resolve()` resolves all symlinks and normalizes paths (including `..` components), which is essential for preventing directory traversal attacks like `../../../etc/passwd`.

**Question 3:** How are binary files handled in the read_file tool?  

A) Rejected with an error  
B) Converted to hexadecimal  
C) Encoded as base64 ✅  
D) Read as UTF-8  

**Explanation:** Binary files are encoded as base64 strings for safe transmission through the JSON-RPC protocol, since JSON cannot directly contain binary data.

**Question 4:** What type of validation is performed on file types for security?  

A) Extension only  
B) MIME type only  
C) Both extension and MIME type ✅  
D) File size only  

**Explanation:** The server validates both the file extension (user-provided) and MIME type (content-based detection) to prevent disguised malicious files and ensure accurate file type identification.

**Question 5:** Which logging level is used for security violations in the file system server?  

A) DEBUG  
B) INFO  
C) WARNING ✅  
D) ERROR  

**Explanation:** Security violations like sandbox escape attempts are logged at WARNING level to indicate suspicious activity that should be monitored but doesn't necessarily break the application.

**Question 6:** What happens when a file path attempts to escape the sandbox?  

A) The server crashes  
B) A SandboxError is raised ✅  
C) The path is automatically corrected  
D) Access is granted with a warning  

**Explanation:** The server raises a SandboxError exception when paths attempt to escape the designated sandbox directory, providing a clear security boundary enforcement mechanism.

**Question 7:** Why does the server implement file size limits?  

A) To save disk space  
B) To prevent denial of service attacks ✅  
C) To improve search performance  
D) To maintain file quality  

**Explanation:** File size limits prevent attackers from uploading extremely large files that could exhaust server memory or disk space, causing denial of service attacks.

**Question 8:** What approach does the server use for file type restrictions?  

A) Blacklist dangerous extensions  
B) Whitelist safe extensions ✅  
C) Allow all extensions  
D) Check file signatures only  

**Explanation:** The server uses a whitelist approach, only allowing predefined safe file extensions, which is more secure than blacklisting dangerous extensions that can be easily circumvented.

**Question 9:** How does the search_files tool prevent performance issues?  

A) By caching all file content  
B) By limiting maximum results returned ✅  
C) By using external search engines  
D) By compressing search results  

**Explanation:** The search tool implements result limits to prevent performance degradation when searching through large file sets, ensuring consistent response times.

**Question 10:** What is the primary benefit of using `aiofiles` for file operations?  

A) Non-blocking file I/O operations ✅  
B) Better error handling  
C) Faster disk access  
D) Automatic file compression  

**Explanation:** `aiofiles` provides asynchronous file operations that don't block the event loop, allowing the server to handle multiple concurrent requests efficiently.

---

## 🧭 Navigation

**Back to Test:** [Session 2 Test Questions →](Session2_Production_Implementation.md#multiple-choice-test)

---
