import os
import re

files_to_patch = [
    r"d:\GoldArmyArgent\frontend\src\views\AgentChat.vue",
    r"d:\GoldArmyArgent\frontend\src\views\CRM.vue",
    r"d:\GoldArmyArgent\frontend\src\views\Dashboard.vue",
    r"d:\GoldArmyArgent\frontend\src\views\Opportunities.vue",
    r"d:\GoldArmyArgent\frontend\src\views\Reseaux.vue"
]

import_statement = "import { authFetch } from '../utils/auth'\n"

for filepath in files_to_patch:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If already patched, skip
    if "import { authFetch }" in content:
        continue

    # Add import right after <script setup> or <script>
    if "<script setup>" in content:
        content = content.replace("<script setup>", f"<script setup>\n{import_statement}")
    else:
        content = content.replace("<script>", f"<script>\n{import_statement}")

    # Replace fetch( with authFetch(
    content = content.replace("await fetch(", "await authFetch(")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Successfully injected authFetch into Vue components.")
