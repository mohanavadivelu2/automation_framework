import subprocess
import time
from utility.usb_controller.base_controller import BaseController
from utility.usb_controller import usb_config

class AdbController(BaseController):
    """
    A controller to manage the USB port state on a rooted Android device via ADB.
    This class provides methods to enable, disable, and reset the USB data connection
    by sending specific shell commands to the device.
    """

    def _run_adb_command(self, adb_args):
        """
        A helper function to run an ADB command and handle common errors.

        Args:
            adb_args (list): A list of strings representing the command and its arguments.
                             Example: ['shell', 'ls']
        
        Returns:
            bool: True if the command was successful, False otherwise.
        """
        command = ['adb'] + adb_args
        print(f"Executing: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                print(f"ADB Response:\n{result.stdout.strip()}")
            return True
        except FileNotFoundError:
            print("\nError: 'adb' command not found.")
            print("Please ensure the Android SDK Platform-Tools are installed and in your system's PATH.")
            return False
        except subprocess.CalledProcessError as e:
            print("\nError executing ADB command.")
            print(f"Return Code: {e.returncode}")
            print(f"Error Output:\n{e.stderr.strip()}")
            if "device not found" in e.stderr:
                print("\nHint: Is your device connected with USB Debugging enabled and authorized?")
            if "permission denied" in e.stderr:
                 print("\nHint: This command likely requires root access. Trying to run 'adb root' first.")
            return False
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            return False

    def _ensure_root_access(self):
        """Attempts to restart ADB in root mode. Necessary for writing to /dev/."""
        print("\nAttempting to gain root access on the device...")
        self._run_adb_command(['root'])
        print("Waiting for device to re-establish connection...")
        self._run_adb_command(['wait-for-device'])
        print("Device connected.")

    def enable_port(self, port_id=None):
        """Sends the command to enable the USB port."""
        print("\n--- Preparing to turn USB ON ---")
        success = self._run_adb_command(['shell', usb_config.USB_ON_CMD])
        if success:
            print("--- Successfully sent command to turn USB ON ---")
        else:
            print("--- Failed to send command to turn USB ON ---")
        return success

    def disable_port(self, port_id=None):
        """Sends the command to disable the USB port."""
        print("\n--- Preparing to turn USB OFF ---")
        success = self._run_adb_command(['shell', usb_config.USB_OFF_CMD])
        if success:
            print("--- Successfully sent command to turn USB OFF ---")
        else:
            print("--- Failed to send command to turn USB OFF ---")
        return success

    def reset_port(self, port_id=None, delay_seconds=5):
        """
        Resets the USB port by disabling and then re-enabling it.
        """
        print("\n--- Starting USB port reset sequence ---")
        self._ensure_root_access()
        
        if self.disable_port():
            print(f"\nWaiting for {delay_seconds} seconds before enabling...")
            time.sleep(delay_seconds)
            self.enable_port()
        
        print("\n--- USB port reset sequence finished ---")
