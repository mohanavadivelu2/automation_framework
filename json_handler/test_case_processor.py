"""
Test case processor module for processing test case groups.

This module provides a ProcessTestCase class that handles loading test case groups,
validating them, and processing each test case in the group.
"""

from typing import List, Optional, Dict, Any
import os

from global_config.project_configuration import TEST_CASE_GROUP_FILE, TEST_CASE_GROUP_NAME, APP_LOG_FOLDER_PATH
from .test_case_helper import load_json
from .validation.test_case_validator import TestCaseValidator
from .test_case_handler import process_test_case
from logger import LogManager


class ProcessTestCase:
    """
    Class responsible for processing test cases from a test case group.
    
    This class handles loading test case groups, validating them, and processing
    each test case in the group. It supports validation sections and exit conditions.
    """
    
    def __init__(self):
        """Initialize the ProcessTestCase instance with logging setup."""
        self.log_manager = LogManager.get_instance()
        self.alog = self.log_manager.get_application_logger()

    def get_test_case_list(self) -> List[str]:
        """
        Load and validate the test case group file, then extract the test case list.
        
        Returns:
            List of test case IDs to process, or empty list if validation fails
        """
        test_case_group = load_json(TEST_CASE_GROUP_FILE)
        validator = TestCaseValidator()
        
        if not test_case_group or not validator.validate_test_case_group(test_case_group):
            self.alog.w(f"Failed to load or validate test case group from {TEST_CASE_GROUP_FILE}")
            return []

        test_case_list = test_case_group[TEST_CASE_GROUP_NAME]
        self.alog.i(f">>> Total test case count [{len(test_case_list)}]")
        return test_case_list

    def _get_log_directory(self, test_case_id: str) -> str:
        """
        Create the log directory path for a test case.
        
        Args:
            test_case_id: ID of the test case
            
        Returns:
            Path to the log directory for the test case
        """
        return os.path.join(APP_LOG_FOLDER_PATH, LogManager.timestamp, test_case_id)

    def _process_single_test_case(self, test_case_id: str) -> None:
        """
        Process a single test case with enhanced validation and exit handling.
        
        Args:
            test_case_id: ID of the test case to process
        """
        file_name = f"{test_case_id}.log"
        tlog = self.log_manager.initialize_test_case_logger(APP_LOG_FOLDER_PATH, test_case_id, file_name)
        tlog.i(f"------ Processing the Test Case {test_case_id} ------")
        
        log_dir = self._get_log_directory(test_case_id)
        
        result, message = process_test_case(test_case_id, log_dir)
        
        if not result and message == "FILE_NOT_FOUND_OR_INVALID_JSON":
            tlog.w(f"Test Case ID '{test_case_id}' definition not found or is invalid. Skipping execution for that case")
            return
        
        if result:
            tlog.i(f"Test case {test_case_id} processed successfully: {message}")
        else:
            tlog.e(f"Test case {test_case_id} failed: {message}")

    def test_case_processor(self) -> None:
        """
        Process all test cases in the test case group.
        
        This method loads the test case list, then processes each test case
        in sequence, logging the results. It handles validation sections and
        exit conditions in the test cases.
        """
        test_case_list = self.get_test_case_list()
        if not test_case_list:
            self.alog.w("No test cases found.")
            return

        for test_case_id in test_case_list:
            try:
                self._process_single_test_case(test_case_id)
            except Exception as e:
                self.alog.e(f"Exception while processing test case {test_case_id}: {e}")
