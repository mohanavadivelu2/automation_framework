from .base import BaseHandler
from ..widget_utils import WidgetUtils
from logger import LogManager
from utility.usb_controller.controller_factory import ControllerFactory
import time

"""
USB Controller Command format:
{
   "widget_type": "usb_reset",
   "action": "reset_port",              # Options: "reset_port", "enable_port", "disable_port" (default: "reset_port")
   "delay_between_commands": 2.0,       # Optional: For reset_port only - delay between disable and enable (default: 2.0)
   "delay_before": 0,                   # Optional: Delay before executing USB command in seconds (default: 0)
   "max_retry": 1,                      # Optional: Maximum number of retry attempts (default: 1 - no retry)
   "attempt_interval": 1,               # Optional: Interval between attempts in seconds (default: 1)
   "validation": {                      # Optional: Commands to execute based on USB operation result
      "success": [                      # Commands to execute if USB operation is successful
        # more commands
      ],
      "failed": [                       # Commands to execute if USB operation fails
        # more commands
      ]
   }
}

Note: The validation section is processed by the CommandProcessor, not by this handler.
USB controller type is determined by the configuration in usb_config.USB_CONTROLLER_TYPE
If no "action" is specified, it defaults to "reset_port" which is the most common operation.
"""

class USBHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        """
        Process a USB controller command.
        
        Args:
            command_data (dict): The command data containing USB operation information
            
        Returns:
            tuple: (success, message) - The result of the USB operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Extract command parameters
        action = command_data.get("action", "reset_port")  # Default to reset_port if not specified
        delay_between_commands = command_data.get("delay_between_commands", 2.0)
        delay_before = command_data.get("delay_before", 0)
        max_retry = command_data.get("max_retry", 1)
        attempt_interval = command_data.get("attempt_interval", 1)
        
        # Optional delay before executing USB command
        if delay_before > 0:
            tlog.i(f"Waiting {delay_before} seconds before USB operation...")
            time.sleep(delay_before)
        
        # Define USB operation function for retry utility
        def usb_operation():
            try:
                # Get controller instance from factory
                controller = ControllerFactory.get_controller()
                tlog.i(f"Created USB controller: {type(controller).__name__}")
                
                # Execute the requested action
                if action == "reset_port" or action is None:
                    tlog.i(f"Executing USB port reset with {delay_between_commands}s delay...")
                    controller.reset_port(delay_between_commands)
                    return True, "USB_PORT_RESET_SUCCESSFUL"
                    
                elif action == "enable_port":
                    tlog.i("Executing USB port enable...")
                    controller.enable_port()
                    return True, "USB_PORT_ENABLE_SUCCESSFUL"
                    
                elif action == "disable_port":
                    tlog.i("Executing USB port disable...")
                    controller.disable_port()
                    return True, "USB_PORT_DISABLE_SUCCESSFUL"
                    
            except Exception as e:
                error_msg = f"USB operation failed: {str(e)}"
                tlog.e(error_msg)
                return False, error_msg
        
        # Use retry utility
        success, message = WidgetUtils.retry_operation(usb_operation, max_retry, attempt_interval, tlog)
        
        if success:
            tlog.i(f"USB {action} completed successfully")
            return True, message
        else:
            return False, message
