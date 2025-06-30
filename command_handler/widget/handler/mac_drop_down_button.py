from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
import time

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "mac_popup_button",
   "select_capture": "//XCUIElementTypePopUpButton[@label='Select Capture']",  # XPath for popup/drop down button
   "select_item": "//XCUIElementTypeMenuItem[@title='Wired CarPlay']",         # XPath for popup/drop down item
   "wait": 4,                                                                  # Optional: Wait time for widget to load in seconds (default: 4)
   "delay_before": 4,                                                         # Optional: Delay between clicks in seconds (default: 2)
   "max_retry": 1,                                                             # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,                                                      # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                                                             # Optional: Commands to execute based on scroll result
      "success": [                                                             # Commands to execute if text entry is successful
          # more command
      ],
      "failed": [                                                              # Commands to execute if text entry fails
        # more command
      ]
   }
}

Note: The validation section is processed by the CommandProcessor, not by this handler.
"""

class MacDropDownButtonHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a Mac dropdown/popup button command.
        
        Args:
            command_data (dict): The command data containing dropdown information
            
        Returns:
            tuple: (success, message) - The result of the dropdown operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Validate required fields
        required_fields = ["base_path", "select_capture", "select_item"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error
            
        # Step 1: Extract command parameters
        base_path = command_data.get("base_path")
        select_capture = command_data.get("select_capture")
        select_item = command_data.get("select_item")
        wait_time = command_data.get("wait", 4)
        delay_before = command_data.get("delay_before", 2)
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))  # Default 0 seconds - no delay
        
        # Step 2: Get driver instance
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result

        # Step 3: Apply delay before clicks
        if delay_before > 0:
            time.sleep(delay_before)


        # Step 4: Define popup button click operation for retry utility
        def popup_button_click_operation():
            return WidgetUtils.click_element(driver, select_capture, "popup button", wait_time, tlog)

        # Step 5: Use retry utility to handle popup button click with retries
        tlog.i("Popup menu - Step 1: Click popup button")
        popup_success, popup_result = WidgetUtils.retry_operation(popup_button_click_operation, max_retry, attempt_interval, tlog)
        if not popup_success:
            return False, f"POPUP_SELECTION_FAILED_AFTER_{max_retry}_RETRIES: {popup_result}"

        # Step 6: Apply delay before clicks
        if delay_before > 0:
            time.sleep(delay_before)

        # Step 7: Define menu item click operation for retry utility
        def menu_item_click_operation():
            return WidgetUtils.click_element(driver, select_item, "menu item", wait_time, tlog)

        # Step 8: Use retry utility to handle menu item click with retries
        tlog.i("Popup menu - Step 2: Click menu item")
        menu_success, menu_result = WidgetUtils.retry_operation(menu_item_click_operation, max_retry, attempt_interval, tlog)
        if not menu_success:
            return False, f"POPUP_SELECTION_FAILED_AFTER_{max_retry}_RETRIES: {menu_result}"

        # Step 9: Return success result
        tlog.i("Popup menu selection completed successfully.")
        return True, "POPUP_SELECTION_SUCCESS"
