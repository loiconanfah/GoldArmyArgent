import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Restore v-show
content = content.replace('v-show="!isWorkspaceFullScreen && (!isWorkspaceOpen || !isMobile)"', 'v-show="!isWorkspaceFullScreen"')

# 2. Restore Input Bar
content = content.replace('flex flex-col gap-2', 'flex flex-col sm:flex-row items-end sm:items-center gap-2')

# 3. Restore Workspace width
content = content.replace('class="flex-1 h-full bg-white flex flex-col shadow-2xl animate-fade-in w-full"', 'class="flex-1 h-full bg-white flex flex-col shadow-2xl animate-fade-in"')

# 4. Remove isMobile logic
content = content.replace('const isMobile = ref(window.innerWidth < 768)\n', '')
content = content.replace("window.addEventListener('resize', () => isMobile.value = window.innerWidth < 768)\n", "")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
