
#Project configuration
ENABLE_VIDEO_ENABLED = "NO"
TEST_CASE_LOGGING_ENABLED = True
EXECUTE_GROUP = "FACETS" #"FACETS" / "SANITY"

if EXECUTE_GROUP == "FACETS":
   # Json directory configuration for FACETS
   BASE_DIRECTORY = "project_config/tata/facets/"
   APPIUM_CLIENT_CONFIGURATION_FILE = BASE_DIRECTORY + "client/mac_client_configuration.json" 
   TEST_CASE_GROUP_FILE = BASE_DIRECTORY + "master/all_test_case.json"
   TEST_CASE_GROUP_NAME = "all_test_case"
   TEST_CASE_DIRECTORY = BASE_DIRECTORY + "test_case/"
   TEST_CASE_COMMON_COMMAND = BASE_DIRECTORY+"common/"
   IMAGES_PATH = BASE_DIRECTORY + "images/"
   OEM_CONFIGURATION_JSON = BASE_DIRECTORY + "config/oem_config.json"
   OEM_CONFIGURATION_FILE = BASE_DIRECTORY + "config/oem_config.py"
   OEM_CONFIGURATION_PACKAGE = "project_config.tata.facets.config.oem_config"
   OEM_CONFIGURATION_CLASS = "OEMConfiguration"

elif EXECUTE_GROUP == "SANITY":
    # Json directory configuration for Sanity
   BASE_DIRECTORY = "project_config/tata/sanity/"
   APPIUM_CLIENT_CONFIGURATION_FILE = BASE_DIRECTORY + "client/android_client_configuration.json"
   TEST_CASE_GROUP_FILE = BASE_DIRECTORY + "master/all_test_case.json"
   TEST_CASE_GROUP_NAME = "all_test_case"
   TEST_CASE_DIRECTORY = BASE_DIRECTORY + "test_case/"
   TEST_CASE_COMMON_COMMAND = BASE_DIRECTORY + "common/"
   IMAGES_PATH = BASE_DIRECTORY + "images/"
   OEM_CONFIGURATION_JSON = BASE_DIRECTORY + "config/oem_config.json"
   OEM_CONFIGURATION_FILE = BASE_DIRECTORY + "config/oem_config.py"
   OEM_CONFIGURATION_PACKAGE = "project_config.tata.sanity.config.oem_config"
   OEM_CONFIGURATION_CLASS = "OEMConfiguration"
   
elif EXECUTE_GROUP == "FCA_SANITY":
   # Json directory configuration for Sanity
   BASE_DIRECTORY = "project_config/fca/sanity/"
   APPIUM_CLIENT_CONFIGURATION_FILE = BASE_DIRECTORY + "client/android_client_configuration.json"
   TEST_CASE_GROUP_FILE = BASE_DIRECTORY + "master/all_test_case.json"
   TEST_CASE_GROUP_NAME = "all_test_case"
   TEST_CASE_DIRECTORY = BASE_DIRECTORY + "test_case/"
   TEST_CASE_COMMON_COMMAND = BASE_DIRECTORY + "common/"
   IMAGES_PATH = BASE_DIRECTORY + "images/"
   OEM_CONFIGURATION_JSON = BASE_DIRECTORY + "config/oem_config.json"
   OEM_CONFIGURATION_FILE = BASE_DIRECTORY + "config/oem_config.py"
   OEM_CONFIGURATION_PACKAGE = "project_config.tata.sanity.config.oem_config"
   OEM_CONFIGURATION_CLASS = "OEMConfiguration"
   
elif EXECUTE_GROUP == "SUBARU_SANITY":
   # Json directory configuration for Sanity
   BASE_DIRECTORY = "project_config/subaru/sanity/"
   APPIUM_CLIENT_CONFIGURATION_FILE = BASE_DIRECTORY + "client/android_client_configuration.json"
   TEST_CASE_GROUP_FILE = BASE_DIRECTORY + "master/all_test_case.json"
   TEST_CASE_GROUP_NAME = "all_test_case"
   TEST_CASE_DIRECTORY = BASE_DIRECTORY + "test_case/"
   TEST_CASE_COMMON_COMMAND = BASE_DIRECTORY + "common/"
   IMAGES_PATH = BASE_DIRECTORY + "images/"
   OEM_CONFIGURATION_JSON = BASE_DIRECTORY + "config/oem_config.json"
   OEM_CONFIGURATION_FILE = BASE_DIRECTORY + "config/oem_config.py"
   OEM_CONFIGURATION_PACKAGE = "project_config.tata.sanity.config.oem_config"
   OEM_CONFIGURATION_CLASS = "OEMConfiguration"
   
elif EXECUTE_GROUP == "DEMO":
   # Json directory configuration for Sanity
   BASE_DIRECTORY = "project_config/demo/sanity/"
   APPIUM_CLIENT_CONFIGURATION_FILE = BASE_DIRECTORY + "client/android_client_configuration.json"
   TEST_CASE_GROUP_FILE = BASE_DIRECTORY + "master/all_test_case.json"
   TEST_CASE_GROUP_NAME = "all_test_case"
   TEST_CASE_DIRECTORY = BASE_DIRECTORY + "test_case/"
   TEST_CASE_COMMON_COMMAND = BASE_DIRECTORY + "common/"
   IMAGES_PATH = BASE_DIRECTORY + "images/"
   OEM_CONFIGURATION_JSON = BASE_DIRECTORY + "config/oem_config.json"
   OEM_CONFIGURATION_FILE = BASE_DIRECTORY + "config/oem_config.py"
   OEM_CONFIGURATION_PACKAGE = "project_config.tata.sanity.config.oem_config"
   OEM_CONFIGURATION_CLASS = "OEMConfiguration"

elif EXECUTE_GROUP == "TATA_GEN3+":
   # Json directory configuration for Sanity
   BASE_DIRECTORY = "project_config/demo/tata_ge3+/"
   APPIUM_CLIENT_CONFIGURATION_FILE = BASE_DIRECTORY + "client/android_client_configuration.json"
   TEST_CASE_GROUP_FILE = BASE_DIRECTORY + "master/all_test_case.json"
   TEST_CASE_GROUP_NAME = "all_test_case"
   TEST_CASE_DIRECTORY = BASE_DIRECTORY + "test_case/"
   TEST_CASE_COMMON_COMMAND = BASE_DIRECTORY + "common/"
   IMAGES_PATH = BASE_DIRECTORY + "images/"
   OEM_CONFIGURATION_JSON = BASE_DIRECTORY + "config/oem_config.json"
   OEM_CONFIGURATION_FILE = BASE_DIRECTORY + "config/oem_config.py"
   OEM_CONFIGURATION_PACKAGE = "project_config.tata.sanity.config.oem_config"
   OEM_CONFIGURATION_CLASS = "OEMConfiguration"
   

   
#Log directory configuration
SERVER_LOG_FOLDER_PATH = "logs/appium_server_logs/"
APP_LOG_FOLDER_PATH = "logs/appium_log/"
APP_LOG_FILE_NAME = "application_log.log"

