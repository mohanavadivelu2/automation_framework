import os
import time
import cv2
import numpy as np
import pyautogui
from PIL import Image
import sys
from io import BytesIO
import pytesseract
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "text_search",
   "search_text": "Text to search for",
   "search_method": "native",         # Optional: Method to use ("native" or "pytesseract", default: "native")
   "partial_match": false,            # Optional: Whether to search for partial text matches (default: false)
   "click_element": true,             # Optional: Whether to click on the found element (default: true)
   "wait": 4,                         # Optional: Wait time in seconds and element finding timeout (default: 4)
   "max_retry": 1,                    # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,             # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                    # Optional: Commands to execute based on result
      "success": [                    # Commands to execute if text is found
        # more command
      ],
      "failed": [                     # Commands to execute if text is not found
        # more command
      ]
   }
}

Note: The validation section is processed by the CommandProcessor, not by this handler.
"""

DEFAULT_IMAGE_LOG = "image_log"
DEFAULT_IMAGE_NAME = "screenshot.png"

class TextSearchHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a text search command using either native Appium methods or OpenCV-based detection.
        
        Args:
            command_data (dict): The command data containing text search information
            
        Returns:
            tuple: (success, message) - The result of the text search operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Validate required fields
        required_fields = ["base_path", "search_text"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error
            
        # Extract command parameters
        base_path = command_data.get("base_path")
        search_text = command_data.get("search_text")
        search_method = command_data.get("search_method", "native").lower()
        partial_match = command_data.get("partial_match", False)
        click_element = command_data.get("click_element", True)
        wait_time = command_data.get("wait", 4)
        max_retry = command_data.get("max_retry", 1)  # default to 1 attempt (no retry)
        attempt_interval = command_data.get("attempt_interval", 0)  # default to 0s (no delay)
        image_log_folder = command_data.get("image_log_folder", DEFAULT_IMAGE_LOG)
        
    
        # Get driver
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result
        
        # Check if pytesseract is installed when using pytesseract method
        if search_method == "pytesseract":
            try:
                import pytesseract
            except ImportError:
                tlog.e("pytesseract is not installed. Please install it using: pip install pytesseract")
                tlog.e("You also need to install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
                return False, "DEPENDENCY_ERROR: pytesseract is not installed"
        
        # Choose search method
        if search_method == "pytesseract":
            # Define pytesseract search operation for retry utility
            def pytesseract_search_operation():
                tlog.d(f"Pytesseract search for text '{search_text}'")
                success, result = self._process_pytesseract_search(search_text, driver, image_log_folder, click_element, tlog)
                
                if success:
                    if click_element:
                        tlog.i(f"Text '{search_text}' found and clicked in screenshot")
                        return True, "TEXT_FOUND_AND_CLICKED_SUCCESSFULLY"
                    else:
                        tlog.i(f"Text '{search_text}' found in screenshot")
                        return True, {"status": "TEXT_FOUND_SUCCESSFULLY", "text_info": result}
                
                return False, "TEXT_NOT_FOUND"
            
            # Use retry utility for pytesseract search
            return WidgetUtils.retry_operation(pytesseract_search_operation, max_retry, attempt_interval, tlog)
            
        elif search_method == "native":
            # Detect platform
            platform = self._detect_platform(driver, tlog)
            tlog.d(f"Detected platform: {platform}")
            
            # Define native search operation for retry utility
            def native_search_operation():
                tlog.d(f"Native search for text '{search_text}'")
                success, result = self._find_text_native(driver, search_text, platform, partial_match, click_element, wait_time, tlog)
                
                if success:
                    if click_element:
                        tlog.i(f"Text '{search_text}' found and clicked successfully")
                        return True, "TEXT_FOUND_AND_CLICKED_SUCCESSFULLY"
                    else:
                        tlog.i(f"Text '{search_text}' found successfully")
                        return True, {"status": "TEXT_FOUND_SUCCESSFULLY", "element_info": result}
                
                return False, "TEXT_NOT_FOUND"
            
            # Use retry utility for native search
            return WidgetUtils.retry_operation(native_search_operation, max_retry, attempt_interval, tlog)
            
        else:
            tlog.e(f"Invalid search_method: {search_method}. Must be 'native' or 'pytesseract'.")
            return False, f"INVALID_PARAMETER: search_method must be 'native' or 'pytesseract', got '{search_method}'"
    
    def _take_screen_shot(self, driver, folder_path=DEFAULT_IMAGE_LOG, file_name=DEFAULT_IMAGE_NAME, logger=None):
        """
        Captures a screenshot using Appium and saves it to a file.
        
        Args:
            driver: The WebDriver instance
            folder_path (str): The folder to save the screenshot
            file_name (str): The name of the screenshot file
            logger: Logger instance for logging messages
            
        Returns:
            str: The path to the saved screenshot
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
            
        screenshot = driver.get_screenshot_as_png()
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        file_path = os.path.join(folder_path, file_name)
        
        with open(file_path, 'wb') as f:
            f.write(screenshot)
        
        logger.d(f"Screenshot saved to {file_path}")
        
        return file_path
    
    def _process_pytesseract_search(self, search_text, driver, folder_path=DEFAULT_IMAGE_LOG, click_element=True, logger=None):
        """
        Finds text in the screenshot using pytesseract OCR, scales coordinates, optionally clicks the detected locations,
        highlights matches, and saves the result.
        
        Args:
            search_text (str): The text to search for in the screenshot
            driver: The WebDriver instance
            folder_path (str): The folder to save the screenshot
            click_element (bool): Whether to click on the found text
            logger: Logger instance for logging messages
            
        Returns:
            tuple: (success, result) - Whether the text was found and additional information
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
            
        logger.d(f"Pytesseract Searching for text --> [{search_text}]")
        
        # Split search text into words
        words = search_text.split()
        
        # Capture screenshot and convert to OpenCV format
        screenshot_path = self._take_screen_shot(driver, folder_path, "screenshot.png", logger)
        image = cv2.imread(screenshot_path)
        
        if image is None:
            logger.e("Failed to load screenshot.")
            return False, []
        
        # Convert to grayscale for OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use pytesseract to get text data
        try:
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        except Exception as e:
            logger.e(f"Error using pytesseract: {e}")
            return False, []
        
        # Read the device resolution from Appium
        screen_size = driver.get_window_size()
        device_width, device_height = screen_size['width'], screen_size['height']
        logger.d(f"Device screen resolution: {device_width}x{device_height}")
        
        # Calculate scaling factors
        screenshot_width, screenshot_height = image.shape[1], image.shape[0]
        scale_width, scale_height = device_width / screenshot_width, device_height / screenshot_height
        logger.d(f"Screenshot resolution: {screenshot_width}x{screenshot_height}")
        logger.d(f"Width X Height scaling factor: {scale_width}x{scale_height}")
        
        found = False
        mid_points = []
        
        # Search for the text in the OCR results
        for i in range(len(data["text"])):
            if data["text"][i].strip().lower() == words[0].lower():
                matched = True
                coords = [(data["left"][i], data["top"][i], data["width"][i], data["height"][i])]
                
                # For multi-word search, check if subsequent words match
                for j in range(1, len(words)):
                    next_index = i + j
                    if next_index < len(data["text"]) and data["text"][next_index].strip().lower() == words[j].lower():
                        coords.append((data["left"][next_index], data["top"][next_index], 
                                      data["width"][next_index], data["height"][next_index]))
                    else:
                        matched = False
                        break
                
                if matched:
                    found = True
                    x_min = min(c[0] for c in coords)
                    y_min = min(c[1] for c in coords)
                    x_max = max(c[0] + c[2] for c in coords)
                    y_max = max(c[1] + c[3] for c in coords)
                    
                    # Apply scaling factor
                    mid_x = (x_min + ((x_max - x_min) / 2)) * scale_width
                    mid_y = (y_min + ((y_max - y_min) / 2)) * scale_height
                    mid_points.append((mid_x, mid_y))
                    
                    # Draw rectangle around the text
                    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    
                    # Draw circle at midpoint
                    cv2.circle(image, (int(mid_x / scale_width), int(mid_y / scale_height)), 5, (0, 0, 255), -1)
        
        if found:
            # Save the highlighted image
            highlighted_image_path = os.path.join(folder_path, f"{search_text.replace(' ', '_')}_{int(time.time())}.png")
            cv2.imwrite(highlighted_image_path, image)
            logger.d(f"Highlighted screenshot saved to {highlighted_image_path}")
            
            # Prepare detailed information about the found text
            text_info = {
                "mid_points": mid_points,
                "highlighted_image": highlighted_image_path
            }
            
            # Click on the text if requested
            if click_element and mid_points:
                # Detect platform
                platform = self._detect_platform(driver, logger)
                logger.d(f"Detected platform for click: {platform}")
                
                # Click on the first match
                mid_x, mid_y = mid_points[0]
                
                # Use different click methods based on platform
                if platform == "android":
                    # For Android, use webdriver agent x,y click function
                    logger.d(f"Using Android webdriver click at ({mid_x}, {mid_y})")
                    driver.tap([(int(mid_x), int(mid_y))], 100)
                else:
                    # For iOS/Mac, use pyautogui
                    logger.d(f"Using pyautogui click at ({mid_x}, {mid_y})")
                    pyautogui.moveTo(mid_x, mid_y)
                    pyautogui.click()
                
                logger.d(f"Clicked on text at ({mid_x}, {mid_y})")
                
            return True, text_info
        
        logger.d(f"Text '{search_text}' not found in screenshot.")
        return False, []
    
    def _detect_platform(self, driver, logger):
        """
        Detect the platform (iOS, Android, or macOS) from the driver instance.
        
        Args:
            driver: The WebDriver instance
            logger: Logger instance for logging messages
            
        Returns:
            str: The detected platform ("ios", "android", "mac", or "unknown")
        """
        try:
            # First try to get from capabilities
            capabilities = driver.capabilities
            if capabilities and "platformName" in capabilities:
                platform_name = capabilities["platformName"].lower()
                if "ios" in platform_name:
                    return "ios"
                elif "android" in platform_name:
                    return "android"
                elif "mac" in platform_name:
                    return "mac"
            
            # Alternative approach using desired_capabilities (older Appium versions)
            if hasattr(driver, "desired_capabilities"):
                desired_caps = driver.desired_capabilities
                if desired_caps and "platformName" in desired_caps:
                    platform_name = desired_caps["platformName"].lower()
                    if "ios" in platform_name:
                        return "ios"
                    elif "android" in platform_name:
                        return "android"
                    elif "mac" in platform_name:
                        return "mac"
            
            # If we can't determine from capabilities, try to infer from available methods
            # Check for both old and new Appium methods
            if hasattr(driver, "find_element_by_ios_predicate") or hasattr(driver, "find_element"):
                try:
                    # Try to find an element using iOS predicate to see if it's supported
                    driver.find_element(AppiumBy.IOS_PREDICATE, "name == 'test'")
                    return "ios"
                except Exception:
                    pass
                    
            if hasattr(driver, "find_element_by_android_uiautomator") or hasattr(driver, "find_element"):
                try:
                    # Try to find an element using Android UIAutomator to see if it's supported
                    driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text('test')")
                    return "android"
                except Exception:
                    pass
            
            # Default fallback
            logger.w("Could not determine platform type, using generic XPath approach")
            return "unknown"
        except Exception as e:
            logger.e(f"Error detecting platform: {e}")
            return "unknown"
    
    def _find_text_native(self, driver, text, platform, partial_match=False, click_element=True, timeout=4, logger=None):
        """
        Find an element by text using native Appium methods and optionally click it, using the appropriate method based on platform.
        
        Args:
            driver: The WebDriver instance
            text: Text to search for
            platform: The platform type ("ios", "android", "mac", or "unknown")
            partial_match: Whether to search for partial text matches
            click_element: Whether to click on the found element
            timeout: Maximum time to wait for element to be clickable (in seconds)
            logger: Logger instance for logging messages
            
        Returns:
            tuple: (success, result) - Whether the text was found and additional information
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
        
        try:
            element = None
            
            if platform == "ios":
                # iOS: Use iOS Predicate String with WebDriverWait
                if partial_match:
                    predicate = f"value CONTAINS '{text}' OR label CONTAINS '{text}' OR name CONTAINS '{text}'"
                else:
                    predicate = f"value == '{text}' OR label == '{text}' OR name == '{text}'"
                
                logger.d(f"Using iOS predicate with WebDriverWait: {predicate}")
                locator = (AppiumBy.IOS_PREDICATE, predicate)
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable(locator)
                )
                
            elif platform == "android":
                # Android: Use UIAutomator with WebDriverWait
                if partial_match:
                    selector = f'new UiSelector().textContains("{text}")'
                else:
                    selector = f'new UiSelector().text("{text}")'
                
                logger.d(f"Using Android UIAutomator with WebDriverWait: {selector}")
                locator = (AppiumBy.ANDROID_UIAUTOMATOR, selector)
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable(locator)
                )
                
            elif platform == "mac":
                # macOS: Use XPath with WebDriverWait
                if partial_match:
                    xpath = f"//*[contains(@name,'{text}') or contains(@value,'{text}') or contains(@label,'{text}')]"
                else:
                    xpath = f"//*[@name='{text}' or @value='{text}' or @label='{text}']"
                
                logger.d(f"Using macOS XPath with WebDriverWait: {xpath}")
                locator = (AppiumBy.XPATH, xpath)
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable(locator)
                )
                
            else:
                # Unknown platform: Try generic XPath as fallback with WebDriverWait
                if partial_match:
                    xpath = f"//*[contains(text(),'{text}') or contains(@text,'{text}')]"
                else:
                    xpath = f"//*[text()='{text}' or @text='{text}']"
                
                logger.d(f"Using generic XPath with WebDriverWait: {xpath}")
                locator = (AppiumBy.XPATH, xpath)
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable(locator)
                )
            
            if element:
                # Extract element information
                element_info = self._extract_element_info(element, logger)
                
                # Click the element if requested
                if click_element:
                    logger.d(f"Clicking on element with text '{text}'")
                    element.click()
                
                return True, element_info
            
            return False, None
            
        except (NoSuchElementException, TimeoutException) as e:
            logger.d(f"Element with text '{text}' not found: {e}")
            return False, None
        except WebDriverException as e:
            logger.e(f"WebDriver error while finding text '{text}': {e}")
            return False, None
        except Exception as e:
            logger.e(f"Unexpected error while finding text '{text}': {e}")
            return False, None
    
    def _extract_element_info(self, element, logger):
        """
        Extract useful information from an element for debugging and reporting.
        
        Args:
            element: The WebElement instance
            logger: Logger instance for logging messages
            
        Returns:
            dict: Information about the element
        """
        try:
            element_info = {
                "text": element.text,
                "tag_name": element.tag_name if hasattr(element, "tag_name") else "unknown",
                "location": element.location,
                "size": element.size
            }
            
            # Try to get additional attributes that might be available
            try:
                element_info["id"] = element.get_attribute("id")
            except:
                pass
                
            try:
                element_info["name"] = element.get_attribute("name")
            except:
                pass
                
            try:
                element_info["class"] = element.get_attribute("class")
            except:
                pass
                
            try:
                element_info["content-desc"] = element.get_attribute("content-desc")
            except:
                pass
            
            return element_info
        except Exception as e:
            logger.w(f"Error extracting element info: {e}")
            return {"error": str(e)}
