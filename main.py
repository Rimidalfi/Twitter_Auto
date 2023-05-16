import os
import csv
import time
import datetime
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
USERURL = os.getenv("USERURL")
counter = 0
follower_list = []
options = Options()
options.add_experimental_option("detach", True)
start_time = datetime.time(0, 0)
end_time = datetime.time(12, 00)
driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()), options=options)


def button_press(xpath: str, waiting_time=15) -> None:

    button = WebDriverWait(driver, waiting_time).until(
        EC.element_to_be_clickable(('xpath', xpath)))
    button.click()


def text_input(xpath: str, text: str, waiting_time=5) -> None:
    input = WebDriverWait(driver, waiting_time).until(
        EC.presence_of_element_located(('xpath', xpath)))
    input.send_keys(text + Keys.RETURN)


def collect_follower(xpath: str, waiting_time=5):
    links = WebDriverWait(driver, waiting_time).until(
        EC.visibility_of_any_elements_located(('xpath', xpath)))

    for link in links:
        follower = link.text.replace("@", "")
        add_entry_to_csv("csv/new_followers.csv", follower)


def add_entry_to_csv(file_path, new_entry):
    # check if new entry is already in csv
    with open(file_path, 'r', newline='') as csvfile:
        global counter
        csv_r = csv.reader(csvfile)
        """ if first 20 new_entries in DB : hold for 1h """
        if any(new_entry in row for row in csv_r):
            print(f"searching ... 🔍 {counter}")
            counter += 1
        else:
            # if entry not in csv, add it
            with open(file_path, 'a', newline='') as csvfile:
                csv_w = csv.writer(csvfile)
                csv_w.writerow([new_entry])
                print("✨ follower added ✨")


driver.get("https://twitter.com/")
driver.maximize_window()
button_press('//span[text()="Unwesentliche Cookies ablehnen"]')
button_press('//span[text()="Anmelden"]')
text_input('//input[@type="text"]', USERNAME)
text_input('//input[@type="password"]', PASSWORD)
time.sleep(3)
driver.get(USERURL)
# button_press('//span[text()="Profile"]')
button_press('//span[starts-with(text(), "Follower")]')

while True:
    current_time = datetime.datetime.now().time()
    if start_time <= current_time <= end_time:
        # loop runs x min
        start = time.time()
        duration = 5*60
        while (time.time()-start) < duration:
            while counter <= 30:
                collect_follower(
                    '//div[@aria-label="Timeline: Followers"]//span[starts-with(text(), "@")]')
            else:
                driver.execute_script("window.scrollBy(0, 500)")
                counter = 0
                time.sleep(3)
        # refreshes the page to start again from the top of the followers list
        driver.refresh()
        time.sleep(3)
    # waits 1 min to check if condiotion
    print("sleeping ... 😴")
    time.sleep(60)
