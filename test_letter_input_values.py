import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.get("https://softekogradecalculator.netlify.app/calculator/grade-calculator?type=letter")
    yield driver
    driver.quit()

def wait_for_clickable(driver, locator, timeout=10):
    """Wait for an element to be clickable and return it."""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))

def handle_click(driver, locator):
    """Attempt to click on an element, handling common exceptions."""
    try:
        element = wait_for_clickable(driver, locator)
        element.click()
    except ElementClickInterceptedException:
        # Scroll into view and try again
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
    except StaleElementReferenceException:
        # Retry finding the element and clicking
        element = wait_for_clickable(driver, locator)
        element.click()

def add_row(driver, task, grade, weight):
    """Add a row with specified task, grade, and weight."""
    handle_click(driver, (By.XPATH, "//button[normalize-space()='+ Add new row']"))
    # Wait for inputs to appear and fill them out
    inputs = WebDriverWait(driver, 10).until(lambda d: d.find_elements(By.CSS_SELECTOR, "input[type='text']"))
    selects = driver.find_elements(By.CSS_SELECTOR, "select")
    inputs[0].send_keys(task)
    selects[0].send_keys(grade)
    inputs[1].send_keys(str(weight))

@pytest.mark.parametrize("task, grade, weight", [
    ("Homework", "A", 20),
    ("Quiz", "B+", 15),
    ("Midterm", "A-", 25)
])
def test_add_and_reset_rows(driver, task, grade, weight):
    add_row(driver, task, grade, weight)
    # Add assertions here to check for the expected outcomes or states

def test_invalid_input_data(driver):
    """Test handling of invalid input data."""
    add_row(driver, "123", "Invalid Grade", "abc")  # Intentionally incorrect data types
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "error-message"))
        )
        error_messages = driver.find_elements(By.CLASS_NAME, "error-message")
        assert any(msg.is_displayed() for msg in error_messages), "Expected at least one error message."
    except TimeoutException:
        pytest.fail("Expected error messages did not appear for invalid inputs.")
