import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add refs after the imports/setup
insertion_point = "const { t } = useI18n()"
new_refs = """
const { t } = useI18n()

// CV Themes for Audit Report
const CV_THEMES = computed(() => CV_TEMPLATES.map(tem => ({
  id: tem.id,
  name: tem.label,
  description: tem.description || 'Professional ATS-friendly layout',
  colors: [tem.accentColor || '#E85D3E', tem.accentColor || '#E85D3E'],
  build: tem.build,
})))

const selectedTheme = ref('goldarmy')
const hoveredTheme = ref(null)
const isDownloadingDocx = ref(false)
"""

if insertion_point in content:
    content = content.replace(insertion_point, new_refs)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("done")
else:
    print("Insertion point not found")
