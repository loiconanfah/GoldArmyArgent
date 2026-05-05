import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add ClockIcon to imports
content = content.replace('  MapPinIcon,', '  ClockIcon,\n  MapPinIcon,')

# 2. Add refs and function
insertion_point = "const isWorkspaceOpen = ref(false)"
new_state = """const showCvHistory = ref(false)
const isWorkspaceOpen = ref(false)"""

if insertion_point in content:
    content = content.replace(insertion_point, new_state)

# Add restore function before </script>
restore_func = """
const restoreCvFromHistory = (entry) => {
    cvText.value = entry.cv_text
    cvFilename.value = entry.name || t('agent_chat.cv_history.restored_cv') || 'CV Restauré'
    showCvHistory.value = false
    toastState.addToast(t('agent_chat.cv_history.restore_success') || 'CV restauré avec succès')
}
</script>"""
content = content.replace('</script>', restore_func)

# 3. Add UI to Context Panel (PDF Upload area)
# Locate the context panel (isUploading area)
panel_marker = '<div v-if="isUploading" class="mb-6 bg-white border border-slate-200 p-4 rounded-2xl shadow-sm relative z-10">'
history_button = """
            <div class="flex justify-between items-center mb-3">
                <h3 class="text-slate-900 font-bold text-sm tracking-wide flex items-center gap-2">
                    {{ t('agent_chat.cv_context') }}
                </h3>
                <div class="flex items-center gap-3">
                    <button 
                        v-if="currentUser?.cv_history?.length"
                        @click="showCvHistory = !showCvHistory" 
                        class="flex items-center gap-1.5 text-[#E85D3E] hover:text-[#C44A2D] text-[10px] font-black uppercase tracking-widest transition-colors"
                    >
                        <ClockIcon class="w-3 h-3" /> {{ t('agent_chat.view_history') }}
                    </button>
                    <button @click="isUploading = false" class="text-slate-500 hover:text-slate-900 text-[10px] font-black uppercase tracking-widest">{{ t('common.close') || 'Fermer' }}</button>
                </div>
            </div>

            <!-- CV HISTORY DROPDOWN -->
            <transition
                enter-active-class="transition duration-200 ease-out"
                enter-from-class="opacity-0 -translate-y-2"
                enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition duration-150 ease-in"
                leave-from-class="opacity-100 translate-y-0"
                leave-to-class="opacity-0 -translate-y-2"
            >
                <div v-if="showCvHistory && currentUser?.cv_history?.length" class="mb-4 bg-slate-50 border border-slate-200 rounded-xl overflow-hidden shadow-inner">
                    <div class="p-3 border-b border-slate-200 bg-white/50">
                        <p class="text-[9px] font-black text-slate-400 uppercase tracking-widest m-0">{{ t('agent_chat.cv_history.versions_desc') }}</p>
                    </div>
                    <div class="max-h-48 overflow-y-auto custom-scrollbar">
                        <button 
                            v-for="(entry, i) in currentUser.cv_history" 
                            :key="i"
                            @click="restoreCvFromHistory(entry)"
                            class="w-full text-left p-3 hover:bg-white flex items-center justify-between group transition-colors border-b border-slate-100 last:border-0"
                        >
                            <div class="flex items-center gap-3">
                                <div class="w-7 h-7 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-400 group-hover:text-[#E85D3E] transition-colors">
                                    <DocumentTextIcon class="w-4 h-4" />
                                </div>
                                <div>
                                    <p class="text-xs font-bold text-slate-700 m-0 group-hover:text-slate-900">{{ entry.name }}</p>
                                    <p class="text-[9px] text-slate-400 m-0">{{ i === 0 ? t('agent_chat.cv_history.current') : '' }}</p>
                                </div>
                            </div>
                            <div class="opacity-0 group-hover:opacity-100 transition-opacity">
                                <span class="text-[9px] font-black text-[#E85D3E] uppercase tracking-widest">{{ t('agent_chat.cv_history.restore') }}</span>
                            </div>
                        </button>
                    </div>
                </div>
            </transition>"""

# Replace the original header in the panel
original_header_pattern = r'<div class="flex justify-between items-center mb-3">.*?</div>'
match = re.search(original_header_pattern, content, re.DOTALL)
if match and panel_marker in content:
    # We want to replace only the header INSIDE the isUploading panel
    panel_start = content.find(panel_marker)
    header_in_panel = content.find('<div class="flex justify-between items-center mb-3">', panel_start)
    header_end = content.find('</div>', header_in_panel) + 6
    
    content = content[:header_in_panel] + history_button + content[header_end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
