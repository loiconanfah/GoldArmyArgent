import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "pw-browsers")

from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as pw:
        # We need to make sure the browser is installed in this specific path
        print(f"Checking Playwright in {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
        browser = pw.chromium.launch(args=["--no-sandbox"])
        print("Playwright launched successfully!")
        browser.close()
except Exception as e:
    print(f"Playwright failed: {e}")
