import os
import asyncio
import io
from playwright.sync_api import sync_playwright

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "pw-browsers")

def _generate_pdf_sync(html: str) -> bytes:
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as pw:
            # Optimized settings
            browser = pw.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
            page = browser.new_page()
            print("Setting content...")
            page.set_content(html, wait_until="load", timeout=20000)
            print("Generating PDF...")
            p_bytes = page.pdf(
                format="A4", print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
            )
            browser.close()
            return p_bytes
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    test_html = """
    <html>
    <head><style>body { font-family: sans-serif; color: gold; background: black; padding: 50px; }</style></head>
    <body>
        <h1>GoldArmy PDF Test</h1>
        <p>Testing Playwright with optimized settings.</p>
    </body>
    </html>
    """
    try:
        pdf_bytes = _generate_pdf_sync(test_html)
        print(f"Success! Generated {len(pdf_bytes)} bytes.")
        with open("scratch/test_output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("Test PDF saved to scratch/test_output.pdf")
    except Exception as e:
        print(f"Test failed: {e}")
