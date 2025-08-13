from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException,WebDriverException

def get_all_button_texts(driver):
    """Retrieve text values of all android.widget.Button elements."""
    buttons = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.Button")
    return [btn.text for btn in buttons if btn.text.strip() != ""]


def click_button_and_return_xpath(driver, target_text):
    """Click a button by text and return its XPath."""
    try:
        xpath = f"//android.widget.Button[@text='{target_text}']"
        element = driver.find_element(AppiumBy.XPATH, xpath)
        element.click()
        print(f"[INFO] Clicked button with text: '{target_text}'")
        return xpath
    except NoSuchElementException:
        print(f"[WARN] No button found with text: '{target_text}'")
        return None

def button_click_by_name(driver, target_text):
    """
    Find a button by its text and click it.
    """
    all_texts = get_all_button_texts(driver)
    if target_text in all_texts:
        xpath_used = click_button_and_return_xpath(driver, target_text)
        if xpath_used:
            return True, f"Button '{target_text}' clicked."
    return False, f"Button '{target_text}' not found."

def click_button_by_match(driver, text_to_find, text_to_click_success="YES", text_to_click_failure="NO", exact_match=False):
    """
    Search for `text_to_find` on the page and click either the success or failure element.

    Args:
        driver: Appium WebDriver instance.
        text_to_find (str): Text to search for on the page.
        text_to_click_success (str): Text of the button to click if found (default: "YES").
        text_to_click_failure (str): Text of the button to click if not found (default: "NO").
        exact_match (bool): True for exact text match, False for substring match.

    Returns:
        bool: True if the click action is successful, False otherwise.
    """
    if not driver:
        raise ValueError("Driver instance is required.")
    if not isinstance(text_to_find, str) or not text_to_find.strip():
        raise ValueError("text_to_find must be a non-empty string.")

    def build_xpath(text, is_exact):
        return (
            f"//*[normalize-space(@text)='{text}']"
            if is_exact
            else f"//*[contains(normalize-space(@text), '{text}')]"
        )

    try:
        # Search for the target text
        search_xpath = build_xpath(text_to_find.strip(), exact_match)
        driver.find_element(AppiumBy.XPATH, search_xpath)
        target_to_click = text_to_click_success
        print(f"[INFO] Found target text: '{text_to_find}'. Clicking '{text_to_click_success}'.")
    except NoSuchElementException:
        target_to_click = text_to_click_failure
        print(f"[WARN] Target text '{text_to_find}' not found. Clicking '{text_to_click_failure}'.")

    try:
        # Always click with exact match to avoid ambiguity
        click_xpath = build_xpath(target_to_click.strip(), True)
        element = driver.find_element(AppiumBy.XPATH, click_xpath)
        element.click()
        print(f"[INFO] Clicked element: '{target_to_click}'.")
        return True
    except NoSuchElementException:
        print(f"[ERROR] Could not find element to click: '{target_to_click}'.")
        return False
    except WebDriverException as e:
        print(f"[ERROR] WebDriver error while clicking '{target_to_click}': {e}")
        return False