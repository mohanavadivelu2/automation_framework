import os
from logger import LogManager
from ..widget_utils import WidgetUtils
from command_handler.widget.handler.base import BaseHandler
from global_config.project_configuration import IMAGES_PATH
from command_handler.widget.image_utility.image_processor import detect_single_template

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "single_template",
   "template_name": "button.png",    # Template to search for
   "ref_img_name": "reference.png",  # Optional: Name for the captured reference image (default: reference.png)
   "output_name": "result.png",      # Optional: Name for the output image with detection results (default: result.png)
   "threshold": 0.7,                 # Optional: Minimum score to consider a match (0.0-1.0)
   "label": "Button",                # Optional: Label for the template
   "expect_match": true,             # Optional: Whether to expect a match or not
   "max_retry": 1,                   # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,            # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                   # Optional: Commands to execute based on detection result
      "success": [                   # Commands to execute if detection result matches expectation
        # more command
      ],
      "failed": [                    # Commands to execute if detection result doesn't match expectation
        # more command
      ]
   }
}

Note: The validation section is processed by the CommandProcessor, not by this handler.
"""

class SingleTemplateHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a single template detection command.
        
        Args:
            command_data (dict): The command data containing template information
            
        Returns:
            tuple: (success, message) - The result of the template detection operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Validate required fields
        required_fields = ["base_path", "template_name"]
        success, error_msg = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error_msg
        
        # Get paths from configuration
        base_path = command_data.get("base_path")
        ref_img_name = command_data.get("ref_img_name", "reference.png")
        template_name = command_data.get("template_name")
        output_name = command_data.get("output_name", "result.png")
        threshold = command_data.get("threshold", 0.7)
        label = command_data.get("label")
        expect_match = command_data.get("expect_match")
        max_retry = command_data.get("max_retry", 1)  # default to 1 attempt (no retry)
        attempt_interval = command_data.get("attempt_interval", 0)  # default to 0s (no delay)
        
        # Get driver
        success, driver_or_msg = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, driver_or_msg
        driver = driver_or_msg
        
        # Construct full paths
        folder_path = LogManager.get_instance().get_log_dir()
        ref_img_path = os.path.join(folder_path, ref_img_name)
        template_path = os.path.join(IMAGES_PATH, template_name)
        output_path = os.path.join(folder_path, output_name)

        try:
            import time
            time.sleep(25)  # Wait for UI to stabilize
            
            # Define template detection operation for retry utility
            def detect_template_operation():
                nonlocal ref_img_path, template_path, output_path, threshold, label, expect_match
                
                screenshot = driver.get_screenshot_as_png()
                with open(ref_img_path, 'wb') as f:
                    f.write(screenshot)

                tlog.d(f"Reference screenshot saved to {ref_img_path}")
                tlog.d(f"Template: {template_path}")

                result, is_detected, match_info = detect_single_template(
                    ref_img_path,
                    template_path,
                    output_path,
                    threshold,
                    label
                )

                tlog.d(f"Template detection result: {result}")
                tlog.d(f"Match score: {match_info['score']:.2f}" if match_info else "No match info")

                if expect_match is not None:
                    tlog.d(f"Expected match: {expect_match}, Detected: {is_detected}")
                    expectation_met = (expect_match == is_detected)

                    if expectation_met:
                        tlog.d("Detection result matches expectation")
                        return True, result
                    else:
                        tlog.d("Detection result does not match expectation")

                        # Fail early if expect_match=False and template is detected
                        if not expect_match and is_detected:
                            expected_str = "no match"
                            detected_str = "match"
                            return False, f"EXPECTATION_MISMATCH: Expected {expected_str}, Got {detected_str}"
                else:
                    if is_detected:
                        tlog.d("Template detected (no expectation specified)")
                        return True, result
                
                # If we get here, detection failed or didn't meet expectations
                if expect_match is not None:
                    expected_str = "match" if expect_match else "no match"
                    detected_str = "match" if is_detected else "no match"
                    return False, f"EXPECTATION_MISMATCH: Expected {expected_str}, Got {detected_str}"
                
                return is_detected, result
            
            # Use retry utility
            return WidgetUtils.retry_operation(detect_template_operation, max_retry, attempt_interval, tlog)

        except Exception as e:
            tlog.e(f"Failed to detect template: {e}")
            return False, f"TEMPLATE_DETECTION_FAILED: {str(e)}"
