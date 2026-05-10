from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        print("Playwright launched successfully!")
        browser.close()
except Exception as e:
    print(f"Playwright failed: {e}")
