import time
import pytest
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestGradeCalculator:
    @pytest.fixture(autouse=True)
    def setup_method(self, request):
        logging.basicConfig(level=logging.INFO)
        self.driver = webdriver.Chrome()
        self.driver.get("https://softekogradecalculator.netlify.app/calculator/grade-calculator")
        def teardown():
            self.driver.quit()
        request.addfinalizer(teardown)

    def add_row(self, task: str, grade: int, weight: int):
        try:
            add_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='+ Add new row']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
            self.driver.execute_script("arguments[0].click();", add_button)
            time.sleep(0.5)
        except Exception as e:
            self.driver.save_screenshot("failed_click.png")
            logging.error(f"Failed to click '+ Add new row': {str(e)}")
            raise

        self.fill_details(task, grade, weight)

    def fill_details(self, task: str, grade: int, weight: int):
        try:
            task_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[placeholder='e.g Assignment']")
            task_inputs[-1].clear()
            task_inputs[-1].send_keys(task)

            grade_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='grade']")
            grade_inputs[-1].clear()
            grade_inputs[-1].send_keys(str(grade))

            weight_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='weight']")
            weight_inputs[-1].clear()
            weight_inputs[-1].send_keys(str(weight))
        except Exception as e:
            self.driver.save_screenshot("data_input_error.png")
            logging.error(f"Error entering data in the new row: {str(e)}")
            raise

    def test_add_and_reset_multiple_times(self):
        form = self.driver.find_element(By.CSS_SELECTOR, "form[class='flex flex-col gap-2']")
        initial_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        cycles = 2
        rows_per_cycle = 4
        for cycle in range(cycles):
            tasks = [("Homework", 80, 15), ("Quiz", 90, 10), ("Midterm", 75, 20), ("Final", 85, 30)]
            for task, grade, weight in tasks:
                self.add_row(task, grade, weight)
            time.sleep(2)
            added_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
            expected_rows = initial_rows + rows_per_cycle
            assert added_rows == expected_rows
            reset_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Reset/Clear']"))
            )
            reset_button.click()
            cleared_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
            assert cleared_rows == initial_rows

    def test_delete_single_row(self):
        form = self.driver.find_element(By.CSS_SELECTOR, "form[class='flex flex-col gap-2']")
        initial_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        tasks = [("Project", 70, 25), ("Lab Work", 85, 20), ("Term Paper", 65, 15), ("Presentation", 80, 25)]
        for task, grade, weight in tasks:
            self.add_row(task, grade, weight)
        WebDriverWait(self.driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row")) == initial_rows + len(tasks)
        )
        added_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        expected_rows = initial_rows + len(tasks)
        assert added_rows == expected_rows
        delete_button = form.find_element(By.XPATH, "//div[contains(@class,'flex flex-col gap-2')]//div[1]//button[1]")
        self.driver.execute_script("arguments[0].click();", delete_button)
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row")) == expected_rows - 1
        )
        remaining_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        expected_remaining = expected_rows - 1
        assert remaining_rows == expected_remaining

    def test_weight_spin_button(self):
        self.add_row("Weight Spin Test", 50, 50)
        time.sleep(1)  # Ensure the row is added and input is updated
        weight_input = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='weight']")[0]
        self.adjust_weight(0, increase=True, clicks=1)
        assert weight_input.get_attribute("value") == "51", "Value not increased as expected by spin button"
        self.adjust_weight(0, increase=False, clicks=1)
        assert weight_input.get_attribute("value") == "50", "Value not decreased as expected by spin button"

    def adjust_weight(self, row_index, increase=True, clicks=1):
        input_field = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='weight']")[row_index]
        for _ in range(clicks):
            if increase:
                self.driver.execute_script("arguments[0].stepUp();", input_field)
            else:
                self.driver.execute_script("arguments[0].stepDown();", input_field)
            time.sleep(0.1)

