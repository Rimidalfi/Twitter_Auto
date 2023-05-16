# import tweepy
# from tweepy import Client
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Setze deine Zugangsdaten hier ein
# consumer_key = os.getenv("API_KEY")
# consumer_secret = os.getenv("API_SECRET")
# access_token = os.getenv("ACCESS_TOKEN")
# access_token_secret = os.getenv("ACCESS_SECRET")
# bearer_token = os.getenv("BEARER_TOKEN")

# client = Client(consumer_key=consumer_key, consumer_secret=consumer_secret,
#                 access_token=access_token, access_token_secret=access_token_secret, bearer_token=bearer_token)

# # client.create_tweet(text="This is a test")


# # followers = Client.get_users_followers(id=1638905720220315648, self=client)
# # print(followers)
# # print(type(followers))

# users = Client.get_me(self=client)
# print(users)
# # print(type(users))

# /html/head/script[2]/text()
# /html/head/script[2]
# <script type="application/ld+json" data-testid="UserProfileSchema-test" data-rh="true">{
#   "@context": "http://schema.org",
#   "@type": "ProfilePage",
#   "dateCreated": "2023-03-23T14:09:32.000Z",
#   "author": {
#     "@type": "Person",
#     "additionalName": "Rimidalfi",
#     "description": "",
#     "givenName": "Rimidalf",
#     "homeLocation": {
#       "@type": "Place",
#       "name": null
#     },
#     "identifier": "1638905720220315648",
#     "image": {
#       "@type": "ImageObject",
#       "contentUrl": "https://pbs.twimg.com/profile_images/1638905916086009856/j7ixDMVp_400x400.jpg",
#       "thumbnailUrl": "https://pbs.twimg.com/profile_images/1638905916086009856/j7ixDMVp_normal.jpg"
#     },
#     "interactionStatistic": [
#       {
#         "@type": "InteractionCounter",
#         "interactionType": "https://schema.org/FollowAction",
#         "name": "Follows",
#         "userInteractionCount": 2
#       },
#       {
#         "@type": "InteractionCounter",
#         "interactionType": "https://schema.org/SubscribeAction",
#         "name": "Friends",
#         "userInteractionCount": 8
#       },
#       {
#         "@type": "InteractionCounter",
#         "interactionType": "https://schema.org/WriteAction",
#         "name": "Tweets",
#         "userInteractionCount": 2
#       }
#     ],
#     "url": "https://twitter.com/Rimidalfi"
#   },
#   "contentRating": ""
# }</script>

# import csv

# with open("csv/new_followers.csv", 'r', newline='') as csvfile:

#     csv_r = csv.reader(csvfile)
#     # print(csv_r.line_num(0))
#     for i in csv_r:
#         print(i[0])
#         if csv_r.line_num == 20:
#             break

# import time
# timer = 5 * 60
# start_time = time.time()
# time_elapsed = 0
# while time_elapsed < timer:
#     time_elapsed = time.time()-start_time
#     print(round(time_elapsed))
#     time.sleep(1)


# def timer(min: int):
#     timer = min * 60
#     start_time = time.time()
#     time_elapsed = 0
#     while time_elapsed < timer:
#         time_elapsed = time.time()-start_time
#         time.sleep(1)

# import datetime

# import time

# start_time = datetime.time(0, 0)
# end_time = datetime.time(13, 13)

# # print(type(start_time))
# # print(type(end_time))
# # print(type(current_time))
# # print(start_time)
# # print(end_time)
# # print(current_time)
# while True:
#     current_time = datetime.datetime.now().time()
#     if start_time <= current_time <= end_time:
#         for i in range(60):
#             print(current_time)

#     print("im sleeping")
#     time.sleep(15)
# # while True:
# #     current_time = datetime.datetime.now().time()
# #     if start_time <= current_time <= end_time:
# #         print(current_time)
# #     time.sleep(1)

import os
import csv
import time
import datetime
# from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
from dotenv import load_dotenv


load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
USERURL = os.getenv("USERURL")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_IP = os.getenv("PROXY_IP")

seleniumwire_options = {
    'proxy': {
        'http': f'http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_IP}:{PROXY_PORT}',
        'https': f'https://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_IP}:{PROXY_PORT}',
    },
}
counter = 0
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()), options=options, seleniumwire_options=seleniumwire_options)


def button_press(xpath: str, waiting_time=15) -> None:

    button = WebDriverWait(driver, waiting_time).until(
        EC.element_to_be_clickable(('xpath', xpath)))
    button.click()


def text_input(xpath: str, text: str, waiting_time=5) -> None:
    input = WebDriverWait(driver, waiting_time).until(
        EC.presence_of_element_located(('xpath', xpath)))
    input.send_keys(text + Keys.RETURN)


def adding_followers(xpath: str, waiting_time=5) -> None:
    links = WebDriverWait(driver, waiting_time).until(
        EC.visibility_of_any_elements_located(('xpath', xpath)))

    for link in links:
        follower = link.text.replace("@", "")
        add_entry_to_csv("csv/new_followers.csv", follower)


def add_entry_to_csv(file_path, new_entry) -> None:
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


def collect_followers(collecting_time: int = 3, pixels_scroll: int = 500, start_hours: int = 00, start_min: int = 00, end_hours: int = 12, end_min: int = 00) -> None:
    start_time = datetime.time(start_hours, start_min)
    end_time = datetime.time(end_hours, end_min)
    global counter
    while True:
        current_time = datetime.datetime.now().time()
        # during timeframe(start_time - end_time) run loop
        if start_time <= current_time <= end_time:
            # loop runs x min (collecting_time)
            start = time.time()
            duration = collecting_time*60
            while (time.time()-start) < duration:
                while counter <= 30:
                    adding_followers(
                        '//div[@aria-label="Timeline: Followers"]//span[starts-with(text(), "@")]')
                    time.sleep(0.1)
                else:
                    driver.execute_script(
                        f"window.scrollBy(0, {pixels_scroll})")
                    counter = 0
                    time.sleep(3)
            # refreshes the page to start again from the top of the followers list after 1 hour
            driver.refresh()
            time.sleep(56*60)
        # waits 1 min to check if condition
        print("sleeping ... 😴")
        time.sleep(60)


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
