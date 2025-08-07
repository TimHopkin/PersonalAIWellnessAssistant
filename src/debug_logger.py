#!/usr/bin/env python3
"""
Development logging system for fast debugging
Structured logging with different levels and real-time output
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json
from pathlib import Path


class DebugLogger:
    """Enhanced logging for development mode"""
    
    def __init__(self, name: str = 'WellnessApp', level: str = 'DEBUG'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_console_handler()
            self._setup_file_handler()
    
    def _setup_console_handler(self):
        """Setup colorized console output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Colorized formatter
        formatter = ColoredFormatter(
            fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup file logging for development"""
        log_file = Path('debug.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def chat_request(self, message: str, session_id: Optional[str] = None):
        """Log chat API requests"""
        self.logger.info(f"CHAT_REQUEST | Message: {message[:50]}{'...' if len(message) > 50 else ''} | Session: {session_id}")
    
    def chat_response(self, response: str, success: bool = True):
        """Log chat API responses"""
        status = "SUCCESS" if success else "ERROR"
        self.logger.info(f"CHAT_RESPONSE | {status} | Response: {response[:50]}{'...' if len(response) > 50 else ''}")
    
    def ai_integration(self, status: str, details: Dict[str, Any]):
        """Log AI integration status"""
        self.logger.info(f"AI_STATUS | {status} | Details: {json.dumps(details, default=str)}")
    
    def api_error(self, endpoint: str, error: Exception, request_data: Dict[str, Any] = None):
        """Log API errors with context"""
        self.logger.error(f"API_ERROR | Endpoint: {endpoint} | Error: {str(error)} | Data: {request_data}")
    
    def performance(self, operation: str, duration_ms: float, details: Dict[str, Any] = None):
        """Log performance metrics"""
        self.logger.info(f"PERFORMANCE | {operation} | {duration_ms:.2f}ms | {details or {}}")
    
    def debug_step(self, step: str, data: Any = None):
        """Log debugging steps with data"""
        if data:
            self.logger.debug(f"DEBUG_STEP | {step} | Data: {json.dumps(data, default=str, indent=2)}")
        else:
            self.logger.debug(f"DEBUG_STEP | {step}")
    
    def security_event(self, event: str, details: Dict[str, Any]):
        """Log security-related events"""
        self.logger.warning(f"SECURITY | {event} | Details: {json.dumps(details, default=str)}")


class ColoredFormatter(logging.Formatter):
    """Add colors to console logging"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        return f"{color}{log_message}{self.COLORS['RESET']}"


# Global logger instance for easy access
debug_logger = DebugLogger()


def log_api_call(func):
    """Decorator to log API calls automatically"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Extract request info
        request_info = {}
        if 'request' in kwargs:
            request_info = {
                'method': kwargs['request'].method,
                'path': kwargs['request'].path,
                'json': kwargs['request'].get_json() if kwargs['request'].is_json else None
            }
        
        debug_logger.debug_step(f"API_CALL_START | {func.__name__}", request_info)
        
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            debug_logger.performance(f"API_CALL | {func.__name__}", duration, {'success': True})
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            debug_logger.api_error(func.__name__, e, request_info)
            debug_logger.performance(f"API_CALL | {func.__name__}", duration, {'success': False})
            raise
    
    return wrapper


def log_chat_interaction(func):
    """Decorator specifically for chat interactions"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Extract message from args/kwargs
        message = None
        session_id = None
        
        if args and len(args) > 0:
            message = str(args[0])[:100]
        if 'message' in kwargs:
            message = kwargs['message'][:100]
        if 'session_id' in kwargs:
            session_id = kwargs['session_id']
        
        debug_logger.chat_request(message or 'Unknown message', session_id)
        
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            
            # Try to extract response
            response = str(result)[:100] if result else 'No response'
            debug_logger.chat_response(response, True)
            debug_logger.performance(f"CHAT | {func.__name__}", duration, {'success': True})
            
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            debug_logger.chat_response(f"Error: {str(e)}", False)
            debug_logger.performance(f"CHAT | {func.__name__}", duration, {'success': False})
            raise
    
    return wrapper


# Convenience functions
def log_info(message: str, **kwargs):
    """Quick info logging with optional structured data"""
    if kwargs:
        debug_logger.logger.info(f"{message} | Data: {json.dumps(kwargs, default=str)}")
    else:
        debug_logger.logger.info(message)


def log_error(message: str, error: Exception = None, **kwargs):
    """Quick error logging"""
    error_str = f" | Error: {str(error)}" if error else ""
    data_str = f" | Data: {json.dumps(kwargs, default=str)}" if kwargs else ""
    debug_logger.logger.error(f"{message}{error_str}{data_str}")


def log_debug(message: str, **kwargs):
    """Quick debug logging"""
    if kwargs:
        debug_logger.logger.debug(f"{message} | Data: {json.dumps(kwargs, default=str)}")
    else:
        debug_logger.logger.debug(message)


# Export for easy importing
__all__ = [
    'DebugLogger', 'debug_logger', 'log_api_call', 'log_chat_interaction',
    'log_info', 'log_error', 'log_debug'
]