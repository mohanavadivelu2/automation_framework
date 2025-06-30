"""
Command execution module for widget handlers.

This module provides the main entry point for processing widget commands.
It uses the WidgetFactory to create appropriate handlers for different widget types
and delegates command execution to them.
"""

import json
from .widget_factory import WidgetFactory
from logger import LogManager

def process_command(command: dict):
    """
    Process a widget command.
    
    This function takes a command dictionary, determines the appropriate widget handler,
    and delegates the command processing to that handler.
    
    Args:
        command (dict): The command to process
        
    Returns:
        tuple: (success, message) - The result of the command execution
    """
    tlog = LogManager.get_instance().get_test_case_logger()
    widget_type = command.get("widget_type")
    if not widget_type:
        tlog.d(f"[generic] Skipping command: {command}")
        return False, "MISSING_WIDGET_TYPE"

    try:
        handler = WidgetFactory.get_handler(widget_type)

        # Get method name: default to 'processCommand' if call_fun is missing or empty
        method_name = command.get("call_fun") or "processCommand"

        if not hasattr(handler, method_name):
            raise AttributeError(f"Handler for '{widget_type}' has no method '{method_name}'")

        method = getattr(handler, method_name)
        if callable(method):
            success, message = method(command)
            tlog.d(f"[{widget_type}] Called '{method_name}': Success={success}, Message='{message}'")
            return success, message
        else:
            tlog.d(f"[{widget_type}] '{method_name}' is not callable")
            return False, "NO_FUNCTION_FOUND"

    except ValueError as e:
        tlog.e(f"[{widget_type}] Value Error: {e}")
        return False, f"VALUE_ERROR: {str(e)}"
    except AttributeError as e:
        tlog.e(f"[{widget_type}] Attribute Error: {e}")
        return False, f"ATTRIBUTE_ERROR: {str(e)}"
    except Exception as e:
        tlog.e(f"[{widget_type}] Error: {e}")
        return False, f"UNEXPECTED_ERROR: {str(e)}"
