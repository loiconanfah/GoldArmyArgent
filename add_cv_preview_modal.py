import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add state and computed
# We need to find the script section
script_marker = "const showCvHistory = ref(false)"
new_state = """const showCvHistory = ref(false)
const showPreviewModal = ref(false)
const previewData = ref(null)

const previewSrcdoc = computed(() => {
    if (!previewData.value || !selectedTheme.value) return ''
    const tpl = CV_THEMES.value.find(t => t.id === selectedTheme.value) || CV_THEMES.value[0]
    try {
        const data = typeof previewData.value === 'string' ? JSON.parse(previewData.value) : previewData.value
        return tpl.build(data, null)
    } catch (e) {
        return 'Error generating preview'
    }
})

const openPreview = (data) => {
    previewData.value = data
    showPreviewModal.value = true
}"""

if script_marker in content:
    content = content.replace(script_marker, new_state)

# 2. Update the Eye icon to trigger preview
eye_icon_trigger = """<div @click="openPreview(msg.content)" class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900/10 backdrop-blur-[2px] cursor-pointer">
                               <EyeIcon class="w-8 h-8 text-white" />
                           </div>"""

# Find the EyeIcon in the template selector area
eye_pattern = r'<div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900/10 backdrop-blur-\[2px\]">\s*<EyeIcon class="w-8 h-8 text-white" />\s*</div>'
content = re.sub(eye_pattern, eye_icon_trigger, content)

# 3. Add the Modal UI at the end of the template (before </template>)
preview_modal_ui = """
    <!-- MODAL: PREVIEW CV -->
    <transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
    >
        <div v-if="showPreviewModal" class="fixed inset-0 z-[110] flex items-center justify-center p-4 md:p-8 bg-slate-900/80 backdrop-blur-sm">
            <div class="bg-white w-full max-w-5xl h-full max-h-[90vh] rounded-[2.5rem] shadow-2xl flex flex-col overflow-hidden relative border border-white/20">
                <!-- Header -->
                <div class="px-8 py-4 bg-white border-b border-slate-100 flex items-center justify-between shrink-0">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-xl bg-[#E85D3E] flex items-center justify-center text-white shadow-lg shadow-[#E85D3E]/20">
                            <EyeIcon class="w-5 h-5" />
                        </div>
                        <div>
                            <h3 class="text-lg font-black text-slate-900 m-0">{{ t('agent_chat.preview.title') || 'Aperçu du CV' }}</h3>
                            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">{{ CV_THEMES.find(t => t.id === selectedTheme)?.name }} Template</p>
                        </div>
                    </div>
                    <button @click="showPreviewModal = false" class="p-2 hover:bg-slate-100 rounded-xl transition-colors">
                        <XMarkIcon class="w-6 h-6 text-slate-400" />
                    </button>
                </div>
                
                <!-- Content (Iframe) -->
                <div class="flex-1 bg-slate-50 p-4 md:p-8 overflow-hidden flex justify-center">
                    <div class="w-full max-w-[800px] h-full bg-white shadow-2xl rounded-sm overflow-hidden">
                        <iframe 
                            :srcdoc="previewSrcdoc" 
                            class="w-full h-full border-none"
                            sandbox="allow-scripts"
                        ></iframe>
                    </div>
                </div>
                
                <!-- Footer Actions -->
                <div class="px-8 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-center gap-4 shrink-0">
                    <button @click="showPreviewModal = false" class="px-6 py-2.5 bg-white border border-slate-200 text-slate-900 text-xs font-black rounded-xl hover:bg-slate-50 transition-colors uppercase tracking-widest">
                        {{ t('common.close') || 'Fermer' }}
                    </button>
                    <button @click="downloadCvDocx(previewData)" class="px-8 py-2.5 bg-[#E85D3E] text-white text-xs font-black rounded-xl shadow-lg shadow-[#E85D3E]/20 hover:bg-[#C44A2D] transition-all uppercase tracking-widest flex items-center gap-2">
                        <ArrowDownTrayIcon class="w-4 h-4" /> {{ t('agent_chat.audit.download_cv') }}
                    </button>
                </div>
            </div>
        </div>
    </transition>
"""

content = content.replace('  </div>\n</template>', preview_modal_ui + '  </div>\n</template>')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
