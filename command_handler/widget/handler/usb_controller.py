from brainstem.stem import USBHub3p
from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
import time
from global_config.project_configuration import USB_CONTROLLER_PORT_NUMBER, USB_CONTROLLER_PORT_RESET_DELAY

class USBControllerHandler(BaseHandler):
    """
    Command format:
    {
        "widget_type": "port_control",
        "port_enable": true  # or false, or null to toggle
    }

    This handler controls a USB port via a BrainStem USBHub3p.
    - If "port_enable" is true, it enables the port.
    - If "port_enable" is false, it disables the port.
    - If "port_enable" is not provided (or null), it toggles the port (disable, wait 1s, then enable).
    """
    def processCommand(self, command_data: dict):
        """
        Process a USB port control command.
        
        Args:
            command_data (dict): The command data containing port control information.
            
        Returns:
            tuple: (success, message) - The result of the port control operation.
        """
        tlog = LogManager.get_instance().get_test_case_logger()
        hub = USBHub3p()
        try:
            # Step 1: Discover and connect to the USBHub3p
            tlog.i("Attempting to connect to USBHub3p...")
            result = hub.discoverAndConnect(0)
            if result != 0:
                tlog.e(f"Failed to connect to USBHub3p. Error code: {result}")
                return False, f"Failed to connect to USBHub3p. Error code: {result}"
            tlog.i("Successfully connected to USBHub3p.")

            # Step 2: Get the port_enable command
            port_enable = command_data.get("port_enable")

            # Step 3: Execute the port action
            if port_enable is not None:
                if port_enable:
                    tlog.i(f"Enabling USB port {USB_CONTROLLER_PORT_NUMBER}...")
                    result = hub.usb.setPortEnable(USB_CONTROLLER_PORT_NUMBER)
                else:
                    tlog.i(f"Disabling USB port {USB_CONTROLLER_PORT_NUMBER}...")
                    result = hub.usb.setPortDisable(USB_CONTROLLER_PORT_NUMBER)
            else:
                # Toggle the port if port_enable is not specified
                tlog.i(f"Toggling USB port {USB_CONTROLLER_PORT_NUMBER}...")
                hub.usb.setPortDisable(USB_CONTROLLER_PORT_NUMBER)
                time.sleep(USB_CONTROLLER_PORT_RESET_DELAY)
                result = hub.usb.setPortEnable(USB_CONTROLLER_PORT_NUMBER)

            # Step 4: Check the result and return
            if result == 0:
                tlog.i(f"USB port {USB_CONTROLLER_PORT_NUMBER} operation successful.")
                return True, f"USB port {USB_CONTROLLER_PORT_NUMBER} operation successful."
            else:
                tlog.e(f"Failed to change port {USB_CONTROLLER_PORT_NUMBER} status. Error code: {result}")
                return False, f"Failed to change port {USB_CONTROLLER_PORT_NUMBER} status. Error code: {result}"
        finally:
            # Step 5: Disconnect from the hub
            hub.disconnect()
            tlog.i("Disconnected from USBHub3p.")
