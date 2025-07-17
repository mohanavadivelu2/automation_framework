from .base_validator import BaseValidator

class TestCaseValidator(BaseValidator):
    """
    Validator for test case JSON data.
    
    This class provides methods to validate the structure and contents of test case JSON files,
    including validation sections and exit conditions.
    """
    
    def validate_test_case_data(self, data, test_case_id):
        """
        Validate the structure and contents of a test case JSON.
        
        Args:
            data: The test case data to validate
            test_case_id: ID of the test case for error messages
            
        Returns:
            tuple: (success, message) - Whether validation passed and a message
        """
        if not self.validate_is_dict(data, f"Test case {test_case_id}.json"):
            return False, "INVALID_JSON_NOT_DICTIONARY"

        if not self.validate_has_list(data, "command", f"{test_case_id}.json"):
            return False, "INVALID_JSON_COMMAND_LIST_INVALID"

        if not self.validate_list_not_empty(data, "command", f"{test_case_id}.json"):
            return False, "INVALID_JSON_COMMAND_LIST_EMPTY"
            
        # Validate each command in the command list
        for i, command in enumerate(data["command"]):
            if not self.validate_command(command, f"{test_case_id}.json command[{i}]"):
                return False, f"INVALID_COMMAND_AT_INDEX_{i}"

        return True, "VALID"

    def validate_test_case_group(self, data):
        """
        Validate the structure of the test case group JSON.
        
        Args:
            data: The test case group data to validate
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        if not self.validate_is_dict(data, "Test case group data"):
            return False
        
        return True
        
    def validate_command(self, command, command_path=""):
        """
        Validate a single command structure.
        
        Args:
            command: The command to validate
            command_path: Path to the command for error messages
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        if not isinstance(command, dict):
            self.hlog.e(f"Command at {command_path} must be a dictionary.")
            return False

        # Handle cleanup directive validation
        if "clean_up" in command:
            if not isinstance(command["clean_up"], str):
                self.hlog.e(f"clean_up value at {command_path} must be a string.")
                return False
            # A cleanup directive should only contain the 'clean_up' key
            if len(command) > 1:
                self.hlog.e(f"Cleanup directive at {command_path} should only contain the 'clean_up' key.")
                return False
            return True

        # Validate common_command if present
        if "common_command" in command and not isinstance(command["common_command"], str):
            self.hlog.e(f"common_command at {command_path} must be a string.")
            return False
            
        return True
        
    def validate_validation_section(self, validation, validation_path=""):
        """
        Validate a validation section structure.
        
        Args:
            validation: The validation section to validate
            validation_path: Path to the validation section for error messages
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        if not isinstance(validation, dict):
            self.hlog.e(f"Validation at {validation_path} must be a dictionary.")
            return False
            
        # Validate success section if present
        if "success" in validation:
            if not isinstance(validation["success"], list):
                self.hlog.e(f"Success at {validation_path}.success must be a list.")
                return False
            for i, cmd in enumerate(validation["success"]):
                if not self.validate_command(cmd, f"{validation_path}.success[{i}]"):
                    return False
                    
        # Validate failed section if present
        if "failed" in validation:
            if not isinstance(validation["failed"], list):
                self.hlog.e(f"Failed at {validation_path}.failed must be a list.")
                return False
            for i, cmd in enumerate(validation["failed"]):
                if not self.validate_command(cmd, f"{validation_path}.failed[{i}]"):
                    return False
                    
        # At least one of success or failed should be present
        if "success" not in validation and "failed" not in validation:
            self.hlog.e(f"Validation at {validation_path} must have at least one of 'success' or 'failed' sections.")
            return False
            
        return True
