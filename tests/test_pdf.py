import asyncio
import os
import sys

from core.cv_html_templates import TEMPLATES

async def main():
    template_builder = TEMPLATES["goldarmy"]["build"]
    
    cv_data = {
        "full_name": "Test User",
        "title": "Ingénieur Logiciel",
        "email": "test@example.com",
        "phone": "+33 6 00 00 00 00",
        "location": "Paris, France",
        "summary": "This is a summary to test the PDF layout.",
        "experiences": [
            {
                "title": "Developpeur",
                "company": "Google",
                "start_date": "2020",
                "end_date": "2023",
                "description": "Building stuff.",
            }
        ],
        "education": [],
        "projects": [],
        "skills": ["Python", "JavaScript"]
    }
    
    html = template_builder(cv_data)
    
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        await page.pdf(
            path="test_goldarmy.pdf",
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        await page.screenshot(path="test_goldarmy_screen.png", full_page=True)
        await browser.close()
        
if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
