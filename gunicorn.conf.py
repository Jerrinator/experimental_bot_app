# Gunicorn configuration for Heroku deployment with extended timeouts for OCR processing

import os

# Server socket
bind = "0.0.0.0:" + str(os.environ.get('PORT', 3000))
backlog = 2048

# Worker processes
workers = 1  # Single worker for SocketIO compatibility
worker_class = "eventlet"
worker_connections = 1000

# Timeout settings - extended for OCR processing
timeout = 600  # 10 minutes for long-running OCR operations
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'basic-chatbot'

# Server mechanics
preload_app = True
daemon = False
pidfile = None
tmp_upload_dir = None

# SSL (not used in Heroku but keeping for completeness)
keyfile = None
certfile = None

# Application
wsgi_module = "app:application"
