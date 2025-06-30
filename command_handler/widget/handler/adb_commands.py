import subprocess
import time
import os
from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager

class ADBBaseHandler(BaseHandler):
    """
    Base class for all ADB-related handlers with common functionality.
    """
    
    def execute_adb_command(self, command_parts, max_retry=1, attempt_interval=0, tlog=None):
        """
        Execute an ADB command with retry logic.
        
        Args:
            command_parts (list): List of command parts to execute
            max_retry (int): Maximum number of retry attempts (default: 1 - no retry)
            attempt_interval (int): Interval between attempts in seconds (default: 0 - no delay)
            tlog: Logger instance
            
        Returns:
            tuple: (success, result/error_message)
        """
        if tlog is None:
            tlog = LogManager.get_instance().get_test_case_logger()
        
        def run_adb_command():
            try:
                tlog.d(f"Executing ADB command: adb {' '.join(command_parts)}")
                result = subprocess.run(['adb'] + command_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if result.returncode == 0:
                    tlog.d(f"ADB Command Success: {' '.join(command_parts)} | Output: {result.stdout.strip()}")
                    return True, result.stdout.strip()
                else:
                    error = result.stderr.strip()
                    tlog.e(f"ADB Command Error: {' '.join(command_parts)} | Error Output: {error}")
                    return False, error
                    
            except Exception as e:
                error = f"ADB Command Exception: {e}"
                tlog.e(error)
                return False, error
        
        # Use the retry utility
        return WidgetUtils.retry_operation(run_adb_command, max_retry, attempt_interval, tlog)


class ADBLaunchHandler(ADBBaseHandler):
    """
    Handler for launching Android applications via ADB.
    
    Command format:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_launch",
       "package_name": "com.example.app",
       "activity_name": ".MainActivity",
       "wait": 2,
       "attempt_interval": 0,
       "max_retry": 1
    }
    ```
    
    Parameters:
    - base_path: Target application identifier (required)
    - widget_type: Must be "adb_launch" (required)
    - package_name: Android package name to launch (required)
    - activity_name: Activity name to launch (required)
    - wait: Wait time in seconds after launching (optional, default: 0)
    - max_retry: Maximum number of retry attempts (optional, default: 1 - no retry)
    - attempt_interval: Interval between attempts in seconds (optional, default: 0 - no delay)
    
    Example:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_launch",
       "package_name": "com.android.settings",
       "activity_name": ".Settings",
       "wait": 2
    }
    ```
    """
    
    def processCommand(self, command_data: dict):
        """
        Process an ADB launch command to start an Android application activity.

        Args:
            command_data (dict): The command data containing launch parameters
            
        Returns:
            tuple: (success, message) - The result of the launch operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Validate required fields
        required_fields = ["base_path", "package_name", "activity_name"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error

        # Extract command parameters
        package_name = command_data.get("package_name")
        activity_name = command_data.get("activity_name")
        wait = command_data.get("wait", 0)
        
        # Get retry parameter
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))

        # Prepare component name
        if "/" in activity_name:
            component = activity_name
        elif activity_name.startswith("."):
            component = f"{package_name}/{package_name}{activity_name}"
        else:
            component = f"{package_name}/{activity_name}"

        # Execute the launch command
        adb_command = ["shell", "am", "start", "-n", component]
        success, result = self.execute_adb_command(adb_command, max_retry, attempt_interval, tlog)
        
        if not success:
            return False, result
            
        # Wait if specified
        if wait > 0:
            tlog.d(f"Waiting for {wait} seconds after launching activity...")
            time.sleep(wait)
            
        # Check if the activity is running in foreground
        check_command = ["shell", "dumpsys", "activity", "|", "grep", package_name]
        success, result = self.execute_adb_command(check_command, max_retry, attempt_interval, tlog)
        
        if success:
            activity_short_name = component.split("/")[-1]
            if activity_short_name in result:
                tlog.d(f"Activity {component} is running successfully.")
                return True, "ACTIVITY_LAUNCHED_SUCCESSFULLY"
            else:
                return False, f"Activity {component} is not running. Output: {result}"
        else:
            return False, f"Error checking activity status: {result}"


class ADBShellHandler(ADBBaseHandler):
    """
    Handler for executing arbitrary ADB shell commands.
    
    Command format:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_shell",
       "command": "dumpsys battery set level 100",
       "max_attempts": 1,
       "attempt_interval": 0,
       "max_retry": 1
    }
    ```
    
    Parameters:
    - base_path: Target application identifier (required)
    - widget_type: Must be "adb_shell" (required)
    - command: Shell command to execute (required)
    - max_retry: Maximum number of retry attempts (optional, default: 1 - no retry)
    - attempt_interval: Interval between attempts in seconds (optional, default: 0 - no delay)
    
    Example:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_shell",
       "command": "settings put global airplane_mode_on 1"
    }
    ```
    """
    
    def processCommand(self, command_data: dict):
        """
        Process an ADB shell command.

        Args:
            command_data (dict): The command data containing shell command
            
        Returns:
            tuple: (success, message) - The result of the shell operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Validate required fields
        success, error = WidgetUtils.validate_required_fields(command_data, ["base_path", "command"], tlog)
        if not success:
            return False, error

        # Extract command parameters
        shell_command = command_data.get("command")
        
        # Get retry parameter
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))

        # Execute the shell command
        command_parts = ["shell"] + shell_command.split()
        success, result = self.execute_adb_command(command_parts, max_retry, attempt_interval, tlog)
        
        if success:
            return True, "SHELL_EXECUTED"
        else:
            return False, f"SHELL_ERROR: {result}"


class ADBInstallHandler(ADBBaseHandler):
    """
    Handler for installing APKs via ADB.
    
    Command format:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_install",
       "apk_path": "/path/to/app.apk",
       "attempt_interval": 0,
       "max_retry": 1
    }
    ```
    
    Parameters:
    - base_path: Target application identifier (required)
    - widget_type: Must be "adb_install" (required)
    - apk_path: Path to the APK file to install (required)
    - max_retry: Maximum number of retry attempts (optional, default: 1 - no retry)
    - attempt_interval: Interval between attempts in seconds (optional, default: 0 - no delay)
    
    Example:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_install",
       "apk_path": "project_config/demo/apps/test_app.apk"
    }
    ```
    """
    
    def processCommand(self, command_data: dict):
        """
        Process an ADB install command to install an APK.

        Args:
            command_data (dict): The command data containing APK path
            
        Returns:
            tuple: (success, message) - The result of the install operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Validate required fields
        success, error = WidgetUtils.validate_required_fields(command_data, ["base_path", "apk_path"], tlog)
        if not success:
            return False, error

        # Extract command parameters
        apk_path = command_data.get("apk_path")
        
        # Get retry parameter
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))

        # Check if APK file exists
        if not os.path.exists(apk_path):
            tlog.e(f"APK file not found: {apk_path}")
            return False, f"APK_FILE_NOT_FOUND: {apk_path}"

        # Execute the install command
        command_parts = ["install", apk_path]
        success, result = self.execute_adb_command(command_parts, max_retry, attempt_interval, tlog)
        
        if success:
            return True, "APK_INSTALLED"
        else:
            return False, f"INSTALL_ERROR: {result}"


class ADBSwipeHandler(ADBBaseHandler):
    """
    Handler for directional swipe gestures via ADB.
    
    Command format:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_swipe",
       "direction": "left",
       "duration": 300,
       "screen_width": 1080,
       "screen_height": 1920,
       "attempt_interval": 0,
       "max_retry": 1
    }
    ```
    
    Parameters:
    - base_path: Target application identifier (required)
    - widget_type: Must be "adb_swipe" (required)
    - direction: Swipe direction, either "left" or "right" (required)
    - duration: Swipe duration in milliseconds (optional, default: 300)
    - screen_width: Screen width in pixels (optional, default: 1080)
    - screen_height: Screen height in pixels (optional, default: 1920)
    - max_retry: Maximum number of retry attempts (optional, default: 1 - no retry)
    - attempt_interval: Interval between attempts in seconds (optional, default: 0 - no delay)
    
    Example:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_swipe",
       "direction": "left",
       "duration": 500
    }
    ```
    """
    
    def processCommand(self, command_data: dict):
        """
        Process an ADB swipe command for directional swipes.

        Args:
            command_data (dict): The command data containing swipe parameters
            
        Returns:
            tuple: (success, message) - The result of the swipe operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Validate required fields
        success, error = WidgetUtils.validate_required_fields(command_data, ["base_path", "direction"], tlog)
        if not success:
            return False, error

        # Extract command parameters
        direction = command_data.get("direction").lower()
        duration = str(command_data.get("duration", 300))
        width = command_data.get("screen_width", 1080)
        height = command_data.get("screen_height", 1920)
        
        # Get retry parameter
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))

        # Calculate swipe coordinates
        mid_y = height // 2
        padding = int(width * 0.1)

        # Adjust for specific screen size (1920x720)
        if direction == "left":
            if width == 1920 and height == 720:
                x1, x2 = 1700, 200  # Working swipe left for this screen
            else:
                x1, x2 = width - padding, padding
        elif direction == "right":
            if width == 1920 and height == 720:
                x1, x2 = 200, 1700  # Working swipe right for this screen
            else:
                x1, x2 = padding, width - padding
        else:
            return False, f"INVALID_DIRECTION: '{direction}' (use 'left' or 'right')"

        # Execute the swipe command
        command_parts = ["shell", "input", "swipe", str(x1), str(mid_y), str(x2), str(mid_y), duration]
        success, result = self.execute_adb_command(command_parts, max_retry, attempt_interval, tlog)
        
        if success:
            return True, f"SWIPE_{direction.upper()}_SUCCESS"
        else:
            return False, f"SWIPE_{direction.upper()}_FAIL: {result}"


class ADBSwipeXYHandler(ADBBaseHandler):
    """
    Handler for precise coordinate swipe gestures via ADB.
    
    Command format:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_swipe_xy",
       "start_x": 500,
       "start_y": 1000,
       "end_x": 100,
       "end_y": 1000,
       "duration": 300,
       "attempt_interval": 0,
       "max_retry": 1
    }
    ```
    
    Parameters:
    - base_path: Target application identifier (required)
    - widget_type: Must be "adb_swipe_xy" (required)
    - start_x: Starting X coordinate for swipe (required)
    - start_y: Starting Y coordinate for swipe (required)
    - end_x: Ending X coordinate for swipe (required)
    - end_y: Ending Y coordinate for swipe (required)
    - duration: Swipe duration in milliseconds (optional, default: 100)
    - max_retry: Maximum number of retry attempts (optional, default: 1 - no retry)
    - attempt_interval: Interval between attempts in seconds (optional, default: 0 - no delay)
    
    Example:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb_swipe_xy",
       "start_x": 500,
       "start_y": 1000,
       "end_x": 100,
       "end_y": 1000,
       "duration": 500
    }
    ```
    """
    
    def processCommand(self, command_data: dict):
        """
        Process an ADB swipe command for precise coordinate swipes.

        Args:
            command_data (dict): The command data containing swipe coordinates
            
        Returns:
            tuple: (success, message) - The result of the swipe operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Validate required fields
        required_fields = ["base_path", "start_x", "start_y", "end_x", "end_y"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error

        # Extract command parameters
        start_x = command_data.get("start_x")
        start_y = command_data.get("start_y")
        end_x = command_data.get("end_x")
        end_y = command_data.get("end_y")
        duration = str(command_data.get("duration", 100))
        
        # Get retry parameter
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))

        # Execute the swipe command
        command_parts = ["shell", "input", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), duration]
        success, result = self.execute_adb_command(command_parts, max_retry, attempt_interval, tlog)
        
        if success:
            return True, "SWIPE_SUCCESSFUL"
        else:
            return False, f"SWIPE_COMMAND_ERROR: {result}"


class ADBHandler(ADBBaseHandler):
    """
    Handler for launching Android applications via ADB (legacy implementation).
    
    Command format:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb",
       "package_name": "com.example.app",
       "activity_name": "com.example.app/.MainActivity",
       "wait": 2,
       "attempt_interval": 0,
       "max_retry": 1
    }
    ```
    
    Parameters:
    - base_path: Target application identifier (required)
    - widget_type: Must be "adb" (required)
    - package_name: Android package name to launch (required)
    - activity_name: Activity name to launch (required)
    - wait: Wait time in seconds after launching (optional, default: 0)
    - max_retry: Maximum number of retry attempts (optional, default: 1 - no retry)
    - attempt_interval: Interval between attempts in seconds (optional, default: 0 - no delay)
    
    Example:
    ```json
    {
       "base_path": "android",
       "widget_type": "adb",
       "package_name": "com.android.settings",
       "activity_name": "com.android.settings/.Settings",
       "wait": 2
    }
    ```
    
    Note: This handler is maintained for backward compatibility. 
    For new implementations, use ADBLaunchHandler instead.
    """
    
    def processCommand(self, command_data: dict):
        """
        Process an ADB command to launch an Android application activity.

        Args:
            command_data (dict): The command data containing ADB operation information

        Returns:
            tuple: (success, message) - The result of the ADB operation
        """
        # For backward compatibility, delegate to ADBLaunchHandler
        handler = ADBLaunchHandler()
        return handler.processCommand(command_data)


class ActivateAppHandler(BaseHandler):
    """
    Handler for activating applications using Appium driver.
    
    Command format:
    ```json
    {
       "base_path": "android",
       "widget_type": "activate_app",
       "bundle_id": "com.example.app",
       "delay_before": 1,
       "attempt_interval": 0,
       "max_retry": 1
    }
    ```
    
    Parameters:
    - base_path: Target application identifier (required)
    - widget_type: Must be "activate_app" (required)
    - bundle_id: Application bundle ID to activate (required)
    - delay_before: Delay in seconds before activation (optional, default: 1)
    - max_retry: Maximum number of retry attempts (optional, default: 1 - no retry)
    - attempt_interval: Interval between attempts in seconds (optional, default: 0 - no delay)
    
    Example:
    ```json
    {
       "base_path": "android",
       "widget_type": "activate_app",
       "bundle_id": "com.android.settings",
       "delay_before": 2
    }
    ```
    """
    
    def processCommand(self, command_data: dict):
        """
        Process an activate app command.

        Args:
            command_data (dict): The command data containing app activation parameters
            
        Returns:
            tuple: (success, message) - The result of the activation operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Validate required fields
        required_fields = ["base_path", "bundle_id"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error

        # Extract command parameters
        base_path = command_data.get("base_path")
        bundle_id = command_data.get("bundle_id")
        delay_before = float(command_data.get("delay_before", 1))
        
        # Get retry parameter
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))

        # Get driver
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result

        # Apply delay if specified
        if delay_before > 0:
            time.sleep(delay_before)

        # Define activation operation for retry utility
        def activate_app_operation():
            try:
                tlog.i(f"Activating app with bundle ID: {bundle_id}")
                driver.activate_app(bundle_id)
                return True, f"App '{bundle_id}' activated successfully"
            except Exception as e:
                tlog.e(f"Failed to activate app: {e}")
                return False, f"ACTIVATE_APP_FAILED: {str(e)}"
        
        # Use retry utility
        return WidgetUtils.retry_operation(activate_app_operation, max_retry, attempt_interval, tlog)


class TerminateAppHandler(BaseHandler):
    """
    Handler for terminating applications using Appium driver.
    
    Command format:
    ```json
    {
       "base_path": "android",
       "widget_type": "terminate_app",
       "bundle_id": "com.example.app",
       "delay_before": 1,
       "attempt_interval": 0,
       "max_retry": 1
    }
    ```
    
    Parameters:
    - base_path: Target application identifier (required)
    - widget_type: Must be "terminate_app" (required)
    - bundle_id: Application bundle ID to terminate (required)
    - delay_before: Delay in seconds before termination (optional, default: 1)
    - max_retry: Maximum number of retry attempts (optional, default: 1 - no retry)
    - attempt_interval: Interval between attempts in seconds (optional, default: 0 - no delay)
    
    Example:
    ```json
    {
       "base_path": "android",
       "widget_type": "terminate_app",
       "bundle_id": "com.android.settings",
       "delay_before": 2
    }
    ```
    """
    
    def processCommand(self, command_data: dict):
        """
        Process a terminate app command.

        Args:
            command_data (dict): The command data containing app termination parameters
            
        Returns:
            tuple: (success, message) - The result of the termination operation
        """
        tlog = LogManager.get_instance().get_test_case_logger()

        # Validate required fields
        required_fields = ["base_path", "bundle_id"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error

        # Extract command parameters
        base_path = command_data.get("base_path")
        bundle_id = command_data.get("bundle_id")
        delay_before = float(command_data.get("delay_before", 1))
        
        # Get retry parameter
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))

        # Get driver
        success, result = WidgetUtils.get_driver(base_path, tlog)
        if not success:
            return False, result
        driver = result

        # Apply delay if specified
        if delay_before > 0:
            time.sleep(delay_before)

        # Define termination operation for retry utility
        def terminate_app_operation():
            try:
                tlog.i(f"Terminating app with bundle ID: {bundle_id}")
                driver.terminate_app(bundle_id)
                return True, f"App '{bundle_id}' terminated successfully"
            except Exception as e:
                tlog.e(f"Failed to terminate app: {e}")
                return False, f"TERMINATE_APP_FAILED: {str(e)}"
        
        # Use retry utility
        return WidgetUtils.retry_operation(terminate_app_operation, max_retry, attempt_interval, tlog)
