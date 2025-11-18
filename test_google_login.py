from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time


# 1. ChromeDriver路径
chrome_driver_path = "/usr/local/bin/chromedriver"

# 创建Service对象, 把这个路径包装成一个Service，供Chrome启动时使用
service = Service(chrome_driver_path)
# 启动 Chrome浏览器，并且Selenium开始控制它
driver = webdriver.Chrome(service=service)

# 2. 打开Google登录页面
driver.get("https://accounts.google.com/signin/v3/identifier")
# 把浏览器窗口最大化显示
driver.maximize_window()

# 3. 输入邮箱
# 找到邮箱输入框
email_input = driver.find_element(By.ID, "identifierId")
# 输入你邮箱
email_input.send_keys("yintao0906@gmail.com")  # ← 改成你的 Gmail
# 按下回车（等于点下一步）
email_input.send_keys(Keys.ENTER)

# 4. 等待密码页面加载
time.sleep(5)

print("\n👉 请在 Chrome 中手动输入密码并完成登录…")
input("登录完成后，回到这里按 Enter，我将继续脚本...")

# 5. 登录成功后，等待 5 秒
print("登录成功！保持页面 5 秒后自动关闭浏览器…")
time.sleep(5)

# 6. 关闭浏览器
driver.quit()
print("浏览器已关闭。")
