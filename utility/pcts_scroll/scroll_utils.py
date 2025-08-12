import os
import time
import logging
import warnings
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from PIL import Image, ImageDraw

# Get logger
logger = logging.getLogger(__name__)

# Configuration constants
MAX_SCROLL_ATTEMPTS = 50
SCROLL_DELAY = 1.0
SMALL_SCROLL_DELAY = 0.5
SCROLL_BEGINNING_MAX_SWIPES = 25

PCTS_SCROLLABLE_RESOURCE_LIST_ID = "com.google.android.projection.gearhead.pctsverifier:id/list"
PCTS_SCROLL_XPATH = f'//android.widget.ExpandableListView[@resource-id="{PCTS_SCROLLABLE_RESOURCE_LIST_ID}"]//android.widget.TextView'

PCTS_TOP_LIST_RESOURCE_ID = "android:id/text1"
PCTS_SUB_LIST_RESOURCE_ID = "com.google.android.projection.gearhead.pctsverifier:id/test_caption"



# =============================================================================
# PUBLIC API METHODS
# =============================================================================

def scroll_to_top(driver, xpath_scrollable_list_id):
    """
    Scrolls the list to the very beginning/top.
    
    Args:
        driver: Appium WebDriver instance
        xpath_scrollable_list_id: Resource ID of the scrollable list
        
    Raises:
        Exception: If scrolling fails or the list is not scrollable
        
    Returns:
        bool: True if successfully scrolled to top, False otherwise
    """
    # Input validation
    if not driver:
        raise ValueError("Driver cannot be None")
    if not xpath_scrollable_list_id or not xpath_scrollable_list_id.strip():
        raise ValueError("Resource ID cannot be empty")
    
    logger.info("Scrolling to the beginning of the list...")
    try:
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().resourceId("{xpath_scrollable_list_id}"))'
            f'.scrollToBeginning({SCROLL_BEGINNING_MAX_SWIPES})'
        )
        time.sleep(SCROLL_DELAY)
        logger.info("Reached beginning of list")
        return True
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        logger.warning(f"Could not scroll to beginning: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during scroll to top: {e}")
        return False

def find_list_item_in_page(driver, resource_id, expected_text):
    """
    Finds a visible list item on the page with the specified resource-id and exact text.

    Args:
        driver: Appium WebDriver instance
        resource_id (str): Resource-id of the target TextView element
        expected_text (str): Exact text to match

    Returns:
        str or None: The matched text if found, else None
    """
    # Input validation
    if not driver:
        raise ValueError("Driver cannot be None")
    if not resource_id or not resource_id.strip():
        raise ValueError("Resource ID cannot be empty")
    if not expected_text or not expected_text.strip():
        raise ValueError("Expected text cannot be empty")
    
    try:
        xpath = f"//android.widget.TextView[@resource-id='{resource_id}' and @text='{expected_text}']"
        elements = driver.find_elements(AppiumBy.XPATH, xpath)

        # XPath already filters for exact match, so just check if element exists and has text
        if elements and elements[0].text:
            return elements[0].text.strip()
        
        logger.info(f"List item with text '{expected_text}' not found for resource-id '{resource_id}'")
        return None
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        logger.warning(f"Element lookup failed for '{expected_text}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in find_list_item_in_page: {e}")
        return None

def scroll_to_text(driver, target_text, exact_match=False):
    """
    Scrolls through a list until the specified text is visible on screen.

    Args:
        driver: Appium WebDriver instance.
        target_text (str): Text to locate within visible list items.
        exact_match (bool): If True, match text exactly. If False, match as substring.

    Returns:
        bool: True if the target_text was found and is visible, False otherwise.
    """
    # Input validation
    if not driver:
        raise ValueError("Driver cannot be None")
    if not target_text or not target_text.strip():
        raise ValueError("Target text cannot be empty")

    match_type = "exact" if exact_match else "substring"
    logger.info(f"Starting scroll to find text ({match_type} match): '{target_text}'")

    # Scroll to the top before searching
    pcts_scroll_to_top(driver)
    max_scrolls = MAX_SCROLL_ATTEMPTS

    for scroll_count in range(1, max_scrolls + 1):
        logger.debug(f"[Scroll {scroll_count}/{max_scrolls}] Checking visible items...")
        visible_items = get_all_visible_text_items_on_page(driver)

        # Log visible items for debugging
        logger.debug(f"Visible items: {visible_items}")

        # Matching logic
        if exact_match:
            found = any(item == target_text for item in visible_items)
        else:
            found = any(target_text in item for item in visible_items)

        if found:
            logger.info(f"Text ({match_type} match) '{target_text}' is now visible on screen.")
            return True

        if not scroll_down_once(driver):
            logger.warning(f"Reached end of list without finding text ({match_type} match) '{target_text}'.")
            break

    logger.error(f"Failed to find text ({match_type} match) '{target_text}' after {max_scrolls} scrolls.")
    return False


def scroll_down_once(driver):
    """
    Scrolls down by one screen in the list.
    
    Args:
        driver: Appium WebDriver instance
        
    Returns:
        bool: True if scroll was successful, False if reached end
    """
    try:
        # Get current visible items
        before_scroll = get_all_visible_text_items_on_page(driver)
        
        # Perform scroll
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().resourceId("{PCTS_SCROLLABLE_RESOURCE_LIST_ID}"))'
            '.scrollForward()'
        )
        time.sleep(SMALL_SCROLL_DELAY)  # Small delay for scroll to complete
        
        # Check if scroll actually happened
        after_scroll = get_all_visible_text_items_on_page(driver)
        
        # If no new items appeared, we've reached the end
        return before_scroll != after_scroll
        
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        logger.warning(f"Could not scroll down: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during scroll down: {e}")
        return False


def get_visible_texts_from_resource(driver, resource_id):
    """
    Gets all visible text items on the page that match the given resource-id.

    Args:
        driver: Appium WebDriver instance
        resource_id (str): Resource-id of the list items (e.g., android:id/text1)

    Returns:
        list: List of visible non-empty text strings
    """
    try:
        xpath = f"//android.widget.TextView[@resource-id='{resource_id}']"
        elements = driver.find_elements(AppiumBy.XPATH, xpath)

        visible_texts = [el.text.strip() for el in elements if el.text and el.text.strip()]
        
        if visible_texts:
            logger.info(f"Visible items found for resource-id '{resource_id}': {visible_texts}")
        else:
            logger.info(f"No visible list items found for resource-id: {resource_id}")

        return visible_texts
    except Exception as e:
        logger.error(f"Error in get_visible_list_items_on_page: {e}")
        return []


def get_visible_texts_from_resources(driver, resource_ids):
    """
    Gets all visible text items on the page that match one or more resource-ids.
    
    .. deprecated:: 1.0
        Use get_visible_texts_from_resource() for single resource-id instead.

    Args:
        driver: Appium WebDriver instance
        resource_ids (str or list): One or more resource-ids (e.g., "android:id/text1" or list of IDs)

    Returns:
        list: List of visible non-empty text strings from all matching resource-ids
    """
    warnings.warn("This function is deprecated. Use get_visible_texts_from_resource() instead.", 
                  DeprecationWarning, stacklevel=2)
    try:
        if isinstance(resource_ids, str):
            resource_ids = [resource_ids]  # Convert single string to list

        all_visible_texts = []

        for resource_id in resource_ids:
            xpath = f"//android.widget.TextView[@resource-id='{resource_id}']"
            elements = driver.find_elements(AppiumBy.XPATH, xpath)

            visible_texts = [el.text.strip() for el in elements if el.text and el.text.strip()]
            
            if visible_texts:
                logger.info(f"Visible items found for resource-id '{resource_id}': {visible_texts}")
            else:
                logger.info(f"No visible list items found for resource-id: {resource_id}")

            all_visible_texts.extend(visible_texts)

        return all_visible_texts

    except Exception as e:
        logger.error(f"Error in get_visible_list_items_on_page: {e}")
        return []

def get_all_visible_text_items_on_page(driver):
    """
    Fetch all visible text content from elements on the page.

    Args:
        driver: Appium WebDriver instance

    Returns:
        List[str]: A list of visible text strings.
    """
    try:
        elements = driver.find_elements(AppiumBy.XPATH, "//*[normalize-space(@text)]")
        visible_texts = [el.text.strip() for el in elements if el.text.strip()]

        if visible_texts:
            logger.info(f"Found {len(visible_texts)} visible text items: {visible_texts}")
        else:
            logger.info("No visible text items found on the page.")

        return visible_texts
    except Exception as e:
        logger.error(f"Error in get_all_visible_text_items_on_page: {e}")
        return []


def take_screenshot(driver, file_name):
    """
    Takes a screenshot and saves it with the specified filename.
    
    Args:
        driver: Appium WebDriver instance
        file_name: Name of the screenshot file (with or without .png extension)
        
    Returns:
        str: Relative path of the screenshot file if successful, None if failed
    """
    try:
        # Add .png extension if not present
        if not file_name.lower().endswith('.png'):
            file_name += '.png'
        
        # Create screenshots directory if it doesn't exist
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        # Full path for the screenshot
        screenshot_path = os.path.join(screenshots_dir, file_name)
        
        # Take screenshot
        success = driver.save_screenshot(screenshot_path)
        
        if success:
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        else:
            logger.error(f"Failed to save screenshot: {file_name}")
            return None
            
    except Exception as e:
        logger.error(f"Error taking screenshot '{file_name}': {e}")
        return None

def get_xpath_and_bounds_for_text_item(driver, target_text):
    """
    Finds the first element containing the target text within the allowed resource-ids.
    Returns both the XPath and bounds for future click or interaction.

    Args:
        driver: Appium WebDriver instance.
        target_text (str): The text (or substring) to search for.

    Returns:
        tuple[str, dict] | (None, None):
            - XPath string for the matching element
            - Bounds dict: {'x': int, 'y': int, 'width': int, 'height': int}
    """
    try:
        resource_ids = [PCTS_TOP_LIST_RESOURCE_ID, PCTS_SUB_LIST_RESOURCE_ID]

        for res_id in resource_ids:
            xpath = f"//android.widget.TextView[@resource-id='{res_id}']"
            elements = driver.find_elements(AppiumBy.XPATH, xpath)

            for el in elements:
                if target_text in el.text:
                    found_xpath = f"{xpath}[@text=\"{el.text}\"]"
                    bounds = el.rect  # {'x': ..., 'y': ..., 'width': ..., 'height': ...}
                    logger.info(
                        f"Found element with text '{el.text}'. XPath: {found_xpath}, Bounds: {bounds}"
                    )
                    return found_xpath, bounds

        logger.warning(f"No element found containing text: '{target_text}'")
        return None, None

    except Exception as e:
        logger.error(f"Error finding element for text '{target_text}': {e}")
        return None, None


def crop_element_from_screenshot(screenshot_path, bounds, output_name=None):
    """
    Crops an element from a screenshot based on its bounds.
    
    Args:
        screenshot_path: Path to the full screenshot
        bounds: Dictionary with 'x', 'y', 'width', 'height' keys
        output_name: Optional name for cropped image (defaults to adding '_cropped')
        
    Returns:
        str: Path to the cropped image if successful, None if failed
    """
    try:
        if not os.path.exists(screenshot_path):
            logger.error(f"Screenshot file not found: {screenshot_path}")
            return None
            
        # Open the screenshot
        img = Image.open(screenshot_path)
        
        # Extract bounds coordinates
        x = bounds['x']
        y = bounds['y']
        width = bounds['width']
        height = bounds['height']
        
        # Calculate crop box (left, top, right, bottom)
        left = x
        top = y
        right = x + width
        bottom = y + height
        
        # Crop the image
        cropped_img = img.crop((left, top, right, bottom))
        
        # Generate output filename
        if output_name is None:
            base_name = os.path.splitext(screenshot_path)[0]
            output_name = f"{base_name}_cropped.png"
        else:
            if not output_name.lower().endswith('.png'):
                output_name += '.png'
            output_name = os.path.join("screenshots", output_name)
        
        # Save cropped image
        cropped_img.save(output_name)
        logger.info(f"Cropped element saved: {output_name}")
        
        return output_name
        
    except Exception as e:
        logger.error(f"Error cropping element from screenshot: {e}")
        return None


def check_arrow_direction(cropped_image_path):
    """
    Analyzes a cropped image to determine if an arrow is pointing up or down.
    
    Args:
        cropped_image_path: Path to the cropped element image
        
    Returns:
        str: 'up', 'down', or 'unknown' based on arrow direction
    """
    try:
        if not os.path.exists(cropped_image_path):
            logger.error(f"Cropped image not found: {cropped_image_path}")
            return 'unknown'
            
        # Open and process the image
        img = Image.open(cropped_image_path)
        gray_img = img.convert('L')
        width, height = gray_img.size
        
        # Focus on the left portion where the arrow typically appears
        arrow_region_width = min(100, width // 3)
        arrow_region = gray_img.crop((0, 0, arrow_region_width, height))
        
        # Use adaptive threshold for binary conversion
        arrow_pixels = list(arrow_region.getdata())
        pixel_avg = sum(arrow_pixels) / len(arrow_pixels)
        
        if pixel_avg > 200:
            threshold = pixel_avg - 30
            invert_binary = False
        elif pixel_avg > 128:
            threshold = pixel_avg - 20
            invert_binary = False
        else:
            threshold = pixel_avg + 20
            invert_binary = True
        
        # Convert to binary
        if invert_binary:
            binary_img = arrow_region.point(lambda x: 255 if x < threshold else 0, mode='1')
        else:
            binary_img = arrow_region.point(lambda x: 0 if x < threshold else 255, mode='1')
        
        # Analyze pixel data
        pixels = list(binary_img.getdata())
        dark_pixels = pixels.count(0)
        light_pixels = pixels.count(255)
        
        # Fallback if binary image is uniform
        if dark_pixels == 0 or light_pixels == 0:
            return analyze_by_shape_position(arrow_region)
        
        # Analyze rows to find arrow pattern
        rows_data = []
        for y in range(binary_img.height):
            row_start = y * binary_img.width
            row_end = row_start + binary_img.width
            row_pixels = pixels[row_start:row_end]
            dark_pixels_in_row = row_pixels.count(0)
            rows_data.append(dark_pixels_in_row)
        
        if len(rows_data) < 3:
            return 'unknown'
            
        # Split into sections
        third = len(rows_data) // 3
        top_section = rows_data[:third]
        middle_section = rows_data[third:2*third]
        bottom_section = rows_data[2*third:]
        
        top_avg = sum(top_section) / len(top_section) if top_section else 0
        middle_avg = sum(middle_section) / len(middle_section) if middle_section else 0
        bottom_avg = sum(bottom_section) / len(bottom_section) if bottom_section else 0
        
        # Check if middle section dominates (common case for UI arrows)
        middle_dominance = middle_avg - max(top_avg, bottom_avg)
        
        if middle_dominance > 1.0:
            # Analyze middle section pattern
            middle_start = third
            middle_end = 2 * third
            middle_rows = rows_data[middle_start:middle_end]
            
            if len(middle_rows) >= 3:
                # Check if pixels increase toward bottom (downward arrow) or top (upward arrow)
                first_half_avg = sum(middle_rows[:len(middle_rows)//2]) / max(1, len(middle_rows)//2)
                second_half_avg = sum(middle_rows[len(middle_rows)//2:]) / max(1, len(middle_rows) - len(middle_rows)//2)
                
                if second_half_avg > first_half_avg + 0.2:
                    return 'down'  # Expanding downward = down arrow
                elif first_half_avg > second_half_avg + 0.2:
                    return 'up'    # Expanding upward = up arrow
                else:
                    # Use peak position as fallback
                    max_pixels_row = max(range(len(middle_rows)), key=lambda i: middle_rows[i])
                    relative_position = max_pixels_row / len(middle_rows)
                    
                    if relative_position < 0.3:
                        return 'down'
                    elif relative_position > 0.7:
                        return 'up'
                    else:
                        return 'unknown'
            else:
                return 'unknown'
        else:
            # Standard top/bottom analysis
            up_score = (top_avg + middle_avg) - bottom_avg
            down_score = (bottom_avg + middle_avg) - top_avg
            
            if up_score > 0.5:
                return 'up'
            elif down_score > 0.5:
                return 'down'
            else:
                return 'unknown'
                
    except Exception as e:
        logger.error(f"Error analyzing arrow direction: {e}")
        return 'unknown'


def analyze_by_shape_position(arrow_region):
    """
    Fallback method: analyze arrow direction by looking at the vertical position 
    of the darkest/most contrasted pixels.
    
    Args:
        arrow_region: PIL Image of the arrow region
        
    Returns:
        str: 'up', 'down', or 'unknown' based on arrow direction
    """
    try:
        pixels = list(arrow_region.getdata())
        width, height = arrow_region.size
        
        # Find contrasted pixels
        min_pixel = min(pixels)
        max_pixel = max(pixels)
        contrast_threshold = min_pixel + (max_pixel - min_pixel) * 0.3
        
        contrasted_positions = []
        for i, pixel in enumerate(pixels):
            if pixel <= contrast_threshold:
                y = i // width
                contrasted_positions.append(y)
        
        if not contrasted_positions:
            return 'unknown'
        
        # Analyze vertical distribution
        avg_y = sum(contrasted_positions) / len(contrasted_positions)
        center_y = height / 2
        
        if avg_y < center_y * 0.7:
            return 'up'
        elif avg_y > center_y * 1.3:
            return 'down'
        else:
            return 'unknown'
            
    except Exception as e:
        logger.error(f"Error in shape position analysis: {e}")
        return 'unknown'


def toggle_element_visibility(driver, target_text, mode, exact_match=False):
    """
    Scrolls to the given element, checks its arrow direction, and toggles visibility.

    Args:
        driver: Appium WebDriver instance.
        target_text (str): Text of the target list item.
        mode (str): "show" to expand, "hide" to collapse.

    Returns:
        bool: True if no further action is needed or action was performed successfully, False otherwise.

    Step-by-step:
    1) Scroll the list until the element with `target_text` is visible.
    2) Locate the element and get its XPath and screen bounds.
    3) Take a full-screen screenshot.
    4) Crop the screenshot to the element bounds.
    5) Run arrow-direction detection on the cropped element.
    6) Decide whether a click is needed based on `mode` and detected arrow.
    7) If needed, click the element and wait for the UI to update.
    8) Return the final success/failure boolean.
    """
    # Input validation
    if not driver:
        raise ValueError("Driver cannot be None")
    if not target_text or not target_text.strip():
        raise ValueError("Target text cannot be empty")
    if not mode or mode.lower() not in ["show", "hide"]:
        raise ValueError("Mode must be 'show' or 'hide'")
    
    logger.info(f"[START] toggle_element_visibility('{target_text}', mode='{mode}')")

    # Step 1: Ensure the target text is visible by scrolling to it
    # - If scroll_to_text returns False, we couldn't locate the item on the list.
    if not scroll_to_text(driver, target_text, exact_match):
        logger.error(f"Could not find '{target_text}' after scrolling.")
        return False

    # Step 2: Find the element XPath and bounds for later actions (click or cropping)
    xpath, bounds = get_xpath_and_bounds_for_text_item(driver, target_text)
    if not xpath:
        logger.error(f"XPath for '{target_text}' not found.")
        return False

    logger.info(f"Element located. XPath: {xpath}, Bounds: {bounds}")

    # Step 3: Capture a full-screen screenshot (so we can crop the element out)
    screenshot_name = f"element_{target_text.replace(' ', '_')}"
    screenshot_path = take_screenshot(driver, screenshot_name)

    # Prepare defaults for steps 4 & 5
    current_arrow = "unknown"   # default when arrow detection isn't available
    cropped_path = None

    # Step 4: If screenshot succeeded, crop the element using its bounds
    if screenshot_path:
        cropped_name = f"{screenshot_name}_cropped"
        cropped_path = crop_element_from_screenshot(screenshot_path, bounds, cropped_name)

        # Step 5: If crop succeeded, detect the arrow direction (up/down/unknown)
        if cropped_path:
            current_arrow = check_arrow_direction(cropped_path)

        # Log screenshot/crop/arrow details for debugging
        logger.info(f"Screenshot saved: {screenshot_path}")
        if cropped_path:
            logger.info(f"Cropped element saved: {cropped_path}")
        logger.info(f"Detected arrow direction: {current_arrow}")
    else:
        # If screenshot failed, we still proceed but arrow remains 'unknown'
        logger.warning("Screenshot failed; arrow detection skipped.")

    # Step 6: Decide whether a click is required based on requested mode and arrow
    action_needed = False

    if mode.lower() == "show":
        # - If arrow points 'down', element is collapsed -> click to expand.
        # - If arrow points 'up', it's already expanded -> no action.
        if current_arrow == "down":
            logger.info("Element collapsed (down arrow). Will click to expand.")
            action_needed = True
        elif current_arrow == "up":
            logger.info("Element already expanded (up arrow). No action needed.")
            return True
        else:
            logger.warning("Unknown arrow direction; cannot safely determine expand state.")
            return False

    elif mode.lower() == "hide":
        # - If arrow points 'up', element is expanded -> click to collapse.
        # - If arrow points 'down', it's already collapsed -> no action.
        if current_arrow == "up":
            logger.info("Element expanded (up arrow). Will click to collapse.")
            action_needed = True
        elif current_arrow == "down":
            logger.info("Element already collapsed (down arrow). No action needed.")
            return True
        else:
            logger.warning("Unknown arrow direction; cannot safely determine collapse state.")
            return False

    else:
        logger.error(f"Invalid mode '{mode}'. Use 'show' or 'hide'.")
        return False

    # Step 7: Perform the click if needed and wait a short time for UI update
    if action_needed:
        try:
            element = driver.find_element(AppiumBy.XPATH, xpath)
            element.click()
            time.sleep(SCROLL_DELAY)  # small pause for UI to reflect change
            logger.info(f"Clicked element '{target_text}' to {mode}.")
            return True
        except Exception as click_error:
            logger.error(f"Failed to click element '{target_text}': {click_error}")
            return False

    # Step 8: If no action needed to reach this point, return True
    return True


def launch_pcts_test_case(driver, main_test_case_name, test_case_name, exact_match=False):
    """
    Launches a PCTS test case by expanding the main test case and clicking the sub-test case.

    Args:
        driver: Appium WebDriver instance.
        main_test_case_name (str): Name of the main test case section to expand.
        test_case_name (str): Name of the specific sub-test case to click.

    Step-by-step:
    1) Expand (show) the main test case section using toggle_element_visibility().
    2) If expansion succeeds, scroll to locate the desired sub-test case.
    3) If the sub-test case is visible, retrieve its XPath and bounds.
    4) Click on the sub-test case element to launch it.
    5) Log success/failure at each stage for debugging.
    """
    logger.info(f"[START] Launching PCTS test case '{main_test_case_name}' → '{test_case_name}'")

    # Step 1: Expand the main test case section
    if toggle_element_visibility(driver, main_test_case_name, "show", exact_match):
        logger.info(f"Main test case '{main_test_case_name}' expanded successfully.")

        # Step 2: Scroll until the sub-test case is visible
        if scroll_to_text(driver, test_case_name, False):
            logger.info(f"Sub-test case '{test_case_name}' found on screen.")

            # Step 3: Get the XPath and bounds of the sub-test case element
            xpath, bounds = get_xpath_and_bounds_for_text_item(driver, test_case_name)
            if xpath:
                logger.info(f"Clicking sub-test case at bounds: {bounds}")

                # Step 4: Click the sub-test case element
                try:
                    driver.find_element(AppiumBy.XPATH, xpath).click()
                    logger.info(f"Successfully clicked sub-test case '{test_case_name}'.")
                    return True
                except Exception as click_error:
                    logger.error(f"Failed to click '{test_case_name}': {click_error}")
                    return False
            else:
                logger.error(f"XPath for sub-test case '{test_case_name}' not found.")
                return False
        else:
            logger.error(f"Sub-test case '{test_case_name}' not found after scrolling.")
            return False
    else:
        logger.error(f"Failed to expand main test case '{main_test_case_name}'.")
        return False

# =============================================================================
# PCTS Helper Function
# =============================================================================

def pcts_scroll_to_top(driver):
    return scroll_to_top(driver, PCTS_SCROLLABLE_RESOURCE_LIST_ID)

def pcts_get_visible_top_list_items(driver):
    """Get visible main category items (top-level list items)"""
    return get_visible_texts_from_resource(driver, PCTS_TOP_LIST_RESOURCE_ID)

def pcts_get_visible_sub_list_items(driver):
    """Get visible sub-category items (expanded list items)"""
    return get_visible_texts_from_resource(driver, PCTS_SUB_LIST_RESOURCE_ID)

