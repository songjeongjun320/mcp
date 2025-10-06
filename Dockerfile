# Multi-stage Docker build for MCP Server
# Stage 1: Build dependencies and validate environment
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Add metadata labels
LABEL maintainer="MCP DevOps Team"
LABEL version="${BUILD_VERSION}"
LABEL description="FastMCP Server for Enterprise Requirements Management"
LABEL build.date="${BUILD_DATE}"
LABEL vcs.ref="${VCS_REF}"

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    git \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt

# Copy source code
COPY . .

# Validate Python syntax and basic structure
RUN python -m py_compile mcp_server.py
RUN python -c "from mcp_server import mcp; print('MCP server validation successful')"

# Stage 2: Production runtime
FROM python:3.11-slim as runtime

# Set build arguments for runtime
ARG BUILD_VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Add metadata labels
LABEL maintainer="MCP DevOps Team"
LABEL version="${BUILD_VERSION}"
LABEL description="FastMCP Server for Enterprise Requirements Management"
LABEL build.date="${BUILD_DATE}"
LABEL vcs.ref="${VCS_REF}"

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Create non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser -s /bin/false mcpuser

# Create app directory with proper permissions
WORKDIR /app
RUN mkdir -p /app/logs /app/cache && \
    chown -R mcpuser:mcpuser /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/mcpuser/.local
RUN chown -R mcpuser:mcpuser /home/mcpuser/.local

# Copy application code
COPY --chown=mcpuser:mcpuser . .

# Set Python path to include user packages
ENV PATH=/home/mcpuser/.local/bin:$PATH
ENV PYTHONPATH=/home/mcpuser/.local/lib/python3.11/site-packages:$PYTHONPATH

# Security hardening
RUN chmod -R o-wrx /app && \
    chmod -R g-wx /app && \
    chmod +x /app/mcp_server.py

# Switch to non-root user
USER mcpuser

# Environment variables with secure defaults
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=10000
ENV MCP_LOG_LEVEL=INFO
ENV MCP_METRICS_ENABLED=true
ENV MCP_HEALTH_CHECK_ENABLED=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port (configurable via environment)
EXPOSE ${PORT}

# Production startup command
CMD ["python", "-m", "mcp_server"]