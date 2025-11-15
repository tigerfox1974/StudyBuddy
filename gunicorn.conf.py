"""
Gunicorn Production Configuration for StudyBuddy
SocketIO support requires gevent worker class
"""

import os
import multiprocessing

# Server Socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker Processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "gevent"  # REQUIRED for SocketIO - async worker
worker_connections = 1000  # Max concurrent connections for gevent worker
threads = 1  # Not used with gevent
timeout = 120  # Worker timeout (AI operations can take time)
keepalive = 5  # Keep-alive connection timeout

# Logging
accesslog = "-"  # Log to stdout (visible in Docker logs)
errorlog = "-"   # Log to stderr (visible in Docker logs)
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "studybuddy"

# Server Mechanics
daemon = False  # Foreground mode (required for Docker)
pidfile = None  # No pid file (not needed in Docker container)
umask = 0o022
user = None  # Set by USER directive in Dockerfile
group = None
tmp_upload_dir = None  # Use default /tmp

# Server Hooks (optional, for monitoring)
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting StudyBuddy server...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading StudyBuddy server...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("StudyBuddy server is ready. Spawning workers...")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Shutting down StudyBuddy server...")

