from selenium.webdriver.chrome.options import Options

chrome_driver_path = "./service_apps/chrome_driver/chromedriver.exe"
ubuntu_chrome_driver_path = "./service_apps/chrome_driver/chromedriver"

options = Options()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
