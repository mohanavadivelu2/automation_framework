from appium.options.mac import Mac2Options
from appium import webdriver
from .platform_session_handler import PlatformSessionHandler
from .validation.mac_validator import MacValidator
"""
To control the system popup in iphone
 {
    "platform_name": "mac",
    "port": "4536",
    "base_path": "facets",
    "bundle_id": "com.apple.Facets3",
    "automation_name": "mac2"
}
    
{
    "platform_name": "ios",
    "base_path": "iphone_settings",
    "udid": "00008130-001449110142001C",
    "automation_name": "XCUITest",
    "bundle_id": "com.apple.Preferences",
    "showXcodeLog": true,
    "port": 4727,
    "xcodeOrgId": "27F2VDTJZT",
    "xcodeSigningId": "iPhone Developer"
}

To control the application in the iphone
{
    "platformName": "ios",
    "appium:udid": "00008130-001449110142001C",
    "appium:automationName": "XCUITest",
    "appium:bundleId": "com.apple.Preferences",
    "showXcodeLog": true
}
"""
class MacSessionHandler(PlatformSessionHandler):
    """
    Handler for Mac platform sessions.
    
    This class implements the PlatformSessionHandler interface for Mac devices.
    It provides methods to set up Appium sessions for Mac, delegating validation
    to the MacValidator.
    """
    
    def __init__(self):
        """Initialize the MacSessionHandler with a validator."""
        self.validator = MacValidator()
    
    def validate_config(self, logger, config):
        """
        Validate Mac configuration using the MacValidator.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration to validate.
            
        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        return self.validator.validate_config(logger, config)
    
    def validate_environment(self, logger, config):
        """
        Validate Mac environment using the MacValidator.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration containing environment details.
            
        Returns:
            bool: True if the environment is valid, False otherwise.
        """
        return self.validator.validate_environment(logger, config)
    
    def setup_session(self, logger, config, base_path, command_executor):
        """
        Set up a Mac session.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration for the session.
            base_path (str): The base path for the session.
            command_executor (str): The URL of the Appium server.
            
        Returns:
            webdriver.Remote: The driver instance if successful, None otherwise.
        """
        try:
            # Validate configuration structure
            if not self.validate_config(logger, config):
                logger.e(f"Invalid Mac configuration structure")
                return None
                
            # Validate environment
            if not self.validate_environment(logger, config):
                logger.e(f"Invalid Mac environment")
                return None

            bundle_id = config.get('bundle_id')

            # Set Appium capabilities
            options = Mac2Options()
            options.bundle_id = bundle_id
            new_command_timeout = config.get('newCommandTimeout', 6000)
            options.set_capability('newCommandTimeout', new_command_timeout)

            logger.d(f"Mac session configured for basePath: {base_path}, URL: {command_executor}")
            return webdriver.Remote(command_executor=command_executor, options=options)

        except Exception as e:
            logger.e(f"Failed to start Mac session: {e}")
            return None
