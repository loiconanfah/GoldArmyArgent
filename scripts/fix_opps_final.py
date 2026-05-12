import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Opportunities.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix Job Card background and border (it was stuck in surface-900)
content = content.replace('bg-surface-900 border border-slate-100 p-6 rounded-3xl transition-all hover:border-surface-600 shadow-xl shadow-black/20', 'bg-white border border-slate-200 p-6 rounded-3xl transition-all hover:border-[#E85D3E] hover:shadow-md')

# 2. Change Apply button to Violet
content = content.replace('bg-indigo-500 hover:bg-indigo-400 text-white px-4 py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-indigo-500/20', 'bg-violet-600 hover:bg-violet-500 text-white px-4 py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-violet-600/20')

# 3. Fix Empty State background (was stuck in surface-900)
content = content.replace('py-24 bg-surface-900/50 rounded-[2rem] border-dashed border-2 border-slate-100', 'py-24 bg-white rounded-[2rem] border-dashed border-2 border-slate-200')
content = content.replace('bg-surface-800 rounded-full mb-6 ring-1 ring-surface-700', 'bg-slate-50 rounded-full mb-6 ring-1 ring-slate-100')
content = content.replace('font-bold text-white mb-2 tracking-tight', 'font-bold text-slate-900 mb-2 tracking-tight')

# 4. Fix Analysis state background
content = content.replace('font-bold text-white mb-3 tracking-tight', 'font-bold text-slate-900 mb-3 tracking-tight')

# 5. Fix Score colors in template (some were still referencing white/slate-300)
content = content.replace('text-white mb-2 truncate group-hover:text-gold-400', 'text-slate-900 mb-2 truncate group-hover:text-[#E85D3E]')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
