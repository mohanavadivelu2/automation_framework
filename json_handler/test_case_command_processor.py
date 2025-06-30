"""
Command processor module for test case execution.

This module provides a CommandProcessor class that handles the execution of commands
with validation and exit handling.
"""

from typing import Tuple, Dict, Any, List
from .test_case_common_command import expand_common_commands
from command_handler.widget.execute_command import process_command
from logger import LogManager


class CommandProcessor:
    """
    Class responsible for processing commands with validation and exit handling.
    
    This class handles the execution of commands, including validation sections
    and exit conditions.
    """
    
    def __init__(self):
        """Initialize the CommandProcessor instance with logging setup."""
        self.log_manager = LogManager.get_instance()
        self.tlog = self.log_manager.get_test_case_logger()
        
    def process_command_with_validation(self, command: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Process a command with validation and exit handling.
        
        Args:
            command: The command to process
            
        Returns:
            Tuple containing success status and message
        """
        # Check for exit condition
        exit_status = command.get("exit", "NO")
        
        # Process the main command
        self.tlog.d(f"Processing command for base_path: {command.get('base_path', 'N/A')}")
        status, message = process_command(command)
        
        if not status:
            self.tlog.i(f"Command failed: {message}")
        
        # Handle valid_match validation if present and command succeeded
        valid_match = command.get("valid_match")
        if valid_match and status:
            self.tlog.d("Valid match validation section found for command")
            
            # The message is now directly the matched image key (e.g., "image_one")
            matched_image = message
            
            if matched_image in valid_match:
                self.tlog.d(f"Processing valid_match commands for {matched_image}")
                match_commands = valid_match.get(matched_image, [])
                for match_command in match_commands:
                    sub_status, sub_message = self.expand_and_process_command(match_command)
                    if not sub_status and match_command.get("exit", "NO") == "YES":
                        self.tlog.i(f"Exit triggered inside valid_match for {matched_image}")
                        return False, "Exit Command Triggered"
            
        # Handle validation if present
        validation = command.get("validation")
        if validation:
            self.tlog.d("Validation section found for command")
            
            if status:
                # Command succeeded, process success validation
                success_commands = validation.get("success", [])
                if success_commands:
                    self.tlog.d("Processing success validation commands")
                    for success_command in success_commands:
                        sub_status, sub_message = self.expand_and_process_command(success_command)
                        if not sub_status and success_command.get("exit", "NO") == "YES":
                            self.tlog.i("Exit triggered inside success validation")
                            return False, "Exit Command Triggered"
                status = True
                message = "VALIDATION_SUCCESS_EXECUTED"
            else:
                # Command failed, process failed validation
                failed_commands = validation.get("failed", [])
                if failed_commands:
                    self.tlog.d("Processing failed validation commands")
                    for failed_command in failed_commands:
                        sub_status, sub_message = self.expand_and_process_command(failed_command)
                        if not sub_status and failed_command.get("exit", "NO") == "YES":
                            self.tlog.i("Exit triggered inside failed validation")
                            return False, "Exit Command Triggered"
                status = True
                message = "VALIDATION_FAILED_EXECUTED"
        
        # Handle exit condition
        if exit_status == "YES":
            self.tlog.i("Exit triggered. Stopping further command execution.")
            return False, "Exit Command Triggered"
            
        return status, message
        
    def expand_and_process_command(self, command: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Expand common commands and process the resulting command.
        
        Args:
            command: The command to expand and process
            
        Returns:
            Tuple containing success status and message
        """
        if "common_command" in command:
            expanded_commands = expand_common_commands([command])
            for expanded_command in expanded_commands:
                status, message = self.process_command_with_validation(expanded_command)
                if not status:
                    return False, message
            return True, "Common Command Processed"
        else:
            self.tlog.i("calling ---->>>> process_command_with_validation ")
            return self.process_command_with_validation(command)
