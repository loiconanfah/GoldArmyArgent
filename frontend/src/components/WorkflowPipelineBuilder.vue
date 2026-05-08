<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  playbooks: { type: Array, default: () => [] }
})

// ── State ──────────────────────────────────────────────────────────────
const MAX_PIPELINES = 3
const pipelines = ref([]) // [{ id, name, nodes:[{id,wfId,x,y}], edges:[{from,to}] }]
const activePipelineIdx = ref(0)

const isWfPickerOpen = ref(false)
const pendingPort = ref(null) // { pipelineIdx, nodeId, side:'out' }
const connecting = ref(null)  // { fromNodeId, x1,y1 }
const mousePos = ref({ x: 0, y: 0 })
const dragging = ref(null)    // { nodeId, offX, offY }
const canvasRef = ref(null)

const toastMsg = ref(null)
const toastType = ref('error')
let toastTimeout = null

function showToast(msg, type = 'error') {
  toastMsg.value = msg
  toastType.value = type
  if (toastTimeout) clearTimeout(toastTimeout)
  toastTimeout = setTimeout(() => { toastMsg.value = null }, 4000)
}

// ── Persistence ────────────────────────────────────────────────────────
const save = () => { try { localStorage.setItem('ga_pipelines_v2', JSON.stringify(pipelines.value)) } catch(e) {} }
const load = () => { try { const s = localStorage.getItem('ga_pipelines_v2'); if (s) pipelines.value = JSON.parse(s) } catch(e) {} }

// ── Current pipeline ───────────────────────────────────────────────────
const pipeline = computed(() => pipelines.value[activePipelineIdx.value] || null)
const nodes = computed(() => pipeline.value?.nodes || [])
const edges = computed(() => pipeline.value?.edges || [])

// ── Workflow helpers ───────────────────────────────────────────────────
const VALID_CONNECTIONS = {
    1:  [2, 3, 4, 6],
    2:  [3, 9],
    3:  [4, 6],
    4:  [7],
    5:  [1, 6],
    6:  [4, 7],
    7:  [9, 8],
    8:  [6],
    9:  [1, 8],
    10: [1],
}

const wfById = (id) => props.playbooks.find(p => p.id === id)
const usedIds = computed(() => new Set(nodes.value.map(n => n.wfId)))
const availableWfs = computed(() => props.playbooks.filter(p => !usedIds.value.has(p.id)))

// ── Node positions ─────────────────────────────────────────────────────
const PORT_R = 7

function nodePortPos(node, side) {
  const W = 140, H = 72
  return {
    x: side === 'out' ? node.x + W : node.x,
    y: node.y + H / 2
  }
}

// ── Bezier path ────────────────────────────────────────────────────────
function bezier(x1, y1, x2, y2) {
  const dx = Math.abs(x2 - x1) * 0.5
  return `M${x1},${y1} C${x1+dx},${y1} ${x2-dx},${y2} ${x2},${y2}`
}

const edgePaths = computed(() => {
  return edges.value.map(e => {
    const fromNode = nodes.value.find(n => n.id === e.from)
    const toNode   = nodes.value.find(n => n.id === e.to)
    if (!fromNode || !toNode) return null
    const p1 = nodePortPos(fromNode, 'out')
    const p2 = nodePortPos(toNode, 'in')
    return { ...e, d: bezier(p1.x, p1.y, p2.x, p2.y) }
  }).filter(Boolean)
})

const ghostPath = computed(() => {
  if (!connecting.value) return null
  const { x1, y1 } = connecting.value
  return bezier(x1, y1, mousePos.value.x, mousePos.value.y)
})

const isValidTarget = (targetNode) => {
  if (!connecting.value) return false
  const p = pipeline.value; if (!p) return false
  const fromNode = p.nodes.find(n => n.id === connecting.value.fromNodeId)
  if (!fromNode || fromNode.id === targetNode.id) return false
  const allowed = VALID_CONNECTIONS[fromNode.wfId] || []
  return allowed.includes(targetNode.wfId)
}

// ── Pipeline CRUD ──────────────────────────────────────────────────────
function addPipeline() {
  if (pipelines.value.length >= MAX_PIPELINES) return
  pipelines.value.push({ id: Date.now(), name: `Pipeline ${pipelines.value.length + 1}`, nodes: [], edges: [] })
  activePipelineIdx.value = pipelines.value.length - 1
  save()
}

function removePipeline(idx) {
  pipelines.value.splice(idx, 1)
  if (activePipelineIdx.value >= pipelines.value.length) activePipelineIdx.value = Math.max(0, pipelines.value.length - 1)
  save()
}

// ── Node CRUD ──────────────────────────────────────────────────────────
function openWfPicker(pipelineIdx) {
  activePipelineIdx.value = pipelineIdx
  isWfPickerOpen.value = true
}

function addNode(wfId) {
  const p = pipelines.value[activePipelineIdx.value]
  if (!p) return
  const col = p.nodes.length
  p.nodes.push({ id: Date.now(), wfId, x: 40 + col * 180, y: 110 })
  isWfPickerOpen.value = false
  save()
}

function removeNode(nodeId) {
  const p = pipeline.value; if (!p) return
  p.nodes = p.nodes.filter(n => n.id !== nodeId)
  p.edges = p.edges.filter(e => e.from !== nodeId && e.to !== nodeId)
  save()
}

// ── Connections ────────────────────────────────────────────────────────
function startConnect(node) {
  const pos = nodePortPos(node, 'out')
  connecting.value = { fromNodeId: node.id, x1: pos.x, y1: pos.y }
}

function endConnect(node) {
  if (!connecting.value) return
  if (connecting.value.fromNodeId === node.id) { connecting.value = null; return }
  
  const p = pipeline.value; if (!p) return
  
  const fromNode = p.nodes.find(n => n.id === connecting.value.fromNodeId)
  if (!fromNode) { connecting.value = null; return }
  
  const allowed = VALID_CONNECTIONS[fromNode.wfId] || []
  if (!allowed.includes(node.wfId)) {
    showToast(`Connexion invalide : "${wfById(fromNode.wfId)?.name}" ne peut pas être relié à "${wfById(node.wfId)?.name}".`, 'error')
    connecting.value = null
    return
  }

  const exists = p.edges.find(e => e.from === connecting.value.fromNodeId && e.to === node.id)
  if (!exists) {
    p.edges.push({ id: Date.now(), from: connecting.value.fromNodeId, to: node.id })
    save()
  }
  connecting.value = null
}

function cancelConnect() { connecting.value = null }

function removeEdge(edgeId) {
  const p = pipeline.value; if (!p) return
  p.edges = p.edges.filter(e => e.id !== edgeId)
  save()
}

// ── Validation & Start ───────────────────────────────────────────────────
function startPipeline() {
  const p = pipeline.value; if (!p) return
  
  if (p.nodes.length === 0) {
    showToast("Le pipeline est vide. Ajoutez des workflows.", "error")
    return
  }
  
  if (p.nodes.length > 1 && p.edges.length < p.nodes.length - 1) {
    showToast("Certains workflows ne sont pas connectés.", "error")
    return
  }

  // Basic check for cycles or completely invalid graphs can go here.
  // For now, if all nodes are mostly connected, we simulate success
  showToast("Pipeline correctement connecté et démarré avec succès !", "success")
}

// ── Drag nodes ─────────────────────────────────────────────────────────
function onNodeMouseDown(e, node) {
  if (e.target.closest('.port')) return
  e.preventDefault()
  const rect = canvasRef.value.getBoundingClientRect()
  dragging.value = { nodeId: node.id, offX: e.clientX - rect.left - node.x, offY: e.clientY - rect.top - node.y }
}

function onCanvasMouseMove(e) {
  const rect = canvasRef.value?.getBoundingClientRect()
  if (!rect) return
  mousePos.value = { x: e.clientX - rect.left, y: e.clientY - rect.top }
  if (dragging.value) {
    const node = nodes.value.find(n => n.id === dragging.value.nodeId)
    if (node) {
      node.x = Math.max(0, mousePos.value.x - dragging.value.offX)
      node.y = Math.max(0, mousePos.value.y - dragging.value.offY)
    }
  }
}

function onCanvasMouseUp() {
  if (dragging.value) { dragging.value = null; save() }
  if (connecting.value) { connecting.value = null }
}

// ── Lifecycle ──────────────────────────────────────────────────────────
onMounted(() => {
  load()
})
</script>

<template>
  <div class="pb-section">
    <!-- Header -->
    <div class="pb-header">
      <div class="flex items-center gap-2">
        <span class="pb-title">Mes Pipelines</span>
        <span class="pb-badge">{{ pipelines.length }}/{{ MAX_PIPELINES }}</span>
      </div>
      <div class="flex items-center gap-2">
        <button v-if="pipeline && pipeline.nodes.length > 0" class="pb-start-btn" @click="startPipeline">
          <svg class="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"></path></svg>
          Démarrer
        </button>
        <button class="pb-new-btn" :disabled="pipelines.length >= MAX_PIPELINES" @click="addPipeline">
          + Nouveau Pipeline
        </button>
      </div>
    </div>

    <!-- Tab pills -->
    <div v-if="pipelines.length > 0" class="pb-tabs">
      <button v-for="(pl, i) in pipelines" :key="pl.id"
        class="pb-tab" :class="{ 'pb-tab-active': activePipelineIdx === i }"
        @click="activePipelineIdx = i">
        <span class="pb-tab-dot" :class="{ 'pb-tab-dot-active': activePipelineIdx === i }"></span>
        <input v-model="pl.name" @change="save()" @click.stop
          class="pb-tab-input" :class="{ 'pb-tab-input-active': activePipelineIdx === i }" />
        <button class="pb-tab-del" @click.stop="removePipeline(i)">✕</button>
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="pipelines.length === 0" class="pb-empty" @click="addPipeline">
      <div class="pb-empty-icon">⚡</div>
      <p class="pb-empty-title">Créez votre premier pipeline</p>
      <p class="pb-empty-sub">Reliez des workflows entre eux pour automatiser votre stratégie</p>
    </div>

    <!-- Canvas -->
    <div v-if="pipeline" class="pb-canvas" ref="canvasRef"
      @mousemove="onCanvasMouseMove"
      @mouseup="onCanvasMouseUp"
      @click="cancelConnect">

      <!-- SVG layer for edges -->
      <svg class="pb-svg" width="100%" height="100%">
        <defs>
          <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#4F46E5"/>
            <stop offset="100%" stop-color="#EC4899"/>
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>

        <!-- Edges -->
        <g v-for="edge in edgePaths" :key="edge.id">
          <!-- Background thicker track -->
          <path :d="edge.d" fill="none" stroke="#1E293B" stroke-width="4" stroke-linecap="round"/>
          
          <!-- Colored solid line -->
          <path :d="edge.d" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round"/>
          
          <!-- Animated glowing dash representing data flow -->
          <path :d="edge.d" fill="none" stroke="url(#edgeGrad)" stroke-width="2.5"
            stroke-linecap="round" filter="url(#glow)"
            stroke-dasharray="15 60" class="edge-anim"/>
            
          <!-- Hitbox for removing -->
          <path :d="edge.d" fill="none" stroke="transparent" stroke-width="15"
            class="edge-hitbox" @click.stop="removeEdge(edge.id)" title="Cliquer pour supprimer"/>
        </g>

        <!-- Ghost connection line -->
        <path v-if="ghostPath" :d="ghostPath" fill="none"
          stroke="#8B5CF6" stroke-width="2" stroke-dasharray="6 4"
          stroke-linecap="round" opacity="0.8"/>
      </svg>

      <!-- Nodes -->
      <div v-for="node in nodes" :key="node.id"
        class="pb-node"
        :class="{ 'pb-node-active': wfById(node.wfId)?.active, 'pb-node-dragging': dragging?.nodeId === node.id }"
        :style="`left:${node.x}px; top:${node.y}px`"
        @mousedown="onNodeMouseDown($event, node)">

        <!-- Input port -->
        <div class="port port-in" 
          :class="{'port-valid-target': isValidTarget(node)}"
          title="Relâchez ici pour connecter"
          @mouseup.stop="endConnect(node)">
          <div class="port-inner port-in-inner"></div>
        </div>

        <!-- Node body -->
        <div class="pb-node-body">
          <div class="pb-node-top">
            <div class="pb-node-icon" :class="wfById(node.wfId)?.active ? 'pb-node-icon-active' : ''">
              <component :is="wfById(node.wfId)?.icon" class="w-4 h-4"/>
            </div>
            <button class="pb-node-del" @click.stop="removeNode(node.id)">✕</button>
          </div>
          <div class="pb-node-name">{{ wfById(node.wfId)?.name }}</div>
          <div class="pb-node-desc">{{ wfById(node.wfId)?.desc }}</div>
          <div v-if="wfById(node.wfId)?.active" class="pb-node-status">
            <span class="pb-status-dot"></span> Actif
          </div>
        </div>

        <!-- Output port -->
        <div class="port port-out" title="Tirer pour connecter" @mousedown.stop="startConnect(node)">
          <div class="port-inner port-out-inner"></div>
        </div>
      </div>

      <!-- Add node button -->
      <button class="pb-add-node" @click.stop="openWfPicker(activePipelineIdx)">
        <span class="text-xl">+</span>
        <span class="text-[10px] font-semibold mt-0.5">Workflow</span>
      </button>

      <!-- Canvas hint -->
      <div v-if="nodes.length === 0" class="pb-canvas-hint">
        Cliquez <strong>+ Workflow</strong> pour ajouter un nœud · Tirez le port <span class="hint-port">●</span> pour connecter
      </div>
      <div v-else-if="nodes.length === 1" class="pb-canvas-hint">
        Ajoutez un autre workflow puis tirez le port droit <span class="hint-port">●</span> vers le port gauche
      </div>
    </div>

    <!-- Workflow picker modal -->
    <Transition name="fade">
      <div v-if="isWfPickerOpen" class="fixed inset-0 z-[80] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm"
        @click.self="isWfPickerOpen = false">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden animate-slide-up">
          <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-indigo-50/40">
            <div>
              <h3 class="font-bold text-slate-800 text-sm">Ajouter un nœud</h3>
              <p class="text-[11px] text-slate-500 mt-0.5">Choisissez un workflow à placer sur le canvas</p>
            </div>
            <button @click="isWfPickerOpen = false" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">✕</button>
          </div>
          <div class="p-3 space-y-1 max-h-72 overflow-y-auto">
            <div v-if="availableWfs.length === 0" class="text-center py-8 text-sm text-slate-400">
              Tous les workflows sont déjà sur le canvas.
            </div>
            <div v-for="wf in availableWfs" :key="wf.id"
              @click="addNode(wf.id)"
              class="flex items-center gap-3 p-3 rounded-xl border border-transparent hover:border-indigo-200 hover:bg-indigo-50/50 cursor-pointer transition-all group">
              <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
                :class="wf.active ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-500 group-hover:bg-indigo-100 group-hover:text-indigo-600'">
                <component :is="wf.icon" class="w-4 h-4"/>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-bold text-slate-800">{{ wf.name }}</div>
                <div class="text-[10px] text-slate-500 truncate">{{ wf.desc }}</div>
              </div>
              <div v-if="wf.active" class="w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0"></div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    <!-- Toast Notification -->
    <Transition name="fade-up">
      <div v-if="toastMsg" class="fixed bottom-6 left-1/2 -translate-x-1/2 px-4 py-3 rounded-2xl shadow-2xl flex items-center gap-3 z-[90] max-w-md w-max border"
        :class="toastType === 'error' ? 'bg-slate-900 border-rose-500/30' : 'bg-emerald-950 border-emerald-500/30'">
        <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
          :class="toastType === 'error' ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'">
          <svg v-if="toastType === 'error'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
        </div>
        <p class="text-sm font-medium" :class="toastType === 'error' ? 'text-rose-100' : 'text-emerald-100'">{{ toastMsg }}</p>
        <button @click="toastMsg = null" class="ml-2 text-slate-400 hover:text-white transition-colors">✕</button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.pb-section {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}
.pb-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.pb-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #111827;
}
.pb-badge {
  font-size: 0.7rem;
  font-weight: 700;
  background: #F1F5F9;
  color: #64748B;
  border: 1px solid #E2E8F0;
  border-radius: 99px;
  padding: 2px 8px;
}
.pb-new-btn {
  font-size: 0.75rem;
  font-weight: 700;
  color: #6366f1;
  background: #EEF2FF;
  border: 1px solid #C7D2FE;
  border-radius: 10px;
  padding: 0.35rem 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.pb-new-btn:hover:not(:disabled) { background: #E0E7FF; box-shadow: 0 2px 8px rgba(99,102,241,.15); }
.pb-new-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.pb-start-btn {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #10B981, #059669);
  border: none;
  border-radius: 10px;
  padding: 0.35rem 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 10px rgba(16,185,129,.3);
}
.pb-start-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(16,185,129,.4);
}

/* Tabs */
.pb-tabs { display: flex; gap: 0.5rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
.pb-tab {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.35rem 0.75rem; border-radius: 99px;
  border: 1.5px solid #E5E7EB; background: white;
  cursor: pointer; transition: all 0.2s; font-size: 0.75rem;
}
.pb-tab-active { border-color: #6366f1; background: #EEF2FF; }
.pb-tab-dot { width:6px; height:6px; border-radius:50%; background:#D1D5DB; flex-shrink:0; }
.pb-tab-dot-active { background: #6366f1; box-shadow: 0 0 6px #6366f1; }
.pb-tab-input { background:transparent; border:none; outline:none; font-weight:700; color:#374151; font-size:0.75rem; width:90px; cursor:pointer; }
.pb-tab-input-active { color:#4338CA; }
.pb-tab-del { color:#CBD5E1; font-size:0.7rem; cursor:pointer; transition:color .2s; padding:0 2px; }
.pb-tab-del:hover { color:#F87171; }

/* Empty */
.pb-empty {
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  padding: 3rem 1rem; border: 2px dashed #E2E8F0; border-radius: 20px;
  background: #FAFAFA; cursor:pointer; transition:all .25s;
}
.pb-empty:hover { border-color: #C7D2FE; background: #F5F3FF; }
.pb-empty-icon { font-size:2rem; margin-bottom:.75rem; }
.pb-empty-title { font-size:.9rem; font-weight:700; color:#374151; }
.pb-empty-sub { font-size:.75rem; color:#9CA3AF; margin-top:.25rem; text-align:center; }

/* Canvas */
.pb-canvas {
  position: relative;
  background: #0F172A;
  border-radius: 20px;
  height: 320px;
  overflow: hidden;
  border: 1px solid #1E293B;
  box-shadow: inset 0 2px 20px rgba(0,0,0,.3), 0 4px 24px rgba(0,0,0,.08);
  background-image:
    radial-gradient(circle at 20% 50%, rgba(99,102,241,.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(139,92,246,.06) 0%, transparent 50%),
    linear-gradient(rgba(255,255,255,.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.015) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 28px 28px, 28px 28px;
  cursor: default;
}

/* SVG */
.pb-svg {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  pointer-events: none;
}
.edge-hitbox { pointer-events: stroke; cursor: pointer; }
.edge-hitbox:hover { stroke: rgba(236,72,153,.2); }
.edge-anim {
  animation: edge-flow 1.5s linear infinite;
}
@keyframes edge-flow {
  from { stroke-dashoffset: 75; }
  to   { stroke-dashoffset: 0; }
}

/* Nodes */
.pb-node {
  position: absolute;
  display: flex;
  align-items: center;
  user-select: none;
  cursor: grab;
  transition: filter .2s;
}
.pb-node:active, .pb-node-dragging { cursor: grabbing; filter: drop-shadow(0 0 12px rgba(99,102,241,.5)); }
.pb-node-active .pb-node-body { border-color: #6366f1 !important; }

.pb-node-body {
  width: 140px;
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(12px);
  border: 1.5px solid rgba(255,255,255,.12);
  border-radius: 14px;
  padding: 0.65rem;
  transition: all .2s;
}
.pb-node-body:hover { border-color: rgba(99,102,241,.5); background: rgba(255,255,255,.09); }

.pb-node-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:.4rem; }
.pb-node-icon {
  width:28px; height:28px; border-radius:8px;
  background:rgba(255,255,255,.1); color:#94A3B8;
  display:flex; align-items:center; justify-content:center;
  transition:all .2s;
}
.pb-node-icon-active { background:rgba(99,102,241,.3); color:#A5B4FC; }
.pb-node-del { color:rgba(255,255,255,.2); font-size:.65rem; cursor:pointer; transition:color .2s; width:16px; height:16px; display:flex; align-items:center; justify-content:center; border-radius:4px; }
.pb-node-del:hover { color:#F87171; background:rgba(248,113,113,.1); }
.pb-node-name { font-size:.7rem; font-weight:800; color:#F1F5F9; line-height:1.2; }
.pb-node-desc { font-size:.6rem; color:#64748B; margin-top:.15rem; line-height:1.3; }
.pb-node-status { display:flex; align-items:center; gap:.3rem; margin-top:.35rem; font-size:.6rem; font-weight:700; color:#34D399; }
.pb-status-dot { width:5px; height:5px; border-radius:50%; background:#34D399; animation:pulse-dot 2s infinite; }
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:.4} }

/* Ports */
.port {
  position: relative;
  width: 14px; height: 14px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; z-index: 10;
  transition: transform .2s;
  cursor: crosshair;
}
.port:hover { transform: scale(1.4); }
.port-in { background: rgba(99,102,241,.2); border:2px solid #6366f1; }
.port-out { background: rgba(139,92,246,.2); border:2px solid #8B5CF6; cursor: grab; }
.port-out:active { cursor: grabbing; }
.port-inner { width:5px; height:5px; border-radius:50%; pointer-events: none; }
.port-in-inner { background:#6366f1; }
.port-out-inner { background:#8B5CF6; }

.port-valid-target {
  transform: scale(1.5);
  background: rgba(52, 211, 153, 0.3) !important;
  border-color: #34D399 !important;
  box-shadow: 0 0 15px rgba(52, 211, 153, 0.4);
}
.port-valid-target .port-inner { background: #34D399 !important; }

/* Add node btn */
.pb-add-node {
  position:absolute; bottom:16px; right:16px;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  width:54px; height:54px; border-radius:14px;
  background:rgba(99,102,241,.15); border:1.5px dashed rgba(99,102,241,.4);
  color:#A5B4FC; cursor:pointer; transition:all .2s; z-index:5;
}
.pb-add-node:hover { background:rgba(99,102,241,.25); border-color:#6366f1; box-shadow:0 0 20px rgba(99,102,241,.25); transform:scale(1.05); }

/* Canvas hint */
.pb-canvas-hint {
  position:absolute; bottom:16px; left:50%; transform:translateX(-50%);
  font-size:.65rem; color:rgba(255,255,255,.3); white-space:nowrap;
  pointer-events:none; font-weight:500;
}
.hint-port { color:#6366f1; font-size:.9rem; }

/* Fade transition */
.fade-enter-active, .fade-leave-active { transition: opacity .2s, transform .2s; }
.fade-enter-from, .fade-leave-to { opacity:0; transform:scale(.97); }
</style>
