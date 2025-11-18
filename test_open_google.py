from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os


def main():
    # 1. 指定 chromedriver 的路径
    # 把下面路径改成你实际的 chromedriver 路径
    driver_path = os.path.expanduser("/usr/local/bin/chromedriver")

    service = Service(driver_path)

    # 2. 设置 Chrome 参数（可选）
    options = Options()
    options.add_argument("--start-maximized")  # 启动时最大化窗口

    # 3. 启动浏览器
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 4. 打开 Google 首页
        driver.get("https://www.google.com")

        print("当前页面标题：", driver.title)

        # 等 5 秒看看页面
        time.sleep(5)
    finally:
        # 5. 关闭浏览器
        driver.quit()


if __name__ == "__main__":
    main()
