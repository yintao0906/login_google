from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def main():
    # 设置 Chrome 启动选项
    options = Options()
    options.add_argument("--start-maximized")

    # 因为 chromedriver 已在 /usr/local/bin，所以 Selenium 能自动找到
    driver = webdriver.Chrome(options=options)

    # 打开网页
    driver.get("https://www.google.com")

    # 停 5 秒，方便看到效果
    import time
    time.sleep(5)

    # 退出浏览器
    driver.quit()

if __name__ == "__main__":
    main()
