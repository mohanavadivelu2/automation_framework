from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
from utility.pcts_scroll import scroll_utils

"""
Command format for pcts_launcher widget.

This handler is used to launch or close test cases in the PCTS Verifier application.

Args:
    widget_type (str): "pcts_launcher"
    action (str): "launch" or "close"
    main_test_case (str): The name of the main test case category.
    sub_test_case (str): The name of the specific sub test case to launch. (Mandatory for "launch" action)

Example for "launch":
{
   "widget_type": "pcts_launcher",
   "action": "launch",
   "main_test_case": "TouchTests",
   "sub_test_case": "PTEP1"
}

Example for "close":
{
   "widget_type": "pcts_launcher",
   "action": "close",
   "main_test_case": "TouchTests"
}
"""
class PctsLauncherHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a pcts launcher command.
        
        Args:
            command_data (dict): The command data containing pcts launcher information
            
        Returns:
            tuple: (success, message) - The result of the pcts launcher operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Step 1: Validate required fields
        required_fields = ["base_path", "widget_type", "action", "main_test_case"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error

        # Step 2: Extract command parameters
        base_path = command_data.get("base_path")
        action = command_data.get("action")
        main_test_case = command_data.get("main_test_case")
        sub_test_case = command_data.get("sub_test_case")

        # Step 3: Get driver instance
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result

        # Step 4: Process action
        if action == "launch":
            if not sub_test_case:
                return False, "sub_test_case is required for launch action"
            success = scroll_utils.launch_pcts_test_case(driver, main_test_case, sub_test_case)
            if success:
                tlog.i(f"Launched test case: {main_test_case} -> {sub_test_case}")
                return True, f"LAUNCH_SUCCESS"
            else:
                return False, f"LAUNCH_FAILED"
        elif action == "close":
            success = scroll_utils.toggle_element_visibility(driver, main_test_case, "hide")
            if success:
                tlog.i(f"Closed test case: {main_test_case}")
                return True, f"CLOSE_SUCCESS"
            else:
                return False, f"CLOSE_FAILED"
        else:
            return False, f"INVALID_ACTION"
