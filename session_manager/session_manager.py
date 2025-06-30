import subprocess
from logger import LogManager
from .android_session_handler import AndroidSessionHandler
from .mac_session_handler import MacSessionHandler
from .ios_session_handler import IOSSessionHandler

class AppiumSessionManager:
    """
    Manager for Appium sessions across different platforms.
    
    This class provides methods to create, retrieve, and quit Appium sessions.
    It uses a registry pattern to support multiple platforms and delegates
    platform-specific operations to registered handlers.
    """
    
    # Class-level driver instance storage
    driver_instances = {}
    
    # Platform handler registry
    _platform_handlers = {}
    
    @classmethod
    def register_platform_handler(cls, platform_name, handler_class):
        """
        Register a platform handler.
        
        Args:
            platform_name (str): The name of the platform (e.g., 'android', 'mac').
            handler_class: The class that implements PlatformSessionHandler.
        """
        cls._platform_handlers[platform_name.lower()] = handler_class

    def __init__(self, config_file, urls):
        """
        Initialize the AppiumSessionManager.
        
        Args:
            config_file (list): The parsed configuration file.
            urls (dict): Mapping from base_path to server URL.
        """
        self.hlog = LogManager().get_instance().get_application_logger()
        self.urls = urls
        self.server_config = config_file
        self.driver_list = {}
        
        # Register default platform handlers
        if not AppiumSessionManager._platform_handlers:
            self._register_default_handlers()

    def _register_default_handlers(self):
        """Register the default platform handlers."""
        AppiumSessionManager.register_platform_handler('android', AndroidSessionHandler)
        AppiumSessionManager.register_platform_handler('mac', MacSessionHandler)
        AppiumSessionManager.register_platform_handler('ios', IOSSessionHandler)

    def create_session(self):
        """
        Create sessions based on platformName with validation.
        
        Returns:
            tuple: (bool, dict) - Success status and driver instances.
        """
        self.hlog.d("Creating the sessions....!")
        
        for config in self.server_config:
            platform_name = config.get('platform_name', '').lower()
            base_path = config.get('base_path')
            
            # Get the handler for this platform
            handler_class = AppiumSessionManager._platform_handlers.get(platform_name)
            if not handler_class:
                self.hlog.e(f"Unsupported platform: {platform_name}")
                self._cleanup_sessions()
                return False, self.driver_instances
            
            # Create an instance of the handler
            handler = handler_class()
            
            # Set up the session using the handler
            driver = handler.setup_session(
                self.hlog,
                config,
                base_path,
                self.get_url_by_base_path(base_path)
            )
            
            if not driver:
                self.hlog.e(f"Failed to create session for platform: {platform_name}, basePath: {base_path}")
                self._cleanup_sessions()
                return False, self.driver_instances

            self._add_session(base_path, driver)

        return True, self.driver_instances

    def _add_session(self, base_path, driver):
        """
        Store the driver instance in the session list.
        
        Args:
            base_path (str): The base path for the session.
            driver: The driver instance.
        """
        self.driver_list[base_path] = driver
        AppiumSessionManager.driver_instances[base_path] = driver

    def retrieve_session(self, base_path):
        """
        Retrieve a driver instance by base_path.
        
        Args:
            base_path (str): The base path for the session.
            
        Returns:
            The driver instance if found, None otherwise.
        """
        return self.driver_list.get(base_path)

    def retrieve_all_sessions(self):
        """
        Retrieve all driver instances.
        
        Returns:
            dict: Mapping from base_path to driver instance.
        """
        return self.driver_list

    def get_driver_instance_by_base_path(self, base_path):
        """
        Class method to retrieve driver from shared class-level mapping.
        
        Args:
            base_path (str): The base path for the session.
            
        Returns:
            The driver instance if found, None otherwise.
        """
        return AppiumSessionManager.driver_instances.get(base_path)

    def quit_all_sessions(self):
        """
        Quit all driver instances and clear the session list.
        """
        for base_path, driver in self.driver_list.items():
            self.hlog.d(f"Quitting session for basePath: {base_path}")
            try:
                driver.quit()
            except Exception as e:
                self.hlog.e(f"Error quitting session for {base_path}: {str(e)}")
        self.driver_list.clear()
        AppiumSessionManager.driver_instances.clear()

    def _cleanup_sessions(self):
        """
        Cleanup method to quit all existing sessions when failure occurs.
        """
        self.hlog.e("Session creation failed, cleaning up all sessions...")
        self.quit_all_sessions()

    def get_url_by_base_path(self, base_path):
        """
        Get the URL for a base path.
        
        Args:
            base_path (str): The base path for the session.
            
        Returns:
            str: The URL if found, an error message otherwise.
        """
        return self.urls.get(base_path, f"NO_URL_FOUND'{base_path}'")
