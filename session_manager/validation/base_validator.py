"""
Base validator module for session_manager.

This module provides a base class for platform-specific validators with common
validation logic that can be shared across different platforms.
"""

class BaseValidator:
    """
    Base class for platform-specific validators.
    
    This class provides common validation methods that can be used by all
    platform-specific validators.
    """
    
    @staticmethod
    def validate_config_structure(logger, config, expected_config):
        """
        Validate configuration against expected keys and value types.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration to validate.
            expected_config (dict): Dictionary mapping keys to expected types.
            
        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        if not isinstance(config, dict):
            logger.e("Configuration should be a dictionary.")
            return False

        config_keys = set(config.keys())
        expected_keys = set(expected_config.keys())

        extra_keys = config_keys - expected_keys
        missing_keys = expected_keys - config_keys

        if extra_keys:
            logger.e(f"Invalid keys found: {extra_keys}")
        if missing_keys:
            logger.e(f"Missing required keys: {missing_keys}")

        type_errors = []
        for key, expected_type in expected_config.items():
            if key in config and not isinstance(config[key], expected_type):
                type_errors.append(
                    f"Invalid type for '{key}': Expected {expected_type.__name__}, got {type(config[key]).__name__}"
                )

        if type_errors:
            for error in type_errors:
                logger.e(error)

        return not (extra_keys or missing_keys or type_errors)
