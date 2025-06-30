import os
import xml.etree.ElementTree as ET
from io import StringIO
from logger import LogManager
from ..widget_utils import WidgetUtils
from command_handler.widget.handler.base import BaseHandler

"""
Command format:
{
   "base_path": "Target application",
   "widget_type": "facet_page_source_search",
   "parent_string": "Step 2",        # The parent element text to search under
   "text_to_find": "hand.point.right", # The text to find under the parent element
   "file_name": "page_source.xml",   # Optional: Custom filename for saving the page source (default: page_source.xml)
   "max_retry": 1,                   # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 0,            # Optional: Interval between attempts in seconds (default: 0 - no delay)
   "validation": {                   # Optional: Commands to execute based on search result
      "success": [                   # Commands to execute if text is found
        # more command
      ],
      "failed": [                    # Commands to execute if text is not found
        # more command
      ]
   }
}

Note: The validation section is processed by the CommandProcessor, not by this handler.
"""

class FacetPageSourceSearchHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a facet page source search command.

        Args:
            command_data (dict): The command data containing search parameters
            
        Returns:
            tuple: (success, message) - The result of the search operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Validate required fields
        required_fields = ["base_path", "parent_string", "text_to_find"]
        success, error_msg = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error_msg

        base_path = command_data.get("base_path")
        parent_string = command_data.get("parent_string")
        text_to_find = command_data.get("text_to_find")
        
        # Get optional file name or fallback to default
        file_name = command_data.get("file_name") or "page_source.xml"
        folder_path = LogManager.get_instance().get_log_dir()
        
        # Get retry parameters
        max_retry = command_data.get("max_retry", 1)  # default to 1 attempt (no retry)
        attempt_interval = command_data.get("attempt_interval", 0)  # default to 0s (no delay)

        # Get driver
        success, driver_or_msg = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, driver_or_msg
        driver = driver_or_msg

        # Define search operation for retry utility
        def search_operation():
            try:
                # Get page source
                page_source = driver.page_source
                
                # Save to file
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                
                tlog.d(f"Page source saved to {file_path}")
                
                # Search for text under parent
                found = self.find_text_under_step(page_source, parent_string, text_to_find)
                
                if found:
                    tlog.d(f"Found text '{text_to_find}' under '{parent_string}'")
                    return True, f"TEXT_FOUND: '{text_to_find}' under '{parent_string}'"
                else:
                    tlog.d(f"Text '{text_to_find}' not found under '{parent_string}'")
                    return False, f"TEXT_NOT_FOUND: '{text_to_find}' under '{parent_string}'"
                    
            except Exception as e:
                tlog.e(f"Failed to search page source: {e}")
                return False, f"PAGE_SOURCE_SEARCH_FAILED: {str(e)}"
        
        # Use retry utility
        return WidgetUtils.retry_operation(search_operation, max_retry, attempt_interval, tlog)
    
    def find_text_under_step(self, page_source, parent_string, search_text):
        """
        Search for text under a specific parent string in the page source.
        
        Args:
            page_source (str): The XML page source to search in
            parent_string (str): The parent element text to search under
            search_text (str): The text to find under the parent element
            
        Returns:
            bool: True if the text was found, False otherwise
        """
        try:
            # Parse the XML string
            root = ET.fromstring(page_source)
            
            def search_in_specific_other(start_node):
                """Search for text under the first XCUIElementTypeOther after step staticText."""
                for i, child in enumerate(start_node):
                    if child.tag == "XCUIElementTypeStaticText" and child.attrib.get("value", "").strip() == parent_string:
                        # Try to find the immediate next <XCUIElementTypeOther>
                        for next_sibling in start_node[i + 1:]:
                            if next_sibling.tag == "XCUIElementTypeOther":
                                for inner in next_sibling.iter("XCUIElementTypeStaticText"):
                                    if search_text in inner.attrib.get("value", ""):
                                        return True
                                break  # Only check the first <XCUIElementTypeOther> after the step
                # Recurse children
                for child in start_node:
                    if search_in_specific_other(child):
                        return True
                return False

            return search_in_specific_other(root)
        except ET.ParseError as e:
            # Log the error
            LogManager.get_instance().get_test_case_logger().e(f"XML parsing error: {e}")
            return False
