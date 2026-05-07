import sys
import re

with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to inject the math functions, variables, etc.
# Find where to inject them. We can inject them right before `const runNinja`
injection = """
// ── 3D Parallax & Hover Logic ──
import gsap from 'gsap'
const ninjaContainer = ref(null)
const ninjaEdgesGroup = ref(null)
const ninjaNodesGroup = ref(null)
const ninjaSvgWrapper = ref(null)

const ninjaHoverNode = ref(null)
const ninjaTooltipX = ref(0)
const ninjaTooltipY = ref(0)

const ninjaTotalProfiles = computed(() => {
    return ninjaCompanies.value ? ninjaCompanies.value.reduce((acc, c) => acc + (c.profiles ? c.profiles.length : 0), 0) : 0
})

const getCompanyX = (index, total) => {
    if (total === 0) return 0
    const angle = (index / total) * Math.PI * 2
    return Math.cos(angle) * 180
}

const getCompanyY = (index, total) => {
    if (total === 0) return 0
    const angle = (index / total) * Math.PI * 2
    return Math.sin(angle) * 180
}

const getProfileX = (cIndex, pIndex, cTotal, pTotal) => {
    const cx = getCompanyX(cIndex, cTotal)
    if (pTotal === 0) return cx
    const baseAngle = (cIndex / cTotal) * Math.PI * 2
    const spread = Math.PI / 2
    const pAngle = baseAngle - (spread / 2) + (pIndex / Math.max(1, pTotal - 1)) * spread
    return cx + Math.cos(pAngle) * 80
}

const getProfileY = (cIndex, pIndex, cTotal, pTotal) => {
    const cy = getCompanyY(cIndex, cTotal)
    if (pTotal === 0) return cy
    const baseAngle = (cIndex / cTotal) * Math.PI * 2
    const spread = Math.PI / 2
    const pAngle = baseAngle - (spread / 2) + (pIndex / Math.max(1, pTotal - 1)) * spread
    return cy + Math.sin(pAngle) * 80
}

const onNinjaMouseMove = (e) => {
    if (!ninjaContainer.value || !ninjaEdgesGroup.value || !ninjaNodesGroup.value) return
    const rect = ninjaContainer.value.getBoundingClientRect()
    const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1
    const ny = ((e.clientY - rect.top) / rect.height) * 2 - 1

    gsap.to(ninjaEdgesGroup.value, { x: nx * -40, y: ny * -40, rotationY: nx * 10, rotationX: -ny * 10, duration: 1, ease: 'power2.out' })
    gsap.to(ninjaNodesGroup.value, { x: nx * -80, y: ny * -80, rotationY: nx * 15, rotationX: -ny * 15, duration: 1, ease: 'power2.out' })
    gsap.to(ninjaSvgWrapper.value, { perspective: 1000, transformStyle: "preserve-3d", duration: 0 })
}

const onNinjaMouseLeave = () => {
    if (ninjaEdgesGroup.value && ninjaNodesGroup.value) {
        gsap.to([ninjaEdgesGroup.value, ninjaNodesGroup.value], { x: 0, y: 0, rotationX: 0, rotationY: 0, duration: 1.5, ease: 'power2.out' })
    }
}

const showNinjaTooltip = (e, profile) => {
    ninjaHoverNode.value = profile
    let x = e.clientX + 20
    let y = e.clientY - 20
    if (x + 320 > window.innerWidth) x = e.clientX - 340
    if (y + 200 > window.innerHeight) y = e.clientY - 220
    ninjaTooltipX.value = x
    ninjaTooltipY.value = y
}

const hideNinjaTooltip = () => {
    ninjaHoverNode.value = null
}
"""

if 'const getCompanyX' not in content:
    # We will find `const runNinja` and inject right above it.
    idx = content.find('const runNinja = async () => {')
    if idx != -1:
        content = content[:idx] + injection + '\n\n' + content[idx:]
        with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Frontend logic successfully injected!")
    else:
        print("Could not find const runNinja")
else:
    print("Already injected.")
