from selenium import webdriver
import json

def execute_side_file(side_file_path):
    # 讀取.side檔案
    with open(side_file_path, 'r', encoding='utf-8') as file:
        side_content = json.load(file)

    # 設定WebDriver
    driver = webdriver.Chrome()

    # 遍歷測試案例
    for test_case in side_content['tests']:
        for command in test_case['commands']:
            action = command['command']
            target = command['target']
            value = command['value']

            # 根據指令執行動作
            if action == 'open':
                driver.get(target)
            elif action == 'click':
                element = driver.find_element_by_css_selector(target)
                element.click()
            elif action == 'sendKeys':
                element = driver.find_element_by_css_selector(target)
                element.send_keys(value)
            # ... 你可以根據需要增加其他指令的處理

    # 清理資源
    driver.quit()

# 執行
side_file_path = '你的.side檔案路徑'
execute_side_file(side_file_path)
