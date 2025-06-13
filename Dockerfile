FROM python:3.11-slim

LABEL maintainer="Zep MCP Server"
LABEL description="Multi-user Memory Context Protocol server for Zep Cloud"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY run_stdio.py .
COPY run_server.py .
COPY mcp.json .

# Create non-root user for security
RUN useradd -m -u 1000 zep && chown -R zep:zep /app
USER zep

# Expose port for SSE transport (optional)
EXPOSE 8052

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.config.settings import Settings; Settings()" || exit 1

# Default command (can be overridden)
CMD ["python", "run_stdio.py"] 