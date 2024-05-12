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
    """Test if the input field prevents invalid data from being accepted."""
    invalid_task = "123416283182"
    invalid_grade = "Invalid Grade"
    invalid_weight = "akjsdhkjashdkj"

    # Add row with invalid data
    add_row(driver, invalid_task, invalid_grade, invalid_weight)

    # Find the input fields again to verify their content
    inputs = driver.find_elements(By.TAG_NAME, "input")

    # Adjust the indices based on the actual layout of your form
    task_input = inputs[0]
    grade_input = inputs[1]
    weight_input = inputs[2]

    # Check if any field still holds the invalid values
    is_invalid_task_retained = task_input.get_attribute("value") == invalid_task
    is_invalid_grade_retained = grade_input.get_attribute("value") == invalid_grade
    is_invalid_weight_retained = weight_input.get_attribute("value") == invalid_weight

    # Test should pass only if none of the invalid inputs are retained
    if is_invalid_task_retained or is_invalid_grade_retained or is_invalid_weight_retained:
        pytest.fail("Input fields are retaining invalid values.")
    else:
        print("Test passed: Input fields did not retain invalid values.")

