import os
import re

FILE_PATH = r"C:\Users\Utilisateur\PycharmProjects\GoldArmyArgent\core\cv_html_templates.py"

def fix_all_templates():
    if not os.path.exists(FILE_PATH):
        print(f"Error: {FILE_PATH} not found.")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Template-specific Sidebar fixes
    sidebar_themes = {
        "goldarmy": {"width": "220px", "bg": "#1A1A2E"},
        "executive": {"width": "220px", "bg": "#161B22"},
        "creatif":   {"width": "220px", "bg": "#0F0718"},
        "neon_tech": {"width": "230px", "bg": "#111128"},
    }

    # GoldArmy
    if 'background:#1A1A2E;padding:28px 18px;flex-shrink:0;' in content:
        content = content.replace(
            "body{font-family:'Inter',sans-serif;font-size:11px;line-height:1.5;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;}",
            "@page{size: A4; margin: 0;} *{margin:0;padding:0;box-sizing:border-box;} body{font-family:'Inter',sans-serif;font-size:11px;line-height:1.5;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;} body::before{content:'';position:fixed;top:0;left:0;bottom:0;width:220px;background:#1A1A2E;z-index:-1;}"
        )
        content = content.replace(".page{display:flex;max-width:900px;margin:0 auto;}", ".page{display:flex;width:100%;min-height:100%;}")
        content = content.replace(".sidebar{width:220px;background:#1A1A2E;padding:28px 18px;flex-shrink:0;}", ".sidebar{width:220px;padding:28px 18px;flex-shrink:0;}")

    # Executive
    if 'background:#161B22;padding:28px 18px;border-right:1px solid #6EE7B722;' in content:
        content = content.replace(
            "body{font-family:'Inter',sans-serif;font-size:11px;background:#0D1117;color:#E0E0FF;-webkit-print-color-adjust:exact;print-color-adjust:exact;}",
            "@page{size: A4; margin: 0;} body{font-family:'Inter',sans-serif;font-size:11px;background:#0D1117;color:#E0E0FF;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;} body::before{content:'';position:fixed;top:0;left:0;bottom:0;width:220px;background:#161B22;border-right:1px solid #6EE7B722;z-index:-1;}"
        )
        content = content.replace(".page{display:flex;max-width:900px;margin:0 auto;min-height:100%;}", ".page{display:flex;width:100%;min-height:100%;}")
        content = content.replace(".sidebar{width:220px;flex-shrink:0;background:#161B22;padding:28px 18px;border-right:1px solid #6EE7B722;}", ".sidebar{width:220px;padding:28px 18px;flex-shrink:0;}")

    # Creatif
    if 'background:#0F0718;padding:28px 18px;flex-shrink:0;' in content:
        content = content.replace(
            "body{font-family:'Nunito',sans-serif;font-size:11px;background:#1A0A2E;color:#E0D0FF;-webkit-print-color-adjust:exact;print-color-adjust:exact;}",
            "@page{size: A4; margin: 0;} body{font-family:'Nunito',sans-serif;font-size:11px;background:#1A0A2E;color:#E0D0FF;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;} body::before{content:'';position:fixed;top:0;left:0;bottom:0;width:220px;background:#0F0718;z-index:-1;}"
        )
        content = content.replace(".page{display:flex;max-width:900px;margin:0 auto;}", ".page{display:flex;width:100%;min-height:100%;}")
        content = content.replace(".sidebar{width:220px;background:#0F0718;padding:28px 18px;flex-shrink:0;}", ".sidebar{width:220px;padding:28px 18px;flex-shrink:0;}")

    # Neon Tech
    if 'background:#111128;padding:28px 18px;border-right:1px solid #00E5FF22;flex-shrink:0;' in content:
        content = content.replace(
            "body{font-family:'Inter',sans-serif;background:#0D0D1A;color:#E0E0FF;font-size:11px;-webkit-print-color-adjust:exact;print-color-adjust:exact;}",
            "@page{size: A4; margin: 0;} body{font-family:'Inter',sans-serif;background:#0D0D1A;color:#E0E0FF;font-size:11px;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;} body::before{content:'';position:fixed;top:0;left:0;bottom:0;width:230px;background:#111128;border-right:1px solid #00E5FF22;z-index:-1;}"
        )
        content = content.replace(".page{width:100%;margin:0 auto;display:flex;}", ".page{display:flex;width:100%;min-height:100%;}")
        content = content.replace(".sidebar{width:230px;background:#111128;padding:28px 18px;border-right:1px solid #00E5FF22;flex-shrink:0;}", ".sidebar{width:230px;padding:28px 18px;flex-shrink:0;}")

    # Minimaliste
    if 'build_minimaliste' in content:
        content = content.replace(
            "body{font-family:'Inter',sans-serif;font-size:11px;background:#fff;color:#222;-webkit-print-color-adjust:exact;print-color-adjust:exact;}",
            "@page{size: A4; margin: 0;} body{font-family:'Inter',sans-serif;font-size:11px;background:#fff;color:#222;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}"
        )
    
    # Classique
    if 'build_classique' in content:
        content = content.replace(
            "body{font-family:'EB Garamond',serif;font-size:12px;background:#fff;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact;}",
            "@page{size: A4; margin: 0;} body{font-family:'EB Garamond',serif;font-size:12px;background:#fff;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}"
        )
        content = content.replace(".page{max-width:820px;margin:0 auto;padding:50px 60px;}", ".page{width:100%;padding:50px 60px;}")

    # Scandinave
    if 'build_scandinave' in content:
        content = content.replace(
            "body{font-family:'DM Sans',sans-serif;background:#FAFAF7;color:#2B2B2B;font-size:11px;line-height:1.6;-webkit-print-color-adjust:exact;print-color-adjust:exact;}",
            "@page{size: A4; margin: 0;} body{font-family:'DM Sans',sans-serif;background:#FAFAF7;color:#2B2B2B;font-size:11px;line-height:1.6;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}"
        )
        content = content.replace(".page{max-width:820px;margin:0 auto;padding:52px 60px;}", ".page{width:100%;padding:52px 60px;}")

    # Timeline
    if 'build_timeline' in content:
        content = content.replace(
            "body{font-family:'Nunito',sans-serif;background:#F9F5F0;color:#2D2D2D;font-size:11px;-webkit-print-color-adjust:exact;print-color-adjust:exact;}",
            "@page{size: A4; margin: 0;} body{font-family:'Nunito',sans-serif;background:#F9F5F0;color:#2D2D2D;font-size:11px;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}"
        )
        content = re.sub(r'<div style="max-width:900px;margin:0 auto;">', '<div style="width:100%;">', content)

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: Templates patched via script.")

if __name__ == "__main__":
    fix_all_templates()
