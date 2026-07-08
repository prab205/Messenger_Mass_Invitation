import os
import time
import random
import regex as re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, InvalidArgumentException, TimeoutException, ElementNotInteractableException, StaleElementReferenceException

# FB's composer markup shifts over time/locale; try known variants in order.
MESSAGE_BOX_SELECTORS = [
    "div[aria-label='Message']",
    "div[contenteditable='true'][role='textbox']",
]

class send_to_messenger:
    def __init__(self, headless=False, profile_dir=None):
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument('headless')
        chrome_options.add_argument('disable-notifications') # Disable 'This page wants to show notification prompt'
        chrome_options.add_argument('start-maximized')

        if profile_dir:
            # Persist cookies/session across runs so Facebook treats this as the
            # same known device instead of flagging a fresh login every launch,
            # which is what triggers checkpoint / restore-session / restore-pin prompts.
            profile_path = os.path.abspath(profile_dir)
            os.makedirs(profile_path, exist_ok=True)
            chrome_options.add_argument(f'--user-data-dir={profile_path}')

        # Chrome's own "restore pages?" bubble appears when the profile wasn't
        # shut down cleanly (e.g. driver.quit() didn't run). These suppress it.
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--disable-session-crashed-bubble')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.current_user_id = None

    def __del__(self):
        # Clean shutdown so Chrome doesn't mark the profile as crashed on next launch.
        self.driver.quit()
        print("Completed")

    def human_pause(self, min_s=0.4, max_s=1.2):
        """Short randomized pause layered on top of explicit waits, so action
        timing doesn't look machine-uniform to bot detection."""
        time.sleep(random.uniform(min_s, max_s))

    def type_text(self, element, text):
        """send_keys goes through ChromeDriver's key-event path, which only
        supports BMP characters — most emoji (surrogate pairs) raise
        InvalidArgumentException. execCommand('insertText', ...) inserts the
        raw string directly and still fires the input event FB's composer
        listens for, so it stays emoji-safe."""
        self.driver.execute_script(
            "arguments[0].focus(); document.execCommand('insertText', false, arguments[1]);",
            element, text
        )

    def find_message_box(self):
        for selector in MESSAGE_BOX_SELECTORS:
            try:
                return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            except TimeoutException:
                continue
        raise TimeoutException(f"None of the known message box selectors matched: {MESSAGE_BOX_SELECTORS}")

    def is_logged_in(self):
        try:
            self.driver.find_element(By.ID, 'email')
            return False
        except NoSuchElementException:
            return True

    def wait_for_manual_login(self, timeout_seconds=120, poll_interval_seconds=5):
        """FB sometimes throws MFA/bot-checkpoint after credential submit,
        landing back on a login-like page instead of the logged-in session.
        Give a human time to clear it manually, polling instead of blocking
        on a single long wait so we can bail out the moment it clears."""
        print(f"\tLogin page detected after submitting credentials (MFA/bot checkup). "
              f"Waiting up to {timeout_seconds}s for manual login...")
        waited = 0
        while waited < timeout_seconds:
            if self.is_logged_in():
                print("\tManual login detected, continuing.")
                return True
            time.sleep(poll_interval_seconds)
            waited += poll_interval_seconds
        return self.is_logged_in()

    def login_to_facebook(self, email, password):
        self.driver.get('https://www.facebook.com/')

        if self.is_logged_in():
            return "Already logged in (restored session)"

        email_element = self.wait.until(EC.presence_of_element_located((By.ID, 'email')))
        email_element.send_keys(email)

        pass_element = self.driver.find_element(By.ID, 'pass')
        pass_element.send_keys(password)

        pass_element.send_keys(Keys.RETURN)
        try:
            self.wait.until(EC.invisibility_of_element_located((By.ID, 'pass')))
        except TimeoutException:
            pass

        if not self.is_logged_in():
            if self.wait_for_manual_login():
                return "Login successful (after manual MFA/bot checkup)"
            raise TimeoutException("Still not logged in after 2 minutes of waiting for manual login")

        return "Login successful"

    def send_message_to_user(self, user_id, message_text):
        # Multiple message_texts (content files) for the same user should be
        # sent back-to-back in the already-open conversation, not by reloading
        # the whole page for every one of them.
        if self.current_user_id != user_id:
            self.driver.get(f'https://www.facebook.com/messages/t/{user_id}')
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            try:
                continue_button = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "div[aria-label='Continue']")
                    )
                )

                continue_button.click()
            except Exception as e:
                pass

            self.current_user_id = user_id

        try:
            message_box = self.find_message_box()
            message_box.click()

            processed_message, images_list = self.process_text_content(message_text)

            if "\n" in processed_message:
                for part in processed_message.split('\n'):
                    self.type_text(message_box, part)
                    ActionChains(self.driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
            else:
                self.type_text(message_box, processed_message)

            if images_list:
                for image_url in images_list:
                    self.attach_image(image_url) 

            message_box.send_keys(Keys.RETURN)
            # Composer clears once FB accepts the message; wait for that instead
            # of a fixed delay, and always pay a small human-like pause on top.
            try:
                self.wait.until(lambda d: message_box.text.strip() == "")
            except (TimeoutException, StaleElementReferenceException):
                pass
            self.human_pause(1.0, 2.5)
            print(f"Successfully sent to {user_id}")
        except (NoSuchElementException, TimeoutException):
            print(f"\tCannot find message box. Failed to send to user {user_id}")
            self.save_debug_snapshot(user_id)
            self.current_user_id = None
        except WebDriverException as e:
            # Log and move on to the next user instead of killing the whole batch
            # over one bad/blocked user_id.
            print(f"\tWebDriver Exception at {user_id}, ", e)
            self.current_user_id = None
        except Exception as e:
            print(f"Failed to send for user {user_id}, ",e)

    def save_debug_snapshot(self, user_id):
        try:
            path = os.path.abspath(f"debug_{user_id}.png")
            self.driver.save_screenshot(path)
            print(f"\tSaved debug screenshot to {path} (current url: {self.driver.current_url})")
        except WebDriverException:
            pass

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
        full_path = os.path.join(os.getcwd(), img_url)
        if not os.path.isfile(full_path):
            print(f'Image not found, skipping attachment: {full_path}')
            return
        try:
            attach_input = self.get_file_input()
            attach_input.send_keys(full_path)
            self.human_pause(0.6, 1.5)
        except (InvalidArgumentException, NoSuchElementException, ElementNotInteractableException, TimeoutException) as e:
            print(f'Failed to attach image {full_path}, ', e)

    def get_file_input(self):
        """Once text is typed into the composer, the toolbar folds the attach
        icon behind "Open more actions"; expand it before retrying."""
        try:
            attach_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            if attach_input.is_enabled():
                return attach_input
        except (NoSuchElementException, ElementNotInteractableException):
            pass

        more_actions = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[aria-label='Open more actions']"))
        )
        more_actions.click()
        return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
