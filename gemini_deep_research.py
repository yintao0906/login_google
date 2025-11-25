"""
gemini_deep_research.py

Full Deep Research automation for Google Gemini:

  1. Attach to an already-open & logged-in Chrome (remote debugging port 9222).
  2. Open Gemini home page.
  3. Find the input box on the home screen and send a Deep Research prompt.
     - By default, uses TEST_PROMPT below.
     - You can override it by passing a custom prompt as command-line arguments.
       Example:
         python gemini_deep_research.py "Deep research: my custom topic..."
  4. Wait for the Deep Research PLAN card.
  5. Pause a few seconds, then click "Start research".
  6. Wait for the final report (markdown content) to appear in Gemini.
  7. Open the Gemini "Thoughts" dropdown (if available) and capture its content.
  8. Click "Share & export" → "Export to Google Docs".
  9. Switch to the newly opened Google Docs tab (if any).
 10. Build the “Download as Markdown (.md)” URL and navigate to it
     (equivalent to File → Download → Markdown (.md)).
 11. Wait for the Markdown file to be downloaded into ~/Downloads
     and rename the newest .md file as “YYYYMMDD-HHMMSS Gemini.md”.
 12. Append the captured Gemini Thoughts as a “Gemini Thoughts” section
     at the end of the Markdown file.

"""


import re
import sys
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------


def get_inner_text(driver, element) -> str:
    """
    Read element.innerText via JavaScript.
    This preserves line breaks better than .text.
    """
    return driver.execute_script("return arguments[0].innerText;", element).strip()


def extract_doc_id(doc_url: str) -> str:
    """
    Extract the Google Docs document ID from a docs.google.com URL.

    Example:
      https://docs.google.com/document/d/ABCDEFG1234567/edit
      -> returns 'ABCDEFG1234567'
    """
    m = re.search(r"/document/d/([^/]+)/", doc_url)
    if not m:
        raise ValueError(f"Cannot extract doc id from URL: {doc_url}")
    return m.group(1)


def wait_for_new_md_and_rename(download_dir: Path, before_files: set[str]) -> Path:
    """
    After triggering the Markdown download in Chrome, wait for a new .md
    file to appear in download_dir, then rename the newest .md file to
    'YYYYMMDD-HHMMSS Gemini.md'. Return the new Path.
    """
    timeout = 60          # seconds
    poll_interval = 2     # seconds
    elapsed = 0

    while elapsed < timeout:
        md_files = list(download_dir.glob("*.md"))
        names_now = {f.name for f in md_files}

        # Detect any new .md file
        new_names = names_now - before_files
        if new_names:
            break

        time.sleep(poll_interval)
        elapsed += poll_interval

    # If no brand-new file detected, just pick the newest .md file
    md_files = list(download_dir.glob("*.md"))
    if not md_files:
        raise FileNotFoundError("No .md file found in Downloads folder.")

    newest = max(md_files, key=lambda p: p.stat().st_mtime)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    new_name = f"{ts} Gemini.md"
    new_path = newest.with_name(new_name)
    newest.rename(new_path)

    return new_path


def capture_gemini_thoughts(driver, wait: WebDriverWait) -> str:
    """
    Capture the Gemini 'Thoughts' / '思路' panel content.

    Works for both Chinese and English UI.
    Does NOT rely on specific headings.
    Finds <thinking-panel ... aria-expanded="true"> instead.
    """
    try:
        # ---- 1. Find the "Thoughts" / "思路" toggle button ----
        def find_toggle(d):
            items = d.find_elements(
                By.XPATH,
                "//span[contains(., 'Thoughts') or contains(., '思路')]"
            )
            for el in items:
                if el.is_displayed():
                    return el
            return None

        toggle = wait.until(find_toggle)
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            toggle
        )
        toggle.click()
        print("Opened Thoughts dropdown.")
        time.sleep(1.2)  # Allow panel to render

        # ---- 2. Find the expanded <thinking-panel> element ----
        panel = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//thinking-panel[@aria-expanded='true']")
            )
        )

        # ---- 3. Extract full innerText using helper ----
        text = get_inner_text(driver, panel)

        print(f"Captured Thoughts text (length={len(text)}).")
        return text

    except Exception as e:
        print("Failed to capture Thoughts:", e)
        return ""


# ---------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------


def main(prompt: str) -> None:
    # -------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------
    DEBUGGER_ADDRESS = "127.0.0.1:9222"  # Chrome launched with --remote-debugging-port=9222
    GEMINI_URL = "https://gemini.google.com/app"

    # Timeouts
    MAX_WAIT_PLAN_SECONDS = 300    # for Deep Research plan
    MAX_WAIT_REPORT_SECONDS = 900  # for final report & Docs export

    # Mac Downloads folder
    download_dir = Path.home() / "Downloads"

    # Extra delay after PLAN appears, before clicking "Start research"
    PLAN_PAUSE_SECONDS = 3

    # -------------------------------------------------------------
    # 1. Attach to already-open Chrome
    # -------------------------------------------------------------
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUGGER_ADDRESS)
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(GEMINI_URL)

        wait_plan = WebDriverWait(driver, MAX_WAIT_PLAN_SECONDS)
        wait_report = WebDriverWait(driver, MAX_WAIT_REPORT_SECONDS)

        # ---------------------------------------------------------
        # 2. Locate the real editable input and send the prompt
        # ---------------------------------------------------------

        def find_homepage_editor(d):
            """
            Locate the actual editable DIV inside Gemini's homepage input area.

            Typical DOM structure:

              <div class="input-container input-gradient ...">
                ...
                <input-area-v2 ...>
                  ...
                  <div class="text-input-field_textarea-inner ...">
                    <div contenteditable="true">  <-- we want THIS
                      ...
                    </div>
                  </div>
                ...
              </input-area-v2>

            Strategy:
              1) Find all "text-input-field_textarea-inner" wrappers.
              2) For each wrapper, search for visible & enabled
                 child div[contenteditable="true"].
              3) If none found, fall back to any visible div[contenteditable="true"].
            """
            # First, find all wrappers
            wrappers = d.find_elements(
                By.CSS_SELECTOR,
                "div.text-input-field_textarea-inner"
            )
            for w in wrappers:
                if not w.is_displayed():
                    continue

                editors = w.find_elements(
                    By.CSS_SELECTOR,
                    "div[contenteditable='true']"
                )
                for e in editors:
                    if e.is_displayed() and e.is_enabled():
                        return e

            # Fallback: any visible contenteditable div on the page
            editors = d.find_elements(
                By.CSS_SELECTOR,
                "div[contenteditable='true']"
            )
            for e in editors:
                if e.is_displayed() and e.is_enabled():
                    return e

            return None

        # Wait until an editable DIV is available
        editor = WebDriverWait(driver, 60).until(
            lambda d: find_homepage_editor(d)
        )

        # Scroll the editor into view
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            editor,
        )

        # Click to focus the editor
        editor.click()
        time.sleep(0.3)

        # Send the Deep Research prompt
        editor.send_keys(prompt)
        editor.send_keys(Keys.ENTER)

        print("Prompt sent. Waiting for Deep Research PLAN...")

        # ---------------------------------------------------------
        # 3. Wait for Deep Research PLAN card
        # ---------------------------------------------------------
        wait_plan.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.research-step-description")
            )
        )
        print("Deep Research plan is ready.")

        # Optional: pause a few seconds so the user can see the plan
        if PLAN_PAUSE_SECONDS > 0:
            time.sleep(PLAN_PAUSE_SECONDS)

        # ---------------------------------------------------------
        # 4. Click "Start research"
        # ---------------------------------------------------------
        start_button_xpath = (
            "//span[normalize-space()='Start research']/ancestor::button"
        )

        clicked = False
        for attempt in range(3):
            try:
                start_button = wait_plan.until(
                    EC.element_to_be_clickable((By.XPATH, start_button_xpath))
                )

                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    start_button,
                )

                start_button.click()
                print(f"Clicked 'Start research' (attempt {attempt + 1}).")
                clicked = True
                break

            except StaleElementReferenceException:
                print(
                    f"'Start research' button became stale (attempt {attempt + 1}), retrying..."
                )
                time.sleep(1)

        if not clicked:
            raise RuntimeError("Failed to click 'Start research' after 3 attempts.")

        print("Clicked 'Start research'. Waiting for final report...")

        # ---------------------------------------------------------
        # 5. Wait for final report (markdown view in Gemini)
        # ---------------------------------------------------------
        wait_report.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div#extended-response-markdown-content.markdown-main-panel",
                )
            )
        )
        print("Final markdown report is visible in Gemini.")

        # ---------------------------------------------------------
        # 6. Capture Gemini Thoughts (if available)
        # ---------------------------------------------------------
        thoughts_text = capture_gemini_thoughts(driver, wait_report)

        # ---------------------------------------------------------
        # 7. Click "Share & export" → "Export to Google Docs"
        # ---------------------------------------------------------
        share_button = wait_report.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(., '分享和导出') "
                    "or contains(., 'Share & export')]",
                )
            )
        )
        share_button.click()
        print("Clicked 'Share & export'.")

        export_to_docs = wait_report.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//span[contains(., '导出到 Google 文档') "
                    "or contains(., 'Export to Google Docs')]",
                )
            )
        )

        # Record window handles BEFORE clicking "Export to Google Docs"
        original_handles = driver.window_handles

        export_to_docs.click()
        print("Clicked 'Export to Google Docs'.")

        # ---------------------------------------------------------
        # 8. Switch to Google Docs tab (or stay on current tab)
        # ---------------------------------------------------------
        try:
            # Case 1: Google Docs opens in a new window/tab
            wait_report.until(EC.new_window_is_opened(original_handles))

            new_handles = driver.window_handles
            new_doc_handles = [h for h in new_handles if h not in original_handles]

            if new_doc_handles:
                driver.switch_to.window(new_doc_handles[0])
                print("Switched to new Google Docs tab.")
            else:
                print("New window detected but no new handle found. Staying on current tab.")
        except TimeoutException:
            # Case 2: Google Docs reuses the current tab
            print("No new tab opened. Google Docs probably loaded in the current tab.")

        # Wait until the current URL is a Docs URL
        wait_report.until(
            lambda d: d.current_url and "docs.google.com" in d.current_url
        )

        doc_url = driver.current_url
        print("Google Docs URL:", doc_url)

        # ---------------------------------------------------------
        # 9. Build "Download as Markdown" URL and trigger download
        # ---------------------------------------------------------
        doc_id = extract_doc_id(doc_url)
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=md"
        print("Navigating to Markdown export URL:", export_url)

        # Record existing .md filenames before download
        before_md_names = {f.name for f in download_dir.glob("*.md")}

        # Trigger the download
        driver.get(export_url)
        print("Chrome is downloading the Markdown file...")

        # ---------------------------------------------------------
        # 10. Wait for the new .md file in ~/Downloads and rename it
        # ---------------------------------------------------------
        saved_path = wait_for_new_md_and_rename(download_dir, before_md_names)
        print("Markdown downloaded and renamed to:", saved_path)

        # ---------------------------------------------------------
        # 11. Append Gemini Thoughts (if captured) to the Markdown file
        # ---------------------------------------------------------
        if thoughts_text:
            try:
                with saved_path.open("a", encoding="utf-8") as f:
                    f.write("\n\n---\n## Gemini Thoughts\n\n")
                    f.write(thoughts_text)
                print("Appended Gemini Thoughts to Markdown file.")
            except Exception as e:
                print("Failed to append Gemini Thoughts to Markdown file:", repr(e))
        else:
            print("No Gemini Thoughts captured; skipping append step.")

    finally:
        # Keep Chrome open for demonstration.
        # To close the browser automatically, uncomment:
        # driver.quit()
        pass


# Default prompt (used when no command-line arguments are provided)
TEST_PROMPT = "Deep research: Explain how LLMs are used in asset pricing."


if __name__ == "__main__":
    # If the user provides arguments, treat them as a custom Deep Research prompt.
    # Example:
    #   python gemini_deep_research.py "Deep research: my custom topic"
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = TEST_PROMPT

    main(user_prompt)
