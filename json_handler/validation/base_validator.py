from logger import LogManager

class BaseValidator:
    def __init__(self):
        self.hlog = LogManager.get_instance().get_application_logger()
        
    def validate_is_dict(self, data, name):
        """
        Validate that the data is a dictionary.
        
        Args:
            data: The data to validate
            name: Name of the data for error messages
            
        Returns:
            bool: True if data is a dictionary, False otherwise
        """
        if not isinstance(data, dict):
            self.hlog.e(f"{name} must be a dictionary.")
            return False
        return True
        
    def validate_has_list(self, data, list_name, name):
        """
        Validate that the data contains a list with the specified name.
        
        Args:
            data: The data to validate
            list_name: Name of the list field to check
            name: Name of the data for error messages
            
        Returns:
            bool: True if data contains a list with the specified name, False otherwise
        """
        if list_name not in data or not isinstance(data[list_name], list):
            self.hlog.e(f"'{list_name}' must be a list in {name}.")
            return False
        return True
        
    def validate_list_not_empty(self, data, list_name, name):
        """
        Validate that the list in the data is not empty.
        
        Args:
            data: The data to validate
            list_name: Name of the list field to check
            name: Name of the data for error messages
            
        Returns:
            bool: True if the list is not empty, False otherwise
        """
        if not data[list_name]:
            self.hlog.e(f"'{list_name}' list is empty in {name}.")
            return False
        return True
