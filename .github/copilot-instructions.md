# Automation Framework - AI Development Guide

## Architecture Overview

This is a multi-platform mobile/desktop automation framework built around Appium servers and JSON-driven test cases. The system uses a singleton pattern with centralized managers for servers, sessions, and logging.

### Core Components

- **ApplicationManager** (`app_manager.py`) - Singleton orchestrator that manages the entire lifecycle: OEM config loading → Appium server startup → session creation → cleanup
- **Session Management** - Multi-platform support (Android/iOS/Mac) with platform-specific handlers in `session_manager/`
- **Widget Command System** - Factory pattern in `command_handler/widget/` that maps JSON commands to executable handlers
- **JSON Test Processing** - Test cases are JSON files processed by `json_handler/` with validation and common command inclusion

### Configuration-Driven Architecture

The framework is heavily configuration-driven through `global_config/project_configuration.py`:

- **EXECUTE_GROUP** switches entire test suites (FACETS/SANITY/FCA_SANITY)
- Each group has its own `project_config/{oem}/{group}/` directory structure:
  - `client/` - Appium server configurations with platform capabilities
  - `test_case/` - Individual JSON test files (e.g., `859F3.json`)
  - `master/all_test_case.json` - Test suite definitions
  - `config/oem_config.py` - OEM-specific configurations loaded dynamically
  - `common/` - Reusable command sequences via `"common_command": "filename.json"`

## Development Patterns

### Adding New Widget Types
1. Create handler in `command_handler/widget/handler/` extending base patterns
2. Register in `WidgetFactory._handlers` dict with string key
3. Handler must implement `processCommand()` or method specified in JSON's `call_fun`

### Platform Session Handlers
Platform handlers in `session_manager/` follow the pattern:
- Extend base session handler interface
- Register via `AppiumSessionManager.register_platform_handler()`
- Handle platform-specific capabilities and driver creation

### JSON Test Case Structure
```json
{
  "facet_id": "859F3",
  "command": [
    {
      "base_path": "facets",           // Maps to driver instance
      "widget_type": "button",         // Maps to WidgetFactory handler
      "xpath": "//XCUIElementTypeButton",
      "wait": 4,
      "delay_before": 2
    },
    {
      "common_command": "setup.json"   // Includes reusable sequences
    }
  ]
}
```

### Logging Architecture
Dual logging system via `LogManager` singleton:
- **Application logs** - Framework lifecycle and errors
- **Test case logs** - Individual test execution details
- Timestamped directories with separate log files

## Key Development Commands

- **Run specific test group**: Modify `EXECUTE_GROUP` in `global_config/project_configuration.py`
- **Debug Appium sessions**: Check `ApplicationManager.get_driver_instance_by_base_path(base_path)`
- **Add new OEM**: Create `project_config/{oem}/` structure and update configuration paths
- **Screen recording**: Use `ScreenRecorder` class for test documentation

## Critical Integration Points

- **Dynamic OEM loading**: `ApplicationManager.load_class_from_path()` imports OEM configs from `project_config/`
- **Multi-server coordination**: Each `base_path` in client config gets dedicated Appium server/session
- **Cross-platform widgets**: Same JSON command structure works across Android/iOS/Mac via platform-specific handlers
- **Validation pipeline**: `json_handler/validation/` ensures test case integrity before execution

## Common Pitfalls

- Always call `ApplicationManager.get_instance()` before using any drivers
- Test case IDs must match JSON filenames exactly (e.g., `859F3.json`)
- `base_path` in test commands must match client configuration entries
- Platform capabilities vary - check existing configs in `project_config/{oem}/{group}/client/`
