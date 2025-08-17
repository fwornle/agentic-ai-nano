# deployments/Dockerfile
FROM python:3.11-slim

# Install system dependencies required for our application
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security (principle of least privilege)
RUN useradd -m -u 1000 mcpuser

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
# If requirements don't change, Docker can reuse this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create log directory with proper permissions
RUN mkdir -p /var/log/mcp && chown mcpuser:mcpuser /var/log/mcp

# Switch to non-root user before running the application
USER mcpuser

# Health check endpoint for container orchestrators
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python scripts/health_check.py || exit 1

# Environment variables for consistent behavior
ENV PYTHONUNBUFFERED=1
ENV MCP_LOG_LEVEL=INFO

# Expose metrics port (separate from main application port)
EXPOSE 9090

# Run the server
CMD ["python", "-m", "src.session4.production_mcp_server"]