"""
Mac validator module for session_manager.

This module provides validation logic specific to Mac platforms.
"""

import subprocess
from .base_validator import BaseValidator

class MacValidator(BaseValidator):
    """
    Validator for Mac platform configurations and environments.
    
    This class provides methods to validate Mac-specific configurations
    and environment settings.
    """
    
    # Expected configuration keys and their types
    EXPECTED_CONFIG = {
        "platform_name": str,
        "port": str,
        "base_path": str,
        "bundle_id": str,
        "automation_name": str
    }
    
    def validate_config(self, logger, config):
        """
        Validate Mac configuration against expected keys and value types.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration to validate.
            
        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        return self.validate_config_structure(logger, config, self.EXPECTED_CONFIG)
    
    def validate_environment(self, logger, config):
        """
        Validate that the Mac environment is properly set up.
        
        This includes checking that the app is installed.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration containing environment details.
            
        Returns:
            bool: True if the environment is valid, False otherwise.
        """
        bundle_id = config.get('bundle_id')
        
        # Check if app is installed
        if not self.validate_mac_app(logger, bundle_id):
            logger.e(f"App with bundle_id {bundle_id} is not installed on Mac.")
            return False
            
        return True
    
    def validate_mac_app(self, logger, bundle_id):
        """
        Check if the app is installed on Mac.
        
        Args:
            logger: The logger instance to use for logging.
            bundle_id (str): The bundle ID of the app to check.
            
        Returns:
            bool: True if the app is installed, False otherwise.
        """
        try:
            result = subprocess.run(["mdfind", f"kMDItemCFBundleIdentifier == '{bundle_id}'"], capture_output=True, text=True)
            return bool(result.stdout.strip())
        except Exception as e:
            logger.e(f"Error checking Mac app: {str(e)}")
            return False
