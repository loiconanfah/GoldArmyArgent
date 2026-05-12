import sys

with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '    <!-- ================================================================\n         NETWORK NINJA TAB — 3D Parallax & Hover Networking\n         ================================================================ -->'
end_marker = '    <!-- Loading Modal for Drafting -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('Markers not found')
    sys.exit(1)

new_template = """    <!-- ================================================================
         NETWORK NINJA TAB — 3D Globe Navigation
         ================================================================ -->
    <div v-else-if="activeTab === 'ninja'"
         class="relative w-full rounded-[2.5rem] bg-[#050505] overflow-hidden flex flex-col animate-fade-in shadow-2xl mt-8"
         style="height: 720px;">

        <!-- Header -->
        <div class="absolute top-5 left-6 z-10 flex items-center gap-3">
            <div class="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-md text-sm text-neutral-300 font-medium">
                <span class="text-[#E85D3E] font-black">🥷</span>
                <span class="text-white font-bold tracking-wide">Network Ninja</span>
            </div>
            <div v-if="ninjaTotalProfiles > 0" class="px-3 py-1.5 bg-[#E85D3E]/10 border border-[#E85D3E]/30 rounded-full flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-[#E85D3E] animate-pulse"></span>
                <span class="text-xs font-bold text-[#E85D3E]">{{ ninjaTotalProfiles }} décideur(s)</span>
            </div>
        </div>

        <!-- Relancer button -->
        <button @click="runNinja" :disabled="ninjaRunning"
            class="absolute top-5 right-6 z-10 px-4 py-2 bg-white/5 border border-white/10 hover:border-[#E85D3E]/60 text-white rounded-xl text-sm font-bold transition-all flex items-center gap-2 backdrop-blur-md">
            <svg v-if="ninjaRunning" class="w-4 h-4 animate-spin text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <svg v-else class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            {{ ninjaRunning ? 'Scan...' : 'Relancer' }}
        </button>

        <!-- Hint -->
        <div class="absolute bottom-5 left-1/2 -translate-x-1/2 z-10 text-neutral-600 text-xs flex items-center gap-2">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5"/></svg>
            Glisser pour faire tourner le globe — survoler un nœud pour voir le profil
        </div>

        <!-- Canvas Globe -->
        <canvas ref="ninjaCanvas"
            class="absolute inset-0 w-full h-full cursor-grab active:cursor-grabbing"
            @mousedown="globeMouseDown"
            @mousemove="globeMouseMove"
            @mouseup="globeMouseUp"
            @mouseleave="globeMouseLeave"
            @touchstart.prevent="globeTouchStart"
            @touchmove.prevent="globeTouchMove"
            @touchend="globeTouchEnd" />

        <!-- Hover Tooltip -->
        <Transition name="fade-scale">
            <div v-if="ninjaHoverNode"
                 @mouseleave="ninjaHoverNode = null"
                 class="fixed z-[200] w-72 bg-[#111]/95 border border-white/10 rounded-2xl shadow-2xl p-5 backdrop-blur-xl pointer-events-auto"
                 :style="{ left: ninjaTooltipX + 'px', top: ninjaTooltipY + 'px' }">
                <p class="text-[#E85D3E] text-[10px] font-black tracking-widest uppercase mb-1">{{ ninjaHoverNode.role }}</p>
                <h4 class="text-white text-base font-black mb-1">{{ ninjaHoverNode.name }}</h4>
                <p class="text-neutral-500 text-xs mb-4">{{ ninjaHoverNode.company_name }}</p>
                <p class="text-neutral-300 text-sm leading-relaxed mb-5 italic border-l-2 border-[#E85D3E] pl-3">
                    "{{ ninjaHoverNode.message }}"
                </p>
                <div class="space-y-1">
                    <a v-if="ninjaHoverNode.linkedin_url" :href="ninjaHoverNode.linkedin_url" target="_blank"
                       class="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors group">
                        <div class="flex items-center gap-3">
                            <svg class="w-4 h-4 text-[#0A66C2]" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                            <span class="text-sm text-neutral-300 group-hover:text-white">Voir le profil LinkedIn</span>
                        </div>
                        <svg class="w-4 h-4 text-neutral-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                    </a>
                    <button @click="copyNinjaMessage(ninjaHoverNode.message, ninjaHoverNode.key)"
                        class="w-full flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors group border border-transparent hover:border-[#E85D3E]/30">
                        <div class="flex items-center gap-3">
                            <svg class="w-4 h-4 text-neutral-500 group-hover:text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                            <span class="text-sm text-neutral-300 group-hover:text-white">Copier ({{ (ninjaHoverNode.message||'').length }} car.)</span>
                        </div>
                        <svg v-if="ninjaCopied[ninjaHoverNode.key]" class="w-4 h-4 text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                        <svg v-else class="w-4 h-4 text-neutral-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                    </button>
                </div>
            </div>
        </Transition>

        <!-- Empty state -->
        <div v-if="!ninjaLoading && !ninjaRunning && ninjaCompanies.length === 0"
             class="absolute inset-0 flex flex-col items-center justify-center text-center z-20">
            <div class="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-4">
                <svg class="w-8 h-8 text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            </div>
            <p class="text-white text-xl font-bold mb-2">Aucun réseau identifié</p>
            <p class="text-neutral-500 text-sm max-w-sm mb-6">Lancez le workflow Network Ninja depuis votre Dashboard pour démarrer la cartographie.</p>
            <button @click="runNinja" class="px-6 py-3 bg-[#E85D3E] hover:bg-[#D04A2C] text-white font-bold rounded-2xl transition-all shadow-lg shadow-[#E85D3E]/30">
                Lancer le scan maintenant
            </button>
        </div>

        <!-- Scanning state -->
        <div v-if="ninjaRunning" class="absolute inset-0 bg-[#050505]/95 z-50 flex flex-col items-center justify-center text-center">
            <div class="relative w-28 h-28 mb-8">
                <div class="absolute inset-0 border-4 border-[#E85D3E]/20 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-[#E85D3E] border-t-transparent rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center text-4xl">🥷</div>
            </div>
            <p class="text-[#E85D3E] text-xl font-black tracking-widest uppercase animate-pulse">Cartographie en cours</p>
            <p class="text-neutral-500 text-sm mt-3 max-w-sm">Analyse sectorielle et recherche des décideurs LinkedIn...</p>
        </div>
    </div>
\n"""

content = content[:start_idx] + new_template + content[end_idx:]

with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Globe template replaced.')
