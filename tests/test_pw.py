import asyncio
import sys

async def main():
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as pw:
            print("Launching browser...")
            browser = await pw.chromium.launch()
            print("Browser launched. Opening page...")
            page = await browser.new_page()
            print("Setting content...")
            await page.set_content("<h1>Hello</h1>", wait_until="networkidle")
            print("Generating PDF...")
            pdf_bytes = await page.pdf(format="A4")
            print("Success, pdf size:", len(pdf_bytes))
            await browser.close()
    except Exception as e:
        print(f"PLAYWRIGHT_ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
