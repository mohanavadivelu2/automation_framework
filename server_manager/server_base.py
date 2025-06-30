import subprocess
import time
import json
import os
import signal
from datetime import datetime
from logger import LogManager 
from global_config.project_configuration import SERVER_LOG_FOLDER_PATH

class AppiumServerBase:
    """Base class for handling Appium server management across platforms."""

    def __init__(self, config_file):
        self.alog = LogManager().get_instance().get_application_logger() 
        self.alog.d("Initializing AppiumServerManager...")

        self.log_folder = SERVER_LOG_FOLDER_PATH  # Directory where log files are stored
        self.ip_address = '127.0.0.1'  # Localhost IP used for Appium binding
        self.urls = {}  # Mapping from base_path to server URL
        self.server_process_list = {}  # Mapping of base_path to Appium server process

        self.json_server_config = self._read_config_file(config_file)  # Parsed full JSON config
        self.base_path_port_list = self._extract_base_path_port(self.json_server_config)  # List of base_path-port mappings
        self.stop_appium_server()

    def _read_config_file(self, config_file):
        """Read and parse the JSON server configuration file."""
        try:
            with open(config_file, 'r') as file:
                return json.load(file).get("ServerConfiguration", [])
        except Exception as e:
            self.alog.e(f"Error loading config file: {e}")
            return []

    def _extract_base_path_port(self, config_data):
        """Extract base_path to port mapping from parsed config."""
        try:
            return [
                {entry["base_path"]: entry["port"]}
                for entry in config_data
                if "base_path" in entry and "port" in entry
            ]
        except Exception as e:
            self.alog.e(f"Error extracting base_path-port list: {e}")
            return []

    def stop_appium_server(self):
        """Platform-specific method to be implemented by subclasses."""
        raise NotImplementedError

    def start_appium_server(self, port, base_path):
        """Platform-specific method to be implemented by subclasses."""
        raise NotImplementedError

    def force_deinit_appium_server(self):
        """Platform-specific method to be implemented by subclasses."""
        raise NotImplementedError

    def get_url_by_base_path(self, base_path):
        return self.urls.get(base_path, f"No URL found for base path '{base_path}'")

    def get_all_urls(self):
        return self.urls
