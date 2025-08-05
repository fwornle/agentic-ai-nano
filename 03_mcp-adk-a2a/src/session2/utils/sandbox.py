"""
Security sandbox for file system operations
"""
from pathlib import Path
from typing import Optional
import os


class SandboxError(Exception):
    """Raised when attempting to access files outside sandbox."""
    pass


class FileSystemSandbox:
    """Ensures all file operations stay within allowed directories."""
    
    def __init__(self, base_path: Path):
        # Resolve to absolute path to prevent tricks with relative paths
        self.base_path = base_path.resolve()
        
        # Create sandbox if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def validate_path(self, path: str) -> Path:
        """
        Validate and resolve a path within the sandbox.
        
        This is our critical security function - it prevents directory traversal
        attacks by ensuring all paths resolve within our sandbox.
        
        Args:
            path: Requested file path (can be relative or absolute)
            
        Returns:
            Resolved safe path within sandbox
            
        Raises:
            SandboxError: If path escapes sandbox
        """
        try:
            # Handle empty path as current directory
            if not path or path == ".":
                return self.base_path
            
            # Convert string to Path and resolve all symlinks and '..' components
            # This is critical - resolve() follows symlinks and normalizes the path
            requested_path = (self.base_path / path).resolve()
            
            # Critical security check: ensure resolved path is within sandbox
            # We use string comparison to handle edge cases properly
            if not str(requested_path).startswith(str(self.base_path)):
                raise SandboxError(
                    f"Path '{path}' escapes sandbox. "
                    f"Resolved to: {requested_path}, "
                    f"but must be within: {self.base_path}"
                )
            
            return requested_path
            
        except Exception as e:
            # Any path resolution errors are potential security issues
            if isinstance(e, SandboxError):
                raise
            raise SandboxError(f"Invalid path '{path}': {str(e)}")
    
    def is_safe_filename(self, filename: str) -> bool:
        """
        Check if filename is safe (no directory separators or special chars).
        
        This prevents creating files with names like "../evil.sh" or "../../etc/passwd"
        
        Args:
            filename: The filename to validate
            
        Returns:
            True if filename is safe, False otherwise
        """
        # List of characters that should never appear in a safe filename
        dangerous_chars = [
            '/', '\\',  # Directory separators
            '..', '~',  # Parent directory references
            '\0', '\n', '\r',  # Null and newline characters
            ':', '*', '?', '"', '<', '>', '|'  # Windows forbidden chars
        ]
        
        # Check for dangerous patterns
        for char in dangerous_chars:
            if char in filename:
                return False
        
        # Check for hidden files (optional - uncomment if you want to block them)
        # if filename.startswith('.'):
        #     return False
        
        # Ensure filename is not empty or just whitespace
        if not filename or filename.isspace():
            return False
        
        # Additional check: filename shouldn't be too long
        if len(filename) > 255:  # Most filesystems have this limit
            return False
        
        return True
    
    def get_relative_path(self, absolute_path: Path) -> Path:
        """
        Get the relative path from sandbox root.
        
        Args:
            absolute_path: An absolute path within the sandbox
            
        Returns:
            Relative path from sandbox root
        """
        try:
            return absolute_path.relative_to(self.base_path)
        except ValueError:
            # Path is not within sandbox
            raise SandboxError(f"Path {absolute_path} is not within sandbox")