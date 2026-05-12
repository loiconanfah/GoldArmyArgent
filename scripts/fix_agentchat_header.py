import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Header with Logo
content = content.replace('font-black text-slate-900 tracking-tight', 'font-black text-slate-900 tracking-tight flex items-center gap-3')
content = content.replace('{{ t(\'agent_chat.title\') }}', '<div class="w-10 h-10 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center justify-center overflow-hidden shrink-0"><img src="/logo_ga.png" class="w-6 h-6 object-contain" /></div> {{ t(\'agent_chat.title\') }}')

# Fix Audit Modal (often uses dark classes too)
content = content.replace('bg-surface-800/60', 'bg-slate-50')
content = content.replace('bg-surface-800', 'bg-white')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
