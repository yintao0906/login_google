from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)

    try:
        # 1. 打开登录页面
        driver.get("https://the-internet.herokuapp.com/login")

        # 2. 等待用户名输入框出现
        wait = WebDriverWait(driver, 10)
        username_input = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button.radius")

        # 3. 输入用户名和密码
        username_input.send_keys("tomsmith")
        password_input.send_keys("SuperSecretPassword!")

        # 4. 点击登录按钮
        login_button.click()

        # 5. 等待登录成功的提示信息
        success_message = wait.until(
            EC.presence_of_element_located((By.ID, "flash"))
        )
        print("登录结果提示：", success_message.text.strip())

    finally:
        # 停 5 秒，看一下结果，再退出
        import time
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    main()
