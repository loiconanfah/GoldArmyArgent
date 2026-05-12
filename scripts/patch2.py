import sys

with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '    <!-- ================================================================\n         NETWORK NINJA TAB — Dark Mindmap Design\n         ================================================================ -->'
end_marker = '    <!-- Loading Modal for Drafting -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('Markers not found')
    sys.exit(1)

new_block = """    <!-- ================================================================
         NETWORK NINJA TAB — Dark Mindmap Design
         ================================================================ -->
    <div v-else-if="activeTab === 'ninja'" class="relative w-full h-[700px] rounded-[2.5rem] bg-[#050505] overflow-hidden flex flex-col font-sans animate-fade-in shadow-xl mt-8">
        
        <!-- SVG Styles for Animation -->
        <svg width="0" height="0" class="hidden">
            <style>
                @keyframes dash {
                    to { stroke-dashoffset: -20; }
                }
                @keyframes pulse-glow {
                    0%, 100% { filter: drop-shadow(0 0 4px rgba(232, 93, 62, 0.4)); transform: scale(1); }
                    50% { filter: drop-shadow(0 0 10px rgba(232, 93, 62, 0.8)); transform: scale(1.1); }
                }
                @keyframes float-node {
                    0%, 100% { transform: translateY(0px); }
                    50% { transform: translateY(-3px); }
                }
                .ninja-anim-edge {
                    stroke-dasharray: 4,4;
                    animation: dash 2s linear infinite;
                }
                .ninja-anim-node {
                    transform-origin: center;
                    animation: pulse-glow 3s infinite ease-in-out;
                }
                .ninja-float {
                    animation: float-node 4s infinite ease-in-out;
                }
            </style>
        </svg>

        <!-- Background Grid / Stars -->
        <div class="absolute inset-0 ninja-dark-bg pointer-events-none opacity-40"></div>
        
        <!-- Header (Internal to canvas) -->
        <div class="absolute top-6 left-6 z-10 flex items-center gap-4">
            <div class="flex items-center gap-2 px-4 py-2 bg-neutral-900/80 border border-neutral-800 rounded-2xl backdrop-blur-md text-sm text-neutral-300 font-medium">
                <span class="text-[#E85D3E] font-black">🥷</span>
                <span class="text-white font-bold tracking-wide">Network Ninja</span>
                <span class="text-neutral-500 ml-2">Scanner Actif</span>
            </div>
            
            <div v-if="ninjaTotalProfiles > 0" class="px-3 py-1.5 bg-[#E85D3E]/10 border border-[#E85D3E]/30 rounded-full flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-[#E85D3E] animate-pulse"></span>
                <span class="text-xs font-bold text-[#E85D3E]">{{ ninjaTotalProfiles }} décideur(s) identifié(s)</span>
            </div>
        </div>

        <!-- Run button inside canvas (Optional, to reload) -->
        <button @click="runNinja" :disabled="ninjaRunning" class="absolute top-6 right-6 z-10 px-4 py-2 bg-neutral-900 border border-neutral-800 hover:border-[#E85D3E] text-white rounded-xl text-sm font-bold transition-all flex items-center gap-2 group shadow-lg">
            <svg v-if="ninjaRunning" class="w-4 h-4 animate-spin text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <svg v-else class="w-4 h-4 text-neutral-400 group-hover:text-[#E85D3E] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            Relancer
        </button>

        <!-- SVG Mindmap -->
        <div class="absolute inset-0 flex items-center justify-center overflow-visible">
            <svg class="w-full h-full overflow-visible" viewBox="-400 -300 800 600">
                <defs>
                    <filter id="glow-orange">
                        <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                        <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                    <filter id="glow-white">
                        <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
                        <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                </defs>

                <!-- Edges -->
                <g class="ninja-edges">
                    <template v-for="(company, ci) in ninjaCompanies" :key="'edge-c-'+ci">
                        <!-- Moi -> Company -->
                        <line x1="0" y1="0" 
                              :x2="getCompanyX(ci, ninjaCompanies.length)" 
                              :y2="getCompanyY(ci, ninjaCompanies.length)"
                              stroke="#E85D3E" stroke-width="1.5" opacity="0.4" class="ninja-anim-edge" />
                              
                        <!-- Company -> Profiles -->
                        <template v-for="(profile, pi) in company.profiles" :key="'edge-p-'+ci+'-'+pi">
                            <line :x1="getCompanyX(ci, ninjaCompanies.length)" 
                                  :y1="getCompanyY(ci, ninjaCompanies.length)"
                                  :x2="getProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)" 
                                  :y2="getProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                  stroke="#a3a3a3" stroke-width="0.5" opacity="0.3" class="ninja-anim-edge" />
                        </template>
                    </template>
                </g>

                <!-- Nodes -->
                <g class="ninja-nodes">
                    <!-- Central Node (Moi) -->
                    <circle cx="0" cy="0" r="10" fill="#ffffff" filter="url(#glow-white)" />
                    <circle cx="0" cy="0" r="4" fill="#ffffff" />
                    
                    <!-- Companies & Profiles -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'node-c-'+ci">
                        <!-- Company Group (Floating) -->
                        <g class="ninja-float" :style="{ animationDelay: ci * 0.2 + 's' }">
                            <!-- Company Node -->
                            <circle :cx="getCompanyX(ci, ninjaCompanies.length)" 
                                    :cy="getCompanyY(ci, ninjaCompanies.length)" 
                                    r="8" fill="#E85D3E" class="cursor-pointer transition-transform hover:scale-150 ninja-anim-node" />
                            <!-- Company Label -->
                            <g :transform="`translate(${getCompanyX(ci, ninjaCompanies.length) + 14}, ${getCompanyY(ci, ninjaCompanies.length) - 10})`">
                                <rect width="130" height="24" rx="12" fill="#171717" stroke="#333333" stroke-width="1" />
                                <text x="12" y="16" fill="#f5f5f5" font-size="10" font-family="sans-serif" font-weight="600">{{ company.company_name.substring(0,18) }}</text>
                            </g>

                            <!-- Profile Nodes -->
                            <template v-for="(profile, pi) in company.profiles" :key="'node-p-'+ci+'-'+pi">
                                <circle :cx="getProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)" 
                                        :cy="getProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)" 
                                        r="5" fill="#a3a3a3" 
                                        class="cursor-pointer transition-all hover:fill-white hover:r-[7px]"
                                        @click.stop="ninjaSelectedNode = { ...profile, company_name: company.company_name, x: getProfileX(ci, pi, ninjaCompanies.length, company.profiles.length), y: getProfileY(ci, pi, ninjaCompanies.length, company.profiles.length), key: company.company_name + '_' + pi }" />
                                <!-- Profile Label -->
                                <g :transform="`translate(${getProfileX(ci, pi, ninjaCompanies.length, company.profiles.length) + 8}, ${getProfileY(ci, pi, ninjaCompanies.length, company.profiles.length) - 10})`">
                                    <rect width="100" height="20" rx="10" fill="#171717" stroke="#262626" stroke-width="1" />
                                    <text x="10" y="14" fill="#a3a3a3" font-size="9" font-family="sans-serif">{{ (profile.name || 'Profil').split(' ')[0] }}</text>
                                </g>
                            </template>
                        </g>
                    </template>
                </g>
            </svg>
        </div>

        <!-- Popover (Connected Topics style) -->
        <Transition name="fade">
            <div v-if="ninjaSelectedNode" 
                 class="absolute z-20 w-80 bg-[#121212] border border-[#262626] rounded-2xl shadow-2xl p-5 backdrop-blur-xl"
                 :style="{ left: `calc(50% + ${ninjaSelectedNode.x}px + 20px)`, top: `calc(50% + ${ninjaSelectedNode.y}px - 20px)` }">
                 
                 <!-- Close button -->
                 <button @click="ninjaSelectedNode = null" class="absolute top-4 right-4 text-neutral-500 hover:text-white">
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                 </button>

                 <!-- Date / Role -->
                 <p class="text-[#E85D3E] text-xs font-bold mb-3 tracking-wide uppercase">{{ ninjaSelectedNode.role }} @ {{ ninjaSelectedNode.company_name }}</p>
                 
                 <!-- Message Quote -->
                 <p class="text-neutral-200 text-sm leading-relaxed mb-6 font-serif italic border-l-2 border-[#E85D3E] pl-3">
                     "{{ ninjaSelectedNode.message }}"
                 </p>
                 
                 <p class="text-neutral-500 text-xs mb-2 uppercase tracking-widest font-bold">Actions</p>
                 
                 <!-- Action Links -->
                 <div class="space-y-1">
                     <a v-if="ninjaSelectedNode.linkedin_url" :href="ninjaSelectedNode.linkedin_url" target="_blank"
                        class="flex items-center justify-between p-3 rounded-xl hover:bg-[#1a1a1a] transition-colors group">
                         <div class="flex items-center gap-3">
                             <svg class="w-4 h-4 text-[#0A66C2]" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                             <span class="text-sm font-medium text-neutral-300 group-hover:text-white">Ouvrir le profil</span>
                         </div>
                         <svg class="w-4 h-4 text-neutral-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                     </a>
                     
                     <button @click="copyNinjaMessage(ninjaSelectedNode.message, ninjaSelectedNode.key)"
                        class="w-full flex items-center justify-between p-3 rounded-xl hover:bg-[#1a1a1a] transition-colors group border border-transparent hover:border-[#E85D3E]/30">
                         <div class="flex items-center gap-3">
                             <svg class="w-4 h-4 text-neutral-400 group-hover:text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                             <span class="text-sm font-medium text-neutral-300 group-hover:text-white">Copier ({{ (ninjaSelectedNode.message || '').length }} car.)</span>
                         </div>
                         <svg v-if="ninjaCopied[ninjaSelectedNode.key]" class="w-4 h-4 text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                         <svg v-else class="w-4 h-4 text-neutral-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                     </button>
                 </div>
            </div>
        </Transition>

        <!-- Bottom Toolbar -->
        <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-2 p-2 bg-neutral-900/80 border border-neutral-800 rounded-full backdrop-blur-xl shadow-2xl">
            <button class="w-10 h-10 rounded-full flex items-center justify-center text-[#E85D3E] bg-[#E85D3E]/10 border border-[#E85D3E]/30 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>
            </button>
            <div class="w-px h-6 bg-neutral-800"></div>
            <button class="w-10 h-10 rounded-full flex items-center justify-center text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/></svg>
            </button>
            <button class="w-10 h-10 rounded-full flex items-center justify-center text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"/></svg>
            </button>
            <div class="w-px h-6 bg-neutral-800"></div>
            <button class="w-10 h-10 rounded-full flex items-center justify-center text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            </button>
        </div>
        
        <!-- Empty State Overlay -->
        <div v-if="!ninjaLoading && ninjaCompanies.length === 0 && !ninjaRunning" class="absolute inset-0 bg-[#050505]/90 backdrop-blur-sm z-40 flex flex-col items-center justify-center text-center">
            <div class="w-16 h-16 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center mb-4">
                <svg class="w-8 h-8 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            </div>
            <p class="text-neutral-300 text-lg font-medium mb-2">Aucun réseau identifié</p>
            <p class="text-neutral-500 text-sm max-w-sm">Lancez le workflow Network Ninja depuis votre Dashboard pour commencer l'extraction.</p>
        </div>

        <!-- Loading / Scanning State Overlay -->
        <div v-if="ninjaRunning" class="absolute inset-0 bg-[#050505]/90 backdrop-blur-sm z-50 flex flex-col items-center justify-center text-center">
            <div class="relative w-24 h-24 mb-6">
                <div class="absolute inset-0 border-4 border-[#E85D3E]/20 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-[#E85D3E] border-t-transparent rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center text-3xl">🥷</div>
            </div>
            <p class="text-[#E85D3E] text-lg font-black tracking-widest uppercase animate-pulse">Extraction en cours</p>
            <p class="text-neutral-400 text-sm mt-2 max-w-xs">Analyse des candidatures et ciblage des décideurs LinkedIn...</p>
        </div>
    </div>
\n"""

content = content[:start_idx] + new_block + content[end_idx:]

with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Success')
