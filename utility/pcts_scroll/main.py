"""
Android Scroll Utilities - Example Usage and Testing

This module demonstrates comprehensive usage of the scroll_utils module for Android 
list automation. It includes examples of all major scroll utility functions with 
detailed comments explaining their usage patterns.

Key Features Demonstrated:
- PCTS-specific convenience functions
- Generic scroll utilities for any Android app
- Smart element detection and interaction
- Screenshot capture and analysis
- Intelligent element visibility toggling
- Complete test case launch workflows

Usage:
    python main.py

Prerequisites:
    - Appium server running on localhost:4723
    - Android device/emulator connected
    - PCTS Verifier app installed (or modify constants for your app)
"""

from appium import webdriver
from appium.options.android import UiAutomator2Options as AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from scroll_utils import (
    pcts_scroll_to_top,
    pcts_get_visible_top_list_items,
    pcts_get_visible_sub_list_items,
    scroll_to_top,
    scroll_to_text,
    take_screenshot,
    get_xpath_and_bounds_for_text_item,
    toggle_element_visibility,
    launch_pcts_test_case
)

import time
import sys
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================================
# ANDROID DEVICE AND APP CONFIGURATION
# =========================================================================

# Appium capabilities for Android automation
PLATFORM_NAME = "Android"
PLATFORM_VERSION = "16"                        # Android API level
DEVICE_NAME = "38031FDJH00D0P"                 # Device serial number
APP_PACKAGE = "com.google.android.projection.gearhead.pctsverifier"  # Target app package
APP_ACTIVITY = ".shell.TestListActivity"       # Entry activity for the app
AUTOMATION_NAME = "UiAutomator2"               # Appium automation engine
COMMAND_EXECUTOR = "http://127.0.0.1:4723"     # Appium server endpoint

# =========================================================================
# APP-SPECIFIC UI ELEMENT RESOURCE IDS
# =========================================================================

# Main scrollable list container (update for your app)
SCROLLABLE_LIST_ID = "com.google.android.projection.gearhead.pctsverifier:id/list"
SCROLL_XPATH = f'//android.widget.ExpandableListView[@resource-id="{SCROLLABLE_LIST_ID}"]//android.widget.TextView'

# Element resource IDs for different list item types (update for your app)
SCROLLABLE_RESOURCE_LIST_ID = "com.google.android.projection.gearhead.pctsverifier:id/list"
SCROLL_XPATH = f'//android.widget.ExpandableListView[@resource-id="{SCROLLABLE_RESOURCE_LIST_ID}"]//android.widget.TextView'

TOP_LIST_RESOURCE_ID = "android:id/text1"          # Main category items
SUB_LIST_RESOURCE_ID = "com.google.android.projection.gearhead.pctsverifier:id/test_caption"  # Sub-test items

# =========================================================================
# APPIUM DRIVER SETUP AND CONFIGURATION
# =========================================================================

def start_driver():
    """
    Initialize and configure Appium WebDriver for Android automation.
    
    Returns:
        WebDriver: Configured Appium WebDriver instance
        
    Raises:
        Exception: If connection to Appium server fails
    """
    options = AppiumOptions()
    
    # Basic device and app configuration
    options.set_capability('platformName', PLATFORM_NAME)
    options.set_capability('platformVersion', PLATFORM_VERSION)
    options.set_capability('deviceName', DEVICE_NAME)
    options.set_capability('appPackage', APP_PACKAGE)
    options.set_capability('appActivity', APP_ACTIVITY)
    options.set_capability('automationName', AUTOMATION_NAME)
    
    # Session management settings
    options.set_capability('newCommandTimeout', 6000)      # Extend timeout for slow operations
    options.set_capability('noReset', True)                # Don't reinstall app
    options.set_capability('dontStopAppOnReset', True)     # Keep app running
    options.set_capability('autoLaunch', True)             # Auto-launch app

    logger.info(f"Initializing Android session for app: {APP_PACKAGE}")
    logger.info(f"Target activity: {APP_ACTIVITY}")
    logger.info(f"Connecting to Appium server at: {COMMAND_EXECUTOR}")
    
    try:
        return webdriver.Remote(command_executor=COMMAND_EXECUTOR, options=options)
    except Exception as e:
        logger.error(f"Failed to connect to Appium server: {e}")
        logger.error("Ensure Appium server is running and device is connected")
        raise

def get_driver():
    """
    Convenience wrapper to get a configured driver instance.
    
    Returns:
        WebDriver: Appium WebDriver instance
    """
    return start_driver()



# =========================================================================
# MAIN EXECUTION AND TESTING
# =========================================================================

def main():
    """
    Main test execution function demonstrating scroll utility capabilities.
    
    This function showcases all major scroll utility functions with practical examples.
    Uncomment specific sections to test different functionalities.
    """
    driver = None
    try:
        # Initialize Appium driver and connect to the app
        driver = get_driver()
        logger.info("✅ Appium session started successfully")

        # Wait for app to fully load
        time.sleep(3)
        logger.info(f"📱 Current activity: {driver.current_activity}")

        # =========================================================================
        # DEMONSTRATION OF SCROLL UTILITY FUNCTIONS
        # =========================================================================
        
        # Example 1: PCTS-specific scroll functions (high-level convenience methods)
        # Scroll to top of PCTS test list
        # if pcts_scroll_to_top(driver):
        #     logger.info("Successfully scrolled to the top of the PCTS list.")
        
        # Get visible main category items (top-level expandable sections)
        # visible_top_items = pcts_get_visible_top_list_items(driver)
        # logger.info(f"Visible top list items: {visible_top_items}")
        
        # Get visible sub-category items (expanded test cases within sections)
        # visible_sub_items = pcts_get_visible_sub_list_items(driver)
        # logger.info(f"Visible sub list items: {visible_sub_items}")
        
        # =========================================================================
        # GENERIC SCROLL UTILITY FUNCTIONS (can be used with any Android list)
        # =========================================================================
        
        # Example 2: Generic scroll to top with custom resource ID
        # if scroll_to_top(driver, SCROLLABLE_LIST_ID):
        #     logger.info("Successfully scrolled to the top of the list.")
        
        # Example 3: Find and scroll to specific text in the list
        # target_text = "AudioTests"  # Replace with any text you want to find
        # if scroll_to_text(driver, target_text):
        #     logger.info(f"Successfully scrolled to text: {target_text}")
        
        # Example 4: Take a screenshot for documentation/debugging
        # screenshot_path = take_screenshot(driver, "app_screenshot")
        # logger.info(f"Screenshot saved: {screenshot_path}")
        
        # Example 5: Get element details including XPath and bounds for interaction
        # target_text = "SpeechRecognitionTests"
        # if scroll_to_text(driver, target_text):
        #     xpath, bounds = get_xpath_and_bounds_for_text_item(driver, target_text)
        #     if xpath:
        #         logger.info(f"Found element at bounds: {bounds}")
        #         # Click the element once found
        #         driver.find_element(AppiumBy.XPATH, xpath).click()
        
        # Example 6: Smart element visibility toggling based on arrow direction
        target_text = "TouchTests"  # Main test category to expand/collapse
        # toggle_element_visibility(driver, target_text, "show")  # Expand if collapsed
        # time.sleep(2)  # Wait for UI animation
        toggle_element_visibility(driver, target_text, "hide")  # Collapse if expanded
        
        # Example 7: Complete test case launch workflow
        # This combines multiple utilities to expand a section and launch a specific test
        #main_test_case_name = "TouchTests"    # Main category to expand
        #test_case_name = "PTEP1"              # Specific test case to launch
        #launch_pcts_test_case(driver, main_test_case_name, test_case_name)
        
        logger.info("🎉 Scroll utility demonstration completed successfully")

    except Exception as e:
        logger.error(f"❌ Error during test execution: {e}")
        sys.exit(1)

    finally:
        # Clean up resources
        if driver:
            logger.info("🔚 Closing Appium session")
            driver.quit()
        else:
            logger.info("ℹ️ No driver session to close")

# Entry point
if __name__ == "__main__":
    main()
