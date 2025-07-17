"""
Test case handler module for processing test cases.

This module provides functions to process test cases, including video recording
setup and command execution with validation and exit handling.
"""

from typing import Tuple, Dict, Any, List, Optional
import time
import os

from .test_case_helper import load_test_case_data, load_json
from .validation.test_case_validator import TestCaseValidator
from .test_case_common_command import expand_common_commands
from .test_case_command_processor import CommandProcessor
from global_config.project_configuration import ENABLE_VIDEO_ENABLED, TEST_CASE_CLEAN_UP
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


def _execute_cleanup(cleanup_file: str, command_processor: CommandProcessor, log_path: str) -> None:
    """Helper function to execute cleanup commands."""
    alog = LogManager.get_instance().get_test_case_logger()
    alog.i(f"--- Executing cleanup file: {cleanup_file} ---")
    
    cleanup_path = os.path.join(TEST_CASE_CLEAN_UP, cleanup_file)
    cleanup_data = load_json(cleanup_path)
    
    if not cleanup_data or "command" not in cleanup_data:
        alog.e(f"Cleanup file not found or invalid: {cleanup_path}")
        return

    cleanup_commands = expand_common_commands(cleanup_data["command"])
    for command in cleanup_commands:
        # We don't care about the status of cleanup commands, just execute them
        command_processor.expand_and_process_command(command)


def process_test_case(test_case_id: str, log_path: str) -> Tuple[bool, str]:
    """
    Process a test case by loading its data, handling cleanup blocks, and executing commands.
    
    Args:
        test_case_id: ID of the test case to process
        log_path: Path to store logs and recordings
        
    Returns:
        Tuple containing success status and message
    """
    alog = LogManager.get_instance().get_test_case_logger()
    command_processor = CommandProcessor()

    test_case_data = load_test_case_data(test_case_id)
    if not test_case_data:
        return False, "FILE_NOT_FOUND_OR_INVALID_JSON"

    validator = TestCaseValidator()
    valid, message = validator.validate_test_case_data(test_case_data, test_case_id)
    if not valid:
        alog.e(f"Test case validation failed: {message}")
        return False, message

    try:
        commands = test_case_data["command"]
        alog.i(f">>> Log path [{log_path}] test case ID [{test_case_id}]")
        alog.i(f">>> Total commands/directives [{len(commands)}]")
        
        screen_recorders = {}
        if ENABLE_VIDEO_ENABLED == "YES":
            # We need to expand common commands first to find all base_paths for recording
            expanded_for_video = expand_common_commands(commands)
            screen_recorders = setup_video_recording(expanded_for_video, test_case_id, log_path)

        message = "SUCCESS"
        status = True
        current_cleanup_file = None

        for command in commands:
            if "clean_up" in command:
                current_cleanup_file = command["clean_up"]
                alog.i(f"Setting cleanup file to: {current_cleanup_file}")
                continue

            # Expand common commands at the point of execution
            expanded_commands = expand_common_commands([command])
            for expanded_command in expanded_commands:
                status, message = command_processor.expand_and_process_command(expanded_command)
                if not status:
                    alog.e(f">>> Command failed: {message} <<<")
                    if current_cleanup_file:
                        _execute_cleanup(current_cleanup_file, command_processor, log_path)
                    # Stop processing further commands in this test case
                    break
            
            if not status:
                break

        if ENABLE_VIDEO_ENABLED == "YES":
            stop_video_recording(screen_recorders)

        return status, message

    except Exception as e:
        alog.e(f"Exception during test case execution: {e}")
        return False, f"EXECUTION_FAILED: {str(e)}"
