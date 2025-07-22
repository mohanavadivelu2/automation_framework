# Automation Framework - Usage Guide

## Table of Contents
1. [Quick Start Guide](#quick-start-guide)
2. [System Overview](#system-overview)
3. [Configuration Setup](#configuration-setup)
4. [Test Development](#test-development)
5. [Advanced Usage](#advanced-usage)
6. [Maintenance and Troubleshooting](#maintenance-and-troubleshooting)
7. [Reference](#reference)

---

## Quick Start Guide

### Prerequisites

Before using this automation framework, ensure you have the following installed:

1. **Python 3.7+** with pip
2. **Appium Server** (install via npm: `npm install -g appium`)
3. **Device drivers** for your target platforms:
   - **Android**: Android SDK, ADB, UiAutomator2 driver
   - **iOS**: Xcode, iOS simulator or physical device, XCUITest driver  
   - **macOS**: Mac2 driver for desktop automation

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd automation_framework
   ```

2. **Install Python dependencies:**
   ```bash
   pip install appium-python-client selenium
   ```

3. **Install Appium drivers:**
   ```bash
   appium driver install uiautomator2    # For Android
   appium driver install xcuitest        # For iOS
   appium driver install mac2            # For macOS
   ```

4. **Verify device connectivity:**
   ```bash
   # For Android
   adb devices
   
   # For iOS (if using simulator)
   xcrun simctl list devices
   ```

### First Test Execution

1. **Configure your test environment** by editing `global_config/project_configuration.py`:
   ```python
   EXECUTE_GROUP = "FACETS"  # Options: "FACETS", "SANITY", "FCA_SANITY"
   ```

2. **Update device configuration** in the appropriate client config file:
   - For FACETS: `project_config/tata/facets/client/mac_client_configuration.json`
   - For SANITY: `project_config/tata/sanity/client/android_client_configuration.json`

3. **Run the framework:**
   ```bash
   python Main.py
   ```

4. **Expected output:**
   ```
   Automation tool version - 2.1.6 - clean_up and Refactor of json_handler
   Starting Appium server for base_path: 'facets' on port: 4539
   Driver instance count [2]
   Press Enter to stop servers and close sessions...
   ```

### Verification

- Check the `logs/` directory for timestamped execution logs
- Verify Appium servers are running on configured ports
- Confirm test cases execute without driver connection errors

---

## System Overview

### What This Framework Does

This is a **multi-platform mobile and desktop automation framework** that:
- Executes JSON-defined test cases across Android, iOS, and macOS platforms
- Manages multiple Appium servers and device sessions simultaneously
- Provides reusable widget commands for common UI interactions
- Supports image-based testing and page source validation
- Offers comprehensive logging and screen recording capabilities

### Key Concepts

#### **OEMs (Original Equipment Manufacturers)**
Different automotive manufacturers with their own test configurations:
- `tata` - Tata Motors configurations
- `fca` - Fiat Chrysler Automobiles  
- `subaru` - Subaru configurations
- `demo` - Sample/demo configurations

#### **Test Groups**
Different types of test suites within each OEM:
- `FACETS` - Feature acceptance tests (typically macOS-based)
- `SANITY` - Basic functionality tests (typically Android-based)
- `PCTS` - Performance and compliance tests

#### **Base Paths**
Logical identifiers that map to specific device/application combinations:
- `facets` - macOS Facets application
- `hu_device_manager` - Android head unit device manager
- `ios-iphone_settings` - iOS Settings application
- `cpta` - CarPlay test application

#### **Widget Commands**
Standardized JSON commands for UI interactions:
- `button` - Click/tap operations
- `text` - Text input operations
- `scroll` - Scrolling operations
- `screenshot` - Capture screen images
- `facet_page_source_search` - Advanced XML parsing and text search

### Directory Structure

```
automation_framework/
├── Main.py                    # Entry point
├── app_manager.py            # Singleton orchestrator
├── global_config/
│   └── project_configuration.py  # Environment switching
├── project_config/           # OEM-specific configurations
│   ├── tata/
│   │   ├── facets/          # Test group
│   │   │   ├── client/      # Appium server configs
│   │   │   ├── test_case/   # Individual JSON tests
│   │   │   ├── master/      # Test suite definitions
│   │   │   ├── common/      # Reusable command sequences
│   │   │   └── config/      # OEM-specific settings
│   │   └── sanity/
│   └── fca/
├── command_handler/
│   └── widget/              # Widget command implementations
├── session_manager/         # Platform-specific drivers
├── json_handler/           # Test case processing
└── logs/                   # Timestamped execution logs
```

### Execution Flow

1. **Initialization:** `ApplicationManager` loads OEM config and starts Appium servers
2. **Session Creation:** Platform-specific handlers create device sessions  
3. **Test Processing:** `ProcessTestCase` loads and validates test suite
4. **Command Execution:** Each JSON command is processed by appropriate widget handler
5. **Cleanup:** Sessions are terminated and servers are stopped

---

## Configuration Setup

### Switching Between OEMs

To change the target OEM (manufacturer), update the paths in `global_config/project_configuration.py`:

```python
# For Tata Motors
BASE_DIRECTORY = "project_config/tata/facets/"

# For FCA  
BASE_DIRECTORY = "project_config/fca/sanity/"

# For Subaru
BASE_DIRECTORY = "project_config/subaru/sanity/"
```

### Switching Between Test Groups

Change the `EXECUTE_GROUP` variable to switch test suites:

```python
EXECUTE_GROUP = "FACETS"    # macOS-based feature tests
EXECUTE_GROUP = "SANITY"    # Android-based sanity tests  
EXECUTE_GROUP = "FCA_SANITY" # FCA-specific sanity tests
```

Each group automatically configures:
- Client configuration file (Appium server settings)
- Test case directory and master file
- Common commands directory
- Image assets directory
- OEM-specific configuration class

### Configuring Device Connections

#### Android Configuration
Edit the Android client config (e.g., `project_config/tata/sanity/client/android_client_configuration.json`):

```json
{
  "ServerConfiguration": [
    {
      "platform_name": "Android",
      "port": "4529",
      "base_path": "hu_device_manager",
      "platform_version": "11",
      "device_name": "f75a993e",           // Your device ID from 'adb devices'
      "app_package": "com.harman.devicemanager",
      "app_activity": "com.harman.devicemanager.ui.MainActivity",
      "automation_name": "UiAutomator2"
    }
  ]
}
```

#### iOS Configuration  
Edit the iOS client config:

```json
{
  "platform_name": "ios",
  "platform_version": "18.5",
  "device_name": "iPhone 15",
  "udid": "00008120-000279620269A01E",    // Your device UDID
  "automation_name": "XCUITest",
  "bundle_id": "com.apple.Preferences",
  "base_path": "ios-iphone_settings",
  "port": "4540"
}
```

#### macOS Configuration
Edit the macOS client config:

```json
{
  "platform_name": "mac",
  "port": "4539", 
  "base_path": "facets",
  "bundle_id": "com.apple.Facets3",       // Your target application
  "automation_name": "mac2"
}
```

### Setting Up Appium Server Configurations

Each `base_path` requires its own Appium server instance. The framework automatically:
1. Reads the client configuration file
2. Starts an Appium server for each unique port
3. Creates device sessions using platform-specific capabilities
4. Maps `base_path` identifiers to driver instances

**Key Configuration Rules:**
- Each `base_path` must have a unique port number
- Platform capabilities must match your actual device/simulator setup
- Bundle IDs and package names must match installed applications

---

## Test Development

### Writing JSON Test Cases

Test cases are JSON files in the `test_case/` directory. Each file represents a complete test scenario.

#### Basic Test Case Structure

```json
{
  "facet_id": "859F3",
  "command": [
    {
      "base_path": "facets",
      "widget_type": "text", 
      "xpath": "//XCUIElementTypeTextField[1]",
      "wait": 4,
      "text": "859F3"
    },
    {
      "base_path": "facets",
      "widget_type": "button",
      "xpath": "//XCUIElementTypeButton[@label='Play']",
      "wait": 4
    }
  ]
}
```

#### Required Fields
- `facet_id`: Unique identifier (must match filename without .json)
- `command`: Array of widget commands to execute sequentially

#### Common Command Parameters
- `base_path`: Maps to driver instance (from client configuration)
- `widget_type`: Determines which handler processes the command  
- `xpath`: Element locator (XPath, ID, etc.)
- `wait`: Maximum seconds to wait for element
- `delay_before`: Seconds to wait before executing command

### Using Common Commands for Reusability

Create reusable command sequences in the `common/` directory:

**common/cp_connect.json:**
```json
{
  "command": [
    {
      "base_path": "hu_device_manager",
      "widget_type": "adb",
      "package_name": "com.harman.devicemanager",
      "activity_name": "com.harman.devicemanager.ui.MainActivity",
      "wait": 4
    },
    {
      "base_path": "hu_device_manager", 
      "widget_type": "button",
      "xpath": "//android.widget.Button[@text='Connect']",
      "wait": 10
    }
  ]
}
```

**Include in test cases:**
```json
{
  "facet_id": "TEST001",
  "command": [
    {
      "common_command": "cp_connect.json"
    },
    {
      "base_path": "facets",
      "widget_type": "screenshot",
      "file_name": "after_connection.png"
    }
  ]
}
```

### Widget Types and Their Parameters

#### Button Widget
```json
{
  "base_path": "facets",
  "widget_type": "button",
  "xpath": "//XCUIElementTypeButton[@label='Start Test']",
  "wait": 4,
  "delay_before": 2
}
```

#### Text Input Widget
```json
{
  "base_path": "facets", 
  "widget_type": "text",
  "xpath": "//XCUIElementTypeTextField[1]",
  "text": "Test Input",
  "wait": 4
}
```

#### Screenshot Widget
```json
{
  "base_path": "facets",
  "widget_type": "screenshot", 
  "file_name": "test_result.png",
  "folder_path": "custom_folder"
}
```

#### Scroll Widget
```json
{
  "base_path": "facets",
  "widget_type": "scroll",
  "direction": "up",
  "duration": 0.3
}
```

#### Advanced Page Source Search
```json
{
  "base_path": "facets",
  "widget_type": "facet_page_source_search",
  "parent_string": "Step 2",
  "text_to_find": "Failed", 
  "occurrence": 1,
  "file_name": "page_source.xml"
}
```

This widget performs sophisticated XML parsing to search for text within specific "Step" boundaries in the page source, making it ideal for validation of multi-step test scenarios.

### Image-Based Testing Patterns

#### Single Template Matching
```json
{
  "base_path": "facets",
  "widget_type": "single_template",
  "template_image": "connect_button.png",
  "threshold": 0.8,
  "action": "click"
}
```

#### Multi-Template Matching  
```json
{
  "base_path": "hu_device_manager",
  "widget_type": "multi_template",
  "image_one": "cp_connected.png",
  "image_two": "cp_disconnected.png", 
  "image_three": "bt_connected.png",
  "ref_img_name": "reference.png",
  "output_name": "result.png",
  "threshold": 0.4
}
```

### Validation and Debugging Test Cases

#### Built-in Validation
Add validation blocks to commands:

```json
{
  "base_path": "facets",
  "widget_type": "button",
  "xpath": "//XCUIElementTypeButton[@label='Submit']",
  "wait": 4,
  "validation": {
    "expected_result": true,
    "failure_action": "continue"
  }
}
```

#### Test Case Validation
The framework automatically validates:
- Required fields in JSON structure
- Base path mapping to active driver instances  
- Widget type registration in WidgetFactory
- XPath syntax and element availability

#### Debugging Failed Tests
1. **Check application logs** in `logs/{timestamp}/application.log`
2. **Review test case logs** in `logs/{timestamp}/test_case.log`
3. **Examine captured screenshots** in `image_log/`
4. **Verify page source dumps** saved during facet_page_source_search operations

---

## Advanced Usage

### Screen Recording During Tests

Enable video recording for test documentation:

```python
# In Main.py or custom test script
from screen_recorder import ScreenRecorder
from app_manager import ApplicationManager

manager = ApplicationManager.get_instance()
driver_instance = manager.get_driver_instance_by_base_path("facets")

record = ScreenRecorder(driver_instance, "logs", "test_execution.mp4")
# Execute your test cases
# record.stop_recording()  # Uncomment when ready to stop
```

Configure recording in `global_config/project_configuration.py`:
```python
ENABLE_VIDEO_ENABLED = "YES"  # Enable recording
```

### Custom Widget Handlers

Create new widget types by extending the base handler:

**command_handler/widget/handler/custom_widget.py:**
```python
from command_handler.widget.handler.base import BaseHandler
from logger import LogManager
from ..widget_utils import WidgetUtils

class CustomWidgetHandler(BaseHandler):
    def processCommand(self, command_data: dict):
        tlog = LogManager.get_instance().get_test_case_logger()
        
        # Validate required fields
        required_fields = ["base_path", "custom_param"]
        success, error_msg = WidgetUtils.validate_required_fields(
            command_data, required_fields, tlog
        )
        if not success:
            return False, error_msg
            
        # Get driver instance
        success, driver_or_msg = WidgetUtils.get_driver(
            command_data.get("base_path"), tlog
        )
        if not success:
            return False, driver_or_msg
        driver = driver_or_msg
        
        # Implement custom logic
        try:
            # Your custom automation logic here
            return True, "CUSTOM_WIDGET_SUCCESS"
        except Exception as e:
            return False, f"CUSTOM_WIDGET_FAILED: {str(e)}"
```

**Register in widget_factory.py:**
```python
from command_handler.widget.handler.custom_widget import CustomWidgetHandler

class WidgetFactory:
    _handlers = {
        # ... existing handlers
        "custom_widget": CustomWidgetHandler,
    }
```

### Multi-Platform Test Scenarios

Design tests that span multiple platforms:

```json
{
  "facet_id": "MULTI001",
  "command": [
    {
      "base_path": "hu_device_manager",
      "widget_type": "adb_launch",
      "package_name": "com.harman.devicemanager"
    },
    {
      "base_path": "facets",
      "widget_type": "button", 
      "xpath": "//XCUIElementTypeButton[@label='Start Test']"
    },
    {
      "base_path": "ios-iphone_settings",
      "widget_type": "text_search",
      "text": "CarPlay"
    }
  ]
}
```

This approach allows coordination between:
- Android head unit applications
- macOS desktop test applications  
- iOS device settings and CarPlay functionality

### Logging and Performance Optimization

#### Custom Logging Levels
```python
from logger import LogManager

tlog = LogManager.get_instance().get_test_case_logger()
tlog.d("Debug message")
tlog.i("Info message") 
tlog.w("Warning message")
tlog.e("Error message")
```

#### Performance Settings
Optimize execution speed:

```json
{
  "base_path": "facets",
  "widget_type": "button",
  "xpath": "//XCUIElementTypeButton[@label='Submit']",
  "wait": 2,           // Reduce wait times for known fast elements
  "delay_before": 0,   // Remove unnecessary delays
  "max_retry": 1       // Reduce retries for non-critical operations
}
```

#### Parallel Test Execution
The framework supports multiple concurrent Appium sessions. Configure different ports for parallel execution:

```json
{
  "ServerConfiguration": [
    {
      "base_path": "test_set_1", 
      "port": "4530"
    },
    {
      "base_path": "test_set_2",
      "port": "4531" 
    }
  ]
}
```

---

## Maintenance and Troubleshooting

### Common Error Scenarios and Solutions

#### 1. Appium Server Startup Failures
**Error:** `Failed to start Appium server for base_path: 'facets' on port: 4539`

**Solutions:**
- Check if port is already in use: `netstat -an | grep 4539`
- Kill existing Appium processes: `pkill -f appium`
- Verify Appium installation: `appium --version`
- Check device connectivity before starting

#### 2. Driver Instance Not Found
**Error:** `No driver found for base_path: 'facets'`

**Solutions:**
- Verify base_path matches client configuration exactly
- Check that ApplicationManager.get_instance() was called before use
- Confirm device session was created successfully during initialization
- Review client configuration JSON for syntax errors

#### 3. Element Not Found Errors
**Error:** `Element not found: //XCUIElementTypeButton[@label='Submit']`

**Solutions:**
- Capture screenshot to verify current UI state
- Use page source dump to inspect actual element structure
- Increase wait timeout for dynamic content
- Verify application is in expected state before element interaction

#### 4. Platform-Specific Issues

**macOS:**
- Enable accessibility permissions for Terminal/IDE
- Check System Preferences > Security & Privacy > Accessibility
- Verify target application allows automation

**iOS:**
- Ensure developer profile is trusted on device
- Check iOS version compatibility with XCUITest driver
- Verify WebDriverAgent installation and signing

**Android:**
- Enable USB debugging and developer options
- Check ADB device authorization
- Verify UiAutomator2 driver installation

### Cleaning Up Cache and Logs

Use the provided cleanup utility:

```bash
python Clean.py
```

This script will:
- Remove all `__pycache__` directories recursively
- Clear old log files from `logs/` directory
- Clean temporary image files from `image_log/`

Manual cleanup:
```bash
# Remove Python cache
find . -name "__pycache__" -type d -exec rm -rf {} +

# Clear logs older than 7 days
find logs/ -name "*" -type d -mtime +7 -exec rm -rf {} +

# Reset image log directory
rm -rf image_log/*
```

### Updating Configurations

#### Adding New Devices
1. **Update client configuration** with new device details
2. **Assign unique port** for new Appium server instance  
3. **Test connectivity** independently before integration
4. **Update test cases** to reference new base_path if needed

#### Version Compatibility
- **Appium Python Client:** Keep compatible with server version
- **Platform Drivers:** Update regularly for OS compatibility
- **Device OS Versions:** Test with latest supported versions

### Performance Monitoring

#### Log Analysis
Monitor execution performance through logs:

```bash
# Check average test execution time
grep "Test completed" logs/*/test_case.log | awk '{print $NF}' | sort -n

# Find frequent failure patterns  
grep "FAILED" logs/*/test_case.log | cut -d: -f3 | sort | uniq -c | sort -nr

# Monitor server startup times
grep "Starting Appium server" logs/*/application.log
```

#### Resource Usage
- Monitor CPU/memory usage during parallel test execution
- Check available disk space for logs and screenshots
- Consider implementing log rotation for long-running test suites

---

## Reference

### Complete Widget Command Reference

#### Basic Interaction Widgets

| Widget Type | Purpose | Required Parameters | Optional Parameters |
|-------------|---------|-------------------|-------------------|
| `button` | Click/tap buttons | `base_path`, `xpath` | `wait`, `delay_before`, `max_retry` |
| `text` | Input text | `base_path`, `xpath`, `text` | `wait`, `delay_before`, `clear_first` |
| `scroll` | Scroll gestures | `base_path`, `direction` | `duration`, `start_x`, `start_y` |
| `radio_button` | Select radio buttons | `base_path`, `xpath` | `wait`, `delay_before` |

#### Advanced Widgets

| Widget Type | Purpose | Required Parameters | Optional Parameters |
|-------------|---------|-------------------|-------------------|
| `screenshot` | Capture screenshots | `base_path` | `file_name`, `folder_path` |
| `single_template` | Image template matching | `base_path`, `template_image` | `threshold`, `action`, `click_offset` |
| `multi_template` | Multiple image matching | `base_path`, `image_one`, `image_two` | `image_three`, `threshold`, `output_name` |
| `page_source` | Dump XML page source | `base_path` | `file_name`, `folder_path` |
| `facet_page_source_search` | Advanced XML text search | `base_path`, `parent_string`, `text_to_find` | `occurrence`, `file_name`, `max_retry` |

#### Platform-Specific Widgets

| Widget Type | Platform | Purpose | Required Parameters |
|-------------|----------|---------|-------------------|
| `ios_scroll` | iOS | iOS-specific scrolling | `base_path`, `direction` |
| `mac_popup_button` | macOS | macOS dropdown menus | `base_path`, `xpath` |
| `adb` | Android | Launch Android apps | `base_path`, `package_name` |
| `adb_swipe` | Android | Android swipe gestures | `base_path`, `start_x`, `start_y`, `end_x`, `end_y` |
| `activate_app` | Cross-platform | Bring app to foreground | `base_path`, `bundle_id` |
| `terminate_app` | Cross-platform | Close application | `base_path`, `bundle_id` |

### Configuration File Templates

#### Basic Android Client Configuration
```json
{
  "ServerConfiguration": [
    {
      "platform_name": "Android",
      "port": "4529",
      "base_path": "android_app",
      "platform_version": "11",
      "device_name": "device_id_here",
      "app_package": "com.example.app",
      "app_activity": "com.example.app.MainActivity", 
      "automation_name": "UiAutomator2",
      "noReset": true
    }
  ]
}
```

#### Basic iOS Client Configuration  
```json
{
  "ServerConfiguration": [
    {
      "platform_name": "ios",
      "port": "4540",
      "base_path": "ios_app",
      "platform_version": "17.0",
      "device_name": "iPhone 15",
      "udid": "device_udid_here",
      "bundle_id": "com.example.app",
      "automation_name": "XCUITest",
      "noReset": true,
      "usePrebuiltWDA": false
    }
  ]
}
```

#### Basic macOS Client Configuration
```json
{
  "ServerConfiguration": [
    {
      "platform_name": "mac", 
      "port": "4539",
      "base_path": "mac_app",
      "bundle_id": "com.example.MacApp",
      "automation_name": "mac2"
    }
  ]
}
```

### Command-Line Operations

#### Starting Framework
```bash
# Standard execution
python Main.py

# With custom Python path
PYTHONPATH=/path/to/framework python Main.py

# Background execution with logging
nohup python Main.py > execution.log 2>&1 &
```

#### Appium Server Management
```bash
# Start Appium server manually
appium server --port 4539 --base-path /

# Check running Appium processes  
ps aux | grep appium

# Kill all Appium processes
pkill -f appium
```

#### Device Management
```bash
# Android device management
adb devices                    # List connected devices
adb logcat                    # View device logs  
adb shell dumpsys activity    # Check running activities

# iOS device management  
xcrun simctl list devices     # List available simulators
idevice_id -l                # List connected physical devices
```

### File Naming Conventions

#### Test Case Files
- **Format:** `{FACET_ID}.json` (e.g., `859F3.json`)
- **Location:** `project_config/{oem}/{group}/test_case/`
- **Naming:** Use uppercase alphanumeric IDs matching the `facet_id` field

#### Common Command Files  
- **Format:** `{purpose}.json` (e.g., `cp_connect.json`)
- **Location:** `project_config/{oem}/{group}/common/`
- **Naming:** Use lowercase with underscores, descriptive names

#### Image Files
- **Screenshots:** `{test_id}_{timestamp}.png`
- **Templates:** `{element_name}.png` (e.g., `connect_button.png`)
- **Results:** `{test_id}_result.png`

#### Log Files
- **Application:** `application.log`
- **Test Cases:** `test_case.log`  
- **Directory:** `logs/{timestamp}/`

This completes the comprehensive usage guide for the automation framework. The document provides step-by-step instructions for setup, configuration, test development, and troubleshooting, with real examples from your codebase.
