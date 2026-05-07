import sys
import re

print("Starting fix_missing_logic.py...")

# --- 1. UPDATE API MAIN ---
api_file = 'api/main.py'
with open(api_file, 'r', encoding='utf-8') as f:
    api_content = f.read()

api_injection = """
# ---------------------------------------------------------------------------
# NETWORK NINJA ROUTES
# ---------------------------------------------------------------------------
from agents.network_ninja_agent import network_ninja_agent

@app.post("/api/network/ninja/run")
async def run_network_ninja(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        result = await network_ninja_agent.run(user_id)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error running network ninja: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/network/ninja/results")
async def get_network_ninja_results(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        db = get_db()
        doc = await db.ninja_results.find_one({"user_id": user_id})
        if not doc:
            return {"status": "success", "data": {"companies": []}}
        
        # Remove mongo _id before returning
        doc.pop("_id", None)
        return {"status": "success", "data": doc}
    except Exception as e:
        logger.error(f"Error getting network ninja results: {e}")
        raise HTTPException(status_code=500, detail=str(e))
"""

if "@app.post(\"/api/network/ninja/run\")" not in api_content:
    api_content += "\n" + api_injection
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(api_content)
    print("API routes added.")
else:
    print("API routes already exist.")

# --- 2. UPDATE RESEAUX.VUE SCRIPT ---
vue_file = 'frontend/src/views/Reseaux.vue'
with open(vue_file, 'r', encoding='utf-8') as f:
    vue_content = f.read()

# We need to insert ALL the ninja logic into the <script setup> block.
# Let's find a good place. Just before `onMounted(async () => {`
script_insertion = """
// ── NETWORK NINJA LOGIC ──
import gsap from 'gsap'
const ninjaContainer = ref(null)
const ninjaEdgesGroup = ref(null)
const ninjaNodesGroup = ref(null)
const ninjaSvgWrapper = ref(null)

const ninjaCompanies = ref([])
const ninjaLoading = ref(true)
const ninjaRunning = ref(false)
const ninjaHoverNode = ref(null)
const ninjaTooltipX = ref(0)
const ninjaTooltipY = ref(0)
const ninjaCopied = ref({})

const ninjaTotalProfiles = computed(() => {
    return ninjaCompanies.value.reduce((acc, c) => acc + (c.profiles ? c.profiles.length : 0), 0)
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

const copyNinjaMessage = async (msg, key) => {
    if (!msg) return
    try {
        await navigator.clipboard.writeText(msg)
        ninjaCopied.value[key] = true
        setTimeout(() => { ninjaCopied.value[key] = false }, 2000)
    } catch(err) {
        console.error("Copie echouee", err)
    }
}

const loadNinjaResults = async () => {
    try {
        ninjaLoading.value = true
        const res = await authFetch('/api/network/ninja/results')
        const data = await res.json()
        if (data && data.status === 'success' && data.data) {
            ninjaCompanies.value = data.data.companies || []
        }
    } catch(err) {
        console.error("Error loading ninja results:", err)
    } finally {
        ninjaLoading.value = false
    }
}

const runNinja = async () => {
    try {
        ninjaRunning.value = true
        ninjaHoverNode.value = null
        const res = await authFetch('/api/network/ninja/run', { method: 'POST' })
        const data = await res.json()
        if (data && data.status === 'success' && data.data) {
            ninjaCompanies.value = data.data.companies || []
            toastState.addToast("Cartographie 3D terminée !", "success")
        }
    } catch(err) {
        console.error("Error running ninja:", err)
        toastState.addToast("Erreur lors de la génération", "error")
    } finally {
        ninjaRunning.value = false
    }
}
// ── END NETWORK NINJA LOGIC ──
"""

if "const runNinja" not in vue_content:
    # insert before onMounted
    idx = vue_content.find("onMounted(async () => {")
    if idx != -1:
        vue_content = vue_content[:idx] + script_insertion + "\n" + vue_content[idx:]
        
        # also we need to call loadNinjaResults inside onMounted
        # look for onMounted block end, but it's simpler to just inject `loadNinjaResults();` after `onMounted(async () => {`
        mounted_marker = "onMounted(async () => {"
        m_idx = vue_content.find(mounted_marker)
        if m_idx != -1:
            vue_content = vue_content[:m_idx + len(mounted_marker)] + "\n    loadNinjaResults();" + vue_content[m_idx + len(mounted_marker):]

        with open(vue_file, 'w', encoding='utf-8') as f:
            f.write(vue_content)
        print("Vue script patched.")
    else:
        print("onMounted not found in vue script!")
else:
    print("Vue script already patched.")
