
#Project configuration
ENABLE_VIDEO_ENABLED = "NO"
TEST_CASE_LOGGING_ENABLED = True
EXECUTE_GROUP = "TATA_PCTS" #"FACETS" / "SANITY"
USB_CONTROLLER_DRIVER = "HARMAN" #CLEVARE or ACRONAMI
USB_CONTROLLER_PORT_NUMBER = 1
USB_CONTROLLER_PORT_RESET_DELAY = 2  # Delay in seconds for USB port reset

if EXECUTE_GROUP == "TATA_FACETS":
   BASE_DIRECTORY = "project_config/tata/facets/"
   APPIUM_CLIENT_CONFIGURATION_FILE = BASE_DIRECTORY + "client/mac_client_configuration.json" 
   TEST_CASE_GROUP_FILE = BASE_DIRECTORY + "master/all_test_case.json"
   TEST_CASE_GROUP_NAME = "all_test_case"
   TEST_CASE_DIRECTORY = BASE_DIRECTORY + "test_case/"
   TEST_CASE_COMMON_COMMAND = BASE_DIRECTORY+"common/"
   TEST_CASE_CLEAN_UP = BASE_DIRECTORY + "clean_up/"
   IMAGES_PATH = BASE_DIRECTORY + "images/"
   OEM_CONFIGURATION_JSON = BASE_DIRECTORY + "config/oem_config.json"
   OEM_CONFIGURATION_FILE = BASE_DIRECTORY + "config/oem_config.py"
   OEM_CONFIGURATION_PACKAGE = "project_config.tata.facets.config.oem_config"
   OEM_CONFIGURATION_CLASS = "OEMConfiguration"

elif EXECUTE_GROUP == "TATA_GEN3+_FACETS":
   BASE_DIRECTORY = "project_config/tata_gen3+/facets/"
   APPIUM_CLIENT_CONFIGURATION_FILE = BASE_DIRECTORY + "client/android_client_configuration.json"
   TEST_CASE_GROUP_FILE = BASE_DIRECTORY + "master/all_test_case.json"
   TEST_CASE_GROUP_NAME = "all_test_case"
   TEST_CASE_DIRECTORY = BASE_DIRECTORY + "test_case/"
   TEST_CASE_COMMON_COMMAND = BASE_DIRECTORY + "common/"
   TEST_CASE_CLEAN_UP = BASE_DIRECTORY + "clean_up/"
   IMAGES_PATH = BASE_DIRECTORY + "images/"
   OEM_CONFIGURATION_JSON = BASE_DIRECTORY + "config/oem_config.json"
   OEM_CONFIGURATION_FILE = BASE_DIRECTORY + "config/oem_config.py"
   OEM_CONFIGURATION_PACKAGE = "project_config.tata_gen3+.facets.config.oem_config"
   OEM_CONFIGURATION_CLASS = "OEMConfiguration"
   
elif EXECUTE_GROUP == "TATA_PCTS":
   BASE_DIRECTORY = "project_config/tata/pcts/"
   APPIUM_CLIENT_CONFIGURATION_FILE = BASE_DIRECTORY + "client/master_configuration.json"
   TEST_CASE_GROUP_FILE = BASE_DIRECTORY + "master/all_test_case.json"
   TEST_CASE_GROUP_NAME = "all_test_case"
   TEST_CASE_DIRECTORY = BASE_DIRECTORY + "test_case/"
   TEST_CASE_COMMON_COMMAND = BASE_DIRECTORY + "common/"
   TEST_CASE_CLEAN_UP = BASE_DIRECTORY + "clean_up/"
   IMAGES_PATH = BASE_DIRECTORY + "images/"
   OEM_CONFIGURATION_JSON = BASE_DIRECTORY + "config/oem_config.json"
   OEM_CONFIGURATION_FILE = BASE_DIRECTORY + "config/oem_config.py"
   OEM_CONFIGURATION_PACKAGE = "project_config.tata.pcts.config.oem_config"
   OEM_CONFIGURATION_CLASS = "OEMConfiguration"
   

   
#Log directory configuration
SERVER_LOG_FOLDER_PATH = "logs/appium_server_logs/"
APP_LOG_FOLDER_PATH = "logs/appium_log/"
APP_LOG_FILE_NAME = "application_log.log"
