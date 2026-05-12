import re

file_path = r"C:\Users\Utilisateur\PycharmProjects\GoldArmyArgent\core\cv_html_templates.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Replace max-width limits with 100% and min-height 100vh on .page
text = re.sub(r'\.page\s*\{\s*display:\s*flex;\s*max-width:\s*[0-9]+px;\s*margin:\s*0\s+auto;', 
              r'.page{display:flex;width:100%;min-height:100vh;margin:0;', text)

# 2. Add fixed background covers for the sidebars to guarantee they NEVER stop on long pages.
# GoldArmy Sidebar
if ".sidebar{width:220px;background:#1A1A2E;" in text:
    text = text.replace(
        "body{font-family:'Inter', sans-serif;background:#F8FAFC;color:#1E293B;margin:0;padding:0;}",
        "body{font-family:'Inter', sans-serif;background:#F8FAFC;color:#1E293B;margin:0;padding:0;} body::before{content:'';position:fixed;top:0;left:0;bottom:0;width:220px;background:#1A1A2E;z-index:-1;}"
    )

# Executive Sidebar
if ".sidebar{width:220px;background:#161B22;border-right:1px solid #6EE7B722;" in text:
    text = text.replace(
        "body{font-family:'Inter', sans-serif;background:#0D1117;color:#E6EDF3;margin:0;padding:0;}",
        "body{font-family:'Inter', sans-serif;background:#0D1117;color:#E6EDF3;margin:0;padding:0;} body::before{content:'';position:fixed;top:0;left:0;bottom:0;width:220px;background:#161B22;border-right:1px solid #6EE7B722;z-index:-1;}"
    )

# Creatif Sidebar
if ".sidebar{width:230px;background:#0F0718;" in text:
    text = text.replace(
        "body{font-family:'Outfit', sans-serif;background:#000000;color:#E2E8F0;margin:0;padding:0;}",
        "body{font-family:'Outfit', sans-serif;background:#000000;color:#E2E8F0;margin:0;padding:0;} body::before{content:'';position:fixed;top:0;left:0;bottom:0;width:230px;background:#0F0718;z-index:-1;}"
    )

# Neon Tech Sidebar
if ".sidebar{width:230px;background:#111128;border-right:1px solid #00E5FF22;" in text:
    text = text.replace(
        "body{font-family:'Space Grotesk', sans-serif;background:#0A0A1A;color:#E2E8F0;margin:0;padding:0;}",
        "body{font-family:'Space Grotesk', sans-serif;background:#0A0A1A;color:#E2E8F0;margin:0;padding:0;} body::before{content:'';position:fixed;top:0;left:0;bottom:0;width:230px;background:#111128;border-right:1px solid #00E5FF22;z-index:-1;}"
    )

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: CSS templates patched.")
