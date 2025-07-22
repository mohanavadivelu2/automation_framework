import os
import xml.etree.ElementTree as ET
from io import StringIO
from logger import LogManager
from ..widget_utils import WidgetUtils
from command_handler.widget.handler.base import BaseHandler
import time

"""
Handler for the 'facet_page_source_search' widget type.

This handler searches for text within an XML page source, with advanced logic for scoping the search
based on "Step" markers within the document.

**Command JSON Format:**
{
   "base_path": "Target application",
   "widget_type": "facet_page_source_search",
   "parent_string": "Step 2",        // The step label to search from.
   "text_to_find": "Failed",         // The text to find.
   "occurrence": 1,                  // Optional: Which occurrence of the step to use. Default is 1.
                                     // Use 99 for the last occurrence.
   "file_name": "page_source.xml",   // Optional: Custom filename for the page source dump.
   "max_retry": 1,                   // Optional: Max retry attempts.
   "attempt_interval": 0,            // Optional: Interval between attempts.
   "validation": { ... }             // Optional: Validation block.
}

**Search Behavior Logic:**

1.  **Standard Search:**
    - If `parent_string` is "Step N", the search is confined to the XML nodes between the
      element for "Step N" and the element for the next step ("Step N+1").

2.  **Last Step Search:**
    - If "Step N" is the last step in the document (no subsequent "Step" element is found),
      the search is performed from "Step N" to the end of the document.

3.  **Missing Step or Invalid Format:**
    - If the `parent_string` is not in the "Step N" format or the specified step is not found
      in the document, the function falls back to searching the entire XML document.

4.  **Multiple Occurrences:**
    - The `occurrence` parameter handles cases where a step label (e.g., "Step 8") appears
      multiple times.
    - `occurrence=1` (default): Starts from the first time "Step 8" appears.
    - `occurrence=2`: Starts from the second time "Step 8" appears.
    - `occurrence=99`: A special value that automatically uses the *last* occurrence of the step.

**Return Value:**
The handler returns a detailed message indicating whether the text was found, the line number of the
found text, the search range (start and end lines), and the total number of occurrences of the
specified step. This rich context is useful for logging and debugging.
"""

class FacetPageSourceSearchHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        tlog = LogManager.get_instance().get_test_case_logger()

        required_fields = ["base_path", "parent_string", "text_to_find"]
        success, error_msg = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error_msg

        base_path = command_data.get("base_path")
        parent_string = command_data.get("parent_string")
        text_to_find = command_data.get("text_to_find")
        occurrence = command_data.get("occurrence", 1)
        file_name = command_data.get("file_name", "page_source.xml")
        folder_path = LogManager.get_instance().get_log_dir()
        max_retry = command_data.get("max_retry", 1)
        attempt_interval = command_data.get("attempt_interval", 0)

        success, driver_or_msg = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, driver_or_msg
        driver = driver_or_msg

        # Check if parent_string is a number and prepend "Step " if it is.
        try:
            step_num_int = int(parent_string)
            parent_string_processed = f"Step {step_num_int}"
            tlog.d(f"Converted numeric parent_string to '{parent_string_processed}'")
        except (ValueError, TypeError):
            # parent_string is not a simple integer, use it as is.
            parent_string_processed = parent_string

        def search_operation():
            time.sleep(command_data.get("delay_before", 5))
            try:
                page_source = driver.page_source
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                
                tlog.d(f"Page source saved to {file_path}")
                
                import re
                step_match = re.search(r'Step\s+(\d+)', str(parent_string_processed), re.IGNORECASE)
                if not step_match:
                    tlog.w(f"parent_string '{parent_string_processed}' is not in 'Step N' format. Searching full document.")
                    step_number = 0 # Indicates a full search
                else:
                    step_number = int(step_match.group(1))

                found, start_line, end_line, found_line, occurrence_count = self.find_text_between_steps(
                    file_path, step_number, text_to_find, occurrence
                )
                
                if found:
                    msg = (f"TEXT_FOUND: '{text_to_find}' at line {found_line} "
                           f"(Searched from line {start_line} to {end_line}). "
                           f"Step {step_number} has {occurrence_count} occurrence(s).")
                    tlog.d(msg)
                    return True, msg
                else:
                    msg = (f"TEXT_NOT_FOUND: '{text_to_find}' "
                           f"(Searched from line {start_line} to {end_line}). "
                           f"Step {step_number} has {occurrence_count} occurrence(s).")
                    tlog.d(msg)
                    return False, msg
                    
            except Exception as e:
                tlog.e(f"Failed to search page source: {e}")
                return False, f"PAGE_SOURCE_SEARCH_FAILED: {str(e)}"
        
        return WidgetUtils.retry_operation(search_operation, max_retry, attempt_interval, tlog)

    def find_text_between_steps(self, xml_file, step_number, search_text, occurrence=1):
        """
        Search for text based on step boundaries in an XML file.

        Args:
            xml_file (str): Path to the XML file.
            step_number (int): The step number to start searching from (0 for full-document search).
            search_text (str): The text to search for.
            occurrence (int): The occurrence of the step to search from.

        Returns:
            tuple: (found, start_line, end_line, found_line, occurrence_count)
        """
        # Step 1: Read and parse the XML file.
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except (FileNotFoundError, ET.ParseError) as e:
            LogManager.get_instance().get_test_case_logger().e(f"Error reading/parsing XML file {xml_file}: {e}")
            return False, -1, -1, -1, 0

        # Step 2: Define the step label.
        start_step_label = f"Step {step_number}" if step_number != 0 else ""

        # Step 3: Get all elements and map them to line numbers for logging.
        all_elements = list(root.iter())
        element_to_line = {}
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            for element in all_elements:
                if element in element_to_line: continue
                element_repr_parts = [f'<{element.tag}'] + [f'{k}="{v}"' for k, v in element.attrib.items()]
                if all(part in stripped_line for part in element_repr_parts):
                    element_to_line[element] = i + 1

        # Step 4: Find all occurrences of the start step.
        start_indices = []
        start_lines = []
        if step_number != 0:
            for i, element in enumerate(all_elements):
                if element.tag == "XCUIElementTypeStaticText" and element.attrib.get("value", "").strip() == start_step_label:
                    start_indices.append(i)
                    start_lines.append(element_to_line.get(element, -1))

        # Step 5: Determine the search range based on the specified occurrence.
        occurrence_count = len(start_indices)
        if occurrence_count == 0:
            # If start step not found or not specified, search the entire document.
            search_range = all_elements
            start_line = 1
            end_line = len(lines)
        else:
            # Handle `occurrence=99` for last occurrence.
            if occurrence == 99:
                occurrence = occurrence_count
            
            if occurrence > occurrence_count:
                return False, -1, -1, -1, occurrence_count

            start_index = start_indices[occurrence - 1]
            start_line = start_lines[occurrence - 1]
            
            # Find the end index (the next "Step" marker).
            end_index = -1
            end_line = -1
            for i in range(start_index + 1, len(all_elements)):
                element = all_elements[i]
                if element.tag == "XCUIElementTypeStaticText" and element.attrib.get("value", "").strip().startswith("Step"):
                    end_index = i
                    end_line = element_to_line.get(element, -1)
                    break
            
            # Define the search range. If no end step is found, search to the end.
            search_range = all_elements[start_index:] if end_index == -1 else all_elements[start_index:end_index]
            if end_line == -1:
                end_line = len(lines)

        # Step 6: Search for the text within the determined range.
        for element in search_range:
            if search_text in element.attrib.get("value", "") or search_text in element.attrib.get("label", ""):
                found_line = element_to_line.get(element, -1)
                return True, start_line, end_line, found_line, occurrence_count
                
        return False, start_line, end_line, -1, occurrence_count
