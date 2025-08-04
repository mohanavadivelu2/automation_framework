"""
Logging Utility for Image Comparator Module

This module provides a unified logging interface that automatically routes
logging based on the calling context:
- Unit tests: Always console logging
- Source code: Always LogManager with debug level
"""

import inspect
import os
from logger import LogManager


class ConsoleLogger:
    """Simple console logger for unit tests."""
    
    def debug(self, message):
        print(f"DEBUG: {message}")
    
    def info(self, message):
        print(f"INFO: {message}")
    
    def warning(self, message):
        print(f"WARNING: {message}")
    
    def error(self, message):
        print(f"ERROR: {message}")
    
    def v(self, message):
        print(f"VERBOSE: {message}")
    
    def d(self, message):
        print(f"DEBUG: {message}")
    
    def i(self, message):
        print(f"INFO: {message}")
    
    def w(self, message):
        print(f"WARNING: {message}")
    
    def e(self, message):
        print(f"ERROR: {message}")


def is_unit_test_context():
    """
    Determine if the current call is from unit test context.
    
    Returns:
        bool: True if called from unit_test folder, False otherwise
    """
    # Get the current call stack
    frame = inspect.currentframe()
    try:
        # Walk up the call stack to find the originating file
        while frame:
            frame_filename = frame.f_code.co_filename
            if frame_filename:
                # Normalize path separators
                normalized_path = os.path.normpath(frame_filename)
                # Check if any part of the path contains 'unit_test'
                if 'unit_test' in normalized_path:
                    return True
            frame = frame.f_back
        return False
    finally:
        del frame


def get_logger():
    """
    Get appropriate logger based on calling context.
    
    Returns:
        Logger instance - ConsoleLogger for unit tests, LogManager for source code
    """
    if is_unit_test_context():
        return ConsoleLogger()
    else:
        try:
            app_logger = LogManager.get_instance().get_application_logger()
            if app_logger:
                return app_logger
            else:
                # Fallback to console if LogManager is not properly initialized
                return ConsoleLogger()
        except Exception:
            # Fallback to console if LogManager fails
            return ConsoleLogger()


def get_logger_for_class(class_instance=None):
    """
    Get logger for a class instance, with optional fallback.
    
    Args:
        class_instance: Optional class instance for context
        
    Returns:
        Logger instance
    """
    return get_logger()
