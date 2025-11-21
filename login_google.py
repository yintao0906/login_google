from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 1. Specify the ChromeDriver path.
chrome_driver_path = "/usr/local/bin/chromedriver"

# 2. Create a Chrome browser instance.
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

try:
    # 3. Open the Google login page.
    driver.get("https://accounts.google.com/signin")

    # 4. Wait and enter the email.
    wait = WebDriverWait(driver, 15)  # 最长等 15 秒

    email_input = wait.until(
        EC.presence_of_element_located((By.ID, "identifierId"))
    )
    email_input.clear()
    email_input.send_keys("yintao0906@gmail.com")
    email_input.send_keys(Keys.ENTER)

    # 5. Wait for the password field to appear and enter the password.
    password_input = wait.until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    password_input.clear()
    password_input.send_keys("Yt008296!")
    password_input.send_keys(Keys.ENTER)

    # 6. After logging in, stay for 5 seconds.
    time.sleep(5)

finally:
    # 7. Close the browser.
    driver.quit()
