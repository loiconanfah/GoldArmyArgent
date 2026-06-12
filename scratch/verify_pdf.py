import fitz

def verify():
    doc = fitz.open("scratch/test_margin_output.pdf")
    print(f"Total pages: {len(doc)}")
    
    # Check page 2 (index 1) text positions
    page2 = doc[1]
    text_instances = page2.get_text("blocks")
    print("Page 2 Text blocks:")
    for b in text_instances:
        # block rect is b[0:4] (x0, y0, x1, y1)
        print(f"  Rect: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) - Text: {repr(b[4].strip())}")
        
    # Check background color at (5, 5) on page 1
    # We can render page to a small pixmap and inspect pixel
    pix = page2.get_pixmap()
    # Check pixel value at (5, 5)
    # pix.width and pix.height tell us size. Let's get color
    # page width/height in points is usually 595.3 x 841.9 (A4)
    # pixmap resolution depends on dpi (default 96 or 72, which maps to size)
    # Let's inspect RGB at pixel index corresponding to (5, 5) in points
    # Points to pixels conversion factor:
    factor_x = pix.width / page2.rect.width
    factor_y = pix.height / page2.rect.height
    px = int(5 * factor_x)
    py = int(5 * factor_y)
    
    color = pix.pixel(px, py)
    print(f"Pixel color at point (5, 5) on page 2: RGB {color}")
    doc.close()

if __name__ == "__main__":
    verify()
