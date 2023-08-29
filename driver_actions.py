import json
import logging
import time
import random
from selenium.common.exceptions import (ElementNotInteractableException, 
                                        StaleElementReferenceException, 
                                        TimeoutException)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(level=logging.INFO)

def random_delay(min_seconds=1, max_seconds=3):
    """Generate a random delay time."""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def retry_on_stale_element(retries=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(retries):
                try:
                    return func(*args, **kwargs)
                except StaleElementReferenceException:
                    logging.warning("StaleElementReferenceException encountered. Retrying...")
                    pass
            return func(*args, **kwargs)  # 最後一次嘗試，如果仍然失敗，則引發異常
        return wrapper
    return decorator

class DriverActions:
    def __init__(self, driver):
        self.driver = driver

    def _convert_locator_type(self, locator_type):
        SUPPORTED_LOCATOR_TYPES = ["ID", "NAME", "XPATH", "TAG_NAME", "CLASS_NAME", "LINK_TEXT", "PARTIAL_LINK_TEXT", "CSS_SELECTOR"]
        
        if locator_type in ["linkText", "LINKTEXT"]:
            locator_type = "LINK_TEXT"
        elif locator_type == "CSS":
            locator_type = "CSS_SELECTOR"
        
        if locator_type not in SUPPORTED_LOCATOR_TYPES:
            raise ValueError(f"Unsupported locator type: {locator_type}")
        
        return locator_type

    def wait_for_element(self, locator_type, locator_value, timeout=10):
        locator_type = self._convert_locator_type(locator_type)
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((getattr(By, locator_type), locator_value)))
        except TimeoutException:
            logging.error(f"Element with locator type {locator_type} and value {locator_value} not found within {timeout} seconds.")
            # 如果您希望在這裡終止整個流程，則保留以下行
            self.driver.quit()
            exit(1)

    def execute(self, action):
        action_type = action["action"]
        if hasattr(self, action_type):
            params = {k: v for k, v in action.items() if k not in ["action"]}
            if "locator_type" in params and params["locator_type"] == "CSS":
                params["locator_type"] = "CSS_SELECTOR"
            getattr(self, action_type)(**params)

    def wait_for_element_to_be_clickable(self, locator_type, locator_value, timeout=10):
        locator_type = self._convert_locator_type(locator_type)
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((getattr(By, locator_type), locator_value)))

    def wait_for_element_to_be_visible(self, locator_type, locator_value, timeout=10):
        locator_type = self._convert_locator_type(locator_type)
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((getattr(By, locator_type), locator_value)))

    @retry_on_stale_element()
    def input(self, locator_type, locator_value, input_value):
        locator_type = self._convert_locator_type(locator_type)
        random_delay()
        element = self.wait_for_element_to_be_visible(locator_type, locator_value)
        try:
            element.send_keys(input_value)
        except ElementNotInteractableException as e:
            logging.error(f"Element not interactable during input: {e}")
            # 使用JavaScript設置元素的值作為回退方法
            self.driver.execute_script("arguments[0].value = arguments[1];", element, input_value)
        except Exception as e:
            logging.error(f"Unexpected error during input: {e}")

    @retry_on_stale_element()
    def click(self, locator_type, locator_value):
        locator_type = self._convert_locator_type(locator_type)
        random_delay()
        try:
            element = self.wait_for_element_to_be_clickable(locator_type, locator_value)
            element.click()
        except ElementNotInteractableException as e:
            logging.error(f"Element not interactable: {e}")
            self.driver.execute_script("arguments[0].click();", element)
        except Exception as e:  # 捕獲所有異常，這可以根據需要進一步細分
            logging.error(f"Unexpected error: {e}")

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
        locator_type = self._convert_locator_type(locator_type)  # 加入這行
        return self.driver.find_element(getattr(By, locator_type), locator_value)

    def find_elements(self, locator_type, locator_value):
        locator_type = self._convert_locator_type(locator_type)  # 加入這行
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
        locator_type = self._convert_locator_type(locator_type)  # 加入這行
        random_delay()
        element = self.wait_for_element(locator_type, locator_value)
        ActionChains(self.driver).click_and_hold(element).perform()

    def mouse_up(self, locator_type, locator_value):
        locator_type = self._convert_locator_type(locator_type)  # 加入這行
        random_delay()
        element = self.wait_for_element(locator_type, locator_value)
        ActionChains(self.driver).release(element).perform()

    
    def execute_actions_from_json(self, actions_json):
        actions = json.loads(actions_json)
        results = []
        for action in actions:
            action["locator_type"] = self._convert_locator_type(action["locator_type"])
            try:
                if action["action"] == "input":
                    self.input(action["locator_type"], action["locator_value"], action["input_value"])

                elif action["action"] == "click":
                    self.click(action["locator_type"], action["locator_value"])

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

                elif action["action"] == "runScript":
                    result = self.execute_script(action["script"])
                    results.append(result)
            except Exception as e:
                            logging.error(f"Error executing action {action['action']}: {e}")
                            self.driver.quit()
                            exit(1)
        return results
