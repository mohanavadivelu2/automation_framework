from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException


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
