from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 1. 指定 ChromeDriver 路径
chrome_driver_path = "/usr/local/bin/chromedriver"

# 2. 创建 Chrome 浏览器实例
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

try:
    # 3. 打开 Google 登录页面
    driver.get("https://accounts.google.com/signin")

    # 4. 等待并输入邮箱
    wait = WebDriverWait(driver, 15)  # 最长等 15 秒

    email_input = wait.until(
        EC.presence_of_element_located((By.ID, "identifierId"))
    )
    email_input.clear()
    email_input.send_keys("yintao0906@gmail.com")
    email_input.send_keys(Keys.ENTER)

    # 5. 等待密码输入框出现并输入密码
    password_input = wait.until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    password_input.clear()
    password_input.send_keys("Yt008296!")
    password_input.send_keys(Keys.ENTER)

    # 6. 登录后，停留 5 秒
    time.sleep(5)

finally:
    # 7. 关闭浏览器
    driver.quit()
