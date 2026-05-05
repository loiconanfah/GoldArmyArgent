path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix incomplete CpuChipIcon
content = content.replace('< class="w-5 h-5 text-[#E85D3E]" />', '<CpuChipIcon class="w-5 h-5 text-[#E85D3E]" />')
# Fix incomplete MapPinIcon
content = content.replace('< class="w-4 h-4 text-slate-400" />', '<MapPinIcon class="w-4 h-4 text-slate-400" />')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
