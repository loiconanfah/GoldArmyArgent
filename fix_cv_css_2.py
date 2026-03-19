import os
import re

file_path = r"C:\Users\Utilisateur\PycharmProjects\GoldArmyArgent\core\cv_html_templates.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    "*{margin:0;padding:0;box-sizing:border-box;}",
    "@page{size: A4; margin: 0;} html,body{width:210mm;height:100%;} *{margin:0;padding:0;box-sizing:border-box;}"
)

text = text.replace("min-height:100vh;", "min-height:100%;")
text = text.replace("max-width:840px;", "width:100%;")
text = text.replace("max-width:860px;", "width:100%;")
text = text.replace("max-width:800px;", "width:100%;")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS")
