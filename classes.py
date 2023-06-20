import json
import time
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

from selenium import webdriver
import mysql.connector
import os
import dotenv
import main
import sys

dotenv.load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")


def get_meta(driver: webdriver, follower: str, xpath: str, waiting_time: int = 5) -> dict:
    """extract metadata from user profile"""
    driver.get(f"https://twitter.com/{follower}")
    json_script = WebDriverWait(driver, waiting_time).until(
        EC.presence_of_element_located(('xpath', xpath))).get_attribute("innerHTML")
    # loading JSON from innerHTML
    json_data = json.loads(json_script)
    twitter_id = json_data['author']['identifier']
    username = json_data['author']['givenName']
    followers_count = json_data['author']['interactionStatistic'][0]['userInteractionCount']
    followings_count = json_data['author']['interactionStatistic'][1]['userInteractionCount']
    creation_date = json_data['dateCreated']
    twitter_handle = json_data['author']['additionalName']
    return {
        "twitter_handle": twitter_handle,
        "username": username,
        "twitter_id": twitter_id,
        "followers_count": followers_count,
        "followings_count": followings_count,
        "creation_date": creation_date[:10]
    }


def waiting_symbol(speed, timer, symbol_length):
    """sleeping time with animation"""
    start = time.time()
    duration = timer * 60
    symbols = ["|", "/", "-", "\\"]
    print(f"sleeping for {timer} min... 😴")

    while (time.time() - start) < duration:
        for i in symbols:
            sys.stdout.write((i + " ")*symbol_length)
            sys.stdout.flush()
            time.sleep(speed)
            sys.stdout.write("\r")
            sys.stdout.flush()


class DatabaseManager:
    def __init__(self, db_host: str, db_port: str, db_user: str, db_password: str, db_database: str) -> None:
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_database = db_database
        self.conn = None
        self.cursor = None

    def connect_to_db(self) -> mysql.connector.connection_cext.CMySQLConnection:
        """open connection to database (making cursor)"""
        self.conn = mysql.connector.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )
        self.cursor = self.conn.cursor()

    def close_connection(self) -> None:
        """Close the cursor and database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def select_from_db(self, table: str, row_1: str, row_2: str) -> list:
        sql_r = f"SELECT * FROM {table} WHERE {row_1} IS NULL AND {row_2} IS NULL"
        self.cursor.execute(sql_r)
        return self.cursor.fetchall()

    def update_db(self, table: str, data_list: list, operation_time: int, driver: webdriver) -> None:

        sql_w_alive = f"UPDATE {table} SET twitter_id=%s, username=%s, followers=%s,followings=%s, creation_date=%s, welcome_msg=%s,dead_acc=%s WHERE twitter_handle=%s"

        sql_w_dead = f"UPDATE {table} SET dead_acc=%s WHERE twitter_handle=%s"
        start = time.time()
        duration = operation_time*60

        for userdata_tuple in data_list:
            try:
                userdata_dict = get_meta(driver, userdata_tuple[1],
                                         '//script[@type="application/ld+json" and @data-testid="UserProfileSchema-test"]',
                                         waiting_time=10)

                self.cursor.execute(sql_w_alive,
                                    (userdata_dict["twitter_id"],
                                        userdata_dict["username"],
                                        userdata_dict["followers_count"],
                                        userdata_dict["followings_count"],
                                        userdata_dict["creation_date"], 0, 0, userdata_dict["twitter_handle"]))
                self.conn.commit()
                print(userdata_dict)
                print("*"*70)
            except TimeoutException:
                self.cursor.execute(sql_w_dead, (1, userdata_tuple[1]))
                self.conn.commit()
                print(f"{userdata_tuple[1]} is a locked or deleted account 😵💀")
                print("*"*70)
            if (time.time()-start) >= duration:
                print("updating database finished, time for a nap...")
                break


if __name__ == "__main__":

    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), options=options)
    manage_db = DatabaseManager(
        DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE)

    while True:
        manage_db.connect_to_db()
        user_list = manage_db.select_from_db(
            "follower_list", "twitter_id", "dead_acc")
        if user_list == []:
            print("no new followers to add to db...\n")
            manage_db.close_connection()
            waiting_symbol(speed=0.35, timer=30, symbol_length=45)

        else:
            manage_db.update_db("follower_list", user_list, 1, driver)
            manage_db.close_connection()
            waiting_symbol(speed=0.35, timer=1, symbol_length=30)


# time.sleep(10)
# conn = main.connect_to_db(DB_HOST, DB_PORT, DB_USER,
#                           DB_PASSWORD, DB_DATABASE)
# cursor = conn.cursor()
# counter = 0
# query = "SELECT * FROM follower_list WHERE twitter_id IS NULL AND dead_acc IS NULL"
# sql_w_alive = "UPDATE follower_list SET twitter_id=%s, username=%s, followers=%s, followings=%s, creation_date=%s, welcome_msg=%s, dead_acc=%s WHERE twitter_handle=%s"
# sql_w_dead = "UPDATE follower_list SET dead_acc=%s WHERE twitter_handle=%s"
# cursor.execute(query)
# list = cursor.fetchall()
# print("-"*30)
# for userdata_tuple in list:
#     try:
#         userdata_dict = get_meta(
#             userdata_tuple[1], '//script[@type="application/ld+json" and @data-testid="UserProfileSchema-test"]', waiting_time=10)
#         cursor.execute(sql_w_alive, (userdata_dict["twitter_id"], userdata_dict["username"],
#                        userdata_dict["followers_count"], userdata_dict["followings_count"], userdata_dict["creation_date"], 0, 0, userdata_dict["twitter_handle"]))
#         conn.commit()
#         print(userdata_dict)
#         print("*"*70)
#     except:
#         cursor.execute(sql_w_dead, (1, userdata_tuple[1]))
#         conn.commit()
#         print(f"{userdata_tuple[1]} is a locked or deleted account 😵💀")
#         print("*"*70)

#     counter += 1
#     if counter == 20:
#         break


# print("-"*30)
# cursor.close()
# conn.close()


# # a = get_meta('Rimidalfi',
# #              '//script[@type="application/ld+json" and @data-testid="UserProfileSchema-test"]')

# driver.quit()
