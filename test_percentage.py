import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestGradeCalculator:
    def setup_method(self, method):
        """Initial setup of the WebDriver with logging configuration."""
        logging.basicConfig(level=logging.INFO)
        self.driver = webdriver.Chrome()
        self.driver.get("https://softekogradecalculator.netlify.app/calculator/grade-calculator")

    def teardown_method(self, method):
        """Tear down the WebDriver session."""
        self.driver.quit()

    def add_row(self, task: str, grade: int, weight: int):
        """Utility method to add a row with task, grade, and weight data."""
        driver = self.driver

        # Click the "+ Add new row" button using JavaScript to avoid click interception
        try:
            add_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='+ Add new row']"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
            driver.execute_script("arguments[0].click();", add_button)
            logging.info("Clicked '+ Add new row' button successfully using JavaScript.")
            time.sleep(0.5)  # Wait for the row to be added
        except Exception as e:
            driver.save_screenshot("failed_click.png")
            logging.error(f"Failed to click '+ Add new row': {str(e)}")
            raise

        # Enter data into the newly created row
        self.fill_details(task, grade, weight)

    def fill_details(self, task: str, grade: int, weight: int):
        """Fill in the details of the new row."""
        driver = self.driver
        try:
            # Access the last input fields to enter the data
            task_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='e.g Assignment']")
            task_inputs[-1].clear()
            task_inputs[-1].send_keys(task)

            grade_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='grade']")
            grade_inputs[-1].clear()
            grade_inputs[-1].send_keys(str(grade))

            weight_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='weight']")
            weight_inputs[-1].clear()
            weight_inputs[-1].send_keys(str(weight))

            logging.info(f"Data entered successfully: {task}, {grade}, {weight}")
        except Exception as e:
            logging.error(f"Error entering data in the new row: {str(e)}")
            driver.save_screenshot("data_input_error.png")
            raise

    def test_add_and_reset_multiple_times(self):
        """Test method to add and reset rows multiple times, verifying consistency."""
        driver = self.driver

        # Count initial rows by selecting all div elements inside the form
        try:
            form = driver.find_element(By.CSS_SELECTOR, "form[class='flex flex-col gap-2']")
            initial_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
            logging.info(f"Initial rows count: {initial_rows}")
        except Exception as e:
            logging.error(f"Error counting initial rows: {str(e)}")
            driver.save_screenshot("initial_rows_error.png")
            raise

        # Perform multiple add-and-reset cycles
        cycles = 2  # Number of times to add rows and then reset
        rows_per_cycle = 4  # Number of rows to add in each cycle

        for cycle in range(cycles):
            tasks = [("Homework", 80, 15), ("Quiz", 90, 10), ("Midterm", 75, 20), ("Final", 85, 30)]
            for task, grade, weight in tasks:
                self.add_row(task, grade, weight)

            # Allow time for rows to be added asynchronously
            time.sleep(2)

            # Verify that the expected number of rows has been added
            try:
                added_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
                expected_rows = initial_rows + rows_per_cycle
                assert added_rows == expected_rows, f"Expected {expected_rows} rows but found {added_rows}"
                logging.info(f"Rows after addition in cycle {cycle + 1}: {added_rows}")
            except AssertionError as e:
                logging.error(f"Assertion error in cycle {cycle + 1}: {str(e)}")
                driver.save_screenshot(f"row_count_error_cycle_{cycle + 1}.png")
                raise

            # Locate and click the "Reset/Clear" button
            try:
                reset_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Reset/Clear']"))
                )
                reset_button.click()
                logging.info(f"Clicked 'Reset/Clear' button successfully in cycle {cycle + 1}.")
            except Exception as e:
                logging.error(f"Failed to click 'Reset/Clear' button in cycle {cycle + 1}: {str(e)}")
                driver.save_screenshot(f"failed_reset_click_cycle_{cycle + 1}.png")
                raise

            # Verify that the rows are back to the initial state
            try:
                cleared_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
                assert cleared_rows == initial_rows, f"Expected {initial_rows} rows after reset in cycle {cycle + 1} but got {cleared_rows}"
                logging.info(f"Rows after reset in cycle {cycle + 1}: {cleared_rows}")
            except AssertionError as e:
                logging.error(f"Assertion error after reset in cycle {cycle + 1}: {str(e)}")
                driver.save_screenshot(f"reset_error_cycle_{cycle + 1}.png")
                raise

    def test_delete_single_row(self):
        """Test method to add and then delete rows using the cross button, verifying each operation."""
        driver = self.driver

        # Count initial rows by selecting all div elements inside the form
        try:
            form = driver.find_element(By.CSS_SELECTOR, "form[class='flex flex-col gap-2']")
            initial_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
            logging.info(f"Initial rows count: {initial_rows}")
        except Exception as e:
            logging.error(f"Error counting initial rows: {str(e)}")
            driver.save_screenshot("initial_rows_error.png")
            raise

        # Add rows with unique tasks
        tasks = [("Project", 70, 25), ("Lab Work", 85, 20), ("Term Paper", 65, 15), ("Presentation", 80, 25)]

        for task, grade, weight in tasks:
            self.add_row(task, grade, weight)

        # Explicitly wait for the rows to be fully added and interactable
        WebDriverWait(driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row")) == initial_rows + len(tasks)
        )

        # Verify that the expected number of rows has been added
        added_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        expected_rows = initial_rows + len(tasks)
        assert added_rows == expected_rows, f"Expected {expected_rows} rows but found {added_rows}"
        logging.info(f"Rows after addition: {added_rows}")

        # Click the "cross" button to delete the first added row
        try:
            # Adjusted XPath to select the delete button inside the first div row
            delete_button = form.find_element(By.XPATH, "//div[contains(@class,'flex flex-col gap-2')]//div[1]//button[1]")
            driver.execute_script("arguments[0].click();", delete_button)
            logging.info("Deleted the first row successfully.")
            time.sleep(1)  # Allow time to visually confirm deletion
        except Exception as e:
            logging.error(f"Failed to locate the delete button: {str(e)}")
            driver.save_screenshot("delete_button_error.png")
            raise

        # Wait for the row to be removed and verify
        WebDriverWait(driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row")) == expected_rows - 1
        )
        remaining_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        expected_remaining = expected_rows - 1
        assert remaining_rows == expected_remaining, f"Expected {expected_remaining} rows after deletion but found {remaining_rows}"
        logging.info(f"Rows after deletion: {remaining_rows}")
