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
   "check_for": "DRIVER_SIDE_LEFT",           # Configuration option to check (any valid OEM_CONFIGURATION field)
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

def is_yes_value(value):
    """
    Check if value represents a 'yes' state.
    
    Args:
        value: The value to check (can be string, boolean, int, tuple, list, etc.)
        
    Returns:
        bool: True if value represents a 'yes' state, False otherwise
    """
    print(f"DEBUG is_yes_value: Original value = {value}, type = {type(value)}")
    
    if value is None:
        print("DEBUG is_yes_value: Value is None, returning False")
        return False
    
    # Handle tuple/list values by extracting the first element
    if isinstance(value, (tuple, list)):
        print(f"DEBUG is_yes_value: Value is tuple/list with length {len(value)}")
        if len(value) == 0:
            print("DEBUG is_yes_value: Empty tuple/list, returning False")
            return False
        original_value = value
        value = value[0]
        print(f"DEBUG is_yes_value: Extracted first element: {original_value} -> {value}")
    
    final_string = str(value).upper()
    result = final_string in ["YES", "TRUE", "ON", "ENABLED", "1", "Y"]
    print(f"DEBUG is_yes_value: Final string = '{final_string}', result = {result}")
    
    return result


def get_target_xpath(check_for: str, yes_xpath: str, no_xpath: str) -> tuple[bool, str]:
    """
    Determine the correct XPath based on a flag in ApplicationManager.OEM_CONFIGURATION.

    Args:
        check_for (str): The name of the configuration field to check (e.g., "DRIVER_SIDE_LEFT").
        yes_xpath (str): XPath if the field value is "YES".
        no_xpath (str): XPath if the field value is not "YES".

    Returns:
        tuple: (True, target_xpath) if check_for is valid, else (False, error_message)
    """
    from app_manager import ApplicationManager  # Optional: for clarity / avoid circular imports
    
    tlog = LogManager.get_instance().get_test_case_logger()
    
    tlog.d(f"Checking for xpath yes: [{yes_xpath}] xpath no: [{no_xpath}] based on check_for [{check_for}]")
    
    if not hasattr(ApplicationManager.OEM_CONFIGURATION, check_for):
        tlog.e(f"Unsupported check_for value: {check_for}")
        return False, "UNSUPPORTED_CHECK_FOR_VALUE"
    
    value = getattr(ApplicationManager.OEM_CONFIGURATION, check_for)
    target_xpath = yes_xpath if is_yes_value(value) else no_xpath
    tlog.d(f"Checking for [{check_for}] value [{value}] is_yes_value: [{is_yes_value(value)}] xpath [{target_xpath}]")
    return True, target_xpath


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
        success, result = get_target_xpath(check_for=check_for, yes_xpath=yes_xpath,no_xpath=no_xpath)
        if success:
            target_xpath = result
        else:
            return False, result
        
        # Step 4: Apply optional delay before clicking
        if delay_before > 0:
            time.sleep(delay_before)
        
        # Step 5: Define radio button click operation for retry utility
        def radio_button_click_operation():
            try:
                # Use the correct API for Selenium/Appium 4+
                element = driver.find_element("xpath", target_xpath)
                # Adjust the attribute and value as per your app's radio button implementation
                is_selected = element.get_attribute("value") == "1"
                if is_selected:
                    tlog.d("Radio button already selected, skipping click.")
                    return True, "RADIO_BUTTON_ALREADY_SELECTED"
            except Exception as e:
                tlog.e(f"Exception during pre-check: {str(e)}")
                # Optionally, continue to click attempt or return failure

            # If not selected, proceed to click as usual
            # (your existing click logic here)
            try:
                element = driver.find_element_by_xpath(target_xpath)
                is_selected = element.get_attribute("value") == "1"  # or use the correct attribute for your UI

                if is_selected:
                    tlog.d("Radio button already selected, skipping click.")
                    return True, "RADIO_BUTTON_ALREADY_SELECTED"
                else:
                    # proceed to click as usual
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
