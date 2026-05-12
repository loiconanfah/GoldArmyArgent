import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Opportunities.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Change Apply button to Pro Slate/Black
content = content.replace('bg-violet-600 hover:bg-violet-500 text-white px-4 py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-violet-600/20', 'bg-slate-900 hover:bg-slate-800 text-white px-4 py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-slate-900/20')

# 2. Also update the shadow in case it was missed
content = content.replace('shadow-violet-600/20', 'shadow-slate-900/20')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
