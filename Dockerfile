# Multi-stage Dockerfile for StudyBuddy Production Deployment
# Stage 1: Builder (dependencies)

FROM python:3.10-slim as builder

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

FROM python:3.10-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 studybuddy

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy gunicorn binary from builder
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy application code
COPY --chown=studybuddy:studybuddy . .

# Create necessary directories with proper permissions
RUN mkdir -p uploads exports invoices && \
    chown -R studybuddy:studybuddy uploads exports invoices

# Switch to non-root user
USER studybuddy

# Expose port
EXPOSE 5000

# Health check (curl kullanarak - requests kütüphanesi gerekmez)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start gunicorn with gevent worker class (required for SocketIO)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]

