import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Opportunities.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add SignalIcon to imports
if 'SignalIcon' not in content:
    content = content.replace('SparklesIcon,', 'SparklesIcon,\n    SignalIcon,')

# 2. Replace the emoji in the template
content = content.replace('<div class="date-num">📡</div>', '<div class="date-num flex items-center justify-center bg-[#E85D3E]/10 rounded-lg w-10 h-10"><SignalIcon class="w-6 h-6 text-[#E85D3E]" /></div>')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
