from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from utils import driver


def wait_until_located(by=By.CLASS_NAME, search="Header_Logo__ahh3T"):
    return WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((by, search)))
