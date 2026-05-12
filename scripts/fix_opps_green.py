import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Opportunities.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Change Apply button to Green Gradient
old_btn = 'bg-slate-900 hover:bg-slate-800 text-white px-4 py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-slate-900/20'
new_btn = 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-4 py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-emerald-600/20'

content = content.replace(old_btn, new_btn)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
