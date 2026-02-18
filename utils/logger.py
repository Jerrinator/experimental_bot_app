# utils/logger.py
# Logging utility for InfoNinja with enhanced Copilot diagnostics format

import logging
import os
import traceback
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
os.makedirs('./logs', exist_ok=True)

# Enhanced log format for Copilot diagnostics
class CopilotFormatter(logging.Formatter):
    def format(self, record):
        base = super().format(record)
        extras = []
        req_id = record.__dict__.get('request_id')
        user_id = record.__dict__.get('user_id') 
        session_id = record.__dict__.get('session_id')
        source = record.__dict__.get('source')
        elapsed = record.__dict__.get('elapsed')
        if req_id:
            extras.append(f"[REQ:{req_id}]")
        if user_id:
            extras.append(f"[USER:{user_id}]")
        if session_id:
            extras.append(f"[SESSION:{session_id}]")
        if source:
            extras.append(f"[SRC:{source}]")
        if elapsed is not None:
            extras.append(f"[ELAPSED:{elapsed:.3f}s]")
        if record.exc_info:
            extras.append(f"[STACKTRACE:{traceback.format_exc()}]")
        return f"{base} {' '.join(extras)}"

# Configure logger with enhanced Copilot format
logger = logging.getLogger("InfoNinja")
logger.setLevel(logging.DEBUG)

# File handler for persistent logs with optimal rotation for Copilot diagnosis
# 2MB per file = ~20,000 interactions per file
# 5 backup files = 100,000 total interactions retained  
# Total disk usage: ~10MB (minimal performance impact)
# Provides sufficient depth for complex multi-edit bug diagnosis
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler(
    './logs/controller.log', 
    maxBytes=2*1024*1024,  # 2MB per file
    backupCount=5,         # Keep 5 rotated files
    encoding='utf-8'
)
formatter = CopilotFormatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)

# Stream handler for console output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Additional specialized log files for edit comparison
def create_specialized_loggers():
    """Create additional loggers for edit comparison tracking with rotation"""
    
    # Workflow log for user interaction tracking
    workflow_logger = logging.getLogger("Workflow")
    workflow_logger.setLevel(logging.INFO)
    workflow_handler = RotatingFileHandler(
        './logs/workflow.log', 
        maxBytes=1*1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    workflow_handler.setFormatter(CopilotFormatter('%(asctime)s [%(levelname)s] %(message)s'))
    workflow_logger.addHandler(workflow_handler)
    
    # Agent activity log for AI action tracking  
    agent_logger = logging.getLogger("Agent")
    agent_logger.setLevel(logging.INFO)
    agent_handler = RotatingFileHandler(
        './logs/agent.log', 
        maxBytes=1*1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    agent_handler.setFormatter(CopilotFormatter('%(asctime)s [%(levelname)s] %(message)s'))
    agent_logger.addHandler(agent_handler)
    
    # Browser interaction log for frontend debugging
    browser_logger = logging.getLogger("Browser")
    browser_logger.setLevel(logging.INFO)
    browser_handler = RotatingFileHandler(
        './logs/browser.log', 
        maxBytes=1*1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    browser_handler.setFormatter(CopilotFormatter('%(asctime)s [%(levelname)s] %(message)s'))
    browser_logger.addHandler(browser_handler)
    
    return workflow_logger, agent_logger, browser_logger

# Create specialized loggers
workflow_logger, agent_logger, browser_logger = create_specialized_loggers()

def log_edit_session_start(edit_description="Code edit session"):
    """Mark the start of an edit session for comparison tracking"""
    session_marker = f"=== EDIT SESSION START: {edit_description} ==="
    logger.info(session_marker, extra={'source': 'edit_tracker', 'log_type': 'session_start'})
    workflow_logger.info(session_marker, extra={'source': 'edit_tracker', 'log_type': 'session_start'})
    return session_marker

def log_edit_session_end(edit_description="Code edit session"):
    """Mark the end of an edit session for comparison tracking"""
    session_marker = f"=== EDIT SESSION END: {edit_description} ==="
    logger.info(session_marker, extra={'source': 'edit_tracker', 'log_type': 'session_end'})
    workflow_logger.info(session_marker, extra={'source': 'edit_tracker', 'log_type': 'session_end'})
    return session_marker
