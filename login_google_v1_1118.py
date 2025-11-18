from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# 1. 指定ChromeDriver路径
chrome_driver_path = "/usr/local/bin/chromedriver"

# 2. 创建Chrome浏览器实例
# driver = webdriver.Chrome(executable_path=chrome_driver_path)
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# 3. 打开Google登录页面
driver.get("https://accounts.google.com/signin")

# 4. 找到邮箱输入框，输入邮箱
email_input = driver.find_element(By.ID, "identifierId")
email_input.send_keys("yintao0906@gmail.com")
email_input.send_keys(Keys.RETURN)

time.sleep(2)  # 等密码页面加载

# 5. 输入密码
password_input = driver.find_element(By.NAME, "password")
password_input.send_keys("Yt008296!")
password_input.send_keys(Keys.RETURN)

# 6. 登陆后停留 5 秒再自动关闭
time.sleep(5)
driver.close()
