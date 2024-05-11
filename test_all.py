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

    def select_grade_type(self, grade_type: str):
        """Select a grade type button (Percentage, Letter, Points)."""
        driver = self.driver
        grade_type_buttons = {
            "Percentage": (By.XPATH, "//button[contains(text(), 'Percentage')]"),
            "Letter": (By.XPATH, "//button[contains(text(), 'Letter')]"),
            "Points": (By.XPATH, "//button[contains(text(), 'Points')]")
        }

        if grade_type in grade_type_buttons:
            button_locator = grade_type_buttons[grade_type]
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(button_locator)
                )
                driver.execute_script("arguments[0].click();", button)
                logging.info(f"Selected grade type: {grade_type}")
            except Exception as e:
                driver.save_screenshot(f"select_{grade_type.lower()}_error.png")
                logging.error(f"Failed to select grade type '{grade_type}': {str(e)}")
                raise
        else:
            raise ValueError(f"Invalid grade type: {grade_type}")

    def add_row(self, task: str, grade: str, weight: int = 0, max_grade: int = None):
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
        self.fill_details(task, grade, weight, max_grade)

    def fill_details(self, task: str, grade: str, weight: int = 0, max_grade: int = None):
        """Fill in the details of the new row, handling different grade types."""
        driver = self.driver
        try:
            # Access the last input fields to enter the data
            task_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='e.g Assignment']")
            task_inputs[-1].clear()
            task_inputs[-1].send_keys(task)

            # For letter grades use a select input, otherwise use normal input
            grade_elements = driver.find_elements(By.CSS_SELECTOR, "select[name*='rows'][name*='grade']")
            if grade_elements:  # Letter grade case
                grade_elements[-1].send_keys(grade)
            else:  # Numeric or point grades
                grade_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='grade']")
                grade_inputs[-1].clear()
                grade_inputs[-1].send_keys(str(grade))

            # Handle weight or max grade based on grade type
            weight_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='weight']")
            if weight_inputs:  # Weight (for percentage or letter grade types)
                weight_inputs[-1].clear()
                weight_inputs[-1].send_keys(str(weight))
            else:  # Max grade (specific to the points grade type)
                max_grade_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='maxGrade']")
                max_grade_inputs[-1].clear()
                max_grade_inputs[-1].send_keys(str(max_grade))

            logging.info(f"Data entered successfully: {task}, {grade}, {weight}, {max_grade}")
        except Exception as e:
            logging.error(f"Error entering data in the new row: {str(e)}")
            driver.save_screenshot("data_input_error.png")
            raise

    def run_tests_for_grade_type(self, grade_type: str, tasks):
        """Add, reset, and delete rows for the given grade type."""
        driver = self.driver
        self.select_grade_type(grade_type)

        # Count initial rows
        try:
            form = driver.find_element(By.CSS_SELECTOR, "form.flex.flex-col.gap-2")
            initial_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
            logging.info(f"Initial rows count for {grade_type}: {initial_rows}")
        except Exception as e:
            logging.error(f"Error counting initial rows for {grade_type}: {str(e)}")
            driver.save_screenshot(f"initial_rows_error_{grade_type.lower()}.png")
            raise

        # Add the specified rows, handle extra parameter for points
        for task_data in tasks:
            if grade_type == "Points":
                task, grade, max_grade = task_data
                self.add_row(task, grade, max_grade=max_grade)
            else:
                task, grade, weight = task_data
                self.add_row(task, grade, weight)

        # Verify the number of added rows
        WebDriverWait(driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row")) == initial_rows + len(tasks)
        )
        added_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        expected_rows = initial_rows + len(tasks)
        assert added_rows == expected_rows, f"Expected {expected_rows} rows but found {added_rows}"
        logging.info(f"Rows after addition for {grade_type}: {added_rows}")

        # Click the "Reset/Clear" button to remove all rows
        try:
            reset_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Reset/Clear']"))
            )
            driver.execute_script("arguments[0].click();", reset_button)
            logging.info(f"Clicked 'Reset/Clear' button for {grade_type}.")
            time.sleep(1)
        except Exception as e:
            logging.error(f"Failed to click 'Reset/Clear' button for {grade_type}: {str(e)}")
            driver.save_screenshot(f"failed_reset_click_{grade_type.lower()}.png")
            raise

        # Verify the rows are reset to the initial state
        WebDriverWait(driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row")) == initial_rows
        )
        cleared_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        assert cleared_rows == initial_rows, f"Expected {initial_rows} rows after reset for {grade_type} but got {cleared_rows}"
        logging.info(f"Rows after reset for {grade_type}: {cleared_rows}")

    def test_all_grade_types(self):
        """Test add/reset/delete operations across different grade types."""
        grade_types_and_tasks = {
            "Percentage": [("Assignment", 90, 25), ("Exam", 85, 30), ("Project", 70, 15)],
            "Letter": [("Presentation", "A", 20), ("Quiz", "B+", 10), ("Report", "C", 20)],
            "Points": [("Task 1", 80, 100), ("Task 2", 75, 90), ("Task 3", 90, 100)],
        }

        for grade_type, tasks in grade_types_and_tasks.items():
            self.run_tests_for_grade_type(grade_type, tasks)
