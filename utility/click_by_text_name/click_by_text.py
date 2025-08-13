import xml.etree.ElementTree as ET
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

def click_by_text(driver, target_text, exact_match=True):
    """
    Click any element (Button, TextView, etc.) by text.
    Parses XML only once for performance and prints all found texts/classes.

    Args:
        driver: Appium driver instance
        target_text: text to search for
        exact_match: True for exact match, False for substring match

    Returns:
        (success: bool, message: str)
    """
    source = driver.page_source
    root = ET.fromstring(source)

    data = []  # Will hold (text, class) pairs
    target_class = None

    for node in root.iter():
        text_val = node.attrib.get("text", "").strip()
        if text_val:
            class_name = node.attrib.get("class", "")
            data.append((text_val, class_name))

            match_found = (
                text_val == target_text if exact_match else target_text in text_val
            )
            if target_class is None and match_found:
                target_class = class_name

    # Print all found texts/classes
    print_texts_and_classes(data)

    if target_class is None:
        return False, f"No element found with text '{target_text}'"

    try:
        if exact_match:
            xpath = f"//{target_class}[@text='{target_text}']"
        else:
            xpath = f"//{target_class}[contains(@text, '{target_text}')]"

        element = driver.find_element(AppiumBy.XPATH, xpath)
        element.click()
        return True, f"Clicked element ({target_class}) with text: '{target_text}'"
    except NoSuchElementException:
        return False, f"Element with text '{target_text}' found in XML but not clickable."


def print_texts_and_classes(data):
    """
    Print all found texts and their classes from the page source.
    """
    print("\n[INFO] Texts and Classes found on page:")
    for text_val, class_name in data:
        print(f"  - Text: '{text_val}' | Class: {class_name}")
