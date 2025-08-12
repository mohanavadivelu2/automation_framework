from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
import time
from utility.pcts_button_click_by_name import pcts_button_click
from app_manager import ApplicationManager

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "button_click_by_config",
   "check_for": "C10_SHIPPING_IN_TRUCK",    # Key to retrieve the button name from OEM configuration
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

class ButtonByConfigHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a button click by config command.
        
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
        delay_before = command_data.get("delay_before", 4)  # Default to 4s if not provided
        
        # Step 4: Get retry parameters for the click operation
        max_retry = command_data.get("max_retry", 1)  # Default to 1 attempt (no retry)
        attempt_interval = command_data.get("attempt_interval", 0)  # Default to 0s (no delay)
        
        # Step 5: Get the button name from OEM configuration
        if not hasattr(ApplicationManager.OEM_CONFIGURATION, check_for):
            tlog.e(f"Unsupported check_for value: {check_for}")
            return False, "UNSUPPORTED_CHECK_FOR_VALUE"
        
        name = getattr(ApplicationManager.OEM_CONFIGURATION, check_for)
        tlog.i(f"button_click_by_config --> Config: {check_for} value{name}")
        
        # Step 6: Get the driver for the specified application
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result
        
        # Step 7: Introduce a delay before the click, if specified
        if delay_before > 0:
            time.sleep(delay_before)
        
        # Step 8: Define the click operation to be executed
        def click_operation():
            return pcts_button_click.button_click_by_name(driver, name)
        
        # Step 9: Use the retry utility to perform the click operation
        success, message = WidgetUtils.retry_operation(click_operation, max_retry, attempt_interval, tlog)
        
        # Step 10: Log the result and return the status
        if success:
            tlog.i(f"Clicked button with name {name} from config key {check_for}")
            return True, "BUTTON_CLICKED_SUCCESSFULLY"
        else:
            return False, message
