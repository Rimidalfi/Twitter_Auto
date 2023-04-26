import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv


load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()), options=options)


def button_press(xpath: str, waiting_time=5) -> None:

    button = WebDriverWait(driver, waiting_time).until(
        EC.element_to_be_clickable(('xpath', xpath)))
    button.click()


def text_input(xpath: str, text: str, waiting_time=5) -> None:
    input = WebDriverWait(driver, waiting_time).until(
        EC.presence_of_element_located(('xpath', xpath)))
    input.send_keys(text + Keys.RETURN)


driver.get("https://twitter.com/")
driver.maximize_window()
button_press('//span[text()="Unwesentliche Cookies ablehnen"]')
button_press('//span[text()="Anmelden"]')
text_input('//input[@type="text"]', USERNAME)
text_input('//input[@type="password"]', PASSWORD)
