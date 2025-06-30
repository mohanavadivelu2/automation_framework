from appium import webdriver
from appium.options.ios import XCUITestOptions
from .platform_session_handler import PlatformSessionHandler

class IOSSessionHandler(PlatformSessionHandler):

    def validate_config(self, logger, config):
        logger.d("Validating iOS config...")
        required_keys = ['platform_version', 'udid', 'bundle_id', 'automation_name']
        for key in required_keys:
            if key not in config:
                logger.e(f"Missing required iOS config key: {key}")
                return False
        return True

    def validate_environment(self, logger, config):
        logger.d("Validating iOS environment...")
        return True

    def setup_session(self, logger, config, base_path, command_executor):
        logger.d(f"Starting iOS session setup for base_path: {base_path}")
        try:
            options = XCUITestOptions()

            # ✅ Use set_capability instead of non-existent methods
            options.set_capability("platformVersion", config.get("platform_version"))
            options.set_capability("deviceName", config.get("device_name", "iPhone"))
            options.set_capability("udid", config.get("udid"))
            options.set_capability("bundleId", config.get("bundle_id"))
            options.set_capability("automationName", config.get("automation_name", "XCUITest"))
            options.set_capability("showXcodeLog", config.get("showXcodeLog", True))
            options.set_capability("noReset", config.get("noReset", True))
            options.set_capability("newCommandTimeout", 300)
            options.set_capability("wdaLocalPort", config.get( "wdaLocalPort"))
            options.set_capability("usePrebuiltWDA", False)  
            options.set_capability("useNewWDA", True)  

            logger.d(f"Desired Capabilities (via Options): {options.to_capabilities()}")
            logger.d(f"Connecting to Appium Server at: {command_executor}")
            driver = webdriver.Remote(command_executor, options=options)
            logger.d("iOS session successfully created")
            return driver

        except Exception as e:
            logger.e(f"Failed to create iOS session: {str(e)}")
            return None
