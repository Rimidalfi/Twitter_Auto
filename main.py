import os
import json
import time
import datetime
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
import pyperclip
import mysql.connector
from dotenv import load_dotenv


load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
USERURL = os.getenv("USERURL")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_IP = os.getenv("PROXY_IP")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

driver = ""
counter = 0
options = Options()
options.add_experimental_option("detach", True)
seleniumwire_options = {
    'proxy': {
        'http': f'http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_IP}:{PROXY_PORT}',
        'https': f'https://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_IP}:{PROXY_PORT}',
        'verify_ssl': False,
    },
}


def button_press(xpath: str, waiting_time=15) -> None:

    button = WebDriverWait(driver, waiting_time).until(
        EC.element_to_be_clickable(('xpath', xpath)))
    button.click()


def text_input(xpath: str, text: str, waiting_time=5) -> None:
    input = WebDriverWait(driver, waiting_time).until(
        EC.presence_of_element_located(('xpath', xpath)))
    input.send_keys(text + Keys.RETURN)


def clipboard_input(xpath: str, text: str, waiting_time=15) -> None:
    """input formated text with emojis"""
    # copy the text to the clipboard
    pyperclip.copy(text)
    input = WebDriverWait(driver, waiting_time).until(
        EC.presence_of_element_located(('xpath', xpath)))
    # paste the text from the clipboard (with command for macOS)
    input.send_keys(Keys.COMMAND + 'v')
    input.send_keys(Keys.CONTROL + 'v')
    input.send_keys(Keys.RETURN)


def connect_to_db(db_host: str, db_port: str, db_user: str, db_password: str, db_database: str) -> mysql.connector.connection_cext.CMySQLConnection:
    """open connection to database"""
    conn = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_database
    )
    return conn


def close_connection_to_db(conn, cursor) -> None:
    """closes connection to database"""
    cursor.close()
    conn.close()


def adding_followers(conn, cursor, xpath: str, waiting_time=5) -> None:
    links = WebDriverWait(driver, waiting_time).until(
        EC.visibility_of_any_elements_located(('xpath', xpath)))

    for link in links:
        follower = link.text.replace("@", "")
        add_entry_to_db(conn, cursor, follower)


def add_entry_to_db(conn, cursor, new_entrry: str, table: str = "follower", columnname: str = "name") -> None:
    """checks if given entry is already in database. If not makes new entry"""
    global counter
    sql_r = f"SELECT {columnname} FROM {table} WHERE {columnname} = %s"
    sql_w = f"INSERT INTO {table} ({columnname}) VALUES(%s)"
    # checks if entry is already in db

    cursor.execute(sql_r, (new_entrry,))
    # returns tuple if entry is found else returns None
    result = cursor.fetchone()
    if result is not None:
        print(f"searching...🔍 {counter}")
        counter += 1
    else:
        cursor.execute(sql_w, (new_entrry,))
        print("✨ follower added ✨")
        conn.commit()


def collect_followers(collecting_time: int = 3, pixels_scroll: int = 500, start_hours: int = 00, start_min: int = 00, end_hours: int = 12, end_min: int = 00) -> None:
    """collects followers in a given timeframe (infinite loop)"""
    start_time = datetime.time(start_hours, start_min)
    end_time = datetime.time(end_hours, end_min)
    global counter
    while True:
        current_time = datetime.datetime.now().time()
        # during timeframe(start_time - end_time) run loop. loop runs x min (collecting_time)
        if start_time <= current_time <= end_time:
            # open connection to database
            conn = connect_to_db(DB_HOST, DB_PORT, DB_USER,
                                 DB_PASSWORD, DB_DATABASE)
            # creating cursor to interact with database
            cursor = conn.cursor()
            start = time.time()
            duration = collecting_time*60
            # during collecting time collect followers
            while (time.time()-start) < duration:
                # collecting followers as long as counter is below 30
                while counter <= 30:
                    adding_followers(conn, cursor,
                                     '//div[@aria-label="Timeline: Followers"]//span[starts-with(text(), "@")]')
                    time.sleep(0.1)
                else:
                    # scroll to load new followers
                    driver.execute_script(
                        f"window.scrollBy(0, {pixels_scroll})")
                    counter = 0
                    time.sleep(3)
            # refreshes the page to start again from the top of the followers list after 1 hour
            driver.refresh()
            # cursor.close()
            close_connection_to_db(conn, cursor)
            print("sleeping for 56 min ... 😴")
            time.sleep(56*60)
        # waits 1 min to check if condition
        print("sleeping ... 😴")
        time.sleep(60)


def message_follower(follower: str, msg: str) -> None:
    """write a direct message to targeted account"""
    driver.get(f"https://twitter.com/{follower}")
    button_press("//div[@aria-label='Message']")
    clipboard_input("//div[@role='textbox']", msg, waiting_time=15)


def get_meta(follower: str, xpath: str, waiting_time=15) -> None:
    """extract metadata from user profile"""
    driver.get(f"https://twitter.com/{follower}")
    json_script = WebDriverWait(driver, waiting_time).until(
        EC.presence_of_element_located(('xpath', xpath))).get_attribute("innerHTML")
    # loading JSON from innerHTML
    json_data = json.loads(json_script)
    username = json_data['author']['givenName']
    twitter_id = json_data['author']['identifier']
    followers_count = json_data['author']['interactionStatistic'][0]['userInteractionCount']
    followings_count = json_data['author']['interactionStatistic'][1]['userInteractionCount']
    creation_date = json_data['dateCreated']


if __name__ == "__main__":
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), options=options, seleniumwire_options=seleniumwire_options)
    driver.maximize_window()
    driver.get("https://twitter.com/")
    button_press('//span[text()="Unwesentliche Cookies ablehnen"]')
    button_press('//span[text()="Anmelden"]')
    text_input('//input[@type="text"]', USERNAME)
    text_input('//input[@type="password"]', PASSWORD)
    time.sleep(3)
    driver.get(USERURL)
    button_press('//span[starts-with(text(), "Follower")]')
    collect_followers()
