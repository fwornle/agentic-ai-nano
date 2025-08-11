"""
Docker configuration and containerization utilities.
"""

from typing import Dict, Any, List
import os
from dataclasses import dataclass

@dataclass
class DockerConfig:
    """Docker configuration for enterprise deployments."""
    image_name: str
    tag: str = "latest"
    port: int = 8000
    environment_vars: Dict[str, str] = None
    volume_mounts: List[Dict[str, str]] = None
    health_check: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.environment_vars is None:
            self.environment_vars = {}
        if self.volume_mounts is None:
            self.volume_mounts = []
        if self.health_check is None:
            self.health_check = {
                "test": ["CMD", "curl", "-f", f"http://localhost:{self.port}/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }

def generate_dockerfile(config: DockerConfig) -> str:
    """Generate Dockerfile content based on configuration."""
    dockerfile_content = f"""
FROM python:3.11-slim as builder

# Build stage for dependencies
WORKDIR /build
COPY requirements.txt .

# Install build dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libffi-dev \\
    libssl-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim as runtime

# Runtime stage with minimal footprint
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Create non-root user for security
RUN groupadd -r agent && useradd -r -g agent agent
RUN mkdir -p /app/logs /app/data && \\
    chown -R agent:agent /app

# Copy application code
COPY --chown=agent:agent src/ ./src/
COPY --chown=agent:agent config/ ./config/

# Switch to non-root user
USER agent

# Expose port
EXPOSE {config.port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
  CMD curl -f http://localhost:{config.port}/health || exit 1

# Start application
CMD ["python", "-m", "src.main"]
"""
    return dockerfile_content.strip()

def generate_docker_compose(config: DockerConfig) -> str:
    """Generate docker-compose.yml content."""
    compose_content = f"""
version: '3.8'

services:
  {config.image_name}:
    build: .
    ports:
      - "{config.port}:{config.port}"
    environment:
"""
    
    for key, value in config.environment_vars.items():
        compose_content += f"      - {key}={value}\n"
    
    if config.volume_mounts:
        compose_content += "    volumes:\n"
        for mount in config.volume_mounts:
            compose_content += f"      - {mount['host']}:{mount['container']}\n"
    
    compose_content += """
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    
networks:
  default:
    driver: bridge
"""
    
    return compose_content.strip()