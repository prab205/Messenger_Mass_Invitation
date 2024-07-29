import os
import time
import regex as re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException, InvalidArgumentException

class send_to_messenger:
    def __init__(self, headless=False):
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument('headless')
        chrome_options.add_argument('disable-notifications') # Disable 'This page wants to show notification prompt'
        chrome_options.add_argument('start-maximized')
        self.driver = webdriver.Chrome(options=chrome_options)

    def __del__(self):
        self.driver.quit()
        print("Completed")

    def login_to_facebook(self, email, password):
        self.driver.get('https://www.facebook.com/')
        
        email_element = self.driver.find_element(By.ID, 'email')
        email_element.send_keys(email)
        
        pass_element = self.driver.find_element(By.ID, 'pass')
        pass_element.send_keys(password)
        
        pass_element.send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for the login to complete
        return "Login successful"

    def send_message_to_user(self, user_id, message_text):
        self.driver.get(f'https://www.facebook.com/messages/t/{user_id}')
        time.sleep(5)  # Wait for the page to load

        try:
            continue_box = self.driver.find_element(By.CSS_SELECTOR,"div[aria-label='Continue']") #Messages sent before end-to-end encrypted. Continue
            continue_box.click()
            time.sleep(2)
        except Exception as e:
            pass

        try:
            message_box = self.driver.find_element(By.CSS_SELECTOR, "div[aria-label='Message']") #Select the message box
            message_box.click()

            processed_message, images_list = self.process_text_content(message_text)

            if "\n" in processed_message:
                for part in processed_message.split('\n'):
                    message_box.send_keys(part)
                    ActionChains(self.driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
            else:
                message_box.send_keys(processed_message)

            if images_list:
                for image_url in images_list:
                    self.attach_image(image_url) 

            message_box.send_keys(Keys.RETURN)
            time.sleep(5)  # Wait for the message to be sent
            print(f"Successfully sent to {user_id}")
            time.sleep(5)
        except NoSuchElementException:
            print(f"\tCannot find message box. Failed to send to user {user_id}")
        except WebDriverException as e:
            print(f"\tWebDriver Exception at {user_id}, ",e)
            exit(-1)
        except Exception as e:
            print(f"Failed to send for user {user_id}, ",e)
    
    def process_text_content(self, message_text):
        img_count = message_text.count('<img>')
        pattern = r"(<img>.*?</img>)"
        images_list = list()

        for i in range(img_count):
            img_tag = re.search(pattern, message_text).group(0)
            message_text = message_text.replace(img_tag, "", 1).strip()
            images_list.append(img_tag[5:-6])

        return message_text, images_list
    
    def attach_image(self, img_url):
        try:
            full_path = os.path.join(os.getcwd(), img_url) 
            attach_button = self.driver.find_element(By.XPATH, '//input[@type="file"]')
            attach_button.send_keys(full_path)
            time.sleep(5)
        except InvalidArgumentException as e:
            print(f'File not found: {full_path}')
            exit(-1)
