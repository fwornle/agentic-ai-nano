"""
File validation utilities for security and type checking
"""
from pathlib import Path
from typing import Dict, Any, Optional
import magic
import hashlib
import mimetypes


class FileValidator:
    """Validates files for safety and compliance."""
    
    def __init__(self, config):
        self.config = config
        
        # Initialize magic for MIME type detection
        # python-magic can detect file types by content, not just extension
        try:
            self.mime = magic.Magic(mime=True)
            self.has_magic = True
        except Exception:
            # Fallback if python-magic fails
            self.has_magic = False
            mimetypes.init()
    
    def validate_file_size(self, path: Path) -> bool:
        """
        Check if file size is within limits to prevent DoS.
        
        Args:
            path: Path to the file
            
        Returns:
            True if file size is acceptable, False otherwise
        """
        try:
            size = path.stat().st_size
            return size <= self.config.max_file_size
        except Exception:
            # If we can't get file size, assume it's too large (fail safe)
            return False
    
    def validate_file_type(self, path: Path) -> Dict[str, Any]:
        """
        Validate file type and return metadata.
        
        We check both extension AND content to prevent disguised files.
        
        Args:
            path: Path to the file
            
        Returns:
            Dictionary with file type information
        """
        extension = path.suffix.lower()
        
        # Get MIME type
        if self.has_magic and path.exists() and path.is_file():
            # Use magic to detect by content
            try:
                mime_type = self.mime.from_file(str(path))
            except Exception:
                # Fallback to mimetypes
                mime_type = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
        else:
            # Use mimetypes module as fallback
            mime_type = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
        
        # Check against allowed extensions
        allowed = extension in self.config.allowed_extensions
        
        # Detect if file is text or binary
        text_mimes = [
            'text/', 'application/json', 'application/xml', 
            'application/yaml', 'application/x-yaml',
            'application/javascript', 'application/typescript',
            'application/x-sh', 'application/x-python'
        ]
        
        is_text = any(mime_type.startswith(prefix) for prefix in text_mimes)
        
        # Additional text file extensions check
        text_extensions = {
            '.txt', '.md', '.json', '.yaml', '.yml', '.xml',
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', 
            '.css', '.scss', '.sass', '.less',
            '.sh', '.bash', '.zsh', '.fish', '.ps1',
            '.cpp', '.c', '.h', '.hpp', '.java', '.rs', 
            '.go', '.rb', '.php', '.lua', '.r', '.m'
        }
        
        if extension in text_extensions:
            is_text = True
        
        return {
            "allowed": allowed,
            "extension": extension,
            "mime_type": mime_type,
            "is_text": is_text,
            "is_binary": not is_text
        }
    
    def calculate_checksum(self, path: Path, algorithm: str = 'sha256') -> str:
        """
        Calculate checksum of file.
        
        Useful for integrity verification and change detection.
        
        Args:
            path: Path to the file
            algorithm: Hash algorithm to use (sha256, md5, sha1)
            
        Returns:
            Hexadecimal checksum string
        """
        # Select hash algorithm
        if algorithm == 'md5':
            hash_func = hashlib.md5()
        elif algorithm == 'sha1':
            hash_func = hashlib.sha1()
        else:
            hash_func = hashlib.sha256()
        
        # Read file in chunks to handle large files efficiently
        try:
            with open(path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    hash_func.update(byte_block)
            
            return hash_func.hexdigest()
        except Exception as e:
            raise ValueError(f"Failed to calculate checksum: {str(e)}")
    
    def is_safe_content(self, content: str) -> bool:
        """
        Basic content validation to detect potentially malicious patterns.
        
        Args:
            content: File content to validate
            
        Returns:
            True if content appears safe, False otherwise
        """
        # List of suspicious patterns (customize based on your needs)
        suspicious_patterns = [
            '<?php system',  # PHP command execution
            'eval(',  # Code evaluation
            '__import__',  # Python dynamic imports
            'os.system',  # System commands
            'subprocess.call',  # Process execution
            '<script>alert',  # XSS attempts
        ]
        
        content_lower = content.lower()
        
        for pattern in suspicious_patterns:
            if pattern.lower() in content_lower:
                return False
        
        return True