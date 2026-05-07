import re

with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove old parallax logic block
old_block = """
// ── 3D Parallax & Hover Logic ──
import gsap from 'gsap'
const ninjaContainer = ref(null)
const ninjaEdgesGroup = ref(null)
const ninjaNodesGroup = ref(null)
const ninjaSvgWrapper = ref(null)

const ninjaHoverNode = ref(null)
const ninjaTooltipX = ref(0)
const ninjaTooltipY = ref(0)

const onNinjaMouseMove = (e) => {
    if (!ninjaContainer.value || !ninjaEdgesGroup.value || !ninjaNodesGroup.value) return
    const rect = ninjaContainer.value.getBoundingClientRect()
    // Calculate normalized mouse position (-1 to 1)
    const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1
    const ny = ((e.clientY - rect.top) / rect.height) * 2 - 1

    // Apply parallax with GSAP
    gsap.to(ninjaEdgesGroup.value, {
        x: nx * -40,
        y: ny * -40,
        rotationY: nx * 10,
        rotationX: -ny * 10,
        duration: 1,
        ease: 'power2.out'
    })
    gsap.to(ninjaNodesGroup.value, {
        x: nx * -80,
        y: ny * -80,
        rotationY: nx * 15,
        rotationX: -ny * 15,
        duration: 1,
        ease: 'power2.out'
    })
    gsap.to(ninjaSvgWrapper.value, {
        perspective: 1000,
        transformStyle: "preserve-3d",
        duration: 0
    })
}

const onNinjaMouseLeave = () => {
    if (ninjaEdgesGroup.value && ninjaNodesGroup.value) {
        gsap.to([ninjaEdgesGroup.value, ninjaNodesGroup.value], {
            x: 0, y: 0, rotationX: 0, rotationY: 0, duration: 1.5, ease: 'power2.out'
        })
    }
}

const showNinjaTooltip = (e, profile) => {
    ninjaHoverNode.value = profile
    // Position tooltip near cursor
    // Adjust position to not go off-screen
    let x = e.clientX + 20
    let y = e.clientY - 20
    if (x + 320 > window.innerWidth) x = e.clientX - 340 // switch to left
    if (y + 200 > window.innerHeight) y = e.clientY - 220 // switch to top
    
    ninjaTooltipX.value = x
    ninjaTooltipY.value = y
}

const hideNinjaTooltip = () => {
    ninjaHoverNode.value = null
}
"""

# Also remove duplicate ninjaTotalProfiles computed and getCompanyX/Y/ProfileX/Y from 3D Parallax section 
# Since globe engine defines its own, we only need the script section ones

if old_block in content:
    content = content.replace(old_block, '\n')
    print("Old parallax block removed.")
else:
    # Try partial
    content = re.sub(
        r'// ── 3D Parallax & Hover Logic ──\nimport gsap from \'gsap\'\nconst ninjaContainer.*?const hideNinjaTooltip = \(\) => \{\s+ninjaHoverNode\.value = null\s+\}\n',
        '\n',
        content,
        flags=re.DOTALL
    )
    print("Old parallax block partially removed (regex).")

with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done.")
