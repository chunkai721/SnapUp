import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from notify import send_line_notify
from pyvirtualdisplay import Display

# Check if we are in a Docker environment
IN_DOCKER = os.environ.get('IN_DOCKER', 'False').lower() == 'true'

# If not in Docker (i.e., in Windows), load environment variables from .env file
if not IN_DOCKER:
    from dotenv import load_dotenv
    load_dotenv()

# Retrieve sensitive data from environment variables
PROGRAM_NAME = os.environ.get('PROGRAM_NAME')
LINE_TOKEN = os.environ.get('LINE_TOKEN')

# Load data from the JSON file
with open('actions.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

URL = data["URL"]
ACTIONS = data["ACTIONS"]

CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument('--no-sandbox')
CHROME_OPTIONS.add_argument('--disable-dev-shm-usage')
CHROME_OPTIONS.add_argument('--headless')
CHROME_OPTIONS.add_argument('--disable-gpu')
CHROME_OPTIONS.add_argument("--disable-software-rasterizer")
CHROME_OPTIONS.add_argument("--disable-setuid-sandbox")


class DriverActions:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, locator_type, locator_value, timeout=10):
        # 將 "linkText" 轉換為 "LINK_TEXT"
        if locator_type == "linkText":
            locator_type = "LINK_TEXT"
        elif locator_type == "CSS":
            locator_type = "CSS_SELECTOR"
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((getattr(By, locator_type), locator_value)))

    def execute(self, action):
        action_type = action["action"]
        if hasattr(self, action_type):
            params = {k: v for k, v in action.items() if k not in ["action"]}
            getattr(self, action_type)(**params)

    def input(self, locator_type, locator_value, input_value):
        element = self.wait_for_element(locator_type, locator_value)
        element.send_keys(input_value)

    def click(self, locator_type, locator_value):
        element = self.wait_for_element(locator_type, locator_value)
        element.click()

    def switch_to(self, frame):
        self.driver.switch_to.frame(frame)

    def get_title(self):
        return self.driver.title

    def get_current_url(self):
        return self.driver.current_url

    def get_page_source(self):
        return self.driver.page_source

    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()

    def go_back(self):
        self.driver.back()

    def go_forward(self):
        self.driver.forward()

    def refresh(self):
        self.driver.refresh()

    def find_element(self, locator_type, locator_value):
        if locator_type == "CSS":
            locator_type = "CSS_SELECTOR"
        return self.driver.find_element(getattr(By, locator_type), locator_value)

    def find_elements(self, locator_type, locator_value):
        if locator_type == "CSS":
            locator_type = "CSS_SELECTOR"
        return self.driver.find_elements(getattr(By, locator_type), locator_value)

    def switch_to_alert(self):
        return self.driver.switch_to.alert()

    def switch_to_default_content(self):
        self.driver.switch_to.default_content()

    def execute_script(self, script):
        return self.driver.execute_script(script)

    def get_cookies(self):
        return self.driver.get_cookies()

    def add_cookie(self, cookie_dict):
        self.driver.add_cookie(cookie_dict)

    def delete_cookie(self, cookie_name):
        self.driver.delete_cookie(cookie_name)

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()

    def save_screenshot(self, path):
        self.driver.save_screenshot(path)

    def get_window_handles(self):
        return self.driver.window_handles

    def switch_to_window(self, handle):
        self.driver.switch_to.window(handle)

    def mouse_down(self, locator_type, locator_value):
        element = self.wait_for_element(locator_type, locator_value)
        ActionChains(self.driver).click_and_hold(element).perform()

    def mouse_up(self, locator_type, locator_value):
        element = self.wait_for_element(locator_type, locator_value)
        ActionChains(self.driver).release(element).perform()
    
    def execute_actions_from_json(self, actions_json):
        actions = json.loads(actions_json)
        results = []

        for action in actions:
            if action["action"] == "input":
                self.wait_and_input(getattr(By, action["locator_type"]), action["locator_value"], action["input_value"])

            elif action["action"] == "click":
                self.wait_and_click(getattr(By, action["locator_type"]), action["locator_value"])

            elif action["action"] == "switch_to":
                self.switch_to(action["frame"])

            elif action["action"] == "get_title":
                results.append(self.get_title())

            elif action["action"] == "get_current_url":
                results.append(self.get_current_url())

            elif action["action"] == "get_page_source":
                results.append(self.get_page_source())

            elif action["action"] == "close":
                self.close()

            elif action["action"] == "quit":
                self.quit()

            elif action["action"] == "go_back":
                self.go_back()

            elif action["action"] == "go_forward":
                self.go_forward()

            elif action["action"] == "refresh":
                self.refresh()

            elif action["action"] == "find_element":
                element = self.find_element(getattr(By, action["locator_type"]), action["locator_value"])
                results.append(element.text if element else None)

            elif action["action"] == "find_elements":
                elements = self.find_elements(getattr(By, action["locator_type"]), action["locator_value"])
                results.append([element.text for element in elements])

            elif action["action"] == "switch_to_alert":
                alert = self.switch_to_alert()
                results.append(alert.text if alert else None)

            elif action["action"] == "switch_to_default_content":
                self.switch_to_default_content()

            elif action["action"] == "execute_script":
                result = self.execute_script(action["script"])
                results.append(result)

            elif action["action"] == "get_cookies":
                results.append(self.get_cookies())

            elif action["action"] == "add_cookie":
                self.add_cookie(action["cookie_dict"])

            elif action["action"] == "delete_cookie":
                self.delete_cookie(action["cookie_name"])

            elif action["action"] == "delete_all_cookies":
                self.delete_all_cookies()

            elif action["action"] == "save_screenshot":
                self.save_screenshot(action["path"])

            elif action["action"] == "get_window_handles":
                results.append(self.get_window_handles())

            elif action["action"] == "switch_to_window":
                self.switch_to_window(action["handle"])

            elif action["action"] == "mouse_down":
                self.mouse_down(getattr(By, action["locator_type"]), action["locator_value"])

            elif action["action"] == "mouse_up":
                self.mouse_up(getattr(By, action["locator_type"]), action["locator_value"])

        return results



def handle_alert(driver):
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
    except:
        pass


def send_error_notify(message):
    """錯誤回報機制"""
    print(f"Error: {message}")  # 日誌輸出
    send_line_notify(LINE_TOKEN, f"{PROGRAM_NAME}: {message}", None)


def snapup():
    try:
        start_time = time.time()  # <-- 新增這一行: 記錄開始時間

        print("Starting the snapup function...")  # 日誌輸出
        if IN_DOCKER:
            display = Display(visible=0, size=(1024, 768))
            display.start()

        # Modify Chrome options based on the environment
        chrome_options = CHROME_OPTIONS if IN_DOCKER or os.name == 'posix' else Options()

        with webdriver.Chrome(options=chrome_options) as driver:
            driver.set_window_size(1024, 768)
            driver.get(URL)

            driver_actions = DriverActions(driver)
            for action in ACTIONS:
                driver_actions.execute(action)

            if IN_DOCKER:
                display.stop()

        end_time = time.time()  # <-- 新增這一行: 記錄結束時間
        elapsed_time = end_time - start_time  # 計算所花費的時間
        print(f"Total time taken: {elapsed_time:.2f} seconds")  # 打印所花費的時間

    except Exception as e:
        send_error_notify(str(e))


def main():
    print(f"{PROGRAM_NAME} started.")  # 日誌輸出
    snapup()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        send_error_notify(f"Unexpected error: {str(e)}")
