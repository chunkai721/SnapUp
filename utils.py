import os
import json
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from notify import send_line_notify

def load_env_vars():
    IN_DOCKER = os.environ.get('IN_DOCKER', 'False').lower() == 'true'
    if not IN_DOCKER:
        load_dotenv()

    PROGRAM_NAME = os.environ.get('PROGRAM_NAME')
    LINE_TOKEN = os.environ.get('LINE_TOKEN')
    # data = load_actions_from_json()
    data = load_actions_from_side('momo3.side')
    URL = data["URL"]
    ACTIONS = data["ACTIONS"]
    CHROME_OPTIONS = get_chrome_options()

    return PROGRAM_NAME, LINE_TOKEN, URL, ACTIONS, CHROME_OPTIONS

def load_actions_from_json():
    with open('actions.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def get_chrome_options():
    # 根據環境設置CHROME_OPTIONS
    IN_DOCKER = os.environ.get('IN_DOCKER', 'False').lower() == 'true'

    CHROME_OPTIONS = Options()
    CHROME_OPTIONS.add_argument('--no-sandbox')
    CHROME_OPTIONS.add_argument('--disable-dev-shm-usage')
    CHROME_OPTIONS.add_argument('--disable-gpu')
    CHROME_OPTIONS.add_argument("--disable-software-rasterizer")
    CHROME_OPTIONS.add_argument("--disable-setuid-sandbox")
    if IN_DOCKER:
        CHROME_OPTIONS.add_argument('--headless')

    return CHROME_OPTIONS

def send_error_notify(message, LINE_TOKEN, PROGRAM_NAME):
    print(f"Error: {message}")
    send_line_notify(LINE_TOKEN, f"{PROGRAM_NAME}: {message}", None)

def load_actions_from_side(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        side_data = json.load(file)
    
    result = {
        "URL": side_data["url"],
        "ACTIONS": []
    }
    
    for test in side_data["tests"]:
        for command in test["commands"]:
            action = {}
            
            command_mapping = {
                "open": "open",
                "click": "click",
                "type": "input",
                "setWindowSize": "setWindowSize",
                "runScript": "runScript",
                # ... 其他命令映射
            }
            action["action"] = command_mapping.get(command["command"], command["command"])
            
            if "target" in command:
                if "=" in command["target"]:
                    locator_type, locator_value = command["target"].split("=", 1)
                    action["locator_type"] = locator_type.upper()
                    action["locator_value"] = locator_value
                else:
                    action["locator_value"] = command["target"]
            
            if command["command"] == "setWindowSize":
                width, height = command["target"].split("x")
                action["width"] = width
                action["height"] = height
            
            if "value" in command and command["value"]:
                action["input_value"] = command["value"]
            
            if action["action"] == "runScript":
                action["script"] = command["target"]
                del action["locator_value"]
            
            result["ACTIONS"].append(action)
    
    return result
