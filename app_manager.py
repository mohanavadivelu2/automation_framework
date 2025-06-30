import threading
import importlib
import sys
import os
from datetime import datetime
from server_manager.server_manager_factory import AppiumServerManagerFactory
from session_manager import AppiumSessionManager
from logger import LogManager, HLog

from global_config.project_configuration import (
    APPIUM_CLIENT_CONFIGURATION_FILE,
    OEM_CONFIGURATION_PACKAGE,
    OEM_CONFIGURATION_CLASS
)


class ApplicationManager:
    _instance = None
    OEM_CONFIGURATION = None
    _lock = threading.Lock()
    _init_lock = threading.Lock()

    def __init__(self):
        if ApplicationManager._instance is not None:
            raise Exception("This class is a singleton!")
        self.alog = LogManager.get_instance().get_application_logger()
        self.server_manager = None
        self.session_manager = None
        self._initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    cls._instance.initialize()
        elif not cls._instance._initialized:
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        with self._init_lock:
            if not self._initialized:
                self.alog.d("ApplicationManager initialize - [Started]")

                # Load OEM Configuration
                self.alog.d("Calling --> load_class_from_path()")
                ApplicationManager.OEM_CONFIGURATION = ApplicationManager.load_class_from_path(OEM_CONFIGURATION_PACKAGE, OEM_CONFIGURATION_CLASS)
                
                
                # Start Appium Servers
                self.server_manager = AppiumServerManagerFactory(APPIUM_CLIENT_CONFIGURATION_FILE)
                self.alog.d("Starting Appium Servers...")
                
                # Start each Appium server defined in the configuration
                success = True
                for entry in self.server_manager.base_path_port_list:
                    for base_path, port in entry.items():
                        self.alog.d(f"Starting Appium server for base_path: '{base_path}' on port: {port}")
                        if not self.server_manager.start_appium_server(port, base_path):
                            self.alog.e(f"Failed to start Appium server for base_path: '{base_path}' on port: {port}")
                            success = False
                            break
                    if not success:
                        break
                
                if success:
                    self.alog.d("--- Appium URLs List ---")
                    urls = self.server_manager.get_all_urls()
                    for base_path, url in urls.items():
                        self.alog.d(f">>>> {base_path}: {url}")

                    self.session_manager = AppiumSessionManager(self.server_manager.json_server_config, urls)
                    status, driver_instances = self.session_manager.create_session()
                    self._initialized = bool(status)
                else:
                    self._initialized = False
                    self.alog.e("Failed to start one or more Appium servers.")

                if driver_instances is not None:
                    self.alog.d(f"Driver instance count [{len(driver_instances)}]")
                else:
                    self.alog.d("Driver instances is None.")


                self.alog.d("ApplicationManager initialize - [Completed]")

    def deinitialize(self):
        with self._init_lock:
            self.alog.d("ApplicationManager deinitialized - [Started]")
            
            if self._initialized:
                if self.session_manager:
                    self.alog.d("Stopping Appium Sessions -> quit_all_sessions")
                    self.session_manager.quit_all_sessions()
                    self.session_manager = None

            self.alog.d("Stopping Appium Servers...")
            if self.server_manager:
                self.alog.d("Stopping Appium Servers -> stop_appium_server")
                self.server_manager.stop_appium_server()
                self.server_manager = None
            self._initialized = False


            self.alog.d("ApplicationManager deinitialized - [Completed]")

    def get_session_manager(self):
        if not self._initialized:
            raise Exception("ApplicationManager not initialized. Call initialize() first.")
        return self.session_manager

    def get_server_manager(self):
        if not self._initialized:
            raise Exception("ApplicationManager not initialized. Call initialize() first.")
        return self.server_manager

    def get_url_by_base_path(self, base_path):
        return self.session_manager.get_url_by_base_path(base_path)

    def get_driver_instance_by_base_path(self, base_path):
        return self.session_manager.get_driver_instance_by_base_path(base_path)
    
    @staticmethod
    def load_class_from_path(package, class_name):
        base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "project_config"))
        if base_directory not in sys.path:
            sys.path.insert(0, base_directory)

        try:
            module = importlib.import_module(package)
            print(f"-----> load_class_from_path OEM_CONFIGURATION_PACKAGE[{package}] OEM_CONFIGURATION_CLASS[{class_name}] ")
            cls = getattr(module, class_name)
            return cls
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to load {class_name} from {package}: {e}")
