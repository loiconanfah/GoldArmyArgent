import os
from playwright.sync_api import sync_playwright

def test_table_spacer():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @page {
        size: A4;
        margin: 0;
    }
    body {
        background: #1A0A2E;
        color: #E0D0FF;
        font-family: sans-serif;
        margin: 0;
        padding: 0;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .page-table {
        width: 100%;
        border-collapse: collapse;
    }
    .header-space {
        height: 60px; /* Top margin on every page */
    }
    .footer-space {
        height: 60px; /* Bottom margin on every page */
    }
    .content {
        padding: 0 48px; /* Left/right padding for text */
    }
    .main-box {
        background: #25103A;
        border: 2px solid #EC4899;
        height: 1500px; /* Force page break */
        padding: 20px;
    }
    </style>
    </head>
    <body>
        <table class="page-table">
            <thead>
                <tr><td><div class="header-space"></div></td></tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <div class="content">
                            <div class="main-box">
                                <h1>Page 1 Content</h1>
                                <p>This is page 1. Scroll down to see page 2.</p>
                                <div style="margin-top: 1000px;">
                                    <h1>Page 2 Content</h1>
                                    <p>This should be on page 2, and have a nice top margin!</p>
                                </div>
                            </div>
                        </div>
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr><td><div class="footer-space"></div></td></tr>
            </tfoot>
        </table>
    </body>
    </html>
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()
        page.set_content(html_content, wait_until="load")
        p_bytes = page.pdf(format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        browser.close()
        
        with open("scratch/test_margin_output.pdf", "wb") as f:
            f.write(p_bytes)
        print("Successfully generated scratch/test_margin_output.pdf")

if __name__ == "__main__":
    test_table_spacer()
