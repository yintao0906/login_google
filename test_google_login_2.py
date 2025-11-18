from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 1. ChromeDriver 路径
chrome_driver_path = "/usr/local/bin/chromedriver"

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

try:
    # 2. 打开 Google 登录页面
    driver.get("https://accounts.google.com/signin/v3/identifier")
    driver.maximize_window()

    # 3. 显式等待：等邮箱输入框出现
    wait = WebDriverWait(driver, 15)  # 最多等 15 秒
    email_input = wait.until(
        EC.visibility_of_element_located((By.ID, "identifierId"))
    )

    # 4. 输入邮箱并回车
    email_input.send_keys("your_email@gmail.com")  # ← 换成你的邮箱
    email_input.send_keys(Keys.ENTER)

    # 5. 等待密码输入框出现（有可能被风控拦住，这里只是演示）
    pwd_input = wait.until(
        EC.visibility_of_element_located((By.NAME, "Passwd"))
    )

    pwd_input.send_keys("your_password")  # ← 换成你的密码（真实场景不推荐这样写死）
    pwd_input.send_keys(Keys.ENTER)

    # 6. 登录后等待几秒，看一下效果
    time.sleep(5)

except Exception as e:
    print("出错了：", e)

finally:
    # 调试的时候可以先把这行注释掉，这样浏览器不会自动关
    time.sleep(5)
    driver.quit()
