from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
import time

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "button",
   "xpath": "//button[@id='submit']",  # XPath of the button to click
   "wait": 10,                         # Optional: Wait time for widget to load in seconds (default: 10)
   "delay_before": 4,                  # Optional: Delay before clicking in seconds (default: 4)
   "max_retry": 1,                     # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,              # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                     # Optional: Commands to execute based on click result
      "success": [                     # Commands to execute if click is successful
        # more command
      ],
      "failed": [                      # Commands to execute if click fails
        # more command
      ]
   }
}

Note: The validation section is processed by the CommandProcessor, not by this handler.
"""

class ButtonHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a button click command.
        
        Args:
            command_data (dict): The command data containing button information
            
        Returns:
            tuple: (success, message) - The result of the button click operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Validate required fields
        required_fields = ["base_path", "xpath"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error
            
        # Extract command parameters
        base_path = command_data.get("base_path")
        xpath = command_data.get("xpath")
        wait_time = command_data.get("wait", 10)  # default to 10s
        delay_before = command_data.get("delay_before", 4)  # default to 4s
        
        # Get retry parameters
        max_retry = command_data.get("max_retry", 1)  # default to 1 attempt (no retry)
        attempt_interval = command_data.get("attempt_interval", 0)  # default to 0s (no delay)
        
        # Get driver
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result
        
        # Optional delay before clicking
        if delay_before > 0:
            time.sleep(delay_before)
        
        # Define click operation function for retry utility
        def click_operation():
            return WidgetUtils.click_element(driver, xpath, "button", wait_time, tlog)
        
        # Use retry utility
        success, message = WidgetUtils.retry_operation(click_operation, max_retry, attempt_interval, tlog)
        
        if success:
            tlog.i(f"Clicked button at {xpath}")
            return True, "BUTTON_CLICKED_SUCCESSFULLY"
        else:
            return False, message
