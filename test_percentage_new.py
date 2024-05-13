import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestGradeCalculator:
    def setup_method(self, method):
        logging.basicConfig(level=logging.INFO)
        self.driver = webdriver.Chrome()
        self.driver.get("https://softekogradecalculator.netlify.app/calculator/grade-calculator")

    def teardown_method(self, method):
        self.driver.quit()

    def add_row(self, task: str, grade: int, weight: int):
        driver = self.driver
        try:
            add_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='+ Add new row']"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
            driver.execute_script("arguments[0].click();", add_button)
            time.sleep(0.5)
        except Exception as e:
            driver.save_screenshot("failed_click.png")
            raise
        self.fill_details(task, grade, weight)

    def fill_details(self, task: str, grade: int, weight: int):
        driver = self.driver
        try:
            task_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='e.g Assignment']")
            task_inputs[-1].clear()
            task_inputs[-1].send_keys(task)
            grade_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='grade']")
            grade_inputs[-1].clear()
            grade_inputs[-1].send_keys(str(grade))
            weight_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='weight']")
            weight_inputs[-1].clear()
            weight_inputs[-1].send_keys(str(weight))
        except Exception as e:
            driver.save_screenshot("data_input_error.png")
            raise

    def test_add_and_reset_multiple_times(self):
        driver = self.driver
        form = driver.find_element(By.CSS_SELECTOR, "form[class='flex flex-col gap-2']")
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
            reset_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Reset/Clear']"))
            )
            reset_button.click()
            cleared_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
            assert cleared_rows == initial_rows

    def test_delete_single_row(self):
        driver = self.driver
        form = driver.find_element(By.CSS_SELECTOR, "form[class='flex flex-col gap-2']")
        initial_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        tasks = [("Project", 70, 25), ("Lab Work", 85, 20), ("Term Paper", 65, 15), ("Presentation", 80, 25)]
        for task, grade, weight in tasks:
            self.add_row(task, grade, weight)
        WebDriverWait(driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row")) == initial_rows + len(tasks)
        )
        added_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        expected_rows = initial_rows + len(tasks)
        assert added_rows == expected_rows
        delete_button = form.find_element(By.XPATH, "//div[contains(@class,'flex flex-col gap-2')]//div[1]//button[1]")
        driver.execute_script("arguments[0].click();", delete_button)
        time.sleep(1)
        WebDriverWait(driver, 10).until(
            lambda d: len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row")) == expected_rows - 1
        )
        remaining_rows = len(form.find_elements(By.CSS_SELECTOR, "div.flex.flex-row"))
        expected_remaining = expected_rows - 1
        assert remaining_rows == expected_remaining

    def adjust_weight(self, row_index, increase=True, clicks=1):
        try:
            input_field = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='weight']")[row_index]
            for _ in range(clicks):
                if increase:
                    self.driver.execute_script("arguments[0].stepUp();", input_field)
                else:
                    self.driver.execute_script("arguments[0].stepDown();", input_field)
                time.sleep(0.1)
        except Exception as e:
            self.driver.save_screenshot("adjust_weight_error.png")
            raise

    def test_weight_input_range(self):
        self.add_row("Exam", 85, 50)
        self.adjust_weight(row_index=0, increase=True, clicks=55)
        weight_input = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='weight']")[0]
        assert int(weight_input.get_attribute("value")) <= 100
        self.adjust_weight(row_index=0, increase=False, clicks=110)
        assert int(weight_input.get_attribute("value")) >= 0

def adjust_grade(self, row_index, increase=True, clicks=1):
    try:
        input_field = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='grade']")[row_index]
        for _ in range(clicks):
            if increase:
                self.driver.execute_script("arguments[0].stepUp();", input_field)
            else:
                self.driver.execute_script("arguments[0].stepDown();", input_field)
            time.sleep(0.1)
    except Exception as e:
        self.driver.save_screenshot("adjust_grade_error.png")
        raise

def test_grade_input_range(self):
    self.add_row("Exam", 85, 50)
    self.adjust_grade(row_index=0, increase=True, clicks=15)
    grade_input = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='rows'][name*='grade']")[0]
    assert int(grade_input.get_attribute("value")) <= 100
    self.adjust_grade(row_index=0, increase=False, clicks=90)
    assert int(grade_input.get_attribute("value")) >= 0
