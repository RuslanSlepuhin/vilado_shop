from selenium.webdriver.chrome.options import Options
from config.os_system import os_system

chrome_driver_path = "./service_apps/chrome_driver/chromedriver.exe" if os_system.lower() == 'windows' else "root/vilado_shop/service_apps/chrome_driver/Ubuntu/chromedriver"
ubuntu_chrome_driver_path = "./service_apps/chrome_driver/chromedriver"

options = Options()
if os_system == 'ubuntu':
    options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
