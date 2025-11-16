# Multi-stage Dockerfile for StudyBuddy Production Deployment
# Stage 1: Builder (dependencies)
# Allow overriding Python version at build time
ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn with gevent support (required for SocketIO)
RUN pip install --no-cache-dir gunicorn[gevent]

# Stage 2: Runtime
FROM python:${PYTHON_VERSION}-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 studybuddy

# Set working directory
WORKDIR /app

# Copy Python packages from builder
# Copy entire versioned Python lib directory to avoid hardcoding minor version
# This ensures compatibility when PYTHON_VERSION is overridden at build time.
COPY --from=builder /usr/local/lib/python*/ /usr/local/lib/

# Copy gunicorn binary from builder
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy application code
COPY --chown=studybuddy:studybuddy . .

# Create necessary directories with proper permissions
RUN mkdir -p uploads exports invoices instance logs && \
    chown -R studybuddy:studybuddy uploads exports invoices instance logs && \
    chown -R studybuddy:studybuddy /app

# Switch to non-root user
USER studybuddy

# Expose port
EXPOSE 5000

# Health check uses curl to test the root endpoint.
# For production, consider implementing a dedicated /health endpoint
# that doesn't require authentication and returns minimal data.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start gunicorn with gevent worker class (required for SocketIO)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]

