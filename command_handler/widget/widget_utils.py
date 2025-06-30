"""
Widget utilities module for command_handler.

This module provides common utility functions for widget handlers to reduce code duplication
and standardize operations like finding elements, waiting, and error handling.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    WebDriverException
)
import time
from logger import LogManager

class WidgetUtils:
    """
    Utility class for widget operations.
    
    This class provides common methods for finding elements, waiting, clicking,
    and other operations used by multiple widget handlers.
    """
    
    @staticmethod
    def find_element(driver, xpath, wait_time=10, logger=None):
        """
        Find an element by xpath with explicit wait.
        
        Args:
            driver: The WebDriver instance
            xpath (str): The xpath to locate the element
            wait_time (int): Maximum time to wait for the element in seconds
            logger: Logger instance for logging messages
            
        Returns:
            tuple: (success, element/error_message)
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
            
        try:
            logger.d(f"Waiting for element at xpath: {xpath} (timeout: {wait_time}s)")
            element = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return True, element
        except TimeoutException:
            logger.e(f"Timeout waiting for element: {xpath}")
            return False, "ELEMENT_NOT_FOUND_TIMEOUT"
        except NoSuchElementException:
            logger.e(f"Element not found: {xpath}")
            return False, "ELEMENT_NOT_FOUND"
        except Exception as e:
            logger.e(f"Error finding element {xpath}: {e}")
            return False, f"ELEMENT_FIND_ERROR: {str(e)}"
    
    @staticmethod
    def find_clickable_element(driver, xpath, wait_time=10, logger=None):
        """
        Find a clickable element by xpath with explicit wait.
        
        Args:
            driver: The WebDriver instance
            xpath (str): The xpath to locate the element
            wait_time (int): Maximum time to wait for the element in seconds
            logger: Logger instance for logging messages
            
        Returns:
            tuple: (success, element/error_message)
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
            
        try:
            logger.d(f"Waiting for clickable element at xpath: {xpath} (timeout: {wait_time}s)")
            element = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            return True, element
        except TimeoutException:
            logger.e(f"Timeout waiting for clickable element: {xpath}")
            return False, "ELEMENT_NOT_CLICKABLE_TIMEOUT"
        except NoSuchElementException:
            logger.e(f"Element not found: {xpath}")
            return False, "ELEMENT_NOT_FOUND"
        except Exception as e:
            #logger.e(f"Error finding clickable element {xpath}: {e}")
            logger.e(f"Error finding clickable element {xpath}")
            return False, f"ELEMENT_FIND_ERROR"
    
    @staticmethod
    def click_element(driver, xpath, description="element", wait_time=10, logger=None):
        """
        Find and click an element by xpath.
        
        Args:
            driver: The WebDriver instance
            xpath (str): The xpath to locate the element
            description (str): Description of the element for logging
            wait_time (int): Maximum time to wait for the element in seconds
            logger: Logger instance for logging messages
            
        Returns:
            tuple: (success, result_message)
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
            
        success, result = WidgetUtils.find_clickable_element(driver, xpath, wait_time, logger)
        if not success:
            return False, result
            
        element = result
        try:
            element.click()
            logger.d(f"Clicked on {description} at {xpath}")
            return True, f"{description.upper().replace(' ', '_')}_CLICKED"
        except ElementNotInteractableException:
            logger.e(f"{description.capitalize()} is not interactable: {xpath}")
            return False, f"{description.upper().replace(' ', '_')}_NOT_INTERACTABLE"
        except WebDriverException as e:
            logger.e(f"WebDriver error during {description} click: {e}")
            return False, f"{description.upper().replace(' ', '_')}_WEBDRIVER_ERROR"
        except Exception as e:
            logger.e(f"Error clicking {description}: {e}")
            return False, f"{description.upper().replace(' ', '_')}_CLICK_ERROR"
    
    @staticmethod
    def enter_text(driver, xpath, text, wait_time=10, clear_first=True, logger=None):
        """
        Find an element and enter text.
        
        Args:
            driver: The WebDriver instance
            xpath (str): The xpath to locate the element
            text (str): The text to enter
            wait_time (int): Maximum time to wait for the element in seconds
            clear_first (bool): Whether to clear the field before entering text
            logger: Logger instance for logging messages
            
        Returns:
            tuple: (success, result_message)
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
            
        success, result = WidgetUtils.find_element(driver, xpath, wait_time, logger)
        if not success:
            return False, result
            
        element = result
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            logger.d(f"Entered text '{text}' at {xpath}")
            return True, "TEXT_ENTERED_SUCCESSFULLY"
        except ElementNotInteractableException:
            logger.e(f"Text field is not interactable: {xpath}")
            return False, "TEXT_FIELD_NOT_INTERACTABLE"
        except Exception as e:
            logger.e(f"Error entering text: {e}")
            return False, f"TEXT_ENTRY_ERROR: {str(e)}"
    
    @staticmethod
    def get_driver(base_path, logger=None):
        """
        Get the driver instance for a base path.
        
        Args:
            base_path (str): The base path to get the driver for
            logger: Logger instance for logging messages
            
        Returns:
            tuple: (success, driver/error_message)
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
            
        from app_manager import ApplicationManager
        
        driver = ApplicationManager.get_instance().get_driver_instance_by_base_path(base_path)
        if not driver:
            logger.e(f"No driver instance found for base path: {base_path}")
            return False, "DRIVER_INSTANCE_NOT_FOUND"
        return True, driver
    
    @staticmethod
    def validate_required_fields(command_data, required_fields, logger=None):
        """
        Validate that required fields are present in command data.
        
        Args:
            command_data (dict): The command data to validate
            required_fields (list): List of required field names
            logger: Logger instance for logging messages
            
        Returns:
            tuple: (success, None/error_message)
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
            
        missing_fields = [field for field in required_fields if not command_data.get(field)]
        if missing_fields:
            logger.e(f"Missing required fields: {', '.join(missing_fields)}")
            return False, "MISSING_REQUIRED_FIELDS"
        return True, None
        
    @staticmethod
    def retry_operation(operation_func, max_retry=1, attempt_interval=0, logger=None):
        """
        Execute an operation with retry logic.
        
        Args:
            operation_func: Function to execute that returns (success, result)
            max_retry (int): Maximum number of retry attempts (default: 1 - no retry)
            attempt_interval (int): Interval between attempts in seconds (default: 0 - no delay)
            logger: Logger instance for logging messages
            
        Returns:
            tuple: (success, result) from the operation
        """
        if logger is None:
            logger = LogManager.get_instance().get_test_case_logger()
            
        for attempt in range(1, max_retry + 1):
            success, result = operation_func()
            
            if success:
                return True, result
                
            if attempt < max_retry:
                if attempt_interval > 0:
                    logger.d(f"Attempt {attempt}/{max_retry} failed. Waiting {attempt_interval}s before retry")
                    time.sleep(attempt_interval)
                else:
                    logger.d(f"Attempt {attempt}/{max_retry} failed. Retrying immediately")
        
        return False, result
