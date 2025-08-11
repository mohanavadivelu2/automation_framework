# Android Scroll Utilities

A comprehensive Python utility module for Android list automation using Appium WebDriver. This module provides intelligent scrolling, element detection, screenshot analysis, and arrow direction recognition for Android UI testing.

## 🚀 Features

- **🎯 Smart Text Finding**: Automatically scroll through lists to find specific text elements
- **📱 Element Analysis**: Extract XPath, bounds, and visual details of UI elements  
- **📸 Screenshot Integration**: Automatic screenshot capture and element cropping
- **🔄 Arrow Direction Detection**: AI-powered detection of UI arrow directions (up/down/unknown)
- **⚡ Smart Element Toggling**: Intelligent expand/collapse based on current arrow state
- **🏗️ Modular Design**: Clean public/private API separation with robust error handling
- **📊 Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📋 Prerequisites

- **Python 3.7+**
- **Appium Server** running on your system
- **Android device/emulator** connected and accessible

## 📦 Installation

```bash
# Install required packages
pip install appium-python-client pillow selenium
```

## 🔧 Configuration

Update the constants in your code to match your Android app:

```python
# PCTS App Configuration (example)
PCTS_SCROLLABLE_RESOURCE_LIST_ID = "com.google.android.projection.gearhead.pctsverifier:id/list"
PCTS_TOP_LIST_RESOURCE_ID = "android:id/text1"
PCTS_SUB_LIST_RESOURCE_ID = "com.google.android.projection.gearhead.pctsverifier:id/test_caption"

# Your App Configuration
YOUR_SCROLLABLE_LIST_ID = "com.yourapp.package:id/your_list"
YOUR_TOP_ITEM_ID = "com.yourapp.package:id/your_text_element"
```

## 📚 API Reference

### 🎯 Core Scrolling Functions

#### `scroll_to_text(driver, target_text)`
Intelligently scrolls through a list until the specified text becomes visible.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance
- `target_text` (str): Text to scroll to and find (supports substring matching)

**Returns:**
- `bool`: True if text was found and is visible, False otherwise

**Example:**
```python
# Find and scroll to "AudioTests" in the list
if scroll_to_text(driver, "AudioTests"):
    logger.info("AudioTests is now visible on screen")
else:
    logger.error("AudioTests not found in the list")
```

#### `scroll_to_top(driver, resource_id)`
Scrolls the list to the very beginning/top position.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance
- `resource_id` (str): Resource ID of the scrollable list element

**Returns:**
- `bool`: True if successfully scrolled to top, False otherwise

**Example:**
```python
if scroll_to_top(driver, PCTS_SCROLLABLE_RESOURCE_LIST_ID):
    logger.info("Successfully scrolled to top of list")
```

### 📱 Element Detection & Analysis

#### `get_xpath_and_bounds_for_text_item(driver, target_text)`
Finds an element and returns its XPath and screen bounds for interaction.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance
- `target_text` (str): Text of the element to locate

**Returns:**
- `tuple`: (xpath_string, bounds_dict) or (None, None) if not found

**Example:**
```python
xpath, bounds = get_xpath_and_bounds_for_text_item(driver, "VideoTests")
if xpath:
    logger.info(f"Element found at bounds: {bounds}")
    # Click the element
    driver.find_element(AppiumBy.XPATH, xpath).click()
```

#### `get_visible_texts_from_resource(driver, resource_id)`
Gets all visible text items that match a specific resource ID.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance
- `resource_id` (str): Resource ID to filter elements by

**Returns:**
- `list`: List of visible text strings

**Example:**
```python
# Get all visible main category items
visible_items = get_visible_texts_from_resource(driver, PCTS_TOP_LIST_RESOURCE_ID)
logger.info(f"Visible categories: {visible_items}")
```

### 📸 Screenshot & Image Analysis

#### `take_screenshot(driver, file_name)`
Captures a screenshot and saves it with automatic directory creation.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance
- `file_name` (str): Name for the screenshot file (auto-adds .png if needed)

**Returns:**
- `str`: Path to saved screenshot, or None if failed

**Example:**
```python
screenshot_path = take_screenshot(driver, "debug_screenshot")
if screenshot_path:
    logger.info(f"Screenshot saved: {screenshot_path}")
```

#### `crop_element_from_screenshot(screenshot_path, bounds, output_name=None)`
Crops a specific element from a full screenshot using element bounds.

**Parameters:**
- `screenshot_path` (str): Path to the full screenshot
- `bounds` (dict): Element bounds with 'x', 'y', 'width', 'height' keys
- `output_name` (str, optional): Custom name for cropped image

**Returns:**
- `str`: Path to cropped image, or None if failed

#### `check_arrow_direction(cropped_image_path)`
Analyzes a cropped element image to detect arrow direction using advanced image processing.

**Parameters:**
- `cropped_image_path` (str): Path to the cropped element image

**Returns:**
- `str`: 'up', 'down', or 'unknown' based on detected arrow direction

### ⚡ Smart Element Control

#### `toggle_element_visibility(driver, target_text, mode)`
Intelligently toggles element visibility based on current arrow direction and desired state.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance
- `target_text` (str): Text of the element to toggle
- `mode` (str): "show" (expand) or "hide" (collapse)

**Returns:**
- `bool`: True if action completed or element already in desired state

**Smart Logic:**
- **"show" mode**: 
  - ⬇️ Down arrow → Clicks to expand
  - ⬆️ Up arrow → Already expanded, no action
  - ❓ Unknown → Returns False (cannot determine state)
- **"hide" mode**:
  - ⬆️ Up arrow → Clicks to collapse  
  - ⬇️ Down arrow → Already collapsed, no action
  - ❓ Unknown → Returns False (cannot determine state)

**Example:**
```python
# Expand AudioTests if it's currently collapsed
if toggle_element_visibility(driver, "AudioTests", "show"):
    logger.info("AudioTests expanded successfully")
    
    # Wait for UI animation
    time.sleep(1)
    
    # Collapse it back
    if toggle_element_visibility(driver, "AudioTests", "hide"):
        logger.info("AudioTests collapsed successfully")
```

#### `launch_pcts_test_case(driver, main_test_case_name, test_case_name)`
Complete workflow to expand a main test category and launch a specific sub-test case.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance
- `main_test_case_name` (str): Name of the main test category to expand
- `test_case_name` (str): Name of the specific test case to launch

**Returns:**
- `bool`: True if test case was successfully launched

**Example:**
```python
# Expand TouchTests category and launch PTEP1 test
if launch_pcts_test_case(driver, "TouchTests", "PTEP1"):
    logger.info("PTEP1 test launched successfully")
```

### 🎯 PCTS-Specific Helper Functions

These functions are pre-configured for PCTS app testing:

#### `pcts_scroll_to_top(driver)`
Scrolls to top of PCTS test list (uses pre-configured resource ID).

#### `pcts_get_visible_top_list_items(driver)`
Gets visible main category items in PCTS app.

#### `pcts_get_visible_sub_list_items(driver)`  
Gets visible sub-test items in PCTS app.

## 🔧 Configuration Constants

The module uses these configurable constants:

```python
# Scroll behavior configuration
MAX_SCROLL_ATTEMPTS = 50        # Maximum scroll attempts before giving up
SCROLL_DELAY = 1.0             # Delay after major scroll operations (seconds)
SMALL_SCROLL_DELAY = 0.5       # Delay after minor scroll operations (seconds)
SCROLL_BEGINNING_MAX_SWIPES = 25  # Max swipes when scrolling to beginning

# PCTS App specific resource IDs
PCTS_SCROLLABLE_RESOURCE_LIST_ID = "com.google.android.projection.gearhead.pctsverifier:id/list"
PCTS_TOP_LIST_RESOURCE_ID = "android:id/text1"
PCTS_SUB_LIST_RESOURCE_ID = "com.google.android.projection.gearhead.pctsverifier:id/test_caption"
```

## 🚀 Usage Examples

### Basic Text Finding
```python
from scroll_utils import scroll_to_text, take_screenshot

# Find and scroll to specific text
if scroll_to_text(driver, "BluetoothTests"):
    # Take screenshot when found
    take_screenshot(driver, "bluetooth_tests_found")
    logger.info("BluetoothTests is now visible")
```

### Element Interaction Workflow
```python
from scroll_utils import scroll_to_text, get_xpath_and_bounds_for_text_item

# Complete element interaction workflow
target_text = "SpeechRecognitionTests"

# Step 1: Scroll to find the element
if scroll_to_text(driver, target_text):
    # Step 2: Get element details for interaction
    xpath, bounds = get_xpath_and_bounds_for_text_item(driver, target_text)
    
    if xpath:
        logger.info(f"Found element at coordinates: {bounds}")
        # Step 3: Interact with the element
        driver.find_element(AppiumBy.XPATH, xpath).click()
        logger.info(f"Successfully clicked {target_text}")
```

### Smart Element Toggling
```python
from scroll_utils import toggle_element_visibility
import time

# Smart expand/collapse workflow
test_category = "AudioTests"

# Expand the category
if toggle_element_visibility(driver, test_category, "show"):
    logger.info(f"{test_category} expanded")
    
    # Wait for expansion animation
    time.sleep(2)
    
    # Do something with expanded content...
    
    # Collapse back
    if toggle_element_visibility(driver, test_category, "hide"):
        logger.info(f"{test_category} collapsed")
```

### Complete Test Case Launch
```python
from scroll_utils import launch_pcts_test_case

# Launch a specific test case
main_category = "TouchTests"
specific_test = "PTEP1"

if launch_pcts_test_case(driver, main_category, specific_test):
    logger.info(f"Successfully launched {specific_test} from {main_category}")
else:
    logger.error(f"Failed to launch {specific_test}")
```

## 📁 File Structure

```
android_scroll/
├── scroll_utils.py          # Main utility module
├── main.py                  # Example usage and testing
├── README.md               # This documentation
├── screenshots/            # Auto-created directory for screenshots
└── __pycache__/           # Python cache directory
```

## 🐛 Error Handling

All functions include comprehensive error handling:

- **Input Validation**: Functions validate parameters before execution
- **Specific Exception Handling**: Catches Appium-specific exceptions separately
- **Graceful Degradation**: Functions return False/None on failure instead of crashing
- **Detailed Logging**: All operations are logged with appropriate levels (INFO/WARNING/ERROR)

## 🔍 Debugging

Enable debug logging to see detailed operation information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show:
- Element search progress
- Scroll attempt details  
- Screenshot and crop operations
- Arrow detection analysis
- Element interaction steps

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests for new functionality
4. Update documentation
5. Submit a pull request

## 📄 License

This project is open source. See the LICENSE file for details.

---

**Need Help?** Check the example usage in `main.py` or enable debug logging for detailed operation insights.

---

#### `get_all_list_items(driver)`

Gets complete list of all items by scrolling through the entire list from top to bottom.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance

**Returns:**
- `list`: Complete ordered list of all text items in the list

**Example:**
```python
all_items = get_all_list_items(driver)
print(f"Total items in list: {len(all_items)}")
print(f"First 5 items: {all_items[:5]}")
print(f"Last 5 items: {all_items[-5:]}")
```

---

#### `find_text_in_list(driver, search_text)`

Searches for specific text in the entire list by scrolling through it.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance
- `search_text` (str): Text to search for

**Returns:**
- `bool`: True if text is found anywhere in the list, False otherwise

**Example:**
```python
test_items = ["AudioTests", "VideoTests", "NetworkTests"]
for item in test_items:
    found = find_text_in_list(driver, item)
    print(f"'{item}' exists in list: {found}")
```

### Screenshot & Analysis Functions

#### `take_screenshot(driver, file_name)`

Takes a screenshot of the current screen and saves it with a relative path return.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance
- `file_name` (str): Base filename for the screenshot (without extension)

**Returns:**
- `str` or `None`: Relative path to saved screenshot file, or None if failed

**Example:**
```python
screenshot_path = take_screenshot(driver, "current_screen")
if screenshot_path:
    print(f"Screenshot saved: {screenshot_path}")
```

---

#### `crop_element_from_screenshot(screenshot_path, bounds, output_name=None)`

Crops a specific element from a screenshot based on element bounds.

**Parameters:**
- `screenshot_path` (str): Path to the full screenshot image
- `bounds` (dict): Element bounds with keys: x, y, width, height
- `output_name` (str, optional): Custom name for cropped image

**Returns:**
- `str` or `None`: Path to cropped image file, or None if failed

**Example:**
```python
bounds = {"x": 100, "y": 200, "width": 300, "height": 50}
cropped_path = crop_element_from_screenshot("screenshot.png", bounds, "my_element")
if cropped_path:
    print(f"Cropped element saved: {cropped_path}")
```

---

#### `check_arrow_direction(cropped_image_path)`

Analyzes a cropped element image to detect arrow direction using advanced image processing.

**Parameters:**
- `cropped_image_path` (str): Path to the cropped element image

**Returns:**
- `str`: Arrow direction - 'up', 'down', 'none', or 'unknown'

**Algorithm Details:**
- Uses adaptive thresholding for binary image conversion
- Analyzes triangular patterns in the middle section of the image
- Compares pixel density in upper vs lower regions
- Handles both filled and outlined arrow styles

**Example:**
```python
arrow_direction = check_arrow_direction("element_cropped.png")
if arrow_direction == "down":
    print("Element has a downward arrow - likely expandable")
elif arrow_direction == "up":
    print("Element has an upward arrow - likely collapsible")
else:
    print("No clear arrow direction detected")
```

### Legacy Compatibility Functions

#### `print_all_list_items(driver)`

Prints all items in the list and returns them as a list for backward compatibility.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance

**Returns:**
- `list`: List of all items that were printed to console

---

#### `scroll_through_list_and_print(driver)`

Original legacy function that prints items while scrolling through the list.

**Parameters:**
- `driver` (WebDriver): Appium WebDriver instance

**Returns:**
- `None`: Just prints items to console

## Usage Examples

### Basic Element Analysis Workflow

```python
from scroll_utils import scroll_to_text, get_element_details

# Complete workflow: Find element and analyze it
target = "VideoTests"
if scroll_to_text(driver, target):
    details = get_element_details(driver, target)
    if details:
        print(f"✓ Found: {details['text']}")
        print(f"  Location: {details['bounds']}")
        print(f"  Screenshot: {details['screenshot_path']}")
        print(f"  Arrow: {details['arrow_direction']}")
        
        # Make decisions based on arrow direction
        if details['arrow_direction'] == 'down':
            print("  → This item can be expanded")
        elif details['arrow_direction'] == 'up':
            print("  → This item is currently expanded")
    else:
        print(f"✗ Could not analyze {target}")
else:
    print(f"✗ {target} not found in list")
```

### Smart Element Visibility Control

```python
from scroll_utils import toggle_element_visibility

# Simple expand/collapse workflow
target = "AudioTests"

# Expand element if needed
print("Expanding element...")
if toggle_element_visibility(driver, target, "show"):
    print("✓ Element is now expanded")
    
    # Wait for UI animation
    time.sleep(1)
    
    # Collapse element if needed  
    print("Collapsing element...")
    if toggle_element_visibility(driver, target, "hide"):
        print("✓ Element is now collapsed")
    else:
        print("✗ Failed to collapse element")
else:
    print("✗ Failed to expand element")

# Advanced usage with error handling
def smart_toggle_element(driver, element_name, desired_state):
    """Safely toggle element with validation"""
    try:
        success = toggle_element_visibility(driver, element_name, desired_state)
        if success:
            print(f"✓ {element_name} is now {desired_state}n")
            return True
        else:
            print(f"✗ Failed to {desired_state} {element_name}")
            return False
    except Exception as e:
        print(f"✗ Error toggling {element_name}: {e}")
        return False

# Use the safe wrapper
smart_toggle_element(driver, "VideoTests", "show")
```

### Batch Element Analysis

```python
from scroll_utils import scroll_to_text, get_element_details

def analyze_test_items(driver, test_names):
    """Analyze multiple test items and categorize them"""
    results = {
        'expandable': [],
        'expanded': [], 
        'regular': [],
        'not_found': []
    }
    
    for test_name in test_names:
        if scroll_to_text(driver, test_name):
            details = get_element_details(driver, test_name)
            if details:
                arrow = details['arrow_direction']
                if arrow == 'down':
                    results['expandable'].append(test_name)
                elif arrow == 'up':
                    results['expanded'].append(test_name)
                else:
                    results['regular'].append(test_name)
            else:
                results['not_found'].append(test_name)
        else:
            results['not_found'].append(test_name)
    
    return results

# Usage
test_items = ["AudioTests", "VideoTests", "NetworkTests", "BluetoothTests"]
analysis = analyze_test_items(driver, test_items)
print(f"Expandable items: {analysis['expandable']}")
print(f"Currently expanded: {analysis['expanded']}")
```

### List Navigation and Content Analysis

```python
from scroll_utils import get_all_list_items, get_visible_items, scroll_to_top

# Get complete inventory
all_items = get_all_list_items(driver)
print(f"Total test categories: {len(all_items)}")

# Filter items by keyword
audio_tests = [item for item in all_items if 'Audio' in item]
video_tests = [item for item in all_items if 'Video' in item]

print(f"Audio-related tests: {audio_tests}")
print(f"Video-related tests: {video_tests}")

# Quick current view check
scroll_to_top(driver)
visible_now = get_visible_items(driver)
print(f"Items visible at top: {visible_now}")
```

### Screenshot and Image Analysis

```python
from scroll_utils import take_screenshot, crop_element_from_screenshot, check_arrow_direction

# Take full screenshot
screen_path = take_screenshot(driver, "full_list_view")

# Manually crop an area and analyze
custom_bounds = {"x": 150, "y": 300, "width": 400, "height": 60}
cropped_path = crop_element_from_screenshot(screen_path, custom_bounds, "custom_element")

if cropped_path:
    arrow_dir = check_arrow_direction(cropped_path)
    print(f"Custom area arrow direction: {arrow_dir}")
```

### Error Handling Best Practices

```python
from scroll_utils import scroll_to_text, get_element_details
import logging

def safe_element_analysis(driver, target_text):
    """Safely analyze an element with proper error handling"""
    try:
        # Step 1: Try to find the element
        if not scroll_to_text(driver, target_text):
            logging.warning(f"Element '{target_text}' not found in list")
            return None
        
        # Step 2: Get detailed analysis
        details = get_element_details(driver, target_text)
        if not details:
            logging.error(f"Failed to get details for '{target_text}'")
            return None
            
        # Step 3: Validate the results
        required_keys = ['text', 'xpath', 'bounds', 'screenshot_path', 'arrow_direction']
        if not all(key in details for key in required_keys):
            logging.error("Incomplete element details returned")
            return None
            
        return details
        
    except Exception as e:
        logging.error(f"Exception during element analysis: {e}")
        return None

# Usage with error handling
result = safe_element_analysis(driver, "AudioTests")
if result:
    print("Analysis successful:", result['arrow_direction'])
else:
    print("Analysis failed - check logs")
```

## Advanced Features

### Arrow Detection Algorithm

The `check_arrow_direction()` function uses sophisticated image processing:

1. **Adaptive Thresholding**: Automatically adjusts threshold based on image brightness
2. **Middle Section Analysis**: Focuses on the center region where arrows typically appear
3. **Shape Pattern Recognition**: Identifies triangular patterns indicating arrow directions
4. **Noise Filtering**: Handles various arrow styles (filled, outlined, different sizes)

### Performance Optimization Tips

```python
# Fast existence check (current view only)
from scroll_utils import get_visible_items

def quick_check_visible(driver, target_text):
    """Quick check if item is visible without scrolling"""
    return target_text in get_visible_items(driver)

# Efficient batch processing
def find_multiple_items_efficiently(driver, target_list):
    """Find multiple items with minimal scrolling"""
    found_items = {}
    all_items = get_all_list_items(driver)  # One complete scan
    
    for target in target_list:
        found_items[target] = target in all_items
    
    return found_items
```

### Integration with Test Frameworks

```python
import pytest
from scroll_utils import scroll_to_text, get_element_details

class TestAndroidList:
    
    def test_expandable_items_have_arrows(self, driver):
        """Test that expandable items show down arrows"""
        expandable_items = ["AudioTests", "VideoTests"] 
        
        for item in expandable_items:
            assert scroll_to_text(driver, item), f"Could not find {item}"
            details = get_element_details(driver, item)
            assert details is not None, f"Could not get details for {item}"
            assert details['arrow_direction'] in ['down', 'up'], \
                f"{item} should have an arrow but got: {details['arrow_direction']}"
    
    def test_all_test_categories_present(self, driver):
        """Verify all expected test categories are in the list"""
        expected_categories = ["Audio", "Video", "Network", "Bluetooth"]
        all_items = get_all_list_items(driver)
        all_text = " ".join(all_items)
        
        for category in expected_categories:
            assert any(category in item for item in all_items), \
                f"No {category} tests found in list"
```

## Troubleshooting

### Common Issues

1. **Arrow Detection Returns 'unknown'**
   - Check if the cropped image contains a clear arrow
   - Verify the element bounds are correct
   - Some UI elements may not have arrows

2. **Elements Not Found**
   - Verify the `SCROLLABLE_LIST_ID` constant matches your app
   - Check if the list is actually scrollable
   - Ensure elements have text content

3. **Screenshot/Cropping Failures**
   - Check write permissions in the screenshots directory
   - Verify PIL (Pillow) is properly installed
   - Bounds coordinates should be within screen dimensions

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now scroll_utils will provide detailed debug output
```

## Module Architecture

### Public vs Private Methods

**Public API (use these in your code):**
- All functions documented above are part of the public API
- Stable interface, backward compatible
- Full error handling and logging

**Private Methods (internal use only):**
- `_scroll_down_once()` - Internal scrolling mechanism
- `_analyze_by_shape_position()` - Internal arrow analysis algorithm

### Constants Configuration

Update these constants for your specific Android app:

```python
# In scroll_utils.py, modify these lines:
SCROLLABLE_LIST_ID = "your.app.package:id/your_list_id"
SCROLL_XPATH = f'//YourListViewType[@resource-id="{SCROLLABLE_LIST_ID}"]//android.widget.TextView'
```

## License

This utility module is provided as-is for Android automation testing purposes.
