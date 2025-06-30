from appium.options.common import AppiumOptions
from appium import webdriver
from .platform_session_handler import PlatformSessionHandler
from .validation.android_validator import AndroidValidator

class AndroidSessionHandler(PlatformSessionHandler):
    """
    Handler for Android platform sessions.
    
    This class implements the PlatformSessionHandler interface for Android devices.
    It provides methods to set up Appium sessions for Android, delegating validation
    to the AndroidValidator.
    """
    
    def __init__(self):
        """Initialize the AndroidSessionHandler with a validator."""
        self.validator = AndroidValidator()
    
    def validate_config(self, logger, config):
        """
        Validate Android configuration using the AndroidValidator.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration to validate.
            
        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        return self.validator.validate_config(logger, config)
    
    def validate_environment(self, logger, config):
        """
        Validate Android environment using the AndroidValidator.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration containing environment details.
            
        Returns:
            bool: True if the environment is valid, False otherwise.
        """
        return self.validator.validate_environment(logger, config)
    
    def setup_session(self, logger, config, base_path, command_executor):
        """
        Set up an Android session.
        
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
                logger.e(f"Invalid Android configuration structure")
                return None
                
            # Validate environment
            if not self.validate_environment(logger, config):
                logger.e(f"Invalid Android environment")
                return None

            device_name = config.get('device_name')
            platform_version = config.get('platform_version')
            app_package = config.get('app_package')
            app_activity = config.get('app_activity')

            # Set Appium capabilities
            options = AppiumOptions()
            options.set_capability('platformName', 'Android')
            options.set_capability('platformVersion', platform_version)
            options.set_capability('deviceName', device_name)
            options.set_capability('appPackage', app_package)
            options.set_capability('appActivity', app_activity)
            options.set_capability('automationName', 'UiAutomator2')
            options.set_capability('newCommandTimeout', 6000)

            logger.d(f"Android session configured for basePath: {base_path}, URL: {command_executor}")
            return webdriver.Remote(command_executor=command_executor, options=options)

        except Exception as e:
            logger.e(f"Failed to start Android session: {e}")
            return None
