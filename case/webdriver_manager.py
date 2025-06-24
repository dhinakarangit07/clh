import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('window-size=1920,1080')
        options.add_argument('--no-sandbox')  # important for headless Chrome on servers
        options.add_argument('--disable-dev-shm-usage')  # avoid limited /dev/shm on container systems
        options.add_argument('--log-level=3')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # Set webdriver-manager cache path to /tmp
        os.environ['WDM_LOCAL'] = '1'
        os.environ['WDM_CACHE_DIR'] = '/tmp'

        chrome_service = Service(ChromeDriverManager().install())
        _driver = webdriver.Chrome(service=chrome_service, options=options)
        _driver.set_page_load_timeout(20)
        _driver.get("https://services.ecourts.gov.in/")
    
    return _driver

def quit_driver():
    global _driver
    if _driver is not None:
        _driver.quit()
        _driver = None
