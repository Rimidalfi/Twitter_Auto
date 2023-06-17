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
#       "name": ""
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
#         "userInteractionCount": 5
#       },
#       {
#         "@type": "InteractionCounter",
#         "interactionType": "https://schema.org/SubscribeAction",
#         "name": "Friends",
#         "userInteractionCount": 14
#       },
#       {
#         "@type": "InteractionCounter",
#         "interactionType": "https://schema.org/WriteAction",
#         "name": "Tweets",
#         "userInteractionCount": 4
#       }
#     ],
#     "url": "https://twitter.com/Rimidalfi"
#   },
#   "contentRating": ""
# }</script>
import json
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import os
import dotenv
import main

dotenv.load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")


def get_meta(follower: str, xpath: str, waiting_time=5) -> dict:
    """extract metadata from user profile"""
    driver.get(f"https://twitter.com/{follower}")
    json_script = WebDriverWait(driver, waiting_time).until(
        EC.presence_of_element_located(('xpath', xpath))).get_attribute("innerHTML")
    # loading JSON from innerHTML
    json_data = json.loads(json_script)
    twitter_handle = json_data['author']['additionalName']
    username = json_data['author']['givenName']
    twitter_id = json_data['author']['identifier']
    followers_count = json_data['author']['interactionStatistic'][0]['userInteractionCount']
    followings_count = json_data['author']['interactionStatistic'][1]['userInteractionCount']
    creation_date = json_data['dateCreated']
    return {
        "twitter_handle": twitter_handle,
        "username": username,
        "twitter_id": twitter_id,
        "followers_count": followers_count,
        "followings_count": followings_count,
        "creation_date": creation_date[:10]
    }


options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()), options=options)
time.sleep(10)
conn = main.connect_to_db(DB_HOST, DB_PORT, DB_USER,
                          DB_PASSWORD, DB_DATABASE)
cursor = conn.cursor()
counter = 0
query = "SELECT * FROM follower_list WHERE twitter_id IS NULL AND dead_acc IS NULL"
sql_w_alive = "UPDATE follower_list SET twitter_id=%s, username=%s, followers=%s, followings=%s, creation_date=%s, welcome_msg=%s, dead_acc=%s WHERE twitter_handle=%s"
sql_w_dead = "UPDATE follower_list SET dead_acc=%s WHERE twitter_handle=%s"
cursor.execute(query)
results = cursor.fetchall()
print("-"*30)
for row in results:
    try:
        a = get_meta(
            row[1], '//script[@type="application/ld+json" and @data-testid="UserProfileSchema-test"]', waiting_time=10)
        cursor.execute(sql_w_alive, (a["twitter_id"], a["username"],
                       a["followers_count"], a["followings_count"], a["creation_date"], 0, 0, a["twitter_handle"]))
        conn.commit()
        print(a)
        print(type(a["creation_date"]))
        print("*"*70)
    except:
        cursor.execute(sql_w_dead, (1, row[1]))
        conn.commit()
        print(f"{row[1]} is a locked or deleted account 😵💀")
        print("*"*70)

    counter += 1
    if counter == 20:
        break


print("-"*30)
cursor.close()
conn.close()


# a = get_meta('Rimidalfi',
#              '//script[@type="application/ld+json" and @data-testid="UserProfileSchema-test"]')

driver.quit()
