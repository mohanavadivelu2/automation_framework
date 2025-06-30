from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
from selenium.webdriver.common.action_chains import ActionChains
import time

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "scroll",
   "xpath": "//div[@class='scrollable-content']",  # XPath for the scrollable element
   "direction": "down",                            # Scroll direction (down/up)
   "distance": 100,                                # Scroll distance in pixels
   "wait": 10,                                     # Optional: Wait time for widget to load in seconds (default: 10)
   "delay_before": 2,                              # Optional: Delay before scrolling in seconds (default: 2)
   "max_retry": 1,                                 # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,                          # Optional: Interval between attempts in seconds (default: 0 - no delay)
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

class ScrollHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a scroll command with retry support.
        
        Args:
            command_data (dict): The command data containing scroll information
            
        Returns:
            tuple: (success, message) - The result of the scroll operation
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
        wait_time = command_data.get("wait", 10)
        direction = command_data.get("direction", "down")
        distance = command_data.get("distance", 100)
        delay_before = command_data.get("delay_before", 2)
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))  # Default 0 seconds - no delay
        
        # Step 2: Get driver instance
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result
        
        # Step 3: Apply optional delay before scrolling
        if delay_before > 0:
            time.sleep(delay_before)
        
        # Step 4: Define scroll operation for retry utility
        def scroll_operation():
            # Find the scroll element
            success, result = WidgetUtils.find_element(driver, xpath, wait_time, tlog)
            if not success:
                return False, result
            element = result
            
            try:
                offset_y = distance if direction.lower() == "down" else -distance
                action = ActionChains(driver)
                action.drag_and_drop_by_offset(element, 0, offset_y).perform()
                
                tlog.i(f"Scrolled {direction} by {distance} pixels using xpath: {xpath}")
                return True, "SCROLL_SUCCESSFUL"
            except Exception as e:
                tlog.e(f"Exception while performing scroll: {e}")
                return False, str(e)
        
        # Step 5: Use retry utility to handle scroll with retries
        success, result = WidgetUtils.retry_operation(scroll_operation, max_retry, attempt_interval, tlog)
        
        # Step 6: Process and return the result
        if success:
            return True, "SCROLL_SUCCESSFUL"
        else:
            return False, f"SCROLL_FAILED_AFTER_{max_retry}_RETRIES: {result}"
