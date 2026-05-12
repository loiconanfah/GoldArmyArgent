import re
import os

def fix_mentor():
    path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Mentor.vue'
    if not os.path.exists(path): return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace 🎓 with AcademicCapIcon
    # Need to make sure AcademicCapIcon is imported
    if 'AcademicCapIcon' not in content:
        content = content.replace('import {', 'import { AcademicCapIcon,')
    
    content = content.replace('<div class="date-num">🎓</div>', '<div class="date-num"><AcademicCapIcon class="w-6 h-6 text-[#E85D3E]" /></div>')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_agentchat():
    path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'
    if not os.path.exists(path): return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Imports
    needed = ['AcademicCapIcon', 'IdentificationIcon', 'CpuChipIcon', 'MapPinIcon']
    for icon in needed:
        if icon not in content:
            content = content.replace('import {', f'import {{ {icon},')

    # 2. Assistant Avatar
    content = content.replace('🪖', '<SparklesIcon class="w-4 h-4 text-white" />')
    
    # 3. Typing Indicator
    content = content.replace('🤖', '<CpuChipIcon class="w-5 h-5 text-[#E85D3E]" />')
    
    # 4. Audit Header
    content = content.replace('🎯', '<IdentificationIcon class="w-8 h-8 text-[#E85D3E]" />')
    
    # 5. Input Bar Location
    content = content.replace('<span class="text-slate-400">📍</span>', '<MapPinIcon class="w-4 h-4 text-slate-400" />')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

fix_mentor()
fix_agentchat()
print("done")
