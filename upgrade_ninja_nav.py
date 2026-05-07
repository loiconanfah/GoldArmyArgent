import re

with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# ─── 1. REPLACE SVG NETWORK SECTION ───
start_marker = '    <!-- ================================================================\n         NETWORK NINJA TAB — Neural Network SVG Mindmap\n         ================================================================ -->'
end_marker = '    <!-- Loading Modal for Drafting -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: markers not found")
    import sys; sys.exit(1)

new_template = r"""    <!-- ================================================================
         NETWORK NINJA TAB — Neural Network SVG Mindmap
         ================================================================ -->
    <div v-else-if="activeTab === 'ninja'"
         class="relative w-full rounded-[2.5rem] overflow-hidden flex flex-col mt-8 shadow-2xl"
         style="height: 720px; background: #080a0c; border: 1px solid rgba(255,255,255,0.06);">

        <!-- Ambient glow -->
        <div class="absolute inset-0 pointer-events-none" style="background: radial-gradient(ellipse 60% 50% at 50% 50%, rgba(232,93,62,0.04) 0%, transparent 70%);"></div>

        <!-- Header -->
        <div class="absolute top-5 left-6 z-20 flex items-center gap-3">
            <div class="flex items-center gap-2 px-4 py-2 rounded-2xl text-sm font-medium" style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);">
                <span style="color:#E85D3E;" class="font-black">🥷</span>
                <span class="text-white font-bold tracking-wide">Network Ninja</span>
            </div>
            <div v-if="ninjaTotalProfiles > 0" class="px-3 py-1.5 rounded-full flex items-center gap-2" style="background:rgba(232,93,62,0.1); border:1px solid rgba(232,93,62,0.3);">
                <span class="w-2 h-2 rounded-full animate-pulse" style="background:#E85D3E;"></span>
                <span class="text-xs font-bold" style="color:#E85D3E;">{{ ninjaTotalProfiles }} décideur(s)</span>
            </div>
        </div>

        <!-- Relancer + Recenter -->
        <div class="absolute top-5 right-6 z-20 flex items-center gap-2">
            <button @click="ninjaResetView()"
                title="Recentrer"
                class="w-9 h-9 rounded-xl flex items-center justify-center transition-all"
                style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); color:#888;">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>
            </button>
            <button @click="runNinja" :disabled="ninjaRunning"
                class="px-4 py-2 text-white rounded-xl text-sm font-bold transition-all flex items-center gap-2"
                style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);">
                <svg v-if="ninjaRunning" class="w-4 h-4 animate-spin" style="color:#E85D3E;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                <svg v-else class="w-4 h-4" style="color:#888;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                {{ ninjaRunning ? 'Scan...' : 'Relancer' }}
            </button>
        </div>

        <!-- Pan/Zoom hint -->
        <div class="absolute bottom-5 left-6 z-20 flex items-center gap-2" style="color:#333; font-size:11px;">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5"/></svg>
            Glisser pour naviguer · Scroll pour zoomer
        </div>

        <!-- Zoom controls -->
        <div class="absolute bottom-4 right-6 z-20 flex flex-col gap-1.5">
            <button @click="ninjaZoom(0.15)" class="w-8 h-8 rounded-xl flex items-center justify-center text-white transition-all" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08);">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            </button>
            <button @click="ninjaZoom(-0.15)" class="w-8 h-8 rounded-xl flex items-center justify-center text-white transition-all" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08);">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>
            </button>
        </div>

        <!-- Pan/Zoom SVG -->
        <svg class="absolute inset-0 w-full h-full select-none"
             :class="ninjaDragging ? 'cursor-grabbing' : 'cursor-grab'"
             @mousedown.prevent="ninjaPanStart"
             @mousemove.prevent="ninjaPanMove"
             @mouseup="ninjaPanEnd"
             @mouseleave="ninjaPanEnd"
             @wheel.prevent="ninjaWheel"
             ref="ninjaSvgEl">

            <!-- Transformed group (pan + zoom) -->
            <g :transform="`translate(${ninjaPanX}, ${ninjaPanY}) scale(${ninjaScale})`">

                <!-- Background particle dots -->
                <circle v-for="i in 50" :key="'bg-'+i"
                    :cx="((i * 139.5) % 960) - 80"
                    :cy="((i * 89.1) % 660) - 30"
                    :r="i % 4 === 0 ? 1.8 : 0.9"
                    fill="white"
                    :opacity="0.02 + (i%4)*0.015" />

                <template v-if="ninjaCompanies.length > 0">

                    <!-- Center → Company edges -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'ec-'+ci">
                        <line x1="500" y1="340"
                            :x2="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                            :y2="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                            stroke="#E85D3E" stroke-width="1" opacity="0.45"
                            stroke-dasharray="6,5" class="ninja-edge-anim" />
                    </template>

                    <!-- Company → Profile edges -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'ep-'+ci">
                        <template v-for="(prof, pi) in company.profiles" :key="'ep-'+ci+'-'+pi">
                            <line
                                :x1="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                                :y1="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                                :x2="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :y2="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                stroke="rgba(255,255,255,0.12)" stroke-width="0.7"
                                stroke-dasharray="3,4" class="ninja-edge-anim-slow" />
                        </template>
                    </template>

                    <!-- Company nodes -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'nc-'+ci">
                        <!-- Pulse ring -->
                        <circle :cx="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                                :cy="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                                r="20" fill="none"
                                stroke="#E85D3E" stroke-width="1" opacity="0.25"
                                class="ninja-pulse-ring"
                                :style="{ animationDelay: ci * 0.4 + 's' }" />
                        <!-- Dot -->
                        <circle :cx="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                                :cy="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                                r="9" fill="#E85D3E">
                            <animate attributeName="r" values="8;10;8" dur="3s" repeatCount="indefinite"
                                :begin="ci * 0.4 + 's'" />
                        </circle>
                        <!-- Glow -->
                        <circle :cx="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                                :cy="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                                r="5" fill="rgba(255,255,255,0.6)" class="pointer-events-none" />

                        <!-- Company label pill (foreignObject) -->
                        <foreignObject
                            :x="ninjaLabelX(ci, ninjaCompanies.length, 210)"
                            :y="ninjaNodeY(ci, ninjaCompanies.length, 210) - 14"
                            width="148" height="28" class="pointer-events-none">
                            <div xmlns="http://www.w3.org/1999/xhtml"
                                 style="background:rgba(12,14,16,0.9); border:1px solid rgba(232,93,62,0.3); border-radius:14px; padding:4px 11px; font-size:11px; font-weight:700; color:#f0f0f0; font-family:sans-serif; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:140px; letter-spacing:0.01em;">
                                {{ company.company_name }}
                            </div>
                        </foreignObject>

                        <!-- Profile nodes -->
                        <template v-for="(prof, pi) in company.profiles" :key="'np-'+ci+'-'+pi">
                            <!-- Large hover target -->
                            <circle
                                :cx="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :cy="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                r="18" fill="transparent" class="cursor-pointer"
                                @mouseenter.stop="showNinjaTooltip($event, { ...prof, company_name: company.company_name, key: company.company_name+'_'+pi })"
                                @mouseleave.stop="scheduleHideTooltip()" />
                            <!-- Visible dot -->
                            <circle
                                :cx="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :cy="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :r="ninjaHoverNode && ninjaHoverNode.key === company.company_name+'_'+pi ? 7 : 5"
                                :fill="ninjaHoverNode && ninjaHoverNode.key === company.company_name+'_'+pi ? '#ffffff' : 'rgba(255,255,255,0.45)'"
                                class="pointer-events-none transition-all" />
                            <!-- Profile name -->
                            <text
                                :x="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length) + 9"
                                :y="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length) + 4"
                                font-size="9" fill="rgba(255,255,255,0.4)"
                                font-family="sans-serif" class="pointer-events-none">
                                {{ (prof.name || '').split(' ')[0] }}
                            </text>
                        </template>
                    </template>

                    <!-- Central node (always rendered on top) -->
                    <circle cx="500" cy="340" r="30" fill="rgba(255,255,255,0.04)" />
                    <circle cx="500" cy="340" r="20" fill="rgba(255,255,255,0.07)">
                        <animate attributeName="r" values="18;22;18" dur="4s" repeatCount="indefinite" />
                    </circle>
                    <circle cx="500" cy="340" r="10" fill="white" opacity="0.95">
                        <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite" />
                    </circle>
                    <circle cx="500" cy="340" r="4" fill="white" />

                </template>
            </g>
        </svg>

        <!-- Hover Tooltip Card -->
        <Transition name="fade-scale">
            <div v-if="ninjaHoverNode"
                 @mouseenter="cancelHideTooltip()"
                 @mouseleave="scheduleHideTooltip()"
                 class="fixed z-[200] w-72 rounded-2xl shadow-2xl p-5"
                 style="background:#0e1012; border:1px solid rgba(255,255,255,0.1); backdrop-filter:blur(20px);"
                 :style="{ left: ninjaTooltipX + 'px', top: ninjaTooltipY + 'px' }">

                <p class="text-xs font-black tracking-widest uppercase mb-1" style="color:#E85D3E;">{{ ninjaHoverNode.role }}</p>
                <h4 class="text-white text-base font-black mb-0.5">{{ ninjaHoverNode.name }}</h4>
                <p class="text-xs mb-4" style="color:#444;">@ {{ ninjaHoverNode.company_name }}</p>

                <p class="text-sm leading-relaxed mb-5 italic pl-3" style="color:#bbb; border-left:2px solid #E85D3E;">
                    "{{ ninjaHoverNode.message }}"
                </p>

                <p class="text-xs uppercase tracking-widest font-black mb-2" style="color:#333;">Connected actions</p>

                <a v-if="ninjaHoverNode.linkedin_url" :href="ninjaHoverNode.linkedin_url" target="_blank"
                   class="flex items-center justify-between p-3 rounded-xl mb-1 transition-all"
                   style="border:1px solid transparent;"
                   onmouseover="this.style.background='rgba(255,255,255,0.04)'; this.style.borderColor='rgba(255,255,255,0.06)'"
                   onmouseout="this.style.background='transparent'; this.style.borderColor='transparent'">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4" fill="#0A66C2" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                        <span class="text-sm font-medium" style="color:#ccc;">Voir le profil</span>
                    </div>
                    <svg class="w-4 h-4" style="color:#444;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </a>

                <button @click="copyNinjaMessage(ninjaHoverNode.message, ninjaHoverNode.key)"
                    class="w-full flex items-center justify-between p-3 rounded-xl transition-all"
                    style="border:1px solid transparent;"
                    onmouseover="this.style.background='rgba(232,93,62,0.06)'; this.style.borderColor='rgba(232,93,62,0.25)'"
                    onmouseout="this.style.background='transparent'; this.style.borderColor='transparent'">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4" style="color:#888;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                        <span class="text-sm font-medium" style="color:#ccc;">Copier ({{ (ninjaHoverNode.message||'').length }} car.)</span>
                    </div>
                    <svg v-if="ninjaCopied[ninjaHoverNode.key]" class="w-4 h-4" style="color:#E85D3E;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    <svg v-else class="w-4 h-4" style="color:#333;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </button>
            </div>
        </Transition>

        <!-- Empty state -->
        <div v-if="!ninjaLoading && !ninjaRunning && ninjaCompanies.length === 0"
             class="absolute inset-0 flex flex-col items-center justify-center text-center z-20">
            <div class="w-16 h-16 rounded-full flex items-center justify-center mb-4"
                 style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08);">
                <svg class="w-8 h-8" style="color:#E85D3E;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            </div>
            <p class="text-white text-xl font-bold mb-2">Aucun réseau identifié</p>
            <p class="text-sm max-w-sm mb-6" style="color:#444;">Lancez le workflow depuis votre Dashboard pour cartographier vos contacts.</p>
            <button @click="runNinja" class="px-6 py-3 text-white font-bold rounded-2xl" style="background:#E85D3E;">Lancer le scan</button>
        </div>

        <!-- Scanning overlay -->
        <div v-if="ninjaRunning" class="absolute inset-0 flex flex-col items-center justify-center text-center z-50"
             style="background:rgba(8,10,12,0.94); backdrop-filter:blur(8px);">
            <div class="relative w-28 h-28 mb-8">
                <div class="absolute inset-0 rounded-full" style="border:4px solid rgba(232,93,62,0.15);"></div>
                <div class="absolute inset-0 rounded-full animate-spin" style="border:4px solid #E85D3E; border-top-color:transparent;"></div>
                <div class="absolute inset-0 flex items-center justify-center text-4xl">🥷</div>
            </div>
            <p class="text-xl font-black tracking-widest uppercase animate-pulse" style="color:#E85D3E;">Scan en cours</p>
            <p class="text-sm mt-3 max-w-sm" style="color:#444;">Identification des décideurs LinkedIn...</p>
        </div>
    </div>
\n"""

content = content[:start_idx] + new_template + content[end_idx:]

with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
    f.write(content)
print("Template replaced.")

# ─── 2. INJECT PAN/ZOOM SCRIPT LOGIC ───
with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Add pan/zoom refs and handlers after the ninjaHoverNode section
pan_zoom_code = """
// ── Ninja Pan/Zoom Navigation ──
const ninjaSvgEl = ref(null)
const ninjaPanX = ref(0)
const ninjaPanY = ref(0)
const ninjaScale = ref(1)
const ninjaDragging = ref(false)
let ninjaDragStart = { x: 0, y: 0, panX: 0, panY: 0 }

const ninjaResetView = () => {
    ninjaPanX.value = 0
    ninjaPanY.value = 0
    ninjaScale.value = 1
}

const ninjaZoom = (delta) => {
    ninjaScale.value = Math.min(3, Math.max(0.3, ninjaScale.value + delta))
}

const ninjaPanStart = (e) => {
    ninjaDragging.value = true
    ninjaDragStart = { x: e.clientX, y: e.clientY, panX: ninjaPanX.value, panY: ninjaPanY.value }
}

const ninjaPanMove = (e) => {
    if (!ninjaDragging.value) return
    ninjaPanX.value = ninjaDragStart.panX + (e.clientX - ninjaDragStart.x)
    ninjaPanY.value = ninjaDragStart.panY + (e.clientY - ninjaDragStart.y)
}

const ninjaPanEnd = () => { ninjaDragging.value = false }

const ninjaWheel = (e) => {
    const delta = e.deltaY > 0 ? -0.1 : 0.1
    ninjaScale.value = Math.min(3, Math.max(0.3, ninjaScale.value + delta))
}
// ── End Pan/Zoom ──
"""

# Also fix ninjaLabelX (position labels based on which side of center)
label_x_code = """
const ninjaLabelX = (i, total, radius) => {
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    const cx = 500 + Math.cos(angle) * radius
    // If node is on the right half, put label to the right; else to the left (with offset)
    return Math.cos(angle) >= 0 ? cx + 14 : cx - 162
}
"""

if 'ninjaDragging' not in content:
    idx = content.find('const showNinjaTooltip')
    content = content[:idx] + pan_zoom_code + '\n' + content[idx:]
    print("Pan/zoom injected.")
else:
    print("Pan/zoom already present.")

if 'ninjaLabelX' not in content:
    idx = content.find('const ninjaNodeX')
    content = content[:idx] + label_x_code + '\n' + content[idx:]
    print("ninjaLabelX injected.")
else:
    print("ninjaLabelX already present.")

# Fix CSS
new_css = """
/* ── Ninja SVG Animations ── */
@keyframes ninja-edge-flow {
  from { stroke-dashoffset: 0; }
  to   { stroke-dashoffset: -22; }
}
.ninja-edge-anim {
  animation: ninja-edge-flow 2s linear infinite;
}
.ninja-edge-anim-slow {
  stroke-dasharray: 3,5;
  animation: ninja-edge-flow 4s linear infinite;
}
.ninja-pulse-ring {
  animation: ninja-ring-pulse 3s ease-in-out infinite;
  transform-box: fill-box;
  transform-origin: center;
}
@keyframes ninja-ring-pulse {
  0%   { opacity: 0.3; transform: scale(0.9); }
  50%  { opacity: 0.08; transform: scale(1.4); }
  100% { opacity: 0.3; transform: scale(0.9); }
}
.fade-scale-enter-active, .fade-scale-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.fade-scale-enter-from, .fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
"""

# Replace old ninja css block
content = re.sub(r'/\* ── Ninja SVG Animations ── \*/.*?\.fade-scale-leave-to \{.*?\}\n', '', content, flags=re.DOTALL)
content = content.replace('</style>', new_css + '\n</style>')

with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("All done.")
