with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Replace the initGlobe function to use ResizeObserver + wait for DOM
old_init = """const initGlobe = async () => {
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
}"""

new_init = """const initGlobe = async () => {
    await nextTick()
    // Small delay to ensure the container has its final dimensions
    await new Promise(r => setTimeout(r, 50))
    const canvas = ninjaCanvas.value
    if (!canvas) return
    // Use the parent container's bounding rect for reliable sizing
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width || canvas.offsetWidth || 800
    canvas.height = rect.height || canvas.offsetHeight || 720
    if (canvas.width < 10) {
        // Fallback: try parent
        const container = canvas.parentElement
        if (container) {
            canvas.width = container.offsetWidth || 800
            canvas.height = container.offsetHeight || 720
        }
    }
    globeCtx = canvas.getContext('2d')
    buildGlobeNodes(ninjaCompanies.value)
    if (globeAnimId) cancelAnimationFrame(globeAnimId)
    globeAnimate()
}"""

if old_init in content:
    content = content.replace(old_init, new_init)
    print("initGlobe fixed.")
else:
    print("WARNING: initGlobe not found exactly, trying partial...")
    # Try to find and replace
    import re
    content = re.sub(
        r'const initGlobe = async \(\) => \{.*?globeAnimate\(\)\n\}',
        new_init,
        content,
        flags=re.DOTALL
    )
    print("Done via regex.")

# Fix 2: The watcher for activeTab - ensure it calls with nextTick delay
old_watch = """// Init when tab becomes active
vWatch(activeTab, (tab) => {
    if (tab === 'ninja') initGlobe()
})"""

new_watch = """// Init when tab becomes active
vWatch(activeTab, async (tab) => {
    if (tab === 'ninja') {
        // Wait for DOM to settle before initializing canvas
        await nextTick()
        setTimeout(() => initGlobe(), 100)
    }
})"""

if old_watch in content:
    content = content.replace(old_watch, new_watch)
    print("vWatch fixed.")
else:
    print("WARNING: vWatch activeTab not found exactly.")

# Fix 3: Also call initGlobe from onMounted if ninja tab already active
old_mounted = "    if (activeTab.value === 'ninja') initGlobe()"
new_mounted = "    if (activeTab.value === 'ninja') setTimeout(() => initGlobe(), 150)"

if old_mounted in content:
    content = content.replace(old_mounted, new_mounted)
    print("onMounted initGlobe delay fixed.")

# Fix 4: Also call initGlobe when ninjaCompanies is loaded
old_ninja_watch = """// Rebuild when companies change
vWatch(ninjaCompanies, () => {
    buildGlobeNodes(ninjaCompanies.value)
}, { deep: true })"""

new_ninja_watch = """// Rebuild when companies change
vWatch(ninjaCompanies, async () => {
    buildGlobeNodes(ninjaCompanies.value)
    // If canvas not yet initialized (e.g., data loaded after mount), init now
    if (!globeCtx && activeTab.value === 'ninja') {
        await nextTick()
        setTimeout(() => initGlobe(), 100)
    }
}, { deep: true })"""

if old_ninja_watch in content:
    content = content.replace(old_ninja_watch, new_ninja_watch)
    print("ninjaCompanies watcher fixed.")

with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("All fixes applied.")
