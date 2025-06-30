from abc import ABC, abstractmethod

class PlatformSessionHandler(ABC):
    """
    Abstract base class for platform-specific session handlers.
    
    This class defines the interface that all platform session handlers must implement.
    It provides a consistent way to validate configurations and set up sessions across
    different platforms.
    """
    
    @abstractmethod
    def validate_config(self, logger, config):
        """
        Validate the configuration for this platform.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration to validate.
            
        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        pass
    
    @abstractmethod
    def validate_environment(self, logger, config):
        """
        Validate that the environment is properly set up for this platform.
        
        This includes checking that devices are connected, apps are installed, etc.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration containing environment details.
            
        Returns:
            bool: True if the environment is valid, False otherwise.
        """
        pass
    
    @abstractmethod
    def setup_session(self, logger, config, base_path, command_executor):
        """
        Set up a session for this platform.
        
        Args:
            logger: The logger instance to use for logging.
            config (dict): The configuration for the session.
            base_path (str): The base path for the session.
            command_executor (str): The URL of the Appium server.
            
        Returns:
            webdriver.Remote: The driver instance if successful, None otherwise.
        """
        pass
