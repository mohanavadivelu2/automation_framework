from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
import time
from utility.pcts_button_click_by_name import pcts_button_click

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "button_click_by_match",
   "check_for": "string to match",       # String needs to be matched with the content of page
   "success" : "YES"                     # button name to click if found
   "failure": "NO",                      # button name to click if not found
   "delay_before": 4,                    # Optional: Delay before clicking in seconds (default: 4)
   "max_retry": 1,                       # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,                # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                       # Optional: Commands to execute based on click result
      "success": [                       # Commands to execute if click is successful
        # more command
      ],
      "failed": [                        # Commands to execute if click fails
        # more command
      ]
   }
}
"""

class ButtonByMatchHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a button click by match command.
        
        Args:
            command_data (dict): The command data containing button information
            
        Returns:
            tuple: (success, message) - The result of the button click operation
        """
        # Step 1: Get the test case logger instance
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Step 2: Validate that all required fields are present in the command
        required_fields = ["base_path", "check_for"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error
            
        # Step 3: Extract parameters from the command data
        base_path = command_data.get("base_path")
        check_for = command_data.get("check_for")
        text_to_click_success = command_data.get("success","YES")
        text_to_click_failure = command_data.get("check_for", "NO")
        delay_before = command_data.get("delay_before", 4)  # Default to 4s if not provided
        
        # Step 4: Get retry parameters for the click operation
        max_retry = command_data.get("max_retry", 1)  # Default to 1 attempt (no retry)
        attempt_interval = command_data.get("attempt_interval", 0)  # Default to 0s (no delay)
        
        # Step 5: Get the driver for the specified application
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result
        
        # Step 6: Introduce a delay before the click, if specified
        if delay_before > 0:
            time.sleep(delay_before)
        
        # Step 7: Define the click operation to be executed
        def click_operation():
            return pcts_button_click.button_click_by_match(driver, check_for,text_to_click_success,text_to_click_failure)
        
        # Step 8: Use the retry utility to perform the click operation
        success, message = WidgetUtils.retry_operation(click_operation, max_retry, attempt_interval, tlog)
        
        # Step 9: Log the result and return the status
        if success:
            tlog.i(f"Clicked button with match {check_for}")
            return True, "BUTTON_CLICKED_SUCCESSFULLY"
        else:
            return False, message
