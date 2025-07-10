
from logger import LogManager, HLog
from global_config.project_configuration import  APP_LOG_FILE_NAME, APP_LOG_FOLDER_PATH
from app_manager import ApplicationManager
from json_handler.test_case_processor import ProcessTestCase
from screen_recorder import ScreenRecorder
import time

def main():

    #Initialize application logger
    log_manager = LogManager.get_instance()
    alog = log_manager.initialize_application_logger(APP_LOG_FOLDER_PATH, APP_LOG_FILE_NAME)
    alog.i("Automation tool version - 2.1.5 - Test Case update")

    # Initialize the application
    manager = ApplicationManager.get_instance()
    


    # Example: Get URL for chrome path
    # url = manager.get_url_by_base_path("chrome")
    # hlog.d(f"URL found was [{url}]")

    # Example: Get driver instance for settings
    """
    driver_instance = manager.get_driver_instance_by_base_path("settings")
    record = ScreenRecorder(driver_instance, "log", "example.mp4")
    if driver_instance is None:
        alog.e("No driver found")
    else:
        alog.d("Driver instance found")
    """


    time.sleep(5)
    processor = ProcessTestCase()
    processor.test_case_processor()

    alog.d("Press Enter to stop servers and close sessions...")
    input()
    
    #record.stop_recording()

    # Deinitialize everything
    manager.deinitialize()

if __name__ == "__main__":
    main()
