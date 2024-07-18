import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('headless')
chrome_options.add_argument('disable-notifications') # Disable 'This page wants to show notification prompt'
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)


def login_to_facebook(email, password):
    driver.get('https://www.facebook.com/')
    
    email_element = driver.find_element(By.ID, 'email')
    email_element.send_keys(email)
    
    pass_element = driver.find_element(By.ID, 'pass')
    pass_element.send_keys(password)
    
    pass_element.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait for the login to complete
    return "Login successful"

def send_message_to_user(user_id, message_text, images_list=None):
    driver.get(f'https://www.facebook.com/messages/t/{user_id}')
    time.sleep(5)  # Wait for the page to load

    try:
        continue_box = driver.find_element(By.CSS_SELECTOR,"div[aria-label='Continue']") #Messages sent before end-to-end encrypted. Continue
        continue_box.click()
        time.sleep(5)
    except Exception as e:
        pass

    try:
        message_box = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Message']") #Select the message box
        message_box.click()
        if "\n" in message_text:
            for part in message_text.split('\n'):
                message_box.send_keys(part)
                ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
        else:
            message_box.send_keys(message_text)

        if images_list:
            for image_url in images_list:
                attach_image(image_url) 

        message_box.send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for the message to be sent
        print(f"Successfully sent to {user_id}")
        time.sleep(5)
    except NoSuchElementException:
        print(f"\tCannot find message box. Failed to send to user {user_id}")
    except WebDriverException as e:
        print(f"**WebDriver Exception at {user_id}, ",e)
        exit(-1)
    except Exception as e:
        print(f"Failed to send for user {user_id}, ",e)

def send_message_csv_file(csv_file, message_text, images_list=None):
    df = pd.read_csv(csv_file)
    try:
        for item in df['User_id']:
            send_message_to_user(item, message_text, images)
    except KeyError as e:
        print(f"Keyerror, {e} column mentioned at line {e.__traceback__.tb_lineno} doesnot exist in csv file")
    except Exception as e:
        print(f"Exception occured, ", e)

def send_message_list(users_list, message_text, images_list=None):
    for user_id in users_list:
        send_message_to_user(user_id, message_text, images)

def attach_image(img_url):
    attach_button = driver.find_element(By.XPATH, '//input[@type="file"]')
    attach_button.send_keys(os.path.join(os.getcwd(), img_url))
    time.sleep(5)


if __name__ == "__main__":
    email = 'prabinpaudel43@gmail.com'
    with open('confidential/password', 'r') as file:
        password = file.readline()
    print(login_to_facebook(email, password))

    with open('resources/message.txt', 'r') as file:
        message_text = file.read()

    img_count = message_text.count('<img>')
    pattern = r"(<img>.*?</img>)"
    images = list()

    for i in range(img_count):
        img_tag = re.search(pattern, message_text).group(0)
        message_text = message_text.replace(img_tag, "", 1).strip()
        images.append(img_tag[5:-6])


    #send_message_csv_file('resources/unfilled.csv', message_text, images)

    user_ids = ['jinpaudel']
    send_message_list(user_ids, message_text, images)

    driver.quit()
