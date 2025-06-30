import os
import json
from typing import Dict, Any, Optional
from global_config.project_configuration import TEST_CASE_DIRECTORY
from logger import LogManager


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load and validate JSON syntax.
    
    Args:
        file_path: Path to the JSON file to load
        
    Returns:
        Dict containing the parsed JSON data, or None if the file is not found or contains invalid JSON
    """
    alog = LogManager.get_instance().get_application_logger()
    try:
        with open(file_path, "r") as file:
            return json.load(file)  # Raises JSONDecodeError if syntax is invalid
    except FileNotFoundError:
        alog.e(f"File not found - {file_path}")
    except json.JSONDecodeError as e:
        alog.e(f"Invalid JSON format in {file_path} - {e}")
    return None


def load_test_case_data(test_case_id: str) -> Optional[Dict[str, Any]]:
    """
    Construct the file path for a test case and load its JSON content.
    
    Args:
        test_case_id: ID of the test case to load
        
    Returns:
        Dict containing the test case data, or None if the file is not found or contains invalid JSON
    """
    alog = LogManager.get_instance().get_application_logger()
    alog.i(f"Loading test case: {test_case_id} from {TEST_CASE_DIRECTORY}")
    test_case_file = os.path.join(TEST_CASE_DIRECTORY, f"{test_case_id}.json")
    return load_json(test_case_file)
