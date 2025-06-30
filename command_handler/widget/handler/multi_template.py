import os
from logger import LogManager
from ..widget_utils import WidgetUtils
from command_handler.widget.handler.base import BaseHandler
from global_config.project_configuration import IMAGES_PATH
from command_handler.widget.image_utility.image_processor import detect_multi_template

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "multi_template",
   "image_one": "state_on.png",
   "image_two": "state_off.png",
   "image_three": "state_disabled.png",
   "ref_img_name": "reference.png",  # Optional: Name for the reference screenshot (default: reference.png)
   "output_name": "result.png",      # Optional: Name for the output image (default: result.png)
   "threshold": 0.7,                # Optional: Matching threshold score (default: 0.70)
   "delay_before": 4,                # Optional: Delay before capturing screenshot in seconds (default: 4)
   "max_retry": 1,                   # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,            # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "valid_match": {
      "image_one": [
          # more command
      ],
      "image_two": [
         # more command
      ],
      "image_three": [
        # more command
      ]
   }
}

Note: Validation is handled elsewhere.
"""

class MultiTemplateHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a multi-template detection command with retry support.
        
        Args:
            command_data (dict): The command data containing template matching information
            
        Returns:
            tuple: (success, message) - The result of the template detection operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Step 1: Validate required fields
        required_fields = ["base_path"]
        success, error_msg = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error_msg
        
        # Step 2: Extract command parameters
        base_path = command_data.get("base_path")
        ref_img_name = command_data.get("ref_img_name", "reference.png")
        output_name = command_data.get("output_name", "result.png")
        threshold = command_data.get("threshold", 0.7)
        delay_before = command_data.get("delay_before", 4)  # Default 4 seconds delay
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))  # Default 0 seconds - no delay

        # Step 3: Extract image paths
        template_paths_dict = {}
        for key, value in command_data.items():
            if key.startswith("image_") and isinstance(value, str):
                template_paths_dict[key] = os.path.join(IMAGES_PATH, value)
        
        if not template_paths_dict:
            return False, "ERROR: No template images provided. At least one image_* parameter is required."
        
        # Step 4: Get driver instance
        success, driver_or_msg = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, driver_or_msg
        driver = driver_or_msg
        
        # Step 5: Prepare file paths
        folder_path = LogManager.get_instance().get_log_dir()
        ref_img_path = os.path.join(folder_path, ref_img_name)
        output_path = os.path.join(folder_path, output_name)

        # Step 6: Define template detection operation for retry utility
        def template_detection_operation():
            try:
                import time
                import re

                # Apply optional delay before capturing screenshot
                if delay_before > 0:
                    time.sleep(delay_before)  # Wait for UI to stabilize
                    
                screenshot = driver.get_screenshot_as_png()
                with open(ref_img_path, 'wb') as f:
                    f.write(screenshot)
                
                tlog.d(f"Reference screenshot saved to {ref_img_path}")
                for label, path in template_paths_dict.items():
                    tlog.d(f"{label}: {path}")
                
                # Call detect_multi_template with 3 args (as required)
                result, detected_state = detect_multi_template(
                    ref_img_path,
                    template_paths_dict,
                    output_path
                )
                
                tlog.d(f"Template detection result (score): {result}")

                # Parse score from result string
                match = re.search(r'Score:\s*([0-9.]+)', result)
                if match:
                    score = float(match.group(1))
                else:
                    score = 0.0
                
                if score >= threshold:
                    return True, detected_state
                else:
                    return False, "No matching template found with required threshold"
            except Exception as e:
                tlog.e(f"Failed to detect template: {e}")
                return False, f"TEMPLATE_DETECTION_FAILED: {str(e)}"

        # Step 7: Use retry utility to handle template detection with retries
        success, result = WidgetUtils.retry_operation(template_detection_operation, max_retry, attempt_interval, tlog)

        # Step 8: Process and return the result
        if success:
            return True, result
        else:
            return False, f"TEMPLATE_DETECTION_FAILED_AFTER_{max_retry}_RETRIES: {result}"
