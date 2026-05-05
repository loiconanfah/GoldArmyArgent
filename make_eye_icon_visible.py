import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update the Eye icon trigger to be visible by default
new_eye_ui = """<div @click="openPreview(msg.content)" class="absolute inset-0 flex items-center justify-center bg-slate-900/5 backdrop-blur-[1px] cursor-pointer hover:bg-slate-900/10 transition-all group/eye">
                           <div class="w-10 h-10 rounded-full bg-white/90 shadow-lg flex items-center justify-center border border-slate-200 group-hover/eye:scale-110 transition-transform">
                               <EyeIcon class="w-5 h-5 text-[#E85D3E]" />
                           </div>
                      </div>"""

# Find the old trigger
old_pattern = r'<div @click="openPreview\(msg\.content\)" class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900/10 backdrop-blur-\[2px\] cursor-pointer">\s*<EyeIcon class="w-8 h-8 text-white" />\s*</div>'
content = re.sub(old_pattern, new_eye_ui, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
