from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
from app_manager import ApplicationManager
import time
import traceback

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "radio_button",
   "check_for": "DRIVER_SIDE_LEFT",           # Configuration option to check (currently only DRIVER_SIDE_LEFT supported)
   "yes_xpath": "//input[@id='left-side']",   # XPath to be clicked when option is YES
   "no_xpath": "//input[@id='right-side']",   # XPath to be clicked when option is NO
   "wait": 4,                                 # Optional: Wait time for widget to load in seconds (default: 4)
   "delay_before": 0,                         # Optional: Delay before clicking in seconds (default: 0)
   "max_retry": 1,                            # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,                     # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                                 # Optional: Commands to execute based on scroll result
      "success": [                                 # Commands to execute if text entry is successful
          # more command
      ],
      "failed": [                                  # Commands to execute if text entry fails
        # more command
      ]
    }
}
"""

class RadioButtonHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a radio button selection command with retry support.
        
        Args:
            command_data (dict): The command data containing radio button information
            
        Returns:
            tuple: (success, message) - The result of the radio button selection operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Validate required fields
        required_fields = ["base_path", "yes_xpath", "no_xpath"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error
            
        # Step 1: Extract command parameters
        base_path = command_data.get("base_path")
        check_for = command_data.get("check_for")
        yes_xpath = command_data.get("yes_xpath")
        no_xpath = command_data.get("no_xpath")
        wait_time = command_data.get("wait", 4)
        delay_before = command_data.get("delay_before", 0)
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))  # Default 0 seconds - no delay
        target_xpath = ""
        
        # Step 2: Get driver instance
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result
        
        # Step 3: Determine which xpath to use based on configuration
        if check_for == "DRIVER_SIDE_LEFT":
            if ApplicationManager.OEM_CONFIGURATION.DRIVER_SIDE_LEFT == "YES":
                target_xpath = yes_xpath
            else:
                target_xpath = no_xpath
            tlog.d(f"Checking for [DRIVER_SIDE_LEFT] value [{ApplicationManager.OEM_CONFIGURATION.DRIVER_SIDE_LEFT}] xpath [{target_xpath}]")
        else:
            tlog.e(f"Unsupported check_for value: {check_for}")
            return False, "UNSUPPORTED_CHECK_FOR_VALUE"
        
        # Step 4: Apply optional delay before clicking
        if delay_before > 0:
            time.sleep(delay_before)
        
        # Step 5: Define radio button click operation for retry utility
        def radio_button_click_operation():
            try:
                return WidgetUtils.click_element(driver, target_xpath, "radio button", wait_time, tlog)
            except Exception as e:
                tlog.e(f"Exception during radio button click: {str(e)}")
                tlog.e(traceback.format_exc())
                return False, str(e)
        
        # Step 6: Use retry utility to handle radio button click with retries
        success, result = WidgetUtils.retry_operation(radio_button_click_operation, max_retry, attempt_interval, tlog)
        
        # Step 7: Process and return the result
        if success:
            return True, "RADIO_BUTTON_SELECTED"
        else:
            return False, f"RADIO_BUTTON_CLICK_FAILED_AFTER_{max_retry}_RETRIES: {result}"
