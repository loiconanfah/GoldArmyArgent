import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Change the download button color from slate-900 to orange
old_style = 'bg-gradient-to-r from-slate-900 to-slate-800 hover:from-[#E85D3E] hover:to-gold-600'
new_style = 'bg-gradient-to-r from-[#E85D3E] to-[#C44A2D] hover:from-[#C44A2D] hover:to-[#E85D3E]'

# Also fix the shadow
old_shadow = 'shadow-2xl shadow-slate-900/20'
new_shadow = 'shadow-2xl shadow-[#E85D3E]/30'

content = content.replace(old_style, new_style)
content = content.replace(old_shadow, new_shadow)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
