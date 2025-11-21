from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def main():
    # 1. 连接到“已经打开、已经登录”的 Chrome（调试端口 9222）
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(options=options)

    try:
        # 2. 打开 Google Gemini 页面
        driver.get("https://gemini.google.com/app")

        # 等待输入框出现
        wait = WebDriverWait(driver, 30)
        input_box = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[contenteditable='true']")
            )
        )

        # 3. 发送 prompt
        prompt = "Write a 3-sentence summary about machine learning."
        input_box.send_keys(prompt)
        input_box.send_keys(Keys.ENTER)
        print("Prompt sent. Waiting for response...")

        # 4. 等待 Gemini 生成回答（简单粗暴先等 15 秒）
        time.sleep(15)

        # 5. 先尝试用 message-content 抓最新回答
        response_text = ""

        contents = driver.find_elements(By.CSS_SELECTOR, "message-content")
        if contents:
            latest = contents[-1]
            response_text = driver.execute_script(
                "return arguments[0].innerText;", latest
            ).strip()
        else:
            # 如果没有 message-content，备用方案：抓所有 p[data-path-to-node]
            print("No <message-content> found, fallback to <p[data-path-to-node]>.")
            paras = driver.find_elements(By.CSS_SELECTOR, "p[data-path-to-node]")
            parts = []
            for p in paras:
                txt = p.text.strip()
                if txt:
                    parts.append(txt)
            response_text = "\n".join(parts)

        # 6. 保存到文本文件
        with open("gemini_output.txt", "w", encoding="utf-8") as f:
            f.write("PROMPT:\n")
            f.write(prompt + "\n\n")
            f.write("RESPONSE:\n")
            f.write(response_text)

        print("Output saved to gemini_output.txt")

    finally:
        # 想自动关浏览器就改成 driver.quit()
        # driver.quit()
        pass


if __name__ == "__main__":
    main()
