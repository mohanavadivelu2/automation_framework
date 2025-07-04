import os
import time
import cv2
import pyautogui

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from global_config.project_configuration import IMAGES_PATH

from logger import LogManager
from ..widget_utils import WidgetUtils
from .base import BaseHandler

DEFAULT_IMAGE_LOG = "image_log"
DEFAULT_REF_IMAGE_NAME = "reference.png"

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "image_click",
   "template_name": "button.png",    # Template image to find and click
   "platform_type": "ios",           # Platform type: ios, android, mac, windows
   "threshold": 0.7,                 # Optional: Matching threshold score (default: 0.8)
   "delay_before": 1,                # Optional: Delay before clicking in seconds (default: 1)
   "ref_img_name": "reference.png",  # Optional: Name for the reference screenshot (default: reference.png)
   "max_retry": 1,                   # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,            # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                   # Optional: Commands to execute based on click result
      "success": [                   # Commands to execute if click is successful
        # more command
      ],
      "failed": [                    # Commands to execute if click fails
        # more command
      ]
   }
}

Note: The validation section is processed by the CommandProcessor, not by this handler.
"""

class ImageClickHandler(BaseHandler):
    def take_screen_shot(self, driver, folder_path=DEFAULT_IMAGE_LOG, file_name=DEFAULT_REF_IMAGE_NAME):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        screenshot = driver.get_screenshot_as_png()
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(screenshot)
        return file_path

    def mark_click_point(self, image_path, x, y, output_path=None):
        img = cv2.imread(image_path)
        if img is None:
            return False, "Image to mark not found"

        # Draw red circle + crosshair
        cv2.circle(img, (x, y), 20, (0, 0, 255), 4)
        cv2.line(img, (x-15, y), (x+15, y), (0, 0, 255), 2)
        cv2.line(img, (x, y-15), (x, y+15), (0, 0, 255), 2)

        output_path = output_path or image_path.replace(".png", "_marked.png")
        cv2.imwrite(output_path, img)
        return True, output_path

    def tap_on_device(self, driver, x, y, platform_type="ios"):
        """
        Modern way to tap on iOS device using Appium v2.
        """
        try:
            if platform_type == "android":
                driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
            else:
                driver.execute_script("mobile: tap", {"x": x, "y": y})

        except Exception as e:
            raise RuntimeError(f"Tap failed using mobile: tap script: {e}")

    def processCommand(self, command_data: dict):
        """
        Process an image click command with retry support.
        
        Args:
            command_data (dict): The command data containing image click information
            
        Returns:
            tuple: (success, message) - The result of the image click operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Step 1: Validate required fields
        required_fields = ["base_path", "template_name", "platform_type"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error

        # Step 2: Extract command parameters
        base_path = command_data.get("base_path")
        template_name = command_data.get("template_name")
        platform_type = command_data.get("platform_type").lower()  # "ios", "android", "mac", "windows"
        threshold = command_data.get("threshold", 0.7)
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))  # Default 0 seconds - no delay
        delay_before = command_data.get("delay_before", 1)
        ref_img_name = command_data.get("ref_img_name", DEFAULT_REF_IMAGE_NAME)

        # Step 3: Get driver instance for mobile platforms
        driver = None
        if platform_type in ["ios", "android"]:
            success, driver_or_msg = WidgetUtils.get_driver(base_path, tlog)
            if not success:
                return False, driver_or_msg
            driver = driver_or_msg

        # Step 4: Prepare log directory and template image
        log_dir = LogManager.get_instance().get_log_dir()
        os.makedirs(log_dir, exist_ok=True)

        template_path = os.path.join(IMAGES_PATH, template_name)
        template = cv2.imread(template_path)
        if template is None:
            return False, f"Template image not found or unreadable: {template_path}"
        if template.ndim == 3 and template.shape[2] == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

        # Step 5: Define image click operation for retry utility
        def image_click_operation():
            # Take screenshot for matching
            if platform_type in ["mac", "windows"]:
                screenshot = pyautogui.screenshot()
                ref_path = os.path.join(log_dir, ref_img_name)
                screenshot.save(ref_path)
            else:
                ref_path = self.take_screen_shot(driver, folder_path=log_dir, file_name=ref_img_name)

            tlog.d(f"Saved reference image to: {ref_path}")
            screenshot_img = cv2.imread(ref_path)
            if screenshot_img is None:
                return False, "Failed to load screenshot image"

            if screenshot_img.ndim == 3 and screenshot_img.shape[2] == 4:
                screenshot_img = cv2.cvtColor(screenshot_img, cv2.COLOR_BGRA2BGR)

            try:
                res = cv2.matchTemplate(screenshot_img, template, cv2.TM_CCOEFF_NORMED)
            except cv2.error as e:
                tlog.e(f"OpenCV error: {e}")
                return False, f"OpenCV error: {str(e)}"

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            tlog.d(f"Template matching score: {max_val:.3f}")

            if max_val >= threshold:
                top_left = max_loc
                h, w = template.shape[:2]
                center_x = top_left[0] + w // 2
                center_y = top_left[1] + h // 2

                tlog.d(f"Clicking at coordinates: ({center_x}, {center_y}) after {delay_before}s delay")
                time.sleep(delay_before)

                if platform_type in ["mac", "windows"]:
                    # Mark click point for logs
                    marked_path = os.path.join(log_dir, f"marked_{template_name}")
                    success_mark, msg_mark = self.mark_click_point(ref_path, center_x, center_y, marked_path)
                    if success_mark:
                        tlog.d(f"Marked click point on image: {msg_mark}")
                    else:
                        tlog.w(f"Failed to mark click point: {msg_mark}")

                    pyautogui.moveTo(center_x, center_y)
                    pyautogui.click()
                else:
                    # For mobile, scale click coords relative to device screen size
                    screen_size = driver.get_window_size()
                    scale_x = screen_size['width'] / screenshot_img.shape[1]
                    scale_y = screen_size['height'] / screenshot_img.shape[0]
                    click_x = int(center_x * scale_x)
                    click_y = int(center_y * scale_y)

                    # Mark click point for debugging/logging
                    marked_path = os.path.join(log_dir, f"marked_{template_name}")
                    success_mark, msg_mark = self.mark_click_point(ref_path, click_x, click_y, marked_path)
                    if success_mark:
                        tlog.d(f"Marked click point on image: {msg_mark}")
                    else:
                        tlog.w(f"Failed to mark click point: {msg_mark}")

                    try:
                        self.tap_on_device(driver, click_x, click_y, platform_type)
                    except Exception as e:
                        tlog.e(f"Device tap failed: {e}")
                        return False, f"Device tap failed: {str(e)}"

                return True, f"Clicked on template '{template_name}' with score {max_val:.3f}"
            else:
                return False, f"Match below threshold. Score: {max_val:.3f}, required: {threshold}"

        # Step 6: Use retry utility to handle image click with retries
        success, result = WidgetUtils.retry_operation(image_click_operation, max_retry, attempt_interval, tlog)

        # Step 7: Process and return the result
        if success:
            return True, result
        else:
            return False, f"IMAGE_CLICK_FAILED_AFTER_{max_retry}_RETRIES: {result}"
