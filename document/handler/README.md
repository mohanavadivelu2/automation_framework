# Command Handler Module

## Overview

The Command Handler module is a core component of the automation framework, designed to handle UI automation commands across different platforms (Android, iOS, Mac) through a unified interface. It provides a standardized way to interact with UI elements, capture screenshots, perform template matching, and execute platform-specific commands.

The module follows a factory pattern to instantiate appropriate handlers based on the command type, making it easy to extend with new functionality while maintaining a consistent interface.

## Architecture

### Core Components

1. **BaseHandler**: An abstract base class that defines the common interface for all handlers. Each handler must implement the `processCommand` method.

2. **WidgetFactory**: A factory class that maps widget types to their corresponding handler classes and instantiates the appropriate handler based on the command.

3. **WidgetUtils**: A utility class providing common functionality used across handlers, such as finding elements, clicking, entering text, and retry operations.

4. **Handler Classes**: Specialized classes that implement the BaseHandler interface to handle specific types of commands.

### Command Execution Flow

1. A command is received as a dictionary with parameters.
2. The `process_command` function in `execute_command.py` extracts the widget type.
3. The WidgetFactory creates an instance of the appropriate handler.
4. The handler's `processCommand` method is called with the command data.
5. The handler processes the command and returns a success/failure result.

### Retry Mechanism

Most handlers support a retry mechanism through the `WidgetUtils.retry_operation` utility. This allows operations to be retried a specified number of times with configurable intervals between attempts, improving reliability in unstable environments.

## Handler Types

The Command Handler module includes several categories of handlers:

### UI Interaction Handlers

These handlers interact with UI elements through standard operations:

- **ButtonHandler**: Clicks buttons identified by XPath
- **TextHandler**: Enters text into input fields
- **RadioButtonHandler**: Selects radio buttons
- **MacDropDownButtonHandler**: Interacts with dropdown menus on macOS

### Template Matching Handlers

These handlers use image recognition to identify UI elements:

- **SingleTemplateHandler**: Matches a single template image against a screenshot
- **MultiTemplateHandler**: Matches multiple template images against a screenshot
- **ImageClickHandler**: Finds and clicks on UI elements using image recognition

### Device Control Handlers

These handlers control device-specific functionality:

- **ADBHandler**: Executes ADB commands on Android devices
- **ADBLaunchHandler**: Launches Android applications
- **ADBShellHandler**: Executes shell commands on Android devices
- **ADBInstallHandler**: Installs APKs on Android devices
- **ADBSwipeHandler**: Performs directional swipes on Android devices
- **ADBSwipeXYHandler**: Performs precise coordinate swipes on Android devices
- **ActivateAppHandler**: Activates applications using Appium
- **TerminateAppHandler**: Terminates applications using Appium
- **ScrollIosHandler**: Performs scrolling operations on iOS devices

### Utility Handlers

These handlers provide utility functions:

- **ScreenshotHandler**: Captures screenshots
- **PageSourceHandler**: Retrieves page source XML
- **TextSearchHandler**: Searches for text in page source
- **FacetPageSourceSearchHandler**: Specialized search for Facet page source

## Common Parameters

Most handlers support the following common parameters:

- **base_path**: Target application identifier (required)
- **widget_type**: Type of widget/command to execute (required)
- **max_retry**: Maximum number of retry attempts (default: 1 - no retry)
- **attempt_interval**: Interval between retry attempts in seconds (default: 0 - no delay)
- **delay_before**: Delay before executing the command in seconds (varies by handler)
- **validation**: Optional section for commands to execute based on operation result:
  - **success**: Commands to execute if operation succeeds
  - **failed**: Commands to execute if operation fails

## Handler Reference

### ButtonHandler

Clicks a button identified by XPath.

```json
{
   "base_path": "Target application",
   "widget_type": "button",
   "xpath": "//button[@id='submit']",
   "wait": 10,
   "delay_before": 4,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### TextHandler

Enters text into an input field.

```json
{
   "base_path": "Target application",
   "widget_type": "text",
   "xpath": "//input[@id='username']",
   "text": "user123",
   "clear_first": true,
   "wait": 10,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### RadioButtonHandler

Selects a radio button.

```json
{
   "base_path": "Target application",
   "widget_type": "radio_button",
   "xpath": "//input[@type='radio' and @value='option1']",
   "wait": 10,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### MacDropDownButtonHandler

Interacts with dropdown menus on macOS.

```json
{
   "base_path": "Target application",
   "widget_type": "mac_popup_button",
   "popup_xpath": "//XCUIElementTypePopUpButton",
   "menu_xpath": "//XCUIElementTypeMenuItem[@name='Option 1']",
   "wait": 10,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### ScreenshotHandler

Captures a screenshot.

```json
{
   "base_path": "Target application",
   "widget_type": "screenshot",
   "file_name": "screenshot.png",
   "delay_before": 4,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### SingleTemplateHandler

Matches a single template image against a screenshot.

```json
{
   "base_path": "Target application",
   "widget_type": "single_template",
   "template_name": "button.png",
   "ref_img_name": "reference.png",
   "output_name": "result.png",
   "threshold": 0.7,
   "delay_before": 4,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### MultiTemplateHandler

Matches multiple template images against a screenshot.

```json
{
   "base_path": "Target application",
   "widget_type": "multi_template",
   "image_one": "state_on.png",
   "image_two": "state_off.png",
   "image_three": "state_disabled.png",
   "ref_img_name": "reference.png",
   "output_name": "result.png",
   "threshold": 0.7,
   "delay_before": 4,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### ImageClickHandler

Finds and clicks on UI elements using image recognition.

```json
{
   "base_path": "Target application",
   "widget_type": "image_click",
   "template_name": "button.png",
   "platform_type": "ios",
   "threshold": 0.8,
   "delay_before": 1,
   "ref_img_name": "reference.png",
   "max_retry": 1,
   "attempt_interval": 0
}
```

### ScrollIosHandler

Performs scrolling operations on iOS devices.

```json
{
   "base_path": "Target application",
   "widget_type": "ios_scroll",
   "direction": "down",
   "duration": 0.5,
   "delay_before": 1,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### PageSourceHandler

Retrieves page source XML.

```json
{
   "base_path": "Target application",
   "widget_type": "page_source",
   "file_name": "page_source.xml",
   "delay_before": 2,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### TextSearchHandler

Searches for text in page source.

```json
{
   "base_path": "Target application",
   "widget_type": "text_search",
   "text": "Login",
   "case_sensitive": false,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### ADBLaunchHandler

Launches Android applications.

```json
{
   "base_path": "android",
   "widget_type": "adb_launch",
   "package_name": "com.android.settings",
   "activity_name": ".Settings",
   "wait": 2,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### ADBShellHandler

Executes shell commands on Android devices.

```json
{
   "base_path": "android",
   "widget_type": "adb_shell",
   "command": "settings put global airplane_mode_on 1",
   "max_retry": 1,
   "attempt_interval": 0
}
```

### ADBInstallHandler

Installs APKs on Android devices.

```json
{
   "base_path": "android",
   "widget_type": "adb_install",
   "apk_path": "project_config/demo/apps/test_app.apk",
   "max_retry": 1,
   "attempt_interval": 0
}
```

### ADBSwipeHandler

Performs directional swipes on Android devices.

```json
{
   "base_path": "android",
   "widget_type": "adb_swipe",
   "direction": "left",
   "duration": 300,
   "screen_width": 1080,
   "screen_height": 1920,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### ADBSwipeXYHandler

Performs precise coordinate swipes on Android devices.

```json
{
   "base_path": "android",
   "widget_type": "adb_swipe_xy",
   "start_x": 500,
   "start_y": 1000,
   "end_x": 100,
   "end_y": 1000,
   "duration": 300,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### ActivateAppHandler

Activates applications using Appium.

```json
{
   "base_path": "android",
   "widget_type": "activate_app",
   "bundle_id": "com.android.settings",
   "delay_before": 2,
   "max_retry": 1,
   "attempt_interval": 0
}
```

### TerminateAppHandler

Terminates applications using Appium.

```json
{
   "base_path": "android",
   "widget_type": "terminate_app",
   "bundle_id": "com.android.settings",
   "delay_before": 2,
   "max_retry": 1,
   "attempt_interval": 0
}
```

## Best Practices

### Error Handling

- Always check the success status returned by handlers
- Use the validation section to handle success and failure cases
- Log errors for debugging purposes

### Retry Strategies

- Set appropriate `max_retry` values based on the stability of the operation
- Use `attempt_interval` to add delays between retries for operations that may need time to stabilize
- Consider increasing wait times for elements that may take longer to appear

### Command Composition

- Break complex operations into multiple commands
- Use the validation section to create conditional flows
- Keep commands focused on a single operation

### Performance Considerations

- Minimize the use of image recognition operations when XPath is available
- Use appropriate thresholds for template matching to balance accuracy and reliability
- Add delays only when necessary to improve stability

## Integration with Test Cases

The Command Handler module is typically used within test cases defined in JSON format. Here's an example of a test case that uses multiple commands:

```json
{
  "test_case_id": "login_test",
  "description": "Test login functionality",
  "commands": [
    {
      "base_path": "login_app",
      "widget_type": "button",
      "xpath": "//button[@id='login_button']",
      "wait": 10
    },
    {
      "base_path": "login_app",
      "widget_type": "text",
      "xpath": "//input[@id='username']",
      "text": "user123",
      "clear_first": true
    },
    {
      "base_path": "login_app",
      "widget_type": "text",
      "xpath": "//input[@id='password']",
      "text": "password123",
      "clear_first": true
    },
    {
      "base_path": "login_app",
      "widget_type": "button",
      "xpath": "//button[@id='submit']",
      "wait": 10,
      "validation": {
        "success": [
          {
            "base_path": "login_app",
            "widget_type": "text_search",
            "text": "Welcome"
          }
        ],
        "failed": [
          {
            "base_path": "login_app",
            "widget_type": "text_search",
            "text": "Invalid credentials"
          }
        ]
      }
    }
  ]
}
```

## Extending the Framework

To add a new handler:

1. Create a new handler class that inherits from BaseHandler
2. Implement the processCommand method
3. Register the handler in WidgetFactory._handlers dictionary
4. Add the handler to the appropriate __init__.py files

Example of a new handler:

```python
from ..widget_utils import WidgetUtils
from .base import BaseHandler
from logger import LogManager
import time

class NewHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Validate required fields
        required_fields = ["base_path", "custom_param"]
        success, error = WidgetUtils.validate_required_fields(command_data, required_fields, tlog)
        if not success:
            return False, error
            
        # Extract command parameters
        base_path = command_data.get("base_path")
        custom_param = command_data.get("custom_param")
        max_retry = int(command_data.get("max_retry", 1))
        attempt_interval = int(command_data.get("attempt_interval", 0))
        
        # Define operation function
        def operation():
            try:
                # Implement custom operation
                return True, "OPERATION_SUCCESS"
            except Exception as e:
                return False, f"OPERATION_FAILED: {str(e)}"
        
        # Use retry utility
        return WidgetUtils.retry_operation(operation, max_retry, attempt_interval, tlog)
