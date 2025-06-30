import os
from logger import LogManager
from ..widget_utils import WidgetUtils
from command_handler.widget.handler.base import BaseHandler
import time

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "page_source",
   "file_name": "page_source.html",  # Optional: Custom filename for the page source (default: page_source.html)
   "delay_before": 2,                # Optional: Delay before capturing page source in seconds (default: 2)
   "max_retry": 1,                   # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,            # Optional: Interval between attempts in seconds (default: 0 - no delay)
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

class PageSourceHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a page source capture command.

        Args:
            command_data (dict): The command data containing page source information
            
        Returns:
            tuple: (success, message) - The result of the page source capture operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Step 1: Extract command parameters
        base_path = command_data.get("base_path")
        file_name = command_data.get("file_name") or "page_source.html"
        delay_before = command_data.get("delay_before", 2)  # Default 2 seconds delay
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))  # Default 0 seconds - no delay
        folder_path = LogManager.get_instance().get_log_dir()

        # Step 2: Validate required field
        if not base_path:
            return False, "MISSING_BASE_PATH"

        # Step 3: Get driver instance
        success, driver_or_msg = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, driver_or_msg
        driver = driver_or_msg

        # Step 4: Apply optional delay before capturing page source
        if delay_before > 0:
            time.sleep(delay_before)

        # Step 5: Define page source capture operation for retry utility
        def page_source_operation():
            try:
                # Get page source
                page_source = driver.page_source
                
                # Save to file
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)

                tlog.d(f"Page source saved to {file_path}")
                return True, file_path
            except Exception as e:
                tlog.e(f"Failed to capture page source: {e}")
                return False, f"PAGE_SOURCE_FAILED: {str(e)}"

        # Step 6: Use retry utility to handle page source capture with retries
        success, result = WidgetUtils.retry_operation(page_source_operation, max_retry, attempt_interval, tlog)

        # Step 7: Process and return the result
        if success:
            return True, result  # result contains the file path
        else:
            return False, f"PAGE_SOURCE_FAILED_AFTER_{max_retry}_RETRIES: {result}"
