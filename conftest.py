# conftest.py
import pytest
from selenium import webdriver

@pytest.fixture(scope="function")
def driver():
    # Setup code
    driver = webdriver.Chrome()
    driver.get("https://softekogradecalculator.netlify.app/calculator/grade-calculator?type=letter")
    yield driver
    driver.quit()
