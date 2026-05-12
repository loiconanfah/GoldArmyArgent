path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix incomplete IdentificationIcon
content = content.replace('< class="w-8 h-8 text-[#E85D3E]" />', '<IdentificationIcon class="w-8 h-8 text-[#E85D3E]" />')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
