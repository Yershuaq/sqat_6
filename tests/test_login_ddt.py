import pytest
import openpyxl
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_data_from_excel(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    data = []
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        username = row[0]
        password = row[1]
        expected = row[2]
        if expected: 
            data.append((username, password, expected))
            
    return data

@pytest.mark.parametrize("username, password, expected_outcome", get_data_from_excel("test_data.xlsx"))
def test_login_ddt(driver, username, password, expected_outcome):
    logging.info(f"TEST DATA: User='{username}', Pass='{password}', Expect='{expected_outcome}'")
    
    driver.get("https://opensource-demo.orangehrmlive.com/")
    
    driver.find_element(By.NAME, "username").send_keys(username if username else "")
    driver.find_element(By.NAME, "password").send_keys(password if password else "")
    driver.find_element(By.TAG_NAME, "button").click()
    
    if expected_outcome == "Dashboard":
        logging.info("Проверка: Должен быть успешный вход")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h6[text()='Dashboard']"))
        )
        assert "dashboard" in driver.current_url
        logging.info("RESULT: PASSED (Dashboard loaded)")
        
    else:
        logging.info("Проверка: Должна быть ошибка входа")
        
        error_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//p[contains(@class, 'alert')] | //span[contains(@class, 'error')]"))
        )
        assert error_element.is_displayed()
        logging.info("RESULT: PASSED (Error message displayed)")