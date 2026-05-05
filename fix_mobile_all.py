import re
import os

def fix_mentor():
    path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Mentor.vue'
    if not os.path.exists(path): return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Already fixed mostly, but let's ensure padding and header are perfect
    style_block = """
<style scoped>
.db-root {
  min-height: 100vh;
  background-color: #F9FAFB;
  padding: 16px;
}

@media (min-width: 768px) {
  .db-root {
    padding: 40px;
  }
}

.db-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .db-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 40px;
  }
}

.header-title-box h1 {
  font-size: 24px;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

@media (min-width: 768px) {
  .header-title-box h1 {
    font-size: 32px;
  }
}
</style>
"""
    # Replace existing style
    content = re.sub(r'<style scoped>.*</style>', style_block, content, flags=re.DOTALL)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_opportunities():
    path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Opportunities.vue'
    if not os.path.exists(path): return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update db-root and db-header for mobile
    content = content.replace('.db-root {', '.db-root {\n  padding: 16px !important;')
    content = content.replace('.db-header {', '.db-header {\n    flex-direction: column !important;')
    
    # Add responsive media queries at the end of style
    mq = """
@media (min-width: 768px) {
    .db-root { padding: 2rem !important; }
    .db-header { flex-direction: row !important; }
    .greeting-text { font-size: 2rem !important; }
}
@media (max-width: 767px) {
    .greeting-text { font-size: 1.25rem !important; }
    .header-date-box { width: 100%; justify-content: space-between; }
}
</style>
"""
    content = content.replace('</style>', mq)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_agentchat():
    path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'
    if not os.path.exists(path): return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Responsive Input Bar (Stack buttons on mobile)
    content = content.replace('flex flex-col sm:flex-row items-end sm:items-center gap-2', 'flex flex-col gap-2')
    
    # 2. Workspace Mobile Handling
    # Add a check for mobile in script
    if 'const isMobile = ref(false)' not in content:
        content = content.replace('const sessionId = ref(', 'const isMobile = ref(window.innerWidth < 768)\nconst sessionId = ref(')
        content = content.replace('onMounted(async () => {', 'onMounted(async () => {\n  window.addEventListener(\'resize\', () => isMobile.value = window.innerWidth < 768)')
        
    # Hide chat if workspace is open on mobile
    content = content.replace('v-show="!isWorkspaceFullScreen"', 'v-show="!isWorkspaceFullScreen && (!isWorkspaceOpen || !isMobile)"')
    
    # Ensure workspace takes full width on mobile
    content = content.replace('class="flex-1 h-full bg-white flex flex-col shadow-2xl animate-fade-in"', 'class="flex-1 h-full bg-white flex flex-col shadow-2xl animate-fade-in w-full"')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

fix_mentor()
fix_opportunities()
fix_agentchat()
print("done")
