"""
Configuration for the File System MCP Server
"""
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
        
        # Allowed file extensions (whitelist approach)
        self.allowed_extensions: Set[str] = {
            '.txt', '.md', '.json', '.yaml', '.yml',
            '.py', '.js', '.ts', '.html', '.css',
            '.csv', '.log', '.conf', '.ini', '.xml',
            '.sh', '.bash', '.zsh', '.fish',
            '.cpp', '.c', '.h', '.hpp', '.java',
            '.rs', '.go', '.rb', '.php'
        }
        
        # Forbidden patterns that might indicate path traversal
        self.forbidden_patterns: List[str] = [
            '..', '~/', '/etc/', '/usr/', '/var/',
            '/sys/', '/proc/', '/dev/', '/tmp/',
            'C:\\Windows', 'C:\\Program Files',
            'C:\\System', 'C:\\Users\\All Users'
        ]
        
        # Performance settings
        self.chunk_size = 8192  # For streaming large files
        self.search_limit = 1000  # Max search results
        self.line_preview_length = 100  # Max chars per line in search results
        
        # Logging settings
        self.log_operations = True
        self.log_file = self.base_path.parent / "filesystem_operations.log"