import os
from datetime import datetime
from logger.log_handler import HLog

class LogManager:
    _instance = None
    _log_app = None
    _log_test = None
    _log_dir = None
    timestamp = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls.timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        return cls._instance

    @staticmethod
    def get_instance():
        if LogManager._instance is None:
            LogManager._instance = LogManager()
            LogManager.timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        return LogManager._instance

    def initialize_application_logger(self, base_path, file_name):
        log_dir = os.path.join(base_path, LogManager.timestamp)
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, file_name)

        if not os.path.exists(log_file_path):
            open(log_file_path, 'a').close()

        self._log_dir = log_dir
        self._log_app = HLog(log_file_path)
        return self._log_app

    def initialize_test_case_logger(self, base_path, test_id, file_name):
        log_dir = os.path.join(base_path, LogManager.timestamp, test_id)
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, file_name)

        if not os.path.exists(log_file_path):
            open(log_file_path, 'a').close()

        self._log_dir = log_dir
        self._log_test = HLog(log_file_path)
        return self._log_test

    def get_application_logger(self):
        return self._log_app

    def get_test_case_logger(self):
        return self._log_test

    def get_log_dir(self):
        return self._log_dir
