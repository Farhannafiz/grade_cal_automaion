import time
import logging
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestGradeCalculator(unittest.TestCase):
    def setUp(self):
        """Initial setup of the WebDriver with logging configuration."""
        logging.basicConfig(level=logging.INFO)
        self.driver = webdriver.Chrome()
        self.driver.get("https://softekogradecalculator.netlify.app/calculator/grade-calculator")
        self.clear_all_rows()

    def tearDown(self):
        """Tear down the WebDriver session."""
        self.driver.quit()

    def clear_all_rows(self):
        """Utility function to clear all rows before starting a test."""
        try:
            reset_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Reset/Clear']"))
            )
            reset_button.click()
            time.sleep(1)  # Allow time for the reset operation to complete
        except Exception:
            logging.info("No rows to clear or reset button not clickable.")

    def select_grade_type(self, grade_type: str):
        """Select a grade type button (Percentage, Letter, Points)."""
        driver = self.driver
        grade_type_buttons = {
            "Percentage": (By.XPATH, "//button[contains(text(), 'Percentage')]"),
            "Letter": (By.XPATH, "//button[contains(text(), 'Letter')]"),
            "Points": (By.XPATH, "//button[contains(text(), 'Points')]")
        }

        button_locator = grade_type_buttons.get(grade_type)
        if button_locator:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button_locator)).click()
            logging.info(f"Selected grade type: {grade_type}")
        else:
            raise ValueError(f"Invalid grade type: {grade_type}")

    def add_row(self, task: str, grade: str, weight: int = 0, max_grade: int = None):
        """Utility method to add a row with task, grade, and weight data."""
        driver = self.driver
        add_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='+ Add new row']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
        driver.execute_script("arguments[0].click();", add_button)
        time.sleep(1)  # Wait for the row to be added
        self.fill_details(task, grade, weight, max_grade)

    def fill_details(self, task: str, grade: str, weight: int = 0, max_grade: int = None):
        """Fill in the details of the new row, handling different grade types."""
        driver = self.driver
        task_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='e.g Assignment']")
        task_inputs[-1].clear()
        task_inputs[-1].send_keys(task)

        grade_elements = driver.find_elements(By.CSS_SELECTOR, "select[name*='rows'][name*='grade'], input[name*='rows'][name*='grade']")
        if grade_elements[-1].tag_name == 'select':
            # It's a dropdown for letter grades
            grade_elements[-1].send_keys(grade)
        else:
            # It's an input for percentage or points
            grade_elements[-1].clear()
            grade_elements[-1].send_keys(str(grade))

        if max_grade is not None:
            max_grade_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='maxGrade']")
            max_grade_inputs[-1].clear()
            max_grade_inputs[-1].send_keys(str(max_grade))
        else:
            weight_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='weight']")
            weight_inputs[-1].clear()
            weight_inputs[-1].send_keys(str(weight))

    def test_percentage_grade_type(self):
        """Test add/reset/delete operations for Percentage grade type."""
        self.run_tests_for_grade_type("Percentage", [("Assignment", 90, 25), ("Exam", 85, 30), ("Project", 70, 15)])

    def test_letter_grade_type(self):
        """Test add/reset/delete operations for Letter grade type."""
        self.run_tests_for_grade_type("Letter", [("Presentation", "A", 20), ("Quiz", "B+", 10), ("Report", "C", 20)])

    def test_points_grade_type(self):
        """Test add/reset/delete operations for Points grade type."""
        self.run_tests_for_grade_type("Points", [("Task 1", 80, 100), ("Task 2", 75, 90), ("Task 3", 90, 100)])

    def run_tests_for_grade_type(self, grade_type: str, tasks):
        """Add, reset, and delete rows for the given grade type."""
        driver = self.driver
        self.select_grade_type(grade_type)

        # Count initial rows
        try:
            form = driver.find_element(By.CSS_SELECTOR, "form.flex.flex-col.gap-2")
            initial_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.gap-3.justify-start"))
            logging.info(f"Initial rows count for {grade_type}: {initial_rows}")
        except Exception as e:
            logging.error(f"Error counting initial rows for {grade_type}: {str(e)}")
            driver.save_screenshot(f"initial_rows_error_{grade_type.lower()}.png")
            raise

        # Add the specified rows
        for task_data in tasks:
            if grade_type == "Points":
                task, grade, max_grade = task_data
                self.add_row(task, grade, max_grade=max_grade)
            else:
                task, grade, weight = task_data
                self.add_row(task, grade, weight)

        # Verify the number of added rows
        WebDriverWait(driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.gap-3.justify-start")) == initial_rows + len(tasks)
        )
        added_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.gap-3.justify-start"))
        expected_rows = initial_rows + len(tasks)
        assert added_rows == expected_rows, f"Expected {expected_rows} rows but found {added_rows}"
        logging.info(f"Rows after addition for {grade_type}: {added_rows}")

        # Click the "Reset/Clear" button to remove all rows
        reset_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Reset/Clear']"))
        )
        reset_button.click()
        time.sleep(1)

        # Verify the rows are reset to the initial state
        WebDriverWait(driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.gap-3.justify-start")) == initial_rows
        )
        cleared_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.gap-3.justify-start"))
        assert cleared_rows == initial_rows, f"Expected {initial_rows} rows after reset for {grade_type} but got {cleared_rows}"
        logging.info(f"Rows after reset for {grade_type}: {cleared_rows}")


if __name__ == "__main__":
    unittest.main()
