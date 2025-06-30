"""
Android validator module for session_manager.

This module provides validation logic specific to Android platforms.
"""

import subprocess
from .base_validator import BaseValidator

class AndroidValidator(BaseValidator):
    """
    Validator for Android platform configurations and environments.
    
    This class provides methods to validate Android-specific configurations
    and environment settings.
    """
    
    # Expected configuration keys and their types
    EXPECTED_CONFIG = {
        "platform_name": str,
        "port": str,
        "base_path": str,
        "platform_version": str,
        "device_name": str,
        "app_package": str,
        "app_activity": str,
        "automation_name": str
    }
    
    def validate_config(self, logger, config):
        """
        Validate Android configuration against expected keys and value types.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration to validate.
            
        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        return self.validate_config_structure(logger, config, self.EXPECTED_CONFIG)
    
    def validate_environment(self, logger, config):
        """
        Validate that the Android environment is properly set up.
        
        This includes checking that the device is connected, the app is installed,
        and the Android version matches the configuration.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration containing environment details.
            
        Returns:
            bool: True if the environment is valid, False otherwise.
        """
        device_name = config.get('device_name')
        platform_version = config.get('platform_version')
        app_package = config.get('app_package')
        
        # Check if the device is connected
        if not self.validate_android_device(logger, device_name):
            logger.e(f"Android device {device_name} not found.")
            return False

        # Get actual Android version from the device
        actual_version = self.get_android_version(logger, device_name)
        if actual_version is None:
            logger.e(f"Failed to retrieve Android version for device {device_name}.")
            return False

        if actual_version != platform_version:
            logger.e(f"Version mismatch: Config version {platform_version} vs Device version {actual_version}.")
            return False

        # Check if app is installed
        if not self.is_app_installed(logger, device_name, app_package):
            logger.e(f"App {app_package} is not installed on the device {device_name}.")
            return False
            
        return True
    
    def validate_android_device(self, logger, device_name):
        """
        Check if the Android device is available via ADB.
        
        Args:
            logger: The logger instance to use for logging.
            device_name (str): The name of the device to check.
            
        Returns:
            bool: True if the device is available, False otherwise.
        """
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            devices = result.stdout.strip().split("\n")[1:]
            return any(device_name in line and "device" in line for line in devices)
        except Exception as e:
            logger.e(f"Error checking Android device: {str(e)}")
            return False
    
    def get_android_version(self, logger, device_name):
        """
        Retrieve the Android version of the connected device.
        
        Args:
            logger: The logger instance to use for logging.
            device_name (str): The name of the device to check.
            
        Returns:
            str: The Android version if successful, None otherwise.
        """
        try:
            result = subprocess.run(
                ["adb", "-s", device_name, "shell", "getprop", "ro.build.version.release"],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.stdout.strip() else None
        except Exception as e:
            logger.e(f"Error retrieving Android version: {str(e)}")
            return None
    
    def is_app_installed(self, logger, device_name, app_package):
        """
        Check if the specified app is installed on the device.
        
        Args:
            logger: The logger instance to use for logging.
            device_name (str): The name of the device to check.
            app_package (str): The package name of the app to check.
            
        Returns:
            bool: True if the app is installed, False otherwise.
        """
        try:
            result = subprocess.run(
                ["adb", "-s", device_name, "shell", "pm", "list", "packages"],
                capture_output=True, text=True
            )
            installed_packages = [line.replace("package:", "").strip() for line in result.stdout.split("\n") if line]
            return app_package in installed_packages
        except Exception as e:
            logger.e(f"Error checking installed app {app_package} on {device_name}: {str(e)}")
            return False
