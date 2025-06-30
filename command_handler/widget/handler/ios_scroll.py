from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
import time

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "ios_scroll",
   "direction": "down",                # Optional: Scroll direction (down/up) (default: down)
   "duration": 0.5,                    # Optional: Duration of the scroll gesture in seconds (default: 0.5)
   "delay_before": 1,                  # Optional: Delay before scrolling in seconds (default: 1)
   "max_retry": 1,                     # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,              # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                   # Optional: Commands to execute based on scroll result
      "success": [                   # Commands to execute if text entry is successful
          # more command
      ],
      "failed": [                    # Commands to execute if text entry fails
        # more command
      ]
   }
}

Note: The validation section is processed by the CommandProcessor, not by this handler.
"""

class ScrollIosHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process an iOS scroll command with retry support.
        
        Args:
            command_data (dict): The command data containing scroll information
            
        Returns:
            tuple: (success, message) - The result of the scroll operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Step 1: Validate required fields
        required_fields = ["base_path"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error

        # Step 2: Extract command parameters
        base_path = command_data.get("base_path")
        direction = command_data.get("direction", "down").lower()
        duration = float(command_data.get("duration", 0.5))
        delay_before = float(command_data.get("delay_before", 1))
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))  # Default 0 seconds - no delay

        # Step 3: Get driver instance
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result

        # Step 4: Apply optional delay before scrolling
        if delay_before > 0:
            time.sleep(delay_before)

        # Step 5: Calculate dynamic scroll distance based on screen size
        window_size = driver.get_window_size()
        width = window_size["width"]
        height = window_size["height"]
        start_x = width // 2
        start_y = int(height * 0.3)
        end_y = int(height * 0.7)

        if direction == "up":
            start_y, end_y = end_y, start_y

        # Step 6: Define scroll operation for retry utility
        def scroll_operation():
            try:
                tlog.i(f"Swiping {direction} from ({start_x}, {start_y}) to ({start_x}, {end_y})")
                driver.execute_script("mobile: dragFromToForDuration", {
                    "duration": duration,
                    "fromX": start_x,
                    "fromY": start_y,
                    "toX": start_x,
                    "toY": end_y
                })
                time.sleep(2)  # Wait for scroll to complete and content to settle
                return True, "SCROLL_SUCCESS"
            except Exception as e:
                tlog.e(f"Swipe failed: {str(e)}")
                return False, str(e)

        # Step 7: Use retry utility to handle scroll with retries
        success, result = WidgetUtils.retry_operation(scroll_operation, max_retry, attempt_interval, tlog)

        # Step 8: Process and return the result
        if success:
            return True, "SCROLL_SUCCESS"
        else:
            return False, f"SCROLL_FAILED_AFTER_{max_retry}_RETRIES: {result}"
