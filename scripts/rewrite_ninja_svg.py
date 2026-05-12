import re

with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# ─── 1. REPLACE THE ENTIRE NINJA TAB TEMPLATE ───
start_marker = '    <!-- ================================================================\n         NETWORK NINJA TAB — 3D Globe Navigation\n         ================================================================ -->'
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
         style="height: 720px; background: #07080a;">

        <!-- Starfield background dots -->
        <svg class="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="xMidYMid slice">
            <circle v-for="i in 60" :key="'star-'+i"
                :cx="((i * 137.508) % 100) + '%'"
                :cy="((i * 97.3) % 100) + '%'"
                :r="(i % 3 === 0) ? 1.5 : 0.8"
                fill="white"
                :opacity="0.05 + (i % 5) * 0.03" />
        </svg>

        <!-- Header -->
        <div class="absolute top-5 left-6 z-20 flex items-center gap-3 pointer-events-none">
            <div class="flex items-center gap-2 px-4 py-2 rounded-2xl text-sm font-medium" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08);">
                <span style="color:#E85D3E;" class="font-black">🥷</span>
                <span class="text-white font-bold tracking-wide">Network Ninja</span>
            </div>
            <div v-if="ninjaTotalProfiles > 0" class="px-3 py-1.5 rounded-full flex items-center gap-2 pointer-events-auto"
                 style="background:rgba(232,93,62,0.12); border:1px solid rgba(232,93,62,0.35);">
                <span class="w-2 h-2 rounded-full animate-pulse" style="background:#E85D3E;"></span>
                <span class="text-xs font-bold" style="color:#E85D3E;">{{ ninjaTotalProfiles }} décideur(s)</span>
            </div>
        </div>

        <!-- Relancer -->
        <button @click="runNinja" :disabled="ninjaRunning"
            class="absolute top-5 right-6 z-20 px-4 py-2 text-white rounded-xl text-sm font-bold transition-all flex items-center gap-2"
            style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08);">
            <svg v-if="ninjaRunning" class="w-4 h-4 animate-spin" style="color:#E85D3E;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <svg v-else class="w-4 h-4" style="color:#888;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            {{ ninjaRunning ? 'Scan...' : 'Relancer' }}
        </button>

        <!-- SVG Network -->
        <svg class="absolute inset-0 w-full h-full" viewBox="0 0 1000 680" preserveAspectRatio="xMidYMid meet">
            <defs>
                <filter id="glow-center">
                    <feGaussianBlur stdDeviation="8" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
                <filter id="glow-company">
                    <feGaussianBlur stdDeviation="5" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
                <filter id="glow-profile">
                    <feGaussianBlur stdDeviation="3" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
            </defs>

            <!-- Background faint web -->
            <template v-if="ninjaCompanies.length > 0">
                <!-- Center → Company edges -->
                <template v-for="(company, ci) in ninjaCompanies" :key="'e-c-'+ci">
                    <line
                        x1="500" y1="340"
                        :x2="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                        :y2="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                        stroke="#E85D3E"
                        stroke-width="1.2"
                        opacity="0.5"
                        stroke-dasharray="5,4"
                        class="ninja-edge-anim" />

                    <!-- Company → Profile edges -->
                    <template v-for="(prof, pi) in company.profiles" :key="'e-p-'+ci+'-'+pi">
                        <line
                            :x1="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                            :y1="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                            :x2="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                            :y2="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                            stroke="#555"
                            stroke-width="0.7"
                            opacity="0.4"
                            class="ninja-edge-anim" />
                    </template>
                </template>

                <!-- Company nodes -->
                <template v-for="(company, ci) in ninjaCompanies" :key="'n-c-'+ci">
                    <!-- Outer glow ring -->
                    <circle
                        :cx="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                        :cy="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                        r="18" fill="none"
                        stroke="#E85D3E" stroke-width="0.8" opacity="0.3"
                        class="ninja-pulse-ring" />

                    <!-- Company dot -->
                    <circle
                        :cx="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                        :cy="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                        r="8" fill="#E85D3E"
                        filter="url(#glow-company)"
                        class="ninja-company-node" />

                    <!-- Company label pill -->
                    <foreignObject
                        :x="ninjaNodeX(ci, ninjaCompanies.length, 210) + 14"
                        :y="ninjaNodeY(ci, ninjaCompanies.length, 210) - 13"
                        width="140" height="26">
                        <div xmlns="http://www.w3.org/1999/xhtml"
                             style="background:rgba(20,20,22,0.85); border:1px solid rgba(255,255,255,0.12); border-radius:13px; padding:3px 10px; font-size:11px; font-weight:700; color:#e5e5e5; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:130px;">
                            {{ company.company_name }}
                        </div>
                    </foreignObject>

                    <!-- Profile nodes -->
                    <template v-for="(prof, pi) in company.profiles" :key="'n-p-'+ci+'-'+pi">
                        <!-- Hover target (larger invisible circle) -->
                        <circle
                            :cx="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                            :cy="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                            r="16" fill="transparent"
                            class="cursor-pointer"
                            @mouseenter="showNinjaTooltip($event, { ...prof, company_name: company.company_name, key: company.company_name+'_'+pi })"
                            @mouseleave="scheduleHideTooltip()" />

                        <!-- Profile dot (visible) -->
                        <circle
                            :cx="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                            :cy="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                            r="5"
                            :fill="ninjaHoverNode && ninjaHoverNode.key === company.company_name+'_'+pi ? '#ffffff' : '#888'"
                            filter="url(#glow-profile)"
                            class="pointer-events-none transition-all" />

                        <!-- Profile name label -->
                        <text
                            :x="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length) + 9"
                            :y="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length) + 4"
                            font-size="9.5" fill="#777"
                            font-family="sans-serif"
                            class="pointer-events-none">
                            {{ (prof.name || 'Profil').split(' ')[0] }}
                        </text>
                    </template>
                </template>

                <!-- Central node (Me) - always on top -->
                <circle cx="500" cy="340" r="22" fill="white" opacity="0.08" />
                <circle cx="500" cy="340" r="14" fill="white" opacity="0.15" filter="url(#glow-center)" />
                <circle cx="500" cy="340" r="7" fill="white" filter="url(#glow-center)" />
            </template>
        </svg>

        <!-- Hover Tooltip Card -->
        <Transition name="fade-scale">
            <div v-if="ninjaHoverNode"
                 @mouseenter="cancelHideTooltip()"
                 @mouseleave="scheduleHideTooltip()"
                 class="fixed z-[200] w-72 rounded-2xl shadow-2xl p-5"
                 style="background:#111214; border:1px solid rgba(255,255,255,0.1); backdrop-filter:blur(16px);"
                 :style="{ left: ninjaTooltipX + 'px', top: ninjaTooltipY + 'px' }">

                <!-- Date / role -->
                <p class="text-xs font-black tracking-widest uppercase mb-1" style="color:#E85D3E;">{{ ninjaHoverNode.role }}</p>
                <h4 class="text-white text-base font-black mb-0.5">{{ ninjaHoverNode.name }}</h4>
                <p class="text-xs mb-4" style="color:#555;">@ {{ ninjaHoverNode.company_name }}</p>

                <!-- Message quote -->
                <p class="text-sm leading-relaxed mb-5 italic pl-3" style="color:#ccc; border-left:2px solid #E85D3E;">
                    "{{ ninjaHoverNode.message }}"
                </p>

                <p class="text-xs uppercase tracking-widest font-black mb-2" style="color:#444;">Connected actions</p>

                <!-- LinkedIn -->
                <a v-if="ninjaHoverNode.linkedin_url" :href="ninjaHoverNode.linkedin_url" target="_blank"
                   class="flex items-center justify-between p-3 rounded-xl transition-colors group mb-1"
                   style="border:1px solid transparent;"
                   onmouseover="this.style.background='rgba(255,255,255,0.05)'"
                   onmouseout="this.style.background='transparent'">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4" fill="#0A66C2" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                        <span class="text-sm font-medium" style="color:#ccc;">Voir le profil LinkedIn</span>
                    </div>
                    <svg class="w-4 h-4" style="color:#555;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </a>

                <!-- Copy message -->
                <button @click="copyNinjaMessage(ninjaHoverNode.message, ninjaHoverNode.key)"
                    class="w-full flex items-center justify-between p-3 rounded-xl transition-colors group"
                    style="border:1px solid transparent;"
                    onmouseover="this.style.borderColor='rgba(232,93,62,0.3)'; this.style.background='rgba(232,93,62,0.05)'"
                    onmouseout="this.style.borderColor='transparent'; this.style.background='transparent'">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4" style="color:#888;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                        <span class="text-sm font-medium" style="color:#ccc;">Copier l'approche ({{ (ninjaHoverNode.message||'').length }} car.)</span>
                    </div>
                    <svg v-if="ninjaCopied[ninjaHoverNode.key]" class="w-4 h-4" style="color:#E85D3E;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    <svg v-else class="w-4 h-4" style="color:#444;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </button>
            </div>
        </Transition>

        <!-- Bottom toolbar (decorative) -->
        <div class="absolute bottom-5 left-1/2 -translate-x-1/2 flex items-center gap-1.5 p-2 rounded-full z-20"
             style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);">
            <div v-for="icon in ['M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4', 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7', 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7', 'M12 4v16m8-8H4']" :key="icon"
                 class="w-9 h-9 rounded-full flex items-center justify-center" style="color:#555;">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icon"/></svg>
            </div>
        </div>

        <!-- Empty state -->
        <div v-if="!ninjaLoading && !ninjaRunning && ninjaCompanies.length === 0"
             class="absolute inset-0 flex flex-col items-center justify-center text-center z-20">
            <div class="w-16 h-16 rounded-full flex items-center justify-center mb-4"
                 style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);">
                <svg class="w-8 h-8" style="color:#E85D3E;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            </div>
            <p class="text-white text-xl font-bold mb-2">Aucun réseau identifié</p>
            <p class="text-sm max-w-sm mb-6" style="color:#555;">Lancez le workflow depuis votre Dashboard pour cartographier vos contacts.</p>
            <button @click="runNinja" class="px-6 py-3 text-white font-bold rounded-2xl transition-all" style="background:#E85D3E;">
                Lancer le scan
            </button>
        </div>

        <!-- Scanning overlay -->
        <div v-if="ninjaRunning" class="absolute inset-0 flex flex-col items-center justify-center text-center z-50"
             style="background:rgba(7,8,10,0.92); backdrop-filter:blur(6px);">
            <div class="relative w-28 h-28 mb-8">
                <div class="absolute inset-0 rounded-full" style="border:4px solid rgba(232,93,62,0.2);"></div>
                <div class="absolute inset-0 rounded-full animate-spin" style="border:4px solid #E85D3E; border-top-color:transparent;"></div>
                <div class="absolute inset-0 flex items-center justify-center text-4xl">🥷</div>
            </div>
            <p class="text-xl font-black tracking-widest uppercase animate-pulse" style="color:#E85D3E;">Scan en cours</p>
            <p class="text-sm mt-3 max-w-sm" style="color:#555;">Identification des décideurs LinkedIn...</p>
        </div>
    </div>
\n"""

content = content[:start_idx] + new_template + content[end_idx:]

with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("Template replaced successfully.")

# ─── 2. INJECT helper functions (ninjaNodeX/Y, ninjaProfileX/Y, scheduleHideTooltip, cancelHideTooltip) ───
with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

helpers = """
// ── Ninja SVG Node positioning helpers ──
const ninjaNodeX = (i, total, radius) => {
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    return 500 + Math.cos(angle) * radius
}
const ninjaNodeY = (i, total, radius) => {
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    return 340 + Math.sin(angle) * radius
}
const ninjaProfileX = (ci, pi, cTotal, pTotal) => {
    const cx = ninjaNodeX(ci, cTotal, 210)
    const baseAngle = (ci / cTotal) * Math.PI * 2 - Math.PI / 2
    const spread = Math.PI / 2.2
    const step = pTotal > 1 ? spread / (pTotal - 1) : 0
    const angle = baseAngle - spread / 2 + step * pi
    return cx + Math.cos(angle) * 95
}
const ninjaProfileY = (ci, pi, cTotal, pTotal) => {
    const cy = ninjaNodeY(ci, cTotal, 210)
    const baseAngle = (ci / cTotal) * Math.PI * 2 - Math.PI / 2
    const spread = Math.PI / 2.2
    const step = pTotal > 1 ? spread / (pTotal - 1) : 0
    const angle = baseAngle - spread / 2 + step * pi
    return cy + Math.sin(angle) * 95
}

const ninjaHoverNode = ref(null)
const ninjaTooltipX = ref(0)
const ninjaTooltipY = ref(0)
let ninjaHideTimer = null

const showNinjaTooltip = (e, profile) => {
    if (ninjaHideTimer) { clearTimeout(ninjaHideTimer); ninjaHideTimer = null }
    ninjaHoverNode.value = profile
    let x = e.clientX + 20
    let y = e.clientY - 30
    if (x + 290 > window.innerWidth) x = e.clientX - 310
    if (y + 320 > window.innerHeight) y = e.clientY - 320
    ninjaTooltipX.value = x
    ninjaTooltipY.value = y
}
const scheduleHideTooltip = () => {
    ninjaHideTimer = setTimeout(() => { ninjaHoverNode.value = null }, 200)
}
const cancelHideTooltip = () => {
    if (ninjaHideTimer) { clearTimeout(ninjaHideTimer); ninjaHideTimer = null }
}
// ── End Ninja Helpers ──
"""

# Remove old globe engine + old positioning functions
# Remove globe engine
content = re.sub(
    r'// ══+\n// 🥷 NETWORK NINJA — 3D Globe Canvas Engine\n// ══+.*?// ── End Globe Engine ──\n',
    '',
    content, flags=re.DOTALL
)

# Remove old graph positioning helpers (old getCompanyX etc)
content = re.sub(
    r'// ── Graph Positioning Helpers ──\nconst getCompanyX.*?const getProfileY.*?\}\n',
    '',
    content, flags=re.DOTALL
)

# Remove old ninjaHoverNode, ninjaTooltipX/Y duplicates (from old code)
content = re.sub(
    r'const ninjaHoverNode = ref\(null\)\nconst ninjaTooltipX = ref\(0\)\nconst ninjaTooltipY = ref\(0\)\n',
    '',
    content
)

# Remove old vWatch and initGlobe (globe engine gone, no need for them)
content = re.sub(
    r'const vWatch = watch\n',
    '',
    content
)
content = re.sub(
    r'// Init when tab becomes active.*?}\n\}.*?\n',
    '',
    content,
    flags=re.DOTALL,
    count=1
)

# Remove old ninjaContainer, ninjaEdgesGroup, etc. refs (from old code if still there)
for old_var in [
    'const ninjaContainer = ref(null)\n',
    'const ninjaEdgesGroup = ref(null)\n',
    'const ninjaNodesGroup = ref(null)\n',
    'const ninjaSvgWrapper = ref(null)\n',
]:
    content = content.replace(old_var, '')

# Inject the helpers before prefillDraft
idx = content.find('const prefillDraft')
if idx != -1:
    content = content[:idx] + helpers + '\n' + content[idx:]
    print("Helpers injected before prefillDraft.")
else:
    idx = content.find('const enrichCompany')
    content = content[:idx] + helpers + '\n' + content[idx:]
    print("Helpers injected before enrichCompany.")

# Also remove initGlobe calls from onMounted
content = content.replace(
    "    if (activeTab.value === 'ninja') setTimeout(() => initGlobe(), 150)\n",
    ''
)
content = content.replace(
    "    if (activeTab.value === 'ninja') initGlobe()\n",
    ''
)

# Ensure CSS for animations in <style>
css_block = """
/* ── Ninja SVG Animations ── */
@keyframes ninja-edge-flow {
  from { stroke-dashoffset: 0; }
  to   { stroke-dashoffset: -18; }
}
.ninja-edge-anim {
  animation: ninja-edge-flow 2.5s linear infinite;
}
.ninja-company-node {
  animation: ninja-company-pulse 3s ease-in-out infinite alternate;
  transform-origin: center;
  transform-box: fill-box;
}
@keyframes ninja-company-pulse {
  from { r: 8; opacity: 0.85; }
  to   { r: 10; opacity: 1; }
}
.ninja-pulse-ring {
  animation: ninja-ring-expand 3s ease-in-out infinite;
  transform-origin: center;
  transform-box: fill-box;
}
@keyframes ninja-ring-expand {
  0%   { r: 12; opacity: 0.4; }
  50%  { r: 22; opacity: 0.1; }
  100% { r: 12; opacity: 0.4; }
}
"""

if '.ninja-edge-anim' not in content:
    content = content.replace('</style>', css_block + '\n</style>')

with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("All done. SVG neural network design applied.")
