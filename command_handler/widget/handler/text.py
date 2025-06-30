from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
import time

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "text",
   "xpath": "//input[@id='username']",  # XPath of the text field
   "text": "user@example.com",          # Text to be entered in the text field
   "wait": 4,                           # Optional: Wait time for widget to load in seconds (default: 4)
   "delay_before": 4,                   # Optional: Delay before entering text in seconds (default: 4)
   "clear_first": true,                 # Optional: Whether to clear the field before entering text (default: true)
   "max_retry": 1,                      # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,               # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                      # Optional: Commands to execute based on text entry result
      "success": [                      # Commands to execute if text entry is successful
        # more command
      ],
      "failed": [                       # Commands to execute if text entry fails
         # more command
      ]
   }
}

Note: The validation section is processed by the CommandProcessor, not by this handler.
"""

class TextHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a text entry command.
        
        Args:
            command_data (dict): The command data containing text field information
            
        Returns:
            tuple: (success, message) - The result of the text entry operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Validate required fields
        required_fields = ["base_path", "xpath"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error
            
        # Step 1: Extract command parameters
        base_path = command_data.get("base_path")
        xpath = command_data.get("xpath")
        wait_time = command_data.get("wait", 4)
        input_text = command_data.get("text", "")
        delay_before = command_data.get("delay_before", 4)
        clear_first = command_data.get("clear_first", True)
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))  # Default 0 seconds - no delay
        
        # Step 2: Get driver instance
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result
        
        # Step 3: Apply optional delay before entering text
        if delay_before > 0:
            time.sleep(delay_before)
        
        # Step 4: Define text entry operation for retry utility
        def text_entry_operation():
            return WidgetUtils.enter_text(
                driver, xpath, input_text, wait_time, clear_first, tlog
            )
        
        # Step 5: Use retry utility to handle text entry with retries
        success, result = WidgetUtils.retry_operation(text_entry_operation, max_retry, attempt_interval, tlog)
        
        # Step 6: Process and return the result
        if success:
            tlog.i(f"Text '{input_text}' entered at {xpath}")
            return True, "TEXT_ENTERED_SUCCESSFULLY"
        else:
            return False, f"TEXT_ENTRY_FAILED_AFTER_{max_retry}_RETRIES: {result}"
