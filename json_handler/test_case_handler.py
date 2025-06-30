"""
Test case handler module for processing test cases.

This module provides functions to process test cases, including video recording
setup and command execution with validation and exit handling.
"""

from typing import Tuple, Dict, Any, List, Optional
import time
import os

from .test_case_helper import load_test_case_data
from .validation.test_case_validator import TestCaseValidator
from .test_case_common_command import expand_common_commands
from .test_case_command_processor import CommandProcessor
from global_config.project_configuration import ENABLE_VIDEO_ENABLED
from command_handler.widget.execute_command import process_command
from logger import LogManager
from screen_recorder import ScreenRecorder
from app_manager import ApplicationManager


def setup_video_recording(commands: List[Dict[str, Any]], test_case_id: str, log_path: str) -> Dict[str, ScreenRecorder]:
    """
    Set up video recording for test case execution.
    
    Args:
        commands: List of commands to be executed
        test_case_id: ID of the test case
        log_path: Path to store the video recordings
        
    Returns:
        Dictionary mapping base paths to ScreenRecorder instances
    """
    alog = LogManager.get_instance().get_test_case_logger()
    screen_recorders = {}
    
    # Get unique base_paths
    unique_base_paths = set(cmd.get("base_path") for cmd in commands if "base_path" in cmd)
    alog.i(f">>> Unique base paths: {unique_base_paths}")

    # Start recording for each unique base_path
    for base_path in unique_base_paths:
        driver = ApplicationManager.get_instance().get_driver_instance_by_base_path(base_path)
        if not driver:
            alog.e(f"No driver found for base path: {base_path}")
            continue
        file_name = f"{test_case_id}_{base_path}.mp4"
        recorder = ScreenRecorder(driver, log_path, file_name)
        recorder.start_recording()
        screen_recorders[base_path] = recorder
        alog.i(f">>> Recording started for base path: {base_path}")
    
    time.sleep(2)  # Allow time for recording to start
    return screen_recorders


def stop_video_recording(screen_recorders: Dict[str, ScreenRecorder]) -> None:
    """
    Stop all active video recordings.
    
    Args:
        screen_recorders: Dictionary mapping base paths to ScreenRecorder instances
    """
    alog = LogManager.get_instance().get_test_case_logger()
    
    for base_path, recorder in screen_recorders.items():
        recorder.stop_recording()
        alog.i(f">>> Recording stopped for base path: {base_path}")
    
    time.sleep(2)  # Allow time for recording to stop


def process_test_case(test_case_id: str, log_path: str) -> Tuple[bool, str]:
    """
    Process a test case by loading its data, expanding common commands, and executing them.
    
    This function supports validation sections and exit conditions in commands.
    
    Args:
        test_case_id: ID of the test case to process
        log_path: Path to store logs and recordings
        
    Returns:
        Tuple containing success status and message
    """
    alog = LogManager.get_instance().get_test_case_logger()
    command_processor = CommandProcessor()

    # Load and validate test case data
    test_case_data = load_test_case_data(test_case_id)
    if not test_case_data:
        return False, "FILE_NOT_FOUND_OR_INVALID_JSON"

    # Validate test case structure
    validator = TestCaseValidator()
    valid, message = validator.validate_test_case_data(test_case_data, test_case_id)
    if not valid:
        alog.e(f"Test case validation failed: {message}")
        return False, message

    try:
        # Expand common commands
        commands = expand_common_commands(test_case_data["command"])
        alog.i(f">>> Log path [{log_path}] test case ID [{test_case_id}]")
        alog.i(f">>> Total commands [{len(commands)}]")
        alog.i(f">>> ENABLE_VIDEO_ENABLED commands [{ENABLE_VIDEO_ENABLED}]")
        
        # Set up video recording if enabled
        screen_recorders = {}
        if ENABLE_VIDEO_ENABLED == "YES":
            screen_recorders = setup_video_recording(commands, test_case_id, log_path)

        # Execute commands with validation and exit handling
        message = "SUCCESS"
        status = True
        for command in commands:
            status, message = command_processor.expand_and_process_command(command)
            if not status:
                if message == "Exit Command Triggered":
                    alog.i(f">>> Execution stopped due to exit command")
                    break
                else:
                    alog.i(f">>> Execution Failed {test_case_id}: {message} <<<")
                    break

        # Stop video recording if enabled
        if ENABLE_VIDEO_ENABLED == "YES":
            stop_video_recording(screen_recorders)

        return status, message

    except Exception as e:
        alog.e(f"Exception during test case execution: {e}")
        return False, f"EXECUTION_FAILED: {str(e)}"
