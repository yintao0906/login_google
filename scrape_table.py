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
        url = "https://www.w3schools.com/html/html_tables.asp"
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        # 1. 网页标题
        print("页面标题：", driver.title)

        # 2. 抓取所有 a 标签（链接）
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"页面上共有 {len(links)} 个链接（仅打印前 10 个）：")
        for a in links[:10]:
            text = a.text.strip()
            href = a.get_attribute("href")
            print(" - 文本：", text or "<无文本>", " | URL：", href)

        # 3. 抓取表格数据
        # 找到 id 为 customers 的表格
        table = wait.until(
            EC.presence_of_element_located((By.ID, "customers"))
        )

        # 表头（th）
        header_cells = table.find_elements(By.CSS_SELECTOR, "tr th")
        headers = [h.text.strip() for h in header_cells]
        print("\n表头：", headers)

        # 表体（每一行 tr，跳过第 0 行表头）
        rows = table.find_elements(By.CSS_SELECTOR, "tr")[1:]

        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [c.text.strip() for c in cells]
            data.append(row_data)

        print("\n表格数据：")
        for row in data:
            print(row)

    finally:
        import time
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    main()
