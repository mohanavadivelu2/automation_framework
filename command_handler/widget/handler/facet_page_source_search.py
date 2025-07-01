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
   "parent_string": "2",       		 # The step label to search from (e.g., "Step 2", "Step 3")
   "text_to_find": "Failed", 		 # The text to find between the specified step and next step
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

Search Behavior:
- For "Step N" format: Searches for text between "Step N" and "Step N+1"
- If next step doesn't exist, searches from "Step N" to end of document
- For non-standard formats or missing steps: Falls back to searching entire document

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
                
                # Search for text between steps
                found = self.find_text_between_steps(page_source, parent_string, text_to_find)
                
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
    
    def find_text_between_steps(self, page_source, parent_string, search_text):
        """
        Search for text between specified step and the next step in the page source.
        If next step is not found, search from specified step to end of document.
        
        Args:
            page_source (str): The XML page source to search in
            parent_string (str): The step label (e.g., "Step 2", "Step 3")
            search_text (str): The text to find between the steps
            
        Returns:
            bool: True if the text was found, False otherwise
        """
        try:
            import re
            
            # Parse the XML string
            root = ET.fromstring(page_source)
            
            # Extract step number from parent_string (e.g., "Step 2" -> 2)
            step_match = re.search(r'Step\s+(\d+)', parent_string, re.IGNORECASE)
            if not step_match:
                # If not in "Step N" format, fallback to full document search
                return self._search_full_document(root, search_text)
            
            step_number = int(step_match.group(1))
            start_step_label = f"Step {step_number}"
            end_step_label = f"Step {step_number + 1}"
            
            def get_all_elements_flat(node):
                """Get all elements in document order (flattened tree)"""
                elements = [node]
                for child in node:
                    elements.extend(get_all_elements_flat(child))
                return elements
            
            def search_between_steps(start_node):
                """Search for text between step boundaries"""
                all_elements = get_all_elements_flat(start_node)
                
                start_index = None
                end_index = None
                
                # Find start and end positions
                for i, element in enumerate(all_elements):
                    if (element.tag == "XCUIElementTypeStaticText" and 
                        element.attrib.get("value", "").strip() == start_step_label):
                        start_index = i
                    elif (element.tag == "XCUIElementTypeStaticText" and 
                          element.attrib.get("value", "").strip() == end_step_label and 
                          start_index is not None):
                        end_index = i
                        break
                
                # If start step not found, fallback to full document search
                if start_index is None:
                    return self._search_full_document(start_node, search_text)
                
                # If end step not found, search from start to end of document
                if end_index is None:
                    end_index = len(all_elements)
                
                # Search for text in the range
                for i in range(start_index, end_index):
                    element = all_elements[i]
                    if (element.tag == "XCUIElementTypeStaticText" and 
                        search_text in element.attrib.get("value", "")):
                        return True
                
                return False
            
            return search_between_steps(root)
            
        except ET.ParseError as e:
            # Log the error
            LogManager.get_instance().get_test_case_logger().e(f"XML parsing error: {e}")
            return False
        except Exception as e:
            # Log any other errors
            LogManager.get_instance().get_test_case_logger().e(f"Error in find_text_between_steps: {e}")
            return False
    
    def _search_full_document(self, root, search_text):
        """
        Search for text in the entire document as a fallback.
        
        Args:
            root: The root XML element to search in
            search_text (str): The text to find
            
        Returns:
            bool: True if the text was found, False otherwise
        """
        try:
            # Search through all XCUIElementTypeStaticText elements in the document
            for element in root.iter("XCUIElementTypeStaticText"):
                if search_text in element.attrib.get("value", ""):
                    return True
            return False
        except Exception as e:
            # Log any errors
            LogManager.get_instance().get_test_case_logger().e(f"Error in _search_full_document: {e}")
            return False
