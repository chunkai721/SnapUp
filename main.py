import os
import time
import json
from selenium import webdriver
from pyvirtualdisplay import Display
from driver_actions import DriverActions
from utils import load_env_vars, send_error_notify,load_actions_from_side

PROGRAM_NAME, LINE_TOKEN, URL, ACTIONS, CHROME_OPTIONS = load_env_vars()

def snapup():
    try:
        start_time = time.time()
        print("Starting the snapup function...")
        
        if os.environ.get('IN_DOCKER', 'False').lower() == 'true':
            display = Display(visible=0, size=(1024, 768))
            display.start()

        with webdriver.Chrome(options=CHROME_OPTIONS) as driver:
            driver.set_window_size(1024, 768)
            driver.get(URL)

            driver_actions = DriverActions(driver)
            for action in ACTIONS:
                try:
                    print(action)
                    driver_actions.execute(action)
                except Exception as e:
                    send_error_notify(f"Error executing action {action['action']}: {str(e)}", LINE_TOKEN, PROGRAM_NAME)

            if os.environ.get('IN_DOCKER', 'False').lower() == 'true':
                display.stop()

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total time taken: {elapsed_time:.2f} seconds")

    except Exception as e:
        send_error_notify(str(e), LINE_TOKEN, PROGRAM_NAME)


def main():
    print(f"{PROGRAM_NAME} started.")
    snapup()
    # result = load_actions_from_side('momo3.side')
    # print(json.dumps(result, indent=4))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        send_error_notify(f"Unexpected error: {str(e)}", LINE_TOKEN, PROGRAM_NAME)
