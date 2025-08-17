# src/session1/tools.py
"""
Tool implementations for bare metal agents.
Provides calculator, web search, and file operation capabilities.
"""

import math
import os
from datetime import datetime
from typing import Dict, List, Any
from base_agent import Tool


class CalculatorTool(Tool):
    """Mathematical calculation tool with safe evaluation"""
    
    def __init__(self):
        super().__init__("calculator", "Perform mathematical calculations")

    async def execute(self, expression: str) -> Dict[str, Any]:
        """Execute mathematical calculation safely"""
        try:
            # Create safe evaluation environment
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round})
            
            # Evaluate with restricted environment
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return {"expression": expression, "result": result}
        except Exception as e:
            return {"expression": expression, "error": str(e)}

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate"
            }
        }


class WebSearchTool(Tool):
    """Tool for web search using a search API"""
    
    def __init__(self, api_key: str = None):
        super().__init__("web_search", "Search the web for information")
        self.api_key = api_key

    async def execute(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Execute web search"""
        # In production, this would call a real search API
        # For demo purposes, we simulate the response
        return {
            "query": query,
            "results": [{
                "title": f"Search result for '{query}'",
                "url": f"https://example.com/search/{query.replace(' ', '-')}",
                "snippet": f"Relevant information about {query} found online."
            }]
        }

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "query": {"type": "string", "description": "Search query"},
            "num_results": {"type": "integer", "description": "Number of results", "default": 5}
        }


class FileOperationTool(Tool):
    """File system operations with security restrictions"""
    
    def __init__(self, allowed_paths: List[str] = None):
        super().__init__("file_ops", "Read and write files")
        self.allowed_paths = allowed_paths or ["./data/"]  # Security: restrict paths

    async def execute(self, operation: str, path: str, content: str = None) -> Dict[str, Any]:
        """Execute file operation with security checks"""
        # Security check: only allow operations in specified directories
        if not any(path.startswith(allowed) for allowed in self.allowed_paths):
            return {"error": f"Path not allowed: {path}"}
        
        try:
            if operation == "read":
                with open(path, 'r') as f:
                    return {"operation": "read", "path": path, "content": f.read()}
            elif operation == "write":
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(content)
                return {"operation": "write", "path": path, "status": "success"}
            else:
                return {"error": f"Unknown operation: {operation}"}
        except Exception as e:
            return {"error": str(e)}

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Operation to perform: 'read' or 'write'"
            },
            "path": {
                "type": "string", 
                "description": "File path"
            },
            "content": {
                "type": "string",
                "description": "Content to write (only for write operation)",
                "required": False
            }
        }