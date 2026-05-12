import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Opportunities.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update job cards to light theme
content = content.replace('relative bg-surface-900 border border-surface-800 p-6 rounded-3xl transition-all hover:border-surface-600 shadow-xl shadow-black/20', 'relative bg-white border border-slate-200 p-6 rounded-3xl transition-all hover:border-[#E85D3E] hover:shadow-md')
content = content.replace('text-white leading-tight mb-2 truncate group-hover:text-gold-400', 'text-slate-900 leading-tight mb-2 truncate group-hover:text-[#E85D3E]')
content = content.replace('bg-surface-800 flex items-center justify-center text-xs font-bold text-white border border-surface-700 shadow-inner', 'bg-slate-50 flex items-center justify-center text-xs font-bold text-slate-700 border border-slate-200 shadow-inner')
content = content.replace('text-gold-400 bg-gold-400/10 border border-gold-400/20', 'text-[#E85D3E] bg-[#E85D3E]/10 border border-[#E85D3E]/20')
content = content.replace('bg-surface-950 rounded-2xl shadow-inner ring-1 ring-surface-800', 'bg-slate-50 rounded-2xl shadow-inner ring-1 ring-slate-100')
content = content.replace('text-white\' : \'text-slate-300', 'text-slate-900\' : \'text-slate-500')

# Card Footer buttons
content = content.replace('bg-surface-800 hover:bg-surface-700 disabled:opacity-50 text-slate-300', 'bg-slate-100 hover:bg-slate-200 disabled:opacity-50 text-slate-600')
content = content.replace('text-slate-400 group-hover/radar:text-white', 'text-slate-400 group-hover/radar:text-[#E85D3E]')
content = content.replace('border-surface-800/80', 'border-slate-100')

# Adapt button colors
content = content.replace('from-gold-500/10 to-amber-500/10 hover:from-gold-500/20 hover:to-amber-500/20 text-gold-400 px-4 py-3.5 rounded-xl font-bold text-sm transition-all border border-gold-500/20 hover:border-gold-500/40', 'from-[#E85D3E]/10 to-[#E85D3E]/5 hover:from-[#E85D3E]/20 hover:to-[#E85D3E]/10 text-[#E85D3E] px-4 py-3.5 rounded-xl font-bold text-sm transition-all border border-[#E85D3E]/20 hover:border-[#E85D3E]/40')
content = content.replace('text-gold-500 group-hover/adapt:scale-110', 'text-[#E85D3E] group-hover/adapt:scale-110')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
