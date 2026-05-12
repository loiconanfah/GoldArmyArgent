import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Backgrounds & Borders
content = content.replace('bg-surface-950', 'bg-[#F9FAFB]')
content = content.replace('bg-surface-900', 'bg-white')
content = content.replace('border-surface-800', 'border-slate-200')
content = content.replace('border-surface-700', 'border-slate-100')
content = content.replace('bg-surface-800', 'bg-white')

# 2. Text Colors
content = content.replace('text-white', 'text-slate-900') # Watch out for white text on colored bgs
# Re-fix some cases where white text IS needed (e.g. inside colored buttons)
content = content.replace('bg-indigo-600 text-slate-900', 'bg-indigo-600 text-white')
content = content.replace('bg-emerald-600 text-slate-900', 'bg-emerald-600 text-white')
content = content.replace('bg-gold-500 text-slate-900', 'bg-[#E85D3E] text-white')

# 3. Accents (Gold -> Coral #E85D3E)
content = content.replace('text-gold-400', 'text-[#E85D3E]')
content = content.replace('bg-gold-500', 'bg-[#E85D3E]')
content = content.replace('from-gold-400 to-amber-600', 'from-[#E85D3E] to-[#C44A2D]')
content = content.replace('shadow-gold-500/20', 'shadow-[#E85D3E]/20')
content = content.replace('border-gold-500', 'border-[#E85D3E]')

# 4. Chat Bubbles
# User Bubble (currently bg-surface-800)
content = content.replace('bg-surface-800 text-slate-900 rounded-2xl p-5 shadow-sm border border-slate-200 font-medium', 'bg-[#F3F4F6] text-slate-800 rounded-2xl p-5 shadow-sm border border-slate-100 font-medium')
# Assistant Bubble background was transparent-ish/prose
content = content.replace('prose prose-invert', 'prose prose-slate')

# 5. UI Elements
content = content.replace('bg-emerald-500/10 text-emerald-400 border-emerald-500/30', 'bg-emerald-50 text-emerald-600 border-emerald-100')
content = content.replace('bg-surface-950/50', 'bg-slate-50')
content = content.replace('border-surface-600', 'border-slate-200')

# 6. Buttons
content = content.replace('bg-indigo-600', 'bg-[#E85D3E]') # Neutralize indigo if it's too much
content = content.replace('from-indigo-600 to-violet-600', 'from-[#E85D3E] to-[#C44A2D]')

# 7. Workspace IDE
content = content.replace('bg-surface-950', 'bg-slate-900') # KEEP IDE DARK? No, user said "dashboard professionnel"
# Actually, dashboards often have dark sidebars but white content.
# Let's make the IDE background a very clean light gray or white.
content = content.replace('bg-slate-900', 'bg-white') 

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
