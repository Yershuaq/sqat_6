import pytest
import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

BS_USER = "bsuser_snXgO6"   
BS_KEY = "LfVoJxUekCp7FdVruKxh"      

BS_REMOTE_URL = f"https://{BS_USER}:{BS_KEY}@hub-cloud.browserstack.com/wd/hub"

def pytest_addoption(parser):
    parser.addoption("--browserstack", action="store_true", help="Run tests on BrowserStack Cloud")

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/execution.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

@pytest.fixture(scope="function")
def driver(request):
    run_in_cloud = request.config.getoption("--browserstack")
    
    if run_in_cloud:
        logging.info(f"--- ЗАПУСК В ОБЛАКЕ (BrowserStack) для {request.node.name} ---")
        
        bstack_options = {
            "os" : "Windows",
            "osVersion" : "11",
            "browserName" : "Firefox",
            "browserVersion" : "latest",
            "projectName" : "Assignment 6",
            "buildName" : "OrangeHRM Build",
            "sessionName" : request.node.name,
            "userName": BS_USER,
            "accessKey": BS_KEY
        }
        
        options = ChromeOptions()
        options.set_capability('bstack:options', bstack_options)
        
        driver = webdriver.Remote(
            command_executor=BS_REMOTE_URL,
            options=options
        )
    else:
        logging.info(f"--- ЗАПУСК ЛОКАЛЬНО (Chrome) для {request.node.name} ---")
        driver = webdriver.Chrome()

    driver.implicitly_wait(10)
    driver.maximize_window()
    
    yield driver
    
    logging.info("--- ЗАВЕРШЕНИЕ ТЕСТА ---")
    driver.quit()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, 'extras', [])
    

    if report.when == 'call' and not item.config.getoption("--browserstack"):
        driver_fixture = item.funcargs.get('driver')
        if driver_fixture:
            screenshot_path = f"screenshots/{item.name}.png"
            if not os.path.exists("reports/screenshots"):
                os.makedirs("reports/screenshots")
            
            driver_fixture.save_screenshot(f"reports/{screenshot_path}")
            
            if pytest_html:
                extras.append(pytest_html.extras.image(screenshot_path))
                report.extras = extras