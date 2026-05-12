import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the old double definitions later in the file
# pattern = r'// Build the theme list.*?isDownloadingDocx = ref\(false\)'
pattern = r'// Build the theme list from the mobile-identical TS templates.*?isDownloadingDocx = ref\(false\)'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Also fix any remaining dark mode classes in prose
content = content.replace('prose prose-invert', 'prose prose-slate')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
