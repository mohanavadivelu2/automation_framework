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
        Process a command with validation.
        
        Args:
            command: The command to process
            
        Returns:
            Tuple containing success status and a message.
            - (True, message): Command succeeded or failure was handled by validation.
            - (False, "Command Failed, No Validation"): Command failed and requires cleanup.
        """
        # Process the main command
        self.tlog.d(f"Processing command for base_path: {command.get('base_path', 'N/A')}")
        status, message = process_command(command)
        
        # Check if the command failed
        if not status:
            self.tlog.i(f"Command failed: {message}")
            
            # If failed, check for validation or valid_match blocks
            validation = command.get("validation")
            valid_match = command.get("valid_match")
            
            if not validation and not valid_match:
                # No validation defined, signal to exit test case
                return False, "Command Failed, No Validation"
            
            # Process failed validation if present
            if validation:
                failed_commands = validation.get("failed", [])
                if failed_commands:
                    self.tlog.d("Processing failed validation commands")
                    for failed_command in failed_commands:
                        sub_status, sub_message = self.expand_and_process_command(failed_command)
                        if not sub_status:
                            # If a command inside failed validation fails, we exit the test case
                            return False, f"Failure in validation: {sub_message}"
                # If failure was handled by validation, we consider it a success for continuing
                return True, "Failure Handled by Validation"
        
        # Handle valid_match validation if present and command succeeded
        valid_match = command.get("valid_match")
        if valid_match and status:
            self.tlog.d("Valid match validation section found for command")
            matched_image = message
            
            if matched_image in valid_match:
                self.tlog.d(f"Processing valid_match commands for {matched_image}")
                match_commands = valid_match.get(matched_image, [])
                for match_command in match_commands:
                    sub_status, sub_message = self.expand_and_process_command(match_command)
                    if not sub_status:
                        return False, f"Failure in valid_match: {sub_message}"
            
        # Handle success validation if present
        validation = command.get("validation")
        if validation and status:
            self.tlog.d("Validation section found for command")
            success_commands = validation.get("success", [])
            if success_commands:
                self.tlog.d("Processing success validation commands")
                for success_command in success_commands:
                    sub_status, sub_message = self.expand_and_process_command(success_command)
                    if not sub_status:
                        return False, f"Failure in success validation: {sub_message}"
                        
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
            # Since common commands can be nested, we process them one by one
            for expanded_command in expanded_commands:
                status, message = self.process_command_with_validation(expanded_command)
                if not status:
                    # If any command in the common block fails, propagate the failure
                    return False, message
            return True, "Common Command Processed"
        
        # self.tlog.i("calling ---->>>> process_command_with_validation ")
        return self.process_command_with_validation(command)
