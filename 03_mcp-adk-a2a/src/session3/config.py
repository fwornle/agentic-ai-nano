# config.py
import os
from typing import Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""
    name: str
    command: str
    args: List[str]
    transport: str = "stdio"
    description: str = ""
    timeout: int = 30
    retry_attempts: int = 3

@dataclass 
class LLMConfig:
    """Configuration for language models."""
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60

class Config:
    """Main configuration class for LangChain MCP integration."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # LLM Configuration
    LLM = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "openai"),
        model=os.getenv("LLM_MODEL", "gpt-4"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    )
    
    # MCP Server Configurations
    MCP_SERVERS = [
        MCPServerConfig(
            name="weather",
            command="python",
            args=["src/session3/mcp_servers/weather_server.py"],
            description="Weather information and forecasts"
        ),
        MCPServerConfig(
            name="filesystem", 
            command="python",
            args=["src/session3/mcp_servers/filesystem_server.py"],
            description="Secure file system operations"
        ),
        MCPServerConfig(
            name="database",
            command="python", 
            args=["src/session3/mcp_servers/database_server.py"],
            description="Database query and manipulation"
        )
    ]
    
    # Agent Configuration
    AGENT_CONFIG = {
        "max_iterations": int(os.getenv("MAX_ITERATIONS", "10")),
        "verbose": os.getenv("VERBOSE", "true").lower() == "true",
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.7")),
        "timeout": int(os.getenv("AGENT_TIMEOUT", "300"))  # 5 minutes
    }
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"