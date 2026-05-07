with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

globe_script = """
// ══════════════════════════════════════════════════════════════
// 🥷 NETWORK NINJA — 3D Globe Canvas Engine
// ══════════════════════════════════════════════════════════════
import { watch as vWatch, nextTick } from 'vue'

const ninjaCanvas = ref(null)
const ninjaHoverNode = ref(null)
const ninjaTooltipX = ref(0)
const ninjaTooltipY = ref(0)

// Globe rotation state
let globeRotX = 0.3
let globeRotY = 0
let globeAutoRotateId = null
let globeIsDragging = false
let globeLastMouse = { x: 0, y: 0 }

// 3D nodes stored as {x3,y3,z3, x2,y2, ...meta}
let globeNodes = []
let globeEdges = []
let globeCtx = null
let globeAnimId = null

// ─ Spherical coordinates ─
const toSphere = (lon, lat, r = 200) => ({
    x: r * Math.cos(lat) * Math.cos(lon),
    y: r * Math.sin(lat),
    z: r * Math.cos(lat) * Math.sin(lon),
})

const projectPoint = (x3, y3, z3, rotX, rotY, cx, cy) => {
    // Rotate around Y
    const cosY = Math.cos(rotY), sinY = Math.sin(rotY)
    let rx = x3 * cosY + z3 * sinY
    let rz = -x3 * sinY + z3 * cosY
    // Rotate around X
    const cosX = Math.cos(rotX), sinX = Math.sin(rotX)
    let ry = y3 * cosX - rz * sinX
    rz = y3 * sinX + rz * cosX
    // Perspective
    const fov = 600
    const scale = fov / (fov + rz + 300)
    return { sx: cx + rx * scale, sy: cy + ry * scale, scale, visible: rz < 250 }
}

const buildGlobeNodes = (companies) => {
    globeNodes = []
    globeEdges = []
    if (!companies || companies.length === 0) return

    // Central node (Me)
    globeNodes.push({ id: 'me', type: 'center', label: 'Moi', x3: 0, y3: 0, z3: 0 })

    const totalCompanies = companies.length
    companies.forEach((company, ci) => {
        // Fibonacci sphere distribution
        const phi = Math.acos(1 - 2 * (ci + 0.5) / totalCompanies)
        const theta = Math.PI * (1 + Math.sqrt(5)) * ci

        const pos = toSphere(theta, phi - Math.PI / 2, 180)
        const cId = `c-${ci}`
        globeNodes.push({
            id: cId, type: 'company',
            label: company.company_name || '',
            ...pos, company_name: company.company_name
        })

        // Edge Me→Company
        globeEdges.push({ from: 'me', to: cId, color: '#E85D3E', width: 1 })

        // Profiles around company
        const profiles = company.profiles || []
        profiles.forEach((prof, pi) => {
            const pAngle = (pi / Math.max(1, profiles.length)) * Math.PI * 2
            const pPos = toSphere(
                theta + Math.cos(pAngle) * 0.6,
                (phi - Math.PI / 2) + Math.sin(pAngle) * 0.6,
                240
            )
            const pId = `p-${ci}-${pi}`
            globeNodes.push({
                id: pId, type: 'profile',
                label: (prof.name || 'Profil').split(' ')[0],
                ...pPos,
                // full profile data
                name: prof.name, role: prof.role,
                linkedin_url: prof.linkedin_url,
                message: prof.message,
                company_name: company.company_name,
                key: `${company.company_name}_${pi}`
            })
            globeEdges.push({ from: cId, to: pId, color: '#444', width: 0.5 })
        })
    })
}

const drawGlobe = () => {
    const canvas = ninjaCanvas.value
    if (!canvas) return
    const ctx = globeCtx
    if (!ctx) return

    const W = canvas.width, H = canvas.height
    const cx = W / 2, cy = H / 2

    ctx.clearRect(0, 0, W, H)

    // Dark radial bg
    const grad = ctx.createRadialGradient(cx, cy, 50, cx, cy, Math.max(W, H) * 0.7)
    grad.addColorStop(0, '#0d0d0d')
    grad.addColorStop(1, '#050505')
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, W, H)

    // Subtle grid lines on sphere surface (latitude circles)
    for (let lat = -75; lat <= 75; lat += 30) {
        ctx.beginPath()
        for (let lon = 0; lon <= 360; lon += 5) {
            const r = lat * Math.PI / 180
            const l = lon * Math.PI / 180
            const pos = toSphere(l, r, 195)
            const p = projectPoint(pos.x, pos.y, pos.z, globeRotX, globeRotY, cx, cy)
            if (!p.visible) continue
            if (lon === 0) ctx.moveTo(p.sx, p.sy)
            else ctx.lineTo(p.sx, p.sy)
        }
        ctx.strokeStyle = 'rgba(255,255,255,0.04)'
        ctx.lineWidth = 0.5
        ctx.stroke()
    }

    // project all nodes
    const projected = {}
    globeNodes.forEach(n => {
        if (n.id === 'me') {
            projected[n.id] = { sx: cx, sy: cy, scale: 1, visible: true }
        } else {
            projected[n.id] = projectPoint(n.x3, n.y3, n.z3, globeRotX, globeRotY, cx, cy)
        }
    })

    // Draw edges (back to front by avg z)
    const sortedEdges = [...globeEdges].sort((a, b) => {
        const za = (projected[a.from]?.scale || 0) + (projected[a.to]?.scale || 0)
        const zb = (projected[b.from]?.scale || 0) + (projected[b.to]?.scale || 0)
        return za - zb
    })
    sortedEdges.forEach(edge => {
        const f = projected[edge.from], t = projected[edge.to]
        if (!f || !t || !f.visible || !t.visible) return
        ctx.beginPath()
        ctx.moveTo(f.sx, f.sy)
        ctx.lineTo(t.sx, t.sy)
        ctx.strokeStyle = edge.color
        ctx.lineWidth = edge.width
        ctx.globalAlpha = 0.35 * Math.min(f.scale, t.scale) * 2
        ctx.stroke()
        ctx.globalAlpha = 1
    })

    // Draw nodes (sorted by z for depth)
    const sortedNodes = [...globeNodes].sort((a, b) => {
        return (projected[a.id]?.scale || 0) - (projected[b.id]?.scale || 0)
    })
    sortedNodes.forEach(n => {
        const p = projected[n.id]
        if (!p) return

        const alpha = n.id === 'me' ? 1 : Math.max(0.3, Math.min(1, p.scale * 1.5))
        ctx.globalAlpha = alpha

        if (n.type === 'center') {
            // Glow center
            const g = ctx.createRadialGradient(p.sx, p.sy, 0, p.sx, p.sy, 18)
            g.addColorStop(0, 'rgba(255,255,255,0.9)')
            g.addColorStop(1, 'rgba(255,255,255,0)')
            ctx.fillStyle = g
            ctx.beginPath()
            ctx.arc(p.sx, p.sy, 18, 0, Math.PI * 2)
            ctx.fill()
            ctx.fillStyle = '#fff'
            ctx.beginPath()
            ctx.arc(p.sx, p.sy, 6, 0, Math.PI * 2)
            ctx.fill()
        } else if (n.type === 'company') {
            const r = Math.max(4, 9 * p.scale)
            // Glow
            const g = ctx.createRadialGradient(p.sx, p.sy, 0, p.sx, p.sy, r * 3)
            g.addColorStop(0, 'rgba(232,93,62,0.6)')
            g.addColorStop(1, 'rgba(232,93,62,0)')
            ctx.fillStyle = g
            ctx.beginPath()
            ctx.arc(p.sx, p.sy, r * 3, 0, Math.PI * 2)
            ctx.fill()
            // Core
            ctx.fillStyle = '#E85D3E'
            ctx.beginPath()
            ctx.arc(p.sx, p.sy, r, 0, Math.PI * 2)
            ctx.fill()
            // Label
            if (p.scale > 0.6) {
                ctx.fillStyle = '#ffffff'
                ctx.font = `${Math.max(9, 11 * p.scale)}px sans-serif`
                ctx.textAlign = 'left'
                ctx.fillText(n.label.substring(0, 16), p.sx + r + 4, p.sy + 4)
            }
        } else if (n.type === 'profile') {
            const r = Math.max(3, 6 * p.scale)
            ctx.fillStyle = '#888'
            ctx.beginPath()
            ctx.arc(p.sx, p.sy, r, 0, Math.PI * 2)
            ctx.fill()
            if (p.scale > 0.65) {
                ctx.fillStyle = '#aaa'
                ctx.font = `${Math.max(8, 9 * p.scale)}px sans-serif`
                ctx.textAlign = 'left'
                ctx.fillText(n.label, p.sx + r + 3, p.sy + 3)
            }
        }
        ctx.globalAlpha = 1
    })
}

let globeRotVelX = 0, globeRotVelY = 0

const globeAnimate = () => {
    if (!globeIsDragging) {
        globeRotY += 0.003 + globeRotVelY
        globeRotX += globeRotVelX
        globeRotVelX *= 0.95
        globeRotVelY *= 0.95
        // clamp X rotation
        globeRotX = Math.max(-1.2, Math.min(1.2, globeRotX))
    }
    drawGlobe()
    globeAnimId = requestAnimationFrame(globeAnimate)
}

const initGlobe = async () => {
    await nextTick()
    const canvas = ninjaCanvas.value
    if (!canvas) return
    const container = canvas.parentElement
    canvas.width = container.clientWidth
    canvas.height = container.clientHeight
    globeCtx = canvas.getContext('2d')
    buildGlobeNodes(ninjaCompanies.value)
    if (globeAnimId) cancelAnimationFrame(globeAnimId)
    globeAnimate()
}

// Drag
const globeMouseDown = (e) => {
    globeIsDragging = true
    globeLastMouse = { x: e.clientX, y: e.clientY }
}
const globeMouseMove = (e) => {
    if (globeIsDragging) {
        const dx = e.clientX - globeLastMouse.x
        const dy = e.clientY - globeLastMouse.y
        globeRotVelY = dx * 0.005
        globeRotVelX = dy * 0.005
        globeRotY += globeRotVelY
        globeRotX += globeRotVelX
        globeRotX = Math.max(-1.2, Math.min(1.2, globeRotX))
        globeLastMouse = { x: e.clientX, y: e.clientY }
    } else {
        // Hover detection
        const canvas = ninjaCanvas.value
        if (!canvas) return
        const rect = canvas.getBoundingClientRect()
        const mx = e.clientX - rect.left
        const my = e.clientY - rect.top
        const cx = canvas.width / 2, cy = canvas.height / 2
        let found = null
        let bestDist = 20
        globeNodes.forEach(n => {
            if (n.type !== 'profile') return
            const p = projectPoint(n.x3, n.y3, n.z3, globeRotX, globeRotY, cx, cy)
            if (!p.visible) return
            const dist = Math.hypot(mx - p.sx, my - p.sy)
            if (dist < bestDist) { bestDist = dist; found = n }
        })
        if (found) {
            ninjaHoverNode.value = found
            let tx = e.clientX + 20
            let ty = e.clientY - 20
            if (tx + 290 > window.innerWidth) tx = e.clientX - 310
            if (ty + 280 > window.innerHeight) ty = e.clientY - 300
            ninjaTooltipX.value = tx
            ninjaTooltipY.value = ty
        } else {
            ninjaHoverNode.value = null
        }
    }
}
const globeMouseUp = () => { globeIsDragging = false }
const globeMouseLeave = () => { globeIsDragging = false }

// Touch
let lastTouch = null
const globeTouchStart = (e) => {
    globeIsDragging = true
    lastTouch = { x: e.touches[0].clientX, y: e.touches[0].clientY }
}
const globeTouchMove = (e) => {
    if (!globeIsDragging || !lastTouch) return
    const dx = e.touches[0].clientX - lastTouch.x
    const dy = e.touches[0].clientY - lastTouch.y
    globeRotVelY = dx * 0.005
    globeRotVelX = dy * 0.005
    globeRotY += globeRotVelY
    globeRotX += globeRotVelX
    lastTouch = { x: e.touches[0].clientX, y: e.touches[0].clientY }
}
const globeTouchEnd = () => { globeIsDragging = false }

// Rebuild when companies change
vWatch(ninjaCompanies, () => {
    buildGlobeNodes(ninjaCompanies.value)
}, { deep: true })

// Init when tab becomes active
vWatch(activeTab, (tab) => {
    if (tab === 'ninja') initGlobe()
})

// ── End Globe Engine ──
"""

if 'initGlobe' not in content:
    # Insert before prefillDraft
    idx = content.find('const prefillDraft')
    if idx == -1:
        idx = content.find('const enrichCompany')
    content = content[:idx] + globe_script + '\n' + content[idx:]

    # Also call initGlobe in onMounted if ninja tab is already active
    content = content.replace(
        'onMounted(() => {\n    loadContacts()\n    fetchProfile()\n    loadNinjaResults()',
        'onMounted(() => {\n    loadContacts()\n    fetchProfile()\n    loadNinjaResults()\n    if (activeTab.value === \'ninja\') initGlobe()'
    )

    with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Globe engine injected!')
else:
    print('Already injected.')
