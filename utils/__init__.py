from selenium.webdriver.chrome.service import Service
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument("--remote-debugging-port=8000")
driver = webdriver.Chrome(service=Service("./chromedriver"), options=options)
