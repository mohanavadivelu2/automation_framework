from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
import time
from utility.click_by_text_name import click_by_text

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "click_by_text",
   "check_for": "string to match",       # String needs to be matched with the content of page
   "exact_match" : True or false,
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

class ClickByTextHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a click by text command.
        
        Args:
            command_data (dict): The command data containing text information
            
        Returns:
            tuple: (success, message) - The result of the click operation
        """
        # Step 1: Get the test case logger instance
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Step 2: Validate that all required fields are present in the command
        required_fields = ["base_path", "check_for", "exact_match"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error
            
        # Step 3: Extract parameters from the command data
        base_path = command_data.get("base_path")
        target_text = command_data.get("check_for")
        exact_match = command_data.get("exact_match")
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
            # The utility function returns a tuple (success, message), but we only need the success status for retry_operation
            success, _ = click_by_text.click_by_text(driver, target_text, exact_match)
            return success, _
        
        # Step 8: Use the retry utility to perform the click operation
        success, message = WidgetUtils.retry_operation(click_operation, max_retry, attempt_interval, tlog)
        
        # Step 9: Log the result and return the status
        if success:
            tlog.i(f"Clicked element with text '{target_text}'")
            return True, "CLICK_BY_TEXT_SUCCESSFUL"
        else:
            return False, message
