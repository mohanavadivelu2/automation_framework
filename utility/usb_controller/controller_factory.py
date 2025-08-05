import os
import sys

# Add the project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utility.usb_controller.controllers.adb_controller import AdbController
from utility.usb_controller.controllers.harman_controller import HarmanController
from utility.usb_controller import usb_config

class ControllerFactory:
    """
    Factory to create controller instances.
    """
    @staticmethod
    def get_controller():
        """
        Get a controller instance based on the controller type.
        """
        if usb_config.USB_CONTROLLER_TYPE == "ADB":
            return AdbController()
        elif usb_config.USB_CONTROLLER_TYPE == "HARMAN":
            return HarmanController()
        else:
            raise ValueError(f"Unknown controller type: {usb_config.USB_CONTROLLER_TYPE}")

if __name__ == '__main__':
    import time

    try:
        # Get the controller instance from the factory
        controller = ControllerFactory.get_controller()
        print(f"Successfully created controller of type: {type(controller).__name__}")

        # --- Test Case 1: Reset the port ---
        print("\n--- Testing Port Reset ---")
        controller.reset_port()
        print("--- Port Reset Test Finished ---")

        time.sleep(2) # Pause between tests

        # --- Test Case 2: Disable the port ---
        print("\n--- Testing Port Disable ---")
        controller.disable_port()
        print("--- Port Disable Test Finished ---")

        time.sleep(2) # Pause between tests

        # --- Test Case 3: Enable the port ---
        print("\n--- Testing Port Enable ---")
        controller.enable_port()
        print("--- Port Enable Test Finished ---")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)